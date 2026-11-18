# Graph Report - Dialogue-flow  (2026-11-18)

## Corpus Check
- 41 files · ~52,120 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 3, .ir 3, .gz 1)

## Summary
- 747 nodes · 1874 edges · 34 communities (23 shown, 11 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 225 edges (avg confidence: 0.87)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `77c2fbed`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Catalogo
- Sinal
- servico.py
- Descoberta automática
- cli.py
- Planejador de pedidos
- Serviço (operações MCP)
- formatos.py
- ServidorMCP
- Instalação no celular
- Gerador de variantes Gree
- Variante Gree a partir da captura real (troca só os bits)
- Emissor infravermelho
- .controlar
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- Contexto para agentes (CLAUDE.md)
- tv do quarto (TV Samsung)
- Execucao
- Registro
- Instalador (instalar.sh)
- Testes de protocolos
- Licenças dos dados
- normalizar
- TestSegundoPlano
- godmode-tracker.js
- vocabulario.py
- Sinal
- .editar_aparelho
- TestVocabulario

## God Nodes (most connected - your core abstractions)
1. `Servico` - 50 edges
2. `Sinal` - 35 edges
3. `Catalogo` - 33 edges
4. `Descoberta` - 33 edges
5. `main()` - 29 edges
6. `criar_servidor()` - 27 edges
7. `normalizar()` - 26 edges
8. `Controlador` - 25 edges
9. `ErroUso` - 24 edges
10. `_iniciar()` - 23 edges

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

## Communities (34 total, 11 thin omitted)

### Community 0 - "Catalogo"
Cohesion: 0.14
Nodes (11): Catalogo, estado_representativo(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), _unzip(), _zip() (+3 more)

### Community 1 - "Sinal"
Cohesion: 0.06
Nodes (27): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+19 more)

### Community 2 - "servico.py"
Cohesion: 0.06
Nodes (23): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi() (+15 more)

### Community 3 - "Descoberta automática"
Cohesion: 0.13
Nodes (4): agora(), Descoberta, ErroDescoberta, termo_por_chave()

### Community 4 - "cli.py"
Cohesion: 0.06
Nodes (41): ampliar_catalogo(), _api(), arquivo_boot(), atualizar(), _aviso(), boot_ativado(), caminho_log(), _carimbo_catalogo() (+33 more)

### Community 5 - "Planejador de pedidos"
Cohesion: 0.14
Nodes (7): Controlador, Etapa, Plano, EmissorSimulado, normalizar_valor(), valores_equivalentes(), TestControle

### Community 6 - "Serviço (operações MCP)"
Cohesion: 0.11
Nodes (16): ErroUso, Servico, criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST() (+8 more)

### Community 7 - "formatos.py"
Cohesion: 0.20
Nodes (16): adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos() (+8 more)

### Community 8 - "ServidorMCP"
Cohesion: 0.06
Nodes (8): resumo_para_instrucoes(), ServidorMCP, catalogo_base(), novo_servico(), TestCapacidades, TestCatalogo, TestResumoInstrucoes, TestServidorMCP

### Community 9 - "Instalação no celular"
Cohesion: 0.17
Nodes (15): Anúncio dos testes (v1.0.1), Catálogo instalado: base + ampliado (9.380 perfis), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026) (+7 more)

### Community 10 - "Gerador de variantes Gree"
Cohesion: 0.19
Nodes (11): exportar_jsonl(), checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main() (+3 more)

### Community 11 - "Variante Gree a partir da captura real (troca só os bits)"
Cohesion: 0.27
Nodes (4): Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105), Perfil Gree Unknown (catálogo nº 102), descartado, Problemas já resolvidos (para não repetir), Versão do servidor (celular 1.0.4, repositório 1.0.5)

### Community 13 - ".controlar"
Cohesion: 0.17
Nodes (14): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50) (+6 more)

### Community 14 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.06
Nodes (32): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+24 more)

### Community 15 - "Contexto para agentes (CLAUDE.md)"
Cohesion: 0.27
Nodes (4): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, empacotar.sh script

### Community 17 - "tv do quarto (TV Samsung)"
Cohesion: 0.52
Nodes (6): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung)

### Community 18 - "Execucao"
Cohesion: 0.07
Nodes (8): exec_cli(), Autorizacao, classificar(), Execucao, gerar_segredo(), Politica, totp(), TestExecucao

### Community 19 - "Registro"
Cohesion: 0.18
Nodes (5): ErroCapacidade, _hash(), _manifesto(), Registro, capacidade_cli()

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 23 - "normalizar"
Cohesion: 0.25
Nodes (4): normalizar_marca(), _traduz(), categoria_canonica(), normalizar()

### Community 25 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

### Community 26 - "vocabulario.py"
Cohesion: 0.24
Nodes (8): chaves_de_teste(), interpretar(), _por_regex(), _registrar(), sem_acentos(), _t(), Termo, todas_chaves()

### Community 30 - ".editar_aparelho"
Cohesion: 0.33
Nodes (4): Aparelhos, ErroAparelho, slug(), Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper)

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 191 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Serviço (operações MCP)` to `servico.py`, `Descoberta automática`, `cli.py`, `Planejador de pedidos`, `ServidorMCP`, `.controlar`, `Execucao`, `Registro`, `Sinal`, `.editar_aparelho`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `Servico` (e.g. with `ServidorMCP` and `Execucao`) actually correct?**
  _`Servico` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Catalogo` be split into smaller, more focused modules?**
  _Cohesion score 0.1402116402116402 - nodes in this community are weakly interconnected._
- **Why does `Catalogo` connect `Catalogo` to `Sinal`, `servico.py`, `Descoberta automática`, `cli.py`, `Instalação no celular`, `normalizar`, `Sinal`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `Sinal` (e.g. with `Catalogo` and `Emissor`) actually correct?**
  _`Sinal` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Should `Sinal` be split into smaller, more focused modules?**
  _Cohesion score 0.05786090005844535 - nodes in this community are weakly interconnected._