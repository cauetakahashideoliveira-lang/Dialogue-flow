# Graph Report - Dialogue-flow  (2026-11-17)

## Corpus Check
- 26 files · ~30,925 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 1, .gz 1)

## Summary
- 441 nodes · 1212 edges · 21 communities (13 shown, 8 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 111 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `323e93de`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- vocabulario.py
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
- protocolos.py
- instalar.sh
- ErroEmissor
- LEIA-ME.md
- empacotar.sh
- ServidorMCP
- Notificador
- TestServidorMCP
- TestProtocolos
- TestVocabulario

## God Nodes (most connected - your core abstractions)
1. `Servico` - 47 edges
2. `Sinal` - 39 edges
3. `Descoberta` - 37 edges
4. `Catalogo` - 34 edges
5. `Controlador` - 27 edges
6. `criar_servidor()` - 24 edges
7. `normalizar()` - 24 edges
8. `iniciar()` - 22 edges
9. `EmissorSimulado` - 22 edges
10. `agora()` - 18 edges

## Surprising Connections (you probably didn't know these)
- `TestControle` --uses--> `Aparelhos`  [INFERRED]
  testes/test_controle_ir.py → controle-ir/controle_ir/aparelhos.py
- `preparar()` --uses--> `Servico`  [INFERRED]
  ferramentas/verificar_cliente_mcp.py → controle-ir/controle_ir/servico.py
- `novo_servico()` --uses--> `Servico`  [INFERRED]
  testes/test_controle_ir.py → controle-ir/controle_ir/servico.py
- `TestDescoberta` --uses--> `EmissorSimulado`  [INFERRED]
  testes/test_controle_ir.py → controle-ir/controle_ir/emissor.py
- `preparar()` --uses--> `EmissorSimulado`  [INFERRED]
  ferramentas/verificar_cliente_mcp.py → controle-ir/controle_ir/emissor.py

## Import Cycles
- None detected.

## Communities (21 total, 8 thin omitted)

### Community 0 - "vocabulario.py"
Cohesion: 0.13
Nodes (13): Aparelhos, progresso_txt(), f(), chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar() (+5 more)

### Community 1 - "servico.py"
Cohesion: 0.07
Nodes (9): capacidades(), ErroAparelho, hora_legivel(), resumo_aparelho(), main(), preparar(), catalogo_base(), novo_servico() (+1 more)

### Community 2 - "cli.py"
Cohesion: 0.12
Nodes (17): ampliar_catalogo(), _api(), carregar_config(), catalogo_atual(), _cfg_caminho(), estado_servidor(), iniciar(), ao_mudar_url() (+9 more)

### Community 3 - "Servico"
Cohesion: 0.14
Nodes (14): ErroUso, Servico, criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST() (+6 more)

### Community 4 - "Catalogo"
Cohesion: 0.10
Nodes (12): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), normalizar_marca() (+4 more)

### Community 5 - "Descoberta"
Cohesion: 0.13
Nodes (4): agora(), Descoberta, ErroDescoberta, termo_por_chave()

### Community 6 - "Controlador"
Cohesion: 0.16
Nodes (8): Controlador, Etapa, executar(), Plano, EmissorSimulado, normalizar_valor(), valores_equivalentes(), TestControle

### Community 7 - "Sinal"
Cohesion: 0.07
Nodes (29): adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos() (+21 more)

### Community 8 - "Estado atual da instalação (17/11/2026)"
Cohesion: 0.25
Nodes (7): Anúncio dos testes (v1.0.1), Aparelhos salvos, Celular, Conector no Claude, Estado atual da instalação (17/11/2026), Frases, Pendências possíveis

### Community 9 - "Controle IR do POCO + Claude"
Cohesion: 0.17
Nodes (11): Como funciona, Conectar ao Claude, Controle IR do POCO + Claude, Descoberta, Desenvolvimento, Instalação (uma etapa por vez), O que foi verificado e o que depende do seu POCO, Por que Termux e não um APK (+3 more)

### Community 11 - "protocolos.py"
Cohesion: 0.16
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 12 - "instalar.sh"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 13 - "ErroEmissor"
Cohesion: 0.20
Nodes (3): Emissor, EmissorTermux, ErroEmissor

## Knowledge Gaps
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `vocabulario.py`, `servico.py`, `cli.py`, `Catalogo`, `Descoberta`, `Controlador`, `Sinal`, `ErroEmissor`, `ServidorMCP`?**
  _High betweenness centrality (0.148) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Should `vocabulario.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._
- **Why does `Sinal` connect `Sinal` to `vocabulario.py`, `servico.py`, `Servico`, `Catalogo`, `Descoberta`, `Controlador`, `ErroEmissor`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `Sinal` (e.g. with `Catalogo` and `Descoberta`) actually correct?**
  _`Sinal` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `servico.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07199032062915911 - nodes in this community are weakly interconnected._
- **Why does `Catalogo` connect `Catalogo` to `servico.py`, `cli.py`, `Servico`, `Descoberta`, `Sinal`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._