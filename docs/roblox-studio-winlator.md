# Roblox Studio + Claude Code no POCO (Winlator): passagem de trabalho

Estado em 25/11, 08:12 (horário do celular). Este documento é para quem continua o projeto.

## Missão do dono

Seguir o guia "PASSO A PASSO - ROBLOX STUDIO + CLAUDE CODE (WINDOWS)" no POCO X8 Pro Max, sem PC, com o Studio
dentro do Winlator e o máximo desempenho. Os passos do guia:

1. Instalar Git, Roblox Studio e Claude Code (`irm https://claude.ai/install.ps1 | iex`).
2. Instalar o Rokit e clonar `cauetakahashideoliveira-lang/Roblox-profissional-developer`, na branch
   `claude/new-session-hla5e4`.
3. Rodar `rokit install` (confiar em rojo, StyLua e lune), depois `lune run verificar`, que deve terminar com
   "Resultado: build confirmado", e por fim `rojo plugin install`.
4. No Studio: criar um Baseplate e ligar Assistant → Settings → MCP Servers → "Enable Studio as MCP server".
   **Não** ligar "Quick connect".
5. No Claude: `claude` → `/plugin` → "Roblox Studio" (Roblox/roblox-studio-agent-plugin). Em `/mcp` deve aparecer
   `plugin:roblox-studio:windows` conectado.
6. Rodar `rojo serve examples/bridge-check/default.project.json` (porta 34872) e, no Studio, Plugins → Rojo →
   Connect. Deve aparecer ServerScriptService > BridgeCheck > Probe.
7. Rodar `/rbx-studio-check testar a ponte` (bridge-01 → bridge-02).

Regras do dono:
- Logins quem faz é ele. Nunca digitar senha.
- Responder em português.
- O modo autônomo vale, mas parar no que for arriscado ou irreversível.
- Regras de tela: `CLAUDE.md` (nunca entrar em Opções do desenvolvedor, Shizuku, Termux, Contas etc.).
- Os docs do repositório Roblox dizem: **nunca exponha o Studio na internet**. O MCP do Studio é stdio
  (`%LOCALAPPDATA%\Roblox\mcp.bat`), então o Claude Code precisa rodar no mesmo Windows (docs/ambiente.md §5
  daquele repositório).

## O que já está pronto

### Winlator 11.2 (Container-1)
- Tela 1280x720.
- Vortek: Vulkan 1.3, 152 extensões ligadas.
- DXVK 2.4.1, VKD3D 2.14.1.
- Box64 no preset "Desempenho", Windows 10, 8 núcleos.
- Benchmark do 7-Zip: 78% do nativo com 8 threads e 86% com 1 thread.
- A unidade D: é `/storage/emulated/0/Download`.
- O toque funciona como touchpad: o dedo arrastado move a seta, quase 1:1 se o arrasto for lento (arrastos
  longos e rápidos aceleram cerca de 1,5×); um toque clica onde a seta está.
- Para reconhecer a seta na posição (0,0), basta empurrá-la ao canto com dois arrastos (2400,1100)→(300,150).

### Roblox Studio
- Versão `version-8d7a1009c17e4ff8`, instalada em `C:\Program Files\Roblox\Versions\...`.
- **Logado** com a conta do dono. O login fica guardado e volta sozinho quando o Studio reabre
  (o log mostra `Authenticated : YES`).

### Ferramentas nativas no Termux
- Ficam em `~/roblox-tools/bin`: rojo 7.7.1 e lune 0.11.1 (pelo `grun`, glibc) e stylua (musl).
- O projeto está em `~/Roblox-profissional-developer`. O `lune run verificar` já passou.
- O GitHub ainda **não** está logado no Termux. O clone foi feito por bundle, e para dar push é preciso o
  `gh auth login` do dono.

### Arquivos em Download (D:)
`Rojo.rbxm` (o plugin 7.7.1), `RobloxStudioInstaller.exe`, `Winlator_11.2.apk`, `dxvk110/`, `diag/`.

## Login do Studio pelo navegador (resolvido)

O login embutido falha no Wine; "Entrar via Navegador" manda para o Chrome com `redirect_uri=roblox-studio-auth:/`.
O Android não tinha quem recebesse esse endereço, então foram criadas três peças:

- **App "Retorno Roblox Studio"** (`br.controleir.retornostudio`, fonte em `ferramentas/winlator/retorno-studio/`):
  - Recebe `roblox-studio-auth:` e registra a URL no logcat, com a tag `RetornoStudio`.
  - Já está instalado.
  - O APK foi compilado com `android.jar` 35 e `build-tools` 35.0.1, e assinado com uma chave descartável.
- **Vigia no Termux** (`~/roblox-tools/bin/pegar-login-studio`):
  - Lê o logcat pelo rish e, quando chega uma URL nova, grava `D:\r.bat`.
  - O `r.bat` chama `"...\RobloxStudioBeta.exe" "<url>"` **direto**. O `start "" "<url>"` do Wine quebra com
    0xC0000005.
- **Laço no Windows** (`D:\espera.bat`, aberto com `cmd /c D:\espera.bat`):
  - Roda cada `D:\r.bat` novo e o renomeia para `r-usado.bat`.
  - Registra o que fez em `D:\auth-log.txt`.
  - É um **canal de comandos do Termux para dentro do Wine**, sem tela: basta gravar `r.tmp` e fazer
    `mv r.tmp r.bat` (com CRLF).

O código do login vence em poucos minutos, então a entrega precisa ser automática. Com as três peças, ela leva
cerca de 2 s. O HyperOS abre o Chrome em tela dividida com o Winlator. A página mostra "Continuar" (conta já
logada); é preciso rolar a metade de cima para ver o botão.

