# Diário da instalação de referência

A revisão de **21/11/2026** consolidou as entregas até o PR #21 na branch padrão, inclusive os PRs #19 e #20 pelo #18. Os números de versão e a lista de pendências de 19/11 abaixo descrevem aquela data. O estado do pacote, a história das missões, as medições de 20/11 e as próximas verificações estão no [guia de passagem](HANDOFF.md). Para saber o que está instalado no seu aparelho, consulte o serviço.

## 26/11 madrugada — missão do PC: tela azul, botão, otimização e ambiente

Registro completo, com benchmark, inventário e recomendações: `docs/entregas/2026-11-26-pc-windows.md` e
`docs/pc-windows.md` no repositório Roblox. Kit em `ferramentas/pc/` de lá.

- **Por que o PC saiu do ar às 23h:** tela azul 0xC2 (BAD_POOL_CALLER), causada pelo driver `zt9101d_drv.sys` do
  adaptador Wi-Fi USB genérico ZTOP, que estava plugado mas sem uso. O dispositivo foi desativado. Depois do
  reinício automático, o agente só voltou com o logon (00:01).
- **Botão "Ligar Agente PC"** na área de trabalho (agente pc-1.0.2, PR #30): liga o agente sem administrador e
  mostra se conectou. O `/saude` informa o canal.
- **Git no PC pelo login do `gh`** (`gh auth setup-git`): o gerenciador de credenciais do Windows falha no
  contexto do agente (tarefa agendada) e o repositório Roblox é privado.
- **O winget trava no contexto do agente** (download do WinINet parado). Node e Ollama vêm das fontes oficiais,
  com assinatura conferida.
- **Otimização (reversível):**
  - disco sempre ligado;
  - inicialização rápida desligada;
  - caminhos longos;
  - **Windows Update sem reinício com usuário logado**: havia um reinício pendente que derrubaria o agente
    entre 7h e 13h.
- **Ambiente:** Node 26.13.1, Rokit 1.2.0 (Rojo 7.7.1, StyLua 2.6.0, Lune 0.11.1) e `lune run verificar` ok no
  PC. Ollama e Studio: ver a entrega.
- **Canal:** uma queda "a Central fechou o canal" às 00:23:11, que voltou em 2 s sozinha.
- **Conexão fantasma (00:57 → 01:1x):** a internet do PC piscou (`getaddrinfo failed`) durante o download do
  Ollama. A conexão velha morreu sem fechar e ficou em CLOSING no Durable Object. O PC reconectou (o `agente.log`
  mostrava "canal conectado"), mas a Central pegava "a última" de `getWebSockets()`, que não tem ordem garantida e
  ainda inclui conexões em CLOSING. Resultado: "PC fora do ar" para toda chamada. A Central **2026-11-26.2**
  escolhe a conexão ABERTA com a batida mais recente (teste e2e "conexão fantasma"), e o deploy limpa as
  fantasmas.
- **Recomendações para o dono:**
  - cabo de rede (hoje só Wi-Fi USB, sinal 59%);
  - Avast (apareceu na pilha) ou exclusões;
  - reiniciar uma vez;
  - BIOS de 2022;
  - religar sozinho (BIOS e logon automático).

## 26/11 — PC Windows na Central (agente_pc) — PASSAGEM PARA A PRÓXIMA SESSÃO

**Estado (26/11 ~23:05):** PC pareado, armado e operado de ponta a ponta pelo conector Controle Geral.
`pc_consultar`, `pc_executar` (PowerShell como administrador) e `pc_tela` testados no Windows real.
Detalhes do agente: [pc.md](pc.md). PRs #26–#29.

**O PC (PcGiga):**

| Item | Valor |
|---|---|
| Sistema | Windows 11 (10.0.26200), usuário `felip`, placa-mãe H610M-HVS/M.2 R2.0 |
| CPU | i5-13400F (10 núcleos / 16 threads) |
| Memória | 32 GB |
| GPU | RTX 4060 Ti 8 GB (compute 8.9), driver 591.86, CUDA 13.1 |
| Disco | C: 953 GB, 498 GB livres |
| Agente | `%LOCALAPPDATA%\agente-pc`, porta local 47630, tarefa agendada "Agente PC - Central" |
| Central | `https://painel-casa.cauetakahashideoliveira.workers.dev`; `/versao` mostra a versão publicada (`2026-11-26.1`) |

- **Já instalado:** Git, GitHub CLI (logado), Python 3.12.10, Claude Code 2.1.332 (sem login: não é usado), winget.
- **Repositórios:** `C:\dev\dialogue-flow` e `C:\dev\roblox`, este na branch padrão (`9a2a399`). O trabalho do
  Winlator está no PR #2 do Roblox, ainda não mesclado.
- **Falta:** Node.js, rokit/rojo/lune/stylua, Roblox Studio, Ollama, VS Code. O WSL não está instalado.

**Como operar o PC:**
- Em conversa nova, use as ferramentas `pc_*`, se aparecerem na lista.
- Em conversa antiga, ou se não aparecerem, use `executar_capacidade(nome="pc_consultar"|"pc_executar"|…,
  argumentos={…})`: a Central encaminha ao PC (#28).
- O PC precisa estar **armado**: a Central arma todos os aparelhos juntos, por até 24 h, com a digital.

**Lições desta sessão:**
1. Com o serviço do celular parado, a Central caía no túnel ngrok morto (404) e o conector inteiro caía, nas conversas
   novas com erro 405. O #27 corrige isso. Se o celular cair: `controle-ir desligar; pkill ngrok; controle-ir ligar`
   no Termux. O Termux:Boot ainda não está instalado.
2. A cada deploy da Central, os canais caem. O celular voltou sozinho; o PC 1.0.0 não voltou, e foi preciso
   reiniciar a tarefa. A 1.0.1 (#29) reconecta em até 1 min, impede a suspensão do PC e registra quedas no
   `agente.log`.
3. A lista de ferramentas é fixa por conversa. As `pc_*` só aparecem em conversa aberta depois de o PC estar
   conectado; antes disso, use a ponte do item acima.

**Próximo passo (aprovado em proposta, não começado):**
1. Ambiente Roblox no PC:
   - Node LTS e rokit, depois `rokit install` em `C:\dev\roblox`;
   - Roblox Studio (o dono faz o login da conta uma vez);
   - `rojo plugin install` e o MCP do Studio;
   - teste bridge-01 → bridge-02 (`/rbx-studio-check`).
2. IA local: Ollama com `qwen2.5-coder:7b` (cabe nos 8 GB de VRAM), servindo os agentes e o `/god-mode`.
3. Fechar o WhatsApp Web antes de usar `pc_tela`/`pc_entrada` (a tela é capturada inteira).

## 23/11 — agente de tela: visão em páginas web, resposta, grafo de telas e vigias (1.0.102)

**Teste real que motivou (POCO, Chrome):** objetivo "pesquisar a cotação do dólar e ler o valor".
- A navegação funcionou (abrir, digitar, pesquisar em < 2 s), mas a página de resultado chega à acessibilidade como
  **um nó só, "Visualização na Web", sem texto**. O executor ficou cego: rolou, voltou e parou com "preciso do
  Claude", com **US$ 1 = R$ 5,99** visível na captura.
- Falso "concluído": `concluido={qualquer:["Real"]}` casou com a **sugestão** "cotação do dólar hoje em real", antes de
  o resultado abrir.

**Aplicado (`capacidades/tela/objetivo.py`, `principal.py`, `vigia.py`):**
- **Visão automática:** área que a acessibilidade não descreve (WebView sem texto dentro, ou as `regioes_visuais`)
  → a captura (720 px) vai ao modelo de visão do nível (`forte` = Opus), que responde `feito`/`resposta` ou o próximo
  passo (tocar x,y da imagem → convertido para a tela, opção pelo número, rolar, voltar). Segurança: toque por
  coordenada só dentro da área cega e com o rótulo passando pela lista de efeitos externos; a página é dado, nunca
  ordem (na política do modelo). Até 8 olhadas por chamada. Rolar funciona na página (gesto na área cega) e a
  assinatura da tela soma um resumo da imagem (senão rolar parecia "sem efeito").
- **Conclusão pelo modelo e resposta:** `concluido` virou opcional (sem ele, o modelo julga) e `pergunta='...'` devolve
  `resposta` lida da tela final (texto pelo Sonnet; imagem pelo modelo do nível). Na decisão por texto o modelo tem a
  opção "✓ objetivo cumprido", conferida pela leitura. O texto digitado e as sugestões que começam com ele não
  concluem mais.
- **Grafo de telas** (`~/.controle-ir/tela/grafo_telas.json`): nó = tela, aresta = toque/rolagem → tela seguinte, e o
  destino de cada objetivo cumprido. Objetivo igual ou parecido (≥ 60% das palavras) acha o caminho por busca em
  largura a partir da tela atual, sem modelo (`via: "grafo"`). `acao=grafo` mostra o resumo.
- **Vigias** (missões de horas): `acao=vigiar, vigia={nome, objetivo, app, pergunta, a_cada (min), condicao:
  muda|abaixo|acima|contem|variacao, duracao (h), quando}` faz a 1ª leitura na hora e depois roda sozinho numa
  thread do serviço, avisando por notificação com som. Só lê (sem `permitir`), adia com a tela apagada ou o dono em
  outro app (modo `livre`), pausa com travar, sobrevive a reiniciar o serviço. Limites: 10 vigias, 5 min–24 h, até 72 h.
- Descrição da ferramenta: o conector só mostra os primeiros **800 caracteres** de cada `cap_*`; o começo da
  descrição da tela agora traz objetivo/pergunta/visão/vigiar.
- **1.0.103 (1º teste real da 1.0.102):** a visão não entrou na página de resultado (o modelo de texto rolou e
  parou). Correções: a área cega conta só os textos do PRÓPRIO app (as teclas do teclado aberto por cima, outro
  pacote, faziam a página parecer descrita), captura reserva pelo `screencap` e `visao_diag` no resultado
  (telas cegas, capturas que falharam, erro do modelo, página descrita e por quem).
- **1.0.104:** o diagnóstico mostrou a causa real — `web_descrita: textos_do_app 5, outros_apps []`: a **barra do
  Chrome** (início, endereço, nova guia, guias, menu) fica desenhada por cima da página, na mesma área, e os 5 botões
  contavam como texto da página (a visão só entrava depois de a rolagem esconder a barra). Agora a área cega vem da
  ÁRVORE da tela (`principal.regioes_web`): só contam descendentes do nó da página; uma lista que cobre ≥ 40% da página
  (sugestões da busca, diálogo) continua sendo lida pelo texto. Teste no POCO com a 1.0.103: "1 dólar americano =
  5,99 reais (conversor do Google)", concluído pela visão em 14,6 s (3 consultas, 1 olhada).
- **1.0.105:** a árvore real do Chrome (`acao=arvore`, nova: o `uiautomator dump` volta vazio com o leitor ligado)
  mostrou a página como `FrameLayout (Visualização na Web)` sem filhos com texto e a barra (`#control_container`)
  como IRMÃ dela. Na guia nova a visão queria buscar de novo: agora pode pedir `digitar` (o mesmo texto autorizado,
  uma vez a mais), e o diagnóstico traz as respostas recusadas. Teste no POCO partindo de um artigo de notícia:
  digitar → rolar (visão) → concluir (visão) em **7,5 s**, resposta "1 dólar ≈ R$ 6,00 (conversor do Google;
  Investing.com cita 5,9575)".
- **1.0.106:** `url=` abre o endereço direto no app (o caminho não depende de onde o app parou; ideal para vigias)
  e a visão pode rolar para cima (a barra de endereço some quando a página é rolada).
- **1.0.107:** o objetivo devolve `valor` (o número que responde à pergunta, separado pelo modelo): "1 dólar ≈
  R$ 6,00" fazia o vigia ler 1. Teste com `url`: abrir endereço → rolar para cima (visão) → concluir em **9,2 s**,
  "1 dólar americano = 5,99 reais (23 de nov., 18:03 UTC, Morningstar)", `valor: 5.99`. Grafo: 7 telas do Chrome,
  3 objetivos.
- **1.0.108:** o endereço reabre na MESMA guia do Chrome (`com.android.browser.application_id`); antes, cada
  leitura abria uma guia nova. Conferido no POCO: 4 guias → 5 na 1ª leitura com a identificação → 5 na 2ª. Duas
  leituras seguidas pelo endereço: 7,4 s e 7,9 s, `valor: 5.99` nas duas.
- **Vigia ainda não rodou sozinho no POCO:** o vigia "dolar" (30 min, variação ≥ 1%, 3 h) nasceu **pausado**
  porque existe `~/.controle-ir/PARAR`. Esse arquivo é gravado em todo travar (e no desarmar pela Central) e só é
  apagado ao armar pelo terminal sem pareamento (`cli.py`); `destravar` não o remove. Num celular pareado ele fica
  para sempre e também para os laços do termômetro e do sono. Uma mudança para comparar a hora do travar com a do
  vigia foi recusada nesta sessão por mexer no freio — decisão do dono. Para rodar: o dono apaga o arquivo no
  Termux (`rm ~/.controle-ir/PARAR`) e pede `vigia={nome:"dolar", retomar:true}`.

## 22/11 — ar condicionado quarto 2 (Brastemp Clean)
- Servidor no POCO: **1.0.101** (canal direto conectado). O conector caiu duas vezes com "Not Found" e voltou
  depois de religar o serviço no celular.
- Novo aparelho `ar condicionado quarto 2`: split Brastemp Clean BBV09BBBNA. Apesar da etiqueta Whirlpool, ele
  **só responde ao protocolo TCL112**: os perfis Consul/Whirlpool não tiveram efeito. Foi identificado com o
  ar ligado e uma busca de códigos "desligar" (candidato 33, TCL TAC-12CHSD). O perfil completo, nº 9524, foi
  gerado por `ferramentas/tcl112.py` (640 estados com oscilação) e importado no celular. Detalhes na
  [ficha](aparelhos/quarto-2/ar-condicionado-quarto-2.md).
- Diagnóstico útil: `rish -c 'logcat -d -s ConsumerIrHal'` mostra cada transmissão (`Send to driver: Enter/Exit`
  e a duração). O `sinal_enviado` da API não garante que o emissor transmitiu; o log, sim.
- Pendente: mapear turbo, apagar painel, dormir e renovar do controle Brastemp Clean.

## 22/11 — rodada ponta a ponta: agir primeiro e modo reunião (1.0.99 `0389999` → 1.0.101)

**Onde o tempo se perdia (medido):**
- **Comando conhecido** ("desliga o ar do quarto"): o Claude Code lê só os primeiros **4096 caracteres** das
  instruções do conector, e o resumo dos aparelhos ficava depois dos ~7.900 de regras. Nenhum modelo via os
  aparelhos e as descrições ainda pediam "use primeiro" (`consultar`) e "consulte antes de controlar" (`opcoes`).
  - Antes: `opcoes` (14 ms no celular) → `controlar` (1.168 ms no celular), **5,7 s** do pedido ao fim do envio,
    com 1 chamada e 1 turno de modelo a mais (no claude.ai, quase sempre 2: `consultar` de 12,9 KB + `opcoes`).
  - Dentro do celular, o `controlar` simulado leva 15 ms; o resto é emissão. O `termux-infrared-transmit` custa
    ~0,3 s (medido com pulso de 1 ms) e o `service call consumer_ir` pelo Shizuku também transmite (Parcel 0), mas o
    ganho seria ~0,2 s. Fica anotado, sem troca de emissor por agora.
- **Controle novo** (modo reunião), feito à mão pelo terminal: 4 comandos e ~154 s até o ciclo funcionar, sem nada
  reutilizável (sem guardar, sem restaurar, sem atalho).
  - O teste que separou as causas: `cmd media_session volume --set` pelo shell é **ignorado** no HyperOS (nem 0
    nem 2 pegam: não é regra do volume zero, é o caminho); `termux-volume` escreve; `cmd audio set-ringer-mode
    VIBRATE/NORMAL` pelo Shizuku muda o toque e, ao voltar ao normal, o volume do toque (1/17) volta sozinho.

**Aplicado:**
- `mcp.py`: TOPO "AJA PRIMEIRO" → aparelhos → modos → REGRAS essenciais (segurança inclusa) dentro de `VISIVEL`
  (4060). Com muitos aparelhos, o resumo encolhe (teclas 20 → 8 → compacto → só nomes) sem cortar nenhum nome.
  `controlar` traz os nomes salvos na própria descrição; `consultar`/`opcoes` não mandam mais chamar antes.
- Capacidade **`modos`** (embutida, em processo): `entrar|sair|alternar|estado|listar|definir|testar|atalho|remover`.
  - Guarda o estado antes de mexer, aplica, confere pela leitura e restaura.
  - Aprende o método que funcionou e as condições (`android_sdk`, `shizuku`) em `~/.controle-ir/modos/aprendido.json`.
    Um método que falhou nas mesmas condições não é tentado de novo; se a condição muda, revalida.
  - Shizuku parado conta como condição, não como defeito. Correções do usuário (`definir` num modo existente)
    ficam registradas como antes/depois e invalidam a validação até um novo `testar`.
  - Plano B sem Shizuku: silencia pelos volumes (sem vibrar) e avisa. O `testar` grava a validação e cria o
    atalho "Modo reuniao (liga-desliga)" no Termux:Widget.
- **1º `testar` real (1.0.99):** validou pelo plano B. O diagnóstico apontou "o toque não mudou", mas um teste
  separou a causa: o `settings get global mode_ringer` só reflete a mudança na 3ª leitura (~0,6 s), e a 1.0.99
  lia com 0,3 s. Era atraso de leitura, não recusa. **1.0.100:** relê por até ~2,5 s; `versao_metodos` entra nas
  condições, para o falso negativo aprendido com o código antigo ser revalidado sozinho.
- **Resultado (1.0.100 no POCO):**

  | Medida | Antes | Depois |
  |---|---|---|
  | Comando conhecido: chamadas até o envio | 2 (`opcoes` + `controlar`; no claude.ai, 3) | 1 (`controlar`) |
  | Comando conhecido: pedido entendido → "sinal enviado" | 5,71 s | 1,23 s |
  | Modo reunião: até o controle funcionar | ~154 s, 4 comandos, nada reutilizável | 3,47 s, 1 chamada (`modos testar`), validado e com atalho |
  | Modo reunião: uso depois de criado | — | entrar 1,55 s, sair 1,31 s (2 e 6 chamadas ao Android); widget 1,6 s / 1,7 s |
  | Intervenções do dono | 0 (ar), 0 (modo) | 0 e 0 |

  As instruções reais, montadas no celular com os 4 aparelhos, têm 7.396 caracteres. Os primeiros 4.096 trazem
  os 4 nomes, as faixas de valores, `x_luz`, o modo reunião e as regras de segurança inteiras.
- Testes: `testes/test_modos.py` (13, celular falso que imita o POCO, inclusive o atraso) e
  `test_instrucoes_poem_aparelhos_e_regras_no_trecho_lido`. 271 testes OK.

## 21/11 — nível e tempo do Stockfish no Termux

O POCO recebeu a versão 1.0.72.1 pelo pacote `9e59cdb`. Com o Stockfish 19, o botão abriu no nível 0
e sugeriu `c2c4` com 50 ms. Após `e2e4`, o comando `configurar` mudou o nível para 17 e o tempo para
250 ms. O motor recebeu `setoption name Skill Level value 17` e `go movetime 250` e respondeu `e7e5`.
Ao reabrir pelo terminal, o estudo recuperou os dois valores. O ensaio usou uma pasta temporária de
preferências. A configuração pessoal conferida ao final foi nível 20 e tempo automático.

## 21/11 — atualização e correções (branch `ccr-201914aa-m2jj33`)
- **POCO:** 1.0.64 → 1.0.65 (`80ca80d`) → 1.0.66 (`944f71c`) → 1.0.67 (`f55b4ef`) → 1.0.68 (`42ff118`) → 1.0.69 (`a17970f`) → 1.0.70 (`9af8695`) → 1.0.71 (`d8ed2bc`) → 1.0.72 (`a2bf6f4`) → 1.0.72.1 (Stockfish, `9e59cdb`) → 1.0.74 (`2da4d0d`, junção com o Stockfish) → **1.0.75** pelo `atualizar_sistema`. O canal
  direto voltou sozinho a cada reinício; aparelhos, catálogo e política ficaram preservados. Conferido com `consultar`
  e com uma missão de leitura (Sonnet, grafo de 1.858 nós). Pareado, armado até a meia-noite, modo autônomo.
- **Android 16:** o Termux não lê `/proc/uptime` nem `/proc/loadavg` (`Permission denied`); o `CLOCK_BOOTTIME`
  funciona e o Python do Termux não tem `os.getloadavg`. O `estado_celular` usa o relógio de boot (98,6 h ligado em
  21/11) e devolve `carga_cpu_1min: null` quando não há leitura (antes saía 0, que parecia processador ocioso).
- **`consultar`:** o perfil misto do “ar do quarto” repetia `modo` (teclas + estado completo); corrigido.
- **Pacote × cache do Python:** o ZIP grava a data fixa de 1980; com um fonte novo do mesmo tamanho o `.pyc` antigo era
  reaproveitado (a 1.0.66 rodou o código novo informando 1.0.65). Desde a 1.0.67 o `instalar.sh` apaga os
  `__pycache__` antes de religar.
- **Testes:** `testes/test_consistencia.py` (listas de risco iguais no celular e na Central, ferramentas da missão,
  resumo, estado do celular, cache na atualização) e `testes/test_capacidades_aparelho.py` (download, termômetro,
  sonar, varredura sem Wi-Fi) e `testes/test_bluetooth.py`: 214 testes Python no total.
- **Checagem completa (1.0.68 `42ff118` → 1.0.69 `a17970f`):** canal direto, emissor (pulso neutro e TV volume +1/−1:
  `sinal_enviado`), os 4 aparelhos (`opcoes` e plano simulado), tela (ler, abrir Configurações, voltar ao início),
  câmera, microfone, sono, missão e rede funcionando. Encontrado e corrigido:
  - `diagnostico_rede`: download voltava HTTP 403 (a Cloudflare recusa o urllib sem User-Agent) → User-Agent próprio e
    OVH de reserva (28 Mbps medidos); a perda até a internet vale pelo melhor de 1.1.1.1 e 8.8.8.8.
  - `termometro`: uma leitura do Termux:API passou de 15 s com outra chamada em andamento e derrubava a medição →
    vira amostra ausente. Chamadas ao Termux:API em paralelo travam; rode uma por vez.
  - `sonar`: no POCO 19 e 18 kHz não chegam ao microfone; 17 kHz chega com ~98 dB de folga. Sem frequência pedida ele
    desce até a que funciona e lembra dela (`~/.controle-ir/medicoes/sonar.json`). O 1º segundo marcava movimento
    falso (gravação começa antes do tom) e a referência pela mediana sumia com movimento longo → percentil 10 dos
    quadros com tom.
- **Teste de uso real (WhatsApp):** o agente de tela abriu o WhatsApp, entrou pela Nova conversa no contato
  “(Você) · Mensagens para mim” e mandou uma mensagem para o próprio dono. A 1ª saiu “MensagemTeste do Claude…”: o
  campo vazio do WhatsApp expõe a dica “Mensagem” como texto e o leitor (`Tela.java`) somava ao digitado. Na 1.0.70 a
  dica é reconhecida também pela dica declarada e pela falta de cursor; a 2ª mensagem saiu exata (10:59), digitada
  pelo leitor recompilado. A trava “coordenada só vale na tela lida” barrou dois toques depois de a tela mudar
  (teclado abrindo), como deve.
- **Varredura fora de casa (1.0.71):** com o Wi-Fi desligado o Termux:API informa o IP `0.0.0.0`; o
  `descobrir_rede` varria a “sub-rede 0.0.0” e gravava o resultado por cima do inventário de casa (os 10 aparelhos
  de 192.168.5 viraram “sumidos”). Agora ele recusa sem Wi-Fi e guarda um inventário por sub-rede
  (`{"redes": {...}}`, lê o formato antigo). O inventário de casa se refaz na próxima varredura em casa.
- **Capacidade nova `bluetooth` (1.0.72):** o Termux:API não tem Bluetooth e o `bluetoothctl` não acha o
  adaptador no Android. O leitor `capacidades/bluetooth/java/controleir/Bluetooth.java` roda como shell pelo
  Shizuku (`app_process`, com a identidade `com.android.shell` para passar nas permissões do Android 12+), só
  ESCUTA a busca BLE (nunca conecta nem pareia) e lista os pareados; com o Bluetooth desligado tenta o modo só BLE
  e desfaz no fim (`ligar=true` liga de verdade só durante a busca, por `cmd bluetooth_manager`). O Python
  classifica pelo nome, fabricante (ID da Bluetooth SIG, anúncio Continuity da Apple) e serviços, e estima a
  distância pelo sinal. Testada aqui contra imitações do Android (`testes/android_stub/`, `testes/test_bluetooth.py`);
  **No POCO (1.0.73–1.0.74):** o `app_process` precisa registrar o serviço do Bluetooth (`ActivityThread.initializeMainlineModules`,
  senão o adaptador vem nulo); estado e pareados funcionam (Honda HFT e AirPods Pro). A **busca é recusada pelo
  HyperOS**: `BtGatt.ScanController: MIUI PERMISSION DENIED: com.android.shell`. Lido no `Bluetooth.apk` (dexdump):
  `ScanController.checkAllowedToScan` libera apps comuns (uid ≥ 10000), mas pacotes do sistema só com tela própria
  em primeiro plano ou serviço em primeiro plano declarado — o Shell não tem nenhum dos dois. Pacote vazio passa
  na regra e quebra adiante (NullPointerException no serviço); `MIUIOP(10053)` não muda nada (testado e
  revertido). A capacidade devolve `busca: bloqueada_hyperos` e, do registro do sistema, os sinais que as buscas
  do próprio sistema captam (fim do endereço e força, sem nome).
- **App auxiliar `Controle IR Bluetooth` (1.0.75):** `br.controleir.bluetooth`, montado aqui com o build-tools 35
  (`ferramentas/construir_app_bluetooth.sh`; chave fora do repositório; `fontes.sha256` + teste acusam APK velho).
  Uma janela de diálogo (`Busca`, só abre com a permissão DUMP, ou seja, pelo shell) escuta a busca BLE como app
  comum — que o HyperOS aceita — e grava o JSON em `Android/data/br.controleir.bluetooth/files`. `modo=auto`
  instala/atualiza pelo shell, dá BLUETOOTH_SCAN/CONNECT (`neverForLocation`: sem localização) e cai no shell se
  não der. O analisador do próprio Android leu o APK (`getPackageArchiveInfo`: ok). **Instalar pelo shell exige
  “Instalar via USB”** (`INSTALL_FAILED_USER_RESTRICTED`); pelo instalador do Android, o arquivo vindo do Termux,
  da pasta Downloads ou do app Arquivos dava “problema ao analisar o pacote” (entrega do arquivo, não o APK).
- **Otimização Cloud ↔ Android, ciclo 1 (1.0.76–1.0.78):**
  - *Medido* (POCO em dados móveis): turno do modelo sozinho ~2,3 s; chamada ao conector fora do celular ~0,5–0,6 s
    (cliente + Central + canal, 2 amostras); WebSocket do canal ida e volta mediana 157 ms (p95 213, n=4); dentro
    do celular: `ver` só árvore 0,15–0,17 s, `tocar` 0,85–1,3 s, `abrir` 0,9–1,2 s. Resposta com imagem 64–82 KB
    contra 1–5 KB só texto. Gargalo = **turnos da nuvem por ação** (~80% do tempo no passo a passo).
  - *Telemetria* (1.0.76): `consultar → servidor.canal.desempenho` (ms dentro do celular por chamada, só o nome da
    ferramenta; RTT do canal medido na hora se houver poucas amostras).
  - *Imagem desnecessária* (1.0.77): `regioes_visuais` contava contêiner vazio de lista como "área visual" e anexava
    captura nas Configurações; agora só área que a acessibilidade não descreve (≥ 3 textos dentro = descrita).
  - *Executor de objetivos* (`tela/objetivo.py`, `acao=objetivo`, 1.0.77): laço perceber→decidir (pistas → memória
    → digitar → modelo do celular → rolar) → agir → conferir no aparelho; erro transitório tenta 1× de novo, depois
    alternativa; tela repetida/limite/prazo param; rótulos de efeito externo só com `permitir`; devolve passos e os
    textos da tela final. 1.0.78: cortina do sistema é recolhida com `cmd statusbar collapse` (o "voltar" injetado
    não fecha no HyperOS — achado no teste real) e texto de outra janela (notificações) nunca volta à nuvem
    (o 1º teste real devolveu texto da cortina: corrigido e coberto por teste).
  - *Incidente* (1.0.78, T5+T6): a pista "Opções do desenvolvedor" foi tocada de novo dentro da tela de opções do
    desenvolvedor, onde o mesmo rótulo é o **interruptor geral** → desligou o modo de desenvolvedor, a depuração sem
    fio e o Shizuku. 1.0.79: cada pista vale uma vez e interruptores (marcáveis, ou linha com marcável ao lado)
    nunca são tocados sem `permitir` — nem por pista, memória, modelo ou "dispensar"; teste reproduz o caso.
    Religar: Sobre o telefone → tocar 7× na versão do OS → Opções do desenvolvedor → Depuração sem fio → Shizuku.
  - *Resultados reais* (mesmo estado inicial, Configurações encerrado): T1 Bluetooth passo a passo 19,3 s / 4
    chamadas / 2 imagens → `sequencia` 9,6 s / 1 / 0 → `objetivo` 7,4 s / 1 / 0 (−62%); T2 versão do Android passo
    a passo 10,6 s / 2 / 0 → `objetivo` 7,3 s / 1 / 0 (−31%), resposta já no resultado. T5+T6 (cortina por cima +
    alvo abaixo da dobra): 1ª tentativa falhou (ver acima); a repetição com a 1.0.78 parou porque o Shizuku caiu
    ("Server is not running") — **refazer T5–T8 e T12 com o Shizuku de pé**. Simulados (`testes/test_objetivo.py`):
    pista, modelo + memória, abrir, notificação, cortina, rolar, toque transitório/estrutural, diálogo, proibidos,
    laço, digitar, app bloqueado.
- **Otimização, ciclo 2 (1.0.79–1.0.84), testes reais no POCO** (tempos "no celular" = dentro do aparelho; "total" =
  relógio do container incluindo turnos do Claude):
  - T5 cortina por cima → recolhe e segue: 8,1 s total (2,25 s no celular). T6 alvo abaixo da dobra → rola e acha
    (4,5 s; o passo de rolar levou 3,4 s esperando a lista assentar: próximo alvo). T7 app lento (Play Store fria):
    a 1.0.79 deu **falso sucesso** (apertou voltar no app anterior e o "Pesquisar" da tela inicial "concluiu") →
    1.0.80 espera o app (1,7 s) e só conclui dentro dele: 2,3 s. T8 toque sem efeito → 2 tentativas e alternativa:
    2,1 s. T2 sem pistas (modelo do celular): 1.0.80 falhou (o modelo só via rolar/voltar: o título não é clicável,
    a linha é; e o cérebro lê 1 dígito) → 1.0.81 acerta com 1 consulta (3,3 s) e, aprendido, 1,4 s sem modelo.
    T4 WhatsApp (ler a conversa Você, sem enviar): ciclo chat↔informações (1.0.81) → corte de ciclo e busca/Meta
    AI fora das opções (1.0.82); desvio por outra conversa aprendido como rota → memória só do caminho certo e
    pista fora da tela é procurada antes do modelo (1.0.83–1.0.84): 3,2 s, 0 consultas, "Enviar" nunca tocado.
  - T12 composto (versão, armazenamento, bateria, rede): passo a passo 13,3 s / 3 chamadas → objetivo +
    estado_celular num lote 6,4 s (−52%). T10/T11: o cliente do Claude executa as chamadas de um lote **em série**
    (B começou 0,74 s depois de A): paralelismo real só dentro do celular; cada chamada extra num lote ~0,7 s.
  - Queda do conector ("Not Found") por ~1–2 min durante o ciclo, voltou sozinha.
- **Otimização, ciclo 3 (1.0.85–1.0.95): cérebros fortes no celular.** O dono pediu inteligência acima de
  economia. Escada `cerebro` no objetivo: rapido (Haiku) | padrao (Haiku+Sonnet) | **forte (Sonnet+Opus, padrão)** |
  maximo (Opus pensando); sobe um degrau sozinho em tela que já falhou/repetiu; o modelo recebe a tela inteira e o
  histórico. Medido no POCO (1 decisão cada, mesma tarefa, todos acertaram): Haiku 1.460 ms, Sonnet 1.552 ms, Opus
  1.675 ms, Opus pensando 1.885 ms — o Opus custa ~0,2 s a mais por decisão (conexões abertas, resposta no 1º
  dígito). Teste difícil (informações do WhatsApp nas Configurações, sem pistas): revelou e corrigiu — Configurações
  → "Apps" abre OUTRO pacote (com.miui.securitycenter: app aberto por toque nosso faz parte do caminho, inclusive se
  abrir devagar); o cliente do Claude **corta chamadas aos 60 s** (o objetivo terminou em 72 s no celular e o
  resultado se perdeu → prazo ≤ 50 s, `acao=objetivo_resultado` recupera o último); rolar lista longa custa ~3–5 s
  por tela e o modelo era consultado a cada uma (rolagem contínua sem consulta); digitou 8× (uma vez por objetivo);
  pista "Apps" casou com "Atualização de apps…" (pista só exato/início); "Pesquisar apps" é botão que abre o campo;
  pista casava com o próprio campo digitado. Forçar parada/limpar/desativar/desligar entram nos proibidos. Final:
  com `pistas` + `digitar:{texto, depois_de}` o caminho completo sai em **7,5 s, 0 consultas** (antes: 72 s e
  falha); sem pistas, o Opus resolveu sozinho um impasse escolhendo o tamanho do app na mesma linha.
- **Piloto com visão + delegação (22/11, 1.0.96–1.0.97, `d0ce4c3`):** Mental Math Master
  (`com.fivedaysweekend.math`) desenha a conta como imagem; o piloto agora recorta a caixa da pergunta, um modelo de
  visão chamado DO celular (Sonnet) transcreve, o celular calcula (sem eval) e toca; `continuar` aperta ▶ do nível
  no fim da rodada. 1.0.96 confundia o botão "Parar Cronômetro (10)" com a pergunta (1.0.97 corrige; não instalada
  ainda: o conector caiu com erro 405 do lado do claude.ai). **Pendente:** `atualizar_sistema(d0ce4c3…)` e iniciar
  `tela acao=piloto iniciar={modo:"quiz", app:"com.fivedaysweekend.math", visao:true, modelo_visao:
  "claude-sonnet-5-5", continuar:[{se:"Pontuação Total", tocar:[900,1244]}], continuar_apos:1.2, duracao:3600}`.
  Regra de delegação ("QUEM FAZ O QUÊ") gravada nas instruções do conector e no CLAUDE.md, após cobrança do dono.
- **Achados sem correção pelo conector:** Termux:Boot não instalado (o início automático fica desligado: instale-o do
  F-Droid, abra uma vez e rode `controle-ir inicio-automatico sim` no Termux); no celular só há os modelos Qwen2.5
  1.5B (o 3B do guia de passagem não está lá); `controle-ir painel …` é recusado pelo conector por ser administrativo
  (de propósito). Rede: Wi-Fi 5 GHz em −68 a −72 dBm, ~23–31 ms até o roteador, 10 aparelhos na rede local (2
  prováveis câmeras IP); túnel de reserva da Central respondendo (HTTP 405 a um GET, como esperado).
- **Pendente (decisão do dono):** merge na branch padrão. Até lá, a linha de instalação do README baixa a 1.0.65.

## Resumo (fim do dia 19/11)
- **Celular:** POCO X8 Pro Max, HyperOS 3 (Android 16), Termux + Termux:API (F-Droid). Servidor **1.0.28**, pareado com a
  Central de Controle (só o painel arma, com a digital do POCO ou do iPad), ligado o tempo todo. **Modo autônomo** ligado (só o celular muda o modo; o freio é o atalho "Travar
  Controle IR").
- Emissor IR confirmado: 30, 33, 36, 38, 40 e 56 kHz. Catálogo: base + ampliado (Flipper-IRDB completa) = 9.380
  perfis, 94.407 sinais únicos, 1.776 marcas. (Termux precisou de `apt update && apt full-upgrade` no início.)
- **Capacidades instaladas:** estado_celular, diagnostico_rede, descobrir_rede, ouvir_bipe (+ `controlar(ouvir=true)`),
  foto (com recorte por alvo), termometro, tela, sono e sonar (sono e sonar ainda sem teste no aparelho).
- **Shizuku** 13.x por depuração sem fio, `rish` em `~/.controle-ir/rish/`, "Depuração USB (Configurações de
  segurança)" ligada (`persist.security.adbinput=1`). Tela **completa desde a 1.0.22**: ver, abrir, tocar, deslizar.
  Depois de reiniciar o celular, tocar em Iniciar no Shizuku de novo. Se o usuário voltar para o chat no meio de uma
  navegação, o gesto cai no app do Claude: para sequências, um único `executar_comando` (am start → dump → tap) é
  mais seguro, conferindo o pacote em primeiro plano antes de tocar.
- **Bateria (tela da Xiaomi, 19/11):** saúde **100%**, 4 ciclos, fabricada em jul/2026, primeiro uso nov/2026;
  **Carregamento inteligente ligado**, **Proteção da bateria (limite fixo de 80%) desligada**. O usuário decidiu
  manter a bateria entre 20% e 80%. Modo de energia atual: "Ultimate".
- **Pacotes no Termux:** numpy 2.5.5, ffmpeg 9.0.2, nmap 7.993. Espelho de pacotes: oficial
  `packages-cf.termux.dev` (cópia do antigo em `~/.controle-ir/sources.list.antes`).
- **Permissões do Android dadas:** microfone e câmera do Termux:API.
- **Central da Casa 2.0:** artefato privado https://claude.ai/artifact/XSh6ivS8Cc6BsKakes2pCh (fonte
  `artefatos/central-da-casa.html`), com o Gênio que controla, programa o celular, cria painéis, lembra e aprende.
- **Conector:** os pedidos de aprovação vêm da regra da organização no claude.ai (`org_ask_ceiling`), não do
  projeto nem do celular. O usuário liberou em 19/11; conferir numa conversa nova.
- **Repositório:** a branch padrão é `claude/ir-control-poco-setup-u46urr` (não existe `main`). O trabalho de 19/11
  está na branch `ccr-045ba202-fbl2x4` (bem à frente da padrão). 113 testes (com os 18 da god-mode). PR #5 (hook que instala o
  graphify e o numpy nas sessões na nuvem) aberto contra a padrão.

