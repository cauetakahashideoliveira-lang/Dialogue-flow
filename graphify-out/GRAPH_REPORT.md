# Graph Report - Dialogue-flow  (2026-11-17)

## Corpus Check
- 26 files · ~30,696 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 1, .gz 1)

## Summary
- 439 nodes · 1211 edges · 14 communities (11 shown, 3 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 115 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9b68ff3a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Sinal
- servico.py
- cli.py
- Servico
- Catalogo
- Descoberta
- Controlador
- Sinal
- Estado atual da instalação (17/11/2026)
- Controle IR do POCO + Claude
- CLAUDE.md
- instalar.sh
- LEIA-ME.md
- empacotar.sh

## God Nodes (most connected - your core abstractions)
1. `Servico` - 48 edges
2. `Sinal` - 39 edges
3. `Descoberta` - 37 edges
4. `Catalogo` - 34 edges
5. `Controlador` - 27 edges
6. `criar_servidor()` - 25 edges
7. `normalizar()` - 24 edges
8. `EmissorSimulado` - 22 edges
9. `iniciar()` - 22 edges
10. `agora()` - 18 edges

## Surprising Connections (you probably didn't know these)
- `TestControle` --uses--> `Sinal`  [INFERRED]
  testes/test_controle_ir.py → controle-ir/controle_ir/sinais.py
- `TestControle` --uses--> `Aparelhos`  [INFERRED]
  testes/test_controle_ir.py → controle-ir/controle_ir/aparelhos.py
- `preparar()` --uses--> `EmissorSimulado`  [INFERRED]
  ferramentas/verificar_cliente_mcp.py → controle-ir/controle_ir/emissor.py
- `novo_servico()` --uses--> `EmissorSimulado`  [INFERRED]
  testes/test_controle_ir.py → controle-ir/controle_ir/emissor.py
- `TestDescoberta` --uses--> `EmissorSimulado`  [INFERRED]
  testes/test_controle_ir.py → controle-ir/controle_ir/emissor.py

## Import Cycles
- None detected.

## Communities (14 total, 3 thin omitted)

### Community 0 - "Sinal"
Cohesion: 0.07
Nodes (35): normalizar_marca(), Etapa, Plano, adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar() (+27 more)

### Community 1 - "servico.py"
Cohesion: 0.05
Nodes (11): capacidades(), hora_legivel(), resumo_aparelho(), main(), preparar(), catalogo_base(), novo_servico(), TestCatalogo (+3 more)

### Community 2 - "cli.py"
Cohesion: 0.09
Nodes (20): ampliar_catalogo(), _api(), carregar_config(), catalogo_atual(), _cfg_caminho(), estado_servidor(), iniciar(), ao_mudar_url() (+12 more)

### Community 3 - "Servico"
Cohesion: 0.08
Nodes (17): Aparelhos, ErroAparelho, ServidorMCP, ErroUso, Servico, criar_servidor(), _corpo(), do_DELETE() (+9 more)

### Community 4 - "Catalogo"
Cohesion: 0.11
Nodes (10): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), _unzip() (+2 more)

### Community 5 - "Descoberta"
Cohesion: 0.13
Nodes (3): agora(), Descoberta, ErroDescoberta

### Community 6 - "Controlador"
Cohesion: 0.14
Nodes (7): Controlador, executar(), Emissor, EmissorSimulado, EmissorTermux, ErroEmissor, TestControle

### Community 7 - "Sinal"
Cohesion: 0.07
Nodes (27): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+19 more)

### Community 8 - "Estado atual da instalação (17/11/2026)"
Cohesion: 0.29
Nodes (6): Aparelhos salvos, Celular, Conector no Claude, Estado atual da instalação (17/11/2026), Frases, Pendências possíveis

### Community 9 - "Controle IR do POCO + Claude"
Cohesion: 0.17
Nodes (11): Como funciona, Conectar ao Claude, Controle IR do POCO + Claude, Descoberta, Desenvolvimento, Instalação (uma etapa por vez), O que foi verificado e o que depende do seu POCO, Por que Termux e não um APK (+3 more)

### Community 12 - "instalar.sh"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

## Knowledge Gaps
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `Sinal`, `servico.py`, `cli.py`, `Catalogo`, `Descoberta`, `Controlador`, `Sinal`?**
  _High betweenness centrality (0.156) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `Servico` (e.g. with `ServidorMCP` and `Aparelhos`) actually correct?**
  _`Servico` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Should `Sinal` be split into smaller, more focused modules?**
  _Cohesion score 0.0700152207001522 - nodes in this community are weakly interconnected._
- **Why does `Sinal` connect `Sinal` to `Sinal`, `servico.py`, `cli.py`, `Servico`, `Catalogo`, `Descoberta`, `Controlador`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `Sinal` (e.g. with `Catalogo` and `Descoberta`) actually correct?**
  _`Sinal` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `servico.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0504828797190518 - nodes in this community are weakly interconnected._
- **Why does `Catalogo` connect `Catalogo` to `Sinal`, `servico.py`, `cli.py`, `Servico`, `Descoberta`, `Sinal`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._