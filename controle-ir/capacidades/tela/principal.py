"""Agente de tela pelo Shizuku (rish): ver a tela e tocar/digitar, sem root. Entrada/saída: JSON.

O rish roda comandos com o usuário "shell" do adb (uid 2000): screencap, uiautomator, input e monkey.
Arquivos: ~/.controle-ir/rish/{rish, rish_shizuku.dex} (exportados pelo app Shizuku).

A saída dos comandos volta por ARQUIVO numa pasta oculta da memória compartilhada (COMPARTILHADA), apagado logo
após a leitura: no POCO (Shizuku 13, Android 16) o cano do rish cortava saídas grandes e misturava stdout e stderr
(a captura PNG chegava com 28 KB de 317 KB e o `id` voltava vazio).
"""
import base64
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import threading
import time
import unicodedata
import xml.etree.ElementTree as ET

BASE = os.environ.get("CONTROLE_IR_DIR") or os.path.expanduser("~/.controle-ir")
RISH = os.path.join(BASE, "rish", "rish")
TMP = os.path.join(BASE, "tela")
# pasta de troca com o usuário shell: ele escreve aqui e o Termux (com acesso ao armazenamento) lê
COMPARTILHADA = os.environ.get("CONTROLE_IR_COMPARTILHADA") or "/storage/emulated/0/Download/.controle-ir-tela"
# área do shell onde o comando escreve de fato: o system_server recusa (Failed transaction) as saídas de `cmd`
# (ex.: input) que apontam para a memória compartilhada ou para o cano do app; daqui o resultado é copiado
TMP_SHELL = os.environ.get("CONTROLE_IR_TMP_SHELL") or "/data/local/tmp"
BLOQUEADOS_ARQ = os.path.join(BASE, "tela_bloqueados.json")
# Apps em que a ferramenta não toca nem digita (bancos, pagamentos, senhas, autenticadores). Editável no arquivo acima.
BLOQUEADOS_PADRAO = [
    "br.com.bb", "com.itau", "br.com.itau", "br.com.bradesco", "com.bradesco", "com.nu.production",
    "br.com.intermedium", "com.santander", "br.com.santander", "br.com.caixa", "br.gov.caixa", "com.mercadopago",
    "com.picpay", "com.c6bank", "br.com.original", "com.btg", "br.com.sicredi", "br.com.sicoob", "com.sicoob",
    "br.com.uol.ps", "com.paypal", "com.google.android.apps.walletnfcrel", "com.samsung.android.spay",
    "com.x8bit.bitwarden", "com.lastpass", "com.onepassword", "com.agilebits", "com.dashlane", "com.keepassdroid",
    "com.azure.authenticator", "com.google.android.apps.authenticator2", "com.authy", "br.gov.meugovbr",
]
TECLAS = {"voltar": 4, "inicio": 3, "recentes": 187, "enter": 66, "apagar": 67}
JAVA_FONTE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "java", "controleir", "Tela.java")
# True quando o módulo roda dentro do serviço do controle-ir: aí o leitor rápido (Java) fica aberto entre as chamadas
EM_PROCESSO = False


# --------------------------------------------------------------------------- funções puras (testadas)
def normalizar(t):
    t = unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", t).strip()


def ler_bounds(b):
    m = re.match(r"\[(-?\d+),(-?\d+)\]\[(-?\d+),(-?\d+)\]", b or "")
    return tuple(int(v) for v in m.groups()) if m else None


_BLOQ_CACHE = {"t": 0.0, "lista": None}


def _privado(pacote):
    """App de banco/pagamento/senha/autenticador (a lista de bloqueio): o conteúdo dele NUNCA é lido nem enviado."""
    if not pacote:
        return False
    if time.time() - _BLOQ_CACHE["t"] > 5 or _BLOQ_CACHE["lista"] is None:
        _BLOQ_CACHE.update(t=time.time(), lista=bloqueados())
    return bloqueado(pacote, _BLOQ_CACHE["lista"])


_CORTE = [80]  # tamanho máximo de cada texto devolvido (texto_max na chamada: até 4000, p/ ler respostas longas)


def elementos(xml_texto, limite=120):
    """Elementos úteis do dump do uiautomator: com texto, descrição ou clicáveis, com o centro para tocar."""
    try:
        raiz = ET.fromstring(xml_texto)
    except ET.ParseError:
        return []
    out = []
    for n in raiz.iter("node"):
        a = n.attrib
        texto, desc = a.get("text", ""), a.get("content-desc", "")
        clicavel = a.get("clickable") == "true" or a.get("long-clickable") == "true"
        editavel = a.get("class", "").endswith("EditText")
        rolavel, marcavel = a.get("scrollable") == "true", a.get("checkable") == "true"
        b = ler_bounds(a.get("bounds"))
        if not b or b[2] <= b[0] or b[3] <= b[1] or not (texto or desc or clicavel or editavel or rolavel or marcavel):
            continue
        if _privado(a.get("package", "")):
            continue  # privacidade: nada de app de banco/senha sai do celular
        out.append({"texto": texto[:_CORTE[0]], "desc": desc[:_CORTE[0]], "id": a.get("resource-id", "").split("/")[-1],
                    "classe": a.get("class", "").split(".")[-1], "clicavel": clicavel, "editavel": editavel,
                    "x": (b[0] + b[2]) // 2, "y": (b[1] + b[3]) // 2, "pacote": a.get("package", ""),
                    "l": b[2] - b[0], "a": b[3] - b[1],
                    "marcado": a.get("checked") == "true" if marcavel else None,
                    "selecionado": a.get("selected") == "true", "rolavel": rolavel,
                    "focado": a.get("focused") == "true", "desativado": a.get("enabled") == "false"})
        if len(out) >= limite:
            break
    return out


def regioes_visuais(xml_texto, fracao=0.15):
    """Áreas que a acessibilidade não descreve (folha sem texto ocupando ≥ `fracao` da tela: tabuleiro, jogo,
    mapa, vídeo). Ali só a imagem mostra o conteúdo. Devolve [[x, y, l, a], ...], a maior primeiro."""
    try:
        raiz = ET.fromstring(xml_texto)
    except ET.ParseError:
        return []
    caixas, folhas = [], []
    for n in raiz.iter("node"):
        b = ler_bounds(n.attrib.get("bounds"))
        if not b or b[2] <= b[0] or b[3] <= b[1]:
            continue
        caixas.append(b)
        if n.find("node") is None and not (n.attrib.get("text") or n.attrib.get("content-desc")):
            folhas.append(b)
    if not caixas:
        return []
    tela = max(c[2] for c in caixas) * max(c[3] for c in caixas)
    out = [[b[0], b[1], b[2] - b[0], b[3] - b[1]] for b in folhas
           if (b[2] - b[0]) * (b[3] - b[1]) >= fracao * tela and (b[2] - b[0]) * (b[3] - b[1]) < 0.9 * tela]
    return sorted(out, key=lambda r: -r[2] * r[3])[:2]


def dentro(ponto, regiao):
    x, y = ponto
    return regiao[0] <= x <= regiao[0] + regiao[2] and regiao[1] <= y <= regiao[1] + regiao[3]


def achar(els, texto):
    """Elemento cujo texto/descrição/id contém `texto` (sem acento, sem caixa). Prefere igual > clicável > primeiro."""
    alvo = normalizar(texto)
    if not alvo:
        return None
    cands = [e for e in els if alvo in normalizar(e["texto"]) or alvo in normalizar(e["desc"])
             or alvo == normalizar(e["id"])]
    if not cands:
        return None
    iguais = [e for e in cands if alvo in (normalizar(e["texto"]), normalizar(e["desc"]))]
    for grupo in (iguais, cands):
        clic = [e for e in grupo if e["clicavel"]]
        if clic:
            return clic[0]
        if grupo:
            return grupo[0]
    return None


def bloqueado(pacote, lista):
    p = (pacote or "").lower()
    return any(p == b.lower() or p.startswith(b.lower() + ".") or p.startswith(b.lower()) for b in lista)


def escapar_input_text(texto):
    """Prepara o texto para `input text`: só ASCII imprimível; espaço vira %s. Devolve (texto, aviso)."""
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    aviso = "acentos e emojis não passam pelo input text; enviado sem acento" if sem_acento != texto else None
    sem_acento = "".join(c for c in sem_acento if 32 <= ord(c) < 127)
    return sem_acento.replace("%", r"\%").replace(" ", "%s"), aviso


def app_em_foco(dumpsys):
    m = re.search(r"mCurrentFocus=Window\{\S+ \S+ ([\w.]+)/", dumpsys or "") or \
        re.search(r"mFocusedApp=.*?([\w.]+)/", dumpsys or "")
    return m.group(1) if m else None


# --------------------------------------------------------------------------- celular
class SemShizuku(RuntimeError):
    pass


# --------------------------------------------------------------------------- leitor rápido (Java pelo Shizuku)
def _jar():
    """O leitor compilado (ecj + dx do Termux; compila na 1ª vez e quando o fonte muda). None se não der."""
    try:
        with open(JAVA_FONTE, "rb") as f:
            fonte = f.read()
    except OSError:
        return None
    os.makedirs(TMP, exist_ok=True)
    jar = os.path.join(TMP, f"controle-tela-{hashlib.sha256(fonte).hexdigest()[:12]}.jar")
    if os.path.exists(jar):
        return jar
    if not (shutil.which("ecj") and shutil.which("dx")) and shutil.which("pkg"):
        subprocess.run(["pkg", "install", "-y", "ecj", "dx"], capture_output=True, timeout=300, check=False)
    if not (shutil.which("ecj") and shutil.which("dx")):
        return None
    trab = os.path.join(TMP, f"compilar-{os.getpid()}")
    shutil.rmtree(trab, ignore_errors=True)
    try:
        os.makedirs(os.path.join(trab, "src", "controleir"))
        os.makedirs(os.path.join(trab, "dex", "controleir"))
        shutil.copy(JAVA_FONTE, os.path.join(trab, "src", "controleir", "Tela.java"))
        subprocess.run(["ecj", "-d", os.path.join(trab, "cls"), os.path.join(trab, "src", "controleir", "Tela.java")],
                       capture_output=True, timeout=180, check=False)
        cls = os.path.join(trab, "cls", "controleir")
        for c in os.listdir(cls) if os.path.isdir(cls) else []:
            shutil.copy(os.path.join(cls, c), os.path.join(trab, "dex", "controleir", c))
        parcial = jar[:-4] + ".parcial.jar"  # o dx escolhe o formato pela extensão: tem de terminar em .jar
        subprocess.run(["dx", "--dex", f"--output={parcial}", os.path.join(trab, "dex")],
                       capture_output=True, timeout=180, check=False)
        if not os.path.exists(parcial):
            return None
        for velho in os.listdir(TMP):
            if velho.startswith("controle-tela-") and velho.endswith(".jar") and velho != os.path.basename(parcial):
                _apagar(os.path.join(TMP, velho))
        os.replace(parcial, jar)
        return jar
    finally:
        shutil.rmtree(trab, ignore_errors=True)


class Ajudante:
    """Processo do leitor (app_process como shell) aberto pelo rish e falado pela entrada padrão; respostas em
    arquivos na pasta de troca. Se não subir, fica de lado por 60 s e tudo segue pelo caminho antigo."""

    def __init__(self):
        self.proc, self.token, self.n, self.falhou_em = None, None, 0, 0.0
        self.trava = threading.Lock()

    def _vivo(self):
        return self.proc is not None and self.proc.poll() is None

    def _matar(self):
        if self.proc is not None:
            try:
                self.proc.stdin.close()
                self.proc.kill()
                self.proc.wait(timeout=2)
            except (OSError, subprocess.TimeoutExpired):
                pass
        self.proc = None

    def _iniciar(self):
        if time.time() - self.falhou_em < 60 or not os.path.exists(RISH):
            return False
        jar = _jar()
        if not jar:
            self.falhou_em = time.time()
            return False
        pasta = _pasta_troca()
        copia = os.path.join(pasta, os.path.basename(jar))
        shutil.copy(jar, copia)
        self.token = f"{os.getpid()}x{time.monotonic_ns() % 10 ** 9}"
        destino = TMP_SHELL + "/controle-tela.jar"
        self.proc = subprocess.Popen(["sh", RISH], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL, env=dict(os.environ, RISH_APPLICATION_ID="com.termux"))
        linha = (f"cp {shlex.quote(copia)} {destino} && export CLASSPATH={destino} && exec app_process /system/bin "
                 f"controleir.Tela {shlex.quote(pasta)} {self.token}\n")
        try:
            self.proc.stdin.write(linha.encode())
            self.proc.stdin.flush()
        except OSError:
            self._matar()
        pronto = os.path.join(pasta, f"pronto-{self.token}")
        fim = time.time() + 10
        while self._vivo() and time.time() < fim:
            if os.path.exists(pronto):
                _apagar(pronto, copia)
                return True
            time.sleep(0.02)
        _apagar(copia)
        self._matar()
        self.falhou_em = time.time()
        return False

    def pedir(self, comando, timeout=15.0):
        with self.trava:
            if not self._vivo() and not self._iniciar():
                return None
            self.n += 1
            ident = f"{self.token}-{self.n}"
            arq = os.path.join(_pasta_troca(), ident + ".r")
            try:
                self.proc.stdin.write(f"{ident} {comando}\n".encode())
                self.proc.stdin.flush()
            except (OSError, ValueError):
                self._matar()
                return None
            fim = time.time() + timeout
            while time.time() < fim:
                if os.path.exists(arq):
                    try:
                        with open(arq, encoding="utf-8", errors="replace") as f:
                            return f.read()
                    finally:
                        _apagar(arq)
                if not self._vivo():
                    break
                time.sleep(0.005)
            self._matar()
            return None


AJUDANTE = Ajudante()


def _ajudante():
    return AJUDANTE if EM_PROCESSO else None


