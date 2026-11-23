# Graph Report - Dialogue-flow  (2026-11-23)

## Corpus Check
- 129 files · ~184,201 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 2761 nodes · 6194 edges · 147 communities (91 shown, 56 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 456 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `0a6d21eb`
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
- _extrair_imagens
- Instalador (instalar.sh)
- Tela
- Execucao
- os
- objetivo.py
- e2e.cjs
- time
- steps
- os
- ps4/principal.py
- Tunel
- descobrir_rede/principal.py
- TestPainel
- cli.py
- TestPrincipal
- schema.sql
- normalizar
- Conexao
- broadlink_para_pulsos
- TestOuvirBipe
- sonar/principal.py
- ServidorMCP
- TestSegundoPlano
- test_god_mode.py
- Registro
- webauthn.js
- session-start.sh
- test_consistencia.py
- diagnostico_rede/principal.py
- Politica
- TestExecucao
- autorizar.js
- app.js
- Canal
- TestTela
- HANDOFF.md
- modos/principal.py
- TestPiloto
- agir
- .anotar
- Aparelhos
- TestSono
- _objetivo
- Passagem de bastão do Dialogue-flow
- TestTunel
- Servico
- CelularFalso
- local.cjs
- EmissorSimulado
- test_objetivo.py
- test_controle_ir.py
- vigia.py
- Cerebros
- BluetoothAdapter
- Emissor
- criar_servidor
- Conexao
- TestRegioesWeb
- canal.py
- Celular
- Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude
- TestVigia
- android.bluetooth.le.ScanResult
- TestProtocolos
- piloto.py
- TestObservador
- Problemas já resolvidos (para não repetir)
- .main
- observador.py
- _iniciar
- bluetooth/principal.py
- BluetoothDevice
- modulo_embutido
- shutil
- Bluetooth.java
- Motor
- TestParidadeDoBloqueio
- atualizar_conhecimento.sh
- gree_variante.py
- calcular
- TestPilotoVisao
- TestLigacaoNoServicoDaTela
- canal.py
- Contribuir com o Dialogue-flow
- Bluetooth
- Piloto
- WebSocket
- ._laco
- .controlar
- TestServidorMCP
- TestResumoInstrucoes
- TestCapacidades
- TestLeitorJava
- _Servidor
- .startScan
- Ar condicionado quarto 2 — Brastemp Clean (protocolo TCL112)
- TestCanal
- AttributionSource
- construir_app_bluetooth.sh script
- ErroSinal
- Process
- PS4: controle completo e jogador que aprende (capacidade `ps4`, 1.0.109+)
- TestPrincipal
- tela/principal.py
- TestVocabulario
- Jogador
- termometro/principal.py
- tcl112.py
- .test_memoria_guarda_so_o_caminho_certo_sem_desvios
- tv do quarto (TV Samsung)
- analisar.py
- Cerebro
- PlanoTest
- jogador.py
- atualizar
- .__init__
- TestArmacao

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
- `variante()` --implements--> `Variante Gree a partir da captura real (troca só os bits)`  [INFERRED]
  ferramentas/gree_variante.py → docs/aparelhos/quarto/ar-do-quarto.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (147 total, 56 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.05
Nodes (82): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+74 more)

### Community 1 - "Descoberta"
Cohesion: 0.13
Nodes (3): agora(), Descoberta, ErroDescoberta

### Community 2 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.11
Nodes (18): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+10 more)

### Community 3 - "_privado"
Cohesion: 0.17
Nodes (8): analisar_web(), arvore(), andar(), ler_bounds(), regioes(), _privado(), regioes_visuais(), regioes_web()

### Community 4 - "Sinal"
Cohesion: 0.10
Nodes (22): adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos() (+14 more)

### Community 5 - "ps4/controle.py"
Cohesion: 0.20
Nodes (8): botao(), ErroComando, executar(), lado(), _limitar(), normalizar(), ponto(), texto_para_passos()

