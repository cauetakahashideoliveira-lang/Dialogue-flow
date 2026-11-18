# Graph Report - Dialogue-flow  (2026-11-18)

## Corpus Check
- 34 files · ~39,283 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 3, .ir 3, .gz 1)

## Summary
- 587 nodes · 1535 edges · 27 communities (20 shown, 7 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 194 edges (avg confidence: 0.87)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `f46b1b12`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Catalogo
- Sinal
- Módulos do pacote controle-ir
- Descoberta automática
- cli.py
- Planejador de pedidos
- Serviço (operações MCP)
- Protocolos IR
- Servidor MCP
- Instalação no celular
- Gerador de variantes Gree
- Ramo: ar do quarto (Gree)
- Emissor infravermelho
- Índice e cômodos + ar do escritório e do laboratório (Carrier nº 94)
- README do projeto
- Contexto para agentes (CLAUDE.md)
- Ramo: tv do quarto (Samsung)
- Notificador (voz)
- Túnel HTTPS
- Instalador (instalar.sh)
- Testes de protocolos
- Licenças dos dados
- ServidorMCP
- TestSegundoPlano
- godmode-tracker.js

## God Nodes (most connected - your core abstractions)
1. `Servico` - 42 edges
2. `Sinal` - 36 edges
3. `Descoberta` - 36 edges
4. `Catalogo` - 34 edges
5. `_iniciar()` - 27 edges
6. `normalizar()` - 26 edges
7. `criar_servidor()` - 25 edges
8. `Controlador` - 25 edges
9. `main()` - 23 edges
10. `EmissorSimulado` - 21 edges

## Surprising Connections (you probably didn't know these)
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `ampliar_catalogo()`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/cli.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper)` --conceptually_related_to--> `ler_flipper()`  [INFERRED]
  docs/aparelhos/README.md → controle-ir/controle_ir/formatos.py
- `variante()` --implements--> `Variante Gree a partir da captura real (troca só os bits)`  [INFERRED]
  ferramentas/gree_variante.py → docs/aparelhos/quarto/ar-do-quarto.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (27 total, 7 thin omitted)

### Community 0 - "Catalogo"
Cohesion: 0.07
Nodes (24): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), normalizar_marca() (+16 more)

### Community 1 - "Sinal"
Cohesion: 0.06
Nodes (31): adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos() (+23 more)

### Community 2 - "Módulos do pacote controle-ir"
Cohesion: 0.06
Nodes (12): capacidades(), _curto(), _faixa_txt(), hora_legivel(), _linhas_aparelho(), resumo_aparelho(), main(), preparar() (+4 more)

### Community 3 - "Descoberta automática"
Cohesion: 0.13
Nodes (3): agora(), Descoberta, ErroDescoberta

### Community 4 - "cli.py"
Cohesion: 0.09
Nodes (35): ampliar_catalogo(), _api(), arquivo_boot(), boot_ativado(), caminho_log(), carregar_config(), catalogo_atual(), _cfg_caminho() (+27 more)

### Community 5 - "Planejador de pedidos"
Cohesion: 0.16
Nodes (8): Controlador, Etapa, executar(), Plano, EmissorSimulado, normalizar_valor(), valores_equivalentes(), TestControle

### Community 6 - "Serviço (operações MCP)"
Cohesion: 0.10
Nodes (9): Aparelhos, ErroAparelho, ErroUso, Servico, slug(), Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper), Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas), Versão do servidor (celular 1.0.4, repositório 1.0.5) (+1 more)

### Community 7 - "Protocolos IR"
Cohesion: 0.16
Nodes (15): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+7 more)

### Community 8 - "Servidor MCP"
Cohesion: 0.21
Nodes (12): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), _origem_ok() (+4 more)

### Community 9 - "Instalação no celular"
Cohesion: 0.19
Nodes (15): Anúncio dos testes (v1.0.1), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026), Frases (+7 more)

### Community 10 - "Gerador de variantes Gree"
Cohesion: 0.23
Nodes (10): checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main(), perfil() (+2 more)

### Community 11 - "Ramo: ar do quarto (Gree)"
Cohesion: 0.22
Nodes (8): Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50), Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105), Perfil Gree Unknown (catálogo nº 102), descartado, Ligar/desligar diretos (energia_ligar 0x99, energia_desligar 0x98)

### Community 12 - "Emissor infravermelho"
Cohesion: 0.20
Nodes (3): Emissor, EmissorTermux, ErroEmissor

### Community 13 - "Índice e cômodos + ar do escritório e do laboratório (Carrier nº 94)"
Cohesion: 0.31
Nodes (8): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Cômodo: Escritório, Cômodo: Laboratório, Cômodo: Quarto, Índice de aparelhos (cômodo → aparelho → controle), Aparelhos salvos

### Community 14 - "README do projeto"
Cohesion: 0.15
Nodes (12): Como funciona, Conectar ao Claude, Controle IR do POCO + Claude, Descoberta, Desenvolvimento, Instalação (uma etapa por vez), Início automático quando o celular liga (Termux:Boot), O que foi verificado e o que depende do seu POCO (+4 more)

### Community 15 - "Contexto para agentes (CLAUDE.md)"
Cohesion: 0.27
Nodes (4): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, empacotar.sh script

### Community 17 - "Ramo: tv do quarto (Samsung)"
Cohesion: 0.43
Nodes (7): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung), Catálogo instalado: base + ampliado (9.380 perfis)

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 23 - "ServidorMCP"
Cohesion: 0.15
Nodes (3): resumo_para_instrucoes(), ServidorMCP, TestResumoInstrucoes

### Community 25 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 141 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Serviço (operações MCP)` to `Módulos do pacote controle-ir`, `Descoberta automática`, `cli.py`, `Servidor MCP`, `ServidorMCP`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `Servico` (e.g. with `ServidorMCP` and `Aparelhos`) actually correct?**
  _`Servico` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Catalogo` be split into smaller, more focused modules?**
  _Cohesion score 0.07380520266182698 - nodes in this community are weakly interconnected._
- **Why does `Catalogo` connect `Catalogo` to `Sinal`, `Módulos do pacote controle-ir`, `Descoberta automática`, `cli.py`, `Ramo: tv do quarto (Samsung)`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `Sinal` (e.g. with `Catalogo` and `Descoberta`) actually correct?**
  _`Sinal` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Should `Sinal` be split into smaller, more focused modules?**
  _Cohesion score 0.06010230179028133 - nodes in this community are weakly interconnected._