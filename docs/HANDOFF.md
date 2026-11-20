# Guia de passagem (handoff) — Controle IR do POCO + Claude

Para quem vai continuar o projeto (outro dev, outra conta, outro repositório). Lendo só este arquivo, os links que
ele aponta e o código, dá para entender, desenvolver, publicar e operar tudo — sem precisar das conversas antigas.

> Versão do sistema no celular quando este guia foi escrito: **1.0.63** (20/11/2026).
> Registro detalhado de tudo o que foi feito, dia a dia: `docs/estado-atual.md`.

---

## 1. O que é

Um celular Android (POCO X8 Pro Max, chip MT6991, 12 GB) vira um **agente doméstico controlado pelo Claude**:

- **Controle infravermelho** de ar-condicionado, TV etc. (emissor IR do próprio celular, catálogo de ~9.400 perfis).
- **Agente de tela**: vê e opera apps do celular pela acessibilidade (Shizuku, sem root), com toques injetados em
  milissegundos.
- **Piloto**: laço rápido que roda no próprio celular (sem passar pelo Claude a cada gesto) — joga quiz com uma
  "escada de inteligência" (memória → modelo local → Claude Sonnet) e xadrez contra robôs com Stockfish.
- **Central de Controle**: Cloudflare Worker que autentica (passkey/digital), arma/desarma o sistema e serve de
  porta de entrada do conector MCP do claude.ai.

## 2. Arquitetura

```
claude.ai (conector "Controle Geral")
   │  MCP + OAuth 2.1 (PKCE)
   ▼
Central de Controle — Cloudflare Worker `painel-casa` (painel/)
   │  D1 (contas, aparelhos, passkeys) · KV (tokens OAuth, só hash) · Durable Object `Canal`
   │  canal direto: WebSocket aberto PELO celular (sem túnel)  ── se cair: túnel ngrok (fallback)
   ▼
Celular — Termux: serviço `controle-ir` (controle-ir/controle_ir/, porta local 8765)
   ├─ servidor MCP local (ferramentas: controlar, consultar, executar_capacidade, tarefa, atualizar_sistema…)
   ├─ execução governada (política no celular; desarmado por padrão; só o dono arma)
   ├─ capacidades plugáveis (controle-ir/capacidades/*: tela, foto, sono, termometro, sonar…)
   │    └─ tela: Python + leitor Java (Tela.java via app_process + Shizuku/rish, UiAutomation)
   │         └─ piloto.py: laço rápido (quiz e xadrez), cérebros locais e da API
   └─ emissor IR (termux-infrared-transmit)
```

Por que assim: o Claude só "vê" a tela quando uma chamada de ferramenta volta (~3 s por decisão). Tudo que precisa
ser rápido mora no celular (reflexos, piloto, motores); o Claude programa, configura e supervisiona.

## 3. Mapa do repositório

| Caminho | O que é |
|---|---|
| `controle-ir/controle_ir/` | Serviço do celular: `servico.py` (ferramentas), `mcp.py` (protocolo), `servidor.py` (HTTP local), `canal.py` (WebSocket com a Central), `painel.py` (sincronização com a Central), `seguranca.py` + `execucao.py` (política e tarefas), `cli.py` (comando `controle-ir`: ligar, atualizar…), `catalogo.py`/`protocolos.py`/`emissor.py` (IR) |
| `controle-ir/capacidades/<nome>/` | Capacidades plugáveis: `capacidade.json` (manifesto + esquema) + `principal.py` |
| `controle-ir/capacidades/tela/` | Agente de tela: `principal.py`, `piloto.py`, `java/controleir/Tela.java` (compilado NO celular), `quiz/quiz.html` (quiz de teste) |
| `controle-ir/instalar.sh` | Instalador no Termux |
| `controle-ir/dados/` | Catálogo IR empacotado |
| `dist/controle-ir.zip` | **Pacote que o celular baixa** (gerado por `ferramentas/empacotar.sh`; vai no commit) |
| `painel/` | Central de Controle (Cloudflare Worker): `src/index.js`, `public/`, `schema.sql`, `wrangler.jsonc`, `testes/e2e.cjs` |
| `artefatos/central-da-casa.html` | Fonte do app "Central da Casa" (artefato do claude.ai) |
| `testes/` | Testes Python (`test_controle_ir.py`, `test_god_mode.py`) |
| `ferramentas/` | `empacotar.sh`, `construir_catalogo.py`, `gree_variante.py`, `verificar_cliente_mcp.py` |
| `docs/` | `estado-atual.md` (diário do que existe), `seguranca.md` (modelo de ameaça e decisões), `modo-deus.md` (visão/roadmap), `aparelhos/` (fichas dos aparelhos da casa), este guia |
| `.claude/` | Hooks e skills do Claude Code (graphify, god-mode) |
| `graphify-out/` | Grafo do código (`GRAPH_REPORT.md`) — `graphify update .` regenera |
| `CLAUDE.md` | Instruções para o Claude Code neste repositório |

## 4. Desenvolver e testar

Requisitos: Python 3.11+ (só biblioteca padrão no celular), Node 20+ para o painel.

