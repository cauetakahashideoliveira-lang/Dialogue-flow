# Segurança do controle-ir: administração externa, armação e auditoria

Este documento reúne decisões e propostas datadas. Para configurar a Central, o cliente ChatGPT ou Claude e um aparelho em outra conta, siga o [guia de contribuição](../CONTRIBUTING.md). A [passagem de bastão](HANDOFF.md) identifica os fluxos incluídos nas versões publicadas.

Princípio: **capacidade ≠ permissão**. O celular implementa tudo o que é possível fazer; o que pode ser usado em
cada momento é concedido de fora do agente, por prazo, e pode ser reduzido ou revogado a qualquer hora.

**Ameaça principal** (definida pelo dono em 19/11): acesso externo — URL do conector vazada, conta Google ou
claude.ai invadida, conta/token do ngrok, instruções injetadas em conteúdo lido pelo agente (tela, páginas,
nomes de dispositivos, e-mails).

## 1. Diagnóstico (código da 1.0.22, auditoria de 19/11)

| Porta de entrada | Credencial | Se vazar (antes da 1.0.23) |
|---|---|---|
| `POST /mcp/<segredo>` pelo ngrok (todas as ferramentas) | segredo estático de 256 bits, comparação em tempo constante, sem prazo nem escopo | controle total: shell, capacidades, tela, câmera, microfone, atualização por commit arbitrário, destravar |
| `/painel?t=` e `/api/*` (só 127.0.0.1) | `token_local` | qualquer app do aparelho ou comando local aprova tarefas pendentes |
| Botões das notificações | acesso ao aparelho / app com acesso a notificações / Shizuku | aprovar, liberar 30 min, copiar a URL |
| Conta claude.ai (login Google) | sessão da conta | usar o conector salvo em qualquer conversa; gravar widgets da Central da Casa |
| Conta/authtoken do ngrok | login ou `~/.config/ngrok/ngrok.yml` | sequestrar o domínio fixo e ficar no meio (ler o segredo, injetar respostas) |
| Inspetor do ngrok em 127.0.0.1:4040 | nenhuma (local) | ver caminho com o segredo e respostas (fotos, telas) |
| Conteúdo lido pelo agente | nenhuma | induzir o agente a chamar `autorizar` (bastava a chamada no modo "chat") |

Achados críticos confirmados relendo o código: aprovação "chat" + perfil autônomo (a URL era a única barreira e
`autorizar` confiava no próprio agente); capacidades embutidas ignoravam política e trava; a classe "leitura"
expunha a semente TOTP, o segredo e o authtoken (`cat`); `atualizar_sistema` sem verificação e com ref que
aceitava `..`; `travar` desfeito por `autorizar(destravar)` e trocas de perfil; política, aprovações, auditoria e
código graváveis pelo mesmo usuário que roda os comandos remotos. Histórico do git e `dist/` sem segredos.

## 2. Etapa 0 — armação diária local (1.0.23, implementada)

- **Desarmado por padrão.** Pelo conector só passam infravermelho, consulta e `travar` (`seguranca.py`, aplicado em
  `ServidorMCP.chamar`, por onde passam TODAS as ferramentas, inclusive `cap_*`; e de novo em
  `Politica.decidir` e `Servico.executar_capacidade`). Terminal, tela, câmera, microfone, capacidades,
  propostas de código e atualização exigem o sistema **armado**.
- **Armar só no celular:** widget “Armar Controle IR” (até a meia-noite) ou `controle-ir armar [horas]`.
  Chegar ao widget exige o celular desbloqueado — a digital. Não existe ferramenta remota que arme, destrave ou
  libere. “Desarmar Controle IR” e “Travar” desligam na hora; a notificação fixa tem o botão Travar.
- **O agente não aprova a si mesmo:** o modo “chat” deixou de existir; `autorizar` só com o código do autenticador
  (de preferência noutro aparelho). Perfis não destravam.
- **Travar é definitivo pelo lado remoto:** nega tudo menos consultar/politica/travar, encerra tarefas e cria
  `~/.controle-ir/PARAR`, que encerra os laços do sono e do termômetro. Sobrevive a reinício (arquivo).
- **Classe `protegido`:** comandos que citam a config, a política, as aprovações, a auditoria, o ngrok, `~/.ssh`,
  `/proc/*/environ` ou `~/.termux/boot` são negados em qualquer perfil (barreira contra o caminho óbvio, não
  isolamento — ver limites).
- `atualizar_sistema` aceita só o hash completo (40 hex); ngrok com `--inspect=false`; token do cloudflared pelo
  ambiente (fora do `ps`); filtro de origens usa o IP acrescentado pelo proxy (o último); notificação sem
  “Copiar URL”.

