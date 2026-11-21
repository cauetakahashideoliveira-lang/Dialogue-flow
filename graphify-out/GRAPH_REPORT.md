# Graph Report - Dialogue-flow  (2026-11-21)

## Corpus Check
- 115 files · ~155,430 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 2272 nodes · 5131 edges · 136 communities (83 shown, 53 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 390 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `9f9165ab`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- test_controle_ir.py
- TestPainel
- Conexao
- normalizar
- EmissorSimulado
- Controlador
- .passo
- Celular
- TestSonarFrequencia
- Politica
- steps
- canal.py
- TestTelaPorArquivo
- test_controle_ir.py
- os
- Descoberta
- ErroSinal
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- f
- Instalador (instalar.sh)
- Tela
- elementos
- subprocess
- re
- e2e.cjs
- json
- steps
- time
- Registro
- time
- descobrir_rede/principal.py
- gree_variante.py
- Catalogo
- exec_cli
- schema.sql
- formatos.py
- Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude
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
- Servico
- HANDOFF.md
- Aparelhos
- TestPiloto
- TestGreeVariante
- .anotar
- Execucao
- TestSono
- agora
- Passagem de bastão do Dialogue-flow
- servidor.py
- criar_servidor
- os
- local.cjs
- TestEstadoCelularSemProc
- ._api
- piloto.py
- Autonomia do planejador no POCO
- Cerebros
- BluetoothAdapter
- Piloto
- Motor
- TestArmacao
- observador.py
- termometro/principal.py
- tela/principal.py
- TestSegundoPlano
- fechar_anuncio
- android.bluetooth.le.ScanResult
- Sinal
- PlanoTest
- Executor
- modulo_embutido
- .main
- caminho_log
- TestObservador
- bluetooth/principal.py
- BluetoothDevice
- _Servidor
- resumo_para_instrucoes
- Bluetooth.java
- TestCapacidades
- novo_servico
- atualizar_conhecimento.sh
- Estado atual da instalação (17/11/2026)
- shutil
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
- abrirCanal
- .decidir
- AttributionSource
- construir_app_bluetooth.sh script
- Canal
- Process
- aplicar_regras
- TestTunel
- Ajudante
- Notificador
- inicio_automatico
- atualizar

## God Nodes (most connected - your core abstractions)
1. `Servico` - 62 edges
2. `main()` - 38 edges
3. `Tela` - 37 edges
4. `Descoberta` - 37 edges
5. `Sinal` - 37 edges
6. `TestTelaPorArquivo` - 36 edges
7. `Catalogo` - 35 edges
8. `Celular` - 33 edges
9. `f()` - 32 edges
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
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `ampliar_catalogo()`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/cli.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (136 total, 53 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.10
Nodes (26): aleatorio(), assinar(), assinarRequisicao(), BAIXO_RISCO, bloqueioNaBorda(), chaves(), config(), cookie() (+18 more)

### Community 1 - "test_controle_ir.py"
Cohesion: 0.07
Nodes (7): main(), preparar(), TestApkAtualizado, TestManifesto, TestFerramentasDaMissao, TestResumoSemRepeticao, TestGodModeStmEPontuacao

### Community 2 - "TestPainel"
Cohesion: 0.09
Nodes (15): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono (+7 more)

### Community 4 - "normalizar"
Cohesion: 0.17
Nodes (13): normalizar_marca(), categoria_canonica(), chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar(), sem_acentos() (+5 more)

### Community 6 - "Controlador"
Cohesion: 0.16
Nodes (6): Controlador, Etapa, Plano, normalizar_valor(), valores_equivalentes(), TestControle

### Community 7 - ".passo"
Cohesion: 0.10
Nodes (10): achar(), compactos(), eventos(), _Executor, els_fn(), relevantes(), _Falha, _Interrompido (+2 more)

### Community 8 - "Celular"
Cohesion: 0.10
Nodes (6): _carregar(), Celular, el(), TestExecutorObjetivo, decidir(), escolher()

### Community 9 - "TestSonarFrequencia"
Cohesion: 0.06
Nodes (8): _carregar(), _Resposta, TestDescobrirRedeSemWifi, TestDiagnosticoRede, urlopen(), TestSonarFrequencia, testar(), TestTermometroSemResposta

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "canal.py"
Cohesion: 0.20
Nodes (11): painel_cli(), _b64(), estado_valido(), _eventos_novos(), gravar(), _http(), ler(), parear() (+3 more)

### Community 14 - "test_controle_ir.py"
Cohesion: 0.11
Nodes (11): capacidades(), _curto(), ErroAparelho, _faixa_txt(), hora_legivel(), _linhas_aparelho(), resumo_aparelho(), executar() (+3 more)

### Community 15 - "os"
Cohesion: 0.13
Nodes (12): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+4 more)

### Community 16 - "Descoberta"
Cohesion: 0.14
Nodes (3): agora(), Descoberta, ErroDescoberta

### Community 17 - "ErroSinal"
Cohesion: 0.15
Nodes (7): broadlink_para_pulsos(), ErroSinal, limitar_duracao(), normalizar_pulsos(), pronto_para_pulsos(), pulsos_para_broadlink(), TestFormatos

### Community 18 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.11
Nodes (18): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+10 more)

