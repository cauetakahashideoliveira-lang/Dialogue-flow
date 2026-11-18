#!/usr/bin/env python3
"""Gera variantes de um sinal Gree (oscilação, visor) a partir de uma captura real do catálogo.

Por que existe: o perfil SmartIR do Gree GWH09KF ("ar do quarto") só traz modo, temperatura e
ventilação, sem oscilação nem visor. O Gree manda o ESTADO COMPLETO em cada quadro, então um botão
novo é o mesmo quadro de uma combinação conhecida com alguns bits trocados.

Como funciona (validado no aparelho real em 17/11/2026):
- parte do sinal Broadlink da combinação pedida e o converte em durações;
- muda só os espaços dos bits pedidos, mantendo os tempos originais do controle
  (cabeçalho ~9600/4850 µs, pausa ~21500 µs entre as metades; os tempos genéricos do ESPHome,
  9000/4000 e 19000 µs, NÃO funcionaram neste aparelho);
- recalcula o checksum (nibble alto do byte 7).

Mapa de bits (bytes em ordem LSB primeiro, 4 bytes + rodapé 010 + pausa + 4 bytes):
  byte 0: modo (bits 0-2), ligado (0x08), ventilação (0x30), swing automático (0x40)
  byte 1: temperatura - 16 (nibble baixo)
  byte 2: turbo (0x10), luz/visor (0x20)
  byte 3: fixo 0x50
  byte 4: posição vertical da aleta (nibble baixo; 0x01 = oscilar)
  byte 7: checksum = (10 + nibbles baixos dos bytes 0-3 + nibbles altos dos bytes 4-6) & 0xF, no nibble alto

Uso:
  python3 ferramentas/gree_variante.py --modo frio --ventilacao automatica --temperatura 16 --oscilar
  python3 ferramentas/gree_variante.py --modo frio --ventilacao automatica --temperatura 16 --visor-desligado
  python3 ferramentas/gree_variante.py --modo frio --ventilacao automatica --temperatura 16 --turbo
  ... --formato json|flipper   (padrão json: {"frequencia", "pulsos"}, aceito por enviar_sinal e editar_aparelho)

Limite: só combinações de quadro único (139 durações). Algumas combinações do perfil têm dois quadros
(o segundo com byte 3 = 0x70); a troca de bits nelas ainda não foi testada no aparelho, por isso a
ferramenta recusa essas combinações em vez de adivinhar.
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "controle-ir"))

from controle_ir import sinais  # noqa: E402

CATALOGO = RAIZ / "controle-ir" / "dados" / "base.jsonl.gz"
PERFIL_PADRAO = "smartir:climate/1184"  # Gree GWH09KF, GC-EAF09HR
QUADRO_UNICO = 139  # 2 cabeçalho + 35 bits + marca e pausa + 32 bits + marca final

BIT_SWING_AUTO = (0, 6)   # byte 0, 0x40
BIT_ALETA_OSCILAR = (4, 0)  # byte 4, nibble baixo = 0x01
BIT_VISOR = (2, 5)        # byte 2, 0x20
BIT_TURBO = (2, 4)        # byte 2, 0x10


class ErroGree(ValueError):
    pass


def perfil(chave: str = PERFIL_PADRAO, catalogo: Path = CATALOGO) -> dict:
    with gzip.open(catalogo, "rt", encoding="utf-8") as f:
        for linha in f:
            d = json.loads(linha)
            if d["chave"] == chave:
                return d
    raise ErroGree(f"perfil {chave} não está em {catalogo}")


def _indice_espaco(byte: int, bit: int) -> int:
    if byte < 4:
        return 2 + 2 * (byte * 8 + bit) + 1
    return 2 + 2 * 35 + 2 + 2 * ((byte - 4) * 8 + bit) + 1


def ler_bytes(pulsos: list[int]) -> list[int]:
    """Decodifica os 8 bytes de um quadro único Gree."""
    if len(pulsos) != QUADRO_UNICO:
        raise ErroGree(f"esperado quadro único com {QUADRO_UNICO} durações, veio {len(pulsos)}")
    limiar = 1100
    out = []
    for byte in range(8):
        v = 0
        for bit in range(8):
            if pulsos[_indice_espaco(byte, bit)] > limiar:
                v |= 1 << bit
        out.append(v)
    return out


def checksum(estado: list[int]) -> int:
    s = 10 + sum(b & 0xF for b in estado[:4]) + sum(b >> 4 for b in estado[4:7])
    return s & 0xF


def variante(pulsos: list[int], bits: dict[tuple[int, int], int]) -> list[int]:
    """Troca os bits pedidos ((byte, bit) -> 0/1) e recalcula o checksum, preservando os tempos."""
    estado = ler_bytes(pulsos)  # valida o formato
    espacos = [pulsos[_indice_espaco(b, i)] for b in range(4) for i in range(8)]
    um = round(sum(s for s in espacos if s > 1100) / max(1, sum(1 for s in espacos if s > 1100)))
    zero = round(sum(s for s in espacos if s <= 1100) / max(1, sum(1 for s in espacos if s <= 1100)))
    q = list(pulsos)

    def gravar(byte, bit, v):
        atual = q[_indice_espaco(byte, bit)] > 1100
        if atual != bool(v):  # só mexe no que muda: o resto fica com o tempo original
            q[_indice_espaco(byte, bit)] = um if v else zero

    for (byte, bit), v in bits.items():
        gravar(byte, bit, v)
    estado = ler_bytes(q)
    cs = checksum(estado)
    for k in range(4):
        gravar(7, 4 + k, (cs >> k) & 1)
    return q


def gerar(modo: str, ventilacao: str, temperatura: int, oscilar=False, visor_desligado=False, turbo=False,
          chave: str = PERFIL_PADRAO) -> dict:
    p = perfil(chave)
    e = next((e for e in p["estado_completo"]["estados"]
              if e["modo"] == modo and e["ventilacao"] == ventilacao and int(e["temperatura"]) == temperatura), None)
    if not e:
        raise ErroGree(f"combinação {modo}/{ventilacao}/{temperatura} não existe no perfil {p['nome']}")
    freq, pulsos = sinais.broadlink_para_pulsos(e["sinal"]["broadlink"])
    bits = {}
    if oscilar:
        bits[BIT_SWING_AUTO] = 1
        bits[BIT_ALETA_OSCILAR] = 1
    if visor_desligado:
        bits[BIT_VISOR] = 0
    if turbo:
        bits[BIT_TURBO] = 1
    novo = variante(list(pulsos), bits)
    return {"frequencia": freq, "pulsos": novo, "bytes": " ".join(f"{b:02X}" for b in ler_bytes(novo)),
            "original": " ".join(f"{b:02X}" for b in ler_bytes(list(pulsos)))}


def flipper(nome: str, sinal: dict) -> str:
    return ("Filetype: IR signals file\nVersion: 1\n#\n"
            f"name: {nome}\ntype: raw\nfrequency: {sinal['frequencia']}\nduty_cycle: 0.330000\n"
            f"data: {' '.join(str(x) for x in sinal['pulsos'])}\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--modo", required=True, choices=["frio", "calor", "desumidificar", "ventilar", "automatico"])
    ap.add_argument("--ventilacao", required=True, choices=["baixa", "media", "alta", "automatica"])
    ap.add_argument("--temperatura", required=True, type=int)
    ap.add_argument("--oscilar", action="store_true")
    ap.add_argument("--visor-desligado", action="store_true")
    ap.add_argument("--turbo", action="store_true")
    ap.add_argument("--perfil", default=PERFIL_PADRAO)
    ap.add_argument("--formato", choices=["json", "flipper"], default="json")
    a = ap.parse_args(argv)
    try:
        r = gerar(a.modo, a.ventilacao, a.temperatura, a.oscilar, a.visor_desligado, a.turbo, a.perfil)
    except ErroGree as e:
        sys.exit(f"erro: {e}")
    print(f"# original {r['original']}  ->  novo {r['bytes']}", file=sys.stderr)
    if a.formato == "flipper":
        extras = [x for x, on in (("oscilar", a.oscilar), ("visor_desligado", a.visor_desligado), ("turbo", a.turbo)) if on]
        print(flipper(f"{a.modo}_{a.ventilacao}_{a.temperatura}_{'_'.join(extras) or 'igual'}", r), end="")
    else:
        print(json.dumps({"frequencia": r["frequencia"], "pulsos": r["pulsos"]}))


if __name__ == "__main__":
    main()
