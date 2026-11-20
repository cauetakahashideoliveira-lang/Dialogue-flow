# Controle IR do POCO + Claude

> **Vai continuar o projeto (outro dev/outro repositório)?** Comece por [`docs/HANDOFF.md`](docs/HANDOFF.md) — arquitetura, como publicar, o que existe só no celular, credenciais e como migrar.

Controle remoto infravermelho universal para o **POCO X8 Pro Max** (ou qualquer Android com emissor IR),
comandado pelo **Claude** numa conversa normal, inclusive pelo app do celular, por meio de um conector **MCP**.

> “Ligue o ar do quarto em 23 °C, modo frio, ventilação baixa.”  
> “Descubra qual controle funciona nesse ventilador. Não sei a marca.”  
> “Aumente o volume da soundbar três passos.”

## Como funciona

```
Claude (app/web) ──HTTPS──▶ túnel Cloudflare ──▶ Termux no POCO (127.0.0.1:8765)
                                                   ├─ servidor MCP  (/mcp/<segredo>)
                                                   ├─ painel local  (/painel)
                                                   ├─ catálogo SQLite (≈640 perfis base; ≈9 mil com o ampliado)
                                                   └─ termux-infrared-transmit ─▶ emissor IR do Android
```

| Peça | O que faz |
|---|---|
| `controle_ir/protocolos.py` | Gera e reconhece NEC/NECext/NEC42, Samsung32, RC5/RC5X, RC6, Sony SIRC 12/15/20, Kaseikyo, RCA e Pioneer (frequência, temporização, endereço, comando, repetição). |
| `controle_ir/sinais.py` | Sinal único em 4 formas (protocolo, bruto, Broadlink, Pronto), impressão para eliminar duplicatas, limite de 2 s do Android, saneamento de capturas corrompidas. |
| `controle_ir/vocabulario.py` | Converte qualquer nome de tecla em função com nome em português e tipo (`tecla`, `alternar`, `definir`, `ajustar`) e marca comandos de serviço/restauração. Nome desconhecido vira comando personalizado. |
| `controle_ir/catalogo.py` | Catálogo SQLite: um sinal pode pertencer a vários perfis; perfis de estado completo guardam a tabela inteira. |
| `controle_ir/descoberta.py` | Bateria de testes no celular: fila priorizada, lotes, intervalo ajustável, pausa imediata, suspeitos, reteste, confirmação, testes de distinção, retomada após reiniciar. |
| `controle_ir/controle.py` | Planejador: tecla direta, passos (com saturação quando a faixa é conhecida), alternância só com estado conhecido, configuração completa de ar-condicionado, relato de falha no meio. |
| `controle_ir/mcp.py` / `servidor.py` | MCP sobre Streamable HTTP (JSON), painel e API, notificação com **Reagiu — pausar**. |

### Por que Termux e não um APK
Avaliei um app Android próprio (ConsumerIrManager). A parte difícil não é o infravermelho, e sim manter um
servidor público HTTPS para o Claude: isso exige embutir e manter um túnel dentro do APK, e eu não teria como
testar no seu aparelho. O caminho com **Termux + Termux:API + cloudflared** já foi validado no seu POCO
(`termux-infrared-frequencies` respondeu de 30 a 56 kHz), atualiza com uma linha e usa pacotes mantidos.
O “app” no celular é o painel (navegador) mais a notificação persistente com botões.

## Instalação (uma etapa por vez)

Requisitos: **Termux** e **Termux:API**, ambos do F-Droid (mesma fonte).

1. Abra o **Termux** e cole esta linha inteira; aperte **Enter**:

   ```
   pkg install -y curl unzip && curl -fL -o "$TMPDIR/controle-ir.zip" https://github.com/cauetakahashideoliveira-lang/Dialogue-flow/raw/claude/ir-control-poco-setup-u46urr/dist/controle-ir.zip && unzip -o "$TMPDIR/controle-ir.zip" 'controle-ir/*' -d "$HOME" && bash "$HOME/controle-ir/instalar.sh"
   ```

   *(Alternativa: baixe o ZIP pelo navegador e use `termux-storage-get "$TMPDIR/controle-ir.zip"` para escolhê-lo.)*