**Garantia:** desarmado, uma URL vazada só alcança infravermelho e consulta. **Limite:** com o sistema armado, quem
tiver a URL tem o alcance da política (no perfil autônomo, shell livre) e, por ser o mesmo usuário do Linux, pode
mexer nos arquivos do próprio fiscal até a armação vencer. É a Etapa 1 que tira o valor da URL.

## 3. Etapa 1 — painel externo com passkey

### 3a. Central de Controle (1.0.24, implementada) — `painel/`

Cloudflare Worker + D1 (`painel/src/index.js`, interface em `painel/public/`). O celular deixa de se armar
sozinho: quem arma é o painel, com a digital.

- **Entrar:** passkey com verificação do usuário (`userVerification: required`). A 1ª passkey exige o segredo
  `CODIGO_INICIAL` (definido na Cloudflare); depois dela o código não cadastra mais nada. Outro aparelho (iPad)
  entra só por **convite de uso único** (10 min) criado com a digital num aparelho já cadastrado.
- **Sessão:** cookie `HttpOnly; Secure; SameSite=Strict`, 12 h no máximo e 30 min parado; para **aumentar poder**
  (armar, convidar, cadastrar celular, revogar, mudar o que passa desarmado) a digital tem de ser de ≤ 2 min.
  Diminuir poder (desarmar, EMERGÊNCIA) não pede digital. Anti-CSRF: só POST com cabeçalho `x-painel` e mesma
  origem; limite de tentativas por IP.
- **Celular:** cadastrado com código de uso único (`controle-ir painel parear <URL> <CÓDIGO>`), recebe um token
  próprio e a **chave pública Ed25519** do painel. A cada 30 s busca o estado **assinado** (aparelho, sequência,
  armado até, travado, o que passa desarmado) e só o aceita se a assinatura e a sequência conferirem (nada de
  estado velho reaproveitado). Sem estado válido, ou com o token revogado: **desarmado** (falha fechada).
  Pareado, `controle-ir armar` no celular é recusado; `desarmar`/`travar` locais continuam valendo (veto local).
- **Aplicado × pendente:** o celular confirma (`ack`) a sequência que aplicou; o painel mostra “pendente” até lá.
- **Auditoria:** eventos do painel e do celular (até 100 por busca, textos truncados) num histórico encadeado por
  hash no D1; o botão “Conferir integridade” aponta o primeiro evento adulterado.
- **Latência medida:** armar/desarmar/emergência chegam ao celular na próxima busca (≤ 30 s + rede); com o
  celular sem internet, vale o último estado assinado até o seu prazo (no máximo 24 h).
- **Custo no celular:** uma requisição HTTPS pequena a cada 30 s (≈ 2 900/dia) e uma verificação Ed25519.
- **Histórico do celular no painel (1.0.25):** só o que acontece depois do pareamento (o anterior fica no
  celular), no máximo 30 eventos por envio, gravados numa transação encadeada; cada evento leva a posição no
  arquivo e o painel ignora reenvios. Sem rede ou com tempo esgotado, o celular só tenta de novo em 30 s.
- **iPad/Safari:** as opções da passkey são buscadas antes do toque (o Safari só abre o Face ID logo depois do
  toque); um convite só é gasto quando a passkey nova é aceita.
- **Evidência:** `node painel/testes/e2e.cjs` (Chromium com autenticador virtual + código real do celular, 30
  verificações) e `testes/test_controle_ir.py::TestPainel`.
- **Raiz de confiança:** a conta da Cloudflare (quem a controla altera o Worker). Use 2FA nela. Recuperação se
  perder todas as passkeys: no D1 (Cloudflare → D1 → painel → Console) `UPDATE credenciais SET revogada = 1;` e
  cadastre de novo com o `CODIGO_INICIAL` (troque-o antes).
- **Limite que continua:** a URL do conector (ngrok) ainda é o segredo de acesso ao celular; durante a janela
  armada, quem a tiver usa a política vigente. Isso é o que a 1b resolve.

### 3b. Gateway OAuth na borda (1.0.26, implementada)

```
claude.ai ──OAuth 2.1 + PKCE──▶ Painel (Worker) ──chamada assinada (Ed25519 + nonce)──▶ ngrok ──▶ celular
                  consentimento com a digital ┘  └ bloqueio na borda (desarmado / EMERGÊNCIA) e revogação do token
```

- **Login do conector:** endereço `https://<painel>/mcp`. O claude.ai descobre o OAuth (RFC 9728), registra-se
  (DCR) e abre `/authorize`, que mostra o app e o destino e só autoriza com a **digital na hora**. Biblioteca
  oficial `@cloudflare/workers-oauth-provider` (tokens só como hash no KV, PKCE S256). Destinos aceitos: claude.ai,
  claude.com e um app no próprio computador (aviso na tela); um cliente que peça outro destino nem se registra.
  Token de acesso de 1 h; o acesso (grant) dura até 30 dias e é revogado no painel na hora (“Revogar acesso”).
