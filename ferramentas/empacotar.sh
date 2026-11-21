#!/usr/bin/env bash
# Gera o pacote do celular. Com --verificar, confere o pacote existente.
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$RAIZ/ferramentas/pacote.py" "$@"
