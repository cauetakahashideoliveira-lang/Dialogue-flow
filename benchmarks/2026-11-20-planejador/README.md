# Autonomia do planejador no POCO

Executamos 160 missões reais de consulta no mesmo POCO, com Sonnet 5.5 em esforço alto. O teste repetiu os mesmos 40 pedidos duas vezes por versão. Cada pedido foi emitido pelo conector e conferido pelo estado final, pela ordem das ferramentas e pelos recibos de execução.

| Medida | Versão anterior | Versão com esquema |
|---|---:|---:|
| Pedidos viáveis concluídos corretamente | 46/60 | 60/60 |
| Pedidos impossíveis interrompidos corretamente | 20/20 | 20/20 |
| Operações extras | 1 | 0 |
| Total de missões corretas | 66/80 | 80/80 |
| Latência mediana de ponta a ponta | 5,55 s | 5,26 s |
| Latência P95 de ponta a ponta | 7,29 s | 6,65 s |

Na comparação por pedido e repetição, 14 resultados passaram de falha para acerto e 0 passaram de acerto para falha. Para os 46 pares viáveis que as duas versões completaram corretamente, a mediana da diferença de tempo (nova menos anterior) foi 0,02 s. As versões rodaram em blocos sucessivos no mesmo aparelho. Variações da rede e da API afetam os tempos.

A revisão atingiu o critério definido antes da bateria: 54/60 viáveis, 20/20 interrupções esperadas e zero operações extras. A amostra cobre consultas de uma a três operações entre cinco ferramentas. A avaliação não mediu operações com efeitos físicos nem o fluxo de navegação por toques.

## Revisões medidas

- Referência instalada no pacote `d4892fe87103687c818aae3122ba6ee9f7cbdc1a`. SHA-256 do módulo instalado: `94c7db85c40db24222aa891cb4e09fb21821dea4d9efb69592744dcbc485fa1c`.
- Candidata com código `842b2bb9613568f00e993ead7ef75e05ded52f81` e pacote `97cc1bda8fd87092fb7d94119cdec4be3cc6b825`. SHA-256 do módulo instalado: `a03ea432d843178da2b99ea04f33be96defe970f0aafba4703718b5616bd13cc`.

O esquema da resposta passa pela API e os índices são revalidados no aparelho. O despachante continua verificando a permissão de cada ferramenta. A versão anterior usava o mesmo motivo tanto para uma resposta que não podia ser interpretada quanto para um plano vazio; os registros anteriores não permitem atribuir uma causa individual às falhas.

## Dados e reprodução

Os arquivos [da referência](resultados-base.jsonl) e [da candidata](resultados-candidata.jsonl) contêm os recibos resumidos. O [gabarito](casos.tsv) contém os pedidos e suas sequências esperadas. Execute `python analisar.py` para recalcular as medidas. Consulte o [protocolo](protocolo.md) para repetir as chamadas no aparelho. Os testes locais do contrato podem ser executados com `python test_planejador.py` em um checkout do repositório.

## Robustez do componente

Os seis testes locais de contrato passaram. Um deles simulou a política passando de armada para travada entre a primeira e a segunda operação pelo despachante MCP real. A missão preservou o primeiro recibo, registrou o bloqueio na segunda operação e não tentou a terceira.

## Próxima bateria

Repetir no ambiente de integração a mudança de permissão e ampliar a cobertura de indisponibilidade da API e erro de ferramenta após uma consulta bem-sucedida. Usar falhas injetadas e recibos controlados para conferir a causa da interrupção e verificar que nenhuma etapa seguinte foi executada. Medir separadamente o tempo da API e o tempo de execução no aparelho antes de escolher uma otimização de latência.