### Community 6 - "Controlador"
Cohesion: 0.17
Nodes (5): Controlador, Etapa, Plano, normalizar_valor(), TestControle

### Community 7 - "agir"
Cohesion: 0.10
Nodes (7): eventos(), _Executor, _Falha, _Interrompido, _janela_curta(), janela_nova(), _linha_do_tempo()

### Community 9 - "TestSonarFrequencia"
Cohesion: 0.06
Nodes (8): _carregar(), _Resposta, TestDescobrirRedeSemWifi, TestDiagnosticoRede, urlopen(), TestSonarFrequencia, testar(), TestTermometroSemResposta

### Community 10 - "test_controle_ir.py"
Cohesion: 0.08
Nodes (5): main(), preparar(), TestApkAtualizado, TestManifesto, TestGodModeStmEPontuacao

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "painel.py"
Cohesion: 0.12
Nodes (12): painel_cli(), _b64(), estado_valido(), _eventos_novos(), gravar(), _http(), ler(), parear() (+4 more)

### Community 14 - "_ajudante"
Cohesion: 0.09
Nodes (24): _ajudante(), aplicar_regras(), els_fn(), calma(), em_anuncio(), fechar_anuncio(), aguardar(), tocar() (+16 more)

### Community 15 - "json"
Cohesion: 0.23
Nodes (12): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+4 more)

### Community 16 - "Catalogo"
Cohesion: 0.12
Nodes (9): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), _unzip() (+1 more)

### Community 17 - "protocolos.py"
Cohesion: 0.15
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 18 - "test_objetivo.py"
Cohesion: 0.12
Nodes (8): CelularWeb, decidir(), TestObjetivoVisaoEGrafo, dec(), jul(), olh(), olhar(), web()

### Community 19 - "_extrair_imagens"
Cohesion: 0.40
Nodes (3): _extrair_imagens(), varrer(), TestImagensAninhadas

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 23 - "os"
Cohesion: 0.13
Nodes (12): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+4 more)

### Community 24 - "objetivo.py"
Cohesion: 0.07
Nodes (28): area_cega(), assinatura(), busca(), concluido(), Executor, assinar(), cega_de(), fim() (+20 more)

### Community 25 - "e2e.cjs"
Cohesion: 0.09
Nodes (15): flagPath, fs, os, path, celular(), { chromium }, { execFileSync, spawn }, filhos (+7 more)

### Community 26 - "time"
Cohesion: 0.09
Nodes (25): guardar(), filtro(), ler_recortes(), main(), reduzir(), validar_recorte(), lembrar(), app_em_foco() (+17 more)

### Community 27 - "steps"
Cohesion: 0.11
Nodes (17): jobs, pacote, name, on, push, workflow_dispatch, runs-on, steps (+9 more)

### Community 28 - "os"
Cohesion: 0.12
Nodes (17): gravar_memoria(), _abrir(), Ajudante, _apagar(), captura(), estado_rapido(), foto_rapida(), _jar() (+9 more)

