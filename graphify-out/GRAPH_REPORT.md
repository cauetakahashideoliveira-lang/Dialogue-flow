# Graph Report - Dialogue-flow  (2026-11-21)

## Corpus Check
- 115 files · ~157,461 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 2287 nodes · 5182 edges · 131 communities (76 shown, 55 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 399 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `20a9acea`
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
- canal.py
- TestTelaPorArquivo
- servico.py
- subprocess
- Catalogo
- protocolos.py
- package.json
- TestImagemNoMcp
- Instalador (instalar.sh)
- Tela
- carregar_config
- subprocess
- re
- e2e.cjs
- json
- steps
- tela/principal.py
- Registro
- _iniciar
- descobrir_rede/principal.py
- gree_variante.py
- Execucao
- TestParidadeDoBloqueio
- schema.sql
- normalizar
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- Notificador
- TestOuvirBipe
- sonar/principal.py
- ServidorMCP
- Servico
- test_god_mode.py
- ._api
- webauthn.js
- session-start.sh
- construir_catalogo.py
- ambiente_missao.py
- Servico
- exec_cli
- autorizar.js
- app.js
- Canal
- TestTermometro
- HANDOFF.md
- termometro/principal.py
- TestPiloto
- os
- .anotar
- agora
- TestSono
- Sincronizador
- Passagem de bastão do Dialogue-flow
- Politica
- TestProtocolos
- criar_servidor
- local.cjs
- TestExecucao
- piloto.py
- _ajudante
- main
- Cerebros
- BluetoothAdapter
- Piloto
- Motor
- TestArmacao
- Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude
- TestResumoSemRepeticao
- agir
- TestSegundoPlano
- ErroEmissor
- android.bluetooth.le.ScanResult
- tv do quarto (TV Samsung)
- PlanoTest
- ar do escritório (ar-condicionado Carrier)
- abrirCanal
- .main
- cli.py
- pacote.py
- bluetooth/principal.py
- BluetoothDevice
- _Servidor
- resumo_para_instrucoes
- Bluetooth.java
- TestCapacidades
- novo_servico
- atualizar_conhecimento.sh
- Estado atual da instalação (17/11/2026)
- TestAtualizacaoRecompila
- TestVocabulario
- TestGodModeStmEPontuacao
- TestCanal
- TestEstadoCelularSemProc
- Contribuir com o Dialogue-flow
- Bluetooth
- Canal
- TestGreeVariante
- ar do quarto (ar-condicionado Gree GWH09KF)
- TestSono
- Tunel
- Autonomia do planejador no POCO
- TestObservador
- TestLeitorJava
- Pacote do celular dist/controle-ir.zip
- .startScan
- TestFerramentasDaMissao
- AttributionSource
- construir_app_bluetooth.sh script
- Process
- re
- TestTunel
- time

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

## Communities (131 total, 55 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.10
Nodes (26): aleatorio(), assinar(), assinarRequisicao(), BAIXO_RISCO, bloqueioNaBorda(), chaves(), config(), cookie() (+18 more)

### Community 1 - "Descoberta"
Cohesion: 0.13
Nodes (4): agora(), Descoberta, ErroDescoberta, termo_por_chave()

### Community 2 - "TestPainel"
Cohesion: 0.09
Nodes (16): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 2. Etapa 0 — armação diária local (1.0.23, implementada), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1) (+8 more)

### Community 4 - "Sinal"
Cohesion: 0.08
Nodes (30): adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos() (+22 more)

### Community 5 - "shutil"
Cohesion: 0.21
Nodes (6): carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar()

### Community 6 - "Controlador"
Cohesion: 0.14
Nodes (9): hora_legivel(), Controlador, Etapa, executar(), Plano, EmissorSimulado, normalizar_valor(), valores_equivalentes() (+1 more)

### Community 7 - ".passo"
Cohesion: 0.10
Nodes (7): eventos(), _Executor, _Falha, _Interrompido, _janela_curta(), janela_nova(), _linha_do_tempo()

