# Graph Report - Dialogue-flow  (2026-11-23)

## Corpus Check
- 129 files · ~185,976 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 2778 nodes · 6222 edges · 159 communities (94 shown, 65 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 457 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `908fc93c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- Descoberta
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- _privado
- Sinal
- ps4/controle.py
- Controlador
- agir
- TestExecutorObjetivo
- TestSonarFrequencia
- test_controle_ir.py
- steps
- painel.py
- TestTelaPorArquivo
- _ajudante
- json
- Catalogo
- protocolos.py
- test_objetivo.py
- ServidorMCP
- Instalador (instalar.sh)
- Tela
- Sinal
- os
- objetivo.py
- e2e.cjs
- f
- steps
- os
- ps4/principal.py
- Tunel
- descobrir_rede/principal.py
- TestPainel
- cli.py
- TestPrincipal
- schema.sql
- vocabulario.py
- Conexao
- sinais.py
- TestOuvirBipe
- sonar/principal.py
- TestCapacidades
- TestSegundoPlano
- test_god_mode.py
- Registro
- webauthn.js
- session-start.sh
- TestEstadoCelularSemProc
- eventos
- Politica
- TestExecucao
- autorizar.js
- app.js
- Canal
- TestTela
- HANDOFF.md
- modos/principal.py
- TestPiloto
- _ferramentas_piloto
- .anotar
- package.json
- TestSono
- _objetivo
- Passagem de bastão do Dialogue-flow
- TestTunel
- Servico
- CelularFalso
- local.cjs
- TestStockfishLocal
- test_objetivo.py
- test_controle_ir.py
- vigia.py
- Cerebros
- BluetoothAdapter
- Emissor
- estado_celular/principal.py
- Conexao
- TestRegioesWeb
- os
- Celular
- Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude
- TestVigia
- android.bluetooth.le.ScanResult
- Jogador
- piloto.py
- CLAUDE.md
- Problemas já resolvidos (para não repetir)
- .main
- observador.py
- _iniciar
- bluetooth/principal.py
- BluetoothDevice
- carregar_config
- execucao.py
- Bluetooth.java
- Motor
- TestParidadeDoBloqueio
- atualizar_conhecimento.sh
- gree_variante.py
- jogador.py
- TestPilotoVisao
- TestLigacaoNoServicoDaTela
- Piloto
- Contribuir com o Dialogue-flow
- Bluetooth
- estudo_xadrez.py
- godmode-tracker.js
- ._laco
- .controlar
- TestBuscarNoCelular
- resumo_para_instrucoes
- Aparelhos
- TestLeitorJava
- _Servidor
- .startScan
- novo_servico
- TestCanal
- AttributionSource
- construir_app_bluetooth.sh script
- analisar.py
- Process
- PS4: controle completo e jogador que aprende (capacidade `ps4`, 1.0.109+)
- Cerebro
- tela/principal.py
- main
- Sincronizador
- conexao.py
- tcl112.py
- .test_memoria_guarda_so_o_caminho_certo_sem_desvios
- TestTermometro
- Notificador
- broadlink_para_pulsos
- ._responder_por_visao
- .__init__
- PlanoTest
- scripts
- TestAppAuxiliar
- TestServidorMCP
- TestClassificacao
- _extrair_imagens
- TestObservador
- TestArmacao
- TestProtocolos
- TestFormatos
- TestAtualizacaoRecompila
- TestVocabulario
- catalogo_base
- TestTelaDicaDoCampo
- TestRepositorio

## God Nodes (most connected - your core abstractions)
1. `Servico` - 63 edges
2. `Celular` - 47 edges
3. `f()` - 47 edges
4. `main()` - 38 edges
5. `Tela` - 37 edges
6. `Descoberta` - 37 edges
7. `Sinal` - 37 edges
8. `TestTelaPorArquivo` - 36 edges
9. `Catalogo` - 35 edges
10. `TestExecutorObjetivo` - 32 edges

## Surprising Connections (you probably didn't know these)
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py
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

## Communities (159 total, 65 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.08
Nodes (59): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+51 more)

### Community 1 - "Descoberta"
Cohesion: 0.10
Nodes (5): agora(), normalizar_marca(), Descoberta, ErroDescoberta, categoria_canonica()

### Community 2 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.11
Nodes (18): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+10 more)

### Community 3 - "_privado"
Cohesion: 0.17
Nodes (8): analisar_web(), arvore(), andar(), ler_bounds(), regioes(), _privado(), regioes_visuais(), regioes_web()

### Community 4 - "Sinal"
Cohesion: 0.19
Nodes (11): adicionar_comando(), ErroFormato, _hex_le(), indice_comandos(), ler_flipper(), ler_sinal_texto(), sinais_pronto(), _sinal_smartir() (+3 more)

### Community 5 - "ps4/controle.py"
Cohesion: 0.16
Nodes (8): botao(), ErroComando, executar(), lado(), _limitar(), normalizar(), ponto(), texto_para_passos()

### Community 6 - "Controlador"
Cohesion: 0.15
Nodes (7): Controlador, Etapa, Plano, EmissorSimulado, normalizar_valor(), valores_equivalentes(), TestControle

### Community 7 - "agir"
Cohesion: 0.11
Nodes (13): achar(), achar_regra(), casas_xadrez(), compactos(), elementos(), escapar_input_text(), _Executor, els_fn() (+5 more)

### Community 9 - "TestSonarFrequencia"
Cohesion: 0.06
Nodes (8): _carregar(), _Resposta, TestDescobrirRedeSemWifi, TestDiagnosticoRede, urlopen(), TestSonarFrequencia, testar(), TestTermometroSemResposta

### Community 10 - "test_controle_ir.py"
Cohesion: 0.08
Nodes (5): TestApkAtualizado, TestManifesto, TestFerramentasDaMissao, TestResumoSemRepeticao, TestGodModeStmEPontuacao

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "painel.py"
Cohesion: 0.12
Nodes (11): nome_da_chamada(), _b64(), _eventos_novos(), gravar(), _http(), parear(), sincronizar(), verificar() (+3 more)

### Community 14 - "_ajudante"
Cohesion: 0.12
Nodes (18): _abrir(), _ajudante(), aplicar_regras(), els_fn(), calma(), em_anuncio(), fechar_anuncio(), tocar() (+10 more)

### Community 15 - "json"
Cohesion: 0.14
Nodes (20): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+12 more)

### Community 16 - "Catalogo"
Cohesion: 0.13
Nodes (10): Catalogo, estado_representativo(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), _unzip(), _zip() (+2 more)

### Community 17 - "protocolos.py"
Cohesion: 0.17
Nodes (15): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+7 more)

### Community 18 - "test_objetivo.py"
Cohesion: 0.12
Nodes (9): CelularWeb, estado_da_captura(), decidir(), TestObjetivoVisaoEGrafo, dec(), jul(), olh(), olhar() (+1 more)

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 22 - "Sinal"
Cohesion: 0.21
Nodes (5): escrever_flipper(), exportar(), sinal(), impressao_protocolo(), Sinal

### Community 23 - "os"
Cohesion: 0.13
Nodes (12): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+4 more)

### Community 24 - "objetivo.py"
Cohesion: 0.07
Nodes (28): area_cega(), assinatura(), busca(), concluido(), Executor, assinar(), cega_de(), fim() (+20 more)

### Community 25 - "e2e.cjs"
Cohesion: 0.13
Nodes (11): celular(), { chromium }, { execFileSync, spawn }, filhos, fs, nodeCrypto, os, PASTA (+3 more)

### Community 26 - "f"
Cohesion: 0.11
Nodes (23): agir(), app_em_foco(), bloqueado(), bloqueados(), _bloqueio_de_toque(), _eh_inicio(), _executar(), escolher() (+15 more)

### Community 27 - "steps"
Cohesion: 0.11
Nodes (17): jobs, pacote, name, on, push, workflow_dispatch, runs-on, steps (+9 more)

### Community 28 - "os"
Cohesion: 0.11
Nodes (21): Ajudante, _apagar(), captura(), curto(), diferenca_curta(), dump_ui(), estado_rapido(), foto_rapida() (+13 more)

### Community 29 - "ps4/principal.py"
Cohesion: 0.15
Nodes (23): cmd_comando(), fundo(), cmd_habilidade(), cmd_jogador(), codificar(), Estado, executar(), _frente() (+15 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.11
Nodes (20): classificar(), ficha_upnp(), ip_do_wifi(), ler_inventarios(), main(), sondar(), ssdp(), tcp() (+12 more)

### Community 32 - "TestPainel"
Cohesion: 0.06
Nodes (30): julgar_depois(), criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json() (+22 more)

### Community 33 - "cli.py"
Cohesion: 0.13
Nodes (15): arquivo_boot(), atualizar(), boot_ativado(), caminho_log(), _carimbo_catalogo(), catalogo_atual(), criar_atalhos(), inicio_automatico() (+7 more)

### Community 34 - "TestPrincipal"
Cohesion: 0.05
Nodes (8): ConexaoFalsa, Gravador, _mod(), TestComandos, TestCompatPyAV, TestConexaoLaco, TestJogador, TestPrincipal

### Community 35 - "schema.sql"
Cohesion: 0.12
Nodes (15): aparelhos, chamadas, config, convites, credenciais, desafios, estado, eventos (+7 more)

### Community 36 - "vocabulario.py"
Cohesion: 0.22
Nodes (14): comando(), importar_texto(), ler_smartir(), novo_perfil(), chaves_de_teste(), interpretar(), normalizar(), _por_regex() (+6 more)

### Community 37 - "Conexao"
Cohesion: 0.14
Nodes (4): compat_av(), _flag(), video_codec(), Conexao

### Community 38 - "sinais.py"
Cohesion: 0.20
Nodes (7): _classes(), ErroSinal, impressao_bruta(), limitar_duracao(), normalizar_pulsos(), pronto_para_pulsos(), _quadros()

### Community 40 - "sonar/principal.py"
Cohesion: 0.22
Nodes (9): analisar_sonar(), escolher_e_testar(), frequencia_lembrada(), gerar_tom(), lembrar(), main(), sugestao_sem_tom(), testar() (+1 more)

### Community 42 - "TestSegundoPlano"
Cohesion: 0.24
Nodes (3): TestSegundoPlano, abrir_console(), reiniciado()

### Community 43 - "test_god_mode.py"
Cohesion: 0.11
Nodes (5): _Base, _ComServidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos

### Community 44 - "Registro"
Cohesion: 0.10
Nodes (7): ErroCapacidade, _hash(), _manifesto(), Registro, capacidade_cli(), classificar(), Execucao

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 48 - "eventos"
Cohesion: 0.11
Nodes (7): classe_janela(), eventos(), historico(), _Interrompido, _janela_curta(), janela_nova(), _linha_do_tempo()

### Community 49 - "Politica"
Cohesion: 0.20
Nodes (6): armar_cli(), painel_cli(), Politica, estado_valido(), ler(), fim_do_dia()

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
Cohesion: 0.19
Nodes (6): Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente, Licenças dos dados de controle

### Community 56 - "modos/principal.py"
Cohesion: 0.09
Nodes (26): Android, aplicar_toque(), aplicar_volume(), atalho(), _avisar(), _chave(), _cond(), definir() (+18 more)

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 58 - "_ferramentas_piloto"
Cohesion: 0.32
Nodes (6): atividade_no_topo(), _ferramentas_piloto(), aguardar(), tabuleiro_local(), tela_chess(), partida_contra_robo()

### Community 59 - ".anotar"
Cohesion: 0.11
Nodes (5): BluetoothDevice, ScanRecord, ScanResult, ParcelUuid, SparseArray

### Community 60 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+10 more)

### Community 62 - "_objetivo"
Cohesion: 0.13
Nodes (14): _json_da_resposta(), _julgar(), julgar(), _modelo_do_nivel(), _objetivo(), abrir(), aplicar_regras(), bloqueado() (+6 more)

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 65 - "Servico"
Cohesion: 0.14
Nodes (4): Servico, Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105), Perfil Gree Unknown (catálogo nº 102), descartado, TestDescoberta

### Community 66 - "CelularFalso"
Cohesion: 0.17
Nodes (3): _carregar(), CelularFalso, TestModos

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 70 - "test_controle_ir.py"
Cohesion: 0.08
Nodes (7): capacidades(), hora_legivel(), resumo_aparelho(), resumo_instrucoes(), executar(), main(), preparar()

### Community 71 - "vigia.py"
Cohesion: 0.13
Nodes (9): _converter(), disparou(), norm(), numero(), satisfaz(), validar(), Vigias, laco() (+1 more)

### Community 74 - "Emissor"
Cohesion: 0.20
Nodes (3): Emissor, EmissorTermux, ErroEmissor

### Community 75 - "estado_celular/principal.py"
Cohesion: 0.36
Nodes (6): carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar()

### Community 76 - "Conexao"
Cohesion: 0.18
Nodes (5): carregar_memoria(), ao_texto(), Conexao, _confianca(), _texto_do_evento()

### Community 78 - "os"
Cohesion: 0.15
Nodes (10): filtro(), ler_recortes(), main(), reduzir(), validar_recorte(), gravar_memoria(), checksum(), empacotar() (+2 more)

### Community 80 - "Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude"
Cohesion: 0.12
Nodes (16): Botão Stockfish para estudos, Capacidades plugáveis (ferramentas novas sem mexer no núcleo), Cobertura dos testes, Como funciona, Conectar ao ChatGPT ou ao Claude, Descoberta, Desenvolvimento, Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude (+8 more)

### Community 81 - "TestVigia"
Cohesion: 0.21
Nodes (3): _carregar(), Relogio, TestVigia

### Community 84 - "piloto.py"
Cohesion: 0.11
Nodes (8): calcular(), ev(), corpo_api(), escolher_pela_conta(), fen(), minha_cor(), quem_mexeu(), tabuleiro_txt()

### Community 85 - "CLAUDE.md"
Cohesion: 0.27
Nodes (4): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, empacotar.sh script

### Community 86 - "Problemas já resolvidos (para não repetir)"
Cohesion: 0.16
Nodes (16): Anúncio dos testes (v1.0.1), Catálogo instalado: base + ampliado (9.380 perfis), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026) (+8 more)

### Community 87 - ".main"
Cohesion: 0.17
Nodes (4): ScanSettings, Builder, Handler, Looper

### Community 88 - "observador.py"
Cohesion: 0.10
Nodes (15): consultar_modelo(), contexto(), executar(), planejar(), modulo_embutido(), relatar_uso(), apps_usando(), _capacidades_rodando() (+7 more)

### Community 89 - "_iniciar"
Cohesion: 0.24
Nodes (10): avisar(), _aviso(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir(), mostrar_url() (+2 more)

### Community 90 - "bluetooth/principal.py"
Cohesion: 0.11
Nodes (19): buscar(), buscar_app(), buscar_shell(), classificar(), compilar(), distancia(), guardar(), _ler_marca() (+11 more)

### Community 92 - "carregar_config"
Cohesion: 0.19
Nodes (14): _api(), carregar_config(), _cfg_caminho(), console(), url_quando_pronta(), estado_servidor(), iniciar_em_segundo_plano(), parar_servico() (+6 more)

### Community 93 - "execucao.py"
Cohesion: 0.24
Nodes (3): exec_cli(), Autorizacao, gerar_segredo()

### Community 99 - "gree_variante.py"
Cohesion: 0.20
Nodes (11): exportar_jsonl(), checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main() (+3 more)

### Community 100 - "jogador.py"
Cohesion: 0.20
Nodes (7): centro_x(), fracao_cor(), mascara_cor(), medir(), perceber(), recompensa(), regiao()

### Community 105 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

### Community 106 - "Bluetooth"
Cohesion: 0.15
Nodes (4): Busca, Runnable, Bluetooth, Runnable

### Community 107 - "estudo_xadrez.py"
Cohesion: 0.40
Nodes (6): abrir(), configurar(), estudar(), ler_preferencias(), mostrar(), Preferencias

### Community 108 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

### Community 109 - "._laco"
Cohesion: 0.31
Nodes (3): chave_quiz(), norm(), quiz_da_tela()

### Community 110 - ".controlar"
Cohesion: 0.10
Nodes (23): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50) (+15 more)

### Community 113 - "resumo_para_instrucoes"
Cohesion: 0.12
Nodes (6): _curto(), _faixa_txt(), _linhas_aparelho(), resumo_compacto(), resumo_para_instrucoes(), TestResumoInstrucoes

### Community 114 - "Aparelhos"
Cohesion: 0.13
Nodes (4): Aparelhos, ErroAparelho, ErroUso, 2. Etapa 0 — armação diária local (1.0.23, implementada)

### Community 115 - "TestLeitorJava"
Cohesion: 0.18
Nodes (3): _carregar(), TestCompilar, TestLeitorJava

### Community 125 - "analisar.py"
Cohesion: 0.31
Nodes (6): agenda(), analisar(), extras(), percentil95(), Comparação do planejador de missões no POCO, Rodada

### Community 127 - "PS4: controle completo e jogador que aprende (capacidade `ps4`, 1.0.109+)"
Cohesion: 0.29
Nodes (6): Instalação no Termux (uma vez, com o sistema armado), Jogador que aprende (`acao=jogador`), Limites medidos/esperados, Preparo (uma vez), PS4: controle completo e jogador que aprende (capacidade `ps4`, 1.0.109+), Uso

### Community 129 - "tela/principal.py"
Cohesion: 0.07
Nodes (24): botao_fechar(), _caixa(), _carregar_objetivo(), _chave(), _conflitos(), _contar(), dentro(), diferenca() (+16 more)

### Community 133 - "main"
Cohesion: 0.17
Nodes (7): ampliar_catalogo(), iniciar(), main(), _pid_do_servico(), _soltar_inicio(), _travar_inicio(), Origens

### Community 135 - "conexao.py"
Cohesion: 0.28
Nodes (3): _ligar_log(), _Memoria, ultimas_linhas()

### Community 136 - "tcl112.py"
Cohesion: 0.11
Nodes (18): RespostaDePlanoInvalida, Ar condicionado quarto 2 — Brastemp Clean (protocolo TCL112), Como foi identificado (22/11), Formato (TCL112, 2 quadros de 14 bytes, LSB primeiro, 38 kHz), Frases, Parâmetros do perfil, Regenerar o perfil no celular, Ressalvas (+10 more)

### Community 141 - "broadlink_para_pulsos"
Cohesion: 0.14
Nodes (3): broadlink_para_pulsos(), TestGreeVariante, TestTcl112

### Community 142 - "._responder_por_visao"
Cohesion: 0.22
Nodes (3): caixa_da_pergunta(), ler_chave(), p()

### Community 145 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, deploy, dev, test:e2e

### Community 149 - "_extrair_imagens"
Cohesion: 0.40
Nodes (3): _extrair_imagens(), varrer(), TestImagensAninhadas

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 911 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **65 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `TestPainel`, `cli.py`, `Descoberta`, `vocabulario.py`, `test_controle_ir.py`, `Controlador`, `sinais.py`, `Emissor`, `Registro`, `.controlar`, `Catalogo`, `Aparelhos`, `ServidorMCP`, `Sinal`, `novo_servico`, `_iniciar`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.08208955223880597 - nodes in this community are weakly interconnected._
- **Why does `Catalogo` connect `Catalogo` to `Descoberta`, `Servico`, `main`, `sinais.py`, `test_controle_ir.py`, `Sinal`, `Problemas já resolvidos (para não repetir)`, `_iniciar`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Should `Descoberta` be split into smaller, more focused modules?**
  _Cohesion score 0.10040816326530612 - nodes in this community are weakly interconnected._
- **Why does `f()` connect `f` to `tela/principal.py`, `Descoberta`, `tcl112.py`, `TestSonarFrequencia`, `.test_memoria_guarda_so_o_caminho_certo_sem_desvios`, `json`, `Catalogo`, `os`, `objetivo.py`, `ps4/principal.py`, `descobrir_rede/principal.py`, `cli.py`, `sonar/principal.py`, `Registro`, `modos/principal.py`, `_objetivo`, `CelularFalso`, `vigia.py`, `Conexao`, `os`, `Jogador`, `bluetooth/principal.py`, `Aparelhos`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._