### Community 29 - "ps4/principal.py"
Cohesion: 0.15
Nodes (22): cmd_comando(), fundo(), cmd_habilidade(), cmd_jogador(), codificar(), Estado, executar(), _gravar() (+14 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.16
Nodes (11): classificar(), ficha_upnp(), ip_do_wifi(), ler_inventarios(), main(), sondar(), ssdp(), tcp() (+3 more)

### Community 32 - "TestPainel"
Cohesion: 0.09
Nodes (15): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono (+7 more)

### Community 33 - "cli.py"
Cohesion: 0.08
Nodes (35): ampliar_catalogo(), _api(), arquivo_boot(), boot_ativado(), caminho_log(), _carimbo_catalogo(), carregar_config(), catalogo_atual() (+27 more)

### Community 34 - "TestPrincipal"
Cohesion: 0.07
Nodes (7): ConexaoFalsa, Gravador, _mod(), TestComandos, TestCompatPyAV, TestConexaoLaco, TestJogador

### Community 35 - "schema.sql"
Cohesion: 0.12
Nodes (15): aparelhos, chamadas, config, convites, credenciais, desafios, estado, eventos (+7 more)

### Community 36 - "normalizar"
Cohesion: 0.14
Nodes (14): normalizar_marca(), categoria_canonica(), chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar(), sem_acentos() (+6 more)

### Community 37 - "Conexao"
Cohesion: 0.10
Nodes (7): compat_av(), _flag(), video_codec(), Conexao, _ligar_log(), _Memoria, ultimas_linhas()

### Community 38 - "broadlink_para_pulsos"
Cohesion: 0.10
Nodes (5): broadlink_para_pulsos(), pulsos_para_broadlink(), TestFormatos, TestGreeVariante, TestTcl112

### Community 40 - "sonar/principal.py"
Cohesion: 0.23
Nodes (8): analisar_sonar(), escolher_e_testar(), frequencia_lembrada(), gerar_tom(), main(), sugestao_sem_tom(), testar(), volume_musica()

### Community 42 - "TestSegundoPlano"
Cohesion: 0.08
Nodes (7): catalogo_base(), TestCatalogo, TestRepositorio, TestSegundoPlano, abrir_console(), reiniciado(), TestStockfishLocal

### Community 43 - "test_god_mode.py"
Cohesion: 0.11
Nodes (5): _Base, _ComServidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos

### Community 44 - "Registro"
Cohesion: 0.20
Nodes (5): ErroCapacidade, _hash(), _manifesto(), Registro, capacidade_cli()

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 47 - "test_consistencia.py"
Cohesion: 0.11
Nodes (5): _estado_celular(), TestAtualizacaoRecompila, TestEstadoCelularSemProc, TestFerramentasDaMissao, TestResumoSemRepeticao

### Community 48 - "diagnostico_rede/principal.py"
Cohesion: 0.40
Nodes (8): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi()

### Community 49 - "Politica"
Cohesion: 0.14
Nodes (6): armar_cli(), exec_cli(), Autorizacao, gerar_segredo(), Politica, fim_do_dia()

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.26
Nodes (15): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+7 more)

### Community 54 - "TestTela"
Cohesion: 0.12
Nodes (3): novo_servico(), TestTela, TestTermometro

### Community 55 - "HANDOFF.md"
Cohesion: 0.15
Nodes (8): Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente, Contexto para o Claude Code, Skill graphify (query, explain, path, update), Licenças dos dados de controle

### Community 56 - "modos/principal.py"
Cohesion: 0.09
Nodes (26): Android, aplicar_toque(), aplicar_volume(), atalho(), _avisar(), _chave(), _cond(), definir() (+18 more)

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 58 - "agir"
Cohesion: 0.08
Nodes (22): achar(), achar_regra(), agir(), _bloqueio_de_toque(), botao_fechar(), casas_xadrez(), compactos(), dump_ui() (+14 more)

### Community 59 - ".anotar"
Cohesion: 0.11
Nodes (5): BluetoothDevice, ScanRecord, ScanResult, ParcelUuid, SparseArray

### Community 61 - "TestSono"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 62 - "_objetivo"
Cohesion: 0.12
Nodes (15): _json_da_resposta(), _julgar(), julgar(), _modelo_do_nivel(), _objetivo(), abrir(), aplicar_regras(), bloqueado() (+7 more)

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 65 - "Servico"
Cohesion: 0.12
Nodes (5): ErroUso, Servico, Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105), Perfil Gree Unknown (catálogo nº 102), descartado, 2. Etapa 0 — armação diária local (1.0.23, implementada)

### Community 66 - "CelularFalso"
Cohesion: 0.17
Nodes (3): _carregar(), CelularFalso, TestModos

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 69 - "test_objetivo.py"
Cohesion: 0.29
Nodes (3): _carregar(), estado_da_captura(), TestAreaCegaComTeclado

