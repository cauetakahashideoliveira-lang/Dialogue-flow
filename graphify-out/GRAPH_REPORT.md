# Graph Report - Dialogue-flow  (2026-11-19)

## Corpus Check
- 70 files · ~116,687 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 3, .ir 3, .gz 1)

## Summary
- 1508 nodes · 3600 edges · 74 communities (46 shown, 28 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 268 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `193547fc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- test_controle_ir.py
- TestPainel
- test_god_mode.py
- normalizar
- sys
- Controlador
- .passo
- re
- tela/principal.py
- Servico
- exec_cli
- package.json
- TestTelaPorArquivo
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- os
- Servico
- sinais.py
- Aparelhos
- mcp.py
- Instalador (instalar.sh)
- Tela
- Licenças dos dados
- Tunel
- TestSegundoPlano
- e2e.cjs
- json
- TestImagemNoMcp
- categoria_canonica
- gree_variante.py
- descobrir_rede/principal.py
- cli.py
- grade
- termometro/principal.py
- painel.py
- Politica
- TestOuvirBipe
- Canal
- TestSonar
- criar_servidor
- Sinal
- _Servidor
- test_god_mode.py
- protocolos.py
- webauthn.js
- session-start.sh
- formatos.py
- TestTermometro
- TestServidorMCP
- execucao.py
- autorizar.js
- app.js
- TestExecucao
- time
- novo_servico
- tv do quarto (TV Samsung)
- TestArmacao
- TestCapacidades
- TestTela
- .test_canal_repassa_chamada_e_aviso
- .aplicar_reflexo
- observador.py
- Reenvios
- subprocess
- TestProtocolos
- time
- Sincronizador
- servico.py
- Canal
- TestGreeVariante

## God Nodes (most connected - your core abstractions)
1. `Servico` - 51 edges
2. `Descoberta` - 36 edges
3. `Sinal` - 36 edges
4. `TestTelaPorArquivo` - 35 edges
5. `Tela` - 34 edges
6. `Catalogo` - 34 edges
7. `main()` - 32 edges
8. `criar_servidor()` - 29 edges
9. `_iniciar()` - 28 edges
10. `normalizar()` - 26 edges

## Surprising Connections (you probably didn't know these)
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `variante()` --implements--> `Variante Gree a partir da captura real (troca só os bits)`  [INFERRED]
  ferramentas/gree_variante.py → docs/aparelhos/quarto/ar-do-quarto.md
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `ampliar_catalogo()`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/cli.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (74 total, 28 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.10
Nodes (58): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+50 more)

### Community 1 - "test_controle_ir.py"
Cohesion: 0.12
Nodes (5): _curto(), _faixa_txt(), _linhas_aparelho(), main(), preparar()

### Community 2 - "TestPainel"
Cohesion: 0.09
Nodes (15): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono (+7 more)

### Community 4 - "normalizar"
Cohesion: 0.23
Nodes (14): comando(), ler_smartir(), _traduz(), chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar() (+6 more)

### Community 5 - "sys"
Cohesion: 0.21
Nodes (8): filtro(), ler_recortes(), main(), reduzir(), validar_recorte(), gravar(), progresso_txt(), f()

### Community 6 - "Controlador"
Cohesion: 0.09
Nodes (11): executar(), main(), Controlador, Etapa, Plano, Emissor, EmissorSimulado, normalizar_valor() (+3 more)

### Community 7 - ".passo"
Cohesion: 0.10
Nodes (9): achar(), achar_regra(), compactos(), eventos(), _Executor, relevantes(), _Falha, _Interrompido (+1 more)

### Community 8 - "re"
Cohesion: 0.15
Nodes (13): agir(), app_em_foco(), atividade_no_topo(), bloqueados(), _bloqueio_de_toque(), _contar(), _executar(), foco() (+5 more)

### Community 9 - "tela/principal.py"
Cohesion: 0.09
Nodes (19): _caixa(), _chave(), _conflitos(), curto(), diferenca(), diferenca_curta(), escapar_input_text(), historico() (+11 more)

### Community 10 - "Servico"
Cohesion: 0.06
Nodes (12): ErroCapacidade, _hash(), _manifesto(), modulo_embutido(), Registro, capacidade_cli(), Execucao, ErroUso (+4 more)

### Community 12 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, @simplewebauthn/browser@14.0.0, wrangler@4.165.0, name (+10 more)

### Community 14 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.06
Nodes (33): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+25 more)

### Community 15 - "os"
Cohesion: 0.18
Nodes (10): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+2 more)

### Community 16 - "Servico"
Cohesion: 0.07
Nodes (13): agora(), Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper() (+5 more)

### Community 17 - "sinais.py"
Cohesion: 0.13
Nodes (10): broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta(), limitar_duracao(), normalizar_pulsos(), pronto_para_pulsos(), pulsos_para_broadlink() (+2 more)

### Community 19 - "mcp.py"
Cohesion: 0.11
Nodes (4): resumo_para_instrucoes(), resumo_instrucoes(), ServidorMCP, TestResumoInstrucoes

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 24 - "TestSegundoPlano"
Cohesion: 0.15
Nodes (4): catalogo_base(), TestCatalogo, TestSegundoPlano, abrir_console()

### Community 25 - "e2e.cjs"
Cohesion: 0.09
Nodes (14): flagPath, fs, os, path, celular(), { chromium }, { execFileSync, spawn }, fs (+6 more)

### Community 26 - "json"
Cohesion: 0.27
Nodes (11): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+3 more)

### Community 28 - "TestImagemNoMcp"
Cohesion: 0.18
Nodes (4): _extrair_imagens(), varrer(), TestImagemNoMcp, TestImagensAninhadas

### Community 30 - "gree_variante.py"
Cohesion: 0.15
Nodes (12): arquivos_cc0(), main(), checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes() (+4 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.13
Nodes (9): classificar(), ficha_upnp(), ip_do_wifi(), main(), sondar(), ssdp(), tcp(), udp() (+1 more)

### Community 32 - "cli.py"
Cohesion: 0.06
Nodes (43): ampliar_catalogo(), _api(), armar_cli(), arquivo_boot(), atualizar(), _aviso(), boot_ativado(), caminho_log() (+35 more)

### Community 33 - "grade"
Cohesion: 0.09
Nodes (16): _abrir(), botao_fechar(), casas_xadrez(), classe_janela(), dentro(), elementos(), em_anuncio(), foto() (+8 more)

### Community 34 - "termometro/principal.py"
Cohesion: 0.33
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 35 - "painel.py"
Cohesion: 0.20
Nodes (11): painel_cli(), _b64(), estado_valido(), _eventos_novos(), gravar(), _http(), ler(), parear() (+3 more)

### Community 38 - "Canal"
Cohesion: 0.13
Nodes (3): Canal, _mascarar(), WebSocket

### Community 39 - "TestSonar"
Cohesion: 0.11
Nodes (4): _carregar_cap(), TestSonar, TestSono, TestVocabulario

### Community 40 - "criar_servidor"
Cohesion: 0.33
Nodes (12): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), local_ok() (+4 more)

### Community 41 - "Sinal"
Cohesion: 0.17
Nodes (4): ler_sinal_texto(), sinal(), _sinal_smartir(), Sinal

### Community 43 - "test_god_mode.py"
Cohesion: 0.11
Nodes (5): _Base, _ComServidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos

### Community 44 - "protocolos.py"
Cohesion: 0.15
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 47 - "formatos.py"
Cohesion: 0.20
Nodes (13): adicionar_comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos(), ler_flipper() (+5 more)

### Community 50 - "execucao.py"
Cohesion: 0.24
Nodes (4): classificar(), gerar_segredo(), armado(), permitido()

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.28
Nodes (14): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+6 more)

### Community 54 - "time"
Cohesion: 0.13
Nodes (17): trecho_do_microfone(), Ajudante, _ajudante(), _apagar(), captura(), dump_ui(), estado_rapido(), foto_rapida() (+9 more)

### Community 56 - "tv do quarto (TV Samsung)"
Cohesion: 0.06
Nodes (42): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF) (+34 more)

### Community 62 - ".aplicar_reflexo"
Cohesion: 0.13
Nodes (10): aplicar_regras(), els_fn(), bloqueado(), calma(), els_fn(), _injetar(), _modelos_do_teclado(), regra_vale() (+2 more)

### Community 63 - "observador.py"
Cohesion: 0.21
Nodes (7): apps_usando(), _capacidades_rodando(), em_uso(), quadro(), recursos_do_comando(), _tarefas(), _tela()

### Community 68 - "subprocess"
Cohesion: 0.16
Nodes (7): js(), rodar(), analisar_sonar(), gerar_tom(), main(), testar(), volume_musica()

### Community 74 - "time"
Cohesion: 0.36
Nodes (8): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi()

### Community 77 - "servico.py"
Cohesion: 0.18
Nodes (6): capacidades(), hora_legivel(), resumo_aparelho(), executar(), EmissorTermux, ErroEmissor

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 456 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `cli.py`, `test_controle_ir.py`, `normalizar`, `Controlador`, `criar_servidor`, `Sinal`, `servico.py`, `formatos.py`, `Servico`, `mcp.py`, `novo_servico`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `Servico` (e.g. with `ServidorMCP` and `criar_servidor()`) actually correct?**
  _`Servico` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.09830508474576272 - nodes in this community are weakly interconnected._
- **Why does `criar_servidor()` connect `criar_servidor` to `cli.py`, `test_controle_ir.py`, `Reenvios`, `TestPainel`, `Servico`, `formatos.py`, `mcp.py`, `novo_servico`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Descoberta` (e.g. with `Catalogo` and `ErroEmissor`) actually correct?**
  _`Descoberta` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_controle_ir.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12307692307692308 - nodes in this community are weakly interconnected._