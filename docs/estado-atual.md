# Estado atual da instalação (17/11/2026)

## Celular
- POCO X8 Pro Max, Android/HyperOS, Termux + Termux:API (F-Droid).
- Emissor IR confirmado: 30, 33, 36, 38, 40 e 56 kHz.
- Termux precisou de `apt update && apt full-upgrade` (curl quebrado por openssl antigo).
- Catálogo instalado: base (632 perfis). Ampliado (Flipper-IRDB completa) ainda não.

## Conector no Claude
- Nome: "Controle do POCO" (sem login, URL com segredo).
- Túnel rápido trycloudflare: a URL muda ao reiniciar → `controle-ir`, `copiar`, remover e readicionar o conector.

## Aparelhos salvos
| Nome | Tipo | Perfil | Como foi achado |
|---|---|---|---|
| escritório | ar-condicionado | Carrier (catálogo nº 94, SmartIR) | busca Carrier, tentativa nº 1 (reteste nº 5 apitou) |

- escritório aceita: modo frio/calor/desumidificar/automático/ventilar; 17–30 °C; ventilação automática/baixa/média/alta; desligar. Sem oscilação.
- Testado pelo usuário: ligar 18 °C, desligar, ligar 18 °C, mudar para 22 °C (preservou frio + automática).

## Frases
1. "Ligue o ar do escritório em 23 °C, modo frio, ventilação baixa."
2. "Agora mude só para 22 °C."
3. "Desligue o ar do escritório."

## Pendências possíveis
- URL fixa: ngrok configurado pelo usuário (v1.0.2 usa termux-chroot automaticamente). Início automático (Termux:Boot) pendente.
- Resumo dos aparelhos nas instruções do MCP para economizar chamadas no chat.

## Anúncio dos testes (v1.0.1)
- Cada envio da busca é falado em voz alta (termux-tts-speak) e mostrado no Termux como "▶ N".
- O número falado = número do histórico: "foi o 5" → pausar, retestar([5]), confirmar(5).
- Desligar a voz: `controle-ir voz nao`.