### Community 70 - "test_controle_ir.py"
Cohesion: 0.09
Nodes (14): capacidades(), _curto(), ErroAparelho, _faixa_txt(), hora_legivel(), _linhas_aparelho(), resumo_aparelho(), resumo_compacto() (+6 more)

### Community 71 - "vigia.py"
Cohesion: 0.14
Nodes (8): _converter(), disparou(), norm(), numero(), satisfaz(), validar(), Vigias, laco()

### Community 72 - "Cerebros"
Cohesion: 0.15
Nodes (3): Cerebros, julgar_depois(), prompt_quiz()

### Community 75 - "criar_servidor"
Cohesion: 0.16
Nodes (13): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), local_ok() (+5 more)

### Community 76 - "Conexao"
Cohesion: 0.20
Nodes (4): carregar_memoria(), ao_texto(), Conexao, _confianca()

### Community 80 - "Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude"
Cohesion: 0.12
Nodes (16): Botão Stockfish para estudos, Capacidades plugáveis (ferramentas novas sem mexer no núcleo), Cobertura dos testes, Como funciona, Conectar ao ChatGPT ou ao Claude, Descoberta, Desenvolvimento, Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude (+8 more)

### Community 81 - "TestVigia"
Cohesion: 0.21
Nodes (3): _carregar(), Relogio, TestVigia

### Community 84 - "piloto.py"
Cohesion: 0.12
Nodes (7): caixa_da_pergunta(), corpo_api(), fen(), minha_cor(), quem_mexeu(), tabuleiro_txt(), _texto_do_evento()

### Community 86 - "Problemas já resolvidos (para não repetir)"
Cohesion: 0.14
Nodes (17): Pacote do celular dist/controle-ir.zip, Anúncio dos testes (v1.0.1), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026) (+9 more)

### Community 87 - ".main"
Cohesion: 0.17
Nodes (4): ScanSettings, Builder, Handler, Looper

### Community 88 - "observador.py"
Cohesion: 0.21
Nodes (8): relatar_uso(), apps_usando(), _capacidades_rodando(), em_uso(), quadro(), recursos_do_comando(), _tarefas(), _tela()

### Community 89 - "_iniciar"
Cohesion: 0.17
Nodes (10): avisar(), _aviso(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir(), mostrar_url() (+2 more)

### Community 90 - "bluetooth/principal.py"
Cohesion: 0.08
Nodes (24): buscar(), buscar_app(), buscar_shell(), classificar(), compilar(), distancia(), _ler_marca(), ler_pareados_dumpsys() (+16 more)

### Community 92 - "modulo_embutido"
Cohesion: 0.22
Nodes (10): modulo_embutido(), _retomar_vigias(), abrir(), configurar(), estudar(), ler_preferencias(), mostrar(), piloto_local() (+2 more)

### Community 93 - "shutil"
Cohesion: 0.21
Nodes (6): carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar()

### Community 99 - "gree_variante.py"
Cohesion: 0.23
Nodes (10): checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main(), perfil() (+2 more)

### Community 100 - "calcular"
Cohesion: 0.40
Nodes (3): calcular(), ev(), escolher_pela_conta()

### Community 104 - "canal.py"
Cohesion: 0.18
Nodes (7): consultar_modelo(), contexto(), executar(), planejar(), RespostaDePlanoInvalida, armado(), permitido()

### Community 105 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

### Community 106 - "Bluetooth"
Cohesion: 0.15
Nodes (4): Busca, Runnable, Bluetooth, Runnable

### Community 107 - "Piloto"
Cohesion: 0.19
Nodes (3): ler_chave(), Piloto, p()

### Community 109 - "._laco"
Cohesion: 0.31
Nodes (3): chave_quiz(), norm(), quiz_da_tela()

### Community 110 - ".controlar"
Cohesion: 0.19
Nodes (14): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50) (+6 more)

