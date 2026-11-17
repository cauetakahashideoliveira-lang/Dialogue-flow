"""Representação única de um sinal infravermelho.

Um sinal pode estar guardado de quatro formas compactas e sempre pode ser
convertido em (frequência, durações) para o emissor:

* ``{"protocolo": "NEC", "endereco": 4, "comando": 8}`` — gerado na hora;
* ``{"frequencia": 38000, "pulsos": [9000, 4500, ...]}`` — bruto;
* ``{"broadlink": "JgB..."}`` — formato base64 do Broadlink/SmartIR;
* ``{"pronto": "0000 006D ..."}`` — Pronto hex.

A *impressão* identifica transmissões equivalentes para eliminar duplicatas
sem perder a associação do sinal a vários perfis.
"""
from __future__ import annotations

import base64
import hashlib
import json

from . import protocolos

LIMITE_DURACAO_US = 1_900_000  # Android recusa padrões acima de ~2 s
FREQ_MIN, FREQ_MAX = 20000, 60000
MAX_PULSO_US = 250_000


class ErroSinal(ValueError):
    pass


def normalizar_pulsos(valores) -> list[int]:
    """Aceita listas com sinal (+pulso/-pausa) ou alternadas e devolve
    durações positivas alternadas, começando e terminando em pulso."""
    vals = [int(round(float(v))) for v in valores]
    if not vals:
        raise ErroSinal("sinal sem durações")
    out: list[int] = []
    if any(v < 0 for v in vals):
        nivel_atual = None
        for v in vals:
            if v == 0:
                continue
            nivel = v > 0
            if out and nivel == nivel_atual:
                out[-1] += abs(v)
            else:
                if not out and not nivel:
                    continue  # pausa inicial
                out.append(abs(v))
                nivel_atual = nivel
    else:
        for i, v in enumerate(vals):
            if v <= 0:
                raise ErroSinal("duração inválida no sinal bruto")
            out.append(v)
    # capturas com estouro de contador (ex.: 1073741453 µs): descarta no início, limita no meio
    while len(out) >= 2 and out[0] > MAX_PULSO_US:
        out = out[2:]
    out = [v if v <= MAX_PULSO_US else (MAX_PULSO_US if i % 2 == 0 else 100000) for i, v in enumerate(out)]
    if len(out) % 2 == 0:
        out.pop()  # descarta a pausa final
    if not out:
        raise ErroSinal("sinal sem pulsos")
    return out


def limitar_duracao(pulsos: list[int]) -> list[int]:
    """Corta repetições finais para respeitar o limite do Android."""
    total = 0
    for i, v in enumerate(pulsos):
        total += v
        if total > LIMITE_DURACAO_US:
            corte = pulsos[:i]
            if len(corte) % 2 == 0:
                corte = corte[:-1]
            return corte
    return pulsos


# ------------------------------------------------------------------ Broadlink
# unidade Broadlink: 269/8192 ms ≈ 32,84 µs


def broadlink_para_pulsos(b64: str) -> tuple[int, list[int]]:
    dados = base64.b64decode(b64.strip() + "=" * (-len(b64.strip()) % 4))
    if len(dados) < 6 or dados[0] not in (0x26, 0xB1, 0xB2, 0xD7):
        raise ErroSinal("código Broadlink inválido")
    if dados[0] != 0x26:
        raise ErroSinal("código Broadlink de RF (não infravermelho)")
    repeticoes = dados[1]
    tamanho = int.from_bytes(dados[2:4], "little")
    corpo = dados[4:4 + tamanho]
    vals: list[int] = []
    i = 0
    while i < len(corpo):
        v = corpo[i]
        i += 1
        if v == 0:
            if i + 2 > len(corpo):
                break
            v = int.from_bytes(corpo[i:i + 2], "big")
            i += 2
        vals.append(int(round(v * 269 / 8192 * 1000)))
    # o último valor (0x0d05 ≈ 109 ms) é a pausa final e é descartado
    pulsos = normalizar_pulsos(vals)
    if repeticoes:
        base = pulsos[:]
        for _ in range(min(repeticoes, 3)):
            pulsos = pulsos + [100000] + base
    return 38000, pulsos


