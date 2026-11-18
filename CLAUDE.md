# Contexto para o Claude Code

- Leia primeiro `graphify-out/GRAPH_REPORT.md` (grafo do código) e `docs/estado-atual.md` (instalação real do usuário).
- **Para operar aparelhos**, use `docs/aparelhos/README.md`: mapa cômodo → aparelho → controle, com uma ficha por
  aparelho (nome exato no conector, perfil, comandos testados, sinais extras `.ir`, ressalvas). Ao cadastrar ou
  testar um aparelho, atualize a ficha, o índice e `docs/estado-atual.md`.
- Para perguntas de arquitetura use a skill graphify: `graphify query "<pergunta>"`, `graphify explain "<nó>"`,
  `graphify path "A" "B"`. Após mudar código, rode `graphify update .` (sem custo de LLM).
- **Visão e roadmap** (capacidades plugáveis, execução governada, atualização pelo GitHub, mapa de oportunidades,
  limites reais): `docs/modo-deus.md`. Capacidade nova reutilizável: pasta em `controle-ir/capacidades/` com
  `capacidade.json` + script (JSON entra/sai) e teste; depois empacote, publique e use `atualizar_sistema(ref)`.
- Responda ao usuário em português. Testes: `python3 -m unittest discover -s testes`.
- Pacote do celular: `ferramentas/empacotar.sh` gera `dist/controle-ir.zip` (baixado pelo Termux).
- Botão novo para ar Gree (oscilação, visor): `ferramentas/gree_variante.py` (parte da captura real do perfil).
