# Ar condicionado quarto 2 — Brastemp Clean (protocolo TCL112)

- **Nome no conector:** `ar condicionado quarto 2` (cadastrado em 22/11/2026)
- **Cômodo:** quarto 2
- **Aparelho:** split Brastemp Clean, unidade interna **BBV09BBBNA**, externa BBY09BBBNA (Whirlpool S.A.,
  9.000 BTU/h; a etiqueta do Inmetro marca **só refrigeração**)
- **Controle original:** "Brastemp Clean" (apagar painel, timer, turbo, dormir, modo, velocidade, ▲▼, liga,
  direcionar, memória, renovar)
- **Perfil:** nº **9524** no catálogo do celular, "Brastemp Clean BBV09BBBNA (TCL112)", gerado por
  [`ferramentas/tcl112.py`](../../../ferramentas/tcl112.py) e importado com `controle-ir importar`
- **Tipo de controle:** estado completo (modo + temperatura + ventilação + oscilação em cada envio)

## Como foi identificado (22/11)

1. A etiqueta diz Whirlpool, e o perfil SmartIR **Consul CBV12CBBNA** (o "irmão" Consul) usa o protocolo
   Whirlpool `83 06 …`. Nada reagiu: nem os estados do perfil (que têm o bit de energia 0 e só mudam a
   temperatura), nem quadros "alternar energia" gerados, nem a variante Hisense DGR11.
2. O log do Android (`logcat -s ConsumerIrHal` pelo rish) mostrou que os quadros de ~250 ms saíam inteiros,
   a 38 kHz: o problema não era o emissor.
3. Com o ar **ligado** pelo botão lateral, uma busca de códigos **desligar** (`buscar(comando_teste="desligar")`)
   desligou o aparelho. O reteste um a um apontou o **candidato 33**: TCL TAC-12CHSD (SmartIR climate/1900
   e 1901, catálogo nº 261 e 262).
4. O estado "frio 23 °C" do perfil nº 261 ligou o ar: bipe 0,13 s depois do envio e ruído +10,7 dB no microfone.
5. O gerador `tcl112.py` reproduz byte a byte 142 das 160 capturas dos dois perfis TCL. As 18 diferenças são
   o calor do XA21I (sem o `0x80` do byte 12) e dois erros de captura do SmartIR (o frio 19 °C é cópia do
   18 °C, e o frio 30 °C tem um bit corrompido).

## Formato (TCL112, 2 quadros de 14 bytes, LSB primeiro, 38 kHz)

Cada envio leva o quadro especial fixo `23 CB 26 02 00 40 00 00 00 00 00 00 00 65`, uma pausa de ~76 ms e o estado:

| Byte | Conteúdo |
|---|---|
| 0–3 | `23 CB 26 01` |
| 5 | `0x20` + `0x04` ligado (o desligar manda `0x20`) |
| 6 | modo: `01` calor, `02` desumidificar, `03` frio, `07` ventilar, `08` automático |
| 7 | 31 − temperatura (16–31 °C) |
| 8 | ventilação `0` auto, `2` baixa, `3` média, `5` alta; `+0x38` oscilação |
| 12 | `0x80`, `+0x08` com oscilação |
| 13 | soma dos bytes 0–12 |

Tempos usados (medidos na captura que funcionou): cabeçalho 3300/1650 µs, marca 590, espaço 265 (0) e 1115 (1).

## Parâmetros do perfil

- Modo: frio, calor, desumidificar, ventilar, automático
- Temperatura: 16–31 °C
- Ventilação: automática, baixa, média, alta (no desumidificar sempre baixa, como o controle faz)
- Oscilação: ligada, desligada (o "direcionar" do controle)
- Desligar: o código capturado do TCL (testado)

## Testado no aparelho

- 22/11 15:47: desligar (candidato 33 da busca) — **desligou**.
- 22/11 15:53: ligar em frio 23 °C, ventilação automática (estado do perfil nº 261) — **ligou**.
- 22/11 16:00: frio 23 °C, ventilação alta, oscilação ligada (perfil nº 9524 gerado) — sinal enviado, ruído
  +9,8 dB no microfone; aguardando confirmação visual da aleta.

## Ressalvas

- **Não use os perfis Consul/Whirlpool** neste aparelho, apesar da marca.
- A etiqueta indica só refrigeração: o modo calor deve ser ignorado pelo aparelho.
- Ainda não mapeados: **turbo**, **apagar painel**, **dormir**, **renovar** e timer. Pelo IRremoteESP8266, turbo seria
  `0x40` no byte 6 e o visor apagado `0x40` no byte 5. Para testar um bit, gere o quadro com
  `python3 ferramentas/tcl112.py quadro --modo frio --temperatura 23 --turbo` (ou `--visor-desligado`) e envie
  com `enviar_sinal`. Depois de confirmado, inclua o bit no perfil e regenere.
- Se o disjuntor cair com o ar ligado, a aleta fica aberta e o aparelho não responde. O botão na lateral da
  unidade interna liga o ar sem controle, o que serve para testar a energia.

## Regenerar o perfil no celular

```
python3 ferramentas/tcl112.py perfil --saida tcl112_quarto2.json
controle-ir importar tcl112_quarto2.json --nome "Brastemp Clean BBV09BBBNA (TCL112)" --categoria ar_condicionado
```

Em seguida, `editar_aparelho(aparelho="ar condicionado quarto 2", trocar_perfil=<perfil_id devolvido>)`. O
gerador não depende do repositório; no celular ele está em `~/.controle-ir/ferramentas/tcl112.py`.

## Frases

- "Liga o ar do quarto 2 em 23 graus." → `controlar(aparelho="ar condicionado quarto 2", ligar=true, definir={modo:"frio", temperatura:23})`
- "Coloca a ventilação no alto e a aleta para oscilar." → `controlar(aparelho="ar condicionado quarto 2", definir={ventilacao:"alta", oscilacao:"ligada"})`
- "Desliga o ar do quarto 2." → `controlar(aparelho="ar condicionado quarto 2", ligar=false)`
