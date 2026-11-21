# Passagem de bastão do Dialogue-flow

Este guia acompanha a revisão de 21/11/2026. A base auditada foi o merge do PR #21 (`6ba61cc`, serviço 1.0.64). A atualização 1.0.65 sincroniza o grafo usado nas missões e o pacote instalável. Consulte o SHA do pacote para distinguir alterações que compartilharam o número 1.0.64.

**Primeira hora de um novo dev.** Clone a branch padrão, rode o cliente MCP simulado e inicie a Central local com uma passkey virtual. O procedimento inclui as versões, as dependências e os resultados esperados. [Guia de contribuição](../CONTRIBUTING.md)

## Arquitetura

| Componente | O que executa | Como observar |
|---|---|---|
| ChatGPT, Claude web ou Claude Code | Envia objetivos e chamadas MCP por HTTPS à Central. | `consultar` informa versão, catálogo e canal do aparelho pareado. |
| Central de Controle (`painel/`) | Worker com passkeys e OAuth. D1 guarda cadastro, estado e auditoria; KV guarda dados do provedor OAuth; um Durable Object por aparelho mantém o WebSocket. | A página do aparelho mostra saúde, último contato, canal e atividade. |
| Termux no Android | Serviço Python residente, MCP, API e painel em loopback. O celular abre o WebSocket para a Central; o túnel configurado serve de caminho alternativo quando necessário. | `controle-ir status`, `controle-ir painel estado`, `controle-ir log`. |
| Capacidades e motores | Emissor IR e catálogo SQLite; nove capacidades embutidas, incluindo leitura de tela via Shizuku, sensores e câmera. Stockfish e modelos locais opcionais executam no telefone. | `capacidades` lista o que aquela instalação oferece. O registro do piloto mostra lances, confirmações e tempos. |
| Artefato Central da Casa (`artefatos/`) | Interface separada publicada no Claude, que usa as ferramentas do projeto. Tem armazenamento da própria conta. | A fonte HTML está versionada e pode ser publicada na conta do responsável. |

## O que aconteceu até aqui