def _injetar(comando):
    """Toque/tecla/texto pelo leitor (injeção direta). False: use o caminho antigo (input pelo shell)."""
    a = _ajudante()
    if not a:
        return False
    r = a.pedir(comando, 15)
    return r is not None and r.strip() == "ok"


def _pasta_troca():
    try:
        os.makedirs(COMPARTILHADA, exist_ok=True)
        nomedia = os.path.join(COMPARTILHADA, ".nomedia")  # fora da galeria
        if not os.path.exists(nomedia):
            open(nomedia, "w").close()
    except OSError:
        pass  # o mkdir do lado do shell ainda tenta
    return COMPARTILHADA


def _ler(caminho):
    try:
        with open(caminho, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def _apagar(*caminhos):
    for c in caminhos:
        try:
            os.remove(c)
        except OSError:
            pass


def rish(cmd, timeout=20):
    """Roda `cmd` como usuário shell pelo Shizuku. Devolve (stdout, stderr, código), lidos de arquivos.
    Dentro do serviço, vai pelo leitor rápido já aberto (sem abrir outra conexão com o Shizuku: ~0,3 s a menos)."""
    a = _ajudante()
    if a:  # saídas em arquivos da área do shell: o HyperOS recusa `input` com saída num cano (provado no POCO)
        t = shlex.quote(f"{TMP_SHELL}/cir-{os.getpid()}-{time.monotonic_ns()}")
        embrulho = (f"( {cmd} ) < /dev/null > {t}.out 2> {t}.err; rc=$?; cat {t}.out; cat {t}.err >&2; "
                    f"rm -f {t}.out {t}.err; exit $rc")
        r = a.pedir(f"shell {embrulho.encode().hex()} {int(timeout * 1000)}", timeout + 5)
        if r is not None and "\n" in r:
            cab, resto = r.split("\n", 1)
            partes = cab.split(" ")
            if len(partes) == 2 and partes[0].lstrip("-").isdigit() and partes[1].isdigit():
                n = int(partes[1])
                return resto[:n], resto[n:], int(partes[0])
    if not os.path.exists(RISH):
        raise SemShizuku("rish não instalado: exporte os arquivos no app Shizuku (Usar o Shizuku em aplicativos de "
                         "terminal → Exportar) e peça ao Claude para copiá-los")
    env = dict(os.environ, RISH_APPLICATION_ID="com.termux")
    pasta = _pasta_troca()
    if not os.access(pasta, os.R_OK | os.W_OK):
        raise SemShizuku(f"o Termux não acessa a pasta de troca {pasta}: rode termux-setup-storage e permita o "
                         "acesso aos arquivos")
    nome = f"cir-{os.getpid()}-{time.monotonic_ns()}"
    base = os.path.join(pasta, nome)
    saida, erros, codigo = base + ".out", base + ".err", base + ".rc"
    t = shlex.quote(os.path.join(TMP_SHELL, nome))
    remoto = (f"mkdir -p {shlex.quote(pasta)}; ( {cmd} ) < /dev/null > {t}.out 2> {t}.err; rc=$?; "
              f"cat {t}.out > {shlex.quote(saida)}; cat {t}.err > {shlex.quote(erros)}; rm -f {t}.out {t}.err; "
              f"echo $rc > {shlex.quote(codigo)}")
    try:
        r = subprocess.run(["sh", RISH, "-c", remoto], capture_output=True, timeout=timeout, env=env, check=False)
        out, err, rc = _ler(saida), _ler(erros), _ler(codigo)
    finally:
        _apagar(saida, erros, codigo)
    if rc is None:  # o comando nem chegou a rodar do lado do shell
        detalhe = (r.stderr + r.stdout).decode(errors="ignore").strip()
        raise SemShizuku("o Shizuku não respondeu: abra o app Shizuku e toque em Iniciar (depois de reiniciar o "
                         f"celular ele precisa ser iniciado de novo). Detalhe: {detalhe[:200] or 'sem saída'}")
    try:
        cod = int(rc.strip())
    except ValueError:
        cod = 1
    return out or "", err or "", cod


def _bloqueio_de_toque(err, cod):
    """A Xiaomi bloqueia `input` sem a opção 'Depuração USB (Configurações de segurança)'. `err`: saída + erros."""
    # no HyperOS o bloqueio aparece como "cmd: Failure calling service input: Failed transaction (2147483646)"
    if any(t in err for t in ("INJECT_EVENTS", "SecurityException", "Failure calling service input",
                              "Failed transaction")):
        return ("a Xiaomi bloqueou o toque: ligue 'Depuração USB (Configurações de segurança)' nas Opções do "
                "desenvolvedor e toque em Iniciar de novo no Shizuku")
    if cod != 0:
        return f"o comando falhou (código {cod}): {err.strip()[:200]}"
    return None


def foco():
    a = _ajudante()
    if a:
        r = a.pedir("foco", 6)
        if r and not r.startswith("ERRO") and r.strip():
            return r.strip()
    out, _, _ = rish("dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'")
    return app_em_foco(out)


def estado_rapido():
    """(app em foco, tela acesa) pelo leitor rápido, sem abrir shell. None se o leitor não respondeu."""
    a = _ajudante()
    if a:
        r = a.pedir("estado", 6)
        if r and not r.startswith("ERRO") and "\n" in r:
            app, acesa = r.split("\n", 1)
            return app.strip() or None, {"1": True, "0": False}.get(acesa.strip())
    return None


def calma(quieto=120, limite=1000):
    """Espera a tela parar de mudar (nenhum evento de acessibilidade por `quieto` ms, até `limite` ms).
    Devolve os ms esperados, ou None sem o leitor rápido."""
    a = _ajudante()
    if not a:
        return None
    r = a.pedir(f"calma {int(quieto)} {int(limite)}", limite / 1000 + 5)
    try:
        return int(r.split()[1]) if r and r.split()[0] in ("ok", "tempo") else None
    except (IndexError, ValueError):
        return None


def eventos():
    """(janelas novas, mudanças, "pacote|classe|texto" da última janela) contados pelo leitor; None sem ele."""
    a = _ajudante()
    if not a:
        return None
    r = a.pedir("eventos", 6)
    try:
        j, m, t, ultima = r.split(" ", 3)
        return int(j), int(m), ultima.strip(), int(t)
    except (AttributeError, ValueError):
        return None


def historico(desde):
    """Janelas surgidas depois de `desde` (relógio do celular, ms): [(t, "pacote|classe|texto"), ...]."""
    a = _ajudante()
    r = a.pedir(f"historico {int(desde)}", 6) if a else None
    out = []
    for linha in (r or "").splitlines():
        t, _, info = linha.partition(" ")
        if t.isdigit():
            out.append((int(t), info))
    return out


def _janela_curta(info):
    pac, cls, txt = (info.split("|") + ["", "", ""])[:3]
    if _privado(pac):
        return f"{pac} (app privado: conteúdo não lido)"
    return f"{pac} {cls.split('.')[-1]}" + (f" «{txt}»" if txt else "")


# --------------------------------------------------------------------------- formato curto (menos tokens)
SINAIS = (("clicavel", "c"), ("editavel", "e"), ("selecionado", "s"), ("rolavel", "r"), ("focado", "f"),
          ("desativado", "d"))
LEGENDA = "texto (desc) #id x,y + sinais: c clicável, e editável, s selecionado, r rolável, f focado, d desativado, M/m marcado/não"


def curto(e):
    """Um elemento numa linha: "Texto" (desc) #id x,y sinais."""
    partes = []
    if e.get("texto"):
        partes.append(f'"{e["texto"]}"')
    if e.get("desc") and e.get("desc") != e.get("texto"):
        partes.append(f'({e["desc"]})')
    if e.get("id"):
        partes.append("#" + e["id"])
    partes.append(f'{e["x"]},{e["y"]}')
    sinais = "".join(c for k, c in SINAIS if e.get(k))
    if e.get("marcado") is not None:
        sinais += "M" if e["marcado"] else "m"
    if sinais:
        partes.append(sinais)
    return " ".join(partes)


def diferenca_curta(dif):
    linhas = [f"+ {curto(e)}" for e in dif["entrou"]] + [f"- {curto(e)}" for e in dif["saiu"]]
    for e in dif["mudou"]:
        antes = e.get("antes", {})
        agora = {k: v for k, v in e.items() if k != "antes"}
        if set(antes) == {"texto"}:
            linhas.append(f'~ {curto(agora)} (era "{antes["texto"]}")')
        else:
            linhas.append(f"~ {curto(agora)} (era {', '.join(f'{k}={v}' for k, v in antes.items())})")
    return linhas


# --------------------------------------------------------------------------- tabuleiro de xadrez (acessibilidade)
_PECAS = {"rei": "k", "dama": "q", "torre": "r", "bispo": "b", "cavalo": "n", "peao": "p",
          "king": "k", "queen": "q", "rook": "r", "bishop": "b", "knight": "n", "pawn": "p"}
_CASA_PECA = re.compile(r"^(brancas|pretas|white|black) (\w+) (?:em|on) ([a-h][1-8])$")
_CASA_VAZIA = re.compile(r"^([a-h][1-8]),? (?:vazio|vazia|empty)$")
_RELOGIO = re.compile(r"^\d{1,2}:\d\d(\.\d)?$")


def casas_xadrez(els):
    """{casa: (x, y, peça)} dos apps que descrevem cada casa ("Brancas Cavalo em f3", "e4, vazio"); peça em FEN
    (maiúscula = brancas, '' = vazia). None se não houver um tabuleiro inteiro na tela."""
    casas = {}
    for e in els:
        d = normalizar(e.get("desc") or e.get("texto") or "")
        m = _CASA_PECA.match(d)
        if m and m.group(2) in _PECAS:
            pc = _PECAS[m.group(2)]
            casas[m.group(3)] = (e["x"], e["y"], pc.upper() if m.group(1) in ("brancas", "white") else pc)
            continue
        m = _CASA_VAZIA.match(d)
        if m:
            casas[m.group(1)] = (e["x"], e["y"], "")
    return casas if len(casas) == 64 else None


def tabuleiro_curto(els):
    """O tabuleiro em 8 linhas (8ª fileira primeiro, FEN: KQRBNP brancas, kqrbnp pretas, . vazia), os relógios
    (esquerda → direita, como aparecem) e os últimos lances escritos na tela. Sem tabuleiro: os textos da tela."""
    casas = casas_xadrez(els)
    if not casas:
        return {"textos": [e["texto"] for e in els if e.get("texto")][:25]}
    linhas = ["".join(casas[f"{c}{r}"][2] or "." for c in "abcdefgh") + f" {r}" for r in range(8, 0, -1)]
    rel = sorted((e for e in els if _RELOGIO.match(e.get("texto") or "")), key=lambda e: (e["y"], e["x"]))
    banda = [e for e in els if e.get("texto") and re.match(r"^(O-O(-O)?|[KQRBNkqrbn]?[a-h]?[1-8]?x?[a-h][1-8](=[QRBNqrbn])?)[+#]?$",
                                                         e["texto"])]
    banda.sort(key=lambda e: e["x"])
    return {"tabuleiro": linhas + ["abcdefgh"], "relogios": [e["texto"] for e in rel],
            "ultimos": [e["texto"] for e in banda][-2:]}


TECLADO = re.compile(r"SoftInputWindow|InputMethod", re.I)


def janela_nova(antes, depois, app=None):
    """A janela que surgiu é outra coisa (aviso, anúncio, outro app), e não a mesma tela se anunciando de novo?"""
    pa, ca = (antes.split("|") + ["", ""])[:2]
    pd, cd = (depois.split("|") + ["", ""])[:2]
    if (pd, cd) == (pa, ca) or TECLADO.search(cd):
        return False
    if not ca:  # sem referência da janela de antes: só o que claramente é outra coisa
        return bool(pd != (app or pd) or re.search(r"Dialog|Popup|Alert|Sheet|Window", cd))
    return True


# --------------------------------------------------------------------------- grade de algarismos (lida no celular)
SIMBOLOS = "123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def teclado_da_grade(els, regiao, n=None):
    """Os botões de símbolo do jogo: uma fileira de 4+ clicáveis do mesmo tamanho, lado a lado, logo abaixo da grade.
    Com n: a fileira de exatamente n botões, se houver; senão a maior (e a mais de baixo no empate).
    [(x, y, l, a)] da esquerda para a direita, ou None."""
    baixo = regiao[1] + regiao[3]
    cands = [e for e in els if e.get("clicavel") and baixo < e["y"] < baixo + 900 and 0 < e.get("l", 0) < regiao[2] / 3]
    linhas = {}
    for e in cands:
        linhas.setdefault(round(e["y"] / 25), []).append(e)
    grupos = []
    for grupo in linhas.values():
        med = sorted(e["l"] for e in grupo)[len(grupo) // 2]
        grupo = [e for e in grupo if abs(e["l"] - med) <= 0.25 * med]
        if len(grupo) >= 4:
            grupos.append(grupo)
    if not grupos:
        return None
    exatos = [g for g in grupos if n and len(g) == n]
    melhor = max(exatos or grupos, key=lambda g: (len(g), g[0]["y"]))
    return [(e["x"], e["y"], e["l"], e["a"]) for e in sorted(melhor, key=lambda e: e["x"])]


def _caixa(n):
    """Dimensões do bloco: 9 → 3x3, 16 → 4x4, 6 → 2x3, 8 → 2x4, 12 → 3x4."""
    br = max(d for d in range(1, int(n ** 0.5) + 1) if n % d == 0)
    return br, n // br


def resolver_grade(g, prazo=10.0):
    """Sudoku NxN (listas, 0 = vazia; 9x9, 16x16, 6x6…) → solução, ou None (repetido, sem solução ou difícil demais
    para o prazo). Máscaras de bits e a casa com menos opções primeiro."""
    n = len(g)
    br, bc = _caixa(n)
    nb = n // bc
    g = [list(r) for r in g]
    lin, col, cx = [0] * n, [0] * n, [0] * n
    for r in range(n):
        for c in range(n):
            v = g[r][c]
            if v:
                b, k = 1 << (v - 1), (r // br) * nb + c // bc
                if lin[r] & b or col[c] & b or cx[k] & b:
                    return None  # repetido: leitura errada
                lin[r] |= b
                col[c] |= b
                cx[k] |= b
    todos = (1 << n) - 1
    fim = time.time() + prazo

    def busca(vazias):
        if not vazias:
            return True
        if time.time() > fim:
            raise TimeoutError
        mi, mm, mk = 0, 0, 99
        for i, (r, c) in enumerate(vazias):
            m = todos & ~(lin[r] | col[c] | cx[(r // br) * nb + c // bc])
            k = bin(m).count("1")
            if k < mk:
                mi, mm, mk = i, m, k
                if k <= 1:
                    break
        if mk == 0:
            return False
        r, c = vazias[mi]
        resto = vazias[:mi] + vazias[mi + 1:]
        k = (r // br) * nb + c // bc
        while mm:
            b = mm & -mm
            mm ^= b
            g[r][c] = b.bit_length()
            lin[r] |= b
            col[c] |= b
            cx[k] |= b
            if busca(resto):
                return True
            lin[r] ^= b
            col[c] ^= b
            cx[k] ^= b
        g[r][c] = 0
        return False

    try:
        return g if busca([(r, c) for r in range(n) for c in range(n) if not g[r][c]]) else None
    except (TimeoutError, RecursionError):
        return None


def resolver_sudoku(g):  # compatibilidade
    return resolver_grade(g)


def _conflitos(g):
    """Casas envolvidas em repetições (linha, coluna ou bloco)."""
    n = len(g)
    br, bc = _caixa(n)
    ruins = set()
    grupos = [[(r, c) for c in range(n)] for r in range(n)] + [[(r, c) for r in range(n)] for c in range(n)]
    grupos += [[(r, c) for r in range(R, R + br) for c in range(C, C + bc)] for R in range(0, n, br) for C in range(0, n, bc)]
    for grupo in grupos:
        vistos = {}
        for r, c in grupo:
            v = g[r][c]
            if v > 0:
                if v in vistos:
                    ruins |= {vistos[v], (r, c)}
                vistos[v] = (r, c)
    return ruins


def _ler_grade(aj, reg, n, k):
    """Grade lida pelos modelos guardados: (g, dúvidas {(r,c): (segundo, margem)}, desconhecidas {(r,c)}).
    g[r][c]: 0 vazia, -1 desconhecida (sem modelo), senão o símbolo (1..k)."""
    r = aj.pedir(f"ler {n} {int(reg[0])} {int(reg[1])} {int(reg[2])} {int(reg[3])} {k}", 15)
    if not r or r.startswith("ERRO"):
        return None, {}, set()
    g, duv, desc = [], {}, set()
    for i, linha in enumerate(r.strip().split("\n")[:n]):
        campos = linha.split()
        if len(campos) != n:
            return None, {}, set()
        lin = []
        for j, cpo in enumerate(campos):
            if cpo == "?":
                lin.append(-1)
                desc.add((i, j))
                continue
            partes = cpo.split(":")
            lin.append(int(partes[0]))
            if len(partes) == 3:
                duv[(i, j)] = (int(partes[1]), int(partes[2]))
        g.append(lin)
    return (g if len(g) == n else None), duv, desc


def _teclado_parado(reg, ate=1.5):
    """O teclado depois de um deslize: duas leituras iguais seguidas (a fileira ainda pode estar rolando)."""
    novo, prev, fim = None, None, time.time() + ate
    while time.time() < fim:
        novo = teclado_da_grade(elementos(dump_ui(), limite=300), reg)
        pos = [t[0] for t in novo] if novo else None
        if pos and pos == prev:
            break
        prev = pos
        time.sleep(0.1)
    return novo


# modelos do teclado já guardados no leitor: {chave: (token do leitor, páginas, total, geometria)}. Jogo seguinte do
# mesmo app com o mesmo teclado na 1ª página → não relê nem desliza (economiza ~3 s por partida no 16x16).
_TECLADOS = {}


def _modelos_do_teclado(aj, reg, els, n=None, tec=None):
    """Guarda os modelos de todas as páginas do teclado (desliza a fileira se ela rola) e volta à 1ª página.
    Devolve (páginas [(primeiro_simbolo_0based, botões)], total de símbolos, geometria do deslize)."""
    aj.pedir("limparmodelos", 5)
    dado = tec is not None
    tec = tec or teclado_da_grade(els, reg, n)
    if not tec:
        return [], 0, None
    x0 = min(t[0] - t[2] // 2 for t in tec)
    x1 = max(t[0] + t[2] // 2 for t in tec)
    m = max(100, (x1 - x0) // 10)  # longe das bordas: deslize que começa na borda é o gesto "voltar" do Android
    x0, x1 = x0 + m, x1 - m
    y = tec[0][1]
    rola = not dado and any(e.get("rolavel") and abs(e["y"] - y) < 60 for e in els)
    if rola:  # a fileira pode estar numa página do meio (deixada assim): volta até a 1ª
        for _ in range(3):
            _injetar(f"deslizar {x0} {y} {x1} {y} 450")
            calma(100, 1200)
            antes = tec
            tec = _teclado_parado(reg) or tec
            if [t[0] for t in tec] == [t[0] for t in antes]:
                break
    paginas, total = [], 0
    for _ in range(4):
        topo = min(t[1] - t[3] // 2 for t in tec)
        alt = max(t[3] for t in tec)
        xa = min(t[0] - t[2] // 2 for t in tec)
        xb = max(t[0] + t[2] // 2 for t in tec)
        aj.pedir(f"modelos {total} {len(tec)} {xa} {topo} {xb - xa} {alt}", 15)
        paginas.append((total, tec))
        total += len(tec)
        if not rola or (n and total >= n):
            break
        _injetar(f"deslizar {x1} {y} {x0} {y} 450")  # próxima página do teclado
        calma(100, 1200)
        novo = _teclado_parado(reg)
        if not novo or [t[0] for t in novo] == [t[0] for t in tec]:
            break  # não mudou: não há outra página
        tec = novo
    for _ in range(len(paginas) - 1):  # volta à primeira página
        _injetar(f"deslizar {x0} {y} {x1} {y} 450")
        calma(100, 1200)
    return paginas, total, (x0, x1, y)


def _plano(casas, sol, reg, paginas, geo, pagina_atual, intervalo, pressao):
    """Passos para preencher `casas` com a solução, página por página do teclado. (passos, página final)."""
    n = len(sol)

    def centro(i, j):
        return [int(reg[0] + reg[2] * (j + 0.5) / n), int(reg[1] + reg[3] * (i + 0.5) / n)]

    por_pagina = {}
    for i, j in casas:
        v = sol[i][j] - 1
        for p, (ini, tec) in enumerate(paginas):
            if ini <= v < ini + len(tec):
                b = tec[v - ini]
                por_pagina.setdefault(p, []).extend([centro(i, j), [b[0], b[1]]])
                break
    passos, atual = [], pagina_atual
    ordem = sorted(por_pagina, key=lambda p: (p != atual, p))
    for p in ordem:
        while atual != p and geo:
            x0, x1, y = geo
            d = [x1, y, x0, y, 450] if p > atual else [x0, y, x1, y, 450]
            passos += [{"calma": 0.3}, {"deslizar": d, "confiar": True}, {"calma": 0.8}]
            atual += 1 if p > atual else -1
        passos.append({"tocar": por_pagina[p], "intervalo": intervalo, "pressao": pressao, "confiar": True})
    return passos, atual


def grade(a):
    """Lê no celular uma grade NxN de símbolos desenhados (tabuleiro sem texto na acessibilidade): os modelos vêm dos
    botões do próprio jogo (todas as páginas do teclado, deslizando a fileira) e ficam guardados. Espera a grade ficar
    estável (avisos do app são dispensados pelos reflexos guardados; anúncio é fechado). antes=[passos] roda o preparo
    na mesma chamada. resolver=true: resolve (9x9, 16x16, 6x6…), preenche página por página, relê e repete o que não
    pegou. n é descoberto pelo teclado (símbolos de todas as páginas) se não for informado."""
    aj = _ajudante()
    if not aj:
        return {"erro": "precisa do leitor rápido (Shizuku)"}
    t0 = time.time()
    tempos = {}
    antes = None
    if a.get("antes"):
        antes = sequencia({"passos": a["antes"], "ver_depois": "nada"})
        tempos["preparo"] = round(time.time() - t0, 2)
    n_pedido = int(a["n"]) if a.get("n") else None
    limite = time.time() + min(float(a.get("ate", 12)), 40)
    reg = tec = els = None
    usados = []
    while time.time() < limite:  # a grade e o teclado à vista (sem aviso por cima)
        if em_anuncio():
            fechar_anuncio(foco())
            continue
        xml = dump_ui()
        els = elementos(xml, limite=300)
        reg = a.get("recorte") or (regioes_visuais(xml) or [None])[0]
        tec = (a.get("teclado") or teclado_da_grade(els, reg, n_pedido)) if reg else None
        if reg and tec:
            break
        r = aplicar_regras(els=els)
        if r:
            usados.append(r)
            continue
        time.sleep(0.15)
    if not (reg and tec):
        return {"erro": "não achei a grade e o teclado do jogo", **({"antes": antes} if antes and antes.get("erro") else {}),
                **({"reflexos": usados} if usados else {})}
    t1 = time.time()
    chave = (n_pedido, tuple(int(v) for v in reg), tuple(tuple(int(v) for v in t) for t in tec))
    guardado = _TECLADOS.get(chave)
    if guardado and guardado[0] == aj.token and not a.get("teclado"):
        _, paginas, total, geo = guardado
        tempos["teclado"] = "guardado"
    else:
        paginas, total, geo = _modelos_do_teclado(aj, reg, els, n_pedido, a.get("teclado"))
        if total and (not n_pedido or total >= n_pedido):
            _TECLADOS.clear()
            _TECLADOS[chave] = (aj.token, paginas, total, geo)
    n = n_pedido or total
    if total < n:
        return {"erro": f"o teclado tem {total} símbolos e a grade precisa de {n}"}
    g, duv, anterior = None, {}, None
    while time.time() < limite + 5:  # leitura estável: duas iguais seguidas (a grade entra animada)
        g, duv, desc = _ler_grade(aj, reg, n, total)
        if g and g == anterior and any(v > 0 for ln in g for v in ln):
            break
        anterior = g
        time.sleep(0.12)
    else:
        return {"erro": "a grade não ficou estável a tempo"}
    tempos["ler"] = round(time.time() - t1, 2)
    simb = lambda v: "." if v == 0 else ("?" if v < 0 else SIMBOLOS[v - 1])  # noqa: E731
    texto = lambda gg: ["".join(simb(v) for v in ln) for ln in gg]  # noqa: E731
    out = {"n": n, "vazias": sum(1 for ln in g for v in ln if v == 0)}
    if usados:
        out["reflexos"] = usados
    if not a.get("resolver"):
        return {**out, "grade": texto(g), **({"duvidas": [f"{i},{j}→{SIMBOLOS[s - 1]}?" for (i, j), (s, _) in duv.items()]}
                                            if duv else {}), "tempos": tempos}
    t2 = time.time()
    ruins = _conflitos(g)
    for (i, j) in sorted(ruins & set(duv), key=lambda c: duv[c][1]):  # repetido numa casa duvidosa: tenta o 2º
        g[i][j] = duv[(i, j)][0]
        out.setdefault("corrigidas", []).append(f"{i},{j}")
        if not _conflitos(g):
            break
    sol = resolver_grade([[max(v, 0) for v in ln] for ln in g]) if not any(v < 0 for ln in g for v in ln) else None
    tempos["resolver"] = round(time.time() - t2, 2)
    if not sol:
        _TECLADOS.pop(chave, None)  # modelos talvez ruins: a próxima vez relê o teclado
        return {**out, "erro": "a grade lida não tem solução (leitura duvidosa)", "grade": texto(g),
                **({"duvidas": [f"{i},{j}" for (i, j) in duv]} if duv else {}), "tempos": tempos}
    vazias = [(i, j) for i in range(n) for j in range(n) if g[i][j] == 0]
    if not vazias:
        return {**out, "feito": "nada a preencher", "tempos": tempos}
    janela = (eventos() or (0, 0, None))[2]
    _ULTIMA["janela"] = janela  # as coordenadas acabaram de ser lidas desta tela
    t3 = time.time()
    intervalo, pressao = float(a.get("intervalo", 0.008)), int(a.get("pressao", 12))
    passos, pagina = _plano(vazias, sol, reg, paginas, geo, 0, intervalo, pressao)
    r2 = sequencia({"passos": passos, "ver_depois": "nada"})
    tempos["preencher"] = round(time.time() - t3, 2)
    if r2.get("erro") or r2.get("interrompido"):
        return {**out, **r2, "tempos": tempos}
    # conferência com os modelos guardados (os botões somem quando um símbolo se completa; os modelos ficam)
    if a.get("conferir", True):
        calma(80, 400)
        ev = eventos()
        if not ev or ev[2] != janela:
            out["concluido"] = True  # a tela mudou (resultado do jogo)
        else:
            lido, _, _ = _ler_grade(aj, reg, n, total)
            faltam = [(i, j) for i, j in vazias if lido and lido[i][j] == 0]
            if not faltam:
                out["conferido"] = True
            elif len(faltam) <= 8:
                pr, _ = _plano(faltam, sol, reg, paginas, geo, pagina, 0.05, 30)
                sequencia({"passos": pr, "ver_depois": "nada"})
                out["refeitos"] = len(faltam)
                out["conferido"] = True
            else:
                out["conferencia"] = "inconclusiva (a tela estava animando)"
    tempos["total"] = round(time.time() - t0, 2)
    out["tempos"] = tempos
    return out


# --------------------------------------------------------------------------- anúncios (resolvidos no celular)
ANUNCIO = re.compile(r"AppLovinFullscreen|TTFullScreen|TTRewardVideo|TTLandingPage|\.AdActivity|FullScreenWebViewDisplay|"
                     r"MBRewardVideo|MBInterstitial|MBCommonActivity|Inneractive|Vungle|AdColony|AudienceNetworkActivity|"
                     r"AdUnitActivity|InterstitialActivity|RewardedVideoActivity|MaxFullscreen|BigoAd|PAGInterstitial|"
                     r"PAGReward|UnityAds|IronSource|AdsActivity", re.I)
IGNORAR_APP = re.compile(r"systemui|securitycenter|inputmethod|permissioncontroller|^android$", re.I)
FECHAR = ("fechar", "close", "pular", "skip", "dispensar", "anuncio fechado", "fechar anuncio")
NAO_TOCAR = ("instalar", "install", "baixar", "baixe", "download", "obter", "peca agora", "saiba mais", "learn more",
             "abrir", "open", "get now", "jogar agora", "play now", "comprar")


def classe_janela(info):
    return (info.split("|") + ["", ""])[1]


def atividade_no_topo():
    """A atividade de fato em primeiro plano (o último evento de janela pode ser da barra do sistema por cima)."""
    out, _, _ = rish("dumpsys activity activities | grep -m1 topResumedActivity", timeout=10)
    m = re.search(r"\s([\w.]+)/([\w.$]+)", out or "")
    return (m.group(1), m.group(2)) if m else (None, None)


def em_anuncio(certeza=False):
    """Há anúncio em primeiro plano? Rápido pelo último evento; se ele veio do sistema (notificação, gravador de
    tela) ou certeza=True, confere a atividade no topo de verdade."""
    ev = eventos()
    if ev and ANUNCIO.search(classe_janela(ev[2])):
        return True
    if certeza or (ev and IGNORAR_APP.search(ev[2].split("|")[0] or "")):
        return bool(ANUNCIO.search(atividade_no_topo()[1] or ""))
    return False


def botao_fechar(els):
    """O botão de fechar/pular do anúncio: pelo nome; senão um elemento pequeno e ativo no canto superior direito.
    Nunca o que leva para fora (instalar, baixar, peça agora…)."""
    if not els:
        return None
    larg = max(e["x"] + e.get("l", 0) // 2 for e in els)
    alt = max(e["y"] + e.get("a", 0) // 2 for e in els)
    for e in els:
        t = normalizar(e.get("texto") or e.get("desc"))
        if e.get("desativado") or any(n in t for n in NAO_TOCAR):
            continue
        if t in ("x", "×", "✕", "»", ">>") or any(f in t for f in FECHAR):
            return e
    for e in els:
        t = normalizar(e.get("texto") or e.get("desc"))
        if (not e.get("desativado") and not re.search(r"\d+\s*s$", t) and e["y"] < 0.12 * alt and e["x"] > 0.82 * larg
                and 0 < e.get("l", 999) < 0.15 * larg and 0 < e.get("a", 999) < 0.08 * alt):
            return e
    return None


def _abrir(pac):
    rish(f"monkey -p {pac} -c android.intent.category.LAUNCHER 1")


def fechar_anuncio(pacote, limite=45):
    """Fica no anúncio até fechá-lo: toca o botão de fechar/pular quando aparece (pelo nome ou no canto, nunca no
    anúncio), volta ao app se um toque abrir outro (loja, WhatsApp) e, passado o limite, encerra e reabre o app."""
    t0, feitos, tocados = time.time(), [], {}
    while time.time() - t0 < limite:
        app = foco()
        if app and pacote and app != pacote and not IGNORAR_APP.search(app):
            feitos.append(f"saiu para {app}: voltou")
            _abrir(pacote)
            calma(150, 2500)
            continue
        if not em_anuncio(certeza=True):
            return {"anuncio": "fechado", "segundos": round(time.time() - t0, 1), "passos": feitos}
        b = botao_fechar(elementos(dump_ui()))
        chave = (b["x"], b["y"]) if b else None
        if b and time.time() - tocados.get(chave, 0) > 2:
            tocados[chave] = time.time()
            _injetar(f"tocar {b['x']} {b['y']}")
            feitos.append(f"tocou fechar {b['x']},{b['y']}")
            calma(150, 1500)
            continue
        time.sleep(0.5)
    if pacote:
        rish(f"am force-stop {pacote}")
        _abrir(pacote)
        calma(200, 4000)
        e = achar(elementos(dump_ui()), "Continuar")
        if e:
            _injetar(f"tocar {e['x']} {e['y']}")
            calma(150, 3000)
        feitos.append("anúncio preso: encerrou e reabriu o app" + (" e tocou Continuar" if e else ""))
    return {"anuncio": "encerrado", "segundos": round(time.time() - t0, 1), "passos": feitos}


def tela_acesa():
    out, _, _ = rish("dumpsys power | grep -m1 mWakefulness=")
    return "Awake" in out if out else None


def bloqueados():
    try:
        with open(BLOQUEADOS_ARQ) as f:
            return json.load(f)
    except (OSError, ValueError):
        return BLOQUEADOS_PADRAO


def dump_ui():
    a = _ajudante()
    if a:  # leitura direta da acessibilidade: ~0,05 s, sem esperar a tela parar
        x = a.pedir("dump", 10)
        if x and x.startswith("<?xml") and "<node" in x:
            return x
    arq = os.path.join(_pasta_troca(), f"ui-{os.getpid()}.xml")
    for _ in range(2):
        try:
            rish(f"uiautomator dump {shlex.quote(arq)}", timeout=25)
            xml = _ler(arq) or ""
        finally:
            _apagar(arq)
        if xml.strip().startswith("<?xml"):
            return xml
        time.sleep(0.8)
    return ""


def _jpeg(png, largura, recorte=None):
    """PNG da captura → JPEG em base64 (≤110 KB), com recorte opcional [x, y, l, a] em pixels reais."""
    os.makedirs(TMP, exist_ok=True)
    jpg = os.path.join(TMP, f"tela-{os.getpid()}-{time.monotonic_ns()}.jpg")  # nome único: a transmissão ao
    try:                                                                          # vivo captura ao mesmo tempo
        try:
            with open(png, "rb") as f:
                if not f.read(8).startswith(b"\x89PNG"):
                    return None
        except OSError:
            return None
        filtro = f"scale='min({largura},iw)':-2"
        if recorte:
            x, y, l, a = (max(0, int(v)) for v in recorte)
            filtro = f"crop={l}:{a}:{x}:{y}," + filtro
        for q in (6, 10, 16):
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", png, "-vf", filtro, "-q:v", str(q), jpg],
                           capture_output=True, timeout=30, check=False)
            if os.path.exists(jpg) and os.path.getsize(jpg) <= 110_000:
                break
        if not os.path.exists(jpg):
            return None
        with open(jpg, "rb") as f:
            return base64.b64encode(f.read()).decode()
    finally:
        _apagar(jpg)


def foto_rapida(largura, recorte=None):
    """JPEG direto do leitor rápido (sem PNG nem ffmpeg). Devolve (base64, "LxA") ou (None, None)."""
    a = _ajudante()
    if not a:
        return None, None
    arq = os.path.join(_pasta_troca(), f"foto-{os.getpid()}-{time.monotonic_ns()}.jpg")
    rec = " " + " ".join(str(max(0, int(v))) for v in recorte) if recorte else ""
    try:
        r = a.pedir(f"foto {int(largura)} 110000 {arq}{rec}", 15)
        if not r or r.startswith("ERRO") or not os.path.exists(arq):
            return None, None
        with open(arq, "rb") as f:
            dados = f.read()
        lw, lh = r.split()[:2]
        return base64.b64encode(dados).decode(), f"{lw}x{lh}"
    except (OSError, ValueError):
        return None, None
    finally:
        _apagar(arq)


def captura(largura):
    """Só a imagem (usada pela transmissão ao vivo da Central). Sem imagem: (None, None)."""
    b64, _ = foto_rapida(largura)
    if b64:
        return b64, largura
    png = os.path.join(_pasta_troca(), f"tela-{os.getpid()}-{time.monotonic_ns()}.png")
    try:
        rish(f"screencap -p {shlex.quote(png)}", timeout=20)
        b64 = _jpeg(png, largura)
        return (b64, largura) if b64 else (None, None)
    finally:
        _apagar(png)


def resolucao_png(png):
    try:
        with open(png, "rb") as f:
            cab = f.read(24)
        return f"{int.from_bytes(cab[16:20], 'big')}x{int.from_bytes(cab[20:24], 'big')}" if cab[:4] == b"\x89PNG" else None
    except OSError:
        return None


def compactos(els):
    """Elementos sem campos vazios (menos texto na resposta)."""
    out = []
    for e in els:
        d = {k: e[k] for k in ("texto", "desc", "id") if e.get(k)}
        if e.get("clicavel"):
            d["clicavel"] = True
        for k in ("editavel", "selecionado", "rolavel", "focado", "desativado"):
            if e.get(k):
                d[k] = True
        if e.get("marcado") is not None:
            d["marcado"] = e["marcado"]
        d["x"], d["y"] = e["x"], e["y"]
        out.append(d)
    return out


def observar(com_elementos=True, com_imagem=True):
    """Dump da interface, captura PNG (se pedida), app em foco e tela acesa.
    Com o leitor rápido: dump e estado direto da acessibilidade, sem shell (o PNG só se a foto rápida falhou).
    Sem ele: UMA chamada ao Shizuku com tudo em paralelo. Devolve (xml, caminho_png, app, acesa); quem chama apaga o PNG."""
    pasta = _pasta_troca()
    nome = f"obs-{os.getpid()}-{time.monotonic_ns()}"
    xml, png = os.path.join(pasta, nome + ".xml"), os.path.join(pasta, nome + ".png")
    if _ajudante():
        texto = dump_ui() if com_elementos else ""
        est = estado_rapido()
        partes = [f"screencap -p {shlex.quote(png)}"] if com_imagem else []
        if est is None:
            partes += ["dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'", "dumpsys power | grep -m1 mWakefulness="]
        info = rish("\n".join(partes), timeout=30)[0] if partes else ""
        app, acesa = est if est else (app_em_foco(info), "Awake" in (info or ""))
        return texto, (png if com_imagem else None), app, acesa
    partes = []
    if com_elementos:
        partes.append(f"(uiautomator dump {shlex.quote(xml)} > /dev/null 2>&1) &")
    if com_imagem:
        partes.append(f"screencap -p {shlex.quote(png)}")
    partes += ["dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'", "dumpsys power | grep -m1 mWakefulness=", "wait"]
    try:
        info, _, _ = rish("\n".join(partes), timeout=30)
        texto = _ler(xml) or "" if com_elementos else ""
    finally:
        _apagar(xml)
    if com_elementos and not texto.strip().startswith("<?xml"):
        texto = dump_ui()  # o dump às vezes falha na primeira (tela em animação)
    return texto, (png if com_imagem else None), app_em_foco(info), "Awake" in (info or "")


# última tela vista (para responder só o que mudou); vive enquanto o módulo fica aberto no serviço
_ULTIMA = {"app": None, "els": None}


def _chave(e):
    return e.get("id", ""), e["x"], e["y"]


def diferenca(antes, depois, app_antes=None, app=None):
    """O que mudou entre duas listas compactas: entrou, saiu e mudou (com o valor anterior). None = tela nova
    (outro app, primeira olhada ou mudança grande demais: aí vale mandar a lista inteira)."""
    if antes is None or app != app_antes:
        return None
    a = {_chave(e): e for e in antes}
    d = {_chave(e): e for e in depois}
    entrou = [e for k, e in d.items() if k not in a]
    saiu = [{c: e[c] for c in ("texto", "desc", "id", "x", "y") if e.get(c) not in (None, "")}
            for k, e in a.items() if k not in d]
    mudou = []
    for k, e in d.items():
        if k in a and e != a[k]:
            v = a[k]
            mudou.append(dict(e, antes={c: v.get(c) for c in set(e) | set(v) if e.get(c) != v.get(c)}))
    if len(entrou) + len(saiu) + len(mudou) > max(25, int(0.6 * len(depois))):
        return None
    return {"entrou": entrou, "saiu": saiu, "mudou": mudou}


def _linha_do_tempo():
    """O que surgiu (janelas) desde a última olhada, para nada passar enquanto o Claude pensava."""
    ev = eventos()
    if ev is None:
        return []
    agora, desde = ev[3], _ULTIMA.get("t")
    _ULTIMA["t"], _ULTIMA["janela"] = agora, ev[2]  # a janela que o Claude viu: referência das coordenadas
    if desde is None:
        return []
    linhas, anterior = [], None
    for t, info in historico(desde):
        if info != anterior:
            linhas.append(f"-{(agora - t) / 1000:.1f}s {_janela_curta(info)}")
        anterior = info
    return linhas[-8:]


def ver(imagem=True, largura=720, com_elementos=True, recorte=None, so_mudancas=False, formato="curto"):
    rapida = foto_rapida(largura, recorte) if imagem and _ajudante() else (None, None)
    xml, png, app, acesa = observar(com_elementos, imagem and not rapida[0])
    out = {"app": app, "tela_acesa": acesa}
    if _privado(app):  # app de banco/senha em primeiro plano: nem imagem nem elementos saem do celular
        if png:
            _apagar(png)
        out["privado"] = "app bloqueado (banco, pagamento ou senha) em primeiro plano: a tela não foi lida"
        _ULTIMA.update(app=app, els=[], regioes=[])
        return out
    tempo = _linha_do_tempo()
    if tempo:
        out["surgiu"] = tempo
    json_ = formato == "json"
    try:
        if rapida[0]:
            out["resolucao"] = rapida[1]
            out["_imagem"] = {"mime": "image/jpeg", "base64": rapida[0]}
            out["largura_imagem"] = largura
            if recorte:
                out["recorte"] = list(recorte)
        if png:
            out["resolucao"] = resolucao_png(png)
        if com_elementos:
            els = compactos(elementos(xml))
            dif = diferenca(_ULTIMA["els"], els, _ULTIMA["app"], app) if so_mudancas else None
            if dif is None:
                out["elementos"] = els if json_ else [curto(e) for e in els]
                out["nota"] = "x,y em pixels reais (use em tocar)" + ("" if json_ else "; " + LEGENDA)
            elif any(dif.values()):
                out["mudancas"] = {k: v for k, v in dif.items() if v} if json_ else diferenca_curta(dif)
                out["sem_mudar"] = len(els) - len(dif["entrou"]) - len(dif["mudou"])
            else:
                out["mudancas"] = "nenhuma"
            _ULTIMA.update(app=app, els=els, regioes=regioes_visuais(xml))
        if imagem and not rapida[0]:
            b64 = _jpeg(png, largura, recorte)
            if b64:
                out["_imagem"] = {"mime": "image/jpeg", "base64": b64}
                out["largura_imagem"] = largura
                if recorte:
                    out["recorte"] = list(recorte)
            else:
                out["imagem_erro"] = ("screencap não devolveu imagem (app com proteção de tela mostra preto, ou o "
                                      "Termux sem acesso ao armazenamento: rode termux-setup-storage)")
    finally:
        if png:
            _apagar(png)
    return out


def _ver_depois(a, padrao=None, tocados=()):
    """Depois de agir, espera a tela assentar (leitor rápido) e olha. 'auto' (padrão com o leitor): só o que mudou e,
    se a tela tem área visual sem texto (tabuleiro, jogo), a imagem SÓ desse recorte quando a tela é nova ou a ação
    tocou nela. 'mudancas' (sem imagem), 'elementos' (lista inteira), 'imagem' (lista + captura) ou 'nada'."""
    if padrao is None:
        padrao = "auto" if _ajudante() else "nada"
    fechado = None
    if _ajudante() and a.get("anuncios", True) is not False and (a.get("ver_depois") or padrao) != "nada" and em_anuncio():
        fechado = fechar_anuncio(foco())
    if (a.get("ver_depois") or padrao) == "auto":
        esperou = calma(int(a.get("calma_ms", 120)), int(a.get("calma_ate", 1000))) if a.get("calma", True) else None
        tela = ver(False, 480, True, None, so_mudancas=True, formato=a.get("formato", "curto"))
        reg = (_ULTIMA.get("regioes") or [None])[0]
        if reg and not tela.get("privado") and ("elementos" in tela or any(dentro(p, reg) for p in tocados)):
            b64, res = foto_rapida(min(720, max(320, int(a.get("largura", 480)))), reg)
            if b64:
                tela["_imagem"] = {"mime": "image/jpeg", "base64": b64}
                tela["recorte"] = reg
        return {"tela": tela, **({"calma_ms": esperou} if esperou is not None else {}),
                **({"anuncio_fechado": fechado} if fechado else {})}
    if a.get("ver_depois") == "tabuleiro":  # xadrez: 8 linhas + relógios, sem a lista de elementos
        return {"app": foco(), **tabuleiro_curto(elementos(dump_ui(), limite=300))}
    modo = a.get("ver_depois") or ("imagem" if a.get("imagem") else padrao)
    esperou = None
    if modo != "nada" and a.get("calma", True) is not False:
        esperou = calma(int(a.get("calma_ms", 120)), int(a.get("calma_ate", 1000)))
    extra = {"calma_ms": esperou} if esperou is not None else {}
    if modo == "nada":
        return {"app": foco()}
    largura = max(320, min(int(a.get("largura", 720)), 1080))
    return {"tela": ver(modo == "imagem", largura, True, a.get("recorte"), so_mudancas=(modo == "mudancas"),
                        formato=a.get("formato", "curto")), **extra}


# --------------------------------------------------------------------------- sequência (vários passos, 1 viagem)
MAX_PASSOS = 300  # passos na lista (contando os aninhados)
MAX_EXECUTADOS = 3000  # passos executados (laços incluídos)
PRAZO_SEQUENCIA = 140  # s (o tempo_limite da capacidade é 150)


def _regex_bloqueados(lista):
    alt = "|".join(re.escape(b) for b in lista if re.match(r"^[\w.]+$", b))
    return f"[ {{/]({alt})[A-Za-z0-9_.]*/" if alt else None


def _linhas_do_passo(p):
    """Linhas de shell de um passo que não depende de ler a tela (caminho sem o leitor rápido).
    None = passo que precisa da tela ou do leitor (texto, condição, laço)."""
    if "tocar" in p:
        alvo = p["tocar"]
        if isinstance(alvo, str):
            return None
        pontos = alvo if alvo and isinstance(alvo[0], (list, tuple)) else [alvo]
        pausa = float(p.get("intervalo", 0.05))
        linhas = []
        for x, y in pontos:
            if p.get("segurar"):
                ms = int(p["segurar"])
                linhas.append(f"input swipe {int(x)} {int(y)} {int(x)} {int(y)} {ms} || exit 3")
            else:
                linhas.append(f"input tap {int(x)} {int(y)} || exit 3")
            if pausa > 0:
                linhas.append(f"sleep {min(pausa, 5):.2f}")
        return linhas
    if "deslizar" in p:
        v = [int(n) for n in p["deslizar"]]
        return [f"input swipe {v[0]} {v[1]} {v[2]} {v[3]} {v[4] if len(v) > 4 else 300} || exit 3"]
    if "digitar" in p:
        if _ajudante():
            return None  # pelo leitor: vai no campo em foco, com acentos
        texto, _ = escapar_input_text(str(p["digitar"]))
        return [f"input text {shlex.quote(texto)} || exit 3"] if texto else []
    if "tecla" in p:
        cod = TECLAS.get(normalizar(p["tecla"]))
        if cod is None:
            raise ValueError(f"tecla deve ser uma de: {', '.join(TECLAS)}")
        return [f"input keyevent {cod} || exit 3"]
    if "esperar" in p:
        return [f"sleep {min(float(p['esperar']), 10):.2f}"]
    if "abrir" in p:
        pac = str(p["abrir"])
        if not re.match(r"^[A-Za-z][\w.]{2,120}$", pac):
            raise ValueError("pacote inválido")
        return [f"monkey -p {pac} -c android.intent.category.LAUNCHER 1 > /dev/null 2>&1 || exit 4", "sleep 1"]
    if any(k in p for k in ("esperar_texto", "esperar_sumir", "se", "se_nao", "repetir", "calma", "esperar_mudanca",
                            "lance", "esperar_vez")):
        return None
    raise ValueError(f"passo desconhecido: {json.dumps(p, ensure_ascii=False)[:80]}")


def _rodar_bloco(linhas, rx):
    """Roda um bloco de passos numa só chamada ao Shizuku, conferindo antes se o app em foco é bloqueado."""
    if not linhas:
        return None
    cab = []
    if rx:
        cab = ["f=$(dumpsys window | grep -m1 mCurrentFocus)",
               f"if echo \"$f\" | grep -qiE {shlex.quote(rx)}; then echo \"BLOQUEADO $f\"; exit 9; fi"]
    out, err, cod = rish("\n".join(cab + linhas), timeout=120)
    if cod == 9:
        return {"erro": "recusado: o app em foco está na lista de bloqueados (banco/pagamento/senha)",
                "foco": app_em_foco(out)}
    if _bloqueio_de_toque(out + err, cod):
        return {"erro": _bloqueio_de_toque(out + err, cod)}
    return None


# --------------------------------------------------------------------------- reflexos guardados no celular
REFLEXOS_ARQ = os.path.join(BASE, "tela_reflexos.json")
MAX_REFLEXOS = 30


def achar_regra(els, texto, exato=False):
    """Como achar, mas texto curto (até 4 letras, ex.: 'OK') só vale igual: 'ok' não casa com 'Facebook'."""
    alvo = normalizar(texto)
    if not alvo:
        return None
    if exato or len(alvo) <= 4:
        for grupo in ([e for e in els if e.get("clicavel")], els):
            for e in grupo:
                if alvo in (normalizar(e.get("texto")), normalizar(e.get("desc"))):
                    return e
        return None
    return achar(els, texto)


def regra_vale(r, app, els_fn, info=""):
    """Onde a regra age agora: ('tecla', código) ou (x, y); None se ela não casa (outro app, texto ausente…)."""
    if r.get("app") and not str(app or "").startswith(str(r["app"])):
        return None
    if r.get("janela"):
        if not info or normalizar(r["janela"]) not in normalizar(info):
            return None
    elif not achar_regra(els_fn(), r["se"], r.get("exato")):
        return None
    if r.get("tecla"):
        return ("tecla", TECLAS[normalizar(r["tecla"])])
    alvo = r["tocar"]
    if isinstance(alvo, str):
        e = achar_regra(els_fn(), alvo, r.get("exato"))
        return (e["x"], e["y"]) if e else None
    return (int(alvo[0]), int(alvo[1]))


def aplicar_regras(app=None, els=None, info=""):
    """Fora de uma sequência (ex.: esperando a grade): aplica a primeira regra que casar e espera assentar.
    Devolve o nome da regra ou None. Nunca em app bloqueado (banco, pagamento, senha)."""
    regras = _regras()
    if not regras or not _ajudante():
        return None
    app = app or foco()
    if bloqueado(app, bloqueados()):
        return None
    cache = {"els": els}

    def els_fn():
        if cache["els"] is None:
            cache["els"] = elementos(dump_ui())
        return cache["els"]

    for r in regras:
        alvo = regra_vale(r, app, els_fn, info)
        if not alvo:
            continue
        _injetar(f"tecla {alvo[1]}" if alvo[0] == "tecla" else f"tocar {alvo[0]} {alvo[1]}")
        calma(120, 1500)
        return r.get("se") or r.get("janela")
    return None


def _regras():
    try:
        with open(REFLEXOS_ARQ) as f:
            r = json.load(f)
        return r if isinstance(r, list) else []
    except (OSError, ValueError):
        return []


def reflexos(regras=None):
    """Lista (sem regras) ou troca as regras. Cada uma: {se:'texto' | janela:'trecho de pacote/classe/texto',
    tocar:[x,y]|'texto' | tecla:'voltar', app:'pacote' (opcional: só nesse app), exato:true (opcional)}.
    Valem nas sequências (no lugar de parar, e enquanto espera um texto) e na espera da grade."""
    if regras is None:
        return {"regras": _regras()}
    if not isinstance(regras, list) or len(regras) > MAX_REFLEXOS:
        return {"erro": f"regras deve ser uma lista (até {MAX_REFLEXOS})"}
    for k, r in enumerate(regras):
        if not isinstance(r, dict) or not (r.get("se") or r.get("janela")) or not (r.get("tocar") or r.get("tecla")):
            return {"erro": f"regra {k + 1}: precisa de se/janela e de tocar/tecla"}
        if r.get("tecla") and normalizar(r["tecla"]) not in TECLAS:
            return {"erro": f"regra {k + 1}: tecla deve ser uma de: {', '.join(TECLAS)}"}
        if r.get("app") and not re.match(r"^[A-Za-z][\w.]{2,120}$", str(r["app"])):
            return {"erro": f"regra {k + 1}: app deve ser o nome do pacote"}
    os.makedirs(BASE, exist_ok=True)
    tmp = REFLEXOS_ARQ + ".tmp"
    with open(tmp, "w") as f:
        json.dump(regras, f, ensure_ascii=False)
    os.replace(tmp, REFLEXOS_ARQ)
    return {"regras": regras, "feito": f"{len(regras)} reflexo(s) guardado(s)"}


# --------------------------------------------------------------------------- rotinas guardadas no celular
ROTINAS_ARQ = os.path.join(BASE, "tela_rotinas.json")
ROTINA_ACOES = ("sequencia", "grade", "ver", "tocar", "digitar", "tecla", "deslizar", "abrir", "fechar_anuncio")


def _rotinas():
    try:
        with open(ROTINAS_ARQ) as f:
            r = json.load(f)
        return r if isinstance(r, dict) else {}
    except (OSError, ValueError):
        return {}


def _resumo_volta(r, segundos):
    """Uma volta de rotina repetida, em poucas palavras (o resultado inteiro de cada uma seria texto demais)."""
    v = {"ok": not r.get("erro") and not r.get("interrompido"), "s": round(segundos, 1)}
    for k in ("n", "vazias", "concluido", "conferido", "refeitos", "erro", "interrompido"):
        if r.get(k) is not None:
            v[k] = str(r[k])[:80] if k in ("erro", "interrompido") else r[k]
    for k in ("anuncios", "reflexos"):
        if r.get(k):
            v[k] = len(r[k])
    return v


def rotina(a):
    """Rotinas guardadas no celular: uma chamada curta no lugar de repetir argumentos longos.
    salvar={nome, args} guarda; apagar=nome apaga; nome roda; nome + vezes=N repete (até 20, dentro de orcamento s,
    padrão 100) e devolve um resumo por volta; sem nada lista."""
    rot = _rotinas()

    def gravar():
        os.makedirs(BASE, exist_ok=True)
        tmp = ROTINAS_ARQ + ".tmp"
        with open(tmp, "w") as f:
            json.dump(rot, f, ensure_ascii=False)
        os.replace(tmp, ROTINAS_ARQ)

    if a.get("salvar"):
        sv = a["salvar"] if isinstance(a["salvar"], dict) else {}
        nome, args = str(sv.get("nome") or ""), sv.get("args")
        if not re.match(r"^[\w-]{1,40}$", nome):
            return {"erro": "nome: até 40 letras, números, _ ou -"}
        if not isinstance(args, dict) or args.get("acao") not in ROTINA_ACOES:
            return {"erro": f"args deve ter acao entre: {', '.join(ROTINA_ACOES)}"}
        rot[nome] = args
        gravar()
        return {"feito": f"rotina {nome} guardada", "rotinas": sorted(rot)}
    if a.get("apagar"):
        rot.pop(str(a["apagar"]), None)
        gravar()
        return {"feito": "apagada", "rotinas": sorted(rot)}
    nome = a.get("nome")
    if not nome:
        return {"rotinas": {k: v.get("acao") for k, v in rot.items()}}
    if nome not in rot:
        return {"erro": f"rotina {nome} não existe", "rotinas": sorted(rot)}
    vezes = max(1, min(int(a.get("vezes") or 1), 20))
    if vezes == 1:
        return {"rotina": nome, **executar(dict(rot[nome]))}
    orcamento = max(10.0, min(float(a.get("orcamento") or 100), 140))
    t0, voltas, ultimo = time.time(), [], {}
    for _ in range(vezes):
        if voltas and time.time() - t0 + max(v["s"] for v in voltas) > orcamento:
            break  # a próxima volta não cabe no tempo desta chamada
        t = time.time()
        ultimo = executar(dict(rot[nome]))
        voltas.append(_resumo_volta(ultimo, time.time() - t))
        if not voltas[-1]["ok"] and not a.get("seguir"):
            break
    out = {"rotina": nome, "feitas": len(voltas), "pedidas": vezes, "segundos": round(time.time() - t0, 1),
           "voltas": voltas}
    if voltas and not voltas[-1]["ok"] and ultimo.get("tela"):
        out["tela"] = ultimo["tela"]  # parou num problema: já mostra a tela
    return out


class _Falha(Exception):
    def __init__(self, info):
        super().__init__(info.get("erro"))
        self.info = info


class _Interrompido(Exception):
    """O reflexo parou a sequência: apareceu algo na tela. Não é erro: é a hora de olhar e decidir de novo."""

    def __init__(self, motivo, elemento):
        super().__init__(motivo)
        self.motivo, self.elemento = motivo, elemento


RECUSA = "recusado: o app em foco está na lista de bloqueados (banco/pagamento/senha)"


def _contar(passos, nivel=0):
    if nivel > 4:
        raise ValueError("passos aninhados demais (até 4 níveis)")
    n = 0
    for p in passos:
        n += 1
        if isinstance(p, dict):
            for k in ("entao", "senao", "repetir"):
                if isinstance(p.get(k), list):
                    n += _contar(p[k], nivel + 1)
    return n


class _Executor:
    """Roda os passos. Com o leitor rápido, cada toque/tecla/deslize é injetado na hora (ms) e as condições leem a
    tela direto da acessibilidade; sem ele, os passos que não leem a tela vão juntos num script de shell."""

    def __init__(self):
        self.lista = bloqueados()
        self.rx = _regex_bloqueados(self.lista)
        self.rapido = _ajudante() is not None
        self.bloco, self.feitos, self.n = [], 0, 0
        self.t0 = time.time()
        self.prazo = self.t0 + PRAZO_SEQUENCIA
        self.app, self.app_em = None, 0.0
        self.t_esperas = 0.0
        self.parar_se = []
        self.parar_em_janela = None  # None: só no meio de levas de toques; True: também entre passos; False: nunca
        self.janela = None  # "pacote|classe|texto" da janela no começo (referência do reflexo)
        self.regras = _regras()
        self.usados = []  # reflexos que agiram nesta sequência
        self.base = None  # janela em que as coordenadas foram lidas (a última vista pelo Claude)
        self.rolou = False  # depois de um deslize, as coordenadas antigas não valem
        self.tocados = []
        self.anuncios = []  # anúncios que o celular fechou sozinho
        self.com_anuncios = True
        self.app_inicial = None  # trava de app inesperado
        self.pressao = None  # ms de cada toque nas levas (None: o padrão do leitor, 12 ms)

    # --- utilidades
    def descarregar(self):
        erro = _rodar_bloco(self.bloco, self.rx)
        self.bloco = []
        if erro:
            raise _Falha(erro)

    def conferir_app(self):
        """O app em foco não pode ser bloqueado (lido no máximo a cada 0,3 s: troca de app leva mais que isso)."""
        if time.time() - self.app_em > 0.3:
            self.app, self.app_em = foco(), time.time()
        if bloqueado(self.app, self.lista):
            raise _Falha({"erro": RECUSA, "foco": self.app})

    def ver_elementos(self):
        self.descarregar()  # o que estava na fila sai antes de olhar
        return elementos(dump_ui())

    def presente(self, texto):
        return achar(self.ver_elementos(), texto) is not None

    def aplicar_reflexo(self, info=""):
        """Alguma regra guardada resolve o que surgiu? Age (tocar/tecla), espera assentar e diz True."""
        if not self.regras or len(self.usados) >= 10:
            return False
        cache = {}

        def els_fn():
            if "els" not in cache:
                cache["els"] = self.ver_elementos()
            return cache["els"]

        app = self.app or foco()
        for r in self.regras:
            alvo = regra_vale(r, app, els_fn, info)
            if not alvo:
                continue
            if alvo[0] == "tecla":
                self.injetar(f"tecla {alvo[1]}", [f"input keyevent {alvo[1]} || exit 3"])
            else:
                x, y = int(alvo[0]), int(alvo[1])
                self.app_em = 0.0
                self.injetar(f"tocar {x} {y}", [f"input tap {x} {y} || exit 3"])
            self.usados.append(r.get("se") or r.get("janela"))
            calma(120, 1500)
            ev = eventos()
            if ev:
                self.janela = ev[2]
            return True
        return False

    def checar_texto(self, onde):
        """Reflexo: algum dos textos de parar_se apareceu? Interrompe e devolve o que surgiu."""
        if not self.parar_se:
            return
        els = self.ver_elementos()
        for t in self.parar_se:
            e = achar(els, t)
            if e:
                if self.aplicar_reflexo():
                    return
                raise _Interrompido(f"apareceu “{e.get('texto') or e.get('desc') or t}” ({onde})", compactos([e])[0])

    def checar_janela(self, info, onde):
        """Surgiu outra janela? Um reflexo guardado resolve (True) ou interrompe; a mesma tela: False."""
        if self.janela is not None and janela_nova(self.janela, info, self.app):
            if self.lidar_anuncio(info):
                return True
            if self.aplicar_reflexo(info):
                return True
            raise _Interrompido(f"surgiu uma janela nova ({onde}): {_janela_curta(info)}", None)
        return False

    def lidar_anuncio(self, info=None):
        """Surgiu anúncio? Fecha no próprio celular e devolve True (a sequência segue de onde estava)."""
        if not (self.rapido and self.com_anuncios):
            return False
        if info is None:
            ev = eventos()
            info = ev[2] if ev else ""
        if not ANUNCIO.search(classe_janela(info)):
            return False
        r = fechar_anuncio(self.app_inicial or self.app)
        self.anuncios.append(r)
        ev = eventos()
        if ev:
            self.janela = ev[2]
            if not ANUNCIO.search(classe_janela(ev[2])):
                self.base = self.base if r["anuncio"] == "fechado" else ev[2]
        self.app_em = 0.0
        return True

    def conferir_outro_app(self, onde):
        """Trava de app inesperado: a tela caiu em outro app (clique em anúncio, link) → para na hora."""
        if not self.rapido or not self.app_inicial:
            return
        ev = eventos()
        pac = (ev[2].split("|")[0] if ev else "") or ""
        if pac and pac != self.app_inicial and not IGNORAR_APP.search(pac):
            atual = foco()
            if atual and atual != self.app_inicial and not IGNORAR_APP.search(atual):
                raise _Interrompido(f"a tela foi para outro app ({atual}) depois do {onde}: parei", None)

    def ancorar(self):
        """Passo informado (leu a tela, esperou um texto, abriu algo): a referência passa a ser a janela atual."""
        if self.rapido:
            ev = eventos()
            if ev:
                self.base = self.janela = ev[2]
        self.rolou = False

    def conferir_coordenadas(self, p, onde, rolagem=True):
        """Toque às cegas (por coordenada) só na tela em que ela foi lida; senão para e manda olhar de novo."""
        if not self.rapido or p.get("confiar") or self.base is None:
            return
        if self.rolou and rolagem:
            raise _Interrompido(f"a tela rolou antes do {onde}: as coordenadas antigas não valem (olhe de novo)", None)
        ev = eventos()
        if ev and janela_nova(self.base, ev[2], self.app):
            if self.lidar_anuncio(ev[2]) or self.aplicar_reflexo(ev[2]):
                return
            raise _Interrompido(f"a tela mudou antes do {onde} ({_janela_curta(ev[2])}): as coordenadas eram de "
                                "outra tela (olhe de novo)", None)

    def tocar_vigiando(self, pontos, pausa, onde):
        """Toques em leva que param na hora se surgir outra janela (aviso, anúncio, fim de jogo) ou um texto de
        parar_se. Com parar_se, a leva vai em pedaços de 2 toques e a tela só é lida se algo mudou."""
        self.conferir_app()
        pedaco = 2 if self.parar_se else len(pontos)
        k, reanuncios = 0, 0
        while k < len(pontos):
            ev = eventos() if self.parar_se else None
            parte = pontos[k:k + pedaco]
            # a mesma tela se anunciando sem parar (animação): o resto da leva vai sem o reflexo de janela
            cmd = "toquesv" if self.parar_em_janela is not False and reanuncios < 20 else "toques"
            ritmo = f"{int(pausa * 1000)}" + (f":{int(self.pressao)}" if self.pressao else "")
            r = (self.injetar_cru(f"{cmd} {ritmo} " + " ".join(f"{x} {y}" for x, y in parte)))
            if r is None:  # leitor caiu: o resto pelo shell, sem reflexo
                linhas = []
                for x, y in pontos[k:]:
                    linhas += [f"input tap {x} {y} || exit 3"] + ([f"sleep {pausa:.2f}"] if pausa else [])
                self.bloco += linhas
                self.descarregar()
                return
            if r.startswith("parou"):
                _, n, info = (r.split(" ", 2) + ["", ""])[:3]
                k += int(n)
                if not self.checar_janela(info, f"{onde}, depois de {k} de {len(pontos)} toques"):
                    self.janela = info  # a mesma tela se anunciando de novo: segue
                reanuncios += 1
                if time.time() > self.prazo:
                    raise _Falha({"erro": f"a sequência passou de {PRAZO_SEQUENCIA} s"})
                continue
            k += len(parte)
            if self.parar_se and ev is not None:
                depois = eventos()
                if depois is None or depois[1] != ev[1]:
                    self.checar_texto(f"{onde}, depois de {k} de {len(pontos)} toques")

    def injetar_cru(self, comando):
        a = _ajudante()
        return a.pedir(comando, 60) if a else None

    def injetar(self, comando, linhas):
        """Pelo leitor (conferindo o app antes); se ele não responder, pelo shell (que confere o app no script).
        Sem o leitor, as linhas entram na fila do shell e saem juntas antes da próxima leitura da tela."""
        if self.rapido:
            self.conferir_app()
            if _injetar(comando):
                return
            self.bloco += linhas
            self.descarregar()
            return
        self.bloco += linhas

    def esperar_mudanca(self, segundos, ignorar):
        """Fica olhando até a tela mudar de verdade (fora do que estiver em `ignorar`: ids ou textos, ex. um relógio)."""
        t0 = time.time()
        fim = t0 + segundos
        ign = [normalizar(i) for i in ignorar]

        def relevantes():
            return [e for e in compactos(self.ver_elementos())
                    if not any(i and (i == normalizar(e.get("id")) or i in normalizar(e.get("texto"))) for i in ign)]

        base = relevantes()
        while time.time() < fim:
            ev = eventos()
            if ev is not None:
                self.injetar_cru(f"aguardar {ev[1]} {int(max(0.05, min(0.7, fim - time.time())) * 1000)}")
            else:
                time.sleep(0.4)
            agora = relevantes()
            if agora != base:
                break
        self.t_esperas += time.time() - t0

    # --- passos
    def rodar(self, passos, rotulo=""):
        for i, p in enumerate(passos):
            self.n += 1
            if self.n > MAX_EXECUTADOS:
                raise _Falha({"erro": f"mais de {MAX_EXECUTADOS} passos executados (laço sem fim?)"})
            if time.time() > self.prazo:
                raise _Falha({"erro": f"a sequência passou de {PRAZO_SEQUENCIA} s"})
            onde = f"passo {rotulo}{i + 1}"
            if not isinstance(p, dict):
                raise _Falha({"erro": f"{onde} inválido"})
            try:
                self.passo(p, onde)
            except (ValueError, TypeError, IndexError, KeyError) as e:
                raise _Falha({"erro": f"{onde}: {e}"}) from e
            self.feitos += 1
            if isinstance(p.get("tocar"), str) or any(k in p for k in ("esperar_texto", "esperar_sumir", "abrir",
                                                                       "esperar_mudanca", "se", "se_nao", "repetir")):
                self.ancorar()
            if self.parar_se and "se" not in p and "se_nao" not in p and "repetir" not in p:
                self.checar_texto(f"depois do {onde}")
            if self.parar_em_janela and self.rapido:
                ev = eventos()
                if ev and not self.checar_janela(ev[2], f"depois do {onde}"):
                    self.janela = ev[2]
            if "abrir" in p:
                self.app_inicial = str(p["abrir"])
            elif normalizar(p.get("tecla")) in ("inicio", "recentes"):
                self.app_inicial = None  # saiu do app de propósito
            elif self.rapido:
                self.lidar_anuncio()
                self.conferir_outro_app(onde)

    def passo(self, p, onde):
        if not self.rapido:
            linhas = _linhas_do_passo(p)
            if linhas is not None:
                self.bloco += linhas
                return
            self.descarregar()  # passo que depende da tela: roda o que acumulou e olha
        if "lance" in p:  # xadrez: "e2e4" → toca a casa de origem e a de destino (lidas agora da tela)
            lance = str(p["lance"]).strip().lower()
            if not re.match(r"^[a-h][1-8][a-h][1-8]$", lance):
                raise ValueError("lance no formato e2e4")
            casas = casas_xadrez(elementos(dump_ui(), limite=300))
            if not casas:
                raise _Falha({"erro": f"{onde}: não há tabuleiro de xadrez na tela", "app": foco()})
            a_, b_ = casas[lance[:2]], casas[lance[2:]]
            p = {"tocar": [[a_[0], a_[1]], [b_[0], b_[1]]], "intervalo": float(p.get("intervalo", 0.06)), "confiar": True}
        if "tocar" in p:
            alvo = p["tocar"]
            if isinstance(alvo, str):
                e = achar(self.ver_elementos(), alvo)
                if not e:
                    raise _Falha({"erro": f"{onde}: nenhum elemento com “{alvo}” na tela", "app": foco()})
                pontos = [[e["x"], e["y"]]]
            else:
                pontos = alvo if alvo and isinstance(alvo[0], (list, tuple)) else [alvo]
                self.conferir_coordenadas(p, onde)
            pontos = [[int(x), int(y)] for x, y in pontos]
            self.tocados += pontos
            self.pressao = p.get("pressao") or self.pressao
            pausa = max(0.0, min(float(p.get("intervalo", 0.05)), 5.0))
            if p.get("segurar"):
                ms = max(50, min(int(p["segurar"]), 5000))
                for k, (x, y) in enumerate(pontos):
                    if k and pausa:
                        time.sleep(pausa)
                    self.injetar(f"tocar {x} {y} {ms}", [f"input swipe {x} {y} {x} {y} {ms} || exit 3"])
                return
            if self.rapido and (len(pontos) > 1 or self.parar_se) and self.parar_em_janela is not False:
                self.tocar_vigiando(pontos, pausa, onde)
                return
            cmd = f"toques {int(pausa * 1000)} " + " ".join(f"{x} {y}" for x, y in pontos)
            linhas = []
            for x, y in pontos:
                linhas += [f"input tap {x} {y} || exit 3"] + ([f"sleep {pausa:.2f}"] if pausa else [])
            self.injetar(cmd, linhas)
        elif "deslizar" in p:
            self.conferir_coordenadas(p, onde, rolagem=False)  # rolar de novo é normal; só a janela importa
            self.rolou = True
            v = [int(n) for n in p["deslizar"]]
            ms = v[4] if len(v) > 4 else 300
            self.injetar(f"deslizar {v[0]} {v[1]} {v[2]} {v[3]} {ms}",
                         [f"input swipe {v[0]} {v[1]} {v[2]} {v[3]} {ms} || exit 3"])
        elif "tecla" in p:
            cod = TECLAS.get(normalizar(p["tecla"]))
            if cod is None:
                raise ValueError(f"tecla deve ser uma de: {', '.join(TECLAS)}")
            self.injetar(f"tecla {cod}", [f"input keyevent {cod} || exit 3"])
            self.app_em = 0.0  # voltar/início podem trocar de app
        elif "digitar" in p:
            self.app_em = 0.0
            self.conferir_app()
            if not _injetar("texto " + str(p["digitar"]).encode().hex()):
                texto, _ = escapar_input_text(str(p["digitar"]))
                if texto:
                    self.bloco = [f"input text {shlex.quote(texto)} || exit 3"]
                    self.descarregar()
        elif "esperar" in p:
            t = min(float(p["esperar"]), 10)
            self.t_esperas += t
            time.sleep(t)
        elif "calma" in p:
            v = p["calma"]
            limite = 1000 if v is True else int(max(0.1, min(float(v), 10)) * 1000)  # segundos, no máximo 10
            t = time.time()
            calma(int(p.get("quieto_ms", 120)), limite)
            self.t_esperas += time.time() - t
        elif "abrir" in p:
            pac = str(p["abrir"])
            if not re.match(r"^[A-Za-z][\w.]{2,120}$", pac):
                raise ValueError("pacote inválido")
            _, erro, cod = rish(f"monkey -p {pac} -c android.intent.category.LAUNCHER 1")
            if cod != 0 or "No activities found" in erro:
                raise _Falha({"erro": f"{onde}: não consegui abrir {pac}: {erro.strip()[:200]}"})
            self.app_em = 0.0
            if self.rapido:
                calma(150, 2500)
            else:
                time.sleep(1)
        elif "esperar_texto" in p or "esperar_sumir" in p:
            texto = p.get("esperar_texto") or p.get("esperar_sumir")
            quer = "esperar_texto" in p
            limite = time.time() + min(float(p.get("ate", 10)), 30)
            t = time.time()
            while self.presente(texto) != quer:
                if self.lidar_anuncio():
                    limite = max(limite, time.time() + 5)  # o tempo do anúncio não conta
                    continue
                if self.rapido and self.regras and self.aplicar_reflexo():
                    continue  # um aviso conhecido estava por cima: dispensado, olha de novo
                if time.time() > limite:
                    raise _Falha({"erro": f"{onde}: “{texto}” {'não apareceu' if quer else 'não sumiu'} a tempo",
                                  "app": foco()})
                time.sleep(0.08 if self.rapido else 0.4)
            self.t_esperas += time.time() - t
        elif "esperar_vez" in p:  # xadrez: espera o adversário mexer (o tabuleiro muda depois do meu lance assentar)
            t = time.time()
            fim = t + min(float(p["esperar_vez"]), 30)
            time.sleep(0.2)

            def foto():
                c = casas_xadrez(elementos(dump_ui(), limite=300))
                return "".join(c[k][2] or "." for k in sorted(c)) if c else None

            base = foto()
            while time.time() < fim:
                agora = foto()
                if agora != base:
                    break
                time.sleep(0.03)
            self.t_esperas += time.time() - t
        elif "esperar_mudanca" in p:
            self.esperar_mudanca(min(float(p["esperar_mudanca"]), 30), p.get("ignorar") or [])
        elif "se" in p or "se_nao" in p:
            texto = p.get("se") if "se" in p else p.get("se_nao")
            verdade = self.presente(texto) == ("se" in p)
            ramo = p.get("entao" if verdade else "senao") or []
            if not isinstance(ramo, list):
                raise ValueError("entao/senao devem ser listas de passos")
            self.rodar(ramo, f"{onde.split()[-1]}.{'entao' if verdade else 'senao'}.")
        elif "repetir" in p:
            corpo = p["repetir"]
            if not isinstance(corpo, list) or not corpo:
                raise ValueError("repetir deve ser uma lista de passos")
            vezes = max(1, min(int(p.get("vezes", 50)), 500))
            ate = p.get("ate_texto") or p.get("ate_sumir")
            for k in range(vezes):
                self.rodar(corpo, f"{onde.split()[-1]}.{k + 1}.")
                if ate is not None and self.presente(ate) == ("ate_texto" in p):
                    return
            if ate is not None:
                raise _Falha({"erro": f"{onde}: repetiu {vezes} vezes e “{ate}” "
                                      f"{'não apareceu' if 'ate_texto' in p else 'não sumiu'}"})
        else:
            raise ValueError(f"passo desconhecido: {json.dumps(p, ensure_ascii=False)[:80]}")


def sequencia(a):
    passos = a.get("passos") or []
    if not isinstance(passos, list) or not passos:
        return {"erro": "informe passos: lista de {tocar:[x,y] | tocar:'texto' | tocar:[[x,y],...] | digitar | tecla | "
                        "deslizar:[x,y,x2,y2] | esperar:s | calma:true | esperar_texto:'...' | esperar_sumir:'...' | "
                        "abrir:'pacote' | se:'texto',entao:[...],senao:[...] | repetir:[...],vezes,ate_texto}"}
    try:
        if _contar(passos) > MAX_PASSOS:
            return {"erro": f"no máximo {MAX_PASSOS} passos por sequência"}
    except ValueError as e:
        return {"erro": str(e)}
    ex = _Executor()
    ps = a.get("parar_se") or []
    ex.parar_se = [ps] if isinstance(ps, str) else [str(t) for t in ps][:20]
    if a.get("parar_em_janela") is not None:
        ex.parar_em_janela = bool(a["parar_em_janela"])
    if ex.rapido:
        ev = eventos()
        ex.janela = ev[2] if ev else None
        ex.base = _ULTIMA.get("janela") or ex.janela  # o Claude planejou em cima da última tela que viu
        ex.app, ex.app_em = foco(), time.time()
        ex.app_inicial = ex.app if ex.app and not IGNORAR_APP.search(ex.app) else None
    ex.com_anuncios = a.get("anuncios", True) is not False
    interrompido = None
    try:
        ex.rodar(passos)
        ex.descarregar()
    except _Falha as f:
        tela = {}
        try:  # o erro já volta com a tela atual (sem chamada extra), mas só se ainda é o app da sequência:
            atual = foco()  # outro app (ex.: o dono abriu uma conversa) não é lido — privacidade
            if atual and atual in (ex.app_inicial, ex.app):
                tela = _ver_depois(dict(a, ver_depois=a.get("ver_depois") if a.get("ver_depois") != "nada" else "auto"))
            elif atual:
                tela = {"app_em_foco": atual, "nota": "outro app em uso: a tela não foi lida"}
        except Exception:  # noqa: BLE001
            pass
        return {**f.info, "feitos": ex.feitos, **({"anuncios": ex.anuncios} if ex.anuncios else {}), **tela}
    except _Interrompido as i:
        interrompido = {"interrompido": i.motivo, **({"elemento": curto(i.elemento)} if i.elemento else {})}
    if ex.usados:
        interrompido = {**(interrompido or {}), "reflexos": ex.usados}
    if ex.anuncios:
        interrompido = {**(interrompido or {}), "anuncios": ex.anuncios}
    gasto = time.time() - ex.t0
    tempos = {"acoes": round(gasto - ex.t_esperas, 2)}
    if ex.t_esperas:
        tempos["esperas"] = round(ex.t_esperas, 2)
    t = time.time()
    atual = foco() if ex.rapido and ex.app_inicial else None
    if atual and atual != ex.app_inicial and not IGNORAR_APP.search(atual) and not any("abrir" in p for p in passos
                                                                                      if isinstance(p, dict)):
        depois = {"app_em_foco": atual, "nota": "outro app em primeiro plano: a tela não foi lida"}  # privacidade
    else:
        depois = _ver_depois(a, tocados=ex.tocados)
    tempos["olhar"] = round(time.time() - t, 2)
    return {**(interrompido or {}), "feito": f"{ex.feitos} passos em {gasto:.1f} s", "tempos": tempos, **depois}


def agir(a):
    acao = a["acao"]
    if acao == "sequencia":
        return sequencia(a)
    app = foco()
    if acao in ("tocar", "digitar", "deslizar") and bloqueado(app, bloqueados()):
        return {"erro": f"recusado: o app em foco ({app}) está na lista de bloqueados (banco/pagamento/senha). "
                        "Edite ~/.controle-ir/tela_bloqueados.json no celular se quiser mudar isso."}
    if acao in ("tocar", "deslizar") and a.get("texto") is None and not a.get("confiar") and _ULTIMA.get("janela"):
        ev = eventos()  # coordenada lida numa tela que já não está aí: não toca, mostra a atual
        if ev and janela_nova(_ULTIMA["janela"], ev[2], app):
            return {"interrompido": f"a tela mudou desde a última olhada ({_janela_curta(ev[2])}): as coordenadas "
                                    "eram de outra tela (olhe de novo)", **_ver_depois(a, "auto")}
    if acao == "tocar":
        x, y, alvo = a.get("x"), a.get("y"), None
        if a.get("texto"):
            alvo = achar(elementos(dump_ui()), a["texto"])
            if not alvo:
                return {"erro": f"nenhum elemento com “{a['texto']}” na tela", "app": app}
            x, y = alvo["x"], alvo["y"]
        if x is None or y is None:
            return {"erro": "informe x e y, ou texto"}
        if not _injetar(f"tocar {int(x)} {int(y)}"):
            out, err, cod = rish(f"input tap {int(x)} {int(y)}")
            if _bloqueio_de_toque(out + err, cod):
                return {"erro": _bloqueio_de_toque(out + err, cod)}
        res = {"feito": f"toque em {int(x)},{int(y)}", "elemento": compactos([alvo])[0] if alvo else None}
    elif acao == "digitar":
        if _injetar("texto " + str(a.get("texto", "")).encode().hex()):  # com acentos, no campo em foco
            res = {"feito": f"digitado ({len(a.get('texto', ''))} caracteres)"}
        else:
            texto, aviso = escapar_input_text(a.get("texto", ""))
            if not texto:
                return {"erro": "nada para digitar"}
            out, err, cod = rish("input text " + shlex.quote(texto))
            if _bloqueio_de_toque(out + err, cod):
                return {"erro": _bloqueio_de_toque(out + err, cod)}
            res = {"feito": f"digitado ({len(a.get('texto', ''))} caracteres)", "aviso": aviso}
    elif acao == "tecla":
        cod = TECLAS.get(normalizar(a.get("tecla")))
        if cod is None:
            return {"erro": f"tecla deve ser uma de: {', '.join(TECLAS)}"}
        if not _injetar(f"tecla {cod}"):
            out, err, rc = rish(f"input keyevent {cod}")
            if _bloqueio_de_toque(out + err, rc):
                return {"erro": _bloqueio_de_toque(out + err, rc)}
        res = {"feito": f"tecla {a['tecla']}"}
    elif acao == "deslizar":
        if None in (a.get("x"), a.get("y"), a.get("x2"), a.get("y2")):
            return {"erro": "informe x, y, x2, y2"}
        if not _injetar(f"deslizar {int(a['x'])} {int(a['y'])} {int(a['x2'])} {int(a['y2'])} 350"):
            out, err, cod = rish(f"input swipe {int(a['x'])} {int(a['y'])} {int(a['x2'])} {int(a['y2'])} 350")
            if _bloqueio_de_toque(out + err, cod):
                return {"erro": _bloqueio_de_toque(out + err, cod)}
        res = {"feito": "deslizou"}
    elif acao == "abrir":
        pac = a.get("pacote") or ""
        if not re.match(r"^[A-Za-z][\w.]{2,120}$", pac):
            return {"erro": "pacote inválido (ex.: com.android.settings)"}
        _, erro, cod = rish(f"monkey -p {pac} -c android.intent.category.LAUNCHER 1")
        if cod != 0 or "No activities found" in erro:
            return {"erro": f"não consegui abrir {pac}: {erro.strip()[:200]}"}
        res = {"feito": f"abriu {pac}"}
    else:
        return {"erro": "acao deve ser ver, tocar, digitar, tecla, deslizar, abrir, sequencia ou estado"}
    espera = float(a.get("esperar") or 0)
    if espera > 0:
        time.sleep(min(espera, 10))
    # depois de agir: com o leitor rápido, espera a tela assentar e diz só o que mudou; sem ele, só o app em foco
    ponto = [[int(a["x"]), int(a["y"])]] if acao == "tocar" and a.get("x") is not None else []
    res.update(_ver_depois(a, "elementos" if espera > 0 and not _ajudante() else None, tocados=ponto))
    return res


# --------------------------------------------------------------------------- piloto (laço rápido no celular)
_PILOTO = []


def _modulo_piloto():
    import importlib.util
    spec = importlib.util.spec_from_file_location("tela_piloto", os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                             "piloto.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _ferramentas_piloto():
    def aguardar(contador, ms):
        aj = _ajudante()
        if not aj:
            time.sleep(ms / 1000)
            return contador
        r = aj.pedir(f"aguardar {int(contador)} {int(ms)}", ms / 1000 + 5)
        try:
            return int((r or "").strip())
        except ValueError:
            return contador

    def tocar(x, y):
        if not _injetar(f"toques 0:30 {int(x)} {int(y)}"):
            rish(f"input tap {int(x)} {int(y)}", timeout=5)

    return {"aguardar": aguardar, "elementos": lambda: elementos(dump_ui(), limite=300), "tocar": tocar,
            "bloqueado": lambda app: bool(app) and bloqueado(app, bloqueados()),
            "casas": lambda: casas_xadrez(elementos(dump_ui(), limite=300)), "contra_robo": partida_contra_robo}


def partida_contra_robo():
    """Xadrez só contra a máquina: a atividade em primeiro plano tem de ser a partida contra robô do app.
    Partida ao vivo contra pessoas = trapaça (e banimento): o piloto não joga."""
    pac, cls = atividade_no_topo()
    return bool(pac and cls) and ("Bot" in cls or "Computer" in cls) and "Live" not in cls


def piloto(a):
    """O laço rápido: liga (iniciar={...}), mostra (estado), desliga (parar), ensina a memória (ensinar=[{pergunta,
    resposta}]) ou testa os cérebros sem a tela (testar={pergunta, opcoes:[...]})."""
    if not _PILOTO:
        m = _modulo_piloto()
        _PILOTO.extend([m, m.Piloto(_ferramentas_piloto())])
    m, p = _PILOTO
    if a.get("parar"):
        p.encerrar()
        return p.estado()
    if a.get("ensinar"):
        mem = m.carregar_memoria()
        for item in a["ensinar"][:200]:
            if isinstance(item, dict) and item.get("pergunta") and item.get("resposta"):
                mem[m.norm(item["pergunta"])] = str(item["resposta"])
        m.gravar_memoria(mem)
        if p.cerebros:
            p.cerebros.memoria.update(mem)
        return {"memoria": len(mem)}
    if a.get("testar"):
        t = a["testar"]
        cfg = dict(a.get("iniciar") or {}, **{k: a[k] for k in ("modelo", "pensar", "cerebros", "local_url", "politica")
                                               if k in a})
        c = m.Cerebros(cfg)
        ops = [{"texto": str(o)} for o in (t.get("opcoes") or [])]
        res = []
        for _ in range(max(1, min(int(t.get("vezes", 1)), 5))):
            idx, fonte, seg, erros = c.decidir(str(t.get("pergunta", "")), ops, float(t.get("prazo", 8)))
            res.append({"escolha": ops[idx]["texto"] if idx is not None else None, "fonte": fonte,
                        "ms": int(seg * 1000), **({"erros": erros} if erros else {})})
        return {"testes": res, "chave_api": bool(m.ler_chave())}
    if a.get("iniciar") is not None:
        cfg = a["iniciar"] if isinstance(a["iniciar"], dict) else {}
        if cfg.get("app") and bloqueado(cfg["app"], bloqueados()):
            return {"erro": "app bloqueado para o agente de tela"}
        if cfg.get("modo") == "xadrez" and not partida_contra_robo():
            return {"erro": "o modo xadrez só joga na tela de partida contra robô (nunca contra pessoas)",
                    "atividade": "/".join(x or "" for x in atividade_no_topo())}
        return p.iniciar(cfg)
    return p.estado(int(a.get("ultimas", 8)))


def executar(a):
    """Ponto de entrada: o serviço chama direto (EM_PROCESSO) e o modo antigo passa por main()."""
    _CORTE[0] = max(80, min(int(a.get("texto_max") or 80), 4000))
    try:
        return _executar(a)
    finally:
        _CORTE[0] = 80


def navegar(app, objetivo, marcador, controles):
    from pathlib import Path
    import hashlib
    import tempfile
    if not all(isinstance(x, str) and x.strip() for x in (app, objetivo, marcador)):
        return {"erro":"informe pacote, objetivo e marcador"}
    if not isinstance(controles,list) or not 1 <= len(controles) <= 32 or not all(isinstance(c,str) and c for c in controles):
        return {"erro":"controles inválidos"}
    if bloqueado(app, bloqueados()):
        return {"erro":"app bloqueado"}
    pasta = Path.home() / "agente-dialogue" / "rotas"
    pasta.mkdir(exist_ok=True, parents=True)
    chave = hashlib.sha256(json.dumps([app, objetivo, marcador, controles]).encode()).hexdigest()
    arquivo = pasta / chave
    memoria = json.loads(arquivo.read_text()) if arquivo.exists() else {}
    novos = {}
    consultas = 0
    feitos = 0
    inicio = time.monotonic()
    def resultado(estado):
        return dict(estado=estado, gestos=feitos, consultas=consultas, ms=round(1000*(time.monotonic()-inicio)))
    if len(controles) == 1 and _ajudante():
        campos = " ".join(v.encode().hex() for v in (app, controles[0], marcador))
        retorno = _ajudante().pedir("navegar " + campos, 4)
        if retorno in ("feito", "presente"):
            feitos = int(retorno == "feito")
            return resultado("objetivo confirmado")
        if retorno != "indisponivel":
            return resultado("transição sem confirmação")
    prazo = 0
    while feitos <= 8:
        if foco() != app:
            return resultado("app indisponível")
        ev = eventos()
        els = elementos(dump_ui(), limite=300)
        nomes = {e[k] for e in els if e.get("pacote")==app for k in ("texto","desc") if e.get(k)}
        if marcador in nomes:
            if novos:
                with tempfile.NamedTemporaryFile(mode="w", dir=pasta, delete=False) as f:
                    json.dump({**memoria, **novos}, f)
                os.replace(f.name, arquivo)
            return resultado("objetivo confirmado")
        visiveis = sorted(nomes.intersection(controles))
        estado = json.dumps([visiveis, sorted({e["id"] for e in els if e.get("pacote")==app and e.get("id")}), sorted(e["texto"] or e["desc"] for e in els if e.get("selecionado") and e.get("pacote")==app)], ensure_ascii=False)
        assinatura = hashlib.sha256(estado.encode()).hexdigest()
        if (not visiveis or assinatura in novos) and time.monotonic() < prazo:
            if ev and _ajudante():
                _ajudante().pedir(f"aguardar {ev[1]} 100", 2)
            else:
                time.sleep(0.05)
            continue
        if not visiveis or assinatura in novos or feitos == 8:
            return resultado("sem avanço confirmado")
        alvo = memoria.get(assinatura)
        if alvo not in visiveis:
            if len(visiveis)==1:
                alvo = visiveis[0]
            else:
                opcoes = visiveis + ["Parar"]
                m = _modulo_piloto()
                brain = m.Cerebros({"cerebros":["api"], "modelos":[m.MODELO], "pensar":False})
                idx, _, _, _ = brain.decidir(objetivo, [{"texto":v} for v in opcoes], 5)
                consultas += 1
                if idx is None or idx >= len(visiveis):
                    return resultado("decisão inconclusiva")
                alvo = visiveis[idx]
                els = elementos(dump_ui(), limite=300)
        if foco() != app:
            return resultado("janela mudou")
        candidatos = [e for e in els if e.get("pacote")==app and alvo in (e["texto"],e["desc"]) and not e.get("desativado")]
        clicaveis = [e for e in candidatos if e.get("clicavel")]
        pontos = {(e["x"],e["y"]) for e in clicaveis or candidatos}
        if len(pontos) != 1:
            return resultado("controle ausente ou ambíguo")
        x,y = pontos.pop()
        if not _injetar(f"toques 0:30 {x} {y}"):
            return resultado("controle indisponível")
        novos[assinatura] = alvo
        feitos += 1
        prazo = time.monotonic() + 1.5


def navegar_etapas(a):
    from pathlib import Path
    import tempfile
    pacote, nome = a.get("pacote"), a.get("nome")
    if not isinstance(pacote, str) or not pacote or bloqueado(pacote, bloqueados()):
        return {"erro": "app indisponível"}
    cfg = a.get("iniciar") or {}
    if not isinstance(cfg, dict):
        return {"erro": "iniciar deve ser um objeto"}
    pasta = os.path.join(BASE, "rotas_confirmadas")
    passos = a.get("passos")
    if nome is None and not cfg.get("marcador"):
        nome = a.get("texto")
    def catalogo():
        rotas = []
        for arq in sorted(Path(pasta).glob("*.json")):
            try:
                dado = json.loads(arq.read_text())
                if isinstance(dado, dict) and dado.get("pacote") == pacote:
                    rotas.append(dado["nome"])
            except (OSError, ValueError, KeyError):
                continue
        return sorted(rotas)
    if a.get("mostrar"):
        return {"rotas": catalogo()}
    arquivo = None
    aprendendo = passos is not None and nome is not None
    if nome is not None:
        if not isinstance(nome, str) or not nome.strip() or len(nome) > 160:
            return {"erro": "nome de rota inválido"}
        chave = hashlib.sha256(json.dumps([pacote, nome.casefold().strip()]).encode()).hexdigest()
        arquivo = os.path.join(pasta, chave + ".json")
        if passos is None:
            try:
                with open(arquivo) as f:
                    registro = json.load(f)
                    passos = registro.get("passos") if isinstance(registro, dict) else registro
            except (OSError, ValueError):
                return {"erro": "rota ainda não aprendida", "rotas": catalogo()}
    if passos is None:
        passos = [dict(cfg, texto=a.get("texto"))] if isinstance(cfg, dict) else []
    if not isinstance(passos, list) or not 1 <= len(passos) <= 8:
        return {"erro": "informe de uma a oito etapas"}
    for passo in passos:
        if not isinstance(passo, dict) or not all(isinstance(passo.get(k), str) and passo[k].strip()
                for k in ("texto", "marcador")):
            return {"erro": "etapa sem objetivo ou marcador"}
        controles = passo.get("controles")
        if not isinstance(controles, list) or not 1 <= len(controles) <= 32 or not all(
                isinstance(c, str) and c.strip() for c in controles):
            return {"erro": "etapa com controles inválidos"}
    if cfg.get("abrir") is True and foco() != pacote:
        abriu = agir({"acao":"abrir", "pacote":pacote, "ver_depois":"nada"})
        limite = time.monotonic() + 2
        while abriu.get("feito") and foco() != pacote and time.monotonic() < limite:
            time.sleep(0.05)
        if foco() != pacote:
            return {"erro": "app não assumiu o primeiro plano"}
    medidas = []
    for passo in passos:
        r = navegar(a.get("pacote"), passo["texto"], passo["marcador"], passo["controles"])
        medidas.append(r)
        if r.get("estado") != "objetivo confirmado":
            break
    if aprendendo and len(medidas) == len(passos) and all(r.get("estado") == "objetivo confirmado" for r in medidas):
        os.makedirs(pasta, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", dir=pasta, delete=False) as f:
            json.dump({"pacote": pacote, "nome": nome, "passos": passos}, f, ensure_ascii=False)
        os.replace(f.name, arquivo)
    return medidas[0] if len(passos) == 1 else {"etapas": medidas}


def _executar(a):
    acao = a.get("acao")
    try:
        if acao == "estado":
            out, _, _ = rish("id; dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'; "
                             "dumpsys power | grep -m1 mWakefulness=")
            r = {"rish": "ok" if "uid=2000" in out or "uid=0" in out else out.strip()[:120],
                 "app": app_em_foco(out), "tela_acesa": "Awake" in out, "ffmpeg": bool(shutil.which("ffmpeg"))}
        elif acao == "ver":
            largura = max(320, min(int(a.get("largura", 720)), 1080))
            r = ver(bool(a.get("imagem", True)), largura, bool(a.get("elementos", True)), a.get("recorte"),
                    so_mudancas=bool(a.get("so_mudancas")), formato=a.get("formato", "curto"))
        elif acao == "grade":
            r = grade(a)
        elif acao == "navegar":
            r = navegar_etapas(a)
        elif acao == "rotina":
            r = rotina(a)
        elif acao == "fechar_anuncio":
            r = fechar_anuncio(foco(), min(float(a.get("limite", 45)), 120)) if em_anuncio(True) else {"anuncio": "nenhum"}
        elif acao == "reflexos":
            r = reflexos(a.get("regras"))
        elif acao == "piloto":
            r = piloto(a)
        else:
            r = agir(a)
    except SemShizuku as e:
        r = {"erro": str(e), "precisa": "shizuku"}
    except subprocess.TimeoutExpired:
        r = {"erro": "o comando na tela demorou demais (o celular pode estar travado ou com a tela apagada)"}
    return r


def main():
    print(json.dumps(executar(json.loads(sys.stdin.read() or "{}")), ensure_ascii=False))


if __name__ == "__main__":
    main()
