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
        # aprendizado durante a partida: o forte confere o local em segundo plano e a exigência de certeza sobe
        self.limiar = float(cfg.get("confianca", 0.95))
        self.trava = threading.Lock()
        self.acordos, self.erros_local, self.correcoes = 0, [], collections.deque(maxlen=20)

    def aprendizado(self):
        return {"limiar": round(self.limiar, 3), "acordos": self.acordos, "erros_local": list(self.erros_local),
                "correcoes": list(self.correcoes)[-5:]}

    def _verificar(self, fila, restantes, chave, pergunta, opcoes, idx_local, conf, forca, mais_forte):
        """O local já tocou sozinho; o mais forte continua e confere. Discordou → o local errou com essa certeza:
        o limiar sobe acima dela (o rápido só age sozinho quando provou ser confiável) e a memória guarda o certo."""
        fim = time.time() + 8
        while restantes and time.time() < fim:
            try:
                nome, idx, erro, seg, c = fila.get(timeout=max(0.01, fim - time.time()))
            except queue.Empty:
                return
            restantes -= 1
            if idx is None or forca.get(nome, 0) != mais_forte:
                continue
            with self.trava:
                self.memoria[chave] = opcoes[idx]["texto"]
                if idx == idx_local:
                    self.acordos += 1
                else:
                    self.erros_local.append(round(conf, 3))
                    self.limiar = min(1.01, max(self.limiar, conf + 0.005))
                    self.correcoes.append({"pergunta": pergunta[:100], "local": opcoes[idx_local]["texto"][:40],
                                           "forte": opcoes[idx]["texto"][:40], "certeza_local": round(conf, 3)})
            return

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
        limiar = self.limiar
        forca = {"local": 0, **{m: k + 1 for k, m in enumerate(self.modelos)}}
        mais_forte = max(forca.values()) if self.modelos else 0
        melhor, erros = None, []  # (força, índice, fonte, segundos)
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
            if nome == "local" and (not self.modelos or conf is None or conf >= limiar):
                if self.modelos and conf is not None and corredores:  # o forte segue conferindo em segundo plano
                    threading.Thread(target=self._verificar, daemon=True,
                                     args=(fila, corredores, chave_quiz(pergunta, opcoes), pergunta, opcoes, idx,
                                           conf, forca, mais_forte)).start()
                return idx, fonte, seg, erros  # o rápido tem certeza (ou é o único): vai já
            if forca[nome] == mais_forte:
                return idx, fonte, seg, erros  # o mais forte chegou: vai
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
        self.parar = threading.Event()
        self.desde = time.time()
        self.th = threading.Thread(target=self._laco, name="piloto", daemon=True)
        self.th.start()
        return self.estado()

    def encerrar(self):
        self.parar.set()
        if self.th and self.th.is_alive():
            self.th.join(timeout=3)
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
                app = next((e.get("pacote") for e in els if e.get("pacote")), "")
                if cfg.get("app") and app != cfg["app"]:
                    self.estado_txt = f"esperando o app {cfg['app']}"
                    continue
                if f["bloqueado"](app):
                    self.estado_txt = "app bloqueado: parado"
                    break
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
                q2 = quiz_da_tela(f["elementos"](), ignorar)  # confirmação: duas leituras iguais seguidas
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
                        agora = quiz_da_tela(f["elementos"](), ignorar)
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