## Pendências anotadas em 19/11
1. **Agente de tela:** usar pelo Gênio; ideia: `abrir` aceitar intent (ex.: `android.intent.action.POWER_USAGE_SUMMARY`
   abre a Bateria direto) e uma ação de sequência que confere o app em primeiro plano antes de cada toque.
2. **Testar sono e sonar** (instalados na 1.0.20): o sonar parado e mexendo o braço; uma noite do laboratório do sono.
3. **Autorizações:** numa conversa nova, rodar algo simples no celular e ver se ainda pede aprovação.
4. **Termômetro:** calibrar com uma temperatura real. **Ouvido do ar:** testar ligar/desligar de verdade (pedir
   antes de desligar o ar). O Gree do quarto não deu bipe audível em 3 tentativas.
5. **Visor do ar:** foto de perto (1–1,5 m), guardar o recorte com `alvo="ar do quarto"`; depois ler os dígitos
   (7 segmentos) para confirmar sozinho.
6. PR do resto da branch para a padrão: o usuário dispensou por ora em 19/11 (conversas novas começam pela padrão,
   que ainda está na 1.0.14). O PR #5 (hook do graphify) espera o merge dele.
7. Ideias registradas em `docs/modo-deus.md` → "Novas frentes (pesquisa de 19/11)", para quando o usuário quiser.