### Community 8 - "Celular"
Cohesion: 0.08
Nodes (6): _carregar(), Celular, el(), TestExecutorObjetivo, decidir(), escolher()

### Community 9 - "TestSonarFrequencia"
Cohesion: 0.06
Nodes (8): _carregar(), _Resposta, TestDescobrirRedeSemWifi, TestDiagnosticoRede, urlopen(), TestSonarFrequencia, testar(), TestTermometroSemResposta

### Community 10 - "test_controle_ir.py"
Cohesion: 0.07
Nodes (5): resumo_instrucoes(), main(), preparar(), TestApkAtualizado, TestManifesto

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "canal.py"
Cohesion: 0.23
Nodes (8): _b64(), _eventos_novos(), gravar(), _http(), parear(), sincronizar(), verificar(), verificar_requisicao()

### Community 14 - "servico.py"
Cohesion: 0.24
Nodes (6): capacidades(), _curto(), _faixa_txt(), _linhas_aparelho(), resumo_aparelho(), resumo_para_instrucoes()

### Community 15 - "subprocess"
Cohesion: 0.18
Nodes (10): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+2 more)

### Community 16 - "Catalogo"
Cohesion: 0.12
Nodes (11): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), _unzip() (+3 more)

### Community 17 - "protocolos.py"
Cohesion: 0.17
Nodes (15): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+7 more)

### Community 18 - "package.json"
Cohesion: 0.10
Nodes (23): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+15 more)

### Community 19 - "TestImagemNoMcp"
Cohesion: 0.18
Nodes (4): _extrair_imagens(), varrer(), TestImagemNoMcp, TestImagensAninhadas

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 22 - "carregar_config"
Cohesion: 0.24
Nodes (12): _api(), carregar_config(), _cfg_caminho(), console(), url_quando_pronta(), estado_servidor(), parar_servico(), _porta_ativa() (+4 more)

### Community 23 - "subprocess"
Cohesion: 0.14
Nodes (6): filtro(), ler_recortes(), main(), reduzir(), validar_recorte(), nome_da_chamada()

### Community 24 - "re"
Cohesion: 0.12
Nodes (16): assinatura(), busca(), concluido(), Executor, fim(), interruptor(), melhor(), norm() (+8 more)

### Community 25 - "e2e.cjs"
Cohesion: 0.09
Nodes (15): flagPath, fs, os, path, celular(), { chromium }, { execFileSync, spawn }, filhos (+7 more)

### Community 26 - "json"
Cohesion: 0.21
Nodes (12): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+4 more)

### Community 27 - "steps"
Cohesion: 0.11
Nodes (17): jobs, pacote, name, on, push, workflow_dispatch, runs-on, steps (+9 more)

### Community 28 - "tela/principal.py"
Cohesion: 0.09
Nodes (18): _caixa(), _chave(), _conflitos(), _contar(), curto(), dentro(), diferenca(), diferenca_curta() (+10 more)

### Community 29 - "Registro"
Cohesion: 0.08
Nodes (20): ErroCapacidade, _hash(), _manifesto(), modulo_embutido(), Registro, capacidade_cli(), relatar_uso(), abrir() (+12 more)

### Community 30 - "_iniciar"
Cohesion: 0.36
Nodes (8): _aviso(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir(), mostrar_url(), _termux()

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.09
Nodes (23): agenda(), analisar(), extras(), percentil95(), Rodada, classificar(), ficha_upnp(), ip_do_wifi() (+15 more)

### Community 32 - "gree_variante.py"
Cohesion: 0.23
Nodes (10): checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main(), perfil() (+2 more)

### Community 35 - "schema.sql"
Cohesion: 0.12
Nodes (15): aparelhos, chamadas, config, convites, credenciais, desafios, estado, eventos (+7 more)

### Community 36 - "normalizar"
Cohesion: 0.14
Nodes (11): normalizar_marca(), categoria_canonica(), chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar(), sem_acentos() (+3 more)

### Community 37 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.11
Nodes (18): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+10 more)

