# Graph Report - Dialogue-flow  (2026-11-19)

## Corpus Check
- 68 files · ~95,813 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 3, .ir 3, .gz 1)

## Summary
- 1231 nodes · 2954 edges · 63 communities (41 shown, 22 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 261 edges (avg confidence: 0.87)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `6035a7e8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- protocolos.py
- TestPainel
- Descoberta
- cli.py
- sys
- Controlador
- normalizar
- criar_servidor
- tela/principal.py
- categoria_canonica
- sonar/principal.py
- observador.py
- TestTelaPorArquivo
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- os
- Sinal
- Aparelhos
- Servico
- Instalador (instalar.sh)
- Catalogo
- Licenças dos dados
- Tunel
- TestSegundoPlano
- e2e.cjs
- json
- TestExecucao
- gree_variante.py
- descobrir_rede/principal.py
- time
- termometro/principal.py
- painel.py
- novo_servico
- TestOuvirBipe
- formatos.py
- TestSonar
- os
- package.json
- TestGreeVariante
- test_god_mode.py
- test_controle_ir.py
- webauthn.js
- session-start.sh
- TestServidorMCP
- Problemas já resolvidos (para não repetir)
- servico.py
- autorizar.js
- app.js
- .controlar
- TestCapacidades
- TestTermometro
- tv do quarto (TV Samsung)
- CLAUDE.md
- resumo_para_instrucoes
- verificar_cliente_mcp.py
- construir_catalogo.py
- _Servidor
- ar do quarto (ar-condicionado Gree GWH09KF)
- novo_servico
- test_controle_ir.py

## God Nodes (most connected - your core abstractions)
1. `Servico` - 63 edges
2. `Descoberta` - 37 edges
3. `Sinal` - 37 edges
4. `Catalogo` - 35 edges
5. `main()` - 32 edges
6. `criar_servidor()` - 27 edges
7. `Controlador` - 26 edges
8. `normalizar()` - 26 edges
9. `_iniciar()` - 26 edges
10. `ErroUso` - 23 edges

## Surprising Connections (you probably didn't know these)
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `ampliar_catalogo()`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/cli.py
- `variante()` --implements--> `Variante Gree a partir da captura real (troca só os bits)`  [INFERRED]
  ferramentas/gree_variante.py → docs/aparelhos/quarto/ar-do-quarto.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (63 total, 22 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.11
Nodes (53): acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao(), autorizar() (+45 more)

### Community 1 - "protocolos.py"
Cohesion: 0.13
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 2 - "TestPainel"
Cohesion: 0.10
Nodes (14): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono, 6. Limites que nenhuma etapa remove (+6 more)

### Community 3 - "Descoberta"
Cohesion: 0.12
Nodes (3): agora(), Descoberta, ErroDescoberta

### Community 4 - "cli.py"
Cohesion: 0.05
Nodes (46): ampliar_catalogo(), _api(), arquivo_boot(), atualizar(), _aviso(), boot_ativado(), caminho_log(), _carimbo_catalogo() (+38 more)

### Community 5 - "sys"
Cohesion: 0.27
Nodes (5): filtro(), ler_recortes(), main(), reduzir(), validar_recorte()

### Community 6 - "Controlador"
Cohesion: 0.08
Nodes (13): hora_legivel(), Controlador, Etapa, executar(), Plano, Emissor, EmissorSimulado, EmissorTermux (+5 more)

### Community 7 - "normalizar"
Cohesion: 0.21
Nodes (14): comando(), ler_smartir(), _traduz(), chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar() (+6 more)

### Community 8 - "criar_servidor"
Cohesion: 0.10
Nodes (16): resumo_instrucoes(), _extrair_imagens(), ServidorMCP, criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS() (+8 more)

### Community 9 - "tela/principal.py"
Cohesion: 0.14
Nodes (20): achar(), agir(), app_em_foco(), bloqueado(), bloqueados(), _bloqueio_de_toque(), compactos(), elementos() (+12 more)

### Community 11 - "sonar/principal.py"
Cohesion: 0.24
Nodes (5): analisar_sonar(), gerar_tom(), main(), testar(), volume_musica()

### Community 12 - "observador.py"
Cohesion: 0.19
Nodes (7): apps_usando(), _capacidades_rodando(), em_uso(), quadro(), recursos_do_comando(), _tarefas(), _tela()

### Community 14 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.06
Nodes (33): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+25 more)

### Community 15 - "os"
Cohesion: 0.12
Nodes (14): js(), rodar(), analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela() (+6 more)

### Community 17 - "Sinal"
Cohesion: 0.10
Nodes (12): sinal(), broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta(), limitar_duracao(), normalizar_pulsos(), pronto_para_pulsos() (+4 more)

### Community 19 - "Servico"
Cohesion: 0.06
Nodes (11): ErroCapacidade, _hash(), _manifesto(), Registro, capacidade_cli(), Execucao, ErroUso, Servico (+3 more)

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Catalogo"
Cohesion: 0.14
Nodes (10): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), _unzip() (+2 more)

### Community 24 - "TestSegundoPlano"
Cohesion: 0.15
Nodes (4): catalogo_base(), TestCatalogo, TestSegundoPlano, abrir_console()

### Community 25 - "e2e.cjs"
Cohesion: 0.09
Nodes (14): flagPath, fs, os, path, celular(), { chromium }, { execFileSync, spawn }, fs (+6 more)

### Community 26 - "json"
Cohesion: 0.23
Nodes (12): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+4 more)

### Community 30 - "gree_variante.py"
Cohesion: 0.22
Nodes (10): checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main(), perfil() (+2 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.18
Nodes (9): classificar(), ficha_upnp(), ip_do_wifi(), main(), sondar(), ssdp(), tcp(), udp() (+1 more)

### Community 32 - "time"
Cohesion: 0.38
Nodes (8): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi()

### Community 34 - "termometro/principal.py"
Cohesion: 0.33
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 35 - "painel.py"
Cohesion: 0.06
Nodes (18): armar_cli(), painel_cli(), Politica, _b64(), estado_valido(), _eventos_novos(), gravar(), _http() (+10 more)

### Community 38 - "formatos.py"
Cohesion: 0.16
Nodes (15): adicionar_comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos(), ler_flipper() (+7 more)

### Community 39 - "TestSonar"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 40 - "os"
Cohesion: 0.17
Nodes (11): _apagar(), captura(), dump_ui(), _jpeg(), _ler(), observar(), _pasta_troca(), rish() (+3 more)

### Community 41 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, @simplewebauthn/browser@14.0.0, wrangler@4.165.0, name (+10 more)

### Community 43 - "test_god_mode.py"
Cohesion: 0.11
Nodes (5): _Base, _ComServidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 48 - "Problemas já resolvidos (para não repetir)"
Cohesion: 0.19
Nodes (15): Anúncio dos testes (v1.0.1), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026), Frases (+7 more)

### Community 50 - "servico.py"
Cohesion: 0.20
Nodes (5): capacidades(), _curto(), _faixa_txt(), _linhas_aparelho(), resumo_aparelho()

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.28
Nodes (14): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+6 more)

### Community 53 - ".controlar"
Cohesion: 0.36
Nodes (8): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Cômodo: Escritório, Cômodo: Laboratório, Cômodo: Quarto, Índice de aparelhos (cômodo → aparelho → controle), Aparelhos salvos

### Community 60 - "tv do quarto (TV Samsung)"
Cohesion: 0.23
Nodes (9): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung), Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas), Catálogo instalado: base + ampliado (9.380 perfis) (+1 more)

### Community 61 - "CLAUDE.md"
Cohesion: 0.27
Nodes (4): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, empacotar.sh script

### Community 67 - "ar do quarto (ar-condicionado Gree GWH09KF)"
Cohesion: 0.31
Nodes (6): Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50), Ligar/desligar diretos (energia_ligar 0x99, energia_desligar 0x98)

### Community 69 - "test_controle_ir.py"
Cohesion: 0.11
Nodes (3): TestObservador, TestProtocolos, TestVocabulario

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 357 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `verificar_cliente_mcp.py`, `Descoberta`, `cli.py`, `novo_servico`, `Controlador`, `normalizar`, `criar_servidor`, `formatos.py`, `servidor.py`, `Sinal`, `servico.py`, `Aparelhos`, `Catalogo`?**
  _High betweenness centrality (0.114) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `Servico` (e.g. with `ServidorMCP` and `Aparelhos`) actually correct?**
  _`Servico` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.1063973063973064 - nodes in this community are weakly interconnected._
- **Why does `Descoberta` connect `Descoberta` to `Controlador`, `categoria_canonica`, `Sinal`, `servico.py`, `Servico`, `Catalogo`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `Descoberta` (e.g. with `Catalogo` and `ErroEmissor`) actually correct?**
  _`Descoberta` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Should `protocolos.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13105413105413105 - nodes in this community are weakly interconnected._