## Histórico de 19/11 (mais recente primeiro)
- **20/11 — Passagem de bastão (1.0.63):** guia `docs/HANDOFF.md` (arquitetura, publicação, credenciais sem valores,
  o que existe só no celular e como recriar, migração para outro repositório). Repositório das atualizações
  configurável no celular (`~/.controle-ir/repositorio` ou `CONTROLE_IR_REPO`; padrão: este repositório).
  Varredura de segredos em arquivos e em todo o histórico: nada encontrado. Branch de trabalho juntada à principal.
- **20/11 — Teste final: vitória contra o "Máximo" (3200) no bullet 1 min (1.0.62):** motor com 7 threads, hash
  256 MB, 0,4 s/lance até o 30º, 0,2 s até o 50º, 0,1 s depois. **Vitória por xeque-mate em 65 lances**, mediana
  0,62 s/lance (p95 0,76 s); avaliação do app: 39 "Melhor", 14 "Ótimo", 1 "Excelente". Para chegar ao Máximo:
  "Jogar com Bots" → fim da lista → bloco "Engine" → arrastar o controle do topo até o fim ("Máximo 3200").
- **20/11 — Piloto no xadrez contra robôs (1.0.61):** modo `xadrez` (Stockfish 19 residente do `pkg`, `ms_lance`
  200–300): lê o tabuleiro pela acessibilidade, percebe a vez pela peça que se mexeu, confirma o lance. Trava:
  só com a atividade de partida contra robô em primeiro plano (`partida_contra_robo`; para sozinho ao sair).
  Resultados: blitz 3+2 contra o Intermediário 1200 — vitória por mate, 20 lances, mediana 0,63 s/lance,
  precisão 99,7%; **bullet 1 min contra Rey Enigma 2500 — vitória por xeque-mate**, 32 lances, mediana 0,50 s
  (p95 0,82 s), avaliação do app: 13 "Melhor", 3 "Brilhante", 1 "Excelente". Caminho no app: Início → Jogar →
  "Jogar com Bots" (NUNCA "Começar Partida": é contra pessoas). A lista de acessibilidade do seletor de tempo
  atrasa: conferir pela imagem.
