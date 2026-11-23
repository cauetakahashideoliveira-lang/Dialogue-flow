"""Jogador que aprende (roda no celular, só numpy).

Laço: olha o quadro → reconhece a situação → escolhe uma habilidade → executa → mede a recompensa → aprende.

- Situação: o quadro é reduzido a 16x9 em tons de cinza; quadros parecidos caem no mesmo "estado"
  (protótipos que se ajustam sozinhos; um quadro diferente de todos vira estado novo, até `estados_max`).
- Escolha: valor aprendido por (estado, habilidade) + bônus de curiosidade (UCB) + o que foi demonstrado.
- Aprendizado: Q ← Q + α·(r + γ·max Q(próximo) − Q). Recompensa vem dos detectores da tela (barra de vida,
  mudança numa região, cor que aparece) e das notas que o Claude/usuário dão (acao=jogador, nota=±1).
- Demonstração: habilidades rodadas à mão com a gravação ligada contam como exemplo para aquele estado.
- Tudo o que acontece fica gravado (estado, habilidade, recompensa e quadros-chave) para o Claude revisar
  e reescrever as habilidades — o "técnico" fora do laço.
"""
import json
import math
import os
import random
import time

import numpy as np

LARGURA, ALTURA = 16, 9


# --------------------------------------------------------------------------- visão
def reduzir(rgb, w=LARGURA, h=ALTURA):
    """rgb: array HxWx3 uint8 → vetor w*h*3 em [0,1] (média por bloco, mantendo a cor)."""
    a = np.asarray(rgb, dtype=np.float32)
    if a.ndim == 2:
        a = np.repeat(a[..., None], 3, axis=2)
    a = a[..., :3]
    H, W = a.shape[:2]
    ys = np.minimum(np.linspace(0, H, h + 1).astype(int)[:-1], H - 1)
    xs = np.minimum(np.linspace(0, W, w + 1).astype(int)[:-1], W - 1)
    linhas = np.add.reduceat(a, ys, axis=0) / np.diff(np.append(ys, H))[:, None, None]
    blocos = np.add.reduceat(linhas, xs, axis=1) / np.diff(np.append(xs, W))[None, :, None]
    return (blocos / 255.0).astype(np.float32).ravel()


def regiao(rgb, r):
    """r = [x, y, largura, altura] em frações da tela (0–1)."""
    a = np.asarray(rgb)
    H, W = a.shape[:2]
    x, y, w, h = [float(v) for v in r]
    x0, y0 = int(max(0, min(1, x)) * W), int(max(0, min(1, y)) * H)
    x1, y1 = max(x0 + 1, int(min(1, x + w) * W)), max(y0 + 1, int(min(1, y + h) * H))
    return a[y0:y1, x0:x1, :3].astype(np.float32)


def fracao_cor(rgb, r, cor, tol=60):
    pedaco = regiao(rgb, r)
    d = np.sqrt(((pedaco - np.asarray(cor, dtype=np.float32)) ** 2).sum(axis=2))
    return float((d <= float(tol)).mean())


def mascara_cor(pedaco, spec):
    """spec: {cor:[r,g,b], tolerancia} (RGB), {matiz:[min,max] graus, sat_min, val_min} (HSV) ou
    {sat_max, val_min, val_max} (cinza/metal)."""
    a = np.asarray(pedaco, dtype=np.float32)[..., :3]
    if "matiz" in spec:
        r, g, b = a[..., 0] / 255, a[..., 1] / 255, a[..., 2] / 255
        mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
        d = mx - mn + 1e-6
        h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
        sat = np.where(mx > 0, (mx - mn) / (mx + 1e-6), 0)
        h0, h1 = [float(x) for x in spec["matiz"]]
        dentro = (h >= h0) & (h <= h1) if h0 <= h1 else (h >= h0) | (h <= h1)
        return dentro & (sat >= float(spec.get("sat_min", 0.4))) & (mx >= float(spec.get("val_min", 0.3)))
    if "sat_max" in spec:  # "metal"/cinza: pouca saturação e brilho numa faixa (ex.: armadura prateada)
        mx, mn = a.max(axis=2) / 255, a.min(axis=2) / 255
        sat = (mx - mn) / (mx + 1e-6)
        return ((sat <= float(spec["sat_max"])) & (mx >= float(spec.get("val_min", 0.3)))
                & (mx <= float(spec.get("val_max", 0.8))))
    dist = np.sqrt(((a - np.asarray(spec.get("cor", [255, 255, 255]), dtype=np.float32)) ** 2).sum(axis=2))
    return dist <= float(spec.get("tolerancia", 60))


