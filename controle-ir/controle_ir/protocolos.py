"""Codificadores e decodificadores de protocolos infravermelhos documentados.

Os campos ``endereco`` e ``comando`` seguem a mesma convenção dos arquivos
``.ir`` do Flipper Zero (campos ``address``/``command`` lidos em little-endian),
para que os perfis importados da Flipper-IRDB gerem exatamente os bits
esperados. As temporizações seguem as especificações públicas de cada
protocolo (NEC, Samsung, Philips RC5/RC6, Sony SIRC, Kaseikyo, RCA, Pioneer).

Todas as durações estão em microssegundos; a lista começa com um pulso
(portadora ligada) e alterna pulso/pausa.
"""
from __future__ import annotations

from dataclasses import dataclass

FREQ_PADRAO = 38000


class ErroProtocolo(ValueError):
    pass


@dataclass(frozen=True)
class EspecPDWM:
    """Protocolo de distância/largura de pulso (NEC, Samsung, SIRC...)."""
    nome: str
    freq: int
    pre_pulso: int
    pre_pausa: int
    bit1_pulso: int
    bit1_pausa: int
    bit0_pulso: int
    bit0_pausa: int

    @property
    def por_largura(self) -> bool:  # bit codificado na largura do pulso
        return self.bit1_pausa == self.bit0_pausa


NEC = EspecPDWM("NEC", 38000, 9000, 4500, 560, 1690, 560, 560)
SAMSUNG = EspecPDWM("Samsung32", 38000, 4500, 4500, 550, 1650, 550, 550)
SIRC = EspecPDWM("SIRC", 40000, 2400, 600, 1200, 600, 600, 600)
KASEIKYO = EspecPDWM("Kaseikyo", 38000, 3456, 1728, 432, 1296, 432, 432)
RCA = EspecPDWM("RCA", 38000, 4000, 4000, 500, 2000, 500, 1000)
PIONEER = EspecPDWM("Pioneer", 40000, 8500, 4225, 500, 1500, 500, 500)

RC5_MEIO_BIT = 889
RC6_MEIO_BIT = 444

PROTOCOLOS = (
    "NEC", "NECext", "NEC42", "NEC42ext", "Samsung32", "RC5", "RC5X", "RC6",
    "SIRC", "SIRC15", "SIRC20", "Kaseikyo", "RCA", "Pioneer",
)
_NOMES = {p.lower(): p for p in PROTOCOLOS}

# Tamanho em bits dos campos (como no Flipper) — usado para validar entradas
TAMANHOS = {
    "NEC": (8, 8), "NECext": (16, 16), "NEC42": (13, 8), "NEC42ext": (26, 16),
    "Samsung32": (8, 8), "RC5": (5, 6), "RC5X": (5, 7), "RC6": (8, 8),
    "SIRC": (5, 7), "SIRC15": (8, 7), "SIRC20": (13, 7), "Kaseikyo": (26, 10),
    "RCA": (4, 8), "Pioneer": (8, 8),
}


def nome_canonico(protocolo: str) -> str:
    p = _NOMES.get(str(protocolo).strip().lower())
    if not p:
        raise ErroProtocolo(f"protocolo desconhecido: {protocolo}")
    return p


def _bits_lsb(valor: int, n: int) -> list[int]:
    return [(valor >> i) & 1 for i in range(n)]


def _bits_bytes_lsb(dados: bytes, n: int) -> list[int]:
    bits: list[int] = []
    for b in dados:
        bits.extend(_bits_lsb(b, 8))
    return bits[:n]


def _quadro_pdwm(e: EspecPDWM, bits: list[int]) -> list[int]:
    d = [e.pre_pulso, e.pre_pausa]
    if e.por_largura:
        for b in bits:
            d += [e.bit1_pulso if b else e.bit0_pulso, e.bit1_pausa]
        d.pop()  # sem pausa após o último bit
    else:
        for b in bits:
            d += [e.bit1_pulso, e.bit1_pausa if b else e.bit0_pausa]
        d.append(e.bit1_pulso)  # bit de parada
    return d


def _juntar_niveis(niveis: list[int], meio: int) -> list[int]:
    """Converte meios-bits (1=portadora) em durações alternadas."""
    while niveis and niveis[0] == 0:
        niveis = niveis[1:]
    while niveis and niveis[-1] == 0:
        niveis = niveis[:-1]
    d: list[int] = []
    atual, cont = None, 0
    for n in niveis:
        if n == atual:
            cont += 1
        else:
            if atual is not None:
                d.append(cont * meio)
            atual, cont = n, 1
    if atual is not None:
        d.append(cont * meio)
    return d


