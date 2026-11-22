# Graph Report - Dialogue-flow  (2026-11-22)

## Corpus Check
- 115 files · ~159,535 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 2312 nodes · 5226 edges · 131 communities (81 shown, 50 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 401 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `835cbcae`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- Descoberta
- TestPainel
- Conexao
- Sinal
- shutil
- Controlador
- .passo
- Celular
- TestSonarFrequencia
- test_controle_ir.py
- steps
- painel.py
- TestTelaPorArquivo
- aparelhos.py
- subprocess
- Catalogo
- protocolos.py
- package.json
- TestImagemNoMcp
- Instalador (instalar.sh)
- Tela
- CLAUDE.md
- subprocess
- re
- e2e.cjs
- json
- steps
- tela/principal.py
- Servico
- _iniciar
- descobrir_rede/principal.py
- TestEstadoCelularSemProc
- cli.py
- TestParidadeDoBloqueio
- schema.sql
- normalizar
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- Notificador
- TestOuvirBipe
- sonar/principal.py
- ServidorMCP
- Registro
- test_god_mode.py
- time
- webauthn.js
- session-start.sh
- hashlib
- Execucao
- Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude
- exec_cli
- autorizar.js
- app.js
- canal.py
- TestTermometro
- HANDOFF.md
- termometro/principal.py
- TestPiloto
- os
- .anotar
- observador.py
- TestSono
- godmode-tracker.js
- Passagem de bastão do Dialogue-flow
- Politica
- vocabulario.py
- criar_servidor
- local.cjs
- TestExecucao
- piloto.py
- objetivo
- Origens
- Cerebros
- BluetoothAdapter
- Piloto
- Motor
- TestArmacao
- ._laco
- TestPilotoVisao
- _ferramentas_piloto
- TestSegundoPlano
- 4. Mapa de oportunidades
- android.bluetooth.le.ScanResult
- TestObservador
- PlanoTest
- TestProtocolos
- TestServidorMCP
- Looper
- atualizar
- Ajudante
- bluetooth/principal.py
- BluetoothDevice
- _Servidor
- resumo_para_instrucoes
- Bluetooth.java
- TestCapacidades
- novo_servico
- atualizar_conhecimento.sh
- gree_variante.py
- estudo_xadrez.py
- TestVocabulario
- analisar.py
- ambiente_missao.py
- Contribuir com o Dialogue-flow
- Bluetooth
- calcular
- scripts
- Sincronizador
- Tunel
- TestTunel
- aplicar_regras
- TestLeitorJava
- resolver_grade
- .startScan
- AttributionSource
- construir_app_bluetooth.sh script
- Autonomia do planejador no POCO
- Process
- _linhas_do_passo
- TestAtualizacaoRecompila
- f
- TestFerramentasDaMissao

## God Nodes (most connected - your core abstractions)
1. `Servico` - 62 edges
2. `Celular` - 40 edges
3. `main()` - 38 edges
4. `Tela` - 37 edges
5. `Descoberta` - 37 edges
6. `Sinal` - 37 edges
7. `TestTelaPorArquivo` - 36 edges
8. `Catalogo` - 35 edges
9. `f()` - 35 edges
10. `TestExecutorObjetivo` - 32 edges

## Surprising Connections (you probably didn't know these)
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py
- `Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper)` --conceptually_related_to--> `ler_flipper()`  [INFERRED]
  docs/aparelhos/README.md → controle-ir/controle_ir/formatos.py
- `3a. Central de Controle (1.0.24, implementada) — `painel/`` --references--> `TestPainel`  [EXTRACTED]
  docs/seguranca.md → testes/test_controle_ir.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (131 total, 50 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.08
Nodes (59): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+51 more)

### Community 1 - "Descoberta"
Cohesion: 0.13
Nodes (3): agora(), Descoberta, ErroDescoberta

### Community 2 - "TestPainel"
Cohesion: 0.10
Nodes (15): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono (+7 more)

### Community 3 - "Conexao"
Cohesion: 0.18
Nodes (5): carregar_memoria(), ao_texto(), Conexao, _confianca(), _texto_do_evento()

### Community 4 - "Sinal"
Cohesion: 0.09
Nodes (11): broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta(), limitar_duracao(), normalizar_pulsos(), pronto_para_pulsos(), pulsos_para_broadlink() (+3 more)

### Community 5 - "shutil"
Cohesion: 0.36
Nodes (6): carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar()

### Community 6 - "Controlador"
Cohesion: 0.08
Nodes (13): hora_legivel(), Controlador, Etapa, executar(), Plano, Emissor, EmissorSimulado, EmissorTermux (+5 more)

### Community 7 - ".passo"
Cohesion: 0.10
Nodes (9): achar(), achar_regra(), eventos(), _Executor, els_fn(), relevantes(), _Falha, _Interrompido (+1 more)

### Community 8 - "Celular"
Cohesion: 0.08
Nodes (6): _carregar(), Celular, el(), TestExecutorObjetivo, decidir(), escolher()

### Community 9 - "TestSonarFrequencia"
Cohesion: 0.06
Nodes (8): _carregar(), _Resposta, TestDescobrirRedeSemWifi, TestDiagnosticoRede, urlopen(), TestSonarFrequencia, testar(), TestTermometroSemResposta

### Community 10 - "test_controle_ir.py"
Cohesion: 0.07
Nodes (4): main(), preparar(), TestApkAtualizado, TestManifesto

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "painel.py"
Cohesion: 0.12
Nodes (11): painel_cli(), _b64(), estado_valido(), _eventos_novos(), gravar(), _http(), ler(), parear() (+3 more)

### Community 14 - "aparelhos.py"
Cohesion: 0.13
Nodes (8): Aparelhos, capacidades(), _curto(), ErroAparelho, _faixa_txt(), _linhas_aparelho(), resumo_aparelho(), Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper)