def medir(rgb, det):
    t = det.get("tipo", "barra")
    if t == "vida":  # fração acesa da barra (qualquer cor: amarela, vermelha, branca); perdida = escura
        pedaco = regiao(rgb, det["regiao"])
        return float((pedaco.max(axis=2) >= float(det.get("limiar_brilho", 110))).mean())
    if t in ("barra", "cor_aparece"):
        return fracao_cor(rgb, det["regiao"], det.get("cor", [255, 255, 255]), det.get("tolerancia", 60))
    if t == "brilho":
        return float(regiao(rgb, det["regiao"]).mean() / 255.0)
    if t == "mudanca":
        return regiao(rgb, det["regiao"]).mean(axis=2)
    raise ValueError(f"detector desconhecido: {t}")


def recompensa(antes, depois, detectores):
    """Soma dos detectores entre dois quadros. Devolve (total, detalhes)."""
    total, det_out = 0.0, {}
    for i, d in enumerate(detectores or []):
        nome = d.get("nome") or f"{d.get('tipo', 'barra')}{i}"
        peso = float(d.get("peso", 1.0))
        a, b = medir(antes, d), medir(depois, d)
        if d.get("tipo") == "mudanca":
            v = float(np.abs(b - a).mean() / 255.0) if a.shape == b.shape else 0.0
        elif d.get("tipo") == "cor_aparece":
            limiar = float(d.get("limiar", 0.3))
            v = 1.0 if (a < limiar <= b) else 0.0
        else:
            v = b - a
        limite = d.get("limite")
        if limite is not None and abs(v) > float(limite):
            v = 0.0  # salto grande = troca de round/tela, não foi a jogada
        det_out[nome] = round(peso * v, 4)
        total += peso * v
    return total, det_out


# --------------------------------------------------------------------------- percepção da luta
def centro_x(rgb, area, spec, minimo=0.0008):
    """Centro horizontal (0–1 da tela) dos pixels da cor `spec` dentro de `area`; None se quase não aparece."""
    pedaco = regiao(rgb, area)
    m = mascara_cor(pedaco, spec)
    frac = float(m.mean())
    if frac < minimo:
        return None, frac, None
    ys, xs = np.nonzero(m)
    x0, y0, w, h = [float(v) for v in area]
    cx = x0 + (float(np.median(xs)) + 0.5) / m.shape[1] * w  # mediana: o cenário não puxa o centro
    topo = y0 + np.percentile(ys, 5) / m.shape[0] * h  # topo do lutador (pulo = topo alto)
    return float(cx), frac, float(topo)