- **Bloqueio na borda:** antes de repassar, o painel aplica o mesmo critério do celular (`seguranca.py`):
  desarmado, só infravermelho e consulta; EMERGÊNCIA, só consultar/politica/travar. O que é barrado nem chega ao
  celular (evento `bloqueado_na_borda`).
- **Repasse assinado:** cada chamada vai ao celular com `X-Painel-Assinatura` = horário + nonce + Ed25519 sobre o
  hash do corpo (mesma chave do estado). O celular confere com a chave fixada, recusa horário fora de ±90 s,
  corpo alterado e nonce repetido. O celular informa ao painel o endereço do MCP dele a cada sincronização.
- **“Aceitar o Claude só pelo painel”** (estado assinado, `so_pelo_painel`): ligado, o celular recusa chamadas
  sem a assinatura do painel; a URL do ngrok vazada deixa de servir. Ligar reduz poder (sem digital); desligar
  pede a digital. Vale mesmo sem rede (último valor assinado).
- **Evidência:** E2E 42/42 (OAuth completo com autenticador virtual, PKCE, cliente com destino de terceiros
  recusado, repasse conferido pelo código real do celular, bloqueio na borda, revogação do token, “só pelo
  painel”) e `TestPainel` (assinatura, horário, corpo trocado, chave errada, repetição; servidor recusando o
  direto quando “só pelo painel”).
- **Limites:** o tráfego das ferramentas passa pelo Worker (conta Cloudflare = raiz de confiança, com 2FA). O
  conector antigo (URL do ngrok) continua aceito até você ligar “só pelo painel”. Sem escopos por missão, por
  decisão do dono (autonomia geral quando armado).

### 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29)

Autonomia geral continua (nada pede aprovação); a Central só mostra o que acontece:
- **Atividade do Claude:** a Central registra cada chamada que repassa (ferramenta, resumo — o comando, a
  capacidade e a ação, o aparelho —, o “por quê” que o Claude informou, recursos tocados, resultado, tempo) e as
  barradas na borda. Fica no D1 por 30 dias; o Claude não escreve nele.
- **Agora no celular:** o celular relata a cada sincronização as tarefas do terminal em execução (com câmera,
  microfone, localização… inferidos do comando), capacidades rodando em 2º plano (lidas de /proc) e, com o painel
  aberto, **câmera e microfone em uso por qualquer app** (AppOps “Running”, o mesmo dado do ponto verde do
  Android, pelo Shizuku). Também mostra o que foi usado nas chamadas dos últimos 2 min.
- **Tela ao vivo:** com o painel aberto e o botão ligado, o celular manda um quadro JPEG (~540 px) a cada ~2 s
  (começa em até 30 s); o pedido vence em 2 min sem renovação, para ao esconder a página, e o último quadro é
  apagado ao parar. Só o último quadro fica guardado.
- **Custo:** fora do painel aberto, nada muda (sem Shizuku, sem quadros). Com o painel aberto, uma consulta
  AppOps a cada 30 s; assistindo, captura + ffmpeg a cada 2 s.

### 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central)

Antes, cada chamada ia Central → túnel ngrok → celular. Agora o **celular disca** para a Central
(`wss://<central>/api/celular/canal`, com o **token do aparelho**) e mantém um WebSocket aberto; um Durable Object
por aparelho (`Canal`, SQLite, plano grátis) segura a conexão. A Central repassa as chamadas do Claude por ele e
**empurra avisos** ("sync") — armar, desarmar, emergência, revogar e abrir o painel chegam ao celular **na hora**
(antes: até 30 s).

Propriedades de segurança (nada afrouxa):
- **Mesma autenticação de ponta a ponta:** cada chamada que desce pelo canal continua **assinada pela Central**
  (X-Painel-Assinatura, Ed25519 + nonce + ±90 s) e é entregue ao servidor **local** (127.0.0.1), que confere a
  assinatura como sempre. Quem roubasse o canal não forjaria chamadas; quem roubasse o token do aparelho só
  receberia chamadas (já filtradas na borda) e não as ver executadas no celular verdadeiro.
- **Aviso não é ordem:** o "sync" só acorda a sincronização; o celular busca e **confere a assinatura** do estado
  como sempre. Um aviso falso não arma nada.
- **Nada novo exposto no celular:** a conexão é de saída (sem porta aberta, funciona em dados móveis e roteado).
- **Falha segura:** o celular confirma cada chamada na hora; sem confirmação em 5 s (ou sem batida há 70 s) o
  canal é descartado e a chamada vai pelo túnel. Reenvios não executam duas vezes: o servidor do celular devolve a
  resposta da primeira se a mesma chamada (corpo idêntico) chegar enquanto ela roda ou até 3 s depois (1.0.46).
