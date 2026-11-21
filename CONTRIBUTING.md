# Contribuir com o Dialogue-flow

Um clone é suficiente para desenvolver o servidor MCP, testar a Central com uma passkey virtual e conferir os dados dos benchmarks. Para usar infravermelho, sensores ou gestos reais, prepare um Android seu. Para operar pela sua conta do ChatGPT ou do Claude, pareie esse Android com uma Central sua. A arquitetura, as decisões e os resultados de cada etapa estão no [guia de passagem](docs/HANDOFF.md).

## Primeiro teste no computador ou na nuvem

Use Git, Python 3.12 e, para a Central, Node 22.12 ou superior com npm. A revisão foi feita com Node 24. Execute os blocos a partir da raiz do clone, salvo quando indicado.

```bash
git clone https://github.com/cauetakahashideoliveira-lang/Dialogue-flow.git
cd Dialogue-flow
git switch -c dev/minha-mudanca
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r testes/requirements.txt
python ferramentas/verificar_cliente_mcp.py
```

O último comando inicia o servidor em uma porta local livre, negocia o protocolo com o SDK oficial, lista as ferramentas, salva um perfil de ar e envia três transmissões ao emissor simulado. A última linha começa com `OK: cliente MCP oficial`. O catálogo e as configurações de teste ficam numa pasta temporária. Esse é o primeiro teste para quem recebeu o repositório e ainda não tem acesso a aparelho ou provedor.

| O que você mudou | Como verificar a partir da raiz |
|---|---|
| Núcleo Python, capacidades, política, atalhos ou CLI | `python -m unittest discover -s testes` |
| Contrato do planejador e interrupção entre operações | `python benchmarks/2026-11-20-planejador/test_planejador.py` |
| Resultado de autonomia publicado | `python benchmarks/2026-11-20-planejador/analisar.py`. Compare a saída com `resumo.json` na mesma pasta. |
| Ferramentas, transporte ou formatos de resposta do MCP | `python ferramentas/verificar_cliente_mcp.py` |
| Conteúdo e permissões do ZIP instalável | `bash ferramentas/empacotar.sh --verificar` |
| Login, pareamento, OAuth, canal ou interface da Central | Execute o teste de ponta a ponta abaixo. |

### Central de Controle em desenvolvimento

O Worker em `painel/` usa D1 para cadastros e auditoria, KV para OAuth e um Durable Object para o canal com o Android. O Wrangler emula os três localmente. Mantenha o ambiente Python do primeiro teste ativo. O teste da Central chama o código Python de pareamento e assinatura.

```bash
cd painel
npm ci
npx playwright install --with-deps chromium
npm run test:e2e
```