def perceber(rgb, cfg):
    """cfg: {area, eu:{spec}, rival:{spec}, distancias:[perto, medio], topo_pulo}. Devolve contexto + chave."""
    area = cfg.get("area", [0.0, 0.15, 1.0, 0.8])
    eu, fe, te = centro_x(rgb, area, cfg["eu"], cfg.get("minimo", 0.0008))
    rv, fr, tr = centro_x(rgb, area, cfg["rival"], cfg.get("minimo", 0.0008))
    agora = time.monotonic()
    memoria = cfg.get("_visto") or {}
    # um lutador some por um instante (clarão, golpe, sobreposição): usa a última posição vista há pouco
    if eu is None and agora - memoria.get("eu_t", -9) < float(cfg.get("memoria_s", 1.5)):
        eu, te = memoria["eu"], memoria.get("eu_topo")
    if rv is None and agora - memoria.get("rv_t", -9) < float(cfg.get("memoria_s", 1.5)):
        rv, tr = memoria["rv"], memoria.get("rv_topo")
    if eu is not None and fe >= float(cfg.get("minimo", 0.0008)):
        memoria.update({"eu": eu, "eu_topo": te, "eu_t": agora})
    if rv is not None and fr >= float(cfg.get("minimo", 0.0008)):
        memoria.update({"rv": rv, "rv_topo": tr, "rv_t": agora})
    cfg["_visto"] = memoria
    ctx = {"eu_x": None if eu is None else round(eu, 3), "rival_x": None if rv is None else round(rv, 3),
           "eu_frac": round(fe, 4), "rival_frac": round(fr, 4)}
    if eu is None or rv is None:
        ctx.update({"frente": cfg.get("_ultimo_frente", "RIGHT"), "chave": "sem_lutador"})
        return ctx
    dist = abs(rv - eu)
    p, m = cfg.get("distancias", [0.16, 0.32])
    faixa = "perto" if dist < p else ("medio" if dist < m else "longe")
    frente = "RIGHT" if rv >= eu else "LEFT"
    cfg["_ultimo_frente"] = frente
    pulo_lim = float(cfg.get("topo_pulo", 0.25))
    rival_alto = tr is not None and tr < pulo_lim
    canto = "canto" if min(eu, 1 - eu) < float(cfg.get("canto", 0.12)) else "meio"
    ctx.update({"distancia": round(dist, 3), "faixa": faixa, "frente": frente, "rival_no_ar": bool(rival_alto),
                "eu_topo": None if te is None else round(te, 3), "rival_topo": None if tr is None else round(tr, 3),
                "chave": f"{faixa}|{'ar' if rival_alto else 'chao'}|{canto}"})
    return ctx


# --------------------------------------------------------------------------- estados
class Estados:
    def __init__(self, limiar=0.08, maximo=48):
        self.limiar, self.maximo = float(limiar), int(maximo)
        self.prot = []  # vetores
        self.n = []

    def atribuir(self, v, aprender=True):
        v = np.asarray(v, dtype=np.float32)
        if not self.prot:
            self.prot.append(v.copy())
            self.n.append(1)
            return 0
        P = np.stack(self.prot)
        d = np.sqrt(((P - v) ** 2).mean(axis=1))
        i = int(d.argmin())
        if d[i] > self.limiar and len(self.prot) < self.maximo and aprender:
            self.prot.append(v.copy())
            self.n.append(1)
            return len(self.prot) - 1
        if aprender:
            self.n[i] += 1
            taxa = max(0.02, 1.0 / self.n[i])
            self.prot[i] = self.prot[i] + taxa * (v - self.prot[i])
        return i

    def dump(self):
        return {"limiar": self.limiar, "maximo": self.maximo, "n": self.n,
                "prot": [[round(float(x), 4) for x in p] for p in self.prot]}

    @classmethod
    def load(cls, d):
        e = cls(d.get("limiar", 0.08), d.get("maximo", 48))
        e.prot = [np.asarray(p, dtype=np.float32) for p in d.get("prot", [])]
        e.n = list(d.get("n", [1] * len(e.prot)))
        return e