- **20/11 madrugada — Piloto com inteligência alta (1.0.56→1.0.60):**
  * Chave da API no celular (`~/.controle-ir/anthropic.key`, 600, criada pelo dono no Termux; permanente; conta
    Team com teto mensal de US$ 100). Latência medida da API daqui: Haiku e Sonnet ~1,3 s por resposta.
  * **Escada de inteligência:** memória → modelo local com CERTEZA (logprobs do llama-server) → Sonnet. O Sonnet
    roda em toda pergunta e serve de **gabarito**: a precisão do local com certeza ≥ 95% é medida na partida
    (início otimista 9/10); o local age sozinho enquanto a precisão medida ≥ meta (90%). Memória só guarda resposta
    do forte. Modelo local trocado para **Qwen2.5-3B Q4_0** (`-t 6`, ~0,6–0,8 s; o 1,5B errava convicto).
  * Rodadas do quiz (placar da página, prazo 2 s): R1 só 1,5B 14/30 · R3 1,5B+Sonnet 22/30 · R4 3B+Sonnet com
    aprendizado radical 16/30 (13 estouros: tudo esperando o Sonnet) · **R5 sem memória 29/30, 0 estouros,
    mediana 1,62 s** · **R6 com a memória da R5: 30/30, mediana 0,70 s (nosso lado 0,22 s)**.
  * Lição: ~0,5 s entre a página desenhar e o piloto agir (atualização da acessibilidade do Chrome + entrega do
    toque) — próximo alvo (perceber por diferença de quadros na captura). Sobreposições do sistema (barra,
    notificação) não travam mais o piloto; app de banco na tela faz o piloto parar.
