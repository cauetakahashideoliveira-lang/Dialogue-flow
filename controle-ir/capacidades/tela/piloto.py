"""Piloto: o laço rápido que roda NO CELULAR, sem passar pelo Claude a cada gesto.

Sistema nervoso em camadas:
  medula   — o leitor Java (acessibilidade + toque direto), milissegundos;
  cerebelo — este laço: percebe a mudança, lê a pergunta, dispara uma CORRIDA DE CÉREBROS (memória, modelo rápido
             pela API, modelo local) e toca no ALVO SEMÂNTICO (o texto da resposta, relocalizado na hora do toque);
  córtex   — o Claude, fora do laço: liga, ajusta a política, lê o gravador de voo e ensina a memória.

Funciona com a biblioteca padrão (http.client com conexão persistente e streaming SSE: toca assim que o primeiro
dígito da resposta chega). A chave da API fica no celular (~/.controle-ir/anthropic.key ou ANTHROPIC_API_KEY) e
nunca passa pelo conector.
"""
from __future__ import annotations

import collections
import http.client
import json
import os
import queue
import re
import ssl
import threading
import time
import unicodedata

BASE = os.environ.get("CONTROLE_IR_DIR") or os.path.expanduser("~/.controle-ir")
PASTA = os.path.join(BASE, "piloto")
MEMORIA_ARQ = os.path.join(PASTA, "memoria.json")
GRAVADOR_ARQ = os.path.join(PASTA, "rodadas.jsonl")
CHAVE_ARQ = os.path.join(BASE, "anthropic.key")
API_HOST = "api.anthropic.com"
API_VERSAO = "2026-10-21"
MODELO = "claude-haiku-5-5"
POLITICA = ("Você joga um quiz. Responda APENAS com o número da alternativa correta (um dígito), sem mais nada. "
            "Se não souber, responda o número da mais provável.")
IGNORAR = ("pular", "desistir", "parar", "sair", "voltar", "dica", "ajuda", "50:50", "50/50", "cartas", "placas",
           "universitarios", "continuar", "ok", "fechar", "menu", "configuracoes")


