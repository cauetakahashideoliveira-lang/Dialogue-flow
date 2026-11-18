# Estado atual da instalação (18/11/2026)

## Celular
- POCO X8 Pro Max, Android/HyperOS, Termux + Termux:API (F-Droid).
- Emissor IR confirmado: 30, 33, 36, 38, 40 e 56 kHz.
- Termux precisou de `apt update && apt full-upgrade` (curl quebrado por openssl antigo).
- Catálogo instalado: base + ampliado (Flipper-IRDB completa) = 9.380 perfis, 94.407 sinais únicos, 1.776 marcas.
- Servidor no celular na versão 1.0.4. O repositório tem a **1.0.7**: ligar/desligar com um toque (Termux:Widget), início automático com Termux:Boot,
  serviço em segundo plano com console, e resumo dos aparelhos nas instruções do conector. A 1.0.5 só corrigia
  a resposta de `editar_aparelho` quando o sinal já existe. **Falta atualizar o celular** (ver "Pendências").

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

## Pendências
- **Atualizar o celular para a 1.0.7** (a linha de instalação com o hash do commit; o instalador encerra o
  serviço antigo sozinho e reconstrói o catálogo, o que leva alguns minutos com o ampliado).
- **Pôr os atalhos na tela inicial:** instalar o app Termux:Widget (F-Droid) → tela inicial → Widgets →
  Termux:Widget → "Termux shortcut" → "Ligar Controle IR" (e "Desligar Controle IR").
- **Opcional — início automático no celular** (gasta mais bateria, serviço sempre ligado): instalar o app Termux:Boot (F-Droid) e abri-lo uma vez; HyperOS →
  Apps → Termux:Boot → Início automático + bateria Sem restrições; responder **s** na etapa 6 do instalador
  (ou `controle-ir inicio-automatico sim`). Depois, reiniciar o celular e conferir no Claude com `consultar`.
- Depois da atualização, gravar as ressalvas como observação de cada aparelho (`editar_aparelho(observacao=…)`)
  para chegarem ao Claude pelo resumo: extras do ar do quarto fixam 16 °C/frio/automática; desligar direto da TV
  ainda não testado; escritório e laboratório compartilham códigos (este último o resumo já detecta sozinho).

## Implementado no repositório em 18/11 (versões 1.0.6 e 1.0.7, ainda não instaladas no celular)
- **Ligar/desligar com um toque (1.0.7):** atalhos "Ligar Controle IR" e "Desligar Controle IR" em
  `~/.shortcuts/tasks` para o app Termux:Widget (o instalador cria; `controle-ir atalhos`); `controle-ir
  ligar|desligar` avisam na tela; botão Desligar na notificação. O usuário prefere ligar só quando for usar,
  para poupar bateria: se o conector não responder, peça para tocar em "Ligar Controle IR".
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