2. O instalador mostra 7 etapas: pacotes → emissor → comando → perfis → catálogo ampliado (pergunta **S/n**) →
   início automático (pergunta **s/N**, veja abaixo) → servidor. Se algo falhar ele diz **qual etapa** e o motivo.
   Rodar de novo atualiza: o serviço antigo é encerrado sozinho e aparelhos, catálogo e segredo são mantidos.
3. No fim aparece a **URL privada** do conector. Digite `copiar` e **Enter**. Não envie a URL a ninguém e
   cubra-a em capturas de tela: ela contém o segredo de acesso ao emissor.

**HyperOS/MIUI:** Configurações → Apps → Termux (e Termux:API) → Economia de bateria → **Sem restrições**;
ative também **Início automático**. O serviço segura um *wake lock* enquanto roda.

### Ligar e desligar com um toque (Termux:Widget)

Para economizar bateria, deixe o serviço desligado e ligue só quando for usar:

1. Instale o app **Termux:Widget** do F-Droid (mesma fonte do Termux).
2. O instalador já cria os atalhos (ou rode `controle-ir atalhos`).
3. Toque e segure num espaço vazio da tela inicial → **Widgets** → **Termux:Widget** → arraste o
   **Termux shortcut** e escolha **Ligar Controle IR**; repita com **Desligar Controle IR**.

**Ligar** abre o serviço em segundo plano e avisa "Controle IR ligado" na tela; **Desligar** encerra tudo e solta o
*wake lock* (o que mais gasta bateria). A notificação "Controle IR ativo" também tem o botão **Desligar**.
No terminal: `controle-ir ligar` / `controle-ir desligar`.
Outros atalhos criados junto: **Modo autonomo**, **Modo cauteloso** e **Travar** (freio), além de **Reverter**. Com o serviço desligado o Claude não alcança o celular:
ligar precisa ser no celular.

### Botão Stockfish para estudos

Escolha **Stockfish** no seletor do **Termux shortcut** para fixar o botão na tela inicial.
Cada toque abre o motor instalado no POCO e mostra uma sugestão na posição inicial. Digite os
lances como `e2e4 e7e5`. Pressione Enter para consultar a posição, use `voltar` para desfazer
um lance ou `sair` para fechar. O estudo funciona offline, inclusive com o serviço Controle IR desligado.
O comando equivalente no Termux é `controle-ir stockfish`.

Para jogar, digite `piloto` no atalho e abra o tabuleiro no Chess.com. O motor aguarda as 64 casas
e consulta o histórico de lances para identificar a vez numa partida em andamento. Ao trocar de app,
o piloto espera e retoma quando você volta. Se o histórico estiver oculto e já for sua vez ao ativar,
use `piloto agora`.
Esse modo usa o Shizuku e as permissões vigentes do Controle IR. Digite `parar` para cancelar
uma ativação pendente ou encerrar o piloto. Se faltar o motor, instale-o com `pkg install stockfish`.

### Início automático quando o celular liga (Termux:Boot)

1. Instale o app **Termux:Boot** do F-Droid (mesma fonte do Termux) e **abra-o uma vez**.
2. HyperOS: Configurações → Apps → Termux:Boot → **Início automático** ativado e Economia de bateria
   **Sem restrições**.
3. No Termux: `controle-ir inicio-automatico sim` (ou responda **s** na etapa 6 do instalador).

O comando cria `~/.termux/boot/controle-ir`, que segura o *wake lock* e roda `controle-ir iniciar --fundo`:
o serviço sobe sem console, grava o registro em `~/.controle-ir/servico.log` (sem o segredo; veja com
`controle-ir log`) e mostra a notificação fixa **Controle IR ativo** (botões *Painel*, *Copiar URL* e *Desligar*).
Com o início automático ativado, digitar `controle-ir` também abre o serviço em segundo plano e mostra só o
**console**: Enter pausa a busca, `c` continua, `copiar`, `url`, `painel`, `log`; `sair`, CTRL+C ou fechar o Termux
fecham só o console, e o conector continua no ar. `parar` (no console) ou `controle-ir parar` encerra o serviço.
Para desligar: `controle-ir inicio-automatico nao`. Conferir: `controle-ir status`.

## Conectar ao Claude

