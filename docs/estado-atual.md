# Estado atual da instalação (17/11/2026)

## Celular
- POCO X8 Pro Max, Android/HyperOS, Termux + Termux:API (F-Droid).
- Emissor IR confirmado: 30, 33, 36, 38, 40 e 56 kHz.
- Termux precisou de `apt update && apt full-upgrade` (curl quebrado por openssl antigo).
- Catálogo instalado: base + ampliado (Flipper-IRDB completa) = 9.380 perfis, 94.407 sinais únicos, 1.776 marcas.
- Servidor na versão 1.0.4.

## Conector no Claude
- Nome atual: "Controle master" (sem login, URL com segredo). O antigo "Controle do POCO" foi removido.
- Túnel: **ngrok com domínio fixo** (`controle-ir tunel ngrok --dominio <endereço>.ngrok-free.app`), executado
  via `termux-chroot` (DNS do Android) e apontando para `http://127.0.0.1:8765` (evita Bad Gateway por IPv6).
- A URL é fixa: reiniciar o Termux não exige mexer no Claude. Muda só com `controle-ir novo-segredo` ou
  trocando o domínio no ngrok.
- O segredo foi regenerado em 17/11 depois de aparecer numa captura de tela.
- Cuidados: não usar CTRL+C na aba do servidor; não fotografar a caixa com a URL.

## Aparelhos salvos
| Nome | Tipo | Perfil | Como foi achado |
|---|---|---|---|
| escritório | ar-condicionado Carrier | Carrier (catálogo nº 94, SmartIR) | busca Carrier, tentativa nº 1 (reteste nº 5 apitou) |
| ar condicionado laboratório | ar-condicionado **Midea** | o mesmo perfil Carrier nº 94 (Midea aceita os códigos) | comandos enviados no laboratório: ventilação média, 17 °C e 20 °C reagiram; **oscilação** adicionada (tecla alternar do perfil Ferroli/York, busca de oscilação em todas as marcas, tentativa nº 1) |

- escritório aceita: modo frio/calor/desumidificar/automático/ventilar; 17–30 °C; ventilação automática/baixa/média/alta; desligar. Sem oscilação.
- Testado pelo usuário: ligar 18 °C, desligar, ligar 18 °C, mudar para 22 °C (preservou frio + automática).

## Frases
1. "Ligue o ar do escritório em 23 °C, modo frio, ventilação baixa."
2. "Agora mude só para 22 °C."
3. "Desligue o ar do escritório."

## Pendências possíveis
- Início automático com Termux:Boot (ainda não configurado).
- Resumo dos aparelhos nas instruções do MCP para economizar chamadas no chat.

## Anúncio dos testes (v1.0.1)
- Cada envio da busca é falado em voz alta (termux-tts-speak) e mostrado no Termux como "▶ N".
- O número falado = número do histórico: "foi o 5" → pausar, retestar([5]), confirmar(5).
- Desligar a voz: `controle-ir voz nao`.

## Problemas já resolvidos (para não repetir)
- `curl` com `CANNOT LINK EXECUTABLE`: `apt update && apt full-upgrade`.
- Download do ZIP em cache do GitHub: usar URL com o hash do commit (`.../raw/<hash>/dist/controle-ir.zip`).
- Domínio do ngrok: usar o endereço `*.ngrok-free.app`, não o código `rd_…`.
- Faixa real do perfil: 17–30 °C (16 °C não existe). Oscilação não disponível; opções: testar perfis Carrier/Midea/Springer com swing ou importar captura.
