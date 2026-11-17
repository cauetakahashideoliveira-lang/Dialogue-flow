# Graph Report - Dialogue-flow  (2026-11-17)

## Corpus Check
- 26 files · ~31,159 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 1, .gz 1)

## Summary
- 444 nodes · 1197 edges · 20 communities (13 shown, 7 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 126 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `c1144e99`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Catalogo
- servico.py
- cli.py
- Servico
- Descoberta
- Controlador
- Sinal
- Estado atual da instalação (17/11/2026)
- Controle IR do POCO + Claude
- CLAUDE.md
- protocolos.py
- instalar.sh
- EmissorSimulado
- LEIA-ME.md
- empacotar.sh
- criar_servidor
- Notificador
- TestProtocolos
- TestVocabulario

## God Nodes (most connected - your core abstractions)
1. `Servico` - 46 edges
2. `Sinal` - 39 edges
3. `Descoberta` - 37 edges
4. `Catalogo` - 34 edges
5. `Controlador` - 26 edges
6. `criar_servidor()` - 24 edges
7. `normalizar()` - 24 edges
8. `iniciar()` - 22 edges
9. `EmissorSimulado` - 20 edges
10. `agora()` - 18 edges

## Surprising Connections (you probably didn't know these)
- `preparar()` --uses--> `Servico`  [INFERRED]
  ferramentas/verificar_cliente_mcp.py → controle-ir/controle_ir/servico.py
- `novo_servico()` --calls--> `Servico`  [INFERRED]
  testes/test_controle_ir.py → controle-ir/controle_ir/servico.py
- `preparar()` --uses--> `EmissorSimulado`  [INFERRED]
  ferramentas/verificar_cliente_mcp.py → controle-ir/controle_ir/emissor.py
- `novo_servico()` --calls--> `EmissorSimulado`  [INFERRED]
  testes/test_controle_ir.py → controle-ir/controle_ir/emissor.py
- `TestControle` --uses--> `Sinal`  [INFERRED]
  testes/test_controle_ir.py → controle-ir/controle_ir/sinais.py

## Import Cycles
- None detected.

## Communities (20 total, 7 thin omitted)

### Community 0 - "Catalogo"
Cohesion: 0.09
Nodes (14): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), normalizar_marca() (+6 more)

### Community 1 - "servico.py"
Cohesion: 0.08
Nodes (9): capacidades(), ErroAparelho, hora_legivel(), resumo_aparelho(), main(), preparar(), catalogo_base(), novo_servico() (+1 more)

### Community 2 - "cli.py"
Cohesion: 0.12
Nodes (17): ampliar_catalogo(), _api(), carregar_config(), catalogo_atual(), _cfg_caminho(), estado_servidor(), iniciar(), ao_mudar_url() (+9 more)

### Community 3 - "Servico"
Cohesion: 0.10
Nodes (14): Aparelhos, ErroUso, Servico, chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar() (+6 more)

### Community 5 - "Descoberta"
Cohesion: 0.13
Nodes (3): agora(), Descoberta, ErroDescoberta

### Community 6 - "Controlador"
Cohesion: 0.16
Nodes (7): Controlador, Etapa, executar(), Plano, normalizar_valor(), valores_equivalentes(), TestControle

### Community 7 - "Sinal"
Cohesion: 0.08
Nodes (29): adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos() (+21 more)

### Community 8 - "Estado atual da instalação (17/11/2026)"
Cohesion: 0.22
Nodes (8): Anúncio dos testes (v1.0.1), Aparelhos salvos, Celular, Conector no Claude, Estado atual da instalação (17/11/2026), Frases, Pendências possíveis, Problemas já resolvidos (para não repetir)

### Community 9 - "Controle IR do POCO + Claude"
Cohesion: 0.17
Nodes (11): Como funciona, Conectar ao Claude, Controle IR do POCO + Claude, Descoberta, Desenvolvimento, Instalação (uma etapa por vez), O que foi verificado e o que depende do seu POCO, Por que Termux e não um APK (+3 more)

### Community 11 - "protocolos.py"
Cohesion: 0.13
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 12 - "instalar.sh"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 13 - "EmissorSimulado"
Cohesion: 0.15
Nodes (5): Emissor, EmissorSimulado, EmissorTermux, ErroEmissor, TestDescoberta

### Community 16 - "criar_servidor"
Cohesion: 0.14
Nodes (13): ServidorMCP, criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json() (+5 more)

## Knowledge Gaps
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `Catalogo`, `servico.py`, `cli.py`, `Descoberta`, `Controlador`, `Sinal`, `EmissorSimulado`, `criar_servidor`?**
  _High betweenness centrality (0.150) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Should `Catalogo` be split into smaller, more focused modules?**
  _Cohesion score 0.09291521486643438 - nodes in this community are weakly interconnected._
- **Why does `Sinal` connect `Sinal` to `Catalogo`, `servico.py`, `Servico`, `Descoberta`, `Controlador`, `protocolos.py`, `EmissorSimulado`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `Sinal` (e.g. with `Catalogo` and `Descoberta`) actually correct?**
  _`Sinal` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `servico.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07532467532467532 - nodes in this community are weakly interconnected._
- **Why does `Catalogo` connect `Catalogo` to `servico.py`, `cli.py`, `Servico`, `Descoberta`, `Sinal`?**
  _High betweenness centrality (0.089) - this node is a cross-community bridge._