* **Pro/Max (individual):** em claude.ai, *Personalizar → Conectores* → **+ Adicionar** →
  **Adicionar conector personalizado** → nome `Controle do POCO` → cole a URL → *Continuar* →
  autenticação **Sem login** (*No sign in*) → **Adicionar**. No plano gratuito cabe um conector personalizado.
* **Team/Enterprise:** um proprietário cadastra em *Configurações da organização → Conectores* → **Adicionar** →
  *Personalizado* → *Web* (mesmos campos); depois cada pessoa abre *Personalizar → Conectores* e clica
  **Conectar**.
* Numa conversa, ative o conector pelo botão **+** → *Conectores*. Conectores remotos funcionam também nos apps
  do celular.

Primeiro teste: peça “use a ferramenta consultar”. A resposta traz as marcas reais do catálogo do POCO.

## Uso no dia a dia

| Você diz | O Claude chama |
|---|---|
| “Descubra o controle desse aparelho, não sei a marca” | `buscar` (sem filtros, por popularidade, em lotes) |
| “É um ventilador antigo” | `buscar(categoria="ventilador")` |
| “Ligou!” / “Apitou!” | `pausar` → suspeitos → `retestar` um por vez → `confirmar` |
| “Esse funcionou. Salve como ventilador da sala” | `salvar_aparelho` |
| “Ligue o ar do quarto em 23 °C, frio, ventilação baixa” | `controlar(ligar, definir={...})`: uma transmissão |
| “Agora só 22 °C” | `controlar(definir={temperatura:22})`: modo e ventilação mantidos |
| “Na TV do quarto, HDMI 2” | tecla direta `entrada_hdmi2` |
| “Volume da soundbar +3” | `ajustar={volume:3}` |
| “Fita LED azul e menos brilho” | `definir={cor:"azul"}, ajustar={brilho:-1}` |
| “Repita a apresentação no projetor” | `controlar(macro="apresentação")` |

Regras que o servidor aplica:

* **Resumo dos aparelhos ao conectar:** as instruções do conector trazem, para cada aparelho salvo, o nome exato,
  os valores aceitos (modo, faixa de temperatura, ventilação, entradas…), as teclas, os botões criados por você,
  as macros, os aparelhos que respondem aos mesmos códigos e a sua observação
  (`editar_aparelho(observacao="…")`). Assim o Claude chama `controlar` direto e só usa `opcoes` para o último
  estado ou para algo fora do resumo. O resumo não leva o estado, que mudaria durante a conversa.
* **Alternância sem estado** (só existe “liga/desliga”): nada é enviado até você dizer o estado atual ou
  autorizar; depois disso o estado presumido evita inverter.
* **Velocidade 2 com só “+/−”**: com a faixa conhecida (`editar_aparelho(faixas={velocidade:{min:1,max:3}})`),
  desce até o mínimo e sobe; sem faixa, explica o que falta.
* **Falha no meio**: devolve `enviados` e `pendentes`, para não repetir volume ou alternância.
* **Último comando × estado real**: `ultimo_envio` e `confirmado` ficam separados; `registrar_estado`
  com `controle_original_usado=true` invalida o que foi presumido.
* Comandos de **serviço, restauração e programação** nunca entram nos testes automáticos e só são enviados com
  `permitir_servico=true`.

### Descoberta
* Pausar: **Enter sozinho** no Termux (na tela do serviço ou no console, quando ele roda em segundo plano), o
  botão **Reagiu — pausar** no painel ou na notificação, ou dizer ao Claude.
* Suspeitos: o último sinal e os enviados dentro da janela de reação (`intervalo + 10 s`).
* Vários perfis com o mesmo sinal: `confirmar` propõe **testes de distinção** com outra função
  (volume, mudo, cor…); `distinguir(teste, variante)` envia cada variante.
* Só uma tecla funcionou: `salvar_aparelho(somente_confirmado=true)` e depois `buscar(modo="teclas")` testa as
  outras teclas dos perfis relacionados (`varredura=true` também gera comandos do mesmo endereço do protocolo).
* Nada funcionou: `progresso` mostra o que foi coberto; amplie o catálogo, importe um perfil SmartIR/Flipper do
  modelo (`importar`) ou um sinal capturado por receptor externo (Flipper Zero, Broadlink, ESPHome; formatos
  `.ir`, Pronto, Broadlink, `38000: 9000 4500 …`).