### Community 15 - "subprocess"
Cohesion: 0.13
Nodes (12): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+4 more)

### Community 16 - "Catalogo"
Cohesion: 0.09
Nodes (11): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), normalizar_marca() (+3 more)

### Community 17 - "protocolos.py"
Cohesion: 0.16
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 18 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+10 more)

### Community 19 - "TestImagemNoMcp"
Cohesion: 0.18
Nodes (4): _extrair_imagens(), varrer(), TestImagemNoMcp, TestImagensAninhadas

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 22 - "CLAUDE.md"
Cohesion: 0.27
Nodes (4): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, empacotar.sh script

### Community 23 - "subprocess"
Cohesion: 0.22
Nodes (6): filtro(), ler_recortes(), main(), reduzir(), validar_recorte(), _jpeg()

### Community 24 - "re"
Cohesion: 0.12
Nodes (16): assinatura(), busca(), concluido(), Executor, fim(), interruptor(), melhor(), norm() (+8 more)

### Community 25 - "e2e.cjs"
Cohesion: 0.13
Nodes (11): celular(), { chromium }, { execFileSync, spawn }, filhos, fs, nodeCrypto, os, PASTA (+3 more)

### Community 26 - "json"
Cohesion: 0.23
Nodes (12): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+4 more)

### Community 27 - "steps"
Cohesion: 0.11
Nodes (17): jobs, pacote, name, on, push, workflow_dispatch, runs-on, steps (+9 more)

### Community 28 - "tela/principal.py"
Cohesion: 0.08
Nodes (22): _chave(), compactos(), _contar(), curto(), dentro(), diferenca(), diferenca_curta(), elementos() (+14 more)

### Community 29 - "Servico"
Cohesion: 0.14
Nodes (3): ErroUso, Servico, 2. Etapa 0 — armação diária local (1.0.23, implementada)