```bash
python3 -m unittest discover -s testes          # 165 testes (Python), ~50 s
graphify update .                               # atualiza o grafo do código (opcional, sem custo de LLM)
cd painel && npm install && npm run dev         # Central local (wrangler dev, porta 8787)
node painel/testes/e2e.cjs                      # E2E da Central (rode com o `npm run dev` ativo, sem variáveis de proxy)
```

## 5. Publicar no celular (o ciclo que se repete)

O celular instala **o `dist/controle-ir.zip` de um commit** — não o código solto. Sempre:

1. Suba a versão em `controle-ir/controle_ir/__init__.py` (para conferir depois).
2. `bash ferramentas/empacotar.sh` (gera `dist/controle-ir.zip`) — **antes** do commit.
3. Testes passando; `git commit` e `git push`.
4. No Claude (conector), `atualizar_sistema(ref=<hash completo do commit>)` — o celular baixa
   `<repositório>/raw/<hash>/dist/controle-ir.zip`, guarda a versão anterior e reinicia em ~1 min.
5. Confira com `consultar` (campo `servidor.versao`). Para voltar atrás: atalho "Reverter Controle IR" no celular.

O repositório precisa ser **público** (o download é sem login).

## 6. Central de Controle (Cloudflare)

- Worker `painel-casa` (`painel/wrangler.jsonc`). Recursos: D1 `painel` (`painel/schema.sql`), KV `OAUTH_KV`,
  Durable Object `Canal` (migração `v1`), assets em `public/`.
- **Segredo** (no painel da Cloudflare, nunca no repo): `CODIGO_INICIAL` (12+ caracteres; só serve para cadastrar a
  primeira passkey).
- Publicação: integração Git da Cloudflare a partir da branch principal (builds de branches de preview foram
  desligados). Alternativa manual: `cd painel && npm run deploy`. Confirme no painel da Cloudflare qual branch
  publica.
- Mudança no painel = PR que o dono aprova.

## 7. Credenciais — onde ficam (nenhuma está no repositório)

| Credencial | Onde vive | Para que serve |
|---|---|---|
| Passkeys do dono | Cloudflare D1 (só a chave pública) + aparelhos do dono | entrar na Central, armar |
| `CODIGO_INICIAL` | segredo do Worker na Cloudflare | cadastrar a 1ª passkey |
| Token do aparelho / segredo local | `~/.controle-ir/` no celular | celular ↔ Central; caminho do /mcp local |
| Chave da API da Anthropic | `~/.controle-ir/anthropic.key` (chmod 600) no celular | cérebros do piloto (Haiku/Sonnet) |
| Tokens OAuth do conector | KV da Cloudflare (só hash) | claude.ai ↔ Central |

Varredura feita em 20/11: nenhum segredo em arquivos nem no histórico do git.

## 8. O que existe só no celular (e como recriar)

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

## 9. Piloto (laço rápido) — como usar

Pela ferramenta `executar_capacidade(nome="tela", argumentos={...})`:

- **Quiz**: `{"acao":"piloto","iniciar":{"modo":"quiz","app":"com.android.chrome","cerebros":["memoria","local","api"],"modelos":["claude-sonnet-5-5"],"confianca":0.95,"precisao_alvo":0.9,"prazo":1.6}}`
  - o Sonnet roda em toda pergunta e é o gabarito; a precisão medida do modelo local decide se ele age sozinho;
    a memória só guarda resposta do Sonnet.
- **Xadrez (só contra robô)**: `{"acao":"piloto","iniciar":{"modo":"xadrez","ms_lance":400,"threads":7,"hash_mb":256}}`
  - recusa/para se a tela não for a partida contra robô. No Chess.com: Jogar → "Jogar com Bots" (NUNCA
    "Começar Partida", que é contra pessoas).
- Estado/gravador: `{"acao":"piloto"}` · parar: `{"acao":"piloto","parar":true}` · medir cérebros sem tela:
  `{"acao":"piloto","testar":{"pergunta":"…","opcoes":["…"]}}`.

Resultados de referência (20/11): quiz 29/30 sem memória (mediana 1,6 s) e 30/30 com memória (0,7 s);
xadrez — vitórias contra os robôs de 1200 (blitz), 2500 e **3200 "Máximo" (bullet 1 min, mate em 65 lances)**.

## 10. Segurança — o essencial (detalhes: `docs/seguranca.md`)

- O sistema fica **desarmado** por padrão: pelo conector só infravermelho, consultas e travar. Armar é só no
  celular/Central, com a digital. Não existe caminho para armar ou aprovar pelo conector.
- Agente de tela: apps de banco/pagamento/senha (lista em `tela/principal.py`, `BLOQUEADOS_PADRAO`, editável em
  `~/.controle-ir/tela_bloqueados.json`) **não são lidos nem tocados**.
- Piloto: só contra a máquina (quiz próprio, robôs). Nunca contra pessoas (trapaça) — há trava no código.
- Nunca colocar chaves/tokens no repositório nem no chat.

## 11. Continuar em OUTRO repositório

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

## 12. Próximos passos sugeridos

- Reduzir os ~0,5 s entre a página mudar e o piloto agir (perceber por diferença de quadros da captura).
- Piloto em apps de quiz reais (contra a máquina).
- Degrau Opus na escada de inteligência para jogos com prazo maior.
- Ideias e roadmap amplo: `docs/modo-deus.md`.
