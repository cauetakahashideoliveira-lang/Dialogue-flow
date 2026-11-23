#!/usr/bin/env python3
"""Gerador do protocolo TCL112 (ar-condicionado TCL e marcas feitas pela TCL, como o Brastemp Clean).

O que se sabe (22/11/2026, "ar condicionado quarto 2" = Brastemp Clean BBV09BBBNA, controle "Brastemp Clean"):
- O aparelho não aceita os códigos Consul/Whirlpool (protocolo 83 06 ...), apesar da etiqueta Whirlpool.
- Desligou com o código "desligar" do perfil SmartIR TCL TAC-12CHSD (busca, candidato 33) e ligou em frio
  23 °C com o estado do mesmo perfil (catálogo smartir:climate/1900).
- Cada envio leva DOIS quadros de 14 bytes (LSB primeiro): um quadro especial fixo (tipo 2) e o estado (tipo 1).

Estado (tipo 1), conferido byte a byte contra as capturas SmartIR climate/1900 e climate/1901:
  0-2  23 CB 26          cabeçalho
  3    01                tipo do quadro (02 = especial)
  5    0x20 | 0x04       0x04 = ligado (o desligar manda 0x20); 0x40 = visor apagado (IRremoteESP8266, a testar)
  6    modo | 0x40       01 calor, 02 desumidificar, 03 frio, 07 ventilar, 08 automático; 0x40 = turbo (a testar)
  7    31 - temperatura  16 a 31 °C
  8    ventilação | 0x38 ventilação 0 auto, 2 baixa, 3 média, 5 alta; 0x38 = oscilação vertical.
                         No desumidificar o controle fixa a ventilação em baixa (2), como nas capturas.
  12   0x80 | 0x08       0x08 acompanha a oscilação (captura do TAC-12CHSD/XA71IN)
  13   soma dos bytes 0-12 (mod 256)

Uso:
  python3 ferramentas/tcl112.py quadro --modo frio --temperatura 23 --ventilacao alta [--oscilacao]
                                       [--turbo] [--visor-desligado] [--formato json|bytes]
  python3 ferramentas/tcl112.py perfil --saida perfil.json [--nome "..."]

O perfil gerado (formato controle-ir/perfil@1) tem estado completo: modo × temperatura × ventilação ×
oscilação, mais o desligar capturado. Importe no celular com `controle-ir importar perfil.json`.
O arquivo não depende do repositório: no celular, rode-o direto com python3.
"""
from __future__ import annotations

import argparse
import base64
import json
import sys

CABECALHO = (0x23, 0xCB, 0x26)
MODOS = {"calor": 0x01, "desumidificar": 0x02, "frio": 0x03, "ventilar": 0x07, "automatico": 0x08}
VENTILACAO = {"automatica": 0b000, "baixa": 0b010, "media": 0b011, "alta": 0b101}
TEMP_MIN, TEMP_MAX = 16, 31

# Quadro especial (tipo 2) que antecede cada estado nas capturas do TAC-12CHSD/XA21I.
ESPECIAL = (0x23, 0xCB, 0x26, 0x02, 0x00, 0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x65)
# Estado do "desligar" capturado (frio, 24 °C, alta, energia 0) — desligou o Brastemp em 22/11.
DESLIGAR = (0x23, 0xCB, 0x26, 0x01, 0x00, 0x20, 0x03, 0x07, 0x05, 0x00, 0x00, 0x00, 0x80, 0xC4)

# Tempos medidos na captura que funcionou no aparelho (Broadlink, climate/1900), em microssegundos.
CAB_MARCA, CAB_ESPACO = 3300, 1650
MARCA, ESPACO_0, ESPACO_1 = 590, 265, 1115
PAUSA = 76000
FREQUENCIA = 38000


class ErroTcl(ValueError):
    pass


def soma(b) -> int:
    return sum(b[:13]) & 0xFF


def estado(modo: str, temperatura: int, ventilacao: str = "automatica", oscilacao: bool = False,
           turbo: bool = False, visor: bool = True, ligado: bool = True) -> list[int]:
    if modo not in MODOS:
        raise ErroTcl(f"modo aceita {', '.join(MODOS)}")
    if ventilacao not in VENTILACAO:
        raise ErroTcl(f"ventilação aceita {', '.join(VENTILACAO)}")
    t = int(temperatura)
    if not TEMP_MIN <= t <= TEMP_MAX:
        raise ErroTcl(f"temperatura de {TEMP_MIN} a {TEMP_MAX} °C")
    b = [0] * 14
    b[0:3] = CABECALHO
    b[3] = 0x01
    b[5] = 0x20 | (0x04 if ligado else 0) | (0 if visor else 0x40)
    b[6] = MODOS[modo] | (0x40 if turbo else 0)
    b[7] = TEMP_MAX - t
    vent = VENTILACAO["baixa"] if modo == "desumidificar" else VENTILACAO[ventilacao]
    b[8] = vent | (0x38 if oscilacao else 0)
    b[12] = 0x80 | (0x08 if oscilacao else 0)
    b[13] = soma(b)
    return b