def pulsos_para_broadlink(pulsos: list[int]) -> str:
    corpo = bytearray()
    for v in list(pulsos) + [100000]:
        u = int(round(v * 8192 / 269 / 1000))
        if u < 256 and u > 0:
            corpo.append(u)
        else:
            corpo += b"\x00" + min(u, 0xFFFF).to_bytes(2, "big")
    cab = bytes([0x26, 0]) + len(corpo).to_bytes(2, "little")
    return base64.b64encode(cab + bytes(corpo)).decode()


# ---------------------------------------------------------------------- Pronto

def pronto_para_pulsos(texto: str) -> tuple[int, list[int]]:
    palavras = [int(x, 16) for x in texto.split()]
    if len(palavras) < 6 or palavras[0] not in (0, 0x100):
        raise ErroSinal("Pronto: apenas o formato 0000 (bruto modulado) é suportado")
    unidade = palavras[1] * 0.241246  # µs por ciclo da portadora
    if unidade <= 0:
        raise ErroSinal("Pronto: frequência inválida")
    freq = int(round(1e6 / unidade))
    n1, n2 = palavras[2], palavras[3]
    corpo = palavras[4:]
    if len(corpo) < 2 * (n1 + n2):
        raise ErroSinal("Pronto: tamanho declarado não confere")
    uma = corpo[:2 * n1]
    rep = corpo[2 * n1:2 * (n1 + n2)]
    seq = uma + rep if uma else rep + rep
    return freq, normalizar_pulsos([max(1, round(c * unidade)) for c in seq])


def pulsos_para_pronto(freq: int, pulsos: list[int]) -> str:
    codigo = int(round(1e6 / (freq * 0.241246)))
    unidade = codigo * 0.241246
    vals = [max(1, round(v / unidade)) for v in pulsos] + [max(1, round(40000 / unidade))]
    if len(vals) % 2:
        vals.append(1)
    pares = len(vals) // 2
    palavras = [0, codigo, pares, 0] + vals
    return " ".join(f"{p:04X}" for p in palavras)


# ------------------------------------------------------------------- impressão

