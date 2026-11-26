# Graph Report - Dialogue-flow  (2026-11-26)

## Corpus Check
- 145 files · ~202,848 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 2991 nodes · 6726 edges · 163 communities (96 shown, 67 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 508 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `13b2a791`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- Descoberta
- TestPainel
- TestVocabulario
- Sinal
- package.json
- Controlador
- agir
- TestExecutorObjetivo
- TestSonarFrequencia
- test_controle_ir.py
- steps
- painel.py
- TestTelaPorArquivo
- ligar
- json
- Catalogo
- protocolos.py
- test_objetivo.py
- _extrair_imagens
- Instalador (instalar.sh)
- Tela
- HANDOFF.md
- jogador.py
- objetivo.py
- e2e.cjs
- nome_da_chamada
- steps
- tela/principal.py
- Controlador
- Tunel
- descobrir_rede/principal.py
- TestJogador
- carregar_config
- godmode-tracker.js
- Tarefas
- normalizar
- piloto.py
- Conexao
- TestOuvirBipe
- ouvir_bipe/principal.py
- ServidorMCP
- TestSegundoPlano
- test_god_mode.py
- Registro
- webauthn.js
- session-start.sh
- TestEstadoCelularSemProc
- painel.py
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- test_agente_pc.py
- autorizar.js
- app.js
- Canal
- novo_servico
- Autonomia do planejador no POCO
- modos/principal.py
- TestPiloto
- ver
- .anotar
- ErroEmissor
- TestSono
- _objetivo
- Passagem de bastão do Dialogue-flow
- ps4/principal.py
- Servico
- CelularFalso
- local.cjs
- TestAgentePC
- test_objetivo.py
- grade
- vigia.py
- Piloto
- BluetoothAdapter
- shutil
- _privado
- TestArmacao
- TestRegioesWeb
- scripts
- Celular
- criar_servidor
- TestVigia
- android.bluetooth.le.ScanResult
- TestProtocolos
- PlanoTest
- TestObservador
- Problemas já resolvidos (para não repetir)
- .main
- observador.py
- _iniciar
- bluetooth/principal.py
- BluetoothClass
- modulo_embutido
- Ferramentas
- Bluetooth.java
- TestResumoSemRepeticao
- TestParidadeDoBloqueio
- atualizar_conhecimento.sh
- gree_variante.py
- TestAtualizacaoRecompila
- TestPilotoVisao
- TestLigacaoNoServicoDaTela
- ambiente_missao.py
- Contribuir com o Dialogue-flow
- Bluetooth
- Variante Gree a partir da captura real (troca só os bits)
- Notificador
- TestGodModeStmEPontuacao
- .controlar
- sistema.py
- TestResumoInstrucoes
- TestCapacidades
- TestBuscarNoCelular
- _Servidor
- .startScan
- sonar/principal.py
- main
- AttributionSource
- construir_app_bluetooth.sh script
- TestServidorMCP
- Process
- elementos
- ServidorMCP
- rish
- TestStockfishLocal
- Cerebros
- atualizar
- tcl112.py
- .test_memoria_guarda_so_o_caminho_certo_sem_desvios
- Motor
- controle_ir/cli.py
- Sinal
- .visao
- Sincronizador
- Conexao
- TestTunel
- TestLeitorJava
- TestAppAuxiliar
- criar_servidor
- PC na Central de Controle (agente do PC)
- os
- .test_atualizar_sem_ref_sai_do_head_destacado
- TestClassificacao
- TestImagemNoMcp
- PS4: controle completo e jogador que aprende (capacidade `ps4`, 1.0.109+)
- _carregar
- calcular
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
- `Regressões: cada erro vira um teste` --references--> `CanalPC`  [INFERRED]
  docs/regressoes.md → pc/agente_pc/cli.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `PC na Central de Controle (agente do PC)` --references--> `verificar_requisicao()`  [INFERRED]
  docs/pc.md → controle-ir/controle_ir/painel.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (163 total, 67 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.08
Nodes (65): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+57 more)

### Community 1 - "Descoberta"
Cohesion: 0.13
Nodes (3): agora(), Descoberta, ErroDescoberta

### Community 2 - "TestPainel"
Cohesion: 0.09
Nodes (15): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono (+7 more)

### Community 4 - "Sinal"
Cohesion: 0.10
Nodes (5): broadlink_para_pulsos(), pulsos_para_broadlink(), TestFormatos, TestGreeVariante, TestTcl112

### Community 5 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+10 more)

### Community 6 - "Controlador"
Cohesion: 0.25
Nodes (5): Controlador, Etapa, Plano, normalizar_valor(), valores_equivalentes()

### Community 7 - "agir"
Cohesion: 0.08
Nodes (13): achar(), achar_regra(), compactos(), eventos(), _Executor, els_fn(), relevantes(), _Falha (+5 more)

### Community 9 - "TestSonarFrequencia"
Cohesion: 0.06
Nodes (8): _carregar(), _Resposta, TestDescobrirRedeSemWifi, TestDiagnosticoRede, urlopen(), TestSonarFrequencia, testar(), TestTermometroSemResposta

### Community 10 - "test_controle_ir.py"
Cohesion: 0.08
Nodes (15): capacidades(), _curto(), ErroAparelho, _faixa_txt(), hora_legivel(), _linhas_aparelho(), resumo_aparelho(), resumo_compacto() (+7 more)

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "painel.py"
Cohesion: 0.06
Nodes (10): exec_cli(), painel_cli(), Autorizacao, classificar(), Execucao, gerar_segredo(), Politica, totp() (+2 more)

### Community 14 - "ligar"
Cohesion: 0.11
Nodes (14): arquivos_cc0(), main(), CanalPC, desligar(), estado(), ligar(), reduzir(), log() (+6 more)

### Community 15 - "json"
Cohesion: 0.14
Nodes (20): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+12 more)

