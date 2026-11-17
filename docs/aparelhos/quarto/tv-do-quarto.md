# TV do quarto — Samsung

- **Nome no conector:** `tv do quarto`
- **Cômodo:** quarto
- **Aparelho:** TV Samsung (modelo ainda não informado)
- **Protocolo:** Samsung32, endereço **0x07** (o padrão das TVs Samsung)
- **Perfil (controle):** Flipper-IRDB "Samsung TV Full" (catálogo nº 2331, catálogo ampliado), 54 teclas
- **Tipo de controle:** teclas (sem estado; liga/desliga do perfil é alternância)
- **Sinais extras:** [tv-do-quarto.ir](tv-do-quarto.ir)

## Testado na TV (17/11/2026)

| Tecla / código Samsung32 | Chave no aparelho | Resultado |
|---|---|---|
| Ligar direto `0x99` | `energia_ligar` (extra "Ligar (direto)") | **funcionou** (no 2º envio, mandado 2 vezes) |
| Smart Hub `0x79` | `inicio_3` | **funcionou**: abre a barra de apps |
| Smart Hub + OK `0x79`, `0x68` | macro `abrir Netflix` | **funcionou**: a Netflix é o 1º app da barra |
| Home `0x46` | `inicio` | não reagiu |
| Netflix `0xF3` (tecla do perfil e do BN59-01330C) | `netflix` | não reagiu — esta TV não tem atalho direto |
| Desligar direto `0x98` | `energia_desligar` (extra "Desligar (direto)") | **ainda não testado** |

As outras teclas (volume, mudo, canal, HDMI 1–4, setas, voltar, sleep...) vêm do perfil e ainda não foram
testadas nesta TV. Trate o primeiro uso de cada uma como teste e pergunte ao usuário.

## Teclas do perfil úteis (código Samsung32, endereço 0x07)

`inicio` 0x46 · `inicio_2` 0x76 · `inicio_3` 0x79 (Smart Hub, funciona) · `cima` 0x60 · `baixo` 0x61 ·
`direita` 0x62 · `esquerda` 0x65 · `ok` 0x68 · `voltar` 0x58 · `reproduzir` 0x47 · `pausar` 0x4A ·
`entrada_alternar` 0x01 · `dormir` 0x03 · `netflix` 0xF3 · `prime_video` 0xF4.
Volume, mudo, canal e HDMI são sinais brutos do perfil.

## Macros

- **`abrir Netflix`**: `teclas: ["inicio_3", "ok"]` (Smart Hub, 0,45 s, OK). Funcionou.

## Pendências

- **YouTube:** não há código IR de YouTube para Samsung no catálogo. Caminho combinado: Smart Hub + setas + OK.
  Falta o usuário dizer a posição do YouTube na barra para criar a macro `abrir YouTube`
  (ex.: `teclas: ["inicio_3", "direita", "direita", "ok"]`).
- Confirmar o desligar direto (0x98). Se não funcionar, usar `energia_alternar` (Power) sabendo o estado.
- Não varrer códigos Samsung desconhecidos: o perfil marca 0x20, 0x3B e 0x3E como "Not available", e a
  faixa tem comandos ocultos de serviço.

## Frases

- "Liga a TV do quarto." → `controlar(aparelho="tv do quarto", ligar=true)` (usa o ligar direto 0x99)
- "Abre a Netflix na TV." → `controlar(aparelho="tv do quarto", macro="abrir Netflix")`
- "Abre o Smart Hub." → `controlar(aparelho="tv do quarto", teclas=["inicio_3"])`