# --------------------------------------------------------------------------- cérebro
class Cerebro:
    """Q-learning tabular sobre (estado, habilidade) + UCB + demonstrações."""

    def __init__(self, habilidades, alfa=0.3, gama=0.6, curiosidade=0.5, peso_demo=0.3):
        self.hab = list(habilidades)
        self.alfa, self.gama, self.curiosidade, self.peso_demo = alfa, gama, curiosidade, peso_demo
        self.q, self.cont, self.demo = {}, {}, {}

    def _k(self, s, h):
        return f"{s}|{h}"

    def valor(self, s, h):
        return self.q.get(self._k(s, h), 0.0)

    def escolher(self, s, explorar=True):
        total = sum(self.cont.get(self._k(s, h), 0) for h in self.hab) + 1
        melhor, pont = None, -math.inf
        for h in self.hab:
            n = self.cont.get(self._k(s, h), 0)
            p = self.valor(s, h) + self.peso_demo * self.demo.get(self._k(s, h), 0) ** 0.5
            if explorar:
                p += self.curiosidade * math.sqrt(math.log(total + 1) / (n + 1)) + random.random() * 1e-6
            if p > pont:
                melhor, pont = h, p
        return melhor

    def aprender(self, s, h, r, s2=None):
        k = self._k(s, h)
        alvo = r + (self.gama * max(self.valor(s2, x) for x in self.hab) if s2 is not None else 0.0)
        self.q[k] = self.valor(s, h) + self.alfa * (alvo - self.valor(s, h))
        self.cont[k] = self.cont.get(k, 0) + 1

    def demonstrar(self, s, h):
        if h not in self.hab:
            self.hab.append(h)
        k = self._k(s, h)
        self.demo[k] = self.demo.get(k, 0) + 1

    def politica(self, n_estados):
        out = {}
        for s in range(n_estados):
            vals = {h: round(self.valor(s, h), 3) for h in self.hab if self._k(s, h) in self.cont}
            if vals:
                out[s] = {"melhor": max(vals, key=vals.get), "valores": vals,
                          "tentativas": sum(self.cont.get(self._k(s, h), 0) for h in self.hab)}
        return out

    def dump(self):
        return {"hab": self.hab, "alfa": self.alfa, "gama": self.gama, "curiosidade": self.curiosidade,
                "peso_demo": self.peso_demo, "q": self.q, "cont": self.cont, "demo": self.demo}

    @classmethod
    def load(cls, d, habilidades=None):
        c = cls(habilidades or d.get("hab", []), d.get("alfa", 0.3), d.get("gama", 0.6),
                d.get("curiosidade", 0.5), d.get("peso_demo", 0.3))
        for h in d.get("hab", []):
            if h not in c.hab:
                c.hab.append(h)
        c.q, c.cont, c.demo = dict(d.get("q", {})), dict(d.get("cont", {})), dict(d.get("demo", {}))
        return c


