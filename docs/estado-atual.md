# Estado atual da instalação (19/11/2026)

## Resumo (fim do dia 19/11)
- **Celular:** POCO X8 Pro Max, HyperOS 3 (Android 16), Termux + Termux:API (F-Droid). Servidor **1.0.27**, pareado com a
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

## Pendências (próxima conversa)
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