def _repetir(quadro: list[int], periodo: int, vezes: int) -> list[int]:
    if vezes <= 1:
        return list(quadro)
    total = sum(quadro)
    pausa = max(periodo - total, 4000)
    out: list[int] = []
    for i in range(vezes):
        out += quadro
        if i < vezes - 1:
            out.append(pausa)
    return out


_toggle = {"RC5": 0, "RC6": 0}


def codificar(protocolo: str, endereco: int, comando: int, repeticoes: int | None = None,
              alternancia: int | None = None) -> tuple[int, list[int]]:
    """Gera (frequência, durações) para um comando de protocolo conhecido."""
    p = nome_canonico(protocolo)
    a, c = int(endereco), int(comando)
    if p in ("NEC", "NECext"):
        if p == "NEC":
            a &= 0xFF
            c &= 0xFF
            dados = bytes([a, a ^ 0xFF, c, c ^ 0xFF])
        else:
            dados = (a & 0xFFFF).to_bytes(2, "little") + (c & 0xFFFF).to_bytes(2, "little")
        quadro = _quadro_pdwm(NEC, _bits_bytes_lsb(dados, 32))
        if repeticoes and repeticoes > 1:
            # código de repetição NEC (9000/2250/560) com período de 110 ms
            rep = [9000, 2250, 560]
            out = list(quadro)
            for _ in range(repeticoes - 1):
                out += [max(110000 - sum(quadro), 4000)] + rep
            return NEC.freq, out
        return NEC.freq, quadro
    if p in ("NEC42", "NEC42ext"):
        if p == "NEC42":
            a &= 0x1FFF
            c &= 0xFF
            valor = a | ((~a & 0x1FFF) << 13) | (c << 26) | ((~c & 0xFF) << 34)
        else:
            valor = (a & 0x3FFFFFF) | ((c & 0xFFFF) << 26)
        return NEC.freq, _quadro_pdwm(NEC, _bits_lsb(valor, 42))
    if p == "Samsung32":
        a &= 0xFF
        c &= 0xFF
        quadro = _quadro_pdwm(SAMSUNG, _bits_bytes_lsb(bytes([a, a, c, c ^ 0xFF]), 32))
        return SAMSUNG.freq, quadro
    if p in ("SIRC", "SIRC15", "SIRC20"):
        n, mask = {"SIRC": (12, 0x1F), "SIRC15": (15, 0xFF), "SIRC20": (20, 0x1FFF)}[p]
        valor = (c & 0x7F) | ((a & mask) << 7)
        quadro = _quadro_pdwm(SIRC, _bits_lsb(valor, n))
        return SIRC.freq, _repetir(quadro, 45000, repeticoes or 3)
    if p == "Kaseikyo":
        ident = (a >> 24) & 3
        fabricante = (a >> 8) & 0xFFFF
        g1, g2 = (a >> 4) & 0xF, a & 0xF
        d0, d1 = fabricante & 0xFF, fabricante >> 8
        par = d0 ^ d1
        par = (par & 0xF) ^ (par >> 4)
        d2 = (par & 0xF) | (g1 << 4)
        d3 = (g2 & 0xF) | ((c & 0xF) << 4)
        d4 = ((ident << 6) | ((c >> 4) & 0x3F)) & 0xFF
        d5 = d2 ^ d3 ^ d4
        quadro = _quadro_pdwm(KASEIKYO, _bits_bytes_lsb(bytes([d0, d1, d2, d3, d4, d5]), 48))
        return KASEIKYO.freq, _repetir(quadro, 130000, repeticoes or 1)
    if p == "RCA":
        a &= 0xF
        c &= 0xFF
        valor = a | (c << 4) | ((~a & 0xF) << 12) | ((~c & 0xFF) << 16)
        return RCA.freq, _quadro_pdwm(RCA, _bits_lsb(valor, 24))
    if p == "Pioneer":
        a &= 0xFF
        c &= 0xFF
        dados = bytes([a, a ^ 0xFF, c, c ^ 0xFF, 0])
        quadro = _quadro_pdwm(PIONEER, _bits_bytes_lsb(dados, 33))
        vezes = repeticoes or 2
        out: list[int] = []
        for i in range(vezes):
            out += quadro
            if i < vezes - 1:
                out.append(26000)
        return PIONEER.freq, out
    if p in ("RC5", "RC5X"):
        t = _toggle["RC5"] if alternancia is None else alternancia & 1
        if alternancia is None:
            _toggle["RC5"] ^= 1
        s2 = 1 if p == "RC5" else 0  # RC5X: segundo bit de início = comando bit 6 invertido
        bits = [1, s2, t] + [(a >> i) & 1 for i in range(4, -1, -1)] + [(c >> i) & 1 for i in range(5, -1, -1)]
        niveis: list[int] = []
        for b in bits:  # Manchester: 1 = pausa→pulso, 0 = pulso→pausa
            niveis += [0, 1] if b else [1, 0]
        quadro = _juntar_niveis(niveis, RC5_MEIO_BIT)
        return 36000, _repetir(quadro, 113792, repeticoes or 1)
    if p == "RC6":
        t = _toggle["RC6"] if alternancia is None else alternancia & 1
        if alternancia is None:
            _toggle["RC6"] ^= 1
        niveis = [1] * 6 + [0] * 2  # líder 2666/889 ≈ 6T/2T
        bits = [(1, 1), (0, 1), (0, 1), (0, 1), (t, 2)]
        bits += [((a >> i) & 1, 1) for i in range(7, -1, -1)]
        bits += [((c >> i) & 1, 1) for i in range(7, -1, -1)]
        for b, larg in bits:  # RC6: 1 = pulso→pausa
            niveis += ([1] * larg + [0] * larg) if b else ([0] * larg + [1] * larg)
        quadro = _juntar_niveis(niveis, RC6_MEIO_BIT)
        return 36000, _repetir(quadro, 107000, repeticoes or 1)
    raise ErroProtocolo(p)  # pragma: no cover