## Capacidades plugáveis (ferramentas novas sem mexer no núcleo)

Uma capacidade é uma pasta com `capacidade.json` (nome, descrição, argumentos em JSON Schema, acessos, efeito,
tempo limite) e um script `.py` ou `.sh` que lê os argumentos em JSON na entrada e escreve o resultado em JSON.
O servidor relê as pastas a cada chamada: não precisa reiniciar.

* **Embutidas** (`controle-ir/capacidades/`): `diagnostico_rede` — Wi-Fi (sinal, frequência, enlace), perda e
  latência até o roteador e a internet, DNS, download, histórico em `~/.controle-ir/medicoes/rede.jsonl` e um
  diagnóstico (Wi-Fi × roteador × provedor × DNS) com sugestões reversíveis; `estado_celular` — bateria, Wi-Fi,
  armazenamento, carga, comandos do Termux:API disponíveis.
* **No Claude:** `capacidades` (listar, ver código, anotar resultado confirmado), `executar_capacidade` e uma
  ferramenta `cap_<nome>` por capacidade ativa (aparece nas conversas novas).
* **Criar durante a conversa:** o Claude escreve o script e chama `propor_capacidade`. Nada roda até você tocar em
  **Aprovar** na notificação (ou **Ver código** antes). A aprovação grava o SHA-256 dos arquivos: se o código mudar,
  volta a exigir aprovação. As suas ficam em `~/.controle-ir/capacidades/` e sobrevivem a reinícios e atualizações.
* Terminal: `controle-ir capacidade listar | ver NOME [--abrir] | aprovar NOME | recusar NOME | remover NOME |
  executar NOME --args '{"rapido": true}'`.

## Execução governada, atualização e recuperação

* `executar_comando` (MCP) roda uma linha de shell no Termux como **tarefa numerada** (saída em arquivo;
  `tarefa(id)` acompanha ou para). A **política só muda no celular**: leitura roda direto; rede, pacotes e o resto
  pedem aprovação na notificação (**Executar / Negar / Liberar 30 min**); `sistema` (atualizar) sempre pergunta.
  `controle-ir exec politica | classe <classe> permitir|perguntar|negar | liberar <min> | travar | destravar | historico`.
* `atualizar_sistema(ref=<commit>)` / `controle-ir atualizar --ref <commit>`: baixa o pacote do commit, guarda a
  versão atual em `~/controle-ir.anterior`, instala e religa. Se o acesso não voltar: atalho **Reverter Controle IR**
  (só shell) ou `controle-ir reverter`.
* **Modo autônomo (rédea solta):** `controle-ir exec modo autonomo` no celular, uma vez. A partir daí o Claude
  pesquisa, cria a ferramenta, roda, observa e ajusta na mesma conversa **sem pedir** a cada passo, e as
  capacidades que ele cria já entram ativas. O console mostra um aviso de que o modo está ligado, toda ação
  continua no `auditoria.jsonl`, e `controle-ir exec travar` (ou "trava tudo" no chat) é o freio imediato.
  Perfis: `autonomo` | `cauteloso` (padrão, pede o que age) | `leitura` (só olhar).
* **De qualquer aparelho (iPad, web, celular):** quando algo pede aprovação, o Claude pergunta no chat e, com o
  seu sim, aprova (`autorizar`); "libera por 2 horas" para de perguntar nesse tempo. Toda aprovação feita
  assim aparece como notificação no celular e fica no histórico. `travar` encerra tudo de qualquer lugar.
  Modos no celular: `controle-ir exec remoto chat` (padrão) | `codigo` (exige o código de um app
  autenticador, `controle-ir exec codigo configurar`) | `desligada` (só pela notificação).
* Auditoria de cada ferramenta e tarefa: `~/.controle-ir/auditoria.jsonl`.
* Visão completa, mapa de oportunidades e limites: [docs/modo-deus.md](docs/modo-deus.md).

## Reabrir, atualizar a URL, URL fixa

