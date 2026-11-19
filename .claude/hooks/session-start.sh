#!/bin/bash
# Início de sessão do Claude Code na nuvem: garante o graphify (grafo do código, ver CLAUDE.md) e o numpy
# (sem ele os testes de áudio — ouvir_bipe, sono, sonar — são pulados). Só instala o que falta: depois da
# primeira vez (e em resume/clear/compact) termina em milissegundos.
set -euo pipefail

# No computador do usuário não mexe em nada
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}"

# Comandos instalados pelo uv (e pelo pip --user) ficam em ~/.local/bin: garante esse diretório no PATH,
# aqui e no resto da sessão
case ":$PATH:" in
  *":$HOME/.local/bin:"*) ;;
  *)
    export PATH="$HOME/.local/bin:$PATH"
    if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
      # shellcheck disable=SC2016  # aspas simples de propósito: expande quando a sessão carregar o arquivo
      echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$CLAUDE_ENV_FILE"
    fi
    ;;
esac

# pip do mesmo python3 que roda os testes; se esse Python for "externally managed", repete com
# --break-system-packages (contêiner descartável)
instalar_pip() {
  python3 -m pip install --quiet --disable-pip-version-check "$@" >&2 \
    || python3 -m pip install --quiet --disable-pip-version-check --break-system-packages "$@" >&2
}

# 1. graphify (pacote PyPI "graphifyy"): ferramenta global, isolada pelo uv quando houver
if ! command -v graphify >/dev/null 2>&1; then
  if command -v uv >/dev/null 2>&1; then
    uv tool install --quiet graphifyy >&2
  else
    instalar_pip graphifyy
  fi
  command -v graphify >/dev/null 2>&1 || { echo "graphify não ficou disponível no PATH" >&2; exit 1; }
fi

# 2. numpy para os testes
if ! python3 -c 'import numpy' >/dev/null 2>&1; then
  instalar_pip numpy
fi