### Community 16 - "Catalogo"
Cohesion: 0.10
Nodes (12): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), normalizar_marca() (+4 more)

### Community 17 - "protocolos.py"
Cohesion: 0.15
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 18 - "test_objetivo.py"
Cohesion: 0.12
Nodes (9): CelularWeb, estado_da_captura(), decidir(), TestObjetivoVisaoEGrafo, dec(), jul(), olh(), olhar() (+1 more)

### Community 19 - "_extrair_imagens"
Cohesion: 0.40
Nodes (3): _extrair_imagens(), varrer(), TestImagensAninhadas

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 22 - "HANDOFF.md"
Cohesion: 0.26
Nodes (3): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Licenças dos dados de controle

### Community 23 - "jogador.py"
Cohesion: 0.05
Nodes (13): centro_x(), Cerebro, Estados, fracao_cor(), Jogador, escrever(), mascara_cor(), medir() (+5 more)

### Community 24 - "objetivo.py"
Cohesion: 0.07
Nodes (28): area_cega(), assinatura(), busca(), concluido(), Executor, assinar(), cega_de(), fim() (+20 more)

### Community 25 - "e2e.cjs"
Cohesion: 0.13
Nodes (11): celular(), { chromium }, { execFileSync, spawn }, filhos, fs, nodeCrypto, os, PASTA (+3 more)

### Community 27 - "steps"
Cohesion: 0.11
Nodes (17): jobs, pacote, name, on, push, workflow_dispatch, runs-on, steps (+9 more)

### Community 28 - "tela/principal.py"
Cohesion: 0.07
Nodes (29): botao_fechar(), _carregar_objetivo(), _chave(), _contar(), dentro(), diferenca(), _eh_inicio(), executar() (+21 more)

### Community 29 - "Controlador"
Cohesion: 0.20
Nodes (3): EmissorSimulado, TestControle, TestDescoberta

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.11
Nodes (20): classificar(), ficha_upnp(), ip_do_wifi(), ler_inventarios(), main(), sondar(), ssdp(), tcp() (+12 more)

### Community 32 - "TestJogador"
Cohesion: 0.05
Nodes (9): ConexaoFalsa, Gravador, _mod(), TestComandos, TestCompatPyAV, TestConexaoLaco, TestJogador, TestPrincipal (+1 more)

