# Ar do quarto — Gree GWH09KF

- **Nome no conector:** `ar do quarto` (antes "quarto"; renomeado em 17/11/2026)
- **Cômodo:** quarto
- **Aparelho:** ar-condicionado Gree, modelo GWH09KF
- **Perfil (controle):** SmartIR `climate/1184` "Gree GWH09KF" (também GC-EAF09HR), catálogo nº 105, licença MIT
- **Tipo de controle:** estado completo (cada sinal leva modo + temperatura + ventilação) + comandos extras
- **Sinais extras:** [ar-do-quarto.ir](ar-do-quarto.ir)

## Como foi identificado (17/11/2026)

1. `buscar(categoria=ar_condicionado, marca=Gree)`, 15 candidatos. O envio nº 1 ligou o aparelho
   (tecla "ligar (estado)"), mas dois perfis tinham esse sinal: nº 102 "Gree Unknown" e nº 105 "Gree GWH09KF".
2. Teste de distinção "Desligar": variante A (nº 102, envio nº 4) não desligou; variante B (nº 105, envio nº 5)
   desligou. Perfil confirmado: **nº 105**.

## Parâmetros do perfil

- Modo: frio, desumidificar, ventilar, calor, automático
- Temperatura: **16–30 °C**, passo 1
- Ventilação: baixa, média, alta, automática
- Desligar: sim (sinal próprio)

## Testado no aparelho

| Pedido | Resultado |
|---|---|
| ligar 18 °C (frio, automática) | sinal enviado |
| desligar | funcionou |
| ligar 16 °C (frio, automática) | sinal enviado; usado como base dos extras |
| **Oscilar** (extra) | **funcionou** |
| **Visor desligado** (extra) | **funcionou** |
| **Turbo** (extra, com oscilação e visor apagado) | **funcionou** |
| 18 °C + oscilar (sinal avulso, não salvo) | sinal enviado, sem confirmação |
| oscilar + visor apagado em 16 °C (sinal avulso, não salvo) | sinal enviado; o mesmo estado está no Turbo, que funcionou |
| ligar 16 °C (frio, automática), 18/11 22:17 | **funcionou** (usuário: "o ar ligou") |
| **Visor desligado** (`x_luz`) com o ar já em 16 °C/frio/automática, 18/11 23:49 (relógio do celular) | **funcionou** (usuário: "deu certo"); estado registrado no celular: ligado, visor desligado |

## Confirmação automática (18/11/2026)

- **Pelo som (`ouvir_bipe` / `controlar` com `ouvir=true`, 1.0.16):** a gravação sincronizada funciona (o envio
  cai em ~1,0 s do áudio), mas em 3 tentativas o microfone **não captou bipe** depois do envio (energia estável
  ~−50 dBFS; só um zumbido de 438 Hz, provavelmente do próprio ar). Sem referência salva. Falta saber se este
  Gree apita ao receber o mesmo estado e a que distância o celular estava.
- **Pela imagem (`foto`, 1.0.17):** funciona; a 2–3 m o ar aparece inteiro (alto da parede, acima do espelho do
  armário) com a **luz do visor acesa no lado direito do painel**, mas os dígitos não dão para ler em 960 px.
  O recorte (`recorte=[x0,y0,x1,y1]`, `alvo="ar do quarto"`) está no GitHub e **só vai para o celular quando o
  usuário pedir**. A foto pega o espelho do armário: o reflexo de quem está no quarto aparece.

## Comandos extras (criados a partir da captura real)

| Rótulo no aparelho | Chave | Quadro Gree (8 bytes) | O que faz |
|---|---|---|---|
| Oscilar (16 °C, frio, ventilação automática) | `oscilacao_alternar` | `49 00 20 50 01 20 00 50` | liga a oscilação vertical e fixa 16 °C, frio, automática |
| Visor desligado (16 °C, frio, ventilação automática) | `x_luz` | `09 00 00 50 00 20 00 50` | apaga o visor e fixa 16 °C, frio, automática |
| Turbo (16 °C, frio, automática, oscilando, visor apagado) | `modo_turbo` | `49 00 10 50 01 20 00 50` | liga o turbo com oscilação e visor apagado; fixa 16 °C, frio, automática |

Gerados com `ferramentas/gree_variante.py`: sinal real de "frio/automática/16 °C" (`09 00 20 50 00 20 00 50`)
com só os bits trocados (oscilar = byte 0 `0x40` + byte 4 `0x01`; visor = byte 2 `0x20` apagado;
turbo = byte 2 `0x10`).
Os tempos são os do controle original (cabeçalho ~9600/4850 µs, pausa ~21500 µs). Duas tentativas anteriores
com tempos genéricos do ESPHome (9000/4000 µs, 19000 µs) **não funcionaram**.

## Ressalvas (importante para quem opera)

- Os extras **fixam 16 °C, frio, ventilação automática**. Mandar "oscilar" com o aparelho em 23 °C o leva a 16 °C.
- Cada extra manda o estado inteiro: `oscilacao_alternar` acende o visor; `x_luz` desliga a oscilação;
  `modo_turbo` liga turbo + oscilação + visor apagado. Para outra combinação, gere com a ferramenta
  (`--oscilar`, `--visor-desligado`, `--turbo`, juntos ou separados).
- Qualquer `controlar` normal (mudar temperatura, modo ou ventilação) usa os sinais do perfil, que têm
  **visor aceso e oscilação desligada**. Depois disso, mande o extra de novo se o usuário quiser.
- A chave `oscilacao_alternar` está registrada como "alternar", mas o quadro **liga** a oscilação (não alterna).
- Para oscilar ou apagar o visor em outra combinação, gere com a ferramenta (só combinações de quadro
  único; as de quadro duplo são recusadas até serem testadas).

## Frases

- "Ligue o ar do quarto em 16 graus." → `controlar(aparelho="ar do quarto", ligar=true, definir={temperatura:16})`
- "Coloca a pá do ar do quarto para oscilar." → `controlar(aparelho="ar do quarto", teclas=["oscilacao_alternar"])`
- "Apaga o visor do ar do quarto." → `controlar(aparelho="ar do quarto", teclas=["x_luz"])`
- "Liga o turbo do ar do quarto." → `controlar(aparelho="ar do quarto", teclas=["modo_turbo"])`
- "Desligue o ar do quarto." → `controlar(aparelho="ar do quarto", ligar=false)`
