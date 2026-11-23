"""Linguagem de comandos do controle do PS4 (pura, testável sem console).

Um comando é uma lista de passos. Cada passo é um dict:
  {"botao": "x"}                      toque curto (ms padrão 80)
  {"botao": "r2", "ms": 600}          segura por 600 ms e solta
  {"segurar": "l2"} / {"soltar": "l2"}
  {"juntos": ["l1", "r1"], "ms": 100} aperta vários ao mesmo tempo
  {"analogico": "esquerdo", "x": 0, "y": -1, "ms": 500}   inclina e volta ao centro (sem ms: fica inclinado)
  {"analogico": "direito", "angulo": 90, "forca": 0.6, "ms": 300}  0° = direita, 90° = cima
  {"esperar": 250}
  {"repetir": 3, "passos": [...]}
  {"habilidade": "nome"}              roda uma habilidade salva
Texto curto também vale: "x", "x x quadrado", "r2:600", "esperar:300".
"""
import math
import time

BOTOES = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'L1', 'R1', 'L2', 'R2', 'CROSS', 'CIRCLE', 'SQUARE', 'TRIANGLE',
          'OPTIONS', 'SHARE', 'PS', 'L3', 'R3', 'TOUCHPAD']

APELIDOS = {
    "x": "CROSS", "xis": "CROSS", "cross": "CROSS", "x_": "CROSS",
    "o": "CIRCLE", "bola": "CIRCLE", "circulo": "CIRCLE", "círculo": "CIRCLE", "circle": "CIRCLE",
    "quadrado": "SQUARE", "square": "SQUARE", "q": "SQUARE",
    "triangulo": "TRIANGLE", "triângulo": "TRIANGLE", "triangle": "TRIANGLE", "t": "TRIANGLE",
    "cima": "UP", "up": "UP", "baixo": "DOWN", "down": "DOWN",
    "esquerda": "LEFT", "left": "LEFT", "direita": "RIGHT", "right": "RIGHT",
    "opcoes": "OPTIONS", "opções": "OPTIONS", "options": "OPTIONS", "start": "OPTIONS",
    "share": "SHARE", "compartilhar": "SHARE", "create": "SHARE",
    "ps": "PS", "home": "PS", "touchpad": "TOUCHPAD", "touch": "TOUCHPAD",
}
for _b in ("L1", "R1", "L2", "R2", "L3", "R3"):
    APELIDOS[_b.lower()] = _b
LADOS = {"esquerdo": "left", "esq": "left", "left": "left", "l": "left",
         "direito": "right", "dir": "right", "right": "right", "r": "right"}
TOQUE_MS = 80
MAX_PASSOS = 2000
MAX_PROFUNDIDADE = 4


class ErroComando(ValueError):
    pass


def botao(nome):
    n = str(nome).strip()
    if n.upper() in BOTOES:
        return n.upper()
    b = APELIDOS.get(n.lower())
    if not b:
        raise ErroComando(f"botão desconhecido: {nome!r} (use x, bola, quadrado, triangulo, l1..r3, cima, "
                          f"baixo, esquerda, direita, opcoes, share, ps, touchpad)")
    return b


def lado(nome):
    l = LADOS.get(str(nome).strip().lower())
    if not l:
        raise ErroComando(f"analógico desconhecido: {nome!r} (esquerdo ou direito)")
    return l


def _limitar(v):
    return max(-1.0, min(1.0, float(v)))


def ponto(p):
    """x/y diretos (y negativo = cima, como no PS4) ou angulo/forca (90° = cima)."""
    if "angulo" in p:
        a = math.radians(float(p["angulo"]))
        f = max(0.0, min(1.0, float(p.get("forca", 1.0))))
        return round(math.cos(a) * f, 4), round(-math.sin(a) * f, 4)
    return _limitar(p.get("x", 0)), _limitar(p.get("y", 0))


def texto_para_passos(txt):
    """'x x r2:600 esperar:300 cima' → passos."""
    passos = []
    for tok in str(txt).replace(",", " ").split():
        nome, _, arg = tok.partition(":")
        if nome.lower() in ("esperar", "espera", "wait", "pausa"):
            passos.append({"esperar": int(arg or 200)})
        elif "+" in nome:
            passos.append({"juntos": nome.split("+"), "ms": int(arg or TOQUE_MS)})
        else:
            passos.append({"botao": nome, "ms": int(arg or TOQUE_MS)})
    return passos