### Community 33 - "carregar_config"
Cohesion: 0.29
Nodes (10): _api(), carregar_config(), console(), url_quando_pronta(), estado_servidor(), parar_servico(), _porta_ativa(), _saude() (+2 more)

### Community 34 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

### Community 35 - "Tarefas"
Cohesion: 0.14
Nodes (4): decodificar(), preparar(), _sem_janela(), Tarefas

### Community 36 - "normalizar"
Cohesion: 0.10
Nodes (23): Aparelhos, adicionar_comando(), comando(), importar_texto(), indice_comandos(), ler_flipper(), ler_smartir(), novo_perfil() (+15 more)

### Community 37 - "piloto.py"
Cohesion: 0.14
Nodes (7): chave_quiz(), fen(), minha_cor(), norm(), quem_mexeu(), quiz_da_tela(), tabuleiro_txt()

### Community 38 - "Conexao"
Cohesion: 0.10
Nodes (7): compat_av(), _flag(), video_codec(), Conexao, _ligar_log(), _Memoria, ultimas_linhas()

### Community 40 - "ouvir_bipe/principal.py"
Cohesion: 0.18
Nodes (10): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+2 more)

### Community 42 - "TestSegundoPlano"
Cohesion: 0.24
Nodes (3): TestSegundoPlano, abrir_console(), reiniciado()

### Community 43 - "test_god_mode.py"
Cohesion: 0.11
Nodes (5): _Base, _ComServidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos

### Community 44 - "Registro"
Cohesion: 0.20
Nodes (5): ErroCapacidade, _hash(), _manifesto(), Registro, capacidade_cli()

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 48 - "painel.py"
Cohesion: 0.08
Nodes (15): aplicar(), interpretar(), montar_pedido(), perguntar(), nome_da_chamada(), _b64(), estado_valido(), _eventos_novos() (+7 more)

### Community 49 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.06
Nodes (34): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+26 more)

### Community 50 - "test_agente_pc.py"
Cohesion: 0.09
Nodes (10): filtro(), ler_recortes(), main(), reduzir(), validar_recorte(), _resultado(), varrer(), matar_arvore() (+2 more)

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.26
Nodes (15): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+7 more)

### Community 53 - "Canal"
Cohesion: 0.10
Nodes (3): Canal, _mascarar(), WebSocket

### Community 54 - "novo_servico"
Cohesion: 0.09
Nodes (5): catalogo_base(), novo_servico(), TestCatalogo, TestTela, TestTermometro

### Community 55 - "Autonomia do planejador no POCO"
Cohesion: 0.22
Nodes (7): Comparação do planejador de missões no POCO, Rodada, Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente

### Community 56 - "modos/principal.py"
Cohesion: 0.09
Nodes (26): Android, aplicar_toque(), aplicar_volume(), atalho(), _avisar(), _chave(), _cond(), definir() (+18 more)

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 58 - "ver"
Cohesion: 0.16
Nodes (12): Ajudante, _apagar(), captura(), curto(), diferenca_curta(), foto_rapida(), _jar(), _jpeg() (+4 more)

### Community 59 - ".anotar"
Cohesion: 0.11
Nodes (5): BluetoothDevice, ScanRecord, ScanResult, ParcelUuid, SparseArray

### Community 60 - "ErroEmissor"
Cohesion: 0.20
Nodes (3): Emissor, EmissorTermux, ErroEmissor

### Community 61 - "TestSono"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 62 - "_objetivo"
Cohesion: 0.10
Nodes (19): escolher(), _json_da_resposta(), _julgar(), julgar(), _modelo_do_nivel(), _modulo_piloto(), _objetivo(), abrir() (+11 more)

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 64 - "ps4/principal.py"
Cohesion: 0.14
Nodes (25): cmd_comando(), fundo(), cmd_habilidade(), cmd_jogador(), codificar(), Estado, executar(), _frente() (+17 more)

