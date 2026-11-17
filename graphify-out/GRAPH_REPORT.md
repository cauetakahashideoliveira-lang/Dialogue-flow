# Graph Report - Dialogue-flow  (2026-11-17)

## Corpus Check
- 26 files · ~31,040 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 1, .gz 1)

## Summary
- 443 nodes · 1196 edges · 23 communities (12 shown, 11 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 126 edges (avg confidence: 0.87)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `bd3187bd`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Aparelhos
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
- ErroEmissor
- LEIA-ME.md
- empacotar.sh
- ServidorMCP
- Notificador
- TestServidorMCP
- TestProtocolos
- TestVocabulario
- sinais.py
- Tunel

## God Nodes (most connected - your core abstractions)
1. `Servico` - 46 edges
2. `Sinal` - 39 edges
3. `Descoberta` - 37 edges
4. `Catalogo` - 34 edges
5. `Controlador` - 26 edges
6. `normalizar()` - 24 edges
7. `criar_servidor()` - 24 edges
8. `iniciar()` - 22 edges
9. `EmissorSimulado` - 20 edges
10. `agora()` - 18 edges

## Surprising Connections (you probably didn't know these)
- `TestControle` --uses--> `Sinal`  [INFERRED]
  testes/test_controle_ir.py → controle-ir/controle_ir/sinais.py
- `TestFormatos` --uses--> `Sinal`  [INFERRED]
  testes/test_controle_ir.py → controle-ir/controle_ir/sinais.py
- `novo_servico()` --calls--> `EmissorSimulado`  [INFERRED]
  testes/test_controle_ir.py → controle-ir/controle_ir/emissor.py
- `novo_servico()` --calls--> `Servico`  [INFERRED]
  testes/test_controle_ir.py → controle-ir/controle_ir/servico.py
- `preparar()` --uses--> `Servico`  [INFERRED]
  ferramentas/verificar_cliente_mcp.py → controle-ir/controle_ir/servico.py

## Import Cycles
- None detected.

## Communities (23 total, 11 thin omitted)

### Community 0 - "Aparelhos"
Cohesion: 0.24
Nodes (3): Aparelhos, progresso_txt(), f()

### Community 1 - "servico.py"
Cohesion: 0.07
Nodes (11): capacidades(), ErroAparelho, hora_legivel(), resumo_aparelho(), EmissorTermux, ErroEmissor, main(), preparar() (+3 more)

### Community 2 - "cli.py"
Cohesion: 0.08
Nodes (26): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), _unzip() (+18 more)

### Community 3 - "Servico"
Cohesion: 0.12
Nodes (14): ErroUso, Servico, criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST() (+6 more)

### Community 5 - "Descoberta"
Cohesion: 0.13
Nodes (4): agora(), Descoberta, ErroDescoberta, termo_por_chave()

### Community 6 - "Controlador"
Cohesion: 0.14
Nodes (8): Controlador, Etapa, executar(), Plano, EmissorSimulado, normalizar_valor(), valores_equivalentes(), TestControle

### Community 7 - "Sinal"
Cohesion: 0.09
Nodes (30): normalizar_marca(), adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto() (+22 more)

### Community 8 - "Estado atual da instalação (17/11/2026)"
Cohesion: 0.25
Nodes (7): Anúncio dos testes (v1.0.1), Aparelhos salvos, Celular, Conector no Claude, Estado atual da instalação (17/11/2026), Frases, Pendências possíveis

### Community 9 - "Controle IR do POCO + Claude"
Cohesion: 0.17
Nodes (11): Como funciona, Conectar ao Claude, Controle IR do POCO + Claude, Descoberta, Desenvolvimento, Instalação (uma etapa por vez), O que foi verificado e o que depende do seu POCO, Por que Termux e não um APK (+3 more)

### Community 11 - "protocolos.py"
Cohesion: 0.11
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 12 - "instalar.sh"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "sinais.py"
Cohesion: 0.12
Nodes (11): broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta(), limitar_duracao(), normalizar_pulsos(), pronto_para_pulsos(), pulsos_para_broadlink() (+3 more)

## Knowledge Gaps
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `Aparelhos`, `servico.py`, `cli.py`, `Descoberta`, `Controlador`, `Sinal`, `ServidorMCP`, `sinais.py`?**
  _High betweenness centrality (0.151) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Should `servico.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06874669487043893 - nodes in this community are weakly interconnected._
- **Why does `Sinal` connect `Sinal` to `servico.py`, `cli.py`, `Servico`, `Descoberta`, `Controlador`, `protocolos.py`, `ErroEmissor`, `sinais.py`?**
  _High betweenness centrality (0.122) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `Sinal` (e.g. with `Catalogo` and `Descoberta`) actually correct?**
  _`Sinal` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `cli.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07731694828469023 - nodes in this community are weakly interconnected._
- **Why does `Catalogo` connect `cli.py` to `servico.py`, `Servico`, `Descoberta`, `Sinal`, `sinais.py`?**
  _High betweenness centrality (0.090) - this node is a cross-community bridge._