### Community 19 - "f"
Cohesion: 0.11
Nodes (23): app_em_foco(), bloqueado(), bloqueados(), executar(), _executar(), escolher(), foco(), main() (+15 more)

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 22 - "elementos"
Cohesion: 0.15
Nodes (11): atividade_no_topo(), casas_xadrez(), foto(), _ferramentas_piloto(), aguardar(), tabuleiro_local(), tela_chess(), tocar() (+3 more)

### Community 23 - "subprocess"
Cohesion: 0.27
Nodes (5): filtro(), ler_recortes(), main(), reduzir(), validar_recorte()

### Community 24 - "re"
Cohesion: 0.18
Nodes (12): assinatura(), busca(), concluido(), interruptor(), melhor(), norm(), proibido(), ranquear() (+4 more)

### Community 25 - "e2e.cjs"
Cohesion: 0.09
Nodes (15): flagPath, fs, os, path, celular(), { chromium }, { execFileSync, spawn }, filhos (+7 more)

### Community 26 - "json"
Cohesion: 0.16
Nodes (15): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+7 more)

### Community 27 - "steps"
Cohesion: 0.11
Nodes (17): jobs, pacote, name, on, push, workflow_dispatch, runs-on, steps (+9 more)

### Community 28 - "time"
Cohesion: 0.12
Nodes (19): agir(), _ajudante(), _apagar(), _bloqueio_de_toque(), captura(), dump_ui(), escapar_input_text(), estado_rapido() (+11 more)

### Community 29 - "Registro"
Cohesion: 0.20
Nodes (5): ErroCapacidade, _hash(), _manifesto(), Registro, capacidade_cli()

### Community 30 - "time"
Cohesion: 0.40
Nodes (8): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi()

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.16
Nodes (11): classificar(), ficha_upnp(), ip_do_wifi(), ler_inventarios(), main(), sondar(), ssdp(), tcp() (+3 more)

### Community 32 - "gree_variante.py"
Cohesion: 0.21
Nodes (10): checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main(), perfil() (+2 more)

### Community 33 - "Catalogo"
Cohesion: 0.13
Nodes (8): Catalogo, estado_representativo(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), progresso_txt(), reconstruir_catalogo()

### Community 34 - "exec_cli"
Cohesion: 0.23
Nodes (3): exec_cli(), Autorizacao, gerar_segredo()

### Community 35 - "schema.sql"
Cohesion: 0.12
Nodes (15): aparelhos, chamadas, config, convites, credenciais, desafios, estado, eventos (+7 more)

### Community 36 - "formatos.py"
Cohesion: 0.17
Nodes (17): adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos() (+9 more)