### Community 115 - "TestLeitorJava"
Cohesion: 0.05
Nodes (7): _carregar(), TestAppAuxiliar, TestBuscarNoCelular, TestClassificacao, TestCompilar, TestLeitorJava, TestTelaDicaDoCampo

### Community 118 - "Ar condicionado quarto 2 — Brastemp Clean (protocolo TCL112)"
Cohesion: 0.22
Nodes (8): Ar condicionado quarto 2 — Brastemp Clean (protocolo TCL112), Como foi identificado (22/11), Formato (TCL112, 2 quadros de 14 bytes, LSB primeiro, 38 kHz), Frases, Parâmetros do perfil, Regenerar o perfil no celular, Ressalvas, Testado no aparelho

### Community 125 - "ErroSinal"
Cohesion: 0.43
Nodes (3): ErroSinal, normalizar_pulsos(), pronto_para_pulsos()

### Community 127 - "PS4: controle completo e jogador que aprende (capacidade `ps4`, 1.0.109+)"
Cohesion: 0.29
Nodes (6): Instalação no Termux (uma vez, com o sistema armado), Jogador que aprende (`acao=jogador`), Limites medidos/esperados, Preparo (uma vez), PS4: controle completo e jogador que aprende (capacidade `ps4`, 1.0.109+), Uso

### Community 129 - "tela/principal.py"
Cohesion: 0.07
Nodes (25): _caixa(), _carregar_objetivo(), _chave(), classe_janela(), _conflitos(), _contar(), curto(), dentro() (+17 more)

### Community 135 - "termometro/principal.py"
Cohesion: 0.29
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 136 - "tcl112.py"
Cohesion: 0.26
Nodes (9): broadlink(), ErroTcl, estado(), _hex(), main(), perfil(), pulsos(), sinal() (+1 more)

### Community 138 - "tv do quarto (TV Samsung)"
Cohesion: 0.36
Nodes (8): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung), Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas), Catálogo instalado: base + ampliado (9.380 perfis)

### Community 140 - "analisar.py"
Cohesion: 0.31
Nodes (6): agenda(), analisar(), extras(), percentil95(), Comparação do planejador de missões no POCO, Rodada

### Community 145 - "jogador.py"
Cohesion: 0.33
Nodes (4): fracao_cor(), medir(), recompensa(), regiao()

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 901 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **56 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `f()` connect `time` to `tela/principal.py`, `Descoberta`, `Jogador`, `termometro/principal.py`, `tcl112.py`, `TestSonarFrequencia`, `.test_memoria_guarda_so_o_caminho_certo_sem_desvios`, `json`, `Catalogo`, `atualizar`, `Execucao`, `os`, `objetivo.py`, `os`, `ps4/principal.py`, `descobrir_rede/principal.py`, `cli.py`, `sonar/principal.py`, `modos/principal.py`, `Aparelhos`, `_objetivo`, `CelularFalso`, `vigia.py`, `Conexao`, `bluetooth/principal.py`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.051839464882943144 - nodes in this community are weakly interconnected._
- **Why does `Servico` connect `Servico` to `TestPrincipal`, `cli.py`, `Descoberta`, `Sinal`, `normalizar`, `test_controle_ir.py`, `Controlador`, `EmissorSimulado`, `ServidorMCP`, `test_controle_ir.py`, `criar_servidor`, `Registro`, `Catalogo`, `Execucao`, `TestTela`, `_iniciar`, `Aparelhos`, `ErroSinal`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Should `Descoberta` be split into smaller, more focused modules?**
  _Cohesion score 0.12926829268292683 - nodes in this community are weakly interconnected._
- **Why does `Tunel` connect `Tunel` to `TestTunel`, `cli.py`, `Problemas já resolvidos (para não repetir)`, `TestArmacao`, `_iniciar`, `shutil`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._