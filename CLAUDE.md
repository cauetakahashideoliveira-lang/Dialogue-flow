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
- Autonomia: no modo autônomo (`politica.perfil=="autonomo"`) aja sem pedir a cada passo; pare só no claramente
  arriscado/irreversível. Só o celular muda o modo. Nunca ajude a acessar rede/conta/equipamento de terceiros.
- Responda ao usuário em português. Testes: `python3 -m unittest discover -s testes`.
- Pacote do celular: `ferramentas/empacotar.sh` gera `dist/controle-ir.zip` (baixado pelo Termux).
- Botão novo para ar Gree (oscilação, visor): `ferramentas/gree_variante.py` (parte da captura real do perfil).
- **Publicar no celular:** rode `ferramentas/empacotar.sh` ANTES do commit — o `atualizar_sistema(ref)` baixa o
  `dist/controle-ir.zip` daquele commit, não o código solto. Suba a versão em `controle_ir/__init__.py` para
  conferir com `consultar`. Se o conector der "Not Found" após atualizar, peça `controle-ir desligar; pkill ngrok;
  controle-ir ligar` (a 1.0.15+ já limpa o ngrok órfão sozinha).
- **Capacidades embutidas:** estado_celular, diagnostico_rede, descobrir_rede, ouvir_bipe, foto, termometro, tela,
  sono, sonar (`controle-ir/capacidades/`, com testes em `testes/`).
- **Central da Casa** (https://claude.ai/artifact/XSh6ivS8Cc6BsKakes2pCh, fonte `artefatos/central-da-casa.html`):
  app do claude.ai com o Gênio (controla, programa o celular, cria painéis). Republique com o mesmo arquivo;
  os dados (`widgets`, `memoria`, `eventos`) ficam no banco do artefato (ferramenta ArtifactData).
- Pedidos de aprovação do conector vêm da regra da organização no claude.ai (`org_ask_ceiling`); não tente
  contornar. Ferramentas novas do conector só aparecem em conversas novas (lista fixa por conversa).