### Community 66 - "CelularFalso"
Cohesion: 0.17
Nodes (3): _carregar(), CelularFalso, TestModos

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 70 - "grade"
Cohesion: 0.09
Nodes (15): aplicar_regras(), els_fn(), _caixa(), calma(), _conflitos(), grade(), _ler_grade(), _modelos_do_teclado() (+7 more)

### Community 71 - "vigia.py"
Cohesion: 0.14
Nodes (8): _converter(), disparou(), norm(), numero(), satisfaz(), validar(), Vigias, laco()

### Community 72 - "Piloto"
Cohesion: 0.18
Nodes (3): caixa_da_pergunta(), gravar_memoria(), Piloto

### Community 74 - "shutil"
Cohesion: 0.21
Nodes (6): carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar()

### Community 75 - "_privado"
Cohesion: 0.17
Nodes (8): analisar_web(), arvore(), andar(), ler_bounds(), regioes(), _privado(), regioes_visuais(), regioes_web()

### Community 78 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, deploy, dev, test:e2e

### Community 80 - "criar_servidor"
Cohesion: 0.24
Nodes (13): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), local_ok() (+5 more)

### Community 81 - "TestVigia"
Cohesion: 0.21
Nodes (3): _carregar(), Relogio, TestVigia

### Community 86 - "Problemas já resolvidos (para não repetir)"
Cohesion: 0.17
Nodes (15): Anúncio dos testes (v1.0.1), Catálogo instalado: base + ampliado (9.380 perfis), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026) (+7 more)

### Community 87 - ".main"
Cohesion: 0.17
Nodes (4): ScanSettings, Builder, Handler, Looper

### Community 88 - "observador.py"
Cohesion: 0.21
Nodes (8): relatar_uso(), apps_usando(), _capacidades_rodando(), em_uso(), quadro(), recursos_do_comando(), _tarefas(), _tela()

### Community 89 - "_iniciar"
Cohesion: 0.26
Nodes (10): avisar(), armar_cli(), _aviso(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir() (+2 more)

### Community 90 - "bluetooth/principal.py"
Cohesion: 0.10
Nodes (21): buscar(), buscar_app(), buscar_shell(), classificar(), compilar(), distancia(), guardar(), _ler_marca() (+13 more)

### Community 92 - "modulo_embutido"
Cohesion: 0.26
Nodes (9): modulo_embutido(), _retomar_vigias(), abrir(), configurar(), estudar(), ler_preferencias(), mostrar(), piloto_local() (+1 more)

### Community 93 - "Ferramentas"
Cohesion: 0.14
Nodes (4): _caminho(), Ferramentas, escapar_sendkeys(), Tela

### Community 97 - "TestParidadeDoBloqueio"
Cohesion: 0.11
Nodes (4): Regressões: cada erro vira um teste, Canal, _conjunto_js(), TestParidadeDoBloqueio

### Community 99 - "gree_variante.py"
Cohesion: 0.23
Nodes (10): checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main(), perfil() (+2 more)

### Community 104 - "ambiente_missao.py"
Cohesion: 0.22
Nodes (6): consultar_modelo(), contexto(), executar(), planejar(), armado(), permitido()

### Community 105 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

### Community 106 - "Bluetooth"
Cohesion: 0.15
Nodes (4): Busca, Runnable, Bluetooth, Runnable

### Community 107 - "Variante Gree a partir da captura real (troca só os bits)"
Cohesion: 0.14
Nodes (8): Pacote do celular dist/controle-ir.zip, Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50), Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105), Perfil Gree Unknown (catálogo nº 102), descartado, Problemas já resolvidos (para não repetir), Versão do servidor (celular 1.0.4, repositório 1.0.5), empacotar.sh script

### Community 110 - ".controlar"
Cohesion: 0.16
Nodes (19): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Ligar/desligar diretos (energia_ligar 0x99, energia_desligar 0x98), Macro abrir Netflix (inicio_3 + ok) (+11 more)

### Community 111 - "sistema.py"
Cohesion: 0.20
Nodes (11): cpu_uso(), discos(), _em_cache(), ligado_ha(), memoria(), nvidia(), placas_windows(), processador() (+3 more)