### Community 30 - "_iniciar"
Cohesion: 0.23
Nodes (11): _aviso(), iniciar(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir(), mostrar_url() (+3 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.16
Nodes (11): classificar(), ficha_upnp(), ip_do_wifi(), ler_inventarios(), main(), sondar(), ssdp(), tcp() (+3 more)

### Community 33 - "cli.py"
Cohesion: 0.10
Nodes (32): ampliar_catalogo(), _api(), arquivo_boot(), boot_ativado(), caminho_log(), _carimbo_catalogo(), carregar_config(), catalogo_atual() (+24 more)

### Community 35 - "schema.sql"
Cohesion: 0.12
Nodes (15): aparelhos, chamadas, config, convites, credenciais, desafios, estado, eventos (+7 more)

### Community 36 - "normalizar"
Cohesion: 0.14
Nodes (19): adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos() (+11 more)

### Community 37 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.17
Nodes (12): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade, 8. Próximos experimentos (ordem sugerida) (+4 more)

### Community 40 - "sonar/principal.py"
Cohesion: 0.22
Nodes (9): analisar_sonar(), escolher_e_testar(), frequencia_lembrada(), gerar_tom(), lembrar(), main(), sugestao_sem_tom(), testar() (+1 more)

### Community 42 - "Registro"
Cohesion: 0.20
Nodes (5): ErroCapacidade, _hash(), _manifesto(), Registro, capacidade_cli()

### Community 43 - "test_god_mode.py"
Cohesion: 0.11
Nodes (5): _Base, _ComServidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos

### Community 44 - "time"
Cohesion: 0.28
Nodes (9): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi() (+1 more)

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 47 - "hashlib"
Cohesion: 0.21
Nodes (7): _jar(), fontes(), impressao(), checksum(), empacotar(), fontes(), verificar()

### Community 49 - "Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude"
Cohesion: 0.12
Nodes (16): Botão Stockfish para estudos, Capacidades plugáveis (ferramentas novas sem mexer no núcleo), Cobertura dos testes, Como funciona, Conectar ao ChatGPT ou ao Claude, Descoberta, Desenvolvimento, Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude (+8 more)

### Community 50 - "exec_cli"
Cohesion: 0.24
Nodes (3): exec_cli(), Autorizacao, gerar_segredo()

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.26
Nodes (15): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+7 more)

### Community 53 - "canal.py"
Cohesion: 0.07
Nodes (6): Canal, _mascarar(), nome_da_chamada(), WebSocket, TestCanal, central()

### Community 56 - "termometro/principal.py"
Cohesion: 0.29
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 58 - "os"
Cohesion: 0.14
Nodes (21): _abrir(), agir(), _ajudante(), _apagar(), app_em_foco(), _bloqueio_de_toque(), calma(), captura() (+13 more)

### Community 59 - ".anotar"
Cohesion: 0.10
Nodes (5): BluetoothDevice, ScanRecord, ScanResult, ParcelUuid, SparseArray

### Community 60 - "observador.py"
Cohesion: 0.19
Nodes (8): relatar_uso(), apps_usando(), _capacidades_rodando(), em_uso(), quadro(), recursos_do_comando(), _tarefas(), _tela()

### Community 61 - "TestSono"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 62 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 64 - "Politica"
Cohesion: 0.26
Nodes (3): armar_cli(), Politica, fim_do_dia()

### Community 65 - "vocabulario.py"
Cohesion: 0.21
Nodes (11): chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar(), sem_acentos(), slug(), _t() (+3 more)

### Community 66 - "criar_servidor"
Cohesion: 0.30
Nodes (12): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), local_ok() (+4 more)

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 69 - "piloto.py"
Cohesion: 0.12
Nodes (7): caixa_da_pergunta(), corpo_api(), fen(), gravar_memoria(), minha_cor(), quem_mexeu(), tabuleiro_txt()

### Community 70 - "objetivo"
Cohesion: 0.20
Nodes (8): classe_janela(), em_anuncio(), objetivo(), abrir(), aplicar_regras(), bloqueado(), elementos(), recolher()

### Community 74 - "Piloto"
Cohesion: 0.19
Nodes (3): ler_chave(), Piloto, p()

### Community 77 - "._laco"
Cohesion: 0.31
Nodes (3): chave_quiz(), norm(), quiz_da_tela()

### Community 79 - "_ferramentas_piloto"
Cohesion: 0.12
Nodes (13): atividade_no_topo(), botao_fechar(), casas_xadrez(), foto(), _ferramentas_piloto(), aguardar(), tabuleiro_local(), tela_chess() (+5 more)

### Community 80 - "TestSegundoPlano"
Cohesion: 0.08
Nodes (7): catalogo_base(), TestCatalogo, TestRepositorio, TestSegundoPlano, abrir_console(), reiniciado(), TestStockfishLocal

