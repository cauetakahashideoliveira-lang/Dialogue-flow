# PC na Central de Controle (agente do PC)

O PC Windows entra na Central como um **segundo aparelho**, com o mesmo modelo de segurança do celular, e o
Claude o opera pelo **mesmo conector** (Controle Geral), com as ferramentas `pc_*`.

```
Claude ── conector Controle Geral (OAuth com a digital) ──► Central (Worker)
                                                            ├─ ferramentas do celular ──► canal ──► celular (Termux)
                                                            └─ ferramentas pc_*        ──► canal ──► PC (agente_pc)
```

- **Canal:** o PC abre um WebSocket com a Central, com o token dele (`controle_ir.canal`, o mesmo código do
  celular). Não precisa de porta aberta, túnel ou IP fixo.
- **Assinatura:** cada chamada é assinada pela Central (Ed25519) e conferida no PC
  (`controle_ir.painel.verificar_requisicao`). O servidor local só escuta em 127.0.0.1 e recusa o que não vier
  assinado.
- **Armado próprio:** o PC tem estado próprio na Central. Desarmado, só `pc_consultar` e `pc_travar` respondem, e
  as outras ferramentas são barradas na borda e de novo no PC. "Armar" na Central arma todos os aparelhos.
- **Auditoria:** cada comando e cada arquivo escrito vai para `auditoria.jsonl` do PC e sobe para a Central, que
  também mostra as chamadas `pc_*` em "Atividade do Claude".

## Ferramentas

| Ferramenta | O que faz |
|---|---|
| `pc_consultar` | Sistema, CPU, memória, discos, placa de vídeo (`nvidia-smi`), programas instalados (git, python, node, rojo, ollama, Roblox Studio…), tarefas e segurança. Sempre responde. |
| `pc_executar` | Comando no PowerShell (padrão), cmd, pwsh ou bash, como administrador. Espera até 55 s; o que demora mais segue rodando como tarefa. |
| `pc_tarefa` | Acompanhar (`aguardar`, `desde`), parar (árvore inteira) ou listar tarefas. |
| `pc_ler_arquivo` / `pc_escrever_arquivo` / `pc_editar_arquivo` / `pc_listar` | Arquivos: leitura por linhas, imagens como imagem, binário em base64, troca exata de trecho (mantém `\r\n` e BOM). |
| `pc_tela` | Captura da tela (todos os monitores ou um), em JPEG. |
| `pc_entrada` | Mouse e teclado: clicar, duplo, direito, arrastar, rolar, digitar e teclas no formato SendKeys. As coordenadas são as da última `pc_tela`. |
| `pc_atualizar` | `git pull` (ou `ref`, que deixa o repositório destacado nesse commit) e reinício do agente. Sem `ref`, volta para a branch padrão se estiver destacado. |
| `pc_travar` | Encerra as tarefas e bloqueia o PC até o dono armar de novo na Central. Sempre responde. |

## Instalar no PC

Pré-requisitos: Git, este repositório clonado (ex.: `C:\dev\dialogue-flow`) e a Central já com a versão que
conhece o PC (este PR publicado).

1. Na Central, entre com a digital e toque em **Cadastrar celular**. O código vale 10 min e serve uma vez só.
2. No **PowerShell como administrador**:
   ```
   powershell -ExecutionPolicy Bypass -File C:\dev\dialogue-flow\pc\instalar.ps1 -Url https://SUA-CENTRAL.workers.dev -Codigo ABCD1234
   ```
   O instalador:
   - instala o Python 3.12 pelo winget, se faltar;
   - cria `%LOCALAPPDATA%\agente-pc\venv` com a biblioteca `cryptography`;
   - pareia o PC com a Central;
   - registra a tarefa agendada **Agente PC - Central**, que liga no logon, oculta e como administrador;
   - confere se o agente respondeu.
3. Na Central, **arme** com a digital. O PC aparece na lista de aparelhos.
4. No Claude, abra uma **conversa nova**: a lista de ferramentas do conector é fixa por conversa. Teste com
   `pc_consultar`.

Para atualizar depois: `pc_atualizar` pelo Claude, ou rode o instalador de novo sem `-Url` e `-Codigo`.

## Religar o PC e o botão "Ligar Agente PC"

- **Depois que o PC desligar:** ligue e entre no Windows. A tarefa agendada liga o agente sozinha, oculta, de 10 a
  30 s depois do logon. Não precisa abrir terminal. Depois, arme na Central com a digital, se o prazo tiver vencido.
- **Botão na área de trabalho, "Ligar Agente PC"** (`pc/ligar.ps1`, criado pelo instalador):
  - liga o agente se ele tiver caído, sem pedir administrador, porque dispara a tarefa agendada, que já roda
    como administrador;
  - espera o agente responder e mostra numa janela se o PC está conectado à Central;
  - se o agente já estiver ligado, só confere.

  O `/saude` local informa o estado do canal (`{"canal": {"conectado": …}}`) desde a pc-1.0.2.
- **Para voltar sozinho depois de uma queda de energia** (opcional, decisão do dono, feito uma vez no PC):
  - BIOS: "Restore on AC Power Loss" em **Power On**, para o PC ligar quando a energia voltar;
  - logon automático do Windows (por exemplo, o Autologon da Sysinternals). A senha fica só no PC, nunca no
    chat. Sem isso, alguém precisa entrar no Windows depois de religar.

## Manter ligado

- **Energia:** `powercfg /change standby-timeout-ac 0` e `powercfg /change hibernate-timeout-ac 0` impedem o PC
  de dormir na tomada.
- **Logon:** o agente liga no logon do usuário, porque precisa da área de trabalho para a tela e o mouse.
  Depois de reiniciar, ele só volta quando alguém entrar no Windows. Para voltar sozinho, configure o logon
  automático, que é uma decisão do dono, por segurança.
- **Comandos locais:**
  - `python -m agente_pc estado`: serviço, Central e armado.
  - `python -m agente_pc desligar`: encerra o serviço até o próximo logon.
  Rode com o Python de `%LOCALAPPDATA%\agente-pc\venv` e `PYTHONPATH=pc;controle-ir`.
- **Registro:** `%LOCALAPPDATA%\agente-pc\agente.log`.

## Limites

- A janela do UAC (área de trabalho segura) não aparece em `pc_tela` nem aceita `pc_entrada`. O agente já roda
  como administrador, então os comandos não pedem UAC.
- Sem o celular no ar, o conector continua de pé só com o PC (`initialize` e `tools/list` respondidos pela
  Central).
- **Conversa aberta antes do PC existir** (sem `pc_*` na lista): use `executar_capacidade` com
  `nome="pc_executar"` (ou outra `pc_*`) e `argumentos={…}`. A Central encaminha ao PC com as mesmas regras.
- Se o PC estiver desligado quando a conversa começa, as ferramentas `pc_*` aparecem mesmo assim, pela última
  lista guardada na Central, e a chamada responde "o PC está fora do ar".

## Testes

- `python3 -m unittest testes.test_agente_pc`: assinatura, repetição, guardião (desarmado, armado,
  travado, emergência), tarefas, tempo limite, arquivos e auditoria.
- Em `painel/`, `npm run test:e2e`, seção 4b'': PC real pareado e conectado pelo canal:
  - lista unida com as ferramentas do celular;
  - barrado desarmado e executando armado;
  - "fora do ar" com a lista guardada;
  - revogação.
- Tela, mouse, teclado e o instalador `.ps1` só rodam no Windows: são conferidos na primeira instalação.
