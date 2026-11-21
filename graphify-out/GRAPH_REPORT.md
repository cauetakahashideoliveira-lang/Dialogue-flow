# Graph Report - Dialogue-flow  (2026-11-21)

## Corpus Check
- 115 files · ~156,117 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 2275 nodes · 5138 edges · 131 communities (78 shown, 53 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 391 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `4b9c2e3a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- test_controle_ir.py
- TestPainel
- Conexao
- normalizar
- shutil
- Controlador
- .passo
- Celular
- TestSonarFrequencia
- Politica
- steps
- canal.py
- TestTelaPorArquivo
- test_controle_ir.py
- subprocess
- Descoberta
- sinais.py
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- f
- Instalador (instalar.sh)
- Tela
- dump_ui
- subprocess
- objetivo.py
- e2e.cjs
- json
- steps
- re
- Servico
- ar do escritório (ar-condicionado Carrier)
- descobrir_rede/principal.py
- gree_variante.py
- novo_servico
- exec_cli
- schema.sql
- formatos.py
- resolver_grade
- package.json
- TestOuvirBipe
- sonar/principal.py
- ServidorMCP
- analisar.py
- test_god_mode.py
- protocolos.py
- webauthn.js
- session-start.sh
- main
- ambiente_missao.py
- TestExecucao
- .controlar
- autorizar.js
- app.js
- Canal
- ErroUso
- HANDOFF.md
- aplicar_regras
- TestPiloto
- TestGreeVariante
- .anotar
- TestSono
- modulo_embutido
- Passagem de bastão do Dialogue-flow
- TestGodModeStmEPontuacao
- TestServidorMCP
- os
- local.cjs
- TestEstadoCelularSemProc
- piloto.py
- .decidir
- Autonomia do planejador no POCO
- Cerebros
- BluetoothAdapter
- Piloto
- Motor
- TestArmacao
- observador.py
- ErroEmissor
- tela/principal.py
- TestSegundoPlano
- android.bluetooth.le.ScanResult
- PlanoTest
- novo_servico
- modulo_embutido
- Looper
- cli.py
- TestObservador
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
- cli.py
- _iniciar
- TestAtualizacaoRecompila
- Contribuir com o Dialogue-flow
- Bluetooth
- TestProtocolos
- TestTermometro
- tv do quarto (TV Samsung)
- Pacote do celular dist/controle-ir.zip
- Tunel
- Sincronizador
- TestVocabulario
- TestLeitorJava
- _extrair_imagens
- .startScan
- scripts
- AttributionSource
- construir_app_bluetooth.sh script
- Process
- grade
- TestTunel
- rish
- TestResumoSemRepeticao
- TestRepositorio

## God Nodes (most connected - your core abstractions)
1. `Servico` - 62 edges
2. `main()` - 38 edges
3. `Tela` - 37 edges
4. `Descoberta` - 37 edges
5. `Sinal` - 37 edges
6. `TestTelaPorArquivo` - 36 edges
7. `Catalogo` - 35 edges
8. `Celular` - 34 edges
9. `f()` - 32 edges
10. `criar_servidor()` - 31 edges

## Surprising Connections (you probably didn't know these)
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py
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

## Communities (131 total, 53 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.08
Nodes (59): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+51 more)

### Community 1 - "test_controle_ir.py"
Cohesion: 0.07
Nodes (6): executar(), main(), preparar(), TestApkAtualizado, TestManifesto, TestFerramentasDaMissao

### Community 2 - "TestPainel"
Cohesion: 0.06
Nodes (30): julgar_depois(), criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json() (+22 more)

### Community 3 - "Conexao"
Cohesion: 0.24
Nodes (3): carregar_memoria(), Conexao, _texto_do_evento()

### Community 4 - "normalizar"
Cohesion: 0.24
Nodes (12): comando(), chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar(), sem_acentos(), slug() (+4 more)

### Community 5 - "shutil"
Cohesion: 0.35
Nodes (6): carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar()

### Community 6 - "Controlador"
Cohesion: 0.16
Nodes (6): Controlador, Etapa, Plano, normalizar_valor(), valores_equivalentes(), TestControle

### Community 7 - ".passo"
Cohesion: 0.11
Nodes (8): achar(), eventos(), _Executor, els_fn(), relevantes(), _Falha, _Interrompido, normalizar()

### Community 8 - "Celular"
Cohesion: 0.09
Nodes (6): _carregar(), Celular, el(), TestExecutorObjetivo, decidir(), escolher()

### Community 9 - "TestSonarFrequencia"
Cohesion: 0.06
Nodes (8): _carregar(), _Resposta, TestDescobrirRedeSemWifi, TestDiagnosticoRede, urlopen(), TestSonarFrequencia, testar(), TestTermometroSemResposta

### Community 10 - "Politica"
Cohesion: 0.23
Nodes (4): armar_cli(), painel_cli(), Politica, fim_do_dia()

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "canal.py"
Cohesion: 0.21
Nodes (10): _b64(), estado_valido(), _eventos_novos(), gravar(), _http(), ler(), parear(), sincronizar() (+2 more)

### Community 14 - "test_controle_ir.py"
Cohesion: 0.12
Nodes (10): agora(), capacidades(), _curto(), ErroAparelho, _faixa_txt(), hora_legivel(), _linhas_aparelho(), resumo_aparelho() (+2 more)

### Community 15 - "subprocess"
Cohesion: 0.13
Nodes (12): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+4 more)

### Community 16 - "Descoberta"
Cohesion: 0.06
Nodes (14): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), normalizar_marca() (+6 more)

### Community 17 - "sinais.py"
Cohesion: 0.13
Nodes (10): broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta(), limitar_duracao(), normalizar_pulsos(), pronto_para_pulsos(), pulsos_para_broadlink() (+2 more)

### Community 18 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.06
Nodes (34): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+26 more)

### Community 19 - "f"
Cohesion: 0.13
Nodes (21): agir(), app_em_foco(), bloqueado(), bloqueados(), _bloqueio_de_toque(), _executar(), escolher(), foco() (+13 more)

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 22 - "dump_ui"
Cohesion: 0.15
Nodes (13): atividade_no_topo(), casas_xadrez(), dentro(), dump_ui(), elementos(), foto(), _ferramentas_piloto(), tabuleiro_local() (+5 more)

### Community 23 - "subprocess"
Cohesion: 0.19
Nodes (9): filtro(), ler_recortes(), main(), reduzir(), validar_recorte(), gravar_memoria(), gravar(), progresso_txt() (+1 more)

### Community 24 - "objetivo.py"
Cohesion: 0.11
Nodes (16): assinatura(), busca(), concluido(), Executor, fim(), interruptor(), melhor(), norm() (+8 more)

### Community 25 - "e2e.cjs"
Cohesion: 0.13
Nodes (11): celular(), { chromium }, { execFileSync, spawn }, filhos, fs, nodeCrypto, os, PASTA (+3 more)

### Community 26 - "json"
Cohesion: 0.14
Nodes (20): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+12 more)

### Community 27 - "steps"
Cohesion: 0.11
Nodes (17): jobs, pacote, name, on, push, workflow_dispatch, runs-on, steps (+9 more)

### Community 28 - "re"
Cohesion: 0.18
Nodes (6): botao_fechar(), janela_nova(), reflexos(), _regex_bloqueados(), _regras(), vez_no_historico()

### Community 29 - "Servico"
Cohesion: 0.05
Nodes (12): ErroCapacidade, _hash(), _manifesto(), Registro, capacidade_cli(), Emissor, EmissorSimulado, classificar() (+4 more)

### Community 30 - "ar do escritório (ar-condicionado Carrier)"
Cohesion: 0.36
Nodes (8): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Cômodo: Escritório, Cômodo: Laboratório, Cômodo: Quarto, Índice de aparelhos (cômodo → aparelho → controle), Aparelhos salvos

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.11
Nodes (19): classificar(), ficha_upnp(), ip_do_wifi(), ler_inventarios(), main(), sondar(), ssdp(), tcp() (+11 more)

### Community 32 - "gree_variante.py"
Cohesion: 0.22
Nodes (10): checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main(), perfil() (+2 more)

### Community 34 - "exec_cli"
Cohesion: 0.19
Nodes (4): exec_cli(), Autorizacao, gerar_segredo(), totp()

### Community 35 - "schema.sql"
Cohesion: 0.12
Nodes (15): aparelhos, chamadas, config, convites, credenciais, desafios, estado, eventos (+7 more)

### Community 36 - "formatos.py"
Cohesion: 0.12
Nodes (19): adicionar_comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos(), ler_flipper() (+11 more)

### Community 37 - "resolver_grade"
Cohesion: 0.25
Nodes (5): _caixa(), _conflitos(), resolver_grade(), busca(), resolver_sudoku()

### Community 38 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+10 more)

### Community 40 - "sonar/principal.py"
Cohesion: 0.22
Nodes (9): analisar_sonar(), escolher_e_testar(), frequencia_lembrada(), gerar_tom(), lembrar(), main(), sugestao_sem_tom(), testar() (+1 more)

### Community 42 - "analisar.py"
Cohesion: 0.33
Nodes (5): agenda(), analisar(), extras(), percentil95(), Rodada

### Community 43 - "test_god_mode.py"
Cohesion: 0.11
Nodes (5): _Base, _ComServidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos

### Community 44 - "protocolos.py"
Cohesion: 0.16
Nodes (15): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+7 more)

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 47 - "main"
Cohesion: 0.17
Nodes (7): ampliar_catalogo(), iniciar(), main(), _pid_do_servico(), _soltar_inicio(), _travar_inicio(), Origens

### Community 48 - "ambiente_missao.py"
Cohesion: 0.18
Nodes (7): consultar_modelo(), contexto(), executar(), planejar(), RespostaDePlanoInvalida, armado(), permitido()

### Community 50 - ".controlar"
Cohesion: 0.20
Nodes (8): Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50), Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105), Perfil Gree Unknown (catálogo nº 102), descartado, Ligar/desligar diretos (energia_ligar 0x99, energia_desligar 0x98)

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.26
Nodes (15): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+7 more)

### Community 53 - "Canal"
Cohesion: 0.07
Nodes (6): Canal, _mascarar(), nome_da_chamada(), WebSocket, TestCanal, central()

### Community 54 - "ErroUso"
Cohesion: 0.18
Nodes (4): Aparelhos, ErroUso, Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper), Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas)

### Community 55 - "HANDOFF.md"
Cohesion: 0.20
Nodes (4): Comparação do planejador de missões no POCO, Contexto para o Claude Code, Skill graphify (query, explain, path, update), Licenças dos dados de controle

### Community 56 - "aplicar_regras"
Cohesion: 0.33
Nodes (4): achar_regra(), aplicar_regras(), els_fn(), regra_vale()

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 59 - ".anotar"
Cohesion: 0.10
Nodes (5): BluetoothDevice, ScanRecord, ScanResult, ParcelUuid, SparseArray

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 66 - "os"
Cohesion: 0.23
Nodes (6): fontes(), impressao(), checksum(), empacotar(), fontes(), verificar()

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 69 - "piloto.py"
Cohesion: 0.11
Nodes (9): ao_texto(), _confianca(), corpo_api(), fen(), ler_chave(), minha_cor(), prompt_quiz(), quem_mexeu() (+1 more)

### Community 70 - ".decidir"
Cohesion: 0.39
Nodes (3): chave_quiz(), norm(), quiz_da_tela()

### Community 71 - "Autonomia do planejador no POCO"
Cohesion: 0.40
Nodes (5): Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente

### Community 77 - "observador.py"
Cohesion: 0.21
Nodes (7): apps_usando(), _capacidades_rodando(), em_uso(), quadro(), recursos_do_comando(), _tarefas(), _tela()

### Community 78 - "ErroEmissor"
Cohesion: 0.39
Nodes (3): relatar_uso(), EmissorTermux, ErroEmissor

### Community 79 - "tela/principal.py"
Cohesion: 0.09
Nodes (19): _chave(), compactos(), _contar(), curto(), diferenca(), diferenca_curta(), escapar_input_text(), executar() (+11 more)

### Community 80 - "TestSegundoPlano"
Cohesion: 0.24
Nodes (3): TestSegundoPlano, abrir_console(), reiniciado()

### Community 86 - "modulo_embutido"
Cohesion: 0.42
Nodes (7): abrir(), configurar(), estudar(), ler_preferencias(), mostrar(), piloto_local(), Preferencias

### Community 88 - "cli.py"
Cohesion: 0.12
Nodes (16): arquivo_boot(), atualizar(), boot_ativado(), caminho_log(), _carimbo_catalogo(), catalogo_atual(), criar_atalhos(), iniciar_em_segundo_plano() (+8 more)

### Community 90 - "bluetooth/principal.py"
Cohesion: 0.12
Nodes (19): buscar(), buscar_app(), buscar_shell(), classificar(), compilar(), distancia(), guardar(), _ler_marca() (+11 more)

### Community 99 - "Estado atual da instalação (17/11/2026)"
Cohesion: 0.16
Nodes (16): Anúncio dos testes (v1.0.1), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026), Frases (+8 more)

### Community 100 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

### Community 102 - "cli.py"
Cohesion: 0.22
Nodes (12): _api(), carregar_config(), _cfg_caminho(), console(), url_quando_pronta(), estado_servidor(), parar_servico(), _porta_ativa() (+4 more)

### Community 103 - "_iniciar"
Cohesion: 0.18
Nodes (9): _aviso(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir(), mostrar_url(), _termux() (+1 more)

### Community 105 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

### Community 106 - "Bluetooth"
Cohesion: 0.15
Nodes (5): Runnable, Bluetooth, Runnable, ScanSettings, Builder

### Community 109 - "tv do quarto (TV Samsung)"
Cohesion: 0.27
Nodes (7): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung), Catálogo instalado: base + ampliado (9.380 perfis)

### Community 115 - "TestLeitorJava"
Cohesion: 0.05
Nodes (7): _carregar(), TestAppAuxiliar, TestBuscarNoCelular, TestClassificacao, TestCompilar, TestLeitorJava, TestTelaDicaDoCampo

### Community 116 - "_extrair_imagens"
Cohesion: 0.40
Nodes (3): _extrair_imagens(), varrer(), TestImagensAninhadas

### Community 119 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, deploy, dev, test:e2e

### Community 127 - "grade"
Cohesion: 0.11
Nodes (13): _abrir(), calma(), classe_janela(), em_anuncio(), fechar_anuncio(), tocar(), grade(), _injetar() (+5 more)

### Community 129 - "rish"
Cohesion: 0.10
Nodes (18): Ajudante, _ajudante(), _apagar(), captura(), estado_rapido(), aguardar(), foto_rapida(), _jar() (+10 more)

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 737 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **53 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TestPiloto` connect `TestPiloto` to `test_controle_ir.py`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.08208955223880597 - nodes in this community are weakly interconnected._
- **Why does `TestPainel` connect `TestPainel` to `test_controle_ir.py`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._
- **Should `test_controle_ir.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06531986531986532 - nodes in this community are weakly interconnected._
- **Why does `Servico` connect `Servico` to `test_controle_ir.py`, `TestPainel`, `novo_servico`, `normalizar`, `formatos.py`, `Controlador`, `_iniciar`, `ServidorMCP`, `tv do quarto (TV Samsung)`, `test_controle_ir.py`, `ErroEmissor`, `Descoberta`, `sinais.py`, `.controlar`, `ErroUso`, `cli.py`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._