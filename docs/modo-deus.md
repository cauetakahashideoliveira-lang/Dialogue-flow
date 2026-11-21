# Modo deus — arquitetura evolutiva e mapa de oportunidades

Este mapa registra a investigação iniciada em 18/11. Para conferir quais propostas chegaram ao código, quais foram medidas e o que falta validar no Android, consulte a [passagem de bastão de 21/11](HANDOFF.md).

Investigação de 18/11/2026. Objetivo: transformar POCO X8 Pro Max + Termux + Claude (app, Claude Code na nuvem) +
conector MCP numa ferramenta que **entende, age, observa e cresce** sobre aparelhos, computadores, redes e contas
autorizadas. Legenda de estado: ✅ funciona hoje · 🧪 construído e testado em simulação (falta o POCO) ·
🔧 exige construção · 🛒 exige equipamento · ❓ hipótese a testar.

## 1. O que mais surpreende (com fundamento)

1. **O Claude já pode criar e implantar ferramentas no celular durante a conversa.** 🧪 A versão 1.0.9 tem
   capacidades plugáveis (script + manifesto, sem reiniciar), execução governada de comandos e atualização pelo
   GitHub com aprovação. O ciclo "tive uma ideia → a função existe" deixou de passar por você colar linhas.
2. **O celular pode operar qualquer app, mesmo sem API**, com ADB sem fio para o próprio aparelho ou Shizuku+rish
   (uid `shell`, sem root): `screencap` + `uiautomator dump` dão "olhos" (imagem + árvore de elementos) e `input`
   dá "mãos". ❓ No Xiaomi exige "Depuração USB (Configurações de segurança)" e reinício
   ([guia Shizuku](https://shizuku.rikka.app/guide/setup/), [FAQ scrcpy](https://github.com/Genymobile/scrcpy/blob/master/FAQ.md)).
3. **Sua TV e seus ares provavelmente falam pela rede, e lá dizem o estado real.** TV Samsung Tizen: REST em
   `:8001/api/v2/` (modelo, PowerState) e WebSocket `:8002` para abrir apps por id, como YouTube e Netflix, sem
   macro de setas ([samsungtvws](https://pypi.org/project/samsungtvws/)). Gree com Wi-Fi: temperatura do sensor da
   evaporadora (`TemSen`) pela LAN ([greeclimate](https://pypi.org/project/greeclimate/)). Carrier/Midea com Wi-Fi:
   temperatura interna e externa e consumo ([msmart-ng](https://pypi.org/project/msmart-ng/)). Isso fecha o ciclo
   agir → **medir** que o IR sozinho não tem. ❓ Depende de os aparelhos terem Wi-Fi (perguntas no §9).
4. **Um PC seu vira extensão do Claude do celular sem abrir porta:** `claude remote-control` (oficial, só HTTPS de
   saída, várias sessões, worktree por sessão) ou o Dispatch do Claude Desktop
   ([docs Remote Control](https://code.claude.com/docs/en/remote-control), [Desktop](https://code.claude.com/docs/en/desktop)).
   Esta sessão na nuvem já tem as ferramentas `list_computer_folders`/`request_computer_folder`; hoje a lista está vazia.
5. **Dá para restringir o conector aos IPs da Anthropic.** Os conectores do claude.ai saem de `160.79.104.0/21`
   ([docs](https://claude.com/docs/connectors/building/authentication)). 🧪 A 1.0.9 registra a origem de cada chamada
   e, depois de confirmada, `controle-ir origens exigir` recusa o resto, mesmo que a URL vaze de novo.
6. **Um botão no celular pode acordar uma sessão Claude Code na nuvem.** O gatilho de API das tarefas agendadas
   (`/fire`) aceita um texto, que pode ser um log ou uma medição. Isso permite "analisar o log do controle" com um
   toque no widget ([routines](https://code.claude.com/docs/en/routines)).

## 2. Gargalo principal e o primeiro avanço (implementado)

**Gargalo:** o Claude só agia no celular por ferramentas fixas. Para *olhar* o ambiente (pacotes, arquivos,
sensores) ou ganhar uma função nova, era preciso escrever código no repositório e você colar uma linha no Termux.
Não havia memória de permissões, histórico nem forma segura de crescer.

**Avanço (1.0.8 → 1.0.9), escolhido por multiplicar todas as outras integrações:**

| Peça | O que destrava | Estado |
|---|---|---|
| **Capacidades plugáveis** (`capacidades.py`): pasta com `capacidade.json` + script `.py`/`.sh` (JSON entra, JSON sai), relida a cada chamada; ferramenta `cap_<nome>` em conversas novas e `executar_capacidade` na atual | Toda integração nova vira ferramenta sem mexer no núcleo | 🧪 |
| **Proposta com aprovação física presa ao hash**: `propor_capacidade` não executa nada; o botão Aprovar leva o SHA-256 revisado; se o código mudar, a aprovação é recusada; subpastas entram no hash | Criar ferramentas no meio da conversa com segurança | 🧪 |
| **Execução governada** (`execucao.py`): `executar_comando` roda shell no Termux como tarefa numerada (saída em arquivo, `tarefa(id)` acompanha ou para), com política por classe (leitura, rede, pacotes, sistema, livre) que **só muda no celular** | Investigar, instalar, prototipar e medir sem você digitar | 🧪 |
| **Permissões persistentes**: `controle-ir exec classe rede permitir`, `exec liberar 30` (janela), `exec travar` (nega tudo e encerra tarefas) | Autorizar uma classe uma vez; parar tudo na hora | 🧪 |
| **Auditoria**: `~/.controle-ir/auditoria.jsonl` registra cada ferramenta chamada e cada pedido, decisão e fim; `controle-ir exec historico` | Histórico compreensível | 🧪 |
| **Atualização pelo GitHub**: `atualizar_sistema(ref=<commit>)` (classe sistema, sempre pede aprovação) baixa, guarda a versão anterior e religa; testado de ponta a ponta num Termux simulado com download real do commit | O que a "oficina" na nuvem constrói chega ao celular sozinho | 🧪 |
| **Reverter só em shell**: atalho "Reverter Controle IR" troca de volta para `~/controle-ir.anterior` mesmo se o Python quebrar | Recuperação quando uma mudança corta o próprio acesso | 🧪 |
| **Aprovações fora do túnel**: `/api` e painel exigem um token só local e recusam qualquer chamada com cabeçalho de túnel | Quem tiver a URL não aprova nada remotamente | 🧪 |
| **Origens**: registra o IP de cada chamada pelo túnel; `exigir` aceita só `160.79.104.0/21` | Segredo vazado deixa de ser chave | 🧪 |
| Embutidas: `diagnostico_rede` (Wi-Fi, perda/latência roteador × internet, DNS, download, histórico, diagnóstico e sugestões reversíveis) e `estado_celular` | O caso "minha internet está ruim" já tem ferramenta | 🧪 |

Testes: `python3 -m unittest discover -s testes` (58 testes, incluindo classificação, aprovação, travamento,
tempo-limite, reinício, reverter em shell, hash, origens e /api pelo túnel).

## 3. Arquitetura evolutiva

```
            VOCÊ (app Claude no celular · web · Claude Code)
                 │ intenção
  ┌──────────────┴───────────────────────────────────────────────────────────┐
  │ CÉREBRO: Claude (chat) e OFICINA: Claude Code na nuvem (repo, web, agentes,  │
  │ testes, tarefas agendadas/API fire)                                        │
  └───┬──────────────────────┬───────────────────────────┬────────────────────┘
      │ MCP (túnel+segredo,  │ Remote Control / Dispatch │ GitHub (memória versionada:
      │ origens Anthropic)   │ (oficial, só saída)       │ capacidades embutidas, docs)
  ┌───┴──────────────┐   ┌───┴──────────────┐         │ atualizar_sistema(ref)
  │ NÓ CELULAR        │   │ NÓ PC             │◄────────┘
  │ inventário        │   │ shell, arquivos,  │
  │ capacidades       │   │ apps, MCPs locais │
  │ execução governada│   └───────────────────┘
  │ auditoria/política│
  │ observação: Wi-Fi,│── LAN: TV (8001/8002), Gree (UDP 7000), Midea (6445), roteador, Tuya…
  │ bateria, câmera,  │── IR (emissor), USB OTG (ESP32: receber IR, sensores, BLE) 🛒
  │ microfone, tela   │── Android: ADB-self/Shizuku (ver/tocar qualquer app) ❓
  └───────────────────┘
```

**Ciclo de crescimento** (já suportado pelas ferramentas da 1.0.9):
1. *Inventário*: `estado_celular`, `capacidades`, `politica`, `executar_comando("pkg list-installed")`.
2. *Lacuna*: o Claude compara o pedido com o inventário e nomeia o que falta (protocolo, pacote, permissão, hardware).
3. *Pesquisa*: no chat (busca na web) ou delegada a uma sessão Claude Code (agentes).
4. *Protótipo*: `executar_comando` (instalar e testar no aparelho), com observação do resultado.
5. *Capacidade*: `propor_capacidade` (pequena, no chat) ou PR no repositório + `atualizar_sistema` (maior, com testes).
6. *Registro*: `capacidades(acao="anotar")` guarda o resultado confirmado; ficha em `docs/aparelhos/` quando envolver aparelho.
7. *Reuso*: `cap_<nome>` aparece em conversas novas; as capacidades do usuário sobrevivem a reinícios e atualizações.

## 4. Mapa de oportunidades

Impacto e esforço de 1 a 5. **M** = multiplicador: aumenta a capacidade de criar outras integrações.

### Celular e Android
| Oportunidade | Pedido de exemplo | Estado | Imp/Esf | M |
|---|---|---|---|---|
| Observação pelo Termux:API (57 comandos: câmera→imagem para o Claude ver, microfone, sensores, notificações recebidas, localização, Wi-Fi scan) | "Tira uma foto do visor do ar e me diz a temperatura." | 🔧 (via capacidade) | 5/2 | M |
| Shell privilegiada sem root (ADB-self ou Shizuku+rish): dumpsys, settings, am/pm, quem gasta bateria | "Qual app está gastando bateria agora?" | ❓ | 5/3 | M |
| **Agente de tela**: ver_tela (screencap + uiautomator) e tocar/digitar em qualquer app | "No app do ar, coloca o laboratório em 24 °C." | ❓ depende do anterior | 5/3 | M |
| Eventos do Android → ações (Tasker/MacroDroid + intent RUN_COMMAND; adesivo NFC como botão) | "Ao entrar no Wi-Fi de casa, liga o controle e põe o quarto em 23 °C." | 🔧 | 4/2 | M |
| Desligar o *phantom process killer* (Android 12+) e isentar o Termux da bateria | "Por que o conector caiu sozinho?" | ❓ toggle nas opções do desenvolvedor | 3/1 | |
| Confirmação automática pelo bipe do ar (microfone + FFT com numpy) | "Liga o ar e confirma se ele recebeu." | ❓ | 4/3 | |
| USB OTG + ESP32: **receber IR** (aprender o controle original), sensores reais, ponte BLE | "Aprenda o botão turbo do controle do Carrier." | 🛒 ~R$ 60–100 | 4/4 | M |

### Casa e rede
| Oportunidade | Pedido de exemplo | Estado | Imp/Esf | M |
|---|---|---|---|---|
| TV Samsung pela rede (estado real, abrir YouTube por id, digitar texto) | "Liga a TV, abre o YouTube e procura 'jornal nacional'." | ❓ TV Tizen no Wi-Fi | 4/2 | |
| Inventário da rede em Python puro (SSDP, mDNS unicast, broadcasts Gree/Midea/Tuya, portas) | "O que tem na minha rede que você consegue controlar?" | 🔧 | 4/2 | M |
| Gree pela LAN (TemSen = temperatura real; estado) | "Que temperatura está no quarto e o ar está mesmo em 23?" | ❓ módulo Wi-Fi | 5/3 | |
| Midea/Carrier pela LAN (interna, externa, consumo) | "O ar do laboratório está ligado? Quanto está lá fora?" | ❓ dongle Wi-Fi | 5/3 | |
| Roteador/ONT: clientes (MAC só pelo roteador), WAN, reiniciar; UPnP IGD sem senha | "Quem está usando a internet? Reinicia o roteador às 4h se cair." | 🔧 depende do modelo | 4/3 | M |
| Diagnóstico ampliado: iperf3 por cômodo, scan de canais, dig, traceroute, speedtest-go | "O Wi-Fi do quarto está pior que o da sala?" | 🧪 base pronta (`diagnostico_rede`) | 3/2 | |
| Segunda "boca" de IR na rede (Broadlink RM4 mini) e tomada com medição (Tuya/Shelly) | "Liga o ar do laboratório (o celular está aqui no quarto)." | 🛒 R$ 60–150 | 4/3 | M |

### Computadores, nuvem e agentes
| Oportunidade | Pedido de exemplo | Estado | Imp/Esf | M |
|---|---|---|---|---|
| **Remote Control no PC** (modo servidor, worktree por sessão) | "No PC de casa, roda os testes e me manda o resumo." | ✅ oficial; falta seu PC | 5/2 | M |
| Dispatch (Claude Desktop pareado, push ao terminar; computer use em macOS/Windows) | "Organiza a pasta Downloads do PC." | ✅ oficial (Pro/Max/Ultra) | 4/1 | |
| Celular como gateway: capacidade `computador` por SSH sobre Tailscale com comando forçado | "O PC está ligado? O que está usando mais memória?" | 🔧 | 4/3 | M |
| Botão no widget → sessão Claude Code na nuvem (`/fire` com log/medição) | (toque) "Analisar o log do controle" → diagnóstico + PR | 🔧 | 3/2 | M |
| Ferramentas do PC direto no chat (Desktop Commander remoto ou MCP próprio com OAuth) | "Procura o PDF da fatura de outubro e resume." | ❓ terceiros/OAuth | 4/2 | M |
| Claude Code dentro do Termux (comunidade, camada glibc) | (aba Code) "Cria um script que mede o Wi-Fi a cada minuto." | ❓ sem suporte oficial | 5/4 | M |

### Observar o resultado (agir → medir → ajustar)
| Oportunidade | Pedido de exemplo | Estado | Imp/Esf | M |
|---|---|---|---|---|
| Ferramenta `verificar`: após cada ação, chama os observadores disponíveis (rede, bip, foto, consumo) e devolve "confirmado/não confirmado" com evidência | "Liga o ar do quarto em 23 °C e me diz se ligou mesmo." | 🔧 sobre as capacidades | 5/2 | M |
| Ouvido: detectar o bip do ar (microfone + FFT com numpy/scipy, pacotes oficiais do Termux) e pausar a busca sozinho | "Descobre o código do ar do laboratório sem eu olhar." | ❓ microfone em 2º plano (issue 648) | 5/2 | M |
| Olho: câmera + visão do Claude (visor do ar, tela da TV); resultado em imagem cabe no conector (~150 mil caracteres) | "Tira uma foto do visor do ar." | ❓ enquadramento | 4/2 | M |
| Tomada com medição (Tuya ~R$ 48–61; Shelly 1PM/EM na caixa) | "O ar ligou? Quanto gastou nesta semana?" | 🛒 ar de 9.000 BTU costuma ir no disjuntor | 5/2 | M |
| Ponte ESP32/ESPHome: receptor IR (`climate_ir` gree/midea), estado sincronizado quando você usa o controle original, RF 433, BLE | "Usei o controle original, atualiza o estado." | 🛒 ~R$ 50–70 | 5/3 | M |
| Termômetro BLE (LYWSD03MMC + firmware pvvx) via ponte: malha fechada de temperatura | "Mantém o quarto em 24 °C até eu acordar." | 🛒 ~R$ 30–50 | 4/2 | M |
| Celular antigo como sentinela fixa (servidor sempre ligado, microfone, câmera) | "Fica de olho no ar do laboratório." | 🛒 usado ~R$ 150–300 | 4/2 | M |

Fontes desta seção: https://esphome.io/components/climate/climate_ir/ · https://esphome.io/components/sensor/xiaomi_ble.html ·
https://github.com/termux/termux-api/issues/648 · https://github.com/termux/termux-packages/tree/master/packages/python-scipy ·
https://support.anthropic.com/en/articles/11503834-building-custom-connectors-via-remote-mcp-servers ·
https://www.github.com/mjg59/python-broadlink.

### O próprio sistema
| Oportunidade | Estado | Imp/Esf | M |
|---|---|---|---|
| Capacidades + execução governada + atualização + reverter (este avanço) | 🧪 | 5/2 | M |
| Dependências declaradas no manifesto (`pip`/`pkg` mostrados e instalados na aprovação) | 🔧 | 3/2 | M |
| Capacidades em git local (histórico, autoteste na ativação, reverter pela conversa) | 🔧 | 4/2 | M |
| Capacidades longas (monitorar 30 min, com progresso) — base pronta em `tarefa(id)` | 🔧 | 4/2 | |
| Aviso "lista mudou" por SSE só quando há mudança (o Claude Code enxerga cap_<nome> sem conversa nova) | 🔧 | 3/2 | |
| MCP Apps: cartão no chat para revisar código e ver gráficos de rede/bateria | 🔧 | 3/3 | |
| OAuth no conector (revogação, conta) | 🔧 | 3/4 | |

## 5. Conexões que mais aumentam a capacidade de criar conexões

1. **Execução governada + capacidades + atualizar_sistema** (feito): transforma qualquer pesquisa em ferramenta
   instalada e reutilizável.
2. **Shell privilegiada (ADB-self/Shizuku) → agente de tela**: qualquer app sem API vira controlável, e as
   configurações do Android ficam observáveis.
3. **Remote Control num PC**: dá um segundo nó com CPU, disco, navegador, IDE e MCPs locais, oficial e sem porta aberta.
4. **Inventário da rede + protocolos locais (TV, Gree, Midea, roteador)**: troca "sinal enviado" por **estado
   medido**, que é a base para testar, medir e ajustar sozinho.
5. **ESP32 por USB/Wi-Fi** 🛒: dá ao celular os sentidos que lhe faltam (receber IR, BLE, sensores, RF 433 MHz).

### Novas frentes (pesquisa de 19/11) — o que mais multiplica

| Frente | O que destrava | Estado | Imp/Esf | M |
|---|---|---|---|---|
| **Gênio na Central da Casa** (sample + conector + db do artefato) | conversa que controla, escreve capacidades, cria painéis, lembra e aprende hábitos | ✅ 2.0 publicada | 5/2 | M |
| **Base fixa**: celular velho com IR (ou Broadlink) parado na casa | o POCO anda com o usuário e o IR precisa de linha de visão; com uma base fixa, "estou chegando, liga o ar" funciona (geocerca no POCO) | 🛒 R$ 60–400 | 5/2 | M |
| **Home Assistant no celular** (Termux + proot, sem root) + **MCP oficial do HA** | +2.000 integrações (Tuya, Xiaomi, Chromecast, câmeras RTSP…), automações e painéis; o Claude fala com tudo pelo MCP do HA | ❓ não oficial, pesado, tomada | 5/4 | M |
| **Assistente offline** (wake word openWakeWord/Vosk + whisper.cpp + modelo pequeno no llama.cpp) | "ei casa, 23 graus" sem internet, sem aprovação, em ~1–2 s | ❓ TFLite no Termux é o risco; bateria | 4/4 | M |
| **Ler o visor do ar sozinho** (recorte + OCR de 7 segmentos com numpy/OpenCV) | confirmação 100% local: envia → fotografa → lê "23" → confirmado | 🔧 | 4/2 | |
| **Olho infravermelho** (câmera com rolling shutter lendo o LED do controle) | aprender o controle original sem hardware; não achei ninguém fazendo isso com controle IR | 🧪 experimento | 5/3 | M |
| **Aparelhos de rede locais** (tinytuya, python-miio, pychromecast) | controle com estado real de Tuya/Xiaomi/Chromecast, se existirem na casa | ❓ depende do que o usuário tem | 4/2 | |
| **Botões físicos NFC** (adesivo + MacroDroid/Tasker → Termux) | encostar o celular na etiqueta da cama = modo dormir | 🛒 R$ 2/etiqueta | 3/2 | |
| **Controle de qualquer lugar** (bot do Telegram por long-polling, só o chat do usuário; ou ntfy) | comandos, fotos e alertas fora de casa sem abrir o Claude e sem porta aberta | 🔧 serviço de terceiros | 4/2 | |
| **Agente de tela** (`tela` + Shizuku; referência: DroidRun/Mobilerun) | o Gênio opera qualquer app (roteador Intelbras, apps dos aparelhos) | 🔧 falta o Shizuku | 5/2 | M |
| **Rotinas na nuvem** (tarefas agendadas do Claude + Gmail + db da Central) | boletim da manhã (sono, temperatura, e-mails) aparecendo no app | ❓ aprovações da organização | 3/2 | |
| **Zelador noturno** (sessão agendada do Claude Code lê os registros, corrige e abre PR) | o sistema se conserta enquanto o usuário dorme; ele só aprova de manhã | 🔧 | 4/3 | M |

Fontes: home-assistant.io/integrations/mcp_server · community.home-assistant.io (HA Core no Android, Wyoming
openWakeWord no Termux) · github.com/clutchthrower/Home-Assistant-For-Android · huggingface.co/blog/Javedalam/wwhisper-cli
· pyimagesearch.com (dígitos de 7 segmentos) · arxiv.org/pdf/1807.04888 · pypi.org/project/tinytuya ·
python-miio.readthedocs.io · github.com/droidrun/mobilerun · archive.cps-vo.org/node/38847 (rolling shutter VLC).

## 6. Limites reais (onde está a barreira)

- **Hardware:** o emissor IR do POCO só transmite. Aprender um controle exige receptor (ESP32/Broadlink/Flipper).
- **Android/permissão:** sem root não há MAC/ARP de outros aparelhos (Android 10+ bloqueia `/proc/net`; 11+ bloqueia
  `ip neigh`); `nmap` só faz connect scan; `mtr`, `tcpdump`, `arp-scan` e `iw` ficam só no repositório root.
  Multicast passivo pode falhar sem MulticastLock: usar consultas ativas com resposta unicast. Scan de Wi-Fi:
  localização ligada e no máximo 4 a cada 2 min.
- **Termux:API sem Bluetooth/BLE** (issue aberta): BLE só por ponte (ESP32) ou app de automação.
- **Sem root, `shell` ≠ root:** ADB/Shizuku não leem dados de outros apps nem passam de FLAG_SECURE (bancos e
  Netflix saem pretos na captura).
- **Segundo plano:** o HyperOS e o phantom process killer matam processos; câmera e microfone podem falhar com a
  tela apagada. O serviço só existe quando ligado (sua escolha de bateria): monitoramento contínuo exige deixá-lo ligado.
- **MCP no claude.ai:** sem SSE o servidor não avisa `tools/list_changed`; a lista fica fixa na conversa (por isso a
  meta-ferramenta). Apps do celular podem guardar a lista antiga até remover e readicionar o conector (relato).
- **Isolamento:** todo script do Termux roda com o mesmo usuário e lê `~/.controle-ir`. A barreira real é a
  aprovação física, a política e a auditoria, não um sandbox.
- **Computadores:** os conectores do claude.ai saem da nuvem da Anthropic e não enxergam sua LAN/tailnet. Remote
  Control exige o PC ligado, com login claude.ai.

## 7. Autonomia com responsabilidade

**Modo autônomo** (`controle-ir exec modo autonomo`, ligado uma vez no celular com consentimento físico): o Claude
age sem pedir aprovação a cada passo — executa qualquer classe e ativa as capacidades que cria na hora. É o "modo
deus" na prática: uma intenção vira pesquisa → ferramenta → execução → observação → ajuste numa conversa só. O que
sustenta isso com segurança, sem atrito recorrente:
- **Consentimento é único e físico:** o perfil só muda no celular; nenhuma ferramenta MCP o altera.
- **Freio sempre a um comando:** `travar` nega tudo e encerra tarefas, de qualquer aparelho, sem código.
- **Tudo auditado:** `auditoria.jsonl` e `tarefas/` registram cada ação; o console avisa que o modo está ligado.
- **Só o Claude alcança o conector:** `origens exigir` aceita apenas `160.79.104.0/21`.
- **Recuperável:** `atualizar_sistema` guarda a versão anterior; o atalho Reverter volta mesmo se o Python quebrar.
O teto deixa de ser "quantas vezes você autoriza" e passa a ser só o que o hardware/OS permitem (§6) e a linha
ética: agir sobre o que é seu ou que você tem permissão para acessar — nunca invadir rede, conta ou equipamento de terceiros.



- **O Claude pede, o usuário concede:** pelo toque no celular ou pelo sim no chat (de qualquer aparelho).
  Classes e modo de aprovação só mudam no celular (há teste disso).
- **Classes:** leitura roda direto; rede, pacotes e livre perguntam (ou rodam dentro de uma janela "liberar N min");
  sistema (atualizar) sempre pergunta. Ajuste fino: `controle-ir exec classe rede permitir`.
- **De qualquer aparelho:** o conector funciona igual no iPad, na web e no celular. Aprovações pelo chat
  (padrão `chat`): o Claude pergunta, o usuário diz sim, o Claude chama `autorizar`; o celular notifica e
  audita. Opcional mais rígido: modo `codigo` (TOTP de app autenticador, uso único, bloqueio após 5 erros).
- **Parar tudo:** `controle-ir exec travar`, o atalho "Desligar Controle IR" ou o botão Desligar da notificação.
- **Histórico:** `controle-ir exec historico`; tarefas em `~/.controle-ir/tarefas/<id>.json` e `.log`.
- **Recuperação:** atualização guarda `~/controle-ir.anterior`; o atalho "Reverter Controle IR" (só shell) volta.
  Antes de mexer em rede ou roteador: medir antes, aplicar uma mudança reversível, medir depois, desfazer se piorar.
- **Credenciais:** `~/.controle-ir/config.json` (600) com o segredo do conector e um token só local para aprovações;
  tokens de serviços futuros no mesmo lugar, nunca no repositório.

## 8. Próximos experimentos (ordem sugerida)

Feito até 19/11: instalação pelo Claude (`atualizar_sistema`, hoje na 1.0.18), capacidades e execução confirmadas
no POCO, modo autônomo, `descobrir_rede` (a TV e os ares não estão na rede: só IR), confirmação pelo som e pela
câmera, termômetro pela bateria, agente de tela escrito, Central da Casa 2.0 com o Gênio.

1. **Shizuku + rish** (o usuário ativa em 20/11) → testar `tela` → o Gênio passa a operar qualquer app.
2. **Instalar a 1.0.19** (sono e sonar) → uma noite do laboratório do sono e o teste do sonar.
3. **Ler o visor do ar** (recorte + 7 segmentos) → confirmação 100% local.
4. `controle-ir origens` depois de algumas chamadas: se tudo vier de `160.79.104.0/21`, ligar `controle-ir origens exigir`.
5. **Base fixa** (celular velho com IR ou Broadlink) + geocerca no POCO → "estou chegando, liga o ar".
6. Experimento do **olho infravermelho** (rolling shutter) para aprender o controle original sem hardware.
7. PC: `claude remote-control --spawn worktree` num terminal do computador (ou Claude Desktop + Dispatch).

## 9. Perguntas (respondidas, destravam frentes inteiras)

1. **TV:** modelo na etiqueta traseira? Está no Wi-Fi? A opção "Ligar com celular" está ativa?
2. **Ares:** o controle do Gree tem tecla WiFi? O Carrier e o Midea têm dongle ou app (Gree+, MSmartHome, NetHome)?
   O laboratório usa outra rede?
3. **Roteador:** marca e modelo, é da operadora, e você tem a senha de admin?
4. **Computador:** Windows, macOS ou Linux? Fica ligado quando você sai? Qual o seu plano no claude.ai (Pro/Max/Ultra/Team)?
5. **Android:** versões exatas do HyperOS e do Android (Configurações → Sobre)? A tela tem PIN? Algum app de banco
   recusa abrir com as opções do desenvolvedor ligadas?
6. **Política:** quais classes podem rodar sem perguntar (sugestão: leitura sempre; rede liberada; pacotes e livre perguntando)?
7. **Compras:** topa R$ 60–150 em um ESP32 + receptor IR + sensor (ou um Broadlink RM4 mini / tomada com medição)?

## 10. Hipóteses de produto (a investigar)

- **"Controle universal com IA" para quem tem celular com emissor IR** (Xiaomi/POCO/Redmi são comuns no Brasil):
  descobrir o controle por testes, criar botões que o controle original não tem e operar por voz/chat. Público:
  usuários de ar split sem Wi-Fi. Diferencial comprovado aqui: gerar o quadro Gree a partir da captura real.
- **Diagnóstico de internet doméstica com evidência** para levar ao provedor: medições históricas por cômodo,
  separação Wi-Fi × roteador × provedor, relatório. Público: quem sofre com a operadora; pequenos escritórios.
- **"Ar observável" para anfitriões de Airbnb/pousadas e técnicos de refrigeração (PMOC):** ESP32 com IR,
  receptor e sensor, mais relatório de uso e temperatura. Hipótese: confirmar demanda e a exigência legal.
- **Kit "dê sentidos ao celular"** (ESP32 com receptor IR, sensor de temperatura e BLE por USB-C, mais as capacidades
  prontas). Público: entusiastas de automação sem Home Assistant.

## Fontes principais

Termux:API (scripts) https://github.com/termux/termux-api-package/tree/master/scripts · BLE ausente
https://github.com/termux/termux-api/issues/713 · phantom killer https://github.com/termux/termux-app/issues/2366 ·
Shizuku https://shizuku.rikka.app/guide/setup/ · RUN_COMMAND https://github.com/termux/termux-app/wiki/RUN_COMMAND-Intent ·
samsungtvws https://pypi.org/project/samsungtvws/ · greeclimate https://pypi.org/project/greeclimate/ ·
msmart-ng https://pypi.org/project/msmart-ng/ · tinytuya https://github.com/jasonacox/tinytuya ·
python-broadlink https://pypi.org/project/broadlink/ · tplinkrouterc6u https://pypi.org/project/tplinkrouterc6u/ ·
pacotes Termux https://packages.termux.dev/apt/termux-main/dists/stable/main/binary-aarch64/Packages ·
Wi-Fi scan https://developer.android.com/develop/connectivity/wifi/wifi-scan ·
Remote Control https://code.claude.com/docs/en/remote-control · Desktop/Dispatch https://code.claude.com/docs/en/desktop ·
routines/fire https://code.claude.com/docs/en/routines · conectores (IPs, OAuth)
https://claude.com/docs/connectors/building/authentication · MCP transports
https://modelcontextprotocol.io/specification/2025-11-25/basic/transports · MCP 2026-07-28
https://modelcontextprotocol.io/specification/2026-07-28/changelog · cache de ferramentas
https://github.com/anthropics/claude-code/issues/38324 · MCP Apps https://claude.com/blog/interactive-tools-in-claude ·
código como habilidade reutilizável https://www.anthropic.com/engineering/code-execution-with-mcp ·
Claude Code no Android (comunidade) https://github.com/ferrumclaudepilgrim/claude-code-android ·
Desktop Commander https://github.com/wonderwhy-er/DesktopCommanderMCP.
