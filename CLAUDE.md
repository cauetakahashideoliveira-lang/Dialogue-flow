# Contexto para o Claude Code

- Comece por [CONTRIBUTING.md](CONTRIBUTING.md) para instalar e testar. [docs/HANDOFF.md](docs/HANDOFF.md) traz as decisões, as medições e o trabalho seguinte, inclusive a integração com ChatGPT.
- Leia primeiro `graphify-out/GRAPH_REPORT.md` (grafo do código) e `docs/estado-atual.md` (instalação real do usuário).
- **Para operar aparelhos**, use `docs/aparelhos/README.md`: mapa cômodo → aparelho → controle, com uma ficha por
  aparelho (nome exato no conector, perfil, comandos testados, sinais extras `.ir`, ressalvas). Ao cadastrar ou
  testar um aparelho, atualize a ficha, o índice e `docs/estado-atual.md`.
- Sessões na nuvem: o hook `.claude/hooks/session-start.sh` instala o graphify (pacote `graphifyy`) e o numpy
  quando faltam. Se `graphify` não existir, rode esse hook com `CLAUDE_CODE_REMOTE=true`.
- Para perguntas de arquitetura use a skill graphify: `graphify query "<pergunta>"`, `graphify explain "<nó>"`,
  `graphify path "A" "B"`. Ao atualizar o conhecimento embarcado, rode `bash ferramentas/atualizar_conhecimento.sh` para regenerar o grafo de código e sincronizar as cópias usadas nas missões.
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
  sono, sonar, bluetooth, modos (`controle-ir/capacidades/`, com testes em `testes/`). **modos** (1.0.99): ajustes do
  próprio celular direto no Android (toque por `cmd audio set-ringer-mode` via Shizuku; volumes pelo `termux-volume`,
  porque o `--set` do shell é ignorado no HyperOS); guarda e restaura, aprende método+condições e cria atalho no widget.
- **Instruções do conector:** o Claude Code lê só os primeiros 4096 caracteres. `mcp.py` monta AJA PRIMEIRO →
  aparelhos → modos → REGRAS dentro de `VISIVEL`; o resto (DETALHES, capacidades) pode ser cortado. Aparelho do
  resumo = `controlar` direto, sem `consultar`/`opcoes` antes (teste `test_instrucoes_poem_aparelhos_e_regras_no_trecho_lido`).
- **Central da Casa** (https://claude.ai/artifact/XSh6ivS8Cc6BsKakes2pCh, fonte `artefatos/central-da-casa.html`):
  app do claude.ai com o Gênio (controla, programa o celular, cria painéis). Republique com o mesmo arquivo;
  os dados (`widgets`, `memoria`, `eventos`) ficam no banco do artefato (ferramenta ArtifactData).
- **Segurança** (`docs/seguranca.md`): desde a 1.0.23 o sistema fica DESARMADO por padrão (pelo conector só
  infravermelho, consulta e travar); o dono arma no celular (widget “Armar Controle IR”). Não há como armar,
  destravar ou aprovar pelo conector (autorizar só com o código do autenticador). **Central de Controle** (`painel/`,
  Cloudflare Worker): pareado (1.0.24+), só ele arma, com a digital; desde a 1.0.26 o conector pode entrar por ele
  (`https://<painel>/mcp`, OAuth com a digital, bloqueio na borda). Conector em uso: **Controle Geral** (o antigo
  “Controle master”, pela URL do ngrok, é recusado desde que “só pelo painel” foi ligado). Mudança no painel = PR que o dono aprova (merge);
  teste local com estado descartável em `painel/`: `npm ci`, `npx playwright install --with-deps chromium` e `npm run test:e2e`.
- **Canal direto** (1.0.46+): o celular mantém um WebSocket com a Central (`controle_ir/canal.py`, Durable Object
  `Canal`); chamadas sem túnel e avisos na hora; sem canal, volta ao ngrok sozinho (`docs/seguranca.md` §3d).
  `consultar` mostra `servidor.canal`. Tela: `acao=grade` lê/resolve grades NxN no celular (9x9, 16x16 com
  letras); `acao=rotina` guarda chamadas longas e repete N vezes; reflexos por app dispensam avisos de jogos.
- Pedidos de aprovação do conector vêm das permissões dele no claude.ai (claude.ai/customize/connectors →
  Controle Geral → “Sempre permitir”; a regra da organização `org_ask_ceiling` pode travar); não tente contornar. Ferramentas novas do conector só aparecem em conversas novas (lista fixa por conversa).
- **`/god-mode`** (`.claude/skills/god-mode/`, adaptação AGPL do G0DM0D3): AutoTune, notas, STM, `perguntar` e
  `comparar` vários modelos (OpenRouter com `OPENROUTER_API_KEY` ou servidor local) com síntese pelo Claude. Sem
  os prompts de jailbreak nem o Parseltongue do original. Não confundir com `/godmode` (capacidade máxima).
- **Delegar é obrigação, não opção** (pedido do dono, 22/11): o Claude é o gestor; quem executa é o agente do
  celular. Laço rápido/repetitivo (jogo, quiz, contas com cronômetro, testes em série) → `tela acao=piloto`
  (`visao:true` se a pergunta for desenhada, `continuar` para emendar rodadas) numa chamada; várias telas até um
  resultado → `acao=objetivo`; sequência conhecida → `sequencia`/`rotina`; trabalho longo → `acao=missao`. Nunca
  operar passo a passo pela nuvem o que tem cronômetro ou passa de 3 chamadas. A mesma regra está nas instruções
  do conector (`controle_ir/mcp.py`, "QUEM FAZ O QUÊ").
- **NUNCA, em teste ou automação de tela:** entrar em Opções do desenvolvedor, Depuração (USB/sem fio), Shizuku,
  Termux, Contas/Segurança/Senhas ou Redefinir; nem tocar em interruptor (liga/desliga) ou ajuste do sistema sem
  pedido explícito do dono. Em 21/11 um teste tocou o interruptor geral das Opções do desenvolvedor e derrubou o
  Shizuku. Testes de desempenho só em telas de leitura (Sobre o telefone, Bluetooth sem alternar, Armazenamento)
  e com `modelo:false` quando o caminho não for conhecido. O `acao=objetivo` (1.0.79+) já recusa interruptores
  sem `permitir` e usa cada pista uma vez.
- **Piloto** (1.0.51+, `capacidades/tela/piloto.py`, `acao=piloto`): laço rápido NO celular (o Claude fica fora do
  laço, como treinador): corrida memória/modelo local/Haiku, alvo semântico, gravador. Modelo local e quiz de teste:
  `docs/estado-atual.md` (19/11 noite). Para o estudo e o piloto do botão Stockfish no POCO, veja o README. Apps bloqueados (banco/senha) não
  são lidos nem tocados.