- **Custo:** batidas a cada 25 s respondidas automaticamente pelo objeto sem acordá-lo (hibernação) — zero de
  processamento parado; bateria do celular ~ a de um app de mensagens.

#### Planejado (próximas etapas)

```
claude.ai / Claude Code ──OAuth 2.1+PKCE──▶ Painel (Cloudflare Worker + D1) ──túnel──▶ celular (controle-ir)
        iPad / POCO ──passkey (digital/Face ID)──▶ Painel: armar, missões, revogar, auditoria
```

- **Identidade do dono:** passkeys (WebAuthn, biblioteca SimpleWebAuthn, `userVerification: required`), uma no
  POCO (Google Password Manager) e outra no iPad (iCloud Keychain). Invadir o Gmail não entrega a passkey.
  E-mail só para alertas. Aparelho novo só entra com aprovação biométrica num aparelho já cadastrado.
- **Gateway na borda:** o conector do claude.ai passa a apontar para o Worker, que faz OAuth 2.1 (CIMD/DCR,
  aceitos pelo claude.ai) com tokens curtos de audiência fixa; a URL secreta do ngrok deixa de existir. O celular
  só aceita chamadas que venham do Worker (cabeçalho assinado). **Revogar e o botão de emergência agem na borda**
  — fora do celular, então valem mesmo que o celular tenha sido adulterado.
- **Missões e perfis → escopos aplicáveis:** cada autorização (JWS Ed25519 assinado pelo Worker, verificado no
  celular com a chave pública fixa) diz cliente, aparelho, ferramentas, operações (ler / alterar / excluir /
  executar / transmitir), destinos de dados, prazo e limites. Exemplos: *infravermelho* (controlar, opcoes…);
  *internet* (diagnostico_rede, descobrir_rede, comandos da classe rede); *pasta* (leitura numa pasta);
  *código* (shell num diretório de trabalho); *tela* (cap tela, com lista de apps); *ampla* (tudo, curta, passkey
  no iPad). O Claude propõe a tradução de uma missão (“corrigir minha internet”) e o painel mostra a lista antes
  de você aprovar. Ampliação: o Claude pede com justificativa; aprovação só no painel.
- **Auditoria:** o celular envia ao Worker cada evento (pedido, decisão, início, fim, bloqueio, processos
  filhos, mudanças de permissão), sem conteúdo integral, encadeado por hash no D1; o agente não escreve no D1.
  Indicador de câmera, microfone e tela ativos.
- **Revogação mensurável:** na borda, imediata; no celular, na próxima chamada (≤ 60 s para laços em 2º plano).
  Sem conexão, a autorização local vence no prazo (no máximo 24 h). O painel só mostra “revogado” depois que o
  celular confirmar.

## 4. Etapa 2 — endurecer a execução (depois da Etapa 1)

Executor separado do fiscal (proot com binds só-leitura do código e de `~/.controle-ir`, ou outro usuário/app),
atualizações aceitas só com o hash aprovado no painel, hash do código em execução comparado com o pacote
aprovado, segredos fora do alcance do shell, Central da Casa sem `executar_comando` em widgets automáticos.

## 5. Decisões do dono

**Decidido em 19/11:** autonomia geral. Armado (com a digital, na Central de Controle) = o Claude tem tudo, sem
escopos por missão; a digital diária é a autorização. Nome geral: Central de Controle. Painel em repositório
único (este), com o merge do dono como aprovação de mudanças. Conector antigo removido do claude.ai.

1. **Hospedar o painel na Cloudflare** (grátis; precisa de uma conta sua). Recomendado.
2. **Quem pode alterar o painel:** repositório separado, só seu (recomendado: o agente não tem acesso), ou este.
3. **Armação:** até a meia-noite (atual) ou por N horas; desarmar após X horas sem uso?
4. **Desarmado libera o infravermelho?** (atual: sim; a alternativa é “nada”).
5. **Recuperação:** duas passkeys (POCO + iPad) + códigos de recuperação impressos, guardados fora do celular.
6. **Sessão ampla:** permitir, com passkey no iPad e prazo máximo (sugestão: 2 h)?

## 6. Limites que nenhuma etapa remove

- Dados entregues ao Claude ou a outro provedor seguem a retenção desse provedor; o painel registra o que saiu.
- Shizuku (usuário shell) toca em qualquer app e lê notificações quando armado; aprovações sensíveis ficam no iPad.
- Durante uma sessão ampla, quem a controla tem o celular; por isso ela é curta, aprovada com passkey e auditada.
- Precisa de teste no aparelho: formato do `X-Forwarded-For` que o ngrok entrega; os widgets Armar/Desarmar; a
  parada dos laços com `PARAR`.