- **19/11 noite — PILOTO: laço rápido no celular (1.0.47→1.0.55):**
  * Objetivo do dono: "modo deus" = ver e reagir como uma pessoa. Diagnóstico (debatido com o ChatGPT no app):
    o celular já percebe/lê/toca em ~0,1–0,3 s; o gargalo é o ciclo do Claude (~3 s por decisão, só vê a tela no
    retorno de cada chamada). Solução: tirar o Claude do laço — `acao=piloto` (`capacidades/tela/piloto.py`).
  * Piloto: espera a tela mudar (Java `aguardar`), lê pergunta+opções pela acessibilidade, **corrida de
    cérebros** (memória → modelo local → Claude Haiku pela API, streaming: toca no 1º dígito), **alvo semântico**
    (relocaliza o TEXTO escolhido na hora do toque; descarta se a pergunta mudou), **descarte de leitura
    rasgada** (pergunta e opções têm de mudar juntas + 2 leituras iguais), gravador `~/.controle-ir/piloto/
    rodadas.jsonl`. `iniciar/estado/parar/ensinar/testar`.
  * Modelo local: llama.cpp **compilado no celular** com `GGML_NATIVE` (dotprod/i8mm; o pacote do Termux é
    genérico e 4,5x mais lento) em `~/.controle-ir/llama.cpp/build/bin`, Qwen2.5-1.5B **Q4_0**
    (`~/.controle-ir/modelos/`), `llama-server` em 127.0.0.1:8080, `-t 4`. Pergunta nova: ~0,32–0,64 s.
    Religar: `B=~/.controle-ir/llama.cpp/build/bin; LD_LIBRARY_PATH=$B setsid nohup $B/llama-server -m
    ~/.controle-ir/modelos/qwen2.5-1.5b-q4_0.gguf --host 127.0.0.1 --port 8080 -c 1024 -t 4 -tb 4 --no-webui &`.
  * Quiz de teste instrumentado: `capacidades/tela/quiz/quiz.html`, servido em 127.0.0.1:**8766** (a 8765 é do
    serviço) e aberto com `rish am start -d URL`. Rodada 1 (só local): 30/30 respondidas, 0 estouros, mediana
    916 ms, p95 1475 ms (medido pela página), **14/30 acertos** — quase todos os erros por leitura rasgada
    (corrigida na 1.0.54, ainda sem nova rodada medida). Chave da API (Haiku) ainda não instalada
    (`~/.controle-ir/anthropic.key`, nunca pelo chat).
  * **Privacidade (1.0.55):** a leitura da tela (`ver`, piloto, sequências) descarta nós e imagem de apps da lista
    de bloqueio (bancos/pagamentos/senhas) — antes só o toque era bloqueado.
  * Outros: deslize do teclado da grade longe da borda (gesto "voltar"), teclado guardado entre partidas,
    `texto_max` (ler textos longos inteiros), xadrez compacto (`lance`, `esperar_vez`, `ver_depois=tabuleiro`).
- **19/11 — Canal direto, grade NxN, rotinas e reenvios (1.0.46 + PR da Central):**
  * **Canal direto** (`controle_ir/canal.py` + Durable Object `Canal` na Central): o celular disca para a Central
    e mantém um WebSocket; as chamadas vão por ele (sem ngrok, sem TLS por chamada) e a Central empurra avisos
    (armar/desarmar/painel aberto chegam na hora). Confirmação de recebimento: sem ela em 5 s, cai para o túnel.
    Detalhes e segurança: `docs/seguranca.md` §3d. E2E da Central: 53/53 (inclui canal, aviso na hora e celular
    congelado → túnel em 5,0 s).
  * **Reenvios:** a mesma chamada repetida pela rede (corpo idêntico, enquanto roda ou até 3 s depois) devolve a
    resposta da primeira — causa provável dos "não achei o teclado" falsos (a 1ª execução resolvia o jogo, a
    resposta se perdia e o reenvio rodava na tela de resultado). `rpc_id` agora vai para a auditoria.
  * **Grade NxN:** modelos guardados no leitor (`modelos`/`ler`), assinatura 32x32 com o símbolo principal do
    botão (ignora a contagem embaixo), teclado em páginas (desliza a fileira), símbolos 1–9 e A–Z, resolvedor
    genérico (9x9, 16x16 em 1 ms, 6x6…), correção de casa duvidosa em conflito, preenchimento por página e
    conferência com os modelos guardados (antes: os botões sumiam e a conferência dava "faltam todas").
    Validado offline: 131/131 no 16x16 (B≠8, G≠C), 81/81 no 9x9.
  * **Reflexos por app** (`app`, texto curto só vale igual) também nas esperas (`esperar_texto`, grade) e
    **rotinas** (`acao=rotina`: salvar/rodar/repetir N vezes numa chamada com resumo por volta).