def pulsos(*quadros) -> list[int]:
    """Quadros de 14 bytes em durações (marca, espaço, ...), com pausa entre eles."""
    p: list[int] = []
    for i, q in enumerate(quadros):
        if i:
            p += [MARCA, PAUSA]
        p += [CAB_MARCA, CAB_ESPACO]
        for byte in q:
            for k in range(8):
                p += [MARCA, ESPACO_1 if (byte >> k) & 1 else ESPACO_0]
    return p + [MARCA]


def broadlink(p: list[int]) -> str:
    """Mesma codificação de controle_ir.sinais.pulsos_para_broadlink (unidade 269/8192 ms)."""
    corpo = bytearray()
    for v in list(p) + [100000]:
        u = int(round(v * 8192 / 269 / 1000))
        if 0 < u < 256:
            corpo.append(u)
        else:
            corpo += b"\x00" + min(u, 0xFFFF).to_bytes(2, "big")
    return base64.b64encode(bytes([0x26, 0]) + len(corpo).to_bytes(2, "little") + bytes(corpo)).decode()


def sinal(*quadros) -> dict:
    return {"broadlink": broadlink(pulsos(*quadros))}


def perfil(nome: str = "Brastemp Clean BBV09BBBNA (TCL112)") -> dict:
    temps = list(range(TEMP_MIN, TEMP_MAX + 1))
    estados = []
    for modo in MODOS:
        for vent in VENTILACAO:
            for osc in (False, True):
                for t in temps:
                    estados.append({"modo": modo, "temperatura": t, "ventilacao": vent,
                                    "oscilacao": "ligada" if osc else "desligada",
                                    "sinal": sinal(ESPECIAL, estado(modo, t, vent, osc))})
    desligar = sinal(ESPECIAL, DESLIGAR)
    return {
        "formato": "controle-ir/perfil@1",
        "chave": "usuario:tcl112-brastemp-clean",
        "nome": nome,
        "categoria": "ar_condicionado",
        "marca": "Brastemp",
        "modelo": "BBV09BBBNA (protocolo TCL112, controle Brastemp Clean)",
        "fonte": "usuario",
        "licenca": "do usuário",
        "comandos": [{"chave": "energia_desligar", "base": "energia_desligar", "rotulo": "Desligar",
                      "tipo": "definir", "sinal": desligar, "efeitos": {"energia": "desligado"}}],
        "estado_completo": {
            "parametros": {
                "modo": list(MODOS),
                "temperatura": {"min": TEMP_MIN, "max": TEMP_MAX, "passo": 1.0, "valores": temps},
                "ventilacao": list(VENTILACAO),
                "oscilacao": ["desligada", "ligada"],
            },
            "desligar": desligar,
            "estados": estados,
        },
    }


def _hex(b) -> str:
    return " ".join(f"{x:02X}" for x in b)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    q = sub.add_parser("quadro", help="um estado, para testar com enviar_sinal")
    q.add_argument("--modo", default="frio", choices=list(MODOS))
    q.add_argument("--temperatura", type=int, default=23)
    q.add_argument("--ventilacao", default="automatica", choices=list(VENTILACAO))
    q.add_argument("--oscilacao", action="store_true")
    q.add_argument("--turbo", action="store_true")
    q.add_argument("--visor-desligado", action="store_true")
    q.add_argument("--formato", default="json", choices=["json", "bytes"])
    pp = sub.add_parser("perfil", help="perfil completo (controle-ir/perfil@1)")
    pp.add_argument("--saida", required=True)
    pp.add_argument("--nome", default="Brastemp Clean BBV09BBBNA (TCL112)")
    a = ap.parse_args(argv)
    if a.cmd == "quadro":
        b = estado(a.modo, a.temperatura, a.ventilacao, a.oscilacao, a.turbo, not a.visor_desligado)
        if a.formato == "bytes":
            print(_hex(b))
        else:
            print(json.dumps({"bytes": _hex(b), "frequencia": FREQUENCIA, "pulsos": pulsos(ESPECIAL, b)},
                             separators=(",", ":")))
        return 0
    p = perfil(a.nome)
    with open(a.saida, "w") as f:
        json.dump(p, f, ensure_ascii=False, separators=(",", ":"))
    print(json.dumps({"saida": a.saida, "estados": len(p["estado_completo"]["estados"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