# --------------------------------------------------------------------------- jogador
class Jogador:
    """Junta visão, cérebro, memória em disco e gravador. Não sabe nada do PS4: recebe
    `olhar()` → quadro RGB e `agir(nome_habilidade)` → executa (para testar com um jogo de mentira)."""

    def __init__(self, pasta, jogo, habilidades, detectores, limiar=0.08, estados_max=48, percepcao=None,
                 **cerebro_cfg):
        self.pasta = os.path.join(pasta, _seguro(jogo))
        self.jogo = jogo
        self.detectores = list(detectores or [])
        os.makedirs(os.path.join(self.pasta, "quadros"), exist_ok=True)
        mem = self._ler()
        self.estados = Estados.load(mem["estados"]) if mem.get("estados") else Estados(limiar, estados_max)
        self.cerebro = (Cerebro.load(mem["cerebro"], habilidades) if mem.get("cerebro")
                        else Cerebro(habilidades, **cerebro_cfg))
        for k, v in cerebro_cfg.items():
            setattr(self.cerebro, k, v)
        self.percepcao = percepcao if percepcao is not None else mem.get("percepcao")
        self.chaves = dict(mem.get("chaves", {}))  # chave da percepção → número do estado
        self.ultimo_ctx = {}
        self.historico = list(mem.get("historico", []))  # recompensa média por bloco de passos
        self.passos_total = int(mem.get("passos_total", 0))
        self.ultimos = []  # (estado, habilidade, recompensa) dos passos recentes (para notas)
        self.bloco = []

    # ---- memória
    def _arq(self):
        return os.path.join(self.pasta, "memoria.json")

    def _ler(self):
        try:
            with open(self._arq()) as f:
                return json.load(f)
        except (OSError, ValueError):
            return {}

    def salvar(self):
        d = {"jogo": self.jogo, "estados": self.estados.dump(), "cerebro": self.cerebro.dump(),
             "historico": self.historico[-500:], "passos_total": self.passos_total,
             "detectores": self.detectores, "percepcao": {k: v for k, v in (self.percepcao or {}).items()
                                                          if not k.startswith("_")} or None,
             "chaves": self.chaves, "salvo": time.strftime("%Y-%m-%d %H:%M:%S")}
        tmp = self._arq() + ".tmp"
        with open(tmp, "w") as f:
            json.dump(d, f)
        os.replace(tmp, self._arq())

    def gravar(self, reg):
        with open(os.path.join(self.pasta, "gravacao.jsonl"), "a") as f:
            f.write(json.dumps(reg, ensure_ascii=False) + "\n")

    # ---- situação
    def situacao(self, quadro, aprender=True):
        """Estado (número) + contexto. Com percepção: chave legível (perto|chao|meio...); sem: protótipos."""
        if not self.percepcao:
            return self.estados.atribuir(reduzir(quadro), aprender), {}
        ctx = perceber(quadro, self.percepcao)
        k = ctx["chave"]
        if k not in self.chaves:
            if not aprender:
                return -1, ctx
            self.chaves[k] = len(self.chaves)
        return self.chaves[k], ctx

    def nome_estado(self, s):
        for k, v in self.chaves.items():
            if v == s:
                return k
        return str(s)

    # ---- um passo
    def passo(self, olhar, agir, explorar=True, guardar_quadro=None):
        q0 = olhar()
        if q0 is None:
            return {"erro": "sem imagem do jogo"}
        s, ctx = self.situacao(q0)
        self.ultimo_ctx = ctx
        h = self.reflexo(q0, ctx) or self.cerebro.escolher(s, explorar)
        t0 = time.monotonic()
        try:
            agir(h, ctx)
        except TypeError:
            agir(h)
        q1 = olhar()
        if q1 is None:
            return {"erro": "sem imagem do jogo"}
        r, det = recompensa(q0, q1, self.detectores)
        s2, _ = self.situacao(q1, aprender=False)
        s2 = None if s2 < 0 else s2
        self.cerebro.aprender(s, h, r, s2)
        self.passos_total += 1
        self.ultimos = (self.ultimos + [(s, h, r)])[-20:]
        self.bloco.append(r)
        if len(self.bloco) >= 25:
            self.historico.append(round(sum(self.bloco) / len(self.bloco), 4))
            self.bloco = []
        reg = {"t": round(time.time(), 2), "passo": self.passos_total, "estado": s,
               "situacao": ctx.get("chave"), "frente": ctx.get("frente"), "habilidade": h,
               "recompensa": round(r, 4), "detalhes": det, "proximo": s2, "ms": int((time.monotonic() - t0) * 1000)}
        if guardar_quadro and (abs(r) >= 0.05 or self.passos_total % 50 == 1):
            reg["quadro"] = guardar_quadro(q1, f"p{self.passos_total:06d}")
        self.gravar(reg)
        return reg

    def reflexo(self, quadro, ctx):
        """Camada rápida antes do aprendido (cfg em self.reflexos): defende quando o rival perto se mexe forte
        ou quando acabei de levar dano; depois de uma defesa sem dano, pune. Devolve a habilidade ou None."""
        cfg = getattr(self, "reflexos", None)
        if not cfg:
            return None
        ant, self._q_ant = getattr(self, "_q_ant", None), quadro
        vida_det = next((d for d in self.detectores if d.get("nome") == cfg.get("minha_vida", "minha_vida")), None)
        vida = medir(quadro, vida_det) if vida_det else None
        vida_ant, self._vida_ant = getattr(self, "_vida_ant", None), vida
        levou = vida is not None and vida_ant is not None and vida_ant - vida > float(cfg.get("dano_min", 0.01))
        ultimo = self.ultimos[-1][1] if self.ultimos else None
        if ultimo in cfg.get("defesas", []) and not levou and cfg.get("punir"):
            if ctx.get("faixa") in ("perto", "medio") and random.random() < float(cfg.get("prob_punir", 0.8)):
                self.reflexos_usados = getattr(self, "reflexos_usados", 0) + 1
                return random.choice(cfg["punir"])
        perto = ctx.get("faixa") in tuple(cfg.get("faixas", ["perto", "medio"]))
        mov = 0.0
        if ant is not None and ctx.get("rival_x") is not None and ant.shape == quadro.shape:
            x = float(ctx["rival_x"])
            r = [max(0.0, x - 0.12), 0.3, 0.24, 0.6]
            mov = float(np.abs(regiao(quadro, r) - regiao(ant, r)).mean() / 255.0)
        ctx["mov_rival"] = round(mov, 4)
        if levou or (perto and mov > float(cfg.get("limiar_mov", 0.05))):
            self.reflexos_usados = getattr(self, "reflexos_usados", 0) + 1
            defs = cfg.get("defesas") or []
            if defs:
                return defs[1] if (ctx.get("rival_no_ar") is False and len(defs) > 1 and random.random() < 0.35) \
                    else defs[0]
        return None

    def demonstrar(self, quadro, habilidade):
        s, _ = self.situacao(quadro)
        self.cerebro.demonstrar(s, habilidade)
        self.gravar({"t": round(time.time(), 2), "demo": True, "estado": s, "habilidade": habilidade})
        return s

    def nota(self, valor, ultimos=5):
        """Nota do técnico (Claude/usuário) para as últimas jogadas: reforça ou pune."""
        alvo = self.ultimos[-max(1, int(ultimos)):]
        for s, h, _ in alvo:
            self.cerebro.aprender(s, h, float(valor), None)
        self.gravar({"t": round(time.time(), 2), "nota": float(valor), "jogadas": [[s, h] for s, h, _ in alvo]})
        return len(alvo)

    def relatorio(self):
        n = len(self.chaves) if self.percepcao else len(self.estados.prot)
        pol = self.cerebro.politica(n)
        if self.percepcao:
            pol = {self.nome_estado(s): v for s, v in pol.items()}
        hist = self.historico[-40:]
        meio = len(hist) // 2
        tendencia = (round(sum(hist[meio:]) / max(1, len(hist) - meio) - sum(hist[:meio]) / max(1, meio), 4)
                     if len(hist) >= 4 else None)
        por_hab = {}
        for k, n in self.cerebro.cont.items():
            h = k.split("|", 1)[1]
            por_hab.setdefault(h, [0, 0.0])
            por_hab[h][0] += n
            por_hab[h][1] += self.cerebro.q.get(k, 0.0) * n
        return {"jogo": self.jogo, "passos": self.passos_total, "estados": n,
                "reflexos_usados": getattr(self, "reflexos_usados", 0),
                "ultima_percepcao": self.ultimo_ctx or None,
                "habilidades": {h: {"usos": v[0], "valor_medio": round(v[1] / max(1, v[0]), 3)}
                                for h, v in sorted(por_hab.items(), key=lambda x: -x[1][0])},
                "politica": pol, "recompensa_por_bloco": hist, "melhorando": tendencia,
                "detectores": self.detectores}


def _seguro(nome):
    s = "".join(c if c.isalnum() or c in "-_" else "_" for c in str(nome or "jogo").lower())
    return s[:40] or "jogo"