def norm(t):
    t = unicodedata.normalize("NFKD", str(t or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


# ----------------------------------------------------------------------------------------------------- percepção
def quiz_da_tela(els, ignorar=IGNORAR):
    """(pergunta, [opções {texto,x,y,l,a}]) de uma tela de quiz, ou None. Opções: o maior grupo (2–6) de botões do
    mesmo tamanho com texto; pergunta: o texto mais longo acima delas."""
    clic = [e for e in els if e.get("clicavel") and e.get("l") and e.get("a")]
    ign = {norm(i) for i in ignorar}
    textos = [e for e in els if (e.get("texto") or e.get("desc")) and not e.get("editavel")]
    por_alvo = {}
    for t in textos:
        s = (t.get("texto") or t.get("desc") or "").strip()
        if not s or len(s) > 120 or norm(s) in ign:
            continue
        alvo = t if t.get("clicavel") and t.get("l") else None
        if alvo is None:
            dentro = [c for c in clic if abs(c["x"] - t["x"]) <= c["l"] / 2 and abs(c["y"] - t["y"]) <= c["a"] / 2]
            if not dentro:
                continue
            alvo = min(dentro, key=lambda c: c["l"] * c["a"])
        chave = (alvo["x"], alvo["y"])
        o = por_alvo.setdefault(chave, {"texto": "", "x": alvo["x"], "y": alvo["y"], "l": alvo["l"], "a": alvo["a"],
                                        "_ids": set()})
        if id(t) not in o["_ids"]:
            o["_ids"].add(id(t))
            o["texto"] = (o["texto"] + " " + s).strip()
    opcoes = [o for o in por_alvo.values() if norm(o["texto"]) and norm(o["texto"]) not in ign]
    grupos = []
    for o in opcoes:
        for g in grupos:
            r = g[0]
            if abs(o["l"] - r["l"]) <= 0.15 * r["l"] and abs(o["a"] - r["a"]) <= 0.3 * r["a"]:
                g.append(o)
                break
        else:
            grupos.append([o])
    grupos = [g for g in grupos if 2 <= len(g) <= 6]
    if not grupos:
        return None
    g = max(grupos, key=lambda g: (len(g), sum(o["y"] for o in g) / len(g)))
    topo = min(o["y"] - o["a"] / 2 for o in g)
    usados = {norm(o["texto"]) for o in g}
    perg = [t for t in textos if t["y"] < topo and len((t.get("texto") or "").strip()) >= 8
            and norm(t.get("texto")) not in usados and norm(t.get("texto")) not in ign]
    if not perg:
        return None
    pergunta = max(perg, key=lambda t: len(t["texto"]))["texto"].strip()
    ops = sorted(g, key=lambda o: (round(o["y"] / 40), o["x"]))
    return pergunta, [{k: v for k, v in o.items() if k != "_ids"} for o in ops]


def chave_quiz(pergunta, opcoes):
    return norm(pergunta) + " || " + " | ".join(sorted(norm(o["texto"]) for o in opcoes))


# ----------------------------------------------------------------------------------------------------- cérebros
def ler_chave():
    k = os.environ.get("ANTHROPIC_API_KEY")
    if k:
        return k.strip()
    try:
        with open(CHAVE_ARQ) as f:
            return f.read().strip() or None
    except OSError:
        return None


class Conexao:
    """Conexão HTTPS persistente (sem um aperto de mão TLS por pergunta); refaz sozinha se cair."""

    def __init__(self, host, porta=443, seguro=True):
        self.host, self.porta, self.seguro = host, porta, seguro
        self.c = None
        self.trava = threading.Lock()

    def _abrir(self):
        if self.seguro:
            self.c = http.client.HTTPSConnection(self.host, self.porta, timeout=10, context=ssl.create_default_context())
        else:
            self.c = http.client.HTTPConnection(self.host, self.porta, timeout=10)
        self.c.connect()

    def post_stream(self, caminho, corpo, cabecalhos, ao_texto):
        """POST com SSE; chama ao_texto(pedaço) a cada delta; devolve quando o stream termina. Se a conexão ainda
        está ocupada com uma resposta atrasada, usa uma conexão avulsa (a pergunta nova não espera a velha)."""
        if not self.trava.acquire(blocking=False):
            extra = Conexao(self.host, self.porta, self.seguro)
            try:
                return extra.post_stream(caminho, corpo, cabecalhos, ao_texto)
            finally:
                extra.fechar()
        try:
            return self._post(caminho, corpo, cabecalhos, ao_texto)
        finally:
            self.trava.release()

    def _post(self, caminho, corpo, cabecalhos, ao_texto):
        for tentativa in range(2):
            try:
                if self.c is None:
                    self._abrir()
                self.c.request("POST", caminho, body=json.dumps(corpo).encode(), headers=cabecalhos)
                r = self.c.getresponse()
                if r.status != 200:
                    txt = r.read()[:300].decode(errors="replace")
                    raise RuntimeError(f"HTTP {r.status}: {txt}")
                while True:
                    linha = r.readline()
                    if not linha:
                        break
                    linha = linha.decode(errors="replace").strip()
                    if not linha.startswith("data:"):
                        continue
                    dado = linha[5:].strip()
                    if dado == "[DONE]":
                        break
                    try:
                        ev = json.loads(dado)
                    except ValueError:
                        continue
                    pedaco = _texto_do_evento(ev)
                    if pedaco:
                        ao_texto(pedaco, ev)
                return
            except (OSError, http.client.HTTPException):
                self.fechar()
                if tentativa:
                    raise

    def aquecer(self):
        with self.trava:
            try:
                if self.c is None:
                    self._abrir()
            except OSError:
                self.c = None

    def fechar(self):
        try:
            if self.c:
                self.c.close()
        except OSError:
            pass
        self.c = None


def _texto_do_evento(ev):
    if ev.get("type") == "content_block_delta" and (ev.get("delta") or {}).get("type") == "text_delta":
        return ev["delta"].get("text", "")
    ch = ev.get("choices")  # servidor local compatível (llama-server)
    if ch and isinstance(ch, list):
        return ((ch[0] or {}).get("delta") or {}).get("content") or ""
    return ""


def prompt_quiz(pergunta, opcoes):
    return "Pergunta: " + pergunta + "\n" + "\n".join(f"{i + 1}) {o['texto']}" for i, o in enumerate(opcoes))


def _confianca(ev, digito):
    """Probabilidade do token com o dígito escolhido (llama-server com logprobs); None se o cérebro não informa."""
    import math
    try:
        for item in ev["choices"][0]["logprobs"]["content"]:
            if digito in item.get("token", ""):
                return math.exp(item["logprob"])
    except (KeyError, IndexError, TypeError):
        pass
    return None


def corpo_api(modelo, sistema, conteudo, pensar=False, esforco="low"):
    """Pedido mais rápido que cada modelo aceita (o raciocínio desliga de jeitos diferentes em cada família)."""
    corpo = {"model": modelo, "max_tokens": 16, "stream": True, "system": sistema,
             "messages": [{"role": "user", "content": conteudo}], "output_config": {"effort": esforco}}
    if pensar:
        corpo["max_tokens"] = 4000
    elif "haiku" in modelo:
        corpo["thinking"] = {"type": "disabled"}
    elif "sonnet-5-5" in modelo:
        corpo["thinking"] = {"type": "between_tools"}
    else:  # Opus 5.5 / Fable: o raciocínio não desliga; esforço baixo e espaço para pensar pouco
        corpo["max_tokens"] = 2000
    return corpo


class Cerebros:
    """Escada de inteligência: memória (ms) → modelo local com CONFIANÇA (~0,3 s) → modelos da API do mais fraco ao
    mais forte, todos disparados juntos. Vale: o local se tiver certeza alta; senão o mais forte que chegar no
    prazo; no aperto, a melhor resposta que já chegou."""

    def __init__(self, cfg):
        self.cfg = cfg
        cer = cfg.get("cerebros", ["memoria", "api"])
        self.modelos = list(cfg.get("modelos") or [cfg.get("modelo", MODELO)]) if "api" in cer else []
        base = re.match(r"^(https?)://([\w.-]+)(?::(\d+))?", cfg.get("api_base", "https://" + API_HOST))
        seguro = base.group(1) == "https"
        porta = int(base.group(3) or (443 if seguro else 80))
        self.conexoes = {m: Conexao(base.group(2), porta, seguro) for m in self.modelos}
        self.local = None
        if "local" in cer:
            m = re.match(r"^http://([\w.]+):(\d+)", cfg.get("local_url", "http://127.0.0.1:8080"))
            self.local = Conexao(m.group(1), int(m.group(2)), seguro=False) if m else None
        self.memoria = carregar_memoria()
        # aprendizado durante a partida: em TODA pergunta em que os dois respondem, o forte serve de gabarito para o
        # local; a precisão medida do local (com certeza alta) decide se ele pode agir sozinho
        self.limiar = float(cfg.get("confianca", 0.95))
        self.alvo = float(cfg.get("precisao_alvo", 0.9))
        self.trava = threading.Lock()
        self.acordos, self.discordancias, self.correcoes = 0, 0, collections.deque(maxlen=20)

    def precisao_local(self):
        """Acerto medido do local quando ele tem certeza alta, com um ponto de partida otimista (9 em 10)."""
        return (self.acordos + 9) / (self.acordos + self.discordancias + 10)

    def local_pode_sozinho(self, conf):
        return conf is not None and conf >= self.limiar and self.precisao_local() >= self.alvo

    def aprendizado(self):
        return {"limiar": self.limiar, "precisao_local": round(self.precisao_local(), 3), "alvo": self.alvo,
                "acordos": self.acordos, "discordancias": self.discordancias,
                "local_sozinho": self.precisao_local() >= self.alvo, "correcoes": list(self.correcoes)[-5:]}

    def _julgar(self, chave, pergunta, opcoes, local, forte):
        """local=(idx, conf) | None; forte=idx | None. Atualiza a memória e a precisão medida do local."""
        with self.trava:
            if forte is not None:
                self.memoria[chave] = opcoes[forte]["texto"]
            if forte is None or not local or local[1] is None or local[1] < self.limiar:
                return
            if local[0] == forte:
                self.acordos += 1
            else:
                self.discordancias += 1
                self.correcoes.append({"pergunta": pergunta[:100], "local": opcoes[local[0]]["texto"][:40],
                                       "forte": opcoes[forte]["texto"][:40], "certeza_local": round(local[1], 3)})

    def _completar(self, fila, restantes, chave, pergunta, opcoes, local, forte, forca, mais_forte):
        """Em segundo plano: espera a peça que falta (o local ou o forte) e julga."""
        fim = time.time() + 8
        while restantes and time.time() < fim and (local is None or forte is None):
            try:
                nome, idx, erro, seg, c = fila.get(timeout=max(0.01, fim - time.time()))
            except queue.Empty:
                break
            restantes -= 1
            if idx is None:
                continue
            if nome == "local":
                local = (idx, c)
            elif forca.get(nome, 0) == mais_forte:
                forte = idx
        self._julgar(chave, pergunta, opcoes, local, forte)

    @property
    def api(self):
        return bool(self.modelos)

    def aquecer(self):
        """Abre as conexões e, no modelo local, processa a política uma vez (fica no cache: a 1ª pergunta de
        verdade não paga os ~2 s de aquecimento)."""
        for c in list(self.conexoes.values()) + [self.local]:
            if c:
                threading.Thread(target=c.aquecer, daemon=True).start()
        if self.local:
            ops = [{"texto": "sim"}, {"texto": "não"}]
            threading.Thread(target=self._local, args=("Aquecimento: responda 1.", ops, queue.Queue(), time.time()),
                             daemon=True).start()

    def _api(self, modelo, pergunta, opcoes, fila, t0):
        chave = ler_chave()
        if not chave:
            fila.put((modelo, None, "sem chave da API no celular", time.time() - t0, None))
            return
        corpo = corpo_api(modelo, self.cfg.get("politica") or POLITICA, prompt_quiz(pergunta, opcoes),
                          bool(self.cfg.get("pensar")), self.cfg.get("esforco", "low"))
        self._correr(modelo, self.conexoes[modelo], "/v1/messages", corpo,
                     {"content-type": "application/json", "x-api-key": chave, "anthropic-version": API_VERSAO},
                     len(opcoes), fila, t0)

    def _local(self, pergunta, opcoes, fila, t0):
        corpo = {"messages": [{"role": "system", "content": self.cfg.get("politica") or POLITICA},
                              {"role": "user", "content": prompt_quiz(pergunta, opcoes)}],
                 "max_tokens": 4, "stream": True, "temperature": 0, "logprobs": True, "top_logprobs": 3}
        self._correr("local", self.local, "/v1/chat/completions", corpo, {"content-type": "application/json"},
                     len(opcoes), fila, t0)

    @staticmethod
    def _correr(nome, con, caminho, corpo, cab, n, fila, t0):
        achou = [False]
        buf = [""]

        def ao_texto(p, ev=None):
            if achou[0]:
                return
            buf[0] += p
            m = re.search(r"[1-9]", buf[0])
            if m and int(m.group()) <= n:
                achou[0] = True
                conf = _confianca(ev, m.group()) if ev else None
                fila.put((nome, int(m.group()) - 1, None, time.time() - t0, conf))  # streaming acionável

        try:
            con.post_stream(caminho, corpo, cab, ao_texto)
            if not achou[0]:
                fila.put((nome, None, f"resposta sem número: {buf[0][:40]!r}", time.time() - t0, None))
        except Exception as e:  # noqa: BLE001 — um cérebro falhar não derruba a corrida
            fila.put((nome, None, str(e)[:160], time.time() - t0, None))

    def decidir(self, pergunta, opcoes, prazo):
        """Devolve (índice ou None, fonte, segundos, erros). A fonte diz quem decidiu (e a certeza do local)."""
        t0 = time.time()
        lembrado = self.memoria.get(chave_quiz(pergunta, opcoes)) or self.memoria.get(norm(pergunta))
        if lembrado:
            for i, o in enumerate(opcoes):
                if norm(o["texto"]) == norm(lembrado):
                    return i, "memoria", time.time() - t0, []
        fila = queue.Queue()
        corredores = 0
        for modelo in self.modelos:
            threading.Thread(target=self._api, args=(modelo, pergunta, opcoes, fila, t0), daemon=True).start()
            corredores += 1
        if self.local:
            threading.Thread(target=self._local, args=(pergunta, opcoes, fila, t0), daemon=True).start()
            corredores += 1
        forca = {"local": 0, **{m: k + 1 for k, m in enumerate(self.modelos)}}
        mais_forte = max(forca.values()) if self.modelos else 0
        chave = chave_quiz(pergunta, opcoes)
        melhor, erros, local = None, [], None  # melhor = (força, índice, fonte, segundos)

        def julgar_depois(local_, forte_):
            if self.modelos and corredores:
                threading.Thread(target=self._completar, daemon=True,
                                 args=(fila, corredores, chave, pergunta, opcoes, local_, forte_, forca,
                                       mais_forte)).start()
            else:
                self._julgar(chave, pergunta, opcoes, local_, forte_)

        while corredores:
            resto = prazo - (time.time() - t0)
            if resto <= 0:
                break
            try:
                nome, idx, erro, seg, conf = fila.get(timeout=resto)
            except queue.Empty:
                break
            corredores -= 1
            if idx is None:
                erros.append(f"{nome}: {erro}")
                continue
            fonte = nome if conf is None else f"{nome} {conf:.0%}"
            if nome == "local":
                local = (idx, conf)
                if not self.modelos or self.local_pode_sozinho(conf):
                    julgar_depois(local, None)  # o forte segue e serve de gabarito
                    return idx, fonte, seg, erros
            if forca[nome] == mais_forte:
                julgar_depois(local, idx)  # o local (se ainda não chegou) é julgado quando chegar
                return idx, fonte, seg, erros
            if not melhor or forca[nome] > melhor[0]:
                melhor = (forca[nome], idx, fonte, seg)
        if melhor:
            return melhor[1], melhor[2], time.time() - t0, erros  # aperto: a melhor que chegou
        return None, None, time.time() - t0, erros


def carregar_memoria():
    try:
        with open(MEMORIA_ARQ, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def gravar_memoria(mem):
    os.makedirs(PASTA, exist_ok=True)
    tmp = MEMORIA_ARQ + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(mem, f, ensure_ascii=False)
    os.replace(tmp, MEMORIA_ARQ)


# ----------------------------------------------------------------------------------------------------- xadrez
INICIAL = "rnbqkbnrpppppppp" + "." * 32 + "PPPPPPPPRNBQKBNR"  # 8ª fileira primeiro


def tabuleiro_txt(casas):
    """64 caracteres, 8ª fileira primeiro (a8..h8, a7..h7, …), '.' vazia."""
    return "".join(casas[f"{c}{r}"][2] or "." for r in range(8, 0, -1) for c in "abcdefgh")


def minha_cor(casas):
    """Quem está embaixo na tela é quem joga (o app vira o tabuleiro para as pretas)."""
    return "w" if casas["a1"][1] > casas["a8"][1] else "b"


def quem_mexeu(antes, agora):
    """Cor de quem fez o lance entre dois tabuleiros: a peça que chegou numa casa (vazia ou de outra cor)."""
    for i, (a, b) in enumerate(zip(antes, agora)):
        if b != "." and a != b:
            return "w" if b.isupper() else "b"
    return None


def fen(tab, vez):
    linhas = []
    for r in range(8):
        lin, vazio = "", 0
        for ch in tab[8 * r:8 * r + 8]:
            if ch == ".":
                vazio += 1
            else:
                lin += (str(vazio) if vazio else "") + ch
                vazio = 0
        linhas.append(lin + (str(vazio) if vazio else ""))
    roque = ""  # direitos de roque presumidos pelas peças nas casas de origem
    if tab[60] == "K":
        roque += ("K" if tab[63] == "R" else "") + ("Q" if tab[56] == "R" else "")
    if tab[4] == "k":
        roque += ("k" if tab[7] == "r" else "") + ("q" if tab[0] == "r" else "")
    return f"{'/'.join(linhas)} {vez} {roque or '-'} - 0 1"


class Motor:
    """Stockfish (UCI) residente: cada lance em `ms` milissegundos."""

    def __init__(self, caminho="stockfish", elo=None, threads=None, hash_mb=None):
        import subprocess
        self.p = subprocess.Popen([caminho], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
        self._mandar("uci")
        self._ate("uciok")
        if threads:
            self._mandar(f"setoption name Threads value {max(1, min(int(threads), 8))}")
        if hash_mb:
            self._mandar(f"setoption name Hash value {max(16, min(int(hash_mb), 2048))}")
        if elo:
            self._mandar("setoption name UCI_LimitStrength value true")
            self._mandar(f"setoption name UCI_Elo value {int(elo)}")
        self._mandar("isready")
        self._ate("readyok")

    def _mandar(self, linha):
        self.p.stdin.write(linha + "\n")
        self.p.stdin.flush()

    def _ate(self, prefixo):
        while True:
            linha = self.p.stdout.readline()
            if not linha:
                raise RuntimeError("o motor fechou")
            if linha.startswith(prefixo):
                return linha.strip()

    def lance(self, fen_, ms):
        self._mandar(f"position fen {fen_}")
        self._mandar(f"go movetime {int(ms)}")
        r = self._ate("bestmove").split()
        return r[1] if len(r) > 1 and r[1] != "(none)" else None

    def tab_apos(self, posicao, movimentos):
        self._mandar(f"position fen {posicao} moves {movimentos}")
        self._mandar("d")
        linhas = self._ate("Fen:").split()[1].replace("/", "")
        return "".join("." * int(c) if c.isdigit() else c for c in linhas)

    def fen_apos_lance_legal(self, fen, lance):
        self._mandar(f"position fen {fen}")
        if lance not in set(self.respostas()):
            return None
        self._mandar(f"position fen {fen} moves {lance}")
        self._mandar("d")
        return self._ate("Fen:").partition(":")[2].strip()

    def respostas(self):
        self._mandar("go perft 1")
        while True:
            linha = self.p.stdout.readline()
            if not linha:
                raise RuntimeError("o motor fechou")
            if linha.startswith("Nodes searched:"):
                return
            lance, separador, total = linha.strip().partition(": ")
            if separador and total == "1":
                yield lance

    def fechar(self):
        try:
            self._mandar("quit")
            self.p.wait(timeout=2)
        except Exception:  # noqa: BLE001
            self.p.kill()


# ----------------------------------------------------------------------------------------------------- o laço
class Piloto:
    """Laço contínuo no celular. `ferramentas` traz as funções do agente de tela (para testar sem o aparelho)."""

    def __init__(self, ferramentas):
        self.f = ferramentas
        self.parar = threading.Event()
        self.th = None
        self.cfg = {}
        self.rodadas = collections.deque(maxlen=200)
        self.desde = 0.0
        self.estado_txt = "parado"
        self.cerebros = None

    @property
    def rodando(self):
        return bool(self.th and self.th.is_alive())

    def iniciar(self, cfg):
        self.encerrar()
        self.cfg = dict(cfg)
        self.cfg.setdefault("cerebros", ["memoria", "api"])
        self.cerebros = Cerebros(self.cfg)
        self.cerebros.aquecer()
        self.rodadas.clear()  # cada partida com o seu placar (o arquivo do gravador guarda tudo)
        self.parar = threading.Event()
        self.desde = time.time()
        alvo = self._laco_xadrez if self.cfg.get("modo") == "xadrez" else self._laco
        self.th = threading.Thread(target=alvo, name="piloto", daemon=True)
        self.th.start()
        return self.estado()

    def encerrar(self):
        self.parar.set()
        if self.th and self.th.is_alive():
            self.th.join(timeout=3)
        self.estado_txt = "parado"

    def _laco_xadrez(self):
        """Xadrez contra o robô: lê o tabuleiro, percebe a vez (a última peça que se mexeu foi do adversário), pede o
        lance ao motor e toca origem e destino. Só na tela de partida contra robô (f["contra_robo"])."""
        f, cfg = self.f, self.cfg
        validar_partida = (lambda: f["contra_robo"](cfg["app"])) if cfg.get("app") else f["contra_robo"]
        ms = max(50, min(int(cfg.get("ms_lance", 300)), 30000))
        fim = time.time() + max(10, min(float(cfg.get("duracao", 600)), 3600))
        try:
            motor = Motor(cfg.get("motor", "stockfish"), cfg.get("elo"), cfg.get("threads"), cfg.get("hash_mb"))
        except Exception as e:  # noqa: BLE001
            self.estado_txt = f"erro: motor não abriu ({str(e)[:80]})"
            return
        visto, meu_ultimo, contador, conferido = None, None, 0, 0.0
        self.estado_txt = "olhando o tabuleiro"
        try:
            while not self.parar.is_set() and time.time() < fim:
                if time.time() - conferido > 3:  # a trava: só contra o robô
                    conferido = time.time()
                    if not validar_partida():
                        self.estado_txt = "parado: não é partida contra robô"
                        break
                contador = f["aguardar"](contador, 250)
                t_mud = time.time()
                casas = f["casas"]()
                if not casas:
                    continue
                tab = tabuleiro_txt(casas)
                c_b = f["casas"]()  # duas leituras iguais: peça a meio caminho não conta
                if not c_b or tabuleiro_txt(c_b) != tab:
                    continue
                cor = minha_cor(casas)
                if visto is None:  # começo: brancas no início, ou `minha_vez` dito por quem ligou no meio da partida
                    minha_vez = (cor == "w" and tab == INICIAL) or bool(cfg.get("minha_vez"))
                elif tab == visto:
                    if meu_ultimo != "refazer":
                        continue
                    minha_vez = True  # o último toque não pegou: joga de novo
                else:
                    minha_vez = quem_mexeu(visto, tab) not in (None, cor)
                visto = tab
                if not minha_vez:
                    continue
                t_lido = time.time()
                n = len(self.rodadas)  # relógio: pensa menos conforme a partida se alonga (bullet não perde no tempo)
                ms_agora = ms if n < 30 else (max(100, ms // 2) if n < 50 else 100)
                posicao = fen(tab, cor)
                lance = motor.lance(posicao, ms_agora)
                t_dec = time.time()
                if not lance:
                    self.estado_txt = "fim de jogo (sem lance)"
                    break
                esperado = motor.tab_apos(posicao, lance)
                respostas = None
                if self.parar.is_set() or not validar_partida():
                    self.estado_txt = "parado: tabuleiro do robô indisponível"
                    break
                a, b = casas[lance[:2]], casas[lance[2:4]]
                f["tocar"](a[0], a[1])
                time.sleep(0.06)
                f["tocar"](b[0], b[1])
                if len(lance) == 5:  # promoção: o app mostra as peças sobre a casa de destino (a dama primeiro)
                    time.sleep(0.25)
                    f["tocar"](b[0], b[1])
                t_toque = time.time()
                meu_ultimo = None
                # confirmação: o tabuleiro tem de mudar com uma peça MINHA; senão, refaz na próxima volta
                ok = False
                limite = time.time() + 1.0
                while time.time() < limite:
                    contador = f["aguardar"](contador, 150)
                    c2 = f["casas"]()
                    if c2:
                        t2 = tabuleiro_txt(c2)
                        if t2 == esperado:
                            visto, ok = esperado, True
                            break
                        if t2 != tab and quem_mexeu(esperado, t2) not in (None, cor):
                            if respostas is None:
                                legais = list(motor.respostas())
                                respostas = {motor.tab_apos(posicao, f"{lance} {r}") for r in legais}
                            if t2 not in respostas:
                                continue
                            # A próxima leitura compara a resposta do robô com nosso lance.
                            visto, ok = esperado, True
                            break
                if not ok:
                    meu_ultimo = "refazer"
                self.rodadas.append({"t": round(t_mud, 3), "lance": lance, "ok": ok,
                                     "ler_ms": int((t_lido - t_mud) * 1000), "decidir_ms": int((t_dec - t_lido) * 1000),
                                     "tocar_ms": int((t_toque - t_dec) * 1000), "total_ms": int((t_toque - t_mud) * 1000),
                                     "fonte": "motor"})
                self.estado_txt = f"jogando ({len(self.rodadas)} lances)"
        except Exception as e:  # noqa: BLE001
            self.estado_txt = f"erro: {str(e)[:120]}"
        finally:
            motor.fechar()
            if not self.estado_txt.startswith(("parado", "erro", "fim")):
                self.estado_txt = "parado"

    def _laco(self):
        f, cfg = self.f, self.cfg
        prazo = max(0.3, min(float(cfg.get("prazo", 2.0)), 20))
        ignorar = tuple(cfg.get("ignorar") or ()) + IGNORAR
        ultima, contador, rasgada_desde = None, 0, None
        fim = time.time() + max(10, min(float(cfg.get("duracao", 600)), 3600))
        self.estado_txt = "olhando"
        while not self.parar.is_set() and time.time() < fim:
            try:
                contador = f["aguardar"](contador, 350)  # dorme até a tela mudar (ou 350 ms)
                t_mud = time.time()
                els = f["elementos"]()
                pacotes = collections.Counter(e.get("pacote") for e in els if e.get("pacote"))
                if any(f["bloqueado"](p) for p in pacotes):
                    self.estado_txt = "app bloqueado na tela: parado"
                    break
                if cfg.get("app"):
                    if cfg["app"] not in pacotes:
                        self.estado_txt = f"esperando o app {cfg['app']}"
                        continue
                    els = [e for e in els if e.get("pacote") in (cfg["app"], None, "")]  # sem sobreposições
                self.estado_txt = "jogando"
                q = quiz_da_tela(els, ignorar)
                if not q:
                    continue
                pergunta, opcoes = q
                chave = chave_quiz(pergunta, opcoes)
                if chave == ultima:
                    continue
                # leitura rasgada: a acessibilidade atualiza em partes (a pergunta muda antes dos botões). Pergunta e
                # opções têm de mudar JUNTAS em relação à última respondida; se só uma mudou, espera o próximo quadro
                # (até 400 ms — duas perguntas seguidas podem ter as mesmas opções de verdade).
                if ultima and rasgada_desde is None:
                    p_ant, o_ant = ultima.split(" || ", 1)
                    p_agora, o_agora = chave.split(" || ", 1)
                    if (p_ant == p_agora) != (o_ant == o_agora):
                        rasgada_desde = time.time()
                        continue
                elif rasgada_desde is not None and time.time() - rasgada_desde < 0.4:
                    p_ant, o_ant = ultima.split(" || ", 1)
                    p_agora, o_agora = chave.split(" || ", 1)
                    if (p_ant == p_agora) != (o_ant == o_agora):
                        continue
                rasgada_desde = None
                els2 = f["elementos"]()
                if cfg.get("app"):
                    els2 = [e for e in els2 if e.get("pacote") in (cfg["app"], None, "")]
                q2 = quiz_da_tela(els2, ignorar)  # confirmação: duas leituras iguais seguidas
                if not q2 or chave_quiz(*q2) != chave:
                    continue
                t_lido = time.time()
                idx, fonte, seg, erros = self.cerebros.decidir(pergunta, opcoes, prazo)
                if idx is None and cfg.get("chutar", True):
                    idx, fonte = 0, "chute"
                t_dec = time.time()
                toque = None
                if idx is not None:
                    alvo = opcoes[idx]
                    if cfg.get("conferir", True):  # alvo semântico: relocaliza o texto escolhido na tela de agora
                        agora_els = f["elementos"]()
                        if cfg.get("app"):
                            agora_els = [e for e in agora_els if e.get("pacote") in (cfg["app"], None, "")]
                        agora = quiz_da_tela(agora_els, ignorar)
                        if not agora or norm(agora[0]) != norm(pergunta):
                            self._registrar(pergunta, opcoes, idx, fonte, "descartado: a pergunta mudou", t_mud,
                                            t_lido, t_dec, None, erros)
                            ultima = chave
                            continue
                        mesmo = [o for o in agora[1] if norm(o["texto"]) == norm(alvo["texto"])]
                        alvo = mesmo[0] if mesmo else alvo
                    f["tocar"](alvo["x"], alvo["y"])
                    toque = time.time()
                    if fonte and not fonte.startswith(("memoria", "chute", "local")):
                        self.cerebros.memoria[chave] = alvo["texto"]  # memória só guarda resposta de cérebro forte
                self._registrar(pergunta, opcoes, idx, fonte, None, t_mud, t_lido, t_dec, toque, erros)
                ultima = chave
                if len(self.rodadas) % 5 == 0:
                    gravar_memoria(self.cerebros.memoria)
            except Exception as e:  # noqa: BLE001 — o laço não morre por uma tela estranha
                self.estado_txt = f"erro: {str(e)[:120]}"
                time.sleep(0.3)
        gravar_memoria(self.cerebros.memoria)
        if "bloqueado" not in self.estado_txt:
            self.estado_txt = "parado"

    def _registrar(self, pergunta, opcoes, idx, fonte, motivo, t_mud, t_lido, t_dec, t_toque, erros):
        r = {"t": round(t_mud, 3), "pergunta": pergunta[:160], "opcoes": [o["texto"][:60] for o in opcoes],
             "escolha": opcoes[idx]["texto"][:60] if idx is not None else None, "fonte": fonte,
             "ler_ms": int((t_lido - t_mud) * 1000), "decidir_ms": int((t_dec - t_lido) * 1000),
             "tocar_ms": int((t_toque - t_dec) * 1000) if t_toque else None,
             "total_ms": int((t_toque - t_mud) * 1000) if t_toque else None}
        if motivo:
            r["motivo"] = motivo
        if erros:
            r["erros"] = erros[:3]
        self.rodadas.append(r)
        try:
            os.makedirs(PASTA, exist_ok=True)
            with open(GRAVADOR_ARQ, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        except OSError:
            pass

    def estado(self, ultimas=8):
        tot = sorted(r["total_ms"] for r in self.rodadas if r.get("total_ms") is not None)

        def pct(p):
            return tot[min(len(tot) - 1, int(p * len(tot)))] if tot else None
        fontes = collections.Counter(r.get("fonte") for r in self.rodadas)
        return {"rodando": self.rodando, "estado": self.estado_txt, "desde": int(self.desde) if self.desde else None,
                "rodadas": len(self.rodadas), "total_ms_p50": pct(0.5), "total_ms_p95": pct(0.95),
                "fontes": dict(fontes), "chave_api": bool(ler_chave()),
                "aprendizado": self.cerebros.aprendizado() if self.cerebros else None,
                "cfg": {k: v for k, v in self.cfg.items() if k != "politica"},
                "ultimas": list(self.rodadas)[-ultimas:]}

