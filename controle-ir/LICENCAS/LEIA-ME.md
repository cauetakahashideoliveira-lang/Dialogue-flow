# Licenças dos dados de controle

| Fonte | Onde entra | Licença | Observação |
|---|---|---|---|
| [SmartIR](https://github.com/smartHomeHub/SmartIR) (`codes/`) | catálogo base (`dados/base.jsonl.gz`) | MIT — texto em `SmartIR-MIT.txt` | Copyright (c) 2019 Vassilis Panos. Perfis de ar-condicionado (estado completo), ventiladores, TVs/som e luzes. Códigos de RF e do formato comprimido Xiaomi foram descartados. |
| [Flipper-IRDB](https://github.com/Lucaslhm/Flipper-IRDB) — arquivos adicionados após o commit `2319685` | catálogo base | CC0-1.0 — texto em `Flipper-IRDB-CC0.txt` | O README do projeto declara que contribuições anteriores a esse commit não estão cobertas pela CC0; por isso só os arquivos posteriores vão no pacote. |
| Flipper-IRDB completa | baixada no celular por `controle-ir catalogo ampliar` | CC0 parcial | Não é redistribuída neste pacote. O próprio usuário faz o download, para uso pessoal. |
| [irdb (probonopd)](https://github.com/probonopd/irdb) | não usada | licença própria com condições (aviso prévio, cópias do produto) | Excluída para evitar obrigações de licença. |

Os commits exatos usados para gerar o catálogo base estão em `dados/origem.json`.
As temporizações de protocolo seguem as especificações públicas (NEC, Samsung, Philips RC5/RC6,
Sony SIRC, Kaseikyo, RCA, Pioneer); a convenção dos campos endereço/comando é a dos arquivos `.ir`
do Flipper Zero, para compatibilidade com a Flipper-IRDB. Nenhum código do firmware do Flipper foi copiado.
