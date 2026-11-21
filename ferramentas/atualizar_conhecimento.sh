#!/usr/bin/env bash
# Atualiza o grafo de código e o contexto que acompanhará a instalação no Termux.
set -euo pipefail
cd "$(dirname "$0")/.."
graphify update .
cp graphify-out/graph.json controle-ir/conhecimento/graph.json
for habilidade in best-tool god-mode godmode graphify; do
  origem=".claude/skills/$habilidade"
  destino="controle-ir/conhecimento/skills/$habilidade"
  for arquivo in "$origem/SKILL.md" "$origem"/LICENSE* "$origem"/ORIGEM*; do
    if [[ -f "$arquivo" ]]; then cp "$arquivo" "$destino/"; fi
  done
done