def normalizar(passos, habilidades=None, _prof=0):
    """Valida e expande (repetir, habilidade, texto) em passos atômicos:
    ("apertar", B) ("soltar", B) ("analogico", lado, x, y) ("esperar", s)."""
    if isinstance(passos, str):
        passos = texto_para_passos(passos)
    if _prof > MAX_PROFUNDIDADE:
        raise ErroComando("habilidades/repetições aninhadas demais")
    out = []
    for p in passos or []:
        if isinstance(p, str):
            out += normalizar(p, habilidades, _prof)
            continue
        if not isinstance(p, dict):
            raise ErroComando(f"passo inválido: {p!r}")
        if "botao" in p:
            b = botao(p["botao"])
            out += [("apertar", b), ("esperar", max(0, int(p.get("ms", TOQUE_MS))) / 1000), ("soltar", b)]
        elif "segurar" in p:
            out.append(("apertar", botao(p["segurar"])))
        elif "soltar" in p:
            out.append(("soltar", botao(p["soltar"])))
        elif "juntos" in p:
            bs = [botao(b) for b in p["juntos"]]
            out += [("apertar", b) for b in bs]
            out.append(("esperar", max(0, int(p.get("ms", TOQUE_MS))) / 1000))
            out += [("soltar", b) for b in bs]
        elif "analogico" in p:
            l = lado(p["analogico"])
            x, y = ponto(p)
            out.append(("analogico", l, x, y))
            if p.get("ms") is not None:
                out += [("esperar", max(0, int(p["ms"])) / 1000), ("analogico", l, 0.0, 0.0)]
        elif "esperar" in p:
            out.append(("esperar", max(0, min(int(p["esperar"]), 60000)) / 1000))
        elif "repetir" in p:
            n = max(1, min(int(p["repetir"]), 500))
            corpo = normalizar(p.get("passos", []), habilidades, _prof + 1)
            for _ in range(n):
                out += corpo
                if len(out) > MAX_PASSOS:
                    break
        elif "habilidade" in p:
            h = (habilidades or {}).get(p["habilidade"])
            if not h:
                raise ErroComando(f"habilidade não encontrada: {p['habilidade']!r}")
            out += normalizar(h["passos"], habilidades, _prof + 1)
        else:
            raise ErroComando(f"passo sem tipo conhecido: {p!r}")
        if len(out) > MAX_PASSOS:
            raise ErroComando(f"comando longo demais (mais de {MAX_PASSOS} passos atômicos)")
    return out


def duracao(atomicos):
    return round(sum(a[1] for a in atomicos if a[0] == "esperar"), 3)


def executar(atomicos, ctrl, dormir=time.sleep, parar=lambda: False):
    """ctrl: objeto com apertar(B), soltar(B), analogico(lado, x, y). Um "segurar" sem "soltar" continua preso
    depois do comando (para soltar num comando seguinte); se der erro ou for interrompido, solta tudo."""
    presos, inclinados, feitos, ok = set(), set(), 0, False
    try:
        for a in atomicos:
            if parar():
                for l in list(inclinados):
                    ctrl.analogico(l, 0.0, 0.0)
                return {"feitos": feitos, "interrompido": True}
            if a[0] == "apertar":
                ctrl.apertar(a[1])
                presos.add(a[1])
            elif a[0] == "soltar":
                ctrl.soltar(a[1])
                presos.discard(a[1])
            elif a[0] == "analogico":
                ctrl.analogico(a[1], a[2], a[3])
                (inclinados.add if (a[2] or a[3]) else inclinados.discard)(a[1])
            elif a[0] == "esperar":
                dormir(a[1])
            feitos += 1
        ok = True
    finally:
        if not ok:
            for b in list(presos):
                ctrl.soltar(b)
            presos.clear()
    return {"feitos": feitos, "segurando": sorted(presos), "analogicos_inclinados": sorted(inclinados)}
