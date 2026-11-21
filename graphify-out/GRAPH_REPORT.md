# Graph Report - Dialogue-flow  (2026-11-21)

## Corpus Check
- 115 files · ~157,025 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 2281 nodes · 5164 edges · 137 communities (82 shown, 55 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 395 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `7ffcc82f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- TestGodModeStmEPontuacao
- TestPainel
- Conexao
- normalizar
- shutil
- Controlador
- .passo
- Celular
- TestSonarFrequencia
- test_controle_ir.py
- steps
- canal.py
- TestTelaPorArquivo
- servico.py
- subprocess
- Descoberta
- Sinal
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- tela/principal.py
- Instalador (instalar.sh)
- Tela
- carregar_config
- subprocess
- objetivo.py
- e2e.cjs
- json
- steps
- tela/principal.py
- Registro
- tv do quarto (TV Samsung)
- descobrir_rede/principal.py
- gree_variante.py
- Execucao
- protocolos.py
- schema.sql
- formatos.py
- Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude
- package.json
- TestOuvirBipe
- sonar/principal.py
- ServidorMCP
- diagnostico_rede/principal.py
- test_god_mode.py
- canal.py
- webauthn.js
- session-start.sh
- ErroEmissor
- ambiente_missao.py
- Servico
- exec_cli
- autorizar.js
- app.js
- Canal
- Servico
- HANDOFF.md
- termometro/principal.py
- TestPiloto
- os
- .anotar
- modulo_embutido
- TestSono
- construir_catalogo.py
- Passagem de bastão do Dialogue-flow
- Politica
- nome_da_chamada
- criar_servidor
- local.cjs
- TestExecucao
- piloto.py
- hashlib
- diagnostico_rede/principal.py
- Cerebros
- BluetoothAdapter
- Piloto
- Motor
- TestArmacao
- observador.py
- Executor
- fechar_anuncio
- TestSegundoPlano
- EmissorSimulado
- android.bluetooth.le.ScanResult
- _iniciar
- PlanoTest
- Reenvios
- modulo_embutido
- Looper
- cli.py
- pacote.py
- bluetooth/principal.py
- BluetoothClass
- _Servidor
- resumo_para_instrucoes
- Bluetooth.java
- TestCapacidades
- novo_servico
- atualizar_conhecimento.sh
- Estado atual da instalação (17/11/2026)
- godmode-tracker.js
- TestParidadeDoBloqueio
- catalogo_base
- TestGreeVariante
- TestEstadoCelularSemProc
- Contribuir com o Dialogue-flow
- Bluetooth
- TestServidorMCP
- Notificador
- Variante Gree a partir da captura real (troca só os bits)
- Tunel
- Autonomia do planejador no POCO
- TestObservador
- TestLeitorJava
- TestProtocolos
- .startScan
- Pacote do celular dist/controle-ir.zip
- scripts
- AttributionSource
- construir_app_bluetooth.sh script
- TestResumoSemRepeticao
- Process
- re
- TestTunel
- time
- TestImagemNoMcp
- TestAtualizacaoRecompila
- TestVocabulario
- TestRepositorio

## God Nodes (most connected - your core abstractions)
1. `Servico` - 62 edges
2. `Celular` - 38 edges
3. `main()` - 38 edges
4. `Tela` - 37 edges
5. `Descoberta` - 37 edges
6. `Sinal` - 37 edges
7. `TestTelaPorArquivo` - 36 edges
8. `Catalogo` - 35 edges
9. `f()` - 34 edges
10. `criar_servidor()` - 31 edges

## Surprising Connections (you probably didn't know these)
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
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

## Communities (137 total, 55 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.08
Nodes (59): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+51 more)

### Community 2 - "TestPainel"
Cohesion: 0.10
Nodes (15): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono (+7 more)

### Community 3 - "Conexao"
Cohesion: 0.18
Nodes (5): carregar_memoria(), ao_texto(), Conexao, _confianca(), _texto_do_evento()

### Community 4 - "normalizar"
Cohesion: 0.22
Nodes (10): _traduz(), chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar(), sem_acentos(), _t() (+2 more)

### Community 5 - "shutil"
Cohesion: 0.24
Nodes (6): carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar()

### Community 6 - "Controlador"
Cohesion: 0.16
Nodes (6): Controlador, Etapa, Plano, normalizar_valor(), valores_equivalentes(), TestControle

### Community 7 - ".passo"
Cohesion: 0.09
Nodes (10): achar(), achar_regra(), compactos(), eventos(), _Executor, relevantes(), _Falha, _Interrompido (+2 more)

### Community 8 - "Celular"
Cohesion: 0.08
Nodes (6): _carregar(), Celular, el(), TestExecutorObjetivo, decidir(), escolher()

### Community 9 - "TestSonarFrequencia"
Cohesion: 0.06
Nodes (8): _carregar(), _Resposta, TestDescobrirRedeSemWifi, TestDiagnosticoRede, urlopen(), TestSonarFrequencia, testar(), TestTermometroSemResposta

### Community 10 - "test_controle_ir.py"
Cohesion: 0.11
Nodes (3): TestApkAtualizado, TestManifesto, TestFerramentasDaMissao

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "canal.py"
Cohesion: 0.12
Nodes (12): painel_cli(), _b64(), estado_valido(), _eventos_novos(), gravar(), _http(), ler(), parear() (+4 more)

### Community 14 - "servico.py"
Cohesion: 0.07
Nodes (12): capacidades(), _curto(), ErroAparelho, _faixa_txt(), hora_legivel(), _linhas_aparelho(), resumo_aparelho(), resumo_para_instrucoes() (+4 more)

### Community 15 - "subprocess"
Cohesion: 0.18
Nodes (10): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+2 more)

### Community 16 - "Descoberta"
Cohesion: 0.06
Nodes (15): agora(), Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper() (+7 more)

### Community 17 - "Sinal"
Cohesion: 0.09
Nodes (17): escrever_flipper(), exportar(), sinal(), sinais_pronto(), broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta() (+9 more)

### Community 18 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.11
Nodes (18): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+10 more)

### Community 19 - "tela/principal.py"
Cohesion: 0.08
Nodes (24): _bloqueio_de_toque(), _chave(), _contar(), curto(), dentro(), diferenca(), diferenca_curta(), escapar_input_text() (+16 more)

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 22 - "carregar_config"
Cohesion: 0.22
Nodes (12): _api(), carregar_config(), console(), url_quando_pronta(), estado_servidor(), iniciar_em_segundo_plano(), parar_servico(), _porta_ativa() (+4 more)

### Community 23 - "subprocess"
Cohesion: 0.27
Nodes (5): filtro(), ler_recortes(), main(), reduzir(), validar_recorte()

### Community 24 - "objetivo.py"
Cohesion: 0.16
Nodes (13): assinatura(), busca(), concluido(), interruptor(), melhor(), norm(), proibido(), ranquear() (+5 more)

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
Cohesion: 0.09
Nodes (14): _caixa(), _conflitos(), elementos(), grade(), ler_bounds(), _ler_grade(), _modelos_do_teclado(), _plano() (+6 more)

### Community 29 - "Registro"
Cohesion: 0.20
Nodes (5): ErroCapacidade, _hash(), _manifesto(), Registro, capacidade_cli()

### Community 30 - "tv do quarto (TV Samsung)"
Cohesion: 0.18
Nodes (16): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50), Ligar/desligar diretos (energia_ligar 0x99, energia_desligar 0x98) (+8 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.16
Nodes (11): classificar(), ficha_upnp(), ip_do_wifi(), ler_inventarios(), main(), sondar(), ssdp(), tcp() (+3 more)

### Community 32 - "gree_variante.py"
Cohesion: 0.22
Nodes (10): checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main(), perfil() (+2 more)

### Community 34 - "protocolos.py"
Cohesion: 0.17
Nodes (15): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+7 more)

### Community 35 - "schema.sql"
Cohesion: 0.12
Nodes (15): aparelhos, chamadas, config, convites, credenciais, desafios, estado, eventos (+7 more)

### Community 36 - "formatos.py"
Cohesion: 0.24
Nodes (12): adicionar_comando(), comando(), ErroFormato, _hex_le(), importar_texto(), indice_comandos(), ler_flipper(), ler_sinal_texto() (+4 more)

### Community 37 - "Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude"
Cohesion: 0.12
Nodes (16): Botão Stockfish para estudos, Capacidades plugáveis (ferramentas novas sem mexer no núcleo), Cobertura dos testes, Como funciona, Conectar ao ChatGPT ou ao Claude, Descoberta, Desenvolvimento, Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude (+8 more)

### Community 38 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+10 more)

### Community 40 - "sonar/principal.py"
Cohesion: 0.23
Nodes (8): analisar_sonar(), escolher_e_testar(), frequencia_lembrada(), gerar_tom(), main(), sugestao_sem_tom(), testar(), volume_musica()

### Community 42 - "diagnostico_rede/principal.py"
Cohesion: 0.38
Nodes (4): agenda(), analisar(), extras(), percentil95()

### Community 43 - "test_god_mode.py"
Cohesion: 0.11
Nodes (5): _Base, _ComServidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 47 - "ErroEmissor"
Cohesion: 0.20
Nodes (3): Emissor, EmissorTermux, ErroEmissor

### Community 48 - "ambiente_missao.py"
Cohesion: 0.18
Nodes (7): consultar_modelo(), contexto(), executar(), planejar(), RespostaDePlanoInvalida, armado(), permitido()

### Community 50 - "exec_cli"
Cohesion: 0.24
Nodes (3): exec_cli(), Autorizacao, gerar_segredo()

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.26
Nodes (15): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+7 more)

### Community 54 - "Servico"
Cohesion: 0.13
Nodes (9): Aparelhos, ErroUso, slug(), Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Smart Hub 0x79 (tecla inicio_3), Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper), Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas) (+1 more)

### Community 55 - "HANDOFF.md"
Cohesion: 0.18
Nodes (5): Comparação do planejador de missões no POCO, Rodada, Contexto para o Claude Code, Skill graphify (query, explain, path, update), Licenças dos dados de controle

### Community 56 - "termometro/principal.py"
Cohesion: 0.29
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 58 - "os"
Cohesion: 0.11
Nodes (19): gravar_memoria(), Ajudante, _ajudante(), _apagar(), app_em_foco(), captura(), dump_ui(), estado_rapido() (+11 more)

### Community 59 - ".anotar"
Cohesion: 0.10
Nodes (5): BluetoothDevice, ScanRecord, ScanResult, ParcelUuid, SparseArray

### Community 61 - "TestSono"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 64 - "Politica"
Cohesion: 0.26
Nodes (3): armar_cli(), Politica, fim_do_dia()

### Community 65 - "nome_da_chamada"
Cohesion: 0.15
Nodes (3): nome_da_chamada(), TestCanal, central()

### Community 66 - "criar_servidor"
Cohesion: 0.30
Nodes (12): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), local_ok() (+4 more)

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 69 - "piloto.py"
Cohesion: 0.15
Nodes (7): chave_quiz(), fen(), minha_cor(), norm(), quem_mexeu(), quiz_da_tela(), tabuleiro_txt()

### Community 70 - "hashlib"
Cohesion: 0.22
Nodes (5): buscar_shell(), compilar(), ler_registro(), fontes(), impressao()

### Community 71 - "diagnostico_rede/principal.py"
Cohesion: 0.40
Nodes (8): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi()

### Community 72 - "Cerebros"
Cohesion: 0.15
Nodes (4): Cerebros, corpo_api(), ler_chave(), prompt_quiz()

### Community 77 - "observador.py"
Cohesion: 0.19
Nodes (8): relatar_uso(), apps_usando(), _capacidades_rodando(), em_uso(), quadro(), recursos_do_comando(), _tarefas(), _tela()

### Community 78 - "Executor"
Cohesion: 0.28
Nodes (3): Executor, fim(), sistema()

### Community 79 - "fechar_anuncio"
Cohesion: 0.14
Nodes (10): _abrir(), aplicar_regras(), els_fn(), botao_fechar(), calma(), els_fn(), fechar_anuncio(), _injetar() (+2 more)

### Community 80 - "TestSegundoPlano"
Cohesion: 0.24
Nodes (3): TestSegundoPlano, abrir_console(), reiniciado()

### Community 83 - "_iniciar"
Cohesion: 0.36
Nodes (8): _aviso(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir(), mostrar_url(), _termux()

### Community 86 - "modulo_embutido"
Cohesion: 0.30
Nodes (7): abrir(), configurar(), estudar(), ler_preferencias(), mostrar(), Preferencias, stockfish_local()

### Community 88 - "cli.py"
Cohesion: 0.09
Nodes (26): ampliar_catalogo(), arquivo_boot(), atualizar(), boot_ativado(), caminho_log(), _carimbo_catalogo(), catalogo_atual(), _cfg_caminho() (+18 more)

### Community 89 - "pacote.py"
Cohesion: 0.36
Nodes (4): checksum(), empacotar(), fontes(), verificar()

### Community 90 - "bluetooth/principal.py"
Cohesion: 0.14
Nodes (15): buscar(), buscar_app(), classificar(), distancia(), _ler_marca(), ler_pareados_dumpsys(), main(), _marcar() (+7 more)

### Community 97 - "novo_servico"
Cohesion: 0.11
Nodes (3): novo_servico(), TestTela, TestTermometro

### Community 99 - "Estado atual da instalação (17/11/2026)"
Cohesion: 0.17
Nodes (16): Anúncio dos testes (v1.0.1), Catálogo instalado: base + ampliado (9.380 perfis), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026) (+8 more)

### Community 100 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

### Community 105 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

### Community 106 - "Bluetooth"
Cohesion: 0.15
Nodes (5): Runnable, Bluetooth, Runnable, ScanSettings, Builder

### Community 109 - "Variante Gree a partir da captura real (troca só os bits)"
Cohesion: 0.40
Nodes (3): Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105), Perfil Gree Unknown (catálogo nº 102), descartado

### Community 113 - "Autonomia do planejador no POCO"
Cohesion: 0.40
Nodes (5): Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente

### Community 115 - "TestLeitorJava"
Cohesion: 0.05
Nodes (7): _carregar(), TestAppAuxiliar, TestBuscarNoCelular, TestClassificacao, TestCompilar, TestLeitorJava, TestTelaDicaDoCampo

### Community 119 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, deploy, dev, test:e2e

### Community 127 - "re"
Cohesion: 0.14
Nodes (12): atividade_no_topo(), casas_xadrez(), classe_janela(), em_anuncio(), foto(), _ferramentas_piloto(), aguardar(), tabuleiro_local() (+4 more)

### Community 129 - "time"
Cohesion: 0.12
Nodes (24): guardar(), lembrar(), agir(), bloqueado(), bloqueados(), _executar(), escolher(), foco() (+16 more)

### Community 133 - "TestImagemNoMcp"
Cohesion: 0.18
Nodes (4): _extrair_imagens(), varrer(), TestImagemNoMcp, TestImagensAninhadas

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 739 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **55 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TestPiloto` connect `TestPiloto` to `servico.py`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.08208955223880597 - nodes in this community are weakly interconnected._
- **Why does `Servico` connect `Servico` to `Execucao`, `criar_servidor`, `novo_servico`, `Controlador`, `ServidorMCP`, `servico.py`, `ErroEmissor`, `Descoberta`, `Sinal`, `EmissorSimulado`, `_iniciar`, `Servico`, `cli.py`, `Registro`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Should `TestPainel` be split into smaller, more focused modules?**
  _Cohesion score 0.09788359788359788 - nodes in this community are weakly interconnected._
- **Why does `Descoberta` connect `Descoberta` to `Sinal`, `Servico`, `servico.py`, `ErroEmissor`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._