### Community 118 - "sonar/principal.py"
Cohesion: 0.22
Nodes (9): analisar_sonar(), escolher_e_testar(), frequencia_lembrada(), gerar_tom(), lembrar(), main(), sugestao_sem_tom(), testar() (+1 more)

### Community 119 - "main"
Cohesion: 0.17
Nodes (7): ampliar_catalogo(), iniciar(), main(), _pid_do_servico(), _soltar_inicio(), _travar_inicio(), Origens

### Community 127 - "elementos"
Cohesion: 0.15
Nodes (13): atividade_no_topo(), casas_xadrez(), classe_janela(), elementos(), em_anuncio(), foto(), _ferramentas_piloto(), aguardar() (+5 more)

### Community 129 - "rish"
Cohesion: 0.12
Nodes (25): _abrir(), agir(), _ajudante(), app_em_foco(), bloqueado(), bloqueados(), _bloqueio_de_toque(), dump_ui() (+17 more)

### Community 133 - "TestStockfishLocal"
Cohesion: 0.15
Nodes (3): escrever(), TestStockfishLocal, linha()

### Community 136 - "tcl112.py"
Cohesion: 0.06
Nodes (30): agenda(), analisar(), extras(), percentil95(), botao(), ErroComando, executar(), lado() (+22 more)

### Community 140 - "controle_ir/cli.py"
Cohesion: 0.14
Nodes (16): arquivo_boot(), boot_ativado(), caminho_log(), _carimbo_catalogo(), catalogo_atual(), _cfg_caminho(), criar_atalhos(), iniciar_em_segundo_plano() (+8 more)

### Community 141 - "Sinal"
Cohesion: 0.10
Nodes (15): ErroFormato, escrever_flipper(), exportar(), _hex_le(), ler_sinal_texto(), sinal(), sinais_pronto(), _sinal_smartir() (+7 more)

### Community 142 - ".visao"
Cohesion: 0.17
Nodes (6): ao_texto(), _confianca(), corpo_api(), ler_chave(), prompt_quiz(), p()

### Community 145 - "Conexao"
Cohesion: 0.24
Nodes (3): carregar_memoria(), Conexao, _texto_do_evento()

### Community 149 - "criar_servidor"
Cohesion: 0.18
Nodes (5): criar_servidor(), do_GET(), do_POST(), _json(), Guardiao

### Community 150 - "PC na Central de Controle (agente do PC)"
Cohesion: 0.25
Nodes (7): Ferramentas, Instalar no PC, Limites, Manter ligado, PC na Central de Controle (agente do PC), Religar o PC e o botão "Ligar Agente PC", Testes

### Community 151 - "os"
Cohesion: 0.09
Nodes (7): checksum(), empacotar(), fontes(), verificar(), TestApkAtualizado, TestManifesto, TestFerramentasDaMissao

### Community 158 - "PS4: controle completo e jogador que aprende (capacidade `ps4`, 1.0.109+)"
Cohesion: 0.29
Nodes (6): Instalação no Termux (uma vez, com o sistema armado), Jogador que aprende (`acao=jogador`), Limites medidos/esperados, Preparo (uma vez), PS4: controle completo e jogador que aprende (capacidade `ps4`, 1.0.109+), Uso

### Community 160 - "calcular"
Cohesion: 0.40
Nodes (3): calcular(), ev(), escolher_pela_conta()

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 967 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **67 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Regressões: cada erro vira um teste` connect `TestParidadeDoBloqueio` to `ligar`?**
  _High betweenness centrality (0.089) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.08198757763975155 - nodes in this community are weakly interconnected._
- **Why does `Canal` connect `TestParidadeDoBloqueio` to `index.js`?**
  _High betweenness centrality (0.087) - this node is a cross-community bridge._
- **Should `Descoberta` be split into smaller, more focused modules?**
  _Cohesion score 0.1346153846153846 - nodes in this community are weakly interconnected._
- **Why does `CanalPC` connect `ligar` to `TestParidadeDoBloqueio`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._