## Armadilhas já encontradas

- **Nunca** abrir o Winlator pela intent do lançador (`monkey`, `am start ... LAUNCHER`, `cap_tela abrir`) com a
  sessão rodando. Isso empilha uma `MainActivity` nova e o Winlator encerra o Wine (EXIT_SELF). Volte pelos
  recentes, ou arraste a divisória da tela dividida até o topo, devagar (cerca de 900 ms).
- **Nova Tarefa** (menu: tecla voltar → Gerenciador de Tarefas → Nova Tarefa):
  1. Tocar no campo em (1750,623) e apagar 14 vezes.
  2. Digitar o comando.
  3. Tocar **sozinho** em CONCLUÍDO do teclado, em (2572,235).
  4. Só então tocar em OK. Tocar em OK com o teclado aberto digita uma letra a mais.
- Com o cmd na frente, o Enter não chega às caixas do Studio. É preciso clicar com a seta.
- O aviso "placa de vídeo não compatível" aparece a cada abertura do Studio; fecha-se com OK.

## Bloqueio atual: vídeo (onde parei)

1. Com o DXVK 2.4.1, o log mostra `Required Vulkan extension VK_EXT_robustness2 not supported`: o Vortek no
   Mali-G925 não tem essa extensão, e o D3D11 não cria o dispositivo em nível nenhum.
2. Com o **DXVK 1.10.3** (oficial, sha256 `8d1a3c91…`, em `D:\dxvk110\`, posto na pasta da versão do Studio),
   o D3D11 cria o dispositivo nos níveis 11_0, 10_1 e 10_0. O Studio passa a usar **OpenGL** ("Using graphics mode
   4-OpenGL").
3. As janelas de plugin (StartPage, Assistant, Rojo…) ainda falham com `Unable to create DXGI swapchain:
   80070057`. O `teste-swap.exe` mostrou que a swapchain em **janela-filha** falha de forma **intermitente**: a
   tentativa seguinte funciona.
4. A correção já está escrita e compilada, mas **ainda não foi testada no celular**:
   - É a DLL intermediária `ferramentas/winlator/dxgi-repete.c`, com 4,6 KB e sha256 `d445f201…`.
   - Ela substitui o `dxgi.dll` e carrega o DXGI real renomeado `dxvk_dxgi.dll`.
   - Repete `CreateSwapChainForHwnd`/`CreateSwapChain` até 8 vezes quando o erro é `E_INVALIDARG`.
   - Log opcional pela variável `DXGI_PROXY_LOG`.
5. `WINEDLLOVERRIDES` definido no cmd **não** pegou: o Studio continuou carregando o DXVK do system32.

Para compilar (no Linux):
`x86_64-w64-mingw32-gcc -shared -Os -s -nostartfiles -Wl,-e,DllMain -Wl,--gc-sections -o dxgi.dll dxgi-repete.c dxgi.def -lkernel32 -luser32`

Os testadores usam `-D__USE_MINGW_ANSI_STDIO=0 -nostartfiles -Wl,-e,entrada`, ficam com cerca de 5 KB e gravam o
resultado em `D:\diag\`. Para mandar arquivos ao celular: gzip + base64 por `executar_comando`, conferindo o
sha256. DLLs grandes não cabem: baixe no próprio celular com `curl`.

## Próximos passos

1. Testar a intermediária:
   - Montar `D:\dxvkrep\` com `d3d11.dll` (1.10.3), `dxgi.dll` (a intermediária), `dxvk_dxgi.dll` (o `dxgi.dll`
     1.10.3 renomeado) e o `teste-swap.exe`.
   - Rodar pelo laço com `DXGI_PROXY_LOG=D:\diag\dxgi-repete.log`.
   - Resultado esperado: os 8 casos OK.
2. Aplicar ao Studio:
   - Copiar os três arquivos para `C:\Program Files\Roblox\Versions\version-8d7a1009c17e4ff8\`.
   - Reabrir com `taskkill /im RobloxStudioBeta.exe /f` e depois `start "" "...\RobloxStudioBeta.exe"`.
   - Conferir no log (copiar o mais novo de `%LOCALAPPDATA%\Roblox\logs` para `D:\diag\atual.log`) se sumiu o
     "Failed Rendering".
   - Uma atualização do Studio cria uma pasta de versão nova: é preciso recopiar os arquivos (ou trocar o DXVK
     do container para 1.10.3, se o Winlator oferecer).
3. Arquivo → Novo (Baseplate); depois ligar Assistant → Settings → MCP Servers. Conferir se nasce
   `C:\users\xuser\AppData\Local\Roblox\mcp.bat` (hoje ele não existe).
4. Copiar `D:\Rojo.rbxm` para `%LOCALAPPDATA%\Roblox\Plugins\`. Rodar `rojo serve` no Termux (o localhost é
   compartilhado com o Wine) e conectar no plugin.
5. Claude Code dentro do Wine (Node para Windows sob o Box64) ou outra ponte local, sem expor o Studio.
   Depois `/plugin` e `/mcp`, e o teste da ponte.
6. Otimização (tarefa 10): RAM e modo de desempenho com o dono.

## Outras pendências do dono

- **Limpeza do Gmail**: o plano de 5 pontos foi feito e está **aguardando aprovação**. Não executar sem ela.
- `~/.controle-ir/PARAR` existe, por isso os vigias de tela estão pausados. Só o dono remove.
- Botão salvo: "gelar quarto no máximo" no "ar do quarto" (Gree 16 °C, ventilação alta, turbo, visor desligado).
