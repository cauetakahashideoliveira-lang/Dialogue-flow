# Ar-condicionado do laboratório — Midea

- **Nome no conector:** `ar condicionado laboratório`
- **Cômodo:** laboratório
- **Aparelho:** ar-condicionado **Midea**
- **Perfil (controle):** SmartIR "Carrier Unknown" (catálogo nº 94); o Midea aceita os códigos Carrier
- **Tipo de controle:** misto (estado completo + tecla de oscilação)
- **Sinais extras:** [ar-condicionado-laboratorio.ir](ar-condicionado-laboratorio.ir)

## Como foi identificado

Comandos do perfil Carrier nº 94 enviados no laboratório: ventilação média, 17 °C e 20 °C reagiram.
Oscilação: busca de oscilação em todas as marcas; a tecla "alternar oscilação" do perfil **Ferroli/York**
funcionou na tentativa nº 1 e foi adicionada ao aparelho.

## Parâmetros

- Modo: frio, calor, desumidificar, automático, ventilar
- Temperatura: 17–30 °C
- Ventilação: automática, baixa, média, alta
- Desligar: sim
- **Oscilação:** `oscilacao_alternar` (alternância: o servidor precisa saber o estado atual; último
  confirmado pelo usuário: **ligada**)

## Último estado confirmado pelo usuário

Ligado, frio, 20 °C, ventilação média, oscilação ligada.

## Ressalvas

- Usa **os mesmos códigos do ar do escritório** (perfil nº 94): se os dois estiverem ao alcance, os dois reagem.
- A oscilação é uma alternância (o mesmo sinal liga e desliga). Se o usuário usar o controle original,
  registre com `registrar_estado(controle_original_usado=true)`.

## Frases

- "Liga o ar do laboratório em 20 graus, ventilação média."
  → `controlar(aparelho="ar condicionado laboratório", ligar=true, definir={temperatura:20, ventilacao:"media"})`
- "Liga a oscilação do ar do laboratório." → `controlar(aparelho="ar condicionado laboratório", definir={oscilacao:true})`
