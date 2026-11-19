# Graph Report - Dialogue-flow  (2026-11-19)

## Corpus Check
- 57 files · ~74,295 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 3, .ir 3, .gz 1)

## Summary
- 968 nodes · 2369 edges · 52 communities (32 shown, 20 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 241 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `2aca762d`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- f
- protocolos.py
- servico.py
- Descoberta
- cli.py
- Controlador
- Serviço (operações MCP)
- Sinal
- ServidorMCP
- tela/principal.py
- sinais.py
- subprocess
- resumo_para_instrucoes
- ar do quarto (ar-condicionado Gree GWH09KF)
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
- normalizar
- descobrir_rede/principal.py
- time
- .editar_aparelho
- termometro/principal.py
- novo_servico
- TestOuvirBipe
- TestImagemNoMcp
- TestSonar
- TestCapacidades
- TestTermometro
- TestGreeVariante
- test_god_mode.py
- TestProtocolos
- Catalogo
- session-start.sh
- gree_variante.py
- Problemas já resolvidos (para não repetir)
- Sinal
- tv do quarto (TV Samsung)
- CLAUDE.md

## God Nodes (most connected - your core abstractions)
1. `Servico` - 52 edges
2. `Sinal` - 35 edges
3. `Catalogo` - 33 edges
4. `Descoberta` - 33 edges
5. `main()` - 30 edges
6. `criar_servidor()` - 27 edges
7. `normalizar()` - 26 edges
8. `Controlador` - 25 edges
9. `ErroUso` - 24 edges
10. `_iniciar()` - 24 edges

## Surprising Connections (you probably didn't know these)
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
- `variante()` --implements--> `Variante Gree a partir da captura real (troca só os bits)`  [INFERRED]
  ferramentas/gree_variante.py → docs/aparelhos/quarto/ar-do-quarto.md
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `ampliar_catalogo()`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/cli.py
- `Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper)` --conceptually_related_to--> `ler_flipper()`  [INFERRED]
  docs/aparelhos/README.md → controle-ir/controle_ir/formatos.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (52 total, 20 thin omitted)

### Community 0 - "f"
Cohesion: 0.23
Nodes (7): filtro(), ler_recortes(), main(), reduzir(), validar_recorte(), progresso_txt(), f()

### Community 1 - "protocolos.py"
Cohesion: 0.14
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 2 - "servico.py"
Cohesion: 0.06
Nodes (12): capacidades(), _curto(), _faixa_txt(), hora_legivel(), _linhas_aparelho(), resumo_aparelho(), executar(), Emissor (+4 more)

### Community 3 - "Descoberta"
Cohesion: 0.13
Nodes (4): agora(), Descoberta, ErroDescoberta, termo_por_chave()

### Community 4 - "cli.py"
Cohesion: 0.06
Nodes (41): ampliar_catalogo(), _api(), arquivo_boot(), atualizar(), _aviso(), boot_ativado(), caminho_log(), _carimbo_catalogo() (+33 more)

### Community 5 - "Controlador"
Cohesion: 0.16
Nodes (6): Controlador, Etapa, Plano, normalizar_valor(), valores_equivalentes(), TestControle

### Community 6 - "Serviço (operações MCP)"
Cohesion: 0.09
Nodes (18): EmissorSimulado, ErroUso, Servico, criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS() (+10 more)

### Community 7 - "Sinal"
Cohesion: 0.20
Nodes (13): adicionar_comando(), comando(), ErroFormato, _hex_le(), importar_texto(), indice_comandos(), ler_flipper(), ler_sinal_texto() (+5 more)

### Community 9 - "tela/principal.py"
Cohesion: 0.19
Nodes (17): achar(), agir(), app_em_foco(), bloqueado(), bloqueados(), captura(), dump_ui(), elementos() (+9 more)

### Community 10 - "sinais.py"
Cohesion: 0.13
Nodes (11): sinais_pronto(), broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta(), normalizar_pulsos(), pronto_para_pulsos(), pulsos_para_broadlink() (+3 more)

### Community 11 - "subprocess"
Cohesion: 0.21
Nodes (7): js(), rodar(), analisar_sonar(), gerar_tom(), main(), testar(), volume_musica()

### Community 13 - "ar do quarto (ar-condicionado Gree GWH09KF)"
Cohesion: 0.19
Nodes (14): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50) (+6 more)

### Community 14 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.06
Nodes (33): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+25 more)

### Community 15 - "os"
Cohesion: 0.18
Nodes (10): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+2 more)

### Community 18 - "Execucao"
Cohesion: 0.07
Nodes (8): exec_cli(), Autorizacao, classificar(), Execucao, gerar_segredo(), Politica, totp(), TestExecucao

### Community 19 - "Registro"
Cohesion: 0.19
Nodes (5): ErroCapacidade, _hash(), _manifesto(), Registro, capacidade_cli()

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "test_controle_ir.py"
Cohesion: 0.13
Nodes (3): catalogo_base(), TestCatalogo, TestVocabulario

### Community 25 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

### Community 26 - "json"
Cohesion: 0.23
Nodes (12): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+4 more)

### Community 29 - "normalizar"
Cohesion: 0.16
Nodes (12): normalizar_marca(), categoria_canonica(), chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar(), sem_acentos() (+4 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.18
Nodes (8): classificar(), ficha_upnp(), ip_do_wifi(), main(), sondar(), tcp(), udp(), vivos()

### Community 32 - "time"
Cohesion: 0.30
Nodes (9): ssdp(), analisar(), dns(), download(), gateway(), main(), ping(), rodar() (+1 more)

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
Cohesion: 0.14
Nodes (10): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), _unzip() (+2 more)

### Community 47 - "gree_variante.py"
Cohesion: 0.15
Nodes (12): arquivos_cc0(), main(), checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes() (+4 more)

### Community 48 - "Problemas já resolvidos (para não repetir)"
Cohesion: 0.15
Nodes (17): Anúncio dos testes (v1.0.1), Catálogo instalado: base + ampliado (9.380 perfis), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026) (+9 more)

### Community 49 - "Sinal"
Cohesion: 0.20
Nodes (6): escrever_flipper(), exportar(), sinal(), _sinal_smartir(), limitar_duracao(), Sinal

### Community 50 - "tv do quarto (TV Samsung)"
Cohesion: 0.27
Nodes (7): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung), Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas)

### Community 51 - "CLAUDE.md"
Cohesion: 0.27
Nodes (4): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, empacotar.sh script

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 271 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Serviço (operações MCP)` to `servico.py`, `Descoberta`, `cli.py`, `Controlador`, `novo_servico`, `Sinal`, `ServidorMCP`, `Execucao`, `Registro`, `tv do quarto (TV Samsung)`, `normalizar`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `Servico` (e.g. with `ServidorMCP` and `criar_servidor()`) actually correct?**
  _`Servico` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `protocolos.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13846153846153847 - nodes in this community are weakly interconnected._
- **Why does `Catalogo` connect `Catalogo` to `servico.py`, `Descoberta`, `cli.py`, `sinais.py`, `Problemas já resolvidos (para não repetir)`, `Sinal`, `normalizar`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `Sinal` (e.g. with `Catalogo` and `Emissor`) actually correct?**
  _`Sinal` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Should `servico.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05687645687645688 - nodes in this community are weakly interconnected._