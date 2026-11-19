# Graph Report - Dialogue-flow  (2026-11-19)

## Corpus Check
- 57 files · ~75,503 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 3, .ir 3, .gz 1)

## Summary
- 983 nodes · 2386 edges · 50 communities (27 shown, 23 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 228 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `beff1748`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- f
- sinais.py
- servico.py
- Descoberta
- cli.py
- Controlador
- Serviço (operações MCP)
- emissor.py
- ServidorMCP
- tela/principal.py
- verificar_cliente_mcp.py
- subprocess
- resumo_para_instrucoes
- TestTelaPorArquivo
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- os
- TestServidorMCP
- Execucao
- Registro
- Instalador (instalar.sh)
- test_controle_ir.py
- Licenças dos dados
- Tunel
- TestSegundoPlano
- godmode-tracker.js
- json
- Sinal
- descobrir_rede/principal.py
- time
- termometro/principal.py
- TestTela
- TestOuvirBipe
- TestImagemNoMcp
- TestSonar
- TestCapacidades
- TestTermometro
- novo_servico
- test_god_mode.py
- TestProtocolos
- Catalogo
- session-start.sh
- subprocess
- gree_variante.py

## God Nodes (most connected - your core abstractions)
1. `Servico` - 51 edges
2. `Sinal` - 35 edges
3. `Descoberta` - 33 edges
4. `Catalogo` - 33 edges
5. `main()` - 30 edges
6. `criar_servidor()` - 27 edges
7. `normalizar()` - 26 edges
8. `Controlador` - 25 edges
9. `ErroUso` - 24 edges
10. `_iniciar()` - 24 edges

## Surprising Connections (you probably didn't know these)
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `variante()` --implements--> `Variante Gree a partir da captura real (troca só os bits)`  [INFERRED]
  ferramentas/gree_variante.py → docs/aparelhos/quarto/ar-do-quarto.md
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
- `Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper)` --conceptually_related_to--> `ler_flipper()`  [INFERRED]
  docs/aparelhos/README.md → controle-ir/controle_ir/formatos.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `ampliar_catalogo()`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/cli.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (50 total, 23 thin omitted)

### Community 0 - "f"
Cohesion: 0.23
Nodes (7): filtro(), ler_recortes(), main(), reduzir(), validar_recorte(), progresso_txt(), f()

### Community 1 - "sinais.py"
Cohesion: 0.06
Nodes (27): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+19 more)

### Community 2 - "servico.py"
Cohesion: 0.20
Nodes (7): capacidades(), _curto(), _faixa_txt(), hora_legivel(), _linhas_aparelho(), resumo_aparelho(), executar()

### Community 3 - "Descoberta"
Cohesion: 0.13
Nodes (3): agora(), Descoberta, ErroDescoberta

### Community 4 - "cli.py"
Cohesion: 0.06
Nodes (40): _api(), arquivo_boot(), atualizar(), _aviso(), boot_ativado(), caminho_log(), _carimbo_catalogo(), carregar_config() (+32 more)

### Community 5 - "Controlador"
Cohesion: 0.16
Nodes (6): Controlador, Etapa, Plano, normalizar_valor(), valores_equivalentes(), TestControle

### Community 6 - "Serviço (operações MCP)"
Cohesion: 0.05
Nodes (39): EmissorSimulado, ErroUso, Servico, criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS() (+31 more)

### Community 7 - "emissor.py"
Cohesion: 0.18
Nodes (3): Emissor, EmissorTermux, ErroEmissor

### Community 9 - "tela/principal.py"
Cohesion: 0.12
Nodes (23): achar(), agir(), _apagar(), app_em_foco(), bloqueado(), bloqueados(), _bloqueio_de_toque(), captura() (+15 more)

### Community 11 - "subprocess"
Cohesion: 0.19
Nodes (7): js(), rodar(), analisar_sonar(), gerar_tom(), main(), testar(), volume_musica()

### Community 14 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.06
Nodes (33): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+25 more)

### Community 15 - "os"
Cohesion: 0.16
Nodes (11): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+3 more)

### Community 18 - "Execucao"
Cohesion: 0.07
Nodes (6): exec_cli(), Autorizacao, Execucao, Politica, totp(), TestExecucao

### Community 19 - "Registro"
Cohesion: 0.19
Nodes (5): ErroCapacidade, _hash(), _manifesto(), Registro, capacidade_cli()

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 24 - "TestSegundoPlano"
Cohesion: 0.15
Nodes (4): catalogo_base(), TestCatalogo, TestSegundoPlano, abrir_console()

### Community 25 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

### Community 26 - "json"
Cohesion: 0.27
Nodes (11): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+3 more)

### Community 29 - "Sinal"
Cohesion: 0.07
Nodes (36): Aparelhos, ErroAparelho, normalizar_marca(), adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar() (+28 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.17
Nodes (9): classificar(), ficha_upnp(), ip_do_wifi(), main(), sondar(), ssdp(), tcp(), udp() (+1 more)

### Community 32 - "time"
Cohesion: 0.38
Nodes (8): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi()

### Community 34 - "termometro/principal.py"
Cohesion: 0.33
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 39 - "TestSonar"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 43 - "test_god_mode.py"
Cohesion: 0.06
Nodes (7): _Base, _ComServidor, _Servidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos, TestGodModeStmEPontuacao

### Community 45 - "Catalogo"
Cohesion: 0.12
Nodes (12): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), _unzip() (+4 more)

### Community 47 - "subprocess"
Cohesion: 0.23
Nodes (4): arquivos_cc0(), main(), flipper(), main()

### Community 48 - "gree_variante.py"
Cohesion: 0.08
Nodes (27): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, Anúncio dos testes (v1.0.1), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade) (+19 more)

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 278 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Serviço (operações MCP)` to `mcp.py`, `servico.py`, `Descoberta`, `cli.py`, `Controlador`, `ServidorMCP`, `verificar_cliente_mcp.py`, `novo_servico`, `Execucao`, `Registro`, `test_controle_ir.py`, `Sinal`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `Servico` (e.g. with `ServidorMCP` and `criar_servidor()`) actually correct?**
  _`Servico` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `sinais.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05807622504537205 - nodes in this community are weakly interconnected._
- **Why does `Catalogo` connect `Catalogo` to `sinais.py`, `servico.py`, `Descoberta`, `cli.py`, `descoberta.py`, `Sinal`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `Sinal` (e.g. with `Catalogo` and `Emissor`) actually correct?**
  _`Sinal` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Should `Descoberta` be split into smaller, more focused modules?**
  _Cohesion score 0.1346153846153846 - nodes in this community are weakly interconnected._