### Community 81 - "4. Mapa de oportunidades"
Cohesion: 0.33
Nodes (6): 4. Mapa de oportunidades, Casa e rede, Celular e Android, Computadores, nuvem e agentes, O próprio sistema, Observar o resultado (agir → medir → ajustar)

### Community 86 - "TestServidorMCP"
Cohesion: 0.17
Nodes (3): julgar_depois(), Reenvios, TestServidorMCP

### Community 90 - "bluetooth/principal.py"
Cohesion: 0.12
Nodes (19): buscar(), buscar_app(), buscar_shell(), classificar(), compilar(), distancia(), guardar(), _ler_marca() (+11 more)

### Community 99 - "gree_variante.py"
Cohesion: 0.05
Nodes (49): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50) (+41 more)

### Community 100 - "estudo_xadrez.py"
Cohesion: 0.26
Nodes (9): modulo_embutido(), abrir(), configurar(), estudar(), ler_preferencias(), mostrar(), piloto_local(), Preferencias (+1 more)

### Community 102 - "analisar.py"
Cohesion: 0.31
Nodes (6): agenda(), analisar(), extras(), percentil95(), Comparação do planejador de missões no POCO, Rodada

### Community 104 - "ambiente_missao.py"
Cohesion: 0.18
Nodes (7): consultar_modelo(), contexto(), executar(), planejar(), RespostaDePlanoInvalida, armado(), permitido()

### Community 105 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

### Community 106 - "Bluetooth"
Cohesion: 0.15
Nodes (5): Runnable, Bluetooth, Runnable, ScanSettings, Builder

### Community 107 - "calcular"
Cohesion: 0.40
Nodes (3): calcular(), ev(), escolher_pela_conta()

### Community 109 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, deploy, dev, test:e2e

### Community 114 - "aplicar_regras"
Cohesion: 0.25
Nodes (6): aplicar_regras(), els_fn(), tocar(), _injetar(), injetar(), regra_vale()

### Community 115 - "TestLeitorJava"
Cohesion: 0.05
Nodes (7): _carregar(), TestAppAuxiliar, TestBuscarNoCelular, TestClassificacao, TestCompilar, TestLeitorJava, TestTelaDicaDoCampo

### Community 116 - "resolver_grade"
Cohesion: 0.25
Nodes (5): _caixa(), _conflitos(), resolver_grade(), busca(), resolver_sudoku()

### Community 125 - "Autonomia do planejador no POCO"
Cohesion: 0.40
Nodes (5): Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente

### Community 128 - "TestAtualizacaoRecompila"
Cohesion: 0.15
Nodes (3): TestAtualizacaoRecompila, TestResumoSemRepeticao, TestGodModeStmEPontuacao

### Community 129 - "f"
Cohesion: 0.11
Nodes (20): bloqueado(), bloqueados(), executar(), _executar(), escolher(), main(), _modulo_piloto(), navegar() (+12 more)

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 754 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **50 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `cli.py`, `Descoberta`, `vocabulario.py`, `gree_variante.py`, `Sinal`, `Controlador`, `normalizar`, `criar_servidor`, `ServidorMCP`, `test_controle_ir.py`, `Registro`, `novo_servico`, `aparelhos.py`, `Catalogo`, `Execucao`, `_iniciar`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.08208955223880597 - nodes in this community are weakly interconnected._
- **Why does `Catalogo` connect `Catalogo` to `Descoberta`, `cli.py`, `Sinal`, `normalizar`, `test_controle_ir.py`, `Servico`, `_iniciar`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Should `Descoberta` be split into smaller, more focused modules?**
  _Cohesion score 0.12926829268292683 - nodes in this community are weakly interconnected._
- **Why does `f()` connect `f` to `Descoberta`, `Conexao`, `Celular`, `TestSonarFrequencia`, `aparelhos.py`, `subprocess`, `Catalogo`, `subprocess`, `re`, `json`, `descobrir_rede/principal.py`, `cli.py`, `sonar/principal.py`, `Execucao`, `termometro/principal.py`, `piloto.py`, `objetivo`, `atualizar`, `bluetooth/principal.py`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._