| Etapa | Entrega que o próximo dev pode encontrar no código |
|---|---|
| 17 e 18/11/2026 · fundação | O serviço passou a emitir IR pelo Termux:API, importar SmartIR e Flipper, montar o catálogo SQLite e salvar perfis confirmados. A descoberta ganhou lotes, pausa, reteste e retomada. O projeto acrescentou atalhos, boot em segundo plano, fichas dos aparelhos e capacidades plugáveis. [Primeiro commit](https://github.com/cauetakahashideoliveira-lang/Dialogue-flow/commit/9b68ff3) · [fichas dos aparelhos](aparelhos/README.md) |
| PRs #1–#5 · ferramentas de desenvolvimento | Hooks e skills do Claude Code, regras do conector e consultas ao grafo entraram no repositório. O hook remoto prepara o ambiente para sessões novas. [Hook e skills](https://github.com/cauetakahashideoliveira-lang/Dialogue-flow/pull/1) · [fichas](https://github.com/cauetakahashideoliveira-lang/Dialogue-flow/pull/3) · [Graphify](https://github.com/cauetakahashideoliveira-lang/Dialogue-flow/pull/5) |
| PRs #6–#12 · Central e transporte | O Worker ganhou passkeys, pareamento, OAuth, revogação, auditoria, estado ao vivo e um WebSocket iniciado pelo Android. O serviço passou a agrupar gestos, usar o leitor rápido em Java e devolver mudanças compactas. [OAuth](https://github.com/cauetakahashideoliveira-lang/Dialogue-flow/pull/8) · [desempenho](https://github.com/cauetakahashideoliveira-lang/Dialogue-flow/pull/11) · [canal direto](https://github.com/cauetakahashideoliveira-lang/Dialogue-flow/pull/12) |
| PR #13 · decisões no aparelho | Entraram reflexos, rotinas, piloto de quiz com memória e modelos, Stockfish residente, confirmação dos lances e tempos por etapa. O diário registra os ensaios no POCO e as limitações físicas. [PR #13](https://github.com/cauetakahashideoliveira-lang/Dialogue-flow/pull/13) · [diário do aparelho](estado-atual.md) |
| PRs #14–#17 · ChatGPT, saúde e rotas | O OAuth aceitou callbacks do ChatGPT. A Central passou a mostrar saúde e canal, o widget ganhou reinício e a navegação passou a guardar rotas confirmadas. A manutenção da sessão MCP passou a responder `ping` e `notifications/initialized` na borda. [ChatGPT](https://github.com/cauetakahashideoliveira-lang/Dialogue-flow/pull/14) · [saúde](https://github.com/cauetakahashideoliveira-lang/Dialogue-flow/pull/15) · [rotas](https://github.com/cauetakahashideoliveira-lang/Dialogue-flow/pull/16) · [transporte](https://github.com/cauetakahashideoliveira-lang/Dialogue-flow/pull/17) |
| PRs #18–#20 · missões e avaliação | Um único pedido do chat passou a executar várias etapas no POCO. O planejador recebeu contexto atualizado, Sonnet com esforço alto e saída validada por esquema. Os PRs #19 e #20 entraram na branch de missão e chegaram à padrão pelo #18. [Missão](https://github.com/cauetakahashideoliveira-lang/Dialogue-flow/pull/18) · [contexto](https://github.com/cauetakahashideoliveira-lang/Dialogue-flow/pull/19) · [planejador e bateria](https://github.com/cauetakahashideoliveira-lang/Dialogue-flow/pull/20) |
| PR #21 · Stockfish pelo botão | O Termux:Widget passou a abrir o estudo offline. O comando local `piloto` passou a reconhecer as 64 casas no Chess.com, consultar a vez no histórico e aguardar quando o app perde o foco. O botão usa esse fluxo sem depender de uma conversa aberta. [PR #21](https://github.com/cauetakahashideoliveira-lang/Dialogue-flow/pull/21) |
| Revisão de 21/11 · outro desenvolvedor | O simulador ganhou um roteiro reproduzível, a Central um teste descartável com dependências declaradas, e os PRs passaram a conferir software, grafo e distribuição. O pacote leva o contexto de código atualizado para as missões. [PR de revisão](https://github.com/cauetakahashideoliveira-lang/Dialogue-flow/pull/22) |

## Missões, rotas e piloto

**Uma missão** entra pelo MCP com `executar_capacidade`, nome `tela` e ação `missao`. O serviço residente monta a lista de ferramentas, a política efetiva, as capacidades instaladas, os resumos de quatro skills e as relações do grafo relevantes para o objetivo. A seleção de ferramentas usa o ID `claude-sonnet-5-5` na API Anthropic com esforço `high`. O código Python no POCO valida o plano e chama o mesmo despachante que atende o MCP. O retorno traz os resultados das etapas já executadas e o motivo de uma eventual interrupção. [Contexto e despachante](../controle-ir/controle_ir/ambiente_missao.py)

Para um primeiro teste de leitura, peça a versão do servidor e o percentual de bateria.

```json
{"nome":"tela","argumentos":{"acao":"missao","texto":"Consulte o servidor e depois informe a bateria do celular."}}
```

As opções padrão são consultar o servidor, ler o estado do celular, consultar a política, consultar o progresso e listar capacidades. O contexto pode descrever mais ferramentas do que as habilitadas para aquele pedido. O modelo escolhe índices das opções recebidas. O despachante revalida as operações na execução. Os códigos de saída distinguem falta de opção permitida, plano vazio, resposta inválida, modelo indisponível e interrupção em uma operação.

**Uma rota** guarda um caminho por aplicativo, rótulos e marcador de chegada. A missão com `passos` pode encadear até 16 etapas, reutilizar rotas e devolver os gestos e o estado de cada etapa. O identificador exato de uma rota permite selecioná-la diretamente. [Execução de navegação](../controle-ir/controle_ir/missao.py) · [rotas](../controle-ir/controle_ir/rotas.py)

**O piloto** corre em outra escala de tempo. Seu laço observa a tela no Android, decide e confirma a ação. A memória, o modelo local opcional e a API atendem ao quiz conforme a configuração. No xadrez, Stockfish calcula o lance no próprio celular. O comando `parar` no atalho encerra o piloto de xadrez. [Piloto](../controle-ir/capacidades/tela/piloto.py) · [estudo e atalho](../controle-ir/controle_ir/estudo_xadrez.py)

## O que foi medido

| Amostra de 20/11/2026 | Resultado publicado e interpretação |
|---|---|
| 142 execuções em 55 casos multidomínio | 54 respostas de raciocínio, 10 missões, 6 operações de calculadora e 72 tentativas de xadrez. O relatório e os CSV podem ser recalculados dentro de uma cópia extraída do ZIP com `python analisar.py`. Cada família tem seu próprio critério de acerto. [Dados, casos e instruções](../benchmarks/2026-11-20-multidominio/) |
| 160 missões de consulta no mesmo POCO | Os mesmos 40 pedidos foram repetidos duas vezes por versão. Acertos totais passaram de 66/80 para 80/80. Na candidata, 60/60 pedidos viáveis foram concluídos e 20/20 inviáveis foram interrompidos, com zero operações extras. [Registros e gabarito](../benchmarks/2026-11-20-planejador/) |
| Latência das mesmas missões | A mediana de ponta a ponta passou de 5,55 s para 5,26 s e o P95 de 7,29 s para 6,65 s. Nos 46 pares viáveis concluídos por ambas as versões, a diferença mediana foi **+15,5 ms**. O ganho demonstrado foi concluir mais pedidos corretamente. As versões rodaram em blocos no mesmo aparelho. [Protocolo](../benchmarks/2026-11-20-planejador/protocolo.md) |
| Xadrez e telas | Na bateria de busca pura, 200 e 500 ms resolveram os mesmos 24/24 problemas; 50 ms resolveu 23/24. O diário registra separadamente uma partida bullet contra o robô Máximo (3200), com mate em 65 lances. Os tempos do motor puro e de uma partida com leitura e toques medem coisas diferentes. [Relatório da bateria](../benchmarks/2026-11-20-multidominio/Bateria_POCO.zip) · [partidas registradas](estado-atual.md) |

As duas baterias são históricas. Nesta revisão, a recomputação reproduziu os quatro CSV e o HTML da primeira e o `resumo.json` da segunda, a partir dos dados gravados. As medições em um POCO descrevem esse aparelho, a rede e a configuração de modelo usados na coleta.

## Mapa do repositório

| Caminho | O que é |
|---|---|
| `controle-ir/controle_ir/` | Serviço do celular: `servico.py` (ferramentas), `mcp.py` (protocolo), `servidor.py` (HTTP local), `canal.py` (WebSocket com a Central), `painel.py` (sincronização com a Central), `seguranca.py` + `execucao.py` (política e tarefas), `cli.py` (comando `controle-ir`: ligar, atualizar…), `catalogo.py`/`protocolos.py`/`emissor.py` (IR) |
| `controle-ir/capacidades/<nome>/` | Capacidades plugáveis: `capacidade.json` (manifesto + esquema) + `principal.py` |
| `controle-ir/capacidades/tela/` | Agente de tela: `principal.py`, `piloto.py`, `java/controleir/Tela.java` (compilado NO celular), `quiz/quiz.html` (quiz de teste) |
| `controle-ir/conhecimento/` | Cópia do grafo e das quatro skills lidas por `ambiente_missao.py` no início de cada missão. |
| `controle-ir/instalar.sh` | Instalador no Termux |
| `controle-ir/dados/` | Catálogo IR empacotado |
| `dist/controle-ir.zip` | **Pacote que o celular baixa** (gerado por `ferramentas/empacotar.sh`; vai no commit) |
| `painel/` | Central de Controle (Cloudflare Worker): `src/index.js`, `public/`, `schema.sql`, `wrangler.jsonc`, `testes/e2e.cjs` |
| `artefatos/central-da-casa.html` | Fonte do app "Central da Casa" (artefato do claude.ai) |
| `testes/` | Testes Python do serviço, ferramentas do projeto e atalho Stockfish |
| `ferramentas/` | `empacotar.sh`, `construir_catalogo.py`, `gree_variante.py`, `verificar_cliente_mcp.py` |
| `docs/` | `estado-atual.md` (diário do que existe), `seguranca.md` (modelo de ameaça e decisões), `modo-deus.md` (visão/roadmap), `aparelhos/` (fichas dos aparelhos da casa), este guia |
| `.claude/` | Hooks e skills do Claude Code (graphify, god-mode) |
| `graphify-out/` | Grafo do código (`GRAPH_REPORT.md`) — `graphify update .` regenera |
| `CLAUDE.md` | Instruções para o Claude Code neste repositório |

## Desenvolver e testar

As verificações de referência são a suíte Python, os contratos do planejador, o roteiro do SDK MCP oficial e o teste do Worker com Chromium. O teste do Worker usa autenticação virtual, celular simulado e armazenamento temporário. Os dados das duas baterias podem ser reanalisados sem chamar modelos. [Comandos e dependências](../CONTRIBUTING.md)

Na revisão, passaram **172 testes Python** e **6 testes de contrato do planejador**. O SDK oficial confirmou três transmissões simuladas. No GitHub Actions, as **56 verificações da Central** cobriram também as duas formas de callback do ChatGPT e as mensagens de manutenção respondidas antes de chamar o Android. [Execução de referência](https://github.com/cauetakahashideoliveira-lang/Dialogue-flow/actions/runs/44899068891)

## Publicar no celular (o ciclo que se repete)

O celular instala **o `dist/controle-ir.zip` de um commit** — não o código solto. Sempre:

1. Suba a versão em `controle-ir/controle_ir/__init__.py` (para conferir depois).
2. `bash ferramentas/empacotar.sh` (gera `dist/controle-ir.zip`) — **antes** do commit.
3. Testes passando; `git commit` e `git push`.
4. No Claude (conector), `atualizar_sistema(ref=<hash completo do commit>)` — o celular baixa
   `<repositório>/raw/<hash>/dist/controle-ir.zip`, guarda a versão anterior e reinicia em ~1 min.
5. Confira com `consultar` (campo `servidor.versao`). Para voltar atrás: atalho "Reverter Controle IR" no celular.

O repositório precisa ser **público** (o download é sem login).

## Central de Controle (Cloudflare)

O gateway MCP escolhe o primeiro aparelho cadastrado que esteja ativo, por ordem de criação. Para desenvolver e operar um segundo ambiente de forma independente, use a Central da conta do novo dev e pareie o telefone dele ali. O teste local usa um Worker e um banco próprios a cada execução.

- Worker `painel-casa` (`painel/wrangler.jsonc`). Recursos: D1 `painel` (`painel/schema.sql`), KV `OAUTH_KV`,
  Durable Object `Canal` (migração `v1`), assets em `public/`.
- **Segredo do Worker** `CODIGO_INICIAL` (12+ caracteres; só serve para cadastrar a
  primeira passkey).
- Na instalação de referência foi usada a integração Git da Cloudflare. Para publicar na conta de desenvolvimento: `cd painel && npm run deploy`. Confirme no painel da Cloudflare qual branch
  publica.
- Mudança no painel = PR que o dono aprova.

## Configuração por instalação

| Credencial | Onde vive | Para que serve |
|---|---|---|
| Passkeys do dono | Cloudflare D1 (só a chave pública) + aparelhos do dono | entrar na Central, armar |
| `CODIGO_INICIAL` | segredo do Worker na Cloudflare | cadastrar a 1ª passkey |
| Token do aparelho / segredo local | `~/.controle-ir/` no celular | celular ↔ Central; caminho do /mcp local |
| Chave da API da Anthropic | `~/.controle-ir/anthropic.key` (chmod 600) no celular | cérebros do piloto (Haiku/Sonnet) |
| Dados do provedor OAuth | KV da instalação Cloudflare | cliente MCP ↔ Central |

Na revisão de 21/11, uma busca por formatos conhecidos de chaves privadas, tokens e URLs MCP com segredo percorreu os 140 arquivos rastreados da revisão de partida e os membros dos ZIPs. Nenhum desses padrões foi encontrado. Para uma nova instalação, gere credenciais próprias nas contas correspondentes.

## O que existe só no celular (e como recriar)

| Item | Onde | Recriar |
|---|---|---|
| Termux, Termux:API, Termux:Widget, Termux:Boot (F-Droid) + Shizuku | apps | README → "Instalação" |
| Serviço `controle-ir` | `~/controle-ir`, config em `~/.controle-ir` | linha de instalação do README |
| Chave da Anthropic | `~/.controle-ir/anthropic.key` | no Termux: `read -rsp "Chave: " K; printf %s "$K" > ~/.controle-ir/anthropic.key; chmod 600 ~/.controle-ir/anthropic.key; unset K` |
| llama.cpp otimizado (dotprod/i8mm) | `~/.controle-ir/llama.cpp/build/bin` | `pkg install cmake git clang`; `git clone --depth 1 https://github.com/ggml-org/llama.cpp`; `cmake -B build -DGGML_NATIVE=ON -DLLAMA_CURL=OFF -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=OFF -DCMAKE_BUILD_TYPE=Release && cmake --build build -j8 --target llama-server llama-bench` (o pacote `llama-cpp` do Termux é genérico e ~4,5x mais lento) |
| Modelos locais | `~/.controle-ir/modelos/` | Qwen2.5-3B-Instruct Q4_0 (`huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF`, arquivo `qwen2.5-3b-instruct-q4_0.gguf`); também há o 1.5B |
| Servidor do modelo local | processo `llama-server` em 127.0.0.1:8080 | `B=~/.controle-ir/llama.cpp/build/bin; LD_LIBRARY_PATH=$B setsid nohup $B/llama-server -m ~/.controle-ir/modelos/qwen2.5-3b-q4_0.gguf --host 127.0.0.1 --port 8080 -c 1024 -t 6 -tb 6 --no-webui > ~/.controle-ir/piloto/llama.log 2>&1 &` |
| Stockfish 19 | `pkg install stockfish` | idem |
| Quiz de teste | servidor em 127.0.0.1:**8766** (a 8765 é do serviço) | `cd ~/controle-ir/capacidades/tela/quiz && setsid nohup python -m http.server 8766 --bind 127.0.0.1 &` (religar após cada atualização) |
| Memória e gravador do piloto | `~/.controle-ir/piloto/` (`memoria.json`, `rodadas.jsonl`) | criados sozinhos |

## Piloto (laço rápido) — como usar

Pela ferramenta `executar_capacidade(nome="tela", argumentos={...})`:

- **Quiz**: `{"acao":"piloto","iniciar":{"modo":"quiz","app":"com.android.chrome","cerebros":["memoria","local","api"],"modelos":["claude-sonnet-5-5"],"confianca":0.95,"precisao_alvo":0.9,"prazo":1.6}}`
  - o Sonnet roda em toda pergunta e é o gabarito; a precisão medida do modelo local decide se ele age sozinho;
    a memória só guarda resposta do Sonnet.
- **Xadrez pelo MCP, configuração padrão para robô**: `{"acao":"piloto","iniciar":{"modo":"xadrez","ms_lance":400,"threads":7,"hash_mb":256}}`
  - recusa/para se a tela não for a partida contra robô. No Chess.com: Jogar → "Jogar com Bots" (NUNCA
    "Começar Partida", que é contra pessoas).
- Estado/gravador: `{"acao":"piloto"}` · parar: `{"acao":"piloto","parar":true}` · medir cérebros sem tela:
  `{"acao":"piloto","testar":{"pergunta":"…","opcoes":["…"]}}`.

Resultados de referência (20/11): quiz 29/30 sem memória (mediana 1,6 s) e 30/30 com memória (0,7 s);
xadrez — vitórias contra os robôs de 1200 (blitz), 2500 e **3200 "Máximo" (bullet 1 min, mate em 65 lances)**.

## Segurança — o essencial (detalhes: `docs/seguranca.md`)

- O sistema fica **desarmado** por padrão: pelo conector só infravermelho, consultas e travar. Armar é só no
  celular/Central, com a digital. A aprovação remota, se habilitada pelo dono, exige o código do autenticador. O pareamento transfere a armação para a Central.
- Agente de tela: apps de banco/pagamento/senha (lista em `tela/principal.py`, `BLOQUEADOS_PADRAO`, editável em
  `~/.controle-ir/tela_bloqueados.json`) **não são lidos nem tocados**.
- O piloto de xadrez padrão do MCP verifica a atividade de robô. O atalho Stockfish usa o modo de tabuleiro local descrito acima. O estado do piloto informa a configuração em uso.
- Nunca colocar chaves/tokens no repositório nem no chat.

## Continuar em OUTRO repositório

1. Crie o repositório novo (público) e envie tudo: `git remote add novo <url>` e
   `git push novo --all && git push novo --tags`.
2. No **celular**, aponte as atualizações para o repositório novo, sem republicar nada:
   `echo https://github.com/<dono>/<repo> > ~/.controle-ir/repositorio` (ou variável `CONTROLE_IR_REPO`).
   A partir daí `atualizar_sistema(ref)` baixa do repositório novo.
3. No código, troque o padrão `REPO_PADRAO` em `controle-ir/controle_ir/cli.py` e a linha de instalação do
   `README.md` (seção "Instalação"), publique uma versão nova.
4. **Cloudflare**: reconecte a integração Git do Worker `painel-casa` ao repositório novo (ou publique com
   `npm run deploy`). O D1/KV/segredos continuam na conta Cloudflare — nada a migrar se for a mesma conta.
5. **claude.ai**: o conector "Controle Geral" aponta para a URL da Central (`https://<worker>/mcp`), não para o
   GitHub — continua funcionando. A "Central da Casa" é um artefato da conta do dono; a fonte está em
   `artefatos/central-da-casa.html` (republicar na conta nova, se mudar de conta).
6. Claude Code no repositório novo: o `CLAUDE.md` e o hook `.claude/hooks/session-start.sh` vêm junto.

## Onde continuar

| Prioridade | Trabalho | Critério de verificação |
|---|---|---|
| 1 | Integrar um segundo dev com sua própria Central e Android. | Criar a primeira passkey, parear, executar `consultar` pela conta do novo dev e confirmar o canal; registrar versão e recibo sem identificadores privados. |
| 2 | Repetir falhas de API e de ferramenta durante missões de várias etapas. | Conferir o código de interrupção, o recibo de cada etapa concluída e a ausência de operações posteriores. |
| 3 | Separar tempo de API, despacho local, leitura da tela e transporte. | Comparar mediana e P95 em casos pareados, por tipo de operação, antes de mudar o modelo ou os tempos do piloto. |
| 4 | Ampliar a amostra para navegação e xadrez. | Usar objetivos inéditos, mudar layout e interromper o foco no meio da partida. Registrar retomada, lances confirmados, toques incorretos e consumo no aparelho. |
| 5 | Revalidar sensores em hardware da nova instalação. | Testar bipe, calibrar temperatura com referência e repetir sono/sonar com autorização do dono. O simulador valida a lógica; os dados físicos dependem do aparelho. |

A cobertura publicada inclui testes de software e medições históricas no POCO de referência. A instalação em outra conta Cloudflare, o pareamento de outro Android e os ensaios físicos acima são os próximos testes de integração. [Plano das baterias](../benchmarks/2026-11-20-planejador/README.md) · [histórico do laboratório](estado-atual.md)
