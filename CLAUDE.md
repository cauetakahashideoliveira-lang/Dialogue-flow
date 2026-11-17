# Contexto para o Claude Code

- Leia primeiro `graphify-out/GRAPH_REPORT.md` (grafo do código) e `docs/estado-atual.md` (instalação real do usuário).
- Para perguntas de arquitetura use a skill graphify: `graphify query "<pergunta>"`, `graphify explain "<nó>"`,
  `graphify path "A" "B"`. Após mudar código, rode `graphify update .` (sem custo de LLM).
- Responda ao usuário em português. Testes: `python3 -m unittest discover -s testes`.
- Pacote do celular: `ferramentas/empacotar.sh` gera `dist/controle-ir.zip` (baixado pelo Termux).