# ---------------------------------------------------------------- decodificação

def _perto(v: int, alvo: int, tol: float = 0.3, minimo: int = 150) -> bool:
    return abs(v - alvo) <= max(alvo * tol, minimo)


def _ler_pdwm(e: EspecPDWM, d: list[int], n_max: int) -> list[int] | None:
    if len(d) < 4 or not (_perto(d[0], e.pre_pulso, 0.12, 200) and _perto(d[1], e.pre_pausa, 0.15, 200)):
        return None
    bits: list[int] = []
    i = 2
    if e.por_largura:
        while i < len(d) and len(bits) <= n_max:
            m = d[i]
            if _perto(m, e.bit1_pulso, 0.3):
                bits.append(1)
            elif _perto(m, e.bit0_pulso, 0.35):
                bits.append(0)
            else:
                break
            i += 1
            if i < len(d) and _perto(d[i], e.bit1_pausa, 0.4):
                i += 1
            else:
                break
        if i < len(d):
            return None
    else:
        meio = (e.bit0_pausa + e.bit1_pausa) / 2
        while i + 1 < len(d) and len(bits) <= n_max:
            if not _perto(d[i], e.bit1_pulso, 0.4):
                break
            s = d[i + 1]
            if s > e.bit1_pausa * 1.6:
                break
            bits.append(1 if s > meio else 0)
            i += 2
        # o quadro precisa terminar no bit de parada
        if i != len(d) - 1 or not _perto(d[i], e.bit1_pulso, 0.4):
            return None
    return bits


def _int_lsb(bits: list[int]) -> int:
    return sum(b << i for i, b in enumerate(bits))


def _primeiro_quadro(d: list[int], separacao: int = 8000) -> list[int]:
    for i in range(1, len(d), 2):
        if d[i] >= separacao:
            return d[:i]
    return d


def _manchester(d: list[int], meio: int) -> list[int] | None:
    niveis: list[int] = []
    for i, v in enumerate(d):
        n = round(v / meio)
        if n not in (1, 2, 3) or not _perto(v, n * meio, 0.35, 120):
            return None
        niveis += [1 if i % 2 == 0 else 0] * n
    return niveis