### Community 40 - "sonar/principal.py"
Cohesion: 0.22
Nodes (9): analisar_sonar(), escolher_e_testar(), frequencia_lembrada(), gerar_tom(), lembrar(), main(), sugestao_sem_tom(), testar() (+1 more)

### Community 43 - "test_god_mode.py"
Cohesion: 0.11
Nodes (5): _Base, _ComServidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos

### Community 44 - "._api"
Cohesion: 0.22
Nodes (5): ao_texto(), _confianca(), corpo_api(), ler_chave(), prompt_quiz()

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 48 - "ambiente_missao.py"
Cohesion: 0.18
Nodes (7): consultar_modelo(), contexto(), executar(), planejar(), RespostaDePlanoInvalida, armado(), permitido()

### Community 49 - "Servico"
Cohesion: 0.15
Nodes (6): Aparelhos, ErroAparelho, ErroUso, slug(), Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper), Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas)

### Community 50 - "exec_cli"
Cohesion: 0.19
Nodes (4): exec_cli(), Autorizacao, gerar_segredo(), totp()

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.26
Nodes (15): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+7 more)

### Community 53 - "Canal"
Cohesion: 0.10
Nodes (3): Canal, _mascarar(), WebSocket

### Community 55 - "HANDOFF.md"
Cohesion: 0.20
Nodes (4): Comparação do planejador de missões no POCO, Contexto para o Claude Code, Skill graphify (query, explain, path, update), Licenças dos dados de controle

### Community 56 - "termometro/principal.py"
Cohesion: 0.32
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 58 - "os"
Cohesion: 0.09
Nodes (18): Ajudante, _apagar(), app_em_foco(), _bloqueio_de_toque(), captura(), estado_rapido(), foto_rapida(), _jpeg() (+10 more)

### Community 59 - ".anotar"
Cohesion: 0.13
Nodes (4): ScanRecord, ScanResult, ParcelUuid, SparseArray

### Community 60 - "agora"
Cohesion: 0.26
Nodes (23): acaoDono(), ackCelular(), agora(), autorizar(), consumirDesafio(), erro(), fresca(), guardarDesafio() (+15 more)

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 64 - "Politica"
Cohesion: 0.20
Nodes (6): armar_cli(), painel_cli(), Politica, estado_valido(), ler(), fim_do_dia()

### Community 66 - "criar_servidor"
Cohesion: 0.10
Nodes (16): julgar_depois(), criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json() (+8 more)

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 69 - "piloto.py"
Cohesion: 0.16
Nodes (8): chave_quiz(), fen(), gravar_memoria(), norm(), quem_mexeu(), quiz_da_tela(), tabuleiro_txt(), _texto_do_evento()

### Community 70 - "_ajudante"
Cohesion: 0.10
Nodes (23): _abrir(), _ajudante(), aplicar_regras(), els_fn(), calma(), classe_janela(), em_anuncio(), fechar_anuncio() (+15 more)

### Community 71 - "main"
Cohesion: 0.17
Nodes (7): ampliar_catalogo(), iniciar(), main(), _pid_do_servico(), _soltar_inicio(), _travar_inicio(), Origens

### Community 77 - "Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude"
Cohesion: 0.12
Nodes (16): Botão Stockfish para estudos, Capacidades plugáveis (ferramentas novas sem mexer no núcleo), Cobertura dos testes, Como funciona, Conectar ao ChatGPT ou ao Claude, Descoberta, Desenvolvimento, Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude (+8 more)

### Community 79 - "agir"
Cohesion: 0.13
Nodes (16): achar(), achar_regra(), agir(), casas_xadrez(), compactos(), dump_ui(), elementos(), escapar_input_text() (+8 more)

### Community 80 - "TestSegundoPlano"
Cohesion: 0.08
Nodes (7): catalogo_base(), TestCatalogo, TestRepositorio, TestSegundoPlano, abrir_console(), reiniciado(), TestStockfishLocal