- **19/11 — Anúncio por baixo da barra do sistema (1.0.45):** um AppLovin com cartão final sem fechar passou como "fechado"
  porque o último evento de janela era da barra de notificações/gravador de tela. Agora, se o último evento vem do
  sistema (ou ao confirmar o fechamento), confere a atividade no topo (`dumpsys activity | topResumedActivity`).
- **19/11 — Grade mais rápida (1.0.44):** teste com a 1.0.43: Sudoku difícil (44 casas) em 8 s no relógio do jogo,
  leitura+solução 0,28 s, 88 toques 2,8 s, olhar final 1,3 s. Agora: `grade` aceita `antes` (retomar o jogo na mesma
  chamada), espera a grade ficar estável (duas leituras iguais) em vez de pausa fixa, preenche com 8 ms de pausa e
  8 ms de pressão (`toques P:H`), relê e repete sozinho até 6 casas que não pegaram (só se a janela não mudou) e não
  espera a animação final. Leitura considera tinta clara ou escura (algarismo branco em casa destacada). O modo
  "Número Primeiro" do app foi descartado: segurar ~0,5 s por algarismo custa mais do que economiza.
- **19/11 — Grade lida no celular (1.0.42):** `acao=grade` lê um tabuleiro de algarismos desenhado (sem texto na
  acessibilidade) no próprio leitor (Java `grade`): cada casa vira uma assinatura 16x16 comparada com os botões 1..N do
  teclado do jogo (achados sozinhos abaixo da grade). Validado offline numa captura antiga: 81/81. `resolver=true`
  resolve o sudoku (MRV) e preenche numa leva só — uma chamada, sem imagem para o Claude.
- **19/11 — Anúncios resolvidos no celular (1.0.41):** medição de uma rodada de Sudoku difícil: 2 min 24 s, sendo ~2 min
  de anúncios (83%), 21 s de leitura/solução do Claude e 3,5 s de execução. Agora: telas de anúncio (regex `ANUNCIO`)
  são fechadas pelo próprio celular (botão fechar/pular pelo nome ou pequeno no canto, nunca "instalar/peça agora";
  volta se abrir outro app; após 45 s, `am force-stop` + reabrir + Continuar). Trava de app inesperado entre passos,
  erro já com a tela atual, e `esperar_mudanca` olha a tela a cada 0,7 s (vídeo não gera eventos). Incidente: um toque
  por coordenada no cartão final de um anúncio abriu uma conversa do WhatsApp (nada enviado).
- **19/11 — Toques direto no gerenciador de entrada (1.0.40):** com a 1.0.39 o Sudoku (51 casas, 102 toques) caiu
  para 68 ms/toque, não ~30: a UiAutomation chama `syncInputTransactions(waitForAnimations=true)` antes/depois de
  cada evento e o app anima a cada número. Agora a leva injeta por `InputManagerGlobal`/`InputManager.injectInputEvent`
  (como o scrcpy; o shell tem INJECT_EVENTS), assíncrono, e só o último toque espera o app consumir; se o sistema
  recusar, volta para a UiAutomation. No teste, um anúncio jogável sem botão de fechar travou o app: a linha do
  tempo mostrou quando surgiu; foi fechado com `am force-stop` pelo Shizuku (sem tocar no anúncio).
- **19/11 — Toques de leva assíncronos (1.0.39):** teste com a 1.0.38: Sudoku médio novo 39/39 sem erros, 78 toques
  em 7,0 s (89 ms cada, porque cada evento esperava o app confirmar). Agora a leva entrega à fila de entrada sem
  esperar (a ordem é mantida), com 12 ms de pressão; só o último toque espera a confirmação.
- **19/11 — Quando tocar às cegas × olhar de novo (1.0.38):** coordenada só vale na janela em que o Claude a leu
  (`_ULTIMA["janela"]`): se a janela mudou desde a última olhada, ou depois de voltar/abrir/rolar, o toque por
  coordenada não sai e volta `interrompido` com a tela atual; toque por texto, esperar_texto, abrir, se/repetir
  reancoram. Na mesma tela, levas seguem direto. `ver_depois="auto"` (padrão): só o que mudou + imagem apenas do
  recorte visual sem texto (tabuleiro/jogo, `regioes_visuais`) quando a tela é nova ou a ação tocou nele.
- **19/11 — Ciclo econômico (1.0.37):** medido de ponta a ponta: 4,3 s por volta, ~2 s são rede + o Claude
  escrever/ler (piso que código não remove). Por isso: respostas curtas (elemento numa linha, mudanças como +/-/~,
  ~metade dos tokens), `surgiu` com as janelas que apareceram desde a última olhada (anel de 32 no leitor) e
  reflexos guardados no celular (`acao=reflexos`, `~/.controle-ir/tela_reflexos.json`): numa sequência, o que bate
  com uma regra é resolvido em ms e a leva segue, sem gastar uma volta do Claude.
- **19/11 — Reflexos na tela (1.0.36):** o leitor conta os eventos da acessibilidade (janelas novas e mudanças).
  Numa leva de toques (`toquesv`), se surgir outra janela (aviso, anúncio, fim de jogo, outro app) ele para na hora e
  a sequência volta com `interrompido` + o que está na tela; a mesma tela se reanunciando não para (nem o teclado).
  `parar_em_janela=true` vigia também entre passos; `parar_se=[textos]` para quando um texto aparecer (lido só se algo
  mudou); passo `esperar_mudanca` fica olhando até a tela mudar de verdade (`ignorar` relógios etc.). Medido na
  1.0.35: esperar a tela assentar + olhar (só o que mudou) em 0,59 s no aparelho.
- **19/11 — Ciclo rápido de ver-agir-decidir (1.0.35):** na sequência, toques, deslizes e teclas vão injetados pelo
  leitor (`toques` num pedido só), não mais pelo `input` do shell (~0,18 s por toque). Depois de agir, espera a tela
  assentar (`calma`, `waitForIdle` da acessibilidade) em vez de pausa fixa e responde só o que mudou desde a última
  olhada (`ver_depois="mudancas"`, padrão). Condições e laços rodam no próprio celular (`se`/`se_nao` com
  `entao`/`senao`, `repetir` com `vezes` e `ate_texto`/`ate_sumir`), sem ida e volta. Estado (app em foco e tela
  acesa) direto do leitor, sem `dumpsys`. Elementos trazem marcado/selecionado/rolável/desativado. Sudoku médio
  inteiro: 43 casas em ~8 s com o caminho antigo (antes desta versão).
- **19/11 — 1.0.33/1.0.34 medidos no POCO:** leitura da tela 0,04 s (antes 2,6–10 s), `ver` só elementos 0,21 s,
  shell 0,09 s (antes 0,32), foto 480 px 0,11 s e 720 px 0,15 s direto da acessibilidade (antes 1,37 s com
  screencap+ffmpeg), `ver` completo 0,48 s (antes ~3 s). Central: /mcp com 1 consulta ao D1 (PR #11).
- **19/11 — Leitor de tela rápido (1.0.32):** `capacidades/tela/java/controleir/Tela.java`, compilado no celular
  (ecj + dx do Termux, na 1ª vez) e rodando pelo Shizuku (app_process): lê a acessibilidade direto (30–180 ms contra
  2,5–8 s do `uiautomator dump`, que espera a tela parar), injeta toques/teclas e digita com acento; também roda os
  comandos de shell sem reabrir o rish (~0,3 s a menos cada). A capacidade tela roda dentro do serviço (`em_processo`)
  para o leitor ficar aberto; desconecta da acessibilidade após 60 s parado e encerra após 5 min. Sem ele, tudo segue
  pelo caminho antigo.
- **19/11 — Agente de tela mais rápido (1.0.30):** `acao=sequencia` com `passos` (vários toques, digitar,
  teclas, esperas e `esperar_texto` numa chamada; os passos sem leitura de tela vão num só script ao Shizuku);
  `ver` faz dump + captura + foco + tela acesa numa viagem; ações respondem só o app (ver_depois=elementos|imagem
  quando precisar); `recorte=[x,y,l,a]`; elementos sem campos vazios. Pela conversa atual use
  executar_capacidade(nome="tela", argumentos={...}) — o esquema novo do cap_tela só aparece em conversa nova.
- **19/11 — Shizuku congelando em 2º plano (HyperOS):** rish dava timeout com o app do Shizuku em segundo
  plano. Feito pelo rish, para moe.shizuku.privileged.api, com.termux e com.termux.api: `dumpsys deviceidle whitelist +pkg`,
  `cmd appops set pkg RUN_IN_BACKGROUND|RUN_ANY_IN_BACKGROUND allow`, `am set-standby-bucket pkg active` (ficou 5 =
  isento) e `cmd appops set pkg 10008 allow` (autostart do MIUI). Reverter: `whitelist -pkg` e `appops ... default`.
  Também recomendado travar o Shizuku nos recentes (cadeado).
- **19/11 — Permissões do Controle Geral:** liberadas pelo dono em claude.ai/customize/connectors (o
  `.claude/settings.json` também lista `mcp__Controle_Geral`). Sudoku aberto pelo Termux (`am start -n
  easy.sudoku.puzzle.solver.free/com.meevii.ui.activity.SplashActivity`); Shizuku caindo — HyperOS derruba.
- **19/11 — Central 1.0.29 + PR #10:** atividade do Claude (cada chamada), “Agora no celular” (terminal,
  capacidades, câmera/microfone por AppOps) e tela ao vivo no painel. E2E 47/47.
- **19/11 — 1.0.28:** o atalho “Armar Controle IR” da tela inicial, com o celular pareado, abre a Central de
  Controle (quem arma é ela, com a digital). Instalada; Shizuku religado (rish responde uid 2000), modo autônomo.
