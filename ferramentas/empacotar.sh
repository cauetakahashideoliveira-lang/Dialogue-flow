#!/usr/bin/env bash
# Gera dist/controle-ir.zip com a pasta controle-ir/ (o que vai para o celular).
set -euo pipefail
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$RAIZ/dist"
rm -f "$RAIZ/dist/controle-ir.zip"
cd "$RAIZ"
find controle-ir -name '__pycache__' -type d -prune -exec rm -rf {} +
zip -q -r -X "$RAIZ/dist/controle-ir.zip" controle-ir -x '*/__pycache__/*' '*.pyc'
( cd "$RAIZ/dist" && sha256sum controle-ir.zip > controle-ir.zip.sha256 )
ls -la "$RAIZ/dist"