def _classes(pulsos: list[int]) -> list[int]:
    """Agrupa durações próximas (±22%) e devolve representantes arredondados."""
    unicos = sorted(set(pulsos))
    grupos: list[list[int]] = []
    for v in unicos:
        if grupos and v <= grupos[-1][0] * 1.22:
            grupos[-1].append(v)
        else:
            grupos.append([v])
    rep = {}
    for g in grupos:
        m = g[len(g) // 2]
        passo = 50 if m < 1000 else (250 if m < 10000 else 2500)
        r = int(round(m / passo) * passo)
        for v in g:
            rep[v] = r
    return [rep[v] for v in pulsos]


def _quadros(pulsos: list[int], separacao: int = 15000) -> list[list[int]]:
    quadros, atual = [], []
    for i, v in enumerate(pulsos):
        if i % 2 == 1 and v >= separacao:
            quadros.append(atual)
            atual = []
        else:
            atual.append(v)
    if atual:
        quadros.append(atual)
    return [q for q in quadros if q]


def impressao_bruta(freq: int, pulsos: list[int]) -> str:
    q = _quadros(_classes(pulsos))
    unicos = []
    for quadro in q:  # quadros repetidos contam uma vez
        if not unicos or unicos[-1] != quadro:
            unicos.append(quadro)
    texto = f"{round(freq / 1000)}|" + ";".join(",".join(map(str, x)) for x in unicos)
    return "raw:" + hashlib.sha1(texto.encode()).hexdigest()[:20]


def impressao_protocolo(protocolo: str, endereco: int, comando: int) -> str:
    p = protocolos.nome_canonico(protocolo)
    a, c = int(endereco), int(comando)
    if p == "RC5X":
        c &= 0x3F
    if p == "NEC":  # NEC é um caso particular de NECext
        p, a, c = "NECext", (a & 0xFF) | ((a ^ 0xFF) << 8), (c & 0xFF) | ((c ^ 0xFF) << 8)
    return f"{p}:{a:x}:{c:x}"


# ----------------------------------------------------------------- classe Sinal

class Sinal:
    __slots__ = ("dados", "_cache")

    def __init__(self, dados: dict):
        if isinstance(dados, Sinal):
            dados = dados.dados
        if not isinstance(dados, dict):
            raise ErroSinal("sinal precisa ser um objeto")
        self.dados = self._validar(dict(dados))
        self._cache = None

    @staticmethod
    def _validar(d: dict) -> dict:
        if "protocolo" in d:
            p = protocolos.nome_canonico(d["protocolo"])
            out = {"protocolo": p, "endereco": int(d.get("endereco", 0)), "comando": int(d.get("comando", 0))}
            if d.get("repeticoes"):
                out["repeticoes"] = int(d["repeticoes"])
            return out
        if "broadlink" in d:
            return {"broadlink": str(d["broadlink"]).strip()}
        if "pronto" in d:
            return {"pronto": " ".join(str(d["pronto"]).split())}
        if "pulsos" in d:
            freq = int(d.get("frequencia") or protocolos.FREQ_PADRAO)
            if not FREQ_MIN <= freq <= FREQ_MAX:
                raise ErroSinal(f"frequência fora da faixa suportada: {freq} Hz")
            return {"frequencia": freq, "pulsos": normalizar_pulsos(d["pulsos"])}
        raise ErroSinal("sinal sem protocolo, pulsos, broadlink ou pronto")

    def transmissao(self) -> tuple[int, list[int]]:
        """(frequência, durações) prontos para o emissor."""
        d = self.dados
        if "protocolo" in d:
            f, p = protocolos.codificar(d["protocolo"], d["endereco"], d["comando"], d.get("repeticoes"))
        elif self._cache:
            f, p = self._cache
        else:
            if "broadlink" in d:
                f, p = broadlink_para_pulsos(d["broadlink"])
            elif "pronto" in d:
                f, p = pronto_para_pulsos(d["pronto"])
            else:
                f, p = d["frequencia"], d["pulsos"]
            self._cache = (f, p)
        p = limitar_duracao(p)
        if not p:
            raise ErroSinal("sinal mais longo que o limite do Android (2 s)")
        return f, p

    def impressao(self) -> str:
        d = self.dados
        if "protocolo" in d:
            return impressao_protocolo(d["protocolo"], d["endereco"], d["comando"])
        f, p = self.transmissao()
        dec = protocolos.decodificar(p, f)
        if dec:
            return impressao_protocolo(*dec)
        return impressao_bruta(f, p)

    def descricao(self) -> str:
        d = self.dados
        if "protocolo" in d:
            return f"{d['protocolo']} endereço 0x{d['endereco']:X} comando 0x{d['comando']:X}"
        f, p = self.transmissao()
        dec = protocolos.decodificar(p, f)
        if dec:
            return f"{dec[0]} endereço 0x{dec[1]:X} comando 0x{dec[2]:X} (de captura)"
        return f"bruto {f / 1000:.1f} kHz, {len(p)} durações"

    def compacto(self) -> dict:
        """Forma mais compacta e equivalente (converte capturas reconhecíveis)."""
        d = self.dados
        if "pulsos" in d:
            dec = protocolos.decodificar(d["pulsos"], d["frequencia"])
            if dec:
                return {"protocolo": dec[0], "endereco": dec[1], "comando": dec[2]}
        return dict(d)

    def para_json(self) -> str:
        return json.dumps(self.dados, separators=(",", ":"))

    def __eq__(self, outro):
        return isinstance(outro, Sinal) and self.impressao() == outro.impressao()

    def __hash__(self):
        return hash(self.impressao())

    def __repr__(self):
        return f"Sinal({self.descricao()})"