### Community 37 - "Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude"
Cohesion: 0.12
Nodes (16): Botão Stockfish para estudos, Capacidades plugáveis (ferramentas novas sem mexer no núcleo), Cobertura dos testes, Como funciona, Conectar ao ChatGPT ou ao Claude, Descoberta, Desenvolvimento, Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude (+8 more)

### Community 38 - "package.json"
Cohesion: 0.10
Nodes (23): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+15 more)

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
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 47 - "main"
Cohesion: 0.21
Nodes (6): ampliar_catalogo(), iniciar(), main(), _soltar_inicio(), _travar_inicio(), Origens

### Community 48 - "ambiente_missao.py"
Cohesion: 0.18
Nodes (7): consultar_modelo(), contexto(), executar(), planejar(), RespostaDePlanoInvalida, armado(), permitido()

### Community 50 - ".controlar"
Cohesion: 0.15
Nodes (16): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50) (+8 more)

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.26
Nodes (15): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+7 more)

### Community 53 - "Canal"
Cohesion: 0.07
Nodes (6): Canal, _mascarar(), nome_da_chamada(), WebSocket, TestCanal, central()

### Community 54 - "Servico"
Cohesion: 0.14
Nodes (4): ErroUso, Servico, Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas), 2. Etapa 0 — armação diária local (1.0.23, implementada)

### Community 55 - "HANDOFF.md"
Cohesion: 0.20
Nodes (4): Comparação do planejador de missões no POCO, Contexto para o Claude Code, Skill graphify (query, explain, path, update), Licenças dos dados de controle

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 59 - ".anotar"
Cohesion: 0.13
Nodes (4): ScanRecord, ScanResult, ParcelUuid, SparseArray

### Community 61 - "TestSono"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 62 - "agora"
Cohesion: 0.26
Nodes (23): acaoDono(), ackCelular(), agora(), autorizar(), consumirDesafio(), erro(), fresca(), guardarDesafio() (+15 more)

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 65 - "criar_servidor"
Cohesion: 0.10
Nodes (16): julgar_depois(), criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json() (+8 more)

### Community 66 - "os"
Cohesion: 0.16
Nodes (9): compilar(), gravar_memoria(), _jar(), fontes(), impressao(), checksum(), empacotar(), fontes() (+1 more)

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 69 - "._api"
Cohesion: 0.22
Nodes (5): ao_texto(), _confianca(), corpo_api(), ler_chave(), prompt_quiz()

### Community 70 - "piloto.py"
Cohesion: 0.17
Nodes (5): fen(), minha_cor(), quem_mexeu(), tabuleiro_txt(), _texto_do_evento()

### Community 71 - "Autonomia do planejador no POCO"
Cohesion: 0.40
Nodes (5): Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente

### Community 77 - "observador.py"
Cohesion: 0.10
Nodes (11): relatar_uso(), Emissor, EmissorTermux, ErroEmissor, apps_usando(), _capacidades_rodando(), em_uso(), quadro() (+3 more)

### Community 78 - "termometro/principal.py"
Cohesion: 0.29
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 79 - "tela/principal.py"
Cohesion: 0.07
Nodes (29): _caixa(), calma(), _chave(), _conflitos(), _contar(), curto(), dentro(), diferenca() (+21 more)

### Community 80 - "TestSegundoPlano"
Cohesion: 0.08
Nodes (7): catalogo_base(), TestCatalogo, TestRepositorio, TestSegundoPlano, abrir_console(), reiniciado(), TestStockfishLocal

### Community 81 - "fechar_anuncio"
Cohesion: 0.13
Nodes (12): _abrir(), botao_fechar(), classe_janela(), em_anuncio(), fechar_anuncio(), _injetar(), objetivo(), abrir() (+4 more)

### Community 83 - "Sinal"
Cohesion: 0.24
Nodes (3): sinal(), _sinal_smartir(), Sinal

### Community 85 - "Executor"
Cohesion: 0.22
Nodes (4): Executor, fim(), sistema(), textos_da_tela()