O teste abre Chromium com autenticador virtual, cadastra duas passkeys, pareia um celular simulado e verifica OAuth, passagem de chamadas, WebSocket, revogação e integridade do histórico. Ele cria um código inicial e um banco descartáveis para cada rodada. O resultado esperado é `Tudo certo`. No Linux com Chromium já instalado, também é possível usar `E2E_CHROMIUM=/usr/bin/chromium npm run test:e2e`. [Instalação do navegador de teste](https://playwright.dev/docs/browsers)

Para explorar a interface pelo navegador, crie `painel/.dev.vars` com `CODIGO_INICIAL` definido para um valor próprio de pelo menos 12 caracteres. Esse arquivo é ignorado pelo Git. Dentro de `painel/`, execute `npm run dev` e abra `http://localhost:8787`. O estado dessa instância fica em `painel/.wrangler/`. [Variáveis locais do Worker](https://developers.cloudflare.com/workers/local-development/environment-variables/)

## Usar uma conta e um aparelho próprios

1. **Se o objetivo é contribuir com código**, abra o clone no editor ou no Claude Code e execute o primeiro teste. No Claude Code em nuvem, o hook de sessão prepara Graphify e NumPy. A instalação de `testes/requirements.txt` também traz o SDK MCP e as dependências de assinatura usadas no teste completo.
2. **Instale o serviço no Android** com o procedimento do README. O instalador checa o emissor IR pelo Termux:API e monta o catálogo. Para exposição de tela e gestos, inicie o Shizuku, autorize o Termux e coloque os componentes `rish` e `rish_shizuku.dex` exportados por ele em `~/.controle-ir/rish/`. Confira `controle-ir status`. Para o atalho Stockfish, instale o motor com `pkg install stockfish`, use o Termux:Widget da mesma origem do Termux e permita **Sobrepor a outros apps** para o Termux se o atalho abrir e voltar à tela inicial. [Instalação e atalhos](README.md#instalação-uma-etapa-por-vez)
3. **Para hospedar a sua Central**, execute `npx wrangler login` e `npx wrangler whoami` em `painel/`. Confira a conta e o nome do Worker em `wrangler.jsonc`. Publique com `npm run deploy` e defina o segredo com `npx wrangler secret put CODIGO_INICIAL`. O projeto declara os bindings `DB`, `OAUTH_KV`, `CANAL` e `ASSETS`; o código inicializa as tabelas D1. A criação desses recursos depende das permissões da sua conta Cloudflare. [Configuração do Wrangler](https://developers.cloudflare.com/workers/wrangler/configuration/) · [Segredos do Worker](https://developers.cloudflare.com/workers/configuration/secrets/)
4. **Cadastre a primeira passkey** na URL HTTPS da sua Central com seu código inicial. Gere um código de pareamento na interface. No seu Termux, execute `controle-ir painel parear https://SEU-WORKER.workers.dev CODIGO` substituindo a URL e o código. Confira `controle-ir painel estado` e o aparelho na Central. Para permitir uma operação que exige armação, o dono usa a passkey na Central pareada. [Modelo de autorização](docs/seguranca.md)
5. **Conecte o cliente de chat** ao endereço HTTPS da Central seguido de `/mcp`, com OAuth. No ChatGPT, registre o app no espaço que permite apps de desenvolvimento e conclua a autorização na sua Central. No Claude Code, use `claude mcp add --transport http controle-geral https://SEU-WORKER.workers.dev/mcp` e abra `/mcp` para autenticar. No Claude web, use o conector remoto com o mesmo endereço. Valide com a ferramenta `consultar` e confira a versão do servidor e o estado do canal. [Integração no ChatGPT](https://developers.openai.com/plugins/deploy/connect-chatgpt) · [MCP no Claude Code](https://code.claude.com/docs/en/mcp)
6. **Para as missões com Sonnet**, configure uma chave própria da API Anthropic no Termux em `~/.controle-ir/anthropic.key`, com permissão `600`. O ID utilizado por esta versão está em `ambiente_missao.MODELO`. Confira o acesso a esse modelo na conta da API antes de medir. A conta do chat, a hospedagem da Central e o faturamento das chamadas ao modelo são configurações distintas. O motor Stockfish e o estudo de xadrez rodam no telefone. [Como as missões funcionam](docs/HANDOFF.md#missões-rotas-e-piloto)

Cada instalação gera suas próprias passkeys, pareamento e estado. As fichas em `docs/aparelhos/` registram o que foi observado na instalação de referência. Descubra e confirme os controles dos seus aparelhos antes de usar comandos físicos. Ao compartilhar diagnóstico, envie versão, código de estado e medidas de tempo. Mantenha tokens, chaves, URLs com segredo, capturas pessoais e o conteúdo de `~/.controle-ir/` fora de commits e PRs.

## Fluxo de contribuição

A branch padrão é `claude/ir-control-poco-setup-u46urr`. Para acompanhar uma eventual troca de padrão, consulte `git remote show origin`. Abra uma branch a partir da padrão atualizada, faça uma mudança por objetivo e inclua no PR o comportamento anterior, como reproduzir, qual teste passou e o que exigiu um aparelho real. Quem usa fork envia o PR à branch padrão deste repositório.

| Área da mudança | Arquivos de entrada |
|---|---|
| Protocolo ou transporte ChatGPT/Claude | `controle-ir/controle_ir/mcp.py`, `servidor.py`, `canal.py`, `painel/src/index.js` |
| Objetivo em linguagem natural, modelo e grafo | `controle-ir/controle_ir/ambiente_missao.py`, `missao.py`, `controle-ir/conhecimento/` |
| Navegação, leitura da tela, reflexos ou xadrez | `controle-ir/controle_ir/rotas.py`, `estudo_xadrez.py`, `controle-ir/capacidades/tela/` |
| Catálogo, protocolos e emissor | `controle-ir/controle_ir/catalogo.py`, `protocolos.py`, `emissor.py`, `controle-ir/LICENCAS/` |
| Nova capacidade | Diretório em `controle-ir/capacidades/` com manifesto e implementação. Acrescente teste e confira como aparece em `tools/list` e na política do aparelho. |

Antes de publicar mudanças em `controle-ir/`, ajuste a versão em `controle-ir/controle_ir/__init__.py` e adicione os fontes novos ao índice com `git add`. Se mudou o código representado no grafo ou uma skill, atualize também o contexto embarcado. A revisão usou `python -m pip install 'graphifyy[sql]==0.9.111'` no ambiente de desenvolvimento.

```bash
bash ferramentas/atualizar_conhecimento.sh
git add graphify-out controle-ir/conhecimento
```

O comando regenera o grafo **de código**, conserva o material semântico já existente e copia o grafo, as quatro skills e os avisos de origem disponíveis para o pacote do Android. `built_at_commit` identifica o checkout usado para gerar o grafo. O commit posterior que guarda o pacote pode ter outro SHA. A origem e os avisos dos dados IR estão em [LICENCAS](controle-ir/LICENCAS/LEIA-ME.md); os das skills acompanham as respectivas pastas. A escolha de uma licença geral para o projeto continua com o mantenedor.

O empacotador lê os arquivos rastreados pelo Git e seus modos. A verificação compara cada arquivo do ZIP com o checkout e confere o SHA-256.

```bash
bash ferramentas/empacotar.sh
bash ferramentas/empacotar.sh --verificar
git add dist/controle-ir.zip dist/controle-ir.zip.sha256
```

Nas branches `codex/**` deste repositório, o workflow de empacotamento também produz e grava esses arquivos depois de mudanças no serviço ou no conhecimento. Aguarde o commit gerado antes de escolher o SHA para instalar. Em um fork, o fluxo manual acima permite conferir e incluir a mesma distribuição no PR.

Para instalar uma revisão de trabalho, use o SHA completo do **commit que contém o ZIP** no repositório configurado no aparelho. Após a instalação, confira `consultar` e `controle-ir status`. O atalho **Reverter Controle IR** restaura a instalação anterior. O fluxo do Cloudflare para o Worker é separado da instalação do pacote no Termux. O PR roda verificações locais em GitHub Actions. [Arquitetura, evidências e próximos testes](docs/HANDOFF.md)
