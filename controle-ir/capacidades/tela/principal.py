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
        out.append({"texto": texto[:80], "desc": desc[:80], "id": a.get("resource-id", "").split("/")[-1],
                    "classe": a.get("class", "").split(".")[-1], "clicavel": clicavel, "editavel": editavel,
                    "x": (b[0] + b[2]) // 2, "y": (b[1] + b[3]) // 2, "pacote": a.get("package", ""),
                    "marcado": a.get("checked") == "true" if marcavel else None,
                    "selecionado": a.get("selected") == "true", "rolavel": rolavel,
                    "focado": a.get("focused") == "true", "desativado": a.get("enabled") == "false"})
        if len(out) >= limite:
            break
    return out


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


def ver(imagem=True, largura=720, com_elementos=True, recorte=None, so_mudancas=False):
    rapida = foto_rapida(largura, recorte) if imagem and _ajudante() else (None, None)
    xml, png, app, acesa = observar(com_elementos, imagem and not rapida[0])
    out = {"app": app, "tela_acesa": acesa}
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
                out["elementos"] = els
                out["nota"] = "coordenadas x,y em pixels da tela real (use-as em tocar); a imagem é reduzida"
            elif any(dif.values()):
                out["mudancas"] = {k: v for k, v in dif.items() if v}
                out["sem_mudar"] = len(els) - len(dif["entrou"]) - len(dif["mudou"])
            else:
                out["mudancas"] = "nenhuma"
            _ULTIMA.update(app=app, els=els)
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


def _ver_depois(a, padrao=None):
    """Depois de agir, espera a tela assentar (leitor rápido) e olha: 'mudancas' (padrão com o leitor: só o que
    mudou desde a última olhada), 'elementos' (lista inteira), 'imagem' (lista + captura) ou 'nada' (só o app)."""
    if padrao is None:
        padrao = "mudancas" if _ajudante() else "nada"
    modo = a.get("ver_depois") or ("imagem" if a.get("imagem") else padrao)
    esperou = None
    if modo != "nada" and a.get("calma", True) is not False:
        esperou = calma(int(a.get("calma_ms", 120)), int(a.get("calma_ate", 1000)))
    extra = {"calma_ms": esperou} if esperou is not None else {}
    if modo == "nada":
        return {"app": foco()}
    largura = max(320, min(int(a.get("largura", 720)), 1080))
    return {"tela": ver(modo == "imagem", largura, True, a.get("recorte"), so_mudancas=(modo == "mudancas")), **extra}


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
    if any(k in p for k in ("esperar_texto", "esperar_sumir", "se", "se_nao", "repetir", "calma")):
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


class _Falha(Exception):
    def __init__(self, info):
        super().__init__(info.get("erro"))
        self.info = info


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

    def passo(self, p, onde):
        if not self.rapido:
            linhas = _linhas_do_passo(p)
            if linhas is not None:
                self.bloco += linhas
                return
            self.descarregar()  # passo que depende da tela: roda o que acumulou e olha
        if "tocar" in p:
            alvo = p["tocar"]
            if isinstance(alvo, str):
                e = achar(self.ver_elementos(), alvo)
                if not e:
                    raise _Falha({"erro": f"{onde}: nenhum elemento com “{alvo}” na tela", "app": foco()})
                pontos = [[e["x"], e["y"]]]
            else:
                pontos = alvo if alvo and isinstance(alvo[0], (list, tuple)) else [alvo]
            pontos = [[int(x), int(y)] for x, y in pontos]
            pausa = max(0.0, min(float(p.get("intervalo", 0.05)), 5.0))
            if p.get("segurar"):
                ms = max(50, min(int(p["segurar"]), 5000))
                for k, (x, y) in enumerate(pontos):
                    if k and pausa:
                        time.sleep(pausa)
                    self.injetar(f"tocar {x} {y} {ms}", [f"input swipe {x} {y} {x} {y} {ms} || exit 3"])
                return
            cmd = f"toques {int(pausa * 1000)} " + " ".join(f"{x} {y}" for x, y in pontos)
            linhas = []
            for x, y in pontos:
                linhas += [f"input tap {x} {y} || exit 3"] + ([f"sleep {pausa:.2f}"] if pausa else [])
            self.injetar(cmd, linhas)
        elif "deslizar" in p:
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
                if time.time() > limite:
                    raise _Falha({"erro": f"{onde}: “{texto}” {'não apareceu' if quer else 'não sumiu'} a tempo",
                                  "app": foco()})
                time.sleep(0.08 if self.rapido else 0.4)
            self.t_esperas += time.time() - t
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
    try:
        ex.rodar(passos)
        ex.descarregar()
    except _Falha as f:
        return {**f.info, "feitos": ex.feitos}
    gasto = time.time() - ex.t0
    tempos = {"acoes": round(gasto - ex.t_esperas, 2)}
    if ex.t_esperas:
        tempos["esperas"] = round(ex.t_esperas, 2)
    t = time.time()
    depois = _ver_depois(a)
    tempos["olhar"] = round(time.time() - t, 2)
    return {"feito": f"{ex.feitos} passos em {gasto:.1f} s", "tempos": tempos, **depois}


def agir(a):
    acao = a["acao"]
    if acao == "sequencia":
        return sequencia(a)
    app = foco()
    if acao in ("tocar", "digitar", "deslizar") and bloqueado(app, bloqueados()):
        return {"erro": f"recusado: o app em foco ({app}) está na lista de bloqueados (banco/pagamento/senha). "
                        "Edite ~/.controle-ir/tela_bloqueados.json no celular se quiser mudar isso."}
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
    res.update(_ver_depois(a, "elementos" if espera > 0 and not _ajudante() else None))
    return res


def executar(a):
    """Ponto de entrada: o serviço chama direto (EM_PROCESSO) e o modo antigo passa por main()."""
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
                    so_mudancas=bool(a.get("so_mudancas")))
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