* Reabrir o serviço: abra o Termux e digite `controle-ir`.
* O túnel rápido (`trycloudflare.com`) **muda de endereço quando reinicia**. Quando aparecer
  “A URL DO TÚNEL MUDOU”, digite `copiar`, remova o conector no Claude e adicione de novo com a nova URL.
  O segredo continua o mesmo; `controle-ir novo-segredo` gera outro.
* URL fixa (opcional): `controle-ir tunel cloudflare --token <token> --url https://ir.seudominio` (túnel
  nomeado da Cloudflare) ou `controle-ir tunel ngrok --dominio seu-nome.ngrok-free.app` (ngrok com domínio
  estático e `ngrok config add-authtoken` feito antes).
* Outros comandos: `controle-ir painel`, `controle-ir status`, `controle-ir pausar`, `controle-ir catalogo ampliar`,
  `controle-ir importar arquivo.ir`, `controle-ir parar`, `controle-ir ligar|desligar`, `controle-ir atalhos`,
  `controle-ir inicio-automatico sim|nao`, `controle-ir log`.

## Segurança
* O servidor escuta só em `127.0.0.1`; o acesso externo exige a URL com segredo de 256 bits (ou
  `Authorization: Bearer`). Comparação em tempo constante, recusa de `Origin` estranha (403), GET → 405.
* Os logs não registram URLs. `~/.controle-ir/config.json` fica com permissão 600.
* Painel e `/api` (aprovar, pausar, travar) usam um **token só local** e recusam chamadas vindas do túnel:
  quem tiver a URL do conector não aprova nada. Aprovação de capacidade presa ao SHA-256 revisado.
* `controle-ir origens` mostra de onde vêm as chamadas ao conector; `controle-ir origens exigir` aceita só
  a rede da Anthropic (`160.79.104.0/21`). Confirme primeiro no modo observar (padrão).

## O que foi verificado e o que depende do seu POCO

| Verificado por software (neste repositório) | Depende do POCO e de um aparelho físico |
|---|---|
| 14 protocolos: ida e volta codificar→decodificar (200 casos aleatórios cada) | Alcance e ângulo do emissor do POCO |
| Amostra de ~6 mil capturas reais da Flipper-IRDB: ~1,5 mil reconhecidas como NEC, RC5, Kaseikyo etc. com bytes de verificação válidos (as demais seguem como sinal bruto) | Se cada perfil do catálogo realmente aciona o seu aparelho |
| 161.666 sinais do catálogo base convertem para transmissão válida (≤ 2 s) | Tempo de resposta do Termux:API em cada envio |
| Planejador: ar-condicionado SmartIR (pedido composto, só temperatura, oscilação ausente, desligar), ventilador Flipper (alternância, saturação, falha no meio), projetor (HDMI 2 direto), fita LED (cor) | Notificação e botões no HyperOS |
| Descoberta: pausa < 3 s, suspeitos, reteste, confirmação, distinção até 1 perfil, lote, retomada após reinício | Túnel `cloudflared` na rede do celular |
| MCP: 58 testes automatizados (incluindo resumo dos aparelhos e serviço em segundo plano) + cliente oficial do SDK MCP (protocolo 2026-07-28 negociado para 2025-11-25) | Cadastro do conector na sua conta do Claude |
| Instalação completa num Termux simulado (pacotes, emissor, catálogo, túnel, `copiar`, `pausar` pela notificação) | Termux:Boot abrindo o serviço quando o HyperOS liga |
| Segundo plano: registro sem segredo (600), instância única, console por pty, `parar` sem matar pid reaproveitado | |

## Desenvolvimento

```
python3 -m unittest discover -s testes -v              # testes
python3 ferramentas/construir_catalogo.py --smartir ... --flipper ...   # regenera dados/base.jsonl.gz
ferramentas/empacotar.sh                                # gera dist/controle-ir.zip
python3 -m venv /tmp/v && /tmp/v/bin/pip install mcp && /tmp/v/bin/python ferramentas/verificar_cliente_mcp.py
PYTHONPATH=controle-ir python3 -m controle_ir iniciar --simulado --sem-tunel   # servidor sem celular
```

Licenças dos dados: veja `controle-ir/LICENCAS/LEIA-ME.md` (SmartIR — MIT; Flipper-IRDB — CC0 para
contribuições a partir de ago/2025; a Flipper-IRDB completa é baixada pelo usuário no celular).