### Community 86 - "modulo_embutido"
Cohesion: 0.29
Nodes (8): modulo_embutido(), abrir(), configurar(), estudar(), ler_preferencias(), mostrar(), piloto_local(), Preferencias

### Community 87 - ".main"
Cohesion: 0.17
Nodes (4): ScanSettings, Builder, Handler, Looper

### Community 88 - "caminho_log"
Cohesion: 0.20
Nodes (6): caminho_log(), iniciar_em_segundo_plano(), mostrar_log(), _redirecionar_para_log(), _registrar(), _seguir_log()

### Community 90 - "bluetooth/principal.py"
Cohesion: 0.12
Nodes (18): buscar(), buscar_app(), buscar_shell(), classificar(), distancia(), guardar(), _ler_marca(), ler_pareados_dumpsys() (+10 more)

### Community 99 - "Estado atual da instalação (17/11/2026)"
Cohesion: 0.16
Nodes (16): Anúncio dos testes (v1.0.1), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026), Frases (+8 more)

### Community 100 - "shutil"
Cohesion: 0.24
Nodes (6): carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar()

### Community 102 - "cli.py"
Cohesion: 0.18
Nodes (15): _api(), _carimbo_catalogo(), carregar_config(), catalogo_atual(), _cfg_caminho(), console(), url_quando_pronta(), estado_servidor() (+7 more)

### Community 103 - "_iniciar"
Cohesion: 0.29
Nodes (9): armar_cli(), _aviso(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir(), mostrar_url() (+1 more)

### Community 105 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

### Community 106 - "Bluetooth"
Cohesion: 0.14
Nodes (4): Busca, Runnable, Bluetooth, Runnable

### Community 109 - "tv do quarto (TV Samsung)"
Cohesion: 0.27
Nodes (7): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung), Catálogo instalado: base + ampliado (9.380 perfis)

### Community 115 - "TestLeitorJava"
Cohesion: 0.05
Nodes (7): _carregar(), TestAppAuxiliar, TestBuscarNoCelular, TestClassificacao, TestCompilar, TestLeitorJava, TestTelaDicaDoCampo

### Community 116 - "_extrair_imagens"
Cohesion: 0.40
Nodes (3): _extrair_imagens(), varrer(), TestImagensAninhadas

### Community 118 - "abrirCanal"
Cohesion: 0.28
Nodes (9): abrirCanal(), aparelhoDoToken(), canalDe(), empurrar(), estadoCanal(), estadoDe(), estadoParaCelular(), inicializar() (+1 more)

### Community 119 - ".decidir"
Cohesion: 0.39
Nodes (3): chave_quiz(), norm(), quiz_da_tela()

### Community 127 - "aplicar_regras"
Cohesion: 0.33
Nodes (4): achar_regra(), aplicar_regras(), els_fn(), regra_vale()

### Community 134 - "inicio_automatico"
Cohesion: 0.33
Nodes (6): arquivo_boot(), boot_ativado(), criar_atalhos(), inicio_automatico(), pasta_atalhos(), script_boot()

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 735 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **53 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `test_controle_ir.py`, `normalizar`, `EmissorSimulado`, `Controlador`, `test_controle_ir.py`, `Descoberta`, `ErroSinal`, `Registro`, `Catalogo`, `formatos.py`, `ServidorMCP`, `Aparelhos`, `Execucao`, `servidor.py`, `criar_servidor`, `observador.py`, `Sinal`, `cli.py`, `_iniciar`, `TestTermometro`, `tv do quarto (TV Samsung)`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.09788359788359788 - nodes in this community are weakly interconnected._
- **Why does `TestPiloto` connect `TestPiloto` to `test_controle_ir.py`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Should `test_controle_ir.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06845513413506013 - nodes in this community are weakly interconnected._
- **Why does `ServidorMCP` connect `ServidorMCP` to `servidor.py`, `criar_servidor`, `TestCapacidades`, `TestArmacao`, `PlanoTest`, `resumo_para_instrucoes`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._