def decodificar(pulsos: list[int], frequencia: int | None = None) -> tuple[str, int, int] | None:
    """Tenta reconhecer o primeiro quadro como um protocolo conhecido.

    Retorna (protocolo, endereco, comando) na convenção do Flipper ou None.
    """
    if not pulsos:
        return None
    q = _primeiro_quadro(list(pulsos))
    # NEC / NEC42
    bits = _ler_pdwm(NEC, q, 42)
    if bits and len(bits) in (32, 42):
        if len(bits) == 32:
            b = [_int_lsb(bits[i:i + 8]) for i in range(0, 32, 8)]
            if b[0] ^ b[1] == 0xFF and b[2] ^ b[3] == 0xFF:
                return "NEC", b[0], b[2]
            return "NECext", b[0] | (b[1] << 8), b[2] | (b[3] << 8)
        v = _int_lsb(bits)
        a, ai = v & 0x1FFF, (v >> 13) & 0x1FFF
        c, ci = (v >> 26) & 0xFF, (v >> 34) & 0xFF
        if a ^ ai == 0x1FFF and c ^ ci == 0xFF:
            return "NEC42", a, c
        return "NEC42ext", v & 0x3FFFFFF, (v >> 26) & 0xFFFF
    bits = _ler_pdwm(SAMSUNG, q, 32)
    if bits and len(bits) == 32:
        b = [_int_lsb(bits[i:i + 8]) for i in range(0, 32, 8)]
        if b[0] == b[1] and b[2] ^ b[3] == 0xFF:
            return "Samsung32", b[0], b[2]
    bits = _ler_pdwm(PIONEER, q, 33)
    if bits and len(bits) == 33:
        b = [_int_lsb(bits[i:i + 8]) for i in range(0, 32, 8)]
        if b[0] ^ b[1] == 0xFF and b[2] ^ b[3] == 0xFF:
            return "Pioneer", b[0], b[2]
    bits = _ler_pdwm(KASEIKYO, q, 48)
    if bits and len(bits) == 48:
        d = [_int_lsb(bits[i:i + 8]) for i in range(0, 48, 8)]
        if d[5] == d[2] ^ d[3] ^ d[4]:
            fabricante = d[0] | (d[1] << 8)
            g1, g2 = d[2] >> 4, d[3] & 0xF
            cmd = (d[3] >> 4) | ((d[4] & 0x3F) << 4)
            ident = d[4] >> 6
            return "Kaseikyo", (ident << 24) | (fabricante << 8) | (g1 << 4) | g2, cmd
    bits = _ler_pdwm(RCA, q, 24)
    if bits and len(bits) == 24:
        v = _int_lsb(bits)
        a, c, ai, ci = v & 0xF, (v >> 4) & 0xFF, (v >> 12) & 0xF, (v >> 16) & 0xFF
        if a ^ ai == 0xF and c ^ ci == 0xFF:
            return "RCA", a, c
    sq = _primeiro_quadro(list(pulsos), 9000)
    bits = _ler_pdwm(SIRC, sq, 20)
    if bits and len(bits) in (12, 15, 20):
        v = _int_lsb(bits)
        nome = {12: "SIRC", 15: "SIRC15", 20: "SIRC20"}[len(bits)]
        return nome, v >> 7, v & 0x7F
    # RC6 (líder 2666/889)
    if len(q) > 4 and _perto(q[0], 2666, 0.15) and _perto(q[1], 889, 0.3):
        niv = _manchester(q[2:], RC6_MEIO_BIT)
        if niv is not None:
            niv = niv + [0] * 4
            pos = 0
            vals = []
            larguras = [1, 1, 1, 1, 2] + [1] * 16
            ok = True
            for larg in larguras:
                if pos + 2 * larg > len(niv):
                    ok = False
                    break
                prim, seg = niv[pos:pos + larg], niv[pos + larg:pos + 2 * larg]
                if all(prim) and not any(seg):
                    vals.append(1)
                elif not any(prim) and all(seg):
                    vals.append(0)
                else:
                    ok = False
                    break
                pos += 2 * larg
            if ok and vals[0] == 1 and vals[1:4] == [0, 0, 0]:
                a = int("".join(map(str, vals[5:13])), 2)
                c = int("".join(map(str, vals[13:21])), 2)
                return "RC6", a, c
    # RC5 (sem líder; começa com meio-bit de pulso)
    if len(q) > 6 and q[0] < 2000:
        niv = _manchester(q, RC5_MEIO_BIT)
        if niv is not None:
            niv = [0] + niv  # primeiro meio-bit (pausa) foi omitido
            if len(niv) % 2:
                niv.append(0)
            if len(niv) >= 28:
                vals = []
                for i in range(0, 28, 2):
                    par = niv[i:i + 2]
                    if par == [0, 1]:
                        vals.append(1)
                    elif par == [1, 0]:
                        vals.append(0)
                    else:
                        vals = []
                        break
                if len(vals) == 14 and vals[0] == 1:
                    a = int("".join(map(str, vals[3:8])), 2)
                    c = int("".join(map(str, vals[8:14])), 2)
                    if vals[1] == 1:
                        return "RC5", a, c
                    return "RC5X", a, c | 0x40
    return None