- **19/11 — Etapa 1b em uso:** conector **“Controle Geral”** no claude.ai entra pela Central de Controle
  (`https://painel-casa.cauetakahashideoliveira.workers.dev/mcp`, OAuth com a digital). “Só pelo painel” LIGADO
  (seq 3): o conector antigo “Controle master” (URL do ngrok) passou a receber 403 — conferido. Celular na 1.0.27.
- **19/11 — Nome geral (1.0.27):** “Painel da Casa” virou **Central de Controle** (o projeto é uma ferramenta
  geral, não só da casa). O endereço `painel-casa.…workers.dev` ficou (trocar invalidaria as passkeys).
- **19/11 — Etapa 1b (1.0.26 + PR #8): OAuth na borda.** Conector novo `https://<painel>/mcp` com login pela
  digital; o painel barra na borda o que o estado não permite e repassa o resto assinado; “só pelo painel” fecha a
  URL do ngrok. Falta: merge, instalar 1.0.26, adicionar o conector novo no claude.ai, testar, ligar “só pelo painel”.
- **19/11 — Etapa 1a em uso:** passkeys do POCO e do iPad cadastradas; POCO pareado e na 1.0.25; armar é pelo
  Central de Controle (atalho na tela inicial), com a digital. Próximo: Etapa 1b (OAuth na borda, fim da URL secreta).
- **19/11 — Painel no ar (PR #6) e POCO pareado.** Na 1ª sincronização o celular tentou mandar o histórico
  antigo inteiro e o envio estourou o tempo (o pareamento valeu). 1.0.25 + PR #7: só o histórico novo, em lotes de
  30 numa transação, sem repetidos; Safari do iPad com as opções da passkey buscadas antes do toque.
- **19/11 — Segurança, Etapa 1a (1.0.24): Central de Controle** (`painel/`, Cloudflare Worker + D1): entrar com
  passkey (digital), iPad por convite de uso único, celular pareado por código, armação/emergência/revogação por
  estado assinado (Ed25519) que o celular busca a cada 30 s, “aplicado × pendente”, histórico encadeado por hash.
  Teste E2E 27/27 (`painel/testes/e2e.cjs`). Falta publicar na conta Cloudflare do usuário e parear o POCO.
- **19/11 — Segurança, Etapa 0 (1.0.23):** auditoria (2 agentes) mostrou que só a URL protegia tudo. Agora:
  sistema desarmado por padrão (só IR/consulta/travar pelo conector), armar só no celular (widgets “Armar” e
  “Desarmar Controle IR”), sem aprovação pelo chat, travar definitivo pelo remoto, classe `protegido`, ref de
  commit completa, ngrok sem inspetor. Arquitetura e decisões em `docs/seguranca.md`.
- **19/11 (manhã) — Toque pelo Shizuku (1.0.22):** mesmo com a opção de segurança ligada, o `input` dava "Failed
  transaction": o system_server recusa a saída de `cmd` apontando para a memória compartilhada ou para o cano do app.
  Com stdin `/dev/null` e saída em `/data/local/tmp` (copiada depois para a pasta de troca) passou. Teste real:
  `am start` da Bateria → dump → toque em "Proteção da bateria" → leitura dos interruptores.
- **19/11 (manhã) — Shizuku e agente de tela:** Shizuku 13 instalado e iniciado por depuração sem fio; `rish`
  exportado para Download/shizuku (o Android não deixa usar a raiz de Download) e copiado para
  `~/.controle-ir/rish/` (PKG → com.termux, .dex 400). O cano do rish cortava saídas (PNG com 28 KB de 317 KB, `id`
  vazio): a **1.0.20** troca tudo por arquivo em `Download/.controle-ir-tela` (oculta, `.nomedia`, apagado na hora) e
  a **1.0.21** reconhece o bloqueio de toque do HyperOS. Ver a tela (captura + 34 elementos) e abrir as
  Configurações funcionaram. O túnel caiu duas vezes durante a configuração (reconectou sozinho uma vez; na outra,
  `controle-ir desligar; pkill ngrok; controle-ir ligar`).
- **19/11 (manhã) — Noite com o serviço ligado sem uso:** o servidor ficou no ar desde 18/11 22:54, sem reiniciar
  (o HyperOS não derrubou), e o usuário viu **gasto mínimo de bateria**. De manhã: 49%, descarregando, 26,6 °C,
  CPU parada (carga 0). Decisão do usuário: **pode ficar ligado o tempo todo** (antes ligava só para usar).
  O histórico do termômetro não mede o repouso (as leituras de 22:56–23:55 foram com o celular em uso, 200–1000 mA).
  **Bateria** (termux-battery-status): saúde GOOD, **4 ciclos**, 26,6 °C, 3,81 V; capacidade de fábrica 8.500 mAh
  (versão global, HyperOS OS3.0.304.0.WPLMIXM). `/sys/class/power_supply` é bloqueado sem root; com o Shizuku dá
  para ler `dumpsys battery`/`batterystats` (capacidade aprendida) para uma conta mais precisa.
- **19/11 — Skill `/god-mode`** (`.claude/skills/god-mode/`): adaptação do G0DM0D3 (elder-plinius, AGPL-3.0) com
  AutoTune de 20 contextos (+ português), aprendizado por notas, STM, pontuação neutra, `perguntar` e `comparar`
  (OpenRouter ou servidor local) com síntese pelo Claude. Ficaram de fora os prompts de jailbreak, a diretiva
  "nunca recuse" e o Parseltongue. Sem `OPENROUTER_API_KEY` no ambiente ainda: o usuário configura nas
  Configurações do ambiente se quiser usar `perguntar`/`comparar`. 18 testes em `testes/test_god_mode.py`.
- **19/11 — Visor do ar do quarto apagado pelo conector** (`x_luz`, 23:49 no relógio do celular): o último estado
  era 16 °C/frio/automática, o mesmo do quadro do `x_luz`, então só o visor mudou. Usuário: "deu certo". Estado
  registrado no celular (`registrar_estado`: ligado, visor desligado).
- **19/11 — Hook de início de sessão** (`.claude/hooks/session-start.sh`): instala o graphify (`graphifyy`, pelo uv)
  e o numpy nas sessões do Claude Code na nuvem; PR #5. Grafo atualizado: 927 nós, 2307 arestas (estava na 1.0.14).
- **19/11 — 1.0.18 no celular (22:54):** `termometro` (temperatura do cômodo pela bateria; 1ª leitura 31 °C na
  bateria → ~29 °C estimado, confiança média com o celular em uso; monitorando 60 min), ouvido do ar no
  `controlar(ouvir=true)` (3 s antes + ~8 s depois do envio, compara o ruído), `tela` e o recorte da `foto`
  instalados com o aval do usuário ("pode começar a fazer essa integração").
- **19/11 — Central da Casa 2.0** (artefato privado https://claude.ai/artifact/XSh6ivS8Cc6BsKakes2pCh, fonte
  `artefatos/central-da-casa.html`): página do claude.ai que usa o conector Controle master (consultar, opcoes,
  controlar, executar_capacidade, executar_comando, capacidades, propor_capacidade). Tem o **Gênio** (sample com
  ferramentas + ditado + voz) que controla, roda comandos no Termux, **escreve e instala capacidades novas** e
  **cria painéis** (botões/medidores/gráficos/notas) guardados no db do artefato (coleção `widgets`), mais
  memória (`memoria`) e diário (`eventos`) com "o que você aprendeu sobre mim". Painéis iniciais gravados:
  `celular` (medidor do estado_celular) e `noite` (Quarto 23 °C, Desligar a TV). Testado com simulação do
  runtime (sem erros); as chamadas reais só rodam abertas no claude.ai. A parte do sono depende da 1.0.19.
- **19/11 — 1.0.19 no GitHub (commit 5f07335), NÃO instalada:** `sono` (laboratório do sono) e `sonar`
  (presença por ultrassom, experimental). Instalar com `atualizar_sistema` quando o usuário estiver presente
  (cada chamada pede aprovação da organização).
- **19/11 — confirmação automática (1.0.16–1.0.17 no celular):** numpy 2.5.5 e ffmpeg 9.0.2 instalados; espelho
  de pacotes trocado do `mirrors.cqupt.edu.cn` (55 KB/s) para o oficial `packages-cf.termux.dev` (6 MB/s; cópia
  em `~/.controle-ir/sources.list.antes`). Microfone e câmera do Termux:API liberados pelo usuário.
  `controlar(ouvir=true)` grava, envia e analisa o bipe no tempo certo (o parâmetro só aparece em conversas
  novas); `foto` devolve a imagem ao Claude. Ver `docs/aparelhos/quarto/ar-do-quarto.md`. O recorte da `foto`
  está no GitHub, **não instalado**: instalar só quando o usuário pedir.
- **19/11 — autorizações:** os pedidos de aprovação vinham da regra da organização no claude.ai
  (`org_ask_ceiling`) para as ferramentas do Controle master; o `.claude/settings.json` não passa por cima dela.
  Liberar em https://claude.ai/customize/connectors → Controle master → permissões das ferramentas.
- **19/11 — rede de casa inventariada** com a capacidade nova `descobrir_rede` (só leitura, sem nmap): roteador
  Intelbras Twibi Giga (`.1`), câmeras IP prováveis (`.95`, `.213`, só RTSP 554), `.11` e `.52` sem portas
  comuns, celular `.94`. TV Samsung e ares não aparecem na rede (sem Wi-Fi ou desligados). Inventário em
  `~/.controle-ir/medicoes/inventario.json`. nmap 7.993 também instalado no Termux.
- **19/11 — queda do conector após atualizar:** o ngrok saía com código 1 em laço (agente antigo órfão segurando
  o domínio fixo) e o conector dava "Not Found"; resolvido com `controle-ir desligar; pkill ngrok; controle-ir
  ligar`. A **1.0.15** encerra ngrok órfão antes de abrir o túnel, mata o grupo de processos ao parar e mostra o
  último erro do túnel no registro.
- **19/11 — modo deus confirmado no POCO** (sessão de teste do Claude Code, conferida por `consultar`): política
  `autonomo` (todas as classes permitir); `estado_celular` ok (bateria, Wi-Fi 5 GHz RSSI −48, 16 comandos do
  Termux:API); `diagnostico_rede` ok (0% de perda, roteador ~26 ms, internet ~76 ms, DNS 64–154 ms, sem
  problemas); `executar_comando` ok (aarch64, kernel 6.6.118, 107 pacotes); `atualizar_sistema` instalou a
  **1.0.14 sozinho, sem aprovação** (ativo desde 21:19:53). Sessões novas do Claude Code pedem permissão para o
  conector (nome interno `96238baf-…`) até o usuário escolher "sempre permitir".
- **19/11:** autoatualização confirmada no POCO (`controle-ir atualizar --ref` → 1.0.13 sozinho); widget
  Ligar/Desligar confirmado na 1.0.13 (reinício 21:06 → 21:08). Usuário ligou o **modo autônomo**.
  1.0.14: atalhos do widget Modo autonomo, Modo cauteloso e Travar.
- **19/11:** celular atualizado para a **1.0.12** (aparelhos e catálogo mantidos; confirmado por `consultar`). O
  atalho Ligar do widget não subiu o serviço e não deixou registro; o serviço sobe com `controle-ir` no Termux.
  A 1.0.13 faz o `ligar` registrar desde o início e mostrar a falha na tela. Sessões antigas do Claude não
  enxergam as ferramentas novas (lista fixa por conversa): usar conversa nova.
- (histórico) Servidor no celular na versão **1.0.7** (atualizado em 18/11 às 20h08; catálogo mantido, sem reconstruir).
- **Termux:Widget instalado** com os atalhos "Ligar Controle IR" e "Desligar Controle IR" na tela inicial,
  testados em 18/11. Até 18/11 o usuário ligava o serviço só para usar; em 19/11 viu que uma noite inteira ligado
  gasta quase nada e decidiu deixar **ligado o tempo todo** (os atalhos continuam valendo). Se o conector não
  responder (Service Unavailable / Not Found), peça para tocar em "Ligar Controle IR"; logo depois de ligar,
  as 1–2 primeiras chamadas podem falhar enquanto o túnel abre (repita após alguns segundos).
- Início automático (Termux:Boot): **não ativado**. O motivo era bateria; com o gasto mínimo medido em 19/11, dá
  para ativar com `controle-ir inicio-automatico sim` se o usuário quiser (volta sozinho depois de reiniciar o celular).

## Conector no Claude
- Nome atual: "Controle master" (sem login, URL com segredo). O antigo "Controle do POCO" foi removido.
- Túnel: **ngrok com domínio fixo** (`controle-ir tunel ngrok --dominio <endereço>.ngrok-free.app`), executado
  via `termux-chroot` (DNS do Android) e apontando para `http://127.0.0.1:8765` (evita Bad Gateway por IPv6).
- A URL é fixa: reiniciar o Termux não exige mexer no Claude. Muda só com `controle-ir novo-segredo` ou
  trocando o domínio no ngrok.
- O segredo foi regenerado em 17/11 depois de aparecer numa captura de tela.
- Cuidados: não usar CTRL+C na aba do servidor (na 1.0.6 com início automático, o console pode ser fechado à
  vontade); não fotografar a caixa com a URL.

## Aparelhos salvos
Ficha completa de cada um (perfil, comandos testados, sinais extras, ressalvas): **[docs/aparelhos/](aparelhos/README.md)**.

| Cômodo | Nome no conector | Aparelho | Perfil | Ficha |
|---|---|---|---|---|
| Quarto | `ar do quarto` | ar-condicionado **Gree** GWH09KF | SmartIR Gree GWH09KF (nº 105) + oscilar, visor desligado e turbo gerados | [ar-do-quarto](aparelhos/quarto/ar-do-quarto.md) |
| Quarto | `tv do quarto` | TV **Samsung** (Samsung32, 0x07) | Flipper "Samsung TV Full" (nº 2331) + ligar/desligar diretos + macro `abrir Netflix` | [tv-do-quarto](aparelhos/quarto/tv-do-quarto.md) |
| Escritório | `ar do escritório` | ar-condicionado **Carrier** | SmartIR Carrier Unknown (nº 94) | [ar-do-escritorio](aparelhos/escritorio/ar-do-escritorio.md) |
| Laboratório | `ar condicionado laboratório` | ar-condicionado **Midea** | o mesmo Carrier nº 94 + oscilação Ferroli/York | [ar-condicionado-laboratorio](aparelhos/laboratorio/ar-condicionado-laboratorio.md) |
| Quarto 2 | `ar condicionado quarto 2` | ar-condicionado **Brastemp Clean** BBV09BBBNA (protocolo TCL112) | nº 9524 gerado por `ferramentas/tcl112.py` | [ar-condicionado-quarto-2](aparelhos/quarto-2/ar-condicionado-quarto-2.md) |

- Em 17/11 "escritório" virou `ar do escritório` e "quarto" virou `ar do quarto` (o quarto também tem a TV).
- Ar do escritório e ar do laboratório usam os mesmos códigos: se os dois estiverem ao alcance, os dois reagem.

## Frases
1. "Ligue o ar do escritório em 23 °C, modo frio, ventilação baixa."
2. "Agora mude só para 22 °C."
3. "Desligue o ar do escritório."
4. "Ligue o ar do quarto em 16 graus." / "Coloca a pá do ar do quarto para oscilar." / "Apaga o visor do ar do quarto."
5. "Liga a TV do quarto." / "Abre a Netflix na TV."

## Pendências antigas (situação em 19/11)
- ✅ **Autonomia máxima ("modo deus")**: `controle-ir exec modo autonomo` ligado no celular; o Claude age sem
  pedir aprovação a cada passo (freio: `travar`). Linha ética: só o que é dele ou autorizado.
- ✅ Aprovação pelo chat sem código (`aprovacao_remota: chat`); não configurar TOTP a menos que ele peça.
- ✅ Instalação pelo Claude: desde a 1.0.13 tudo sobe com `atualizar_sistema(ref)` (hoje está na 1.0.18).
- ⏳ Gravar as ressalvas como observação de cada aparelho (`editar_aparelho(observacao=…)`) para chegarem ao
  Claude pelo resumo: extras do ar do quarto fixam 16 °C/frio/automática (o "visor desligado" também põe 16 °C);
  desligar direto da TV ainda não testado (escritório e laboratório compartilham códigos: o resumo já detecta).

## Implementado em 18/11 (versões 1.0.6 e 1.0.7, instaladas no celular)
- **Ligar/desligar com um toque (1.0.7):** atalhos "Ligar Controle IR" e "Desligar Controle IR" em
  `~/.shortcuts/tasks` para o app Termux:Widget (o instalador cria; `controle-ir atalhos`); `controle-ir
  ligar|desligar` avisam na tela; botão Desligar na notificação. Desde 19/11 o serviço fica ligado direto (gasto
  mínimo numa noite); se o conector não responder, peça para tocar em "Ligar Controle IR".
- **Início automático (Termux:Boot):** `controle-ir inicio-automatico sim|nao|status` cria/remove
  `~/.termux/boot/controle-ir` (wake lock + `controle-ir iniciar --fundo`).
- **Segundo plano:** `iniciar --fundo` roda sem console; registro em `~/.controle-ir/servico.log` (permissão 600,
  sem o segredo; `controle-ir log`); notificação fixa "Controle IR ativo" (Painel, Copiar URL).
- **Console:** `controle-ir` com o serviço já rodando (ou com o início automático ativado) abre só o console:
  Enter pausa, `c` continua, `copiar`, `url`, `painel`, `log`, `parar`; `sair`/CTRL+C/fechar o Termux não
  derrubam o conector. Com isso a ressalva "não usar CTRL+C na aba do servidor" deixa de valer no modo segundo plano.
- **`controle-ir parar`** confere se o pid é mesmo do controle-ir antes de encerrar e espera o serviço sair.
- **Resumo dos aparelhos no `initialize` do MCP:** nome exato, valores aceitos, faixas, teclas, botões criados
  pelo usuário, macros, aparelhos com os mesmos códigos e observação. A regra "chame opcoes antes" virou
  "chame controlar direto se couber no resumo; opcoes para o último estado ou o que faltar".

## Anúncio dos testes (v1.0.1)
- Cada envio da busca é falado em voz alta (termux-tts-speak) e mostrado no Termux como "▶ N".
- O número falado = número do histórico: "foi o 5" → pausar, retestar([5]), confirmar(5).
- Desligar a voz: `controle-ir voz nao`.

## Problemas já resolvidos (para não repetir)
- `curl` com `CANNOT LINK EXECUTABLE`: `apt update && apt full-upgrade`.
- Download do ZIP em cache do GitHub: usar URL com o hash do commit (`.../raw/<hash>/dist/controle-ir.zip`).
- Domínio do ngrok: usar o endereço `*.ngrok-free.app`, não o código `rd_…`.
- Faixa real do perfil Carrier (escritório/laboratório): 17–30 °C (16 °C não existe). O Gree do quarto vai de 16 a 30 °C.
- Botão que o perfil não tem num Gree (oscilação, visor): **não** montar o quadro pelos tempos genéricos do
  ESPHome (falhou duas vezes). Usar `ferramentas/gree_variante.py`, que parte da captura real e troca só os bits.
- `editar_aparelho` com um sinal que o perfil já tem não duplica a tecla (na 1.0.4 responde "adicionado" mesmo
  assim). Ex.: o Smart Hub 0x79 já era a tecla `inicio_3` da TV.