### Community 81 - "ErroEmissor"
Cohesion: 0.20
Nodes (3): Emissor, EmissorTermux, ErroEmissor

### Community 83 - "tv do quarto (TV Samsung)"
Cohesion: 0.31
Nodes (7): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung), Catálogo instalado: base + ampliado (9.380 perfis)

### Community 85 - "ar do escritório (ar-condicionado Carrier)"
Cohesion: 0.36
Nodes (8): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Cômodo: Escritório, Cômodo: Laboratório, Cômodo: Quarto, Índice de aparelhos (cômodo → aparelho → controle), Aparelhos salvos

### Community 86 - "abrirCanal"
Cohesion: 0.28
Nodes (9): abrirCanal(), aparelhoDoToken(), canalDe(), empurrar(), estadoCanal(), estadoDe(), estadoParaCelular(), inicializar() (+1 more)

### Community 87 - ".main"
Cohesion: 0.19
Nodes (4): ScanSettings, Builder, Handler, Looper

### Community 88 - "cli.py"
Cohesion: 0.10
Nodes (17): arquivo_boot(), atualizar(), boot_ativado(), caminho_log(), _carimbo_catalogo(), catalogo_atual(), criar_atalhos(), iniciar_em_segundo_plano() (+9 more)

### Community 89 - "pacote.py"
Cohesion: 0.21
Nodes (7): _jar(), fontes(), impressao(), checksum(), empacotar(), fontes(), verificar()

### Community 90 - "bluetooth/principal.py"
Cohesion: 0.12
Nodes (19): buscar(), buscar_app(), buscar_shell(), classificar(), compilar(), distancia(), guardar(), _ler_marca() (+11 more)

### Community 99 - "Estado atual da instalação (17/11/2026)"
Cohesion: 0.16
Nodes (16): Anúncio dos testes (v1.0.1), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026), Frases (+8 more)

### Community 105 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

### Community 106 - "Bluetooth"
Cohesion: 0.15
Nodes (3): Runnable, Bluetooth, Runnable

### Community 109 - "ar do quarto (ar-condicionado Gree GWH09KF)"
Cohesion: 0.20
Nodes (8): Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50), Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105), Perfil Gree Unknown (catálogo nº 102), descartado, Ligar/desligar diretos (energia_ligar 0x99, energia_desligar 0x98)

### Community 113 - "Autonomia do planejador no POCO"
Cohesion: 0.40
Nodes (5): Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente

### Community 115 - "TestLeitorJava"
Cohesion: 0.05
Nodes (7): _carregar(), TestAppAuxiliar, TestBuscarNoCelular, TestClassificacao, TestCompilar, TestLeitorJava, TestTelaDicaDoCampo

### Community 127 - "re"
Cohesion: 0.15
Nodes (6): ssdp(), atividade_no_topo(), botao_fechar(), partida_contra_robo(), tabuleiro_curto(), vez_no_historico()

### Community 129 - "time"
Cohesion: 0.10
Nodes (22): bloqueado(), bloqueados(), executar(), _executar(), escolher(), main(), _modulo_piloto(), navegar() (+14 more)

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 742 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **55 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `Descoberta`, `Execucao`, `criar_servidor`, `Sinal`, `novo_servico`, `Controlador`, `ServidorMCP`, `test_controle_ir.py`, `ar do quarto (ar-condicionado Gree GWH09KF)`, `servico.py`, `Catalogo`, `Servico`, `ErroEmissor`, `cli.py`, `Registro`, `_iniciar`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.09788359788359788 - nodes in this community are weakly interconnected._
- **Why does `TestTelaPorArquivo` connect `TestTelaPorArquivo` to `test_controle_ir.py`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Should `Descoberta` be split into smaller, more focused modules?**
  _Cohesion score 0.12775842044134728 - nodes in this community are weakly interconnected._
- **Why does `TestClassificacao` connect `TestLeitorJava` to `test_controle_ir.py`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._