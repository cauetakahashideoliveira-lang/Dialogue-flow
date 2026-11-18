# Ar do escritório — Carrier

- **Nome no conector:** `ar do escritório` (antes "escritório"; renomeado em 17/11/2026)
- **Cômodo:** escritório
- **Aparelho:** ar-condicionado Carrier
- **Perfil (controle):** SmartIR "Carrier Unknown" (catálogo nº 94), licença MIT
- **Tipo de controle:** estado completo (modo + temperatura + ventilação em cada sinal)
- **Sinais extras:** nenhum (só o perfil)

## Como foi identificado

Busca Carrier, tentativa nº 1 (o reteste nº 5 apitou).

## Parâmetros do perfil

- Modo: frio, calor, desumidificar, automático, ventilar
- Temperatura: **17–30 °C** (16 °C não existe neste perfil)
- Ventilação: automática, baixa, média, alta
- Desligar: sim
- **Sem oscilação** e sem visor no perfil

## Testado no aparelho

- Ligar 18 °C, desligar, ligar 18 °C, mudar para 22 °C (preservou frio + automática): funcionou.
- 17/11: ligar 23 °C (frio, automática): sinal enviado.

## Ressalvas

- Usa **os mesmos códigos do ar do laboratório** (perfil nº 94). Se os dois estiverem ao alcance do
  celular, os dois reagem.
- Oscilação: o perfil não tem. No laboratório (Midea), a tecla de oscilação do perfil Ferroli/York funcionou;
  se o usuário quiser no escritório, teste esse sinal ([laboratório](../laboratorio/ar-condicionado-laboratorio.ir))
  e pergunte antes de salvar.

## Frases

- "Ligue o ar do escritório em 23 °C, modo frio, ventilação baixa."
  → `controlar(aparelho="ar do escritório", ligar=true, definir={temperatura:23, modo:"frio", ventilacao:"baixa"})`
- "Agora mude só para 22 °C." → `controlar(aparelho="ar do escritório", definir={temperatura:22})`
- "Desligue o ar do escritório." → `controlar(aparelho="ar do escritório", ligar=false)`
