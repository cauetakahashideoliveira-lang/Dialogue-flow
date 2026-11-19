# Graph Report - Dialogue-flow  (2026-11-19)

## Corpus Check
- 41 files · ~53,302 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 3, .ir 3, .gz 1)

## Summary
- 751 nodes · 1868 edges · 32 communities (17 shown, 15 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 216 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `a32092c5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Catalogo
- Sinal
- json
- Descoberta automática
- cli.py
- Controlador
- Serviço (operações MCP)
- Sinal
- ServidorMCP
- ErroUso
- servico.py
- descoberta.py
- resumo_para_instrucoes
- .controlar
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- emissor.py
- TestServidorMCP
- Execucao
- Registro
- Instalador (instalar.sh)
- test_controle_ir.py
- Licenças dos dados
- Tunel
- TestSegundoPlano
- godmode-tracker.js

## God Nodes (most connected - your core abstractions)
1. `Servico` - 49 edges
2. `Sinal` - 35 edges
3. `Catalogo` - 33 edges
4. `Descoberta` - 33 edges
5. `main()` - 30 edges
6. `criar_servidor()` - 27 edges
7. `normalizar()` - 26 edges
8. `Controlador` - 25 edges
9. `_iniciar()` - 24 edges
10. `ErroUso` - 24 edges

## Surprising Connections (you probably didn't know these)
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `ampliar_catalogo()`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/cli.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `variante()` --implements--> `Variante Gree a partir da captura real (troca só os bits)`  [INFERRED]
  ferramentas/gree_variante.py → docs/aparelhos/quarto/ar-do-quarto.md
- `Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper)` --conceptually_related_to--> `ler_flipper()`  [INFERRED]
  docs/aparelhos/README.md → controle-ir/controle_ir/formatos.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (32 total, 15 thin omitted)

### Community 0 - "Catalogo"
Cohesion: 0.10
Nodes (12): Catalogo, estado_representativo(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), normalizar_marca(), _unzip() (+4 more)

### Community 1 - "Sinal"
Cohesion: 0.05
Nodes (30): escrever_flipper(), sinal(), _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM (+22 more)

### Community 2 - "json"
Cohesion: 0.08
Nodes (24): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi() (+16 more)

### Community 3 - "Descoberta automática"
Cohesion: 0.13
Nodes (3): agora(), Descoberta, ErroDescoberta

### Community 4 - "cli.py"
Cohesion: 0.06
Nodes (42): ampliar_catalogo(), _api(), arquivo_boot(), atualizar(), _aviso(), boot_ativado(), caminho_log(), capacidade_cli() (+34 more)

### Community 5 - "Controlador"
Cohesion: 0.17
Nodes (5): Controlador, Etapa, Plano, normalizar_valor(), TestControle

### Community 6 - "Serviço (operações MCP)"
Cohesion: 0.09
Nodes (17): Emissor, EmissorSimulado, Servico, criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS() (+9 more)

### Community 7 - "Sinal"
Cohesion: 0.09
Nodes (32): Aparelhos, ErroAparelho, adicionar_comando(), comando(), ErroFormato, exportar(), _hex_le(), importar_texto() (+24 more)

### Community 8 - "ServidorMCP"
Cohesion: 0.13
Nodes (3): resumo_instrucoes(), ServidorMCP, TestCapacidades

### Community 10 - "servico.py"
Cohesion: 0.20
Nodes (7): capacidades(), _curto(), _faixa_txt(), hora_legivel(), _linhas_aparelho(), resumo_aparelho(), executar()

### Community 13 - ".controlar"
Cohesion: 0.05
Nodes (44): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF) (+36 more)

### Community 14 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.06
Nodes (32): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+24 more)

### Community 18 - "Execucao"
Cohesion: 0.10
Nodes (6): exec_cli(), Autorizacao, gerar_segredo(), Politica, totp(), TestExecucao

### Community 19 - "Registro"
Cohesion: 0.20
Nodes (4): ErroCapacidade, _hash(), _manifesto(), Registro

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 24 - "TestSegundoPlano"
Cohesion: 0.15
Nodes (4): catalogo_base(), TestCatalogo, TestSegundoPlano, abrir_console()

### Community 25 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 193 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Serviço (operações MCP)` to `Descoberta automática`, `cli.py`, `Sinal`, `ServidorMCP`, `ErroUso`, `servico.py`, `descoberta.py`, `.controlar`, `Registro`, `mcp.py`, `servidor.py`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `Servico` (e.g. with `ServidorMCP` and `Execucao`) actually correct?**
  _`Servico` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Catalogo` be split into smaller, more focused modules?**
  _Cohesion score 0.1021021021021021 - nodes in this community are weakly interconnected._
- **Why does `Catalogo` connect `Catalogo` to `Sinal`, `Descoberta automática`, `cli.py`, `servico.py`, `descoberta.py`, `.controlar`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `Sinal` (e.g. with `Catalogo` and `Emissor`) actually correct?**
  _`Sinal` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Should `Sinal` be split into smaller, more focused modules?**
  _Cohesion score 0.05217391304347826 - nodes in this community are weakly interconnected._