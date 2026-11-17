#!/usr/bin/env python3
"""Gera controle-ir/dados/base.jsonl.gz a partir das fontes com licença clara.

Uso (no computador de desenvolvimento):

    git clone --depth 1 https://github.com/smartHomeHub/SmartIR /tmp/SmartIR
    git clone https://github.com/Lucaslhm/Flipper-IRDB /tmp/Flipper-IRDB   # histórico completo
    python3 ferramentas/construir_catalogo.py --smartir /tmp/SmartIR --flipper /tmp/Flipper-IRDB

Somente entram no pacote:
* SmartIR (licença MIT);
* arquivos da Flipper-IRDB adicionados depois do commit 2319685, quando o
  repositório adotou a CC0 (o README diz que os anteriores não estão cobertos).
O restante da Flipper-IRDB pode ser baixado pelo próprio usuário no celular
(``controle-ir catalogo ampliar``).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "controle-ir"))

from controle_ir import catalogo, formatos  # noqa: E402

COMMIT_CC0 = "2319685f2cbf0cd3f809609622cade14d24fb819"


def arquivos_cc0(repo: Path) -> tuple[list[str], str]:
    def git(*a):
        return subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True, text=True).stdout
    antes = set(x for x in git("ls-tree", "-r", "--name-only", COMMIT_CC0).splitlines() if x.endswith(".ir"))
    agora = [x for x in git("ls-files").splitlines() if x.endswith(".ir")]
    head = git("rev-parse", "HEAD").strip()
    return sorted(x for x in agora if x not in antes), head


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smartir", required=True)
    ap.add_argument("--flipper", required=True)
    ap.add_argument("--saida", default=str(RAIZ / "controle-ir" / "dados" / "base.jsonl.gz"))
    a = ap.parse_args()

    perfis = []
    smart = Path(a.smartir) / "codes"
    sm_ok = sm_falha = 0
    for f in sorted(smart.glob("*/*.json")):
        try:
            dados = json.loads(f.read_text(errors="ignore"))
            perfis.append(formatos.ler_smartir(dados, f.parent.name, f"smartir:{f.parent.name}/{f.stem}"))
            sm_ok += 1
        except Exception as e:  # noqa: BLE001 — relatório de arquivos inválidos
            sm_falha += 1
            print(f"  SmartIR ignorado {f.parent.name}/{f.name}: {e}", file=sys.stderr)
    smartir_head = subprocess.run(["git", "-C", a.smartir, "rev-parse", "HEAD"], capture_output=True,
                                  text=True).stdout.strip()

    cc0, flipper_head = arquivos_cc0(Path(a.flipper))
    fl_ok = fl_falha = 0
    for rel in cc0:
        try:
            m = catalogo.metadados_flipper(rel)
            p = formatos.ler_flipper((Path(a.flipper) / rel).read_text(errors="ignore"), f"flipper:{rel}",
                                     m["nome"], m["categoria"], m["marca"], m["modelo"],
                                     "flipper-irdb-cc0", "CC0-1.0")
            p["nome"] = m["nome"]
            p.pop("descartados", None)
            perfis.append(p)
            fl_ok += 1
        except Exception as e:  # noqa: BLE001
            fl_falha += 1
            print(f"  Flipper ignorado {rel}: {e}", file=sys.stderr)

    catalogo.exportar_jsonl(perfis, a.saida)
    origem = {
        "smartir": {"repositorio": "https://github.com/smartHomeHub/SmartIR", "commit": smartir_head,
                    "licenca": "MIT", "perfis": sm_ok, "ignorados": sm_falha},
        "flipper-irdb-cc0": {"repositorio": "https://github.com/Lucaslhm/Flipper-IRDB", "commit": flipper_head,
                             "licenca": "CC0-1.0", "a_partir_do_commit": COMMIT_CC0, "perfis": fl_ok,
                             "ignorados": fl_falha},
    }
    Path(a.saida).with_name("origem.json").write_text(json.dumps(origem, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(origem, indent=2, ensure_ascii=False))
    print(f"gravado {a.saida} ({Path(a.saida).stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
