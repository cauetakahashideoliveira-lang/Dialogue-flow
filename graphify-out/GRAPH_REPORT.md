# Graph Report - Dialogue-flow  (2026-11-23)

## Corpus Check
- 129 files · ~183,524 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 2741 nodes · 6156 edges · 138 communities (91 shown, 47 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 454 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `f26b3414`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- Descoberta
- TestPainel
- TestVocabulario
- Sinal
- jogador.py
- Controlador
- agir
- TestExecutorObjetivo
- TestSonarFrequencia
- test_controle_ir.py
- steps
- painel.py
- TestTelaPorArquivo
- agir
- json
- .adicionar_perfil
- protocolos.py
- test_objetivo.py
- TestImagemNoMcp
- Instalador (instalar.sh)
- Tela
- Pacote do celular dist/controle-ir.zip
- os
- re
- e2e.cjs
- grade
- steps
- time
- ps4/principal.py
- Tunel
- descobrir_rede/principal.py
- vigia.py
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
- f
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- exec_cli
- autorizar.js
- app.js
- Canal
- novo_servico
- HANDOFF.md
- modos/principal.py
- TestPiloto
- elementos
- .anotar
- ErroEmissor
- TestSono
- _objetivo
- Passagem de bastão do Dialogue-flow
- Politica
- Servico
- CelularFalso
- local.cjs
- TestExecucao
- test_objetivo.py
- test_controle_ir.py
- vigia.py
- Cerebros
- BluetoothAdapter
- .executar
- criar_servidor
- Conexao
- TestRegioesWeb
- _privado
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
- Segurança do controle-ir: administração externa, armação e auditoria
- Bluetooth.java
- Motor
- TestParidadeDoBloqueio
- atualizar_conhecimento.sh
- gree_variante.py
- ._responder_por_visao
- TestPilotoVisao
- TestLigacaoNoServicoDaTela
- ambiente_missao.py
- Contribuir com o Dialogue-flow
- Bluetooth
- Piloto
- Notificador
- ._laco
- .controlar
- Sincronizador
- TestResumoInstrucoes
- TestCapacidades
- TestLeitorJava
- _Servidor
- .startScan
- Reenvios
- Origens
- AttributionSource
- construir_app_bluetooth.sh script
- Ar condicionado quarto 2 — Brastemp Clean (protocolo TCL112)
- Process
- PS4: controle completo e jogador que aprende (capacidade `ps4`, 1.0.109+)
- TestServidorMCP
- tela/principal.py
- Autonomia do planejador no POCO
- atualizar
- tcl112.py
- .test_memoria_guarda_so_o_caminho_certo_sem_desvios

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
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
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

## Communities (138 total, 47 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.05
Nodes (82): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+74 more)

### Community 1 - "Descoberta"
Cohesion: 0.08
Nodes (5): agora(), Catalogo, normalizar_marca(), Descoberta, ErroDescoberta

### Community 2 - "TestPainel"
Cohesion: 0.13
Nodes (10): 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), Planejado (próximas etapas), TestPainel, do_GET() (+2 more)

### Community 4 - "Sinal"
Cohesion: 0.10
Nodes (17): ErroFormato, escrever_flipper(), exportar(), _hex_le(), indice_comandos(), ler_flipper(), ler_sinal_texto(), sinal() (+9 more)

### Community 5 - "jogador.py"
Cohesion: 0.05
Nodes (21): agenda(), analisar(), extras(), percentil95(), botao(), ErroComando, executar(), lado() (+13 more)

### Community 6 - "Controlador"
Cohesion: 0.15
Nodes (7): Controlador, Etapa, Plano, EmissorSimulado, normalizar_valor(), valores_equivalentes(), TestControle

### Community 7 - "agir"
Cohesion: 0.07
Nodes (15): achar(), achar_regra(), casas_xadrez(), compactos(), escapar_input_text(), eventos(), _Executor, relevantes() (+7 more)

### Community 9 - "TestSonarFrequencia"
Cohesion: 0.07
Nodes (7): _carregar(), _Resposta, TestDiagnosticoRede, urlopen(), TestSonarFrequencia, testar(), TestTermometroSemResposta

### Community 10 - "test_controle_ir.py"
Cohesion: 0.09
Nodes (3): TestApkAtualizado, TestManifesto, TestGodModeStmEPontuacao

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "painel.py"
Cohesion: 0.10
Nodes (10): _b64(), _eventos_novos(), gravar(), _http(), parear(), sincronizar(), verificar(), verificar_requisicao() (+2 more)

### Community 14 - "agir"
Cohesion: 0.12
Nodes (24): agir(), _ajudante(), app_em_foco(), bloqueado(), bloqueados(), _bloqueio_de_toque(), _executar(), escolher() (+16 more)

### Community 15 - "json"
Cohesion: 0.11
Nodes (22): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+14 more)

### Community 16 - ".adicionar_perfil"
Cohesion: 0.17
Nodes (8): estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), _unzip(), _zip()

### Community 17 - "protocolos.py"
Cohesion: 0.15
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 18 - "test_objetivo.py"
Cohesion: 0.13
Nodes (7): CelularWeb, decidir(), TestObjetivoVisaoEGrafo, dec(), olh(), olhar(), web()

### Community 19 - "TestImagemNoMcp"
Cohesion: 0.18
Nodes (4): _extrair_imagens(), varrer(), TestImagemNoMcp, TestImagensAninhadas

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 23 - "os"
Cohesion: 0.07
Nodes (26): carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar(), filtro(), ler_recortes() (+18 more)

### Community 24 - "re"
Cohesion: 0.13
Nodes (15): area_cega(), assinatura(), busca(), concluido(), interruptor(), melhor(), no_retangulo(), norm() (+7 more)

### Community 25 - "e2e.cjs"
Cohesion: 0.09
Nodes (15): flagPath, fs, os, path, celular(), { chromium }, { execFileSync, spawn }, filhos (+7 more)

### Community 26 - "grade"
Cohesion: 0.08
Nodes (16): aplicar_regras(), els_fn(), _caixa(), calma(), _conflitos(), els_fn(), grade(), _ler_grade() (+8 more)

### Community 27 - "steps"
Cohesion: 0.11
Nodes (17): jobs, pacote, name, on, push, workflow_dispatch, runs-on, steps (+9 more)

### Community 28 - "time"
Cohesion: 0.14
Nodes (15): Ajudante, _apagar(), captura(), dump_ui(), estado_rapido(), foto_rapida(), _jpeg(), _ler() (+7 more)

### Community 29 - "ps4/principal.py"
Cohesion: 0.15
Nodes (22): cmd_comando(), fundo(), cmd_habilidade(), cmd_jogador(), codificar(), Estado, executar(), _gravar() (+14 more)

### Community 30 - "Tunel"
Cohesion: 0.10
Nodes (3): Tunel, TestArmacao, TestTunel

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.12
Nodes (19): classificar(), ficha_upnp(), ip_do_wifi(), ler_inventarios(), main(), sondar(), ssdp(), tcp() (+11 more)

### Community 32 - "vigia.py"
Cohesion: 0.22
Nodes (7): _converter(), disparou(), norm(), numero(), satisfaz(), validar(), sem_acentos()

### Community 33 - "cli.py"
Cohesion: 0.11
Nodes (32): ampliar_catalogo(), _api(), arquivo_boot(), boot_ativado(), caminho_log(), _carimbo_catalogo(), carregar_config(), catalogo_atual() (+24 more)

### Community 34 - "TestPrincipal"
Cohesion: 0.07
Nodes (6): ConexaoFalsa, Gravador, _mod(), TestComandos, TestJogador, TestPrincipal

### Community 35 - "schema.sql"
Cohesion: 0.12
Nodes (15): aparelhos, chamadas, config, convites, credenciais, desafios, estado, eventos (+7 more)

### Community 36 - "normalizar"
Cohesion: 0.14
Nodes (19): Aparelhos, adicionar_comando(), comando(), importar_texto(), ler_smartir(), novo_perfil(), _traduz(), categoria_canonica() (+11 more)

### Community 38 - "broadlink_para_pulsos"
Cohesion: 0.10
Nodes (5): broadlink_para_pulsos(), pulsos_para_broadlink(), TestFormatos, TestGreeVariante, TestTcl112

### Community 40 - "sonar/principal.py"
Cohesion: 0.22
Nodes (9): analisar_sonar(), escolher_e_testar(), frequencia_lembrada(), gerar_tom(), lembrar(), main(), sugestao_sem_tom(), testar() (+1 more)

### Community 41 - "ServidorMCP"
Cohesion: 0.12
Nodes (3): PlanoTest, ServidorMCP, 2. Etapa 0 — armação diária local (1.0.23, implementada)

### Community 42 - "TestSegundoPlano"
Cohesion: 0.08
Nodes (7): catalogo_base(), TestCatalogo, TestRepositorio, TestSegundoPlano, abrir_console(), reiniciado(), TestStockfishLocal

### Community 43 - "test_god_mode.py"
Cohesion: 0.11
Nodes (5): _Base, _ComServidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos

### Community 44 - "Registro"
Cohesion: 0.10
Nodes (7): ErroCapacidade, _hash(), _manifesto(), Registro, capacidade_cli(), classificar(), Execucao

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 47 - "test_consistencia.py"
Cohesion: 0.11
Nodes (5): _estado_celular(), TestAtualizacaoRecompila, TestEstadoCelularSemProc, TestFerramentasDaMissao, TestResumoSemRepeticao

### Community 48 - "f"
Cohesion: 0.12
Nodes (5): Executor, Grafo, gravar(), f(), TestDescobrirRedeSemWifi

### Community 49 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.11
Nodes (18): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+10 more)

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
Cohesion: 0.07
Nodes (6): Canal, _mascarar(), nome_da_chamada(), WebSocket, TestCanal, central()

### Community 54 - "novo_servico"
Cohesion: 0.11
Nodes (3): novo_servico(), TestTela, TestTermometro

### Community 55 - "HANDOFF.md"
Cohesion: 0.18
Nodes (5): Comparação do planejador de missões no POCO, Rodada, Contexto para o Claude Code, Skill graphify (query, explain, path, update), Licenças dos dados de controle

### Community 56 - "modos/principal.py"
Cohesion: 0.09
Nodes (26): Android, aplicar_toque(), aplicar_volume(), atalho(), _avisar(), _chave(), _cond(), definir() (+18 more)

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 58 - "elementos"
Cohesion: 0.11
Nodes (15): _abrir(), atividade_no_topo(), botao_fechar(), classe_janela(), dentro(), elementos(), em_anuncio(), fechar_anuncio() (+7 more)

### Community 59 - ".anotar"
Cohesion: 0.13
Nodes (4): ScanRecord, ScanResult, ParcelUuid, SparseArray

### Community 60 - "ErroEmissor"
Cohesion: 0.20
Nodes (3): Emissor, EmissorTermux, ErroEmissor

### Community 61 - "TestSono"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 62 - "_objetivo"
Cohesion: 0.10
Nodes (18): _json_da_resposta(), _julgar(), julgar(), _modelo_do_nivel(), _objetivo(), abrir(), abrir_url(), aplicar_regras() (+10 more)

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 64 - "Politica"
Cohesion: 0.20
Nodes (6): armar_cli(), painel_cli(), Politica, estado_valido(), ler(), fim_do_dia()

### Community 65 - "Servico"
Cohesion: 0.10
Nodes (5): ErroUso, Servico, Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105), Perfil Gree Unknown (catálogo nº 102), descartado, TestDescoberta

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
Cohesion: 0.08
Nodes (14): capacidades(), _curto(), ErroAparelho, _faixa_txt(), hora_legivel(), _linhas_aparelho(), resumo_aparelho(), resumo_compacto() (+6 more)

### Community 72 - "Cerebros"
Cohesion: 0.16
Nodes (3): Cerebros, ler_chave(), prompt_quiz()

### Community 74 - ".executar"
Cohesion: 0.18
Nodes (11): assinar(), cega_de(), fim(), ler_resposta(), regioes(), inteiro(), numerico(), sistema() (+3 more)

### Community 75 - "criar_servidor"
Cohesion: 0.24
Nodes (13): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), local_ok() (+5 more)

### Community 76 - "Conexao"
Cohesion: 0.18
Nodes (5): carregar_memoria(), ao_texto(), Conexao, _confianca(), _texto_do_evento()

### Community 78 - "_privado"
Cohesion: 0.17
Nodes (8): analisar_web(), arvore(), andar(), ler_bounds(), regioes(), _privado(), regioes_visuais(), regioes_web()

### Community 80 - "Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude"
Cohesion: 0.12
Nodes (16): Botão Stockfish para estudos, Capacidades plugáveis (ferramentas novas sem mexer no núcleo), Cobertura dos testes, Como funciona, Conectar ao ChatGPT ou ao Claude, Descoberta, Desenvolvimento, Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude (+8 more)

### Community 81 - "TestVigia"
Cohesion: 0.21
Nodes (3): _carregar(), Relogio, TestVigia

### Community 84 - "piloto.py"
Cohesion: 0.14
Nodes (6): corpo_api(), fen(), gravar_memoria(), minha_cor(), quem_mexeu(), tabuleiro_txt()

### Community 86 - "Problemas já resolvidos (para não repetir)"
Cohesion: 0.14
Nodes (17): Anúncio dos testes (v1.0.1), Catálogo instalado: base + ampliado (9.380 perfis), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026) (+9 more)

### Community 87 - ".main"
Cohesion: 0.17
Nodes (4): ScanSettings, Builder, Handler, Looper

### Community 88 - "observador.py"
Cohesion: 0.21
Nodes (8): relatar_uso(), apps_usando(), _capacidades_rodando(), em_uso(), quadro(), recursos_do_comando(), _tarefas(), _tela()

### Community 89 - "_iniciar"
Cohesion: 0.17
Nodes (13): avisar(), _aviso(), iniciar(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir() (+5 more)

### Community 90 - "bluetooth/principal.py"
Cohesion: 0.11
Nodes (19): buscar(), buscar_app(), buscar_shell(), classificar(), compilar(), distancia(), guardar(), _ler_marca() (+11 more)

### Community 92 - "modulo_embutido"
Cohesion: 0.47
Nodes (6): abrir(), configurar(), estudar(), ler_preferencias(), mostrar(), Preferencias

### Community 93 - "Segurança do controle-ir: administração externa, armação e auditoria"
Cohesion: 0.40
Nodes (5): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono, 6. Limites que nenhuma etapa remove, Segurança do controle-ir: administração externa, armação e auditoria

### Community 99 - "gree_variante.py"
Cohesion: 0.22
Nodes (10): checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main(), perfil() (+2 more)

### Community 100 - "._responder_por_visao"
Cohesion: 0.20
Nodes (4): caixa_da_pergunta(), calcular(), ev(), escolher_pela_conta()

### Community 104 - "ambiente_missao.py"
Cohesion: 0.12
Nodes (9): consultar_modelo(), contexto(), executar(), planejar(), RespostaDePlanoInvalida, modulo_embutido(), resumo_instrucoes(), armado() (+1 more)

### Community 105 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

### Community 106 - "Bluetooth"
Cohesion: 0.14
Nodes (4): Busca, Runnable, Bluetooth, Runnable

### Community 109 - "._laco"
Cohesion: 0.31
Nodes (3): chave_quiz(), norm(), quiz_da_tela()

### Community 110 - ".controlar"
Cohesion: 0.12
Nodes (21): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50) (+13 more)

### Community 115 - "TestLeitorJava"
Cohesion: 0.05
Nodes (7): _carregar(), TestAppAuxiliar, TestBuscarNoCelular, TestClassificacao, TestCompilar, TestLeitorJava, TestTelaDicaDoCampo

### Community 125 - "Ar condicionado quarto 2 — Brastemp Clean (protocolo TCL112)"
Cohesion: 0.22
Nodes (8): Ar condicionado quarto 2 — Brastemp Clean (protocolo TCL112), Como foi identificado (22/11), Formato (TCL112, 2 quadros de 14 bytes, LSB primeiro, 38 kHz), Frases, Parâmetros do perfil, Regenerar o perfil no celular, Ressalvas, Testado no aparelho

### Community 127 - "PS4: controle completo e jogador que aprende (capacidade `ps4`, 1.0.109+)"
Cohesion: 0.29
Nodes (6): Instalação no Termux (uma vez, com o sistema armado), Jogador que aprende (`acao=jogador`), Limites medidos/esperados, Preparo (uma vez), PS4: controle completo e jogador que aprende (capacidade `ps4`, 1.0.109+), Uso

### Community 129 - "tela/principal.py"
Cohesion: 0.09
Nodes (23): _carregar_objetivo(), _chave(), _contar(), curto(), diferenca(), diferenca_curta(), _eh_inicio(), executar() (+15 more)

### Community 133 - "Autonomia do planejador no POCO"
Cohesion: 0.40
Nodes (5): Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente

### Community 136 - "tcl112.py"
Cohesion: 0.28
Nodes (9): broadlink(), ErroTcl, estado(), _hex(), main(), perfil(), pulsos(), sinal() (+1 more)

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 894 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **47 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `cli.py`, `Descoberta`, `TestPrincipal`, `normalizar`, `Sinal`, `test_controle_ir.py`, `Controlador`, `ambiente_missao.py`, `ServidorMCP`, `criar_servidor`, `Registro`, `.controlar`, `novo_servico`, `_iniciar`, `ErroEmissor`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.051839464882943144 - nodes in this community are weakly interconnected._
- **Why does `f()` connect `f` to `tela/principal.py`, `Descoberta`, `jogador.py`, `atualizar`, `tcl112.py`, `.test_memoria_guarda_so_o_caminho_certo_sem_desvios`, `agir`, `json`, `.adicionar_perfil`, `os`, `ps4/principal.py`, `descobrir_rede/principal.py`, `cli.py`, `normalizar`, `sonar/principal.py`, `Registro`, `modos/principal.py`, `_objetivo`, `CelularFalso`, `vigia.py`, `Conexao`, `piloto.py`, `bluetooth/principal.py`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Should `Descoberta` be split into smaller, more focused modules?**
  _Cohesion score 0.08123904149620105 - nodes in this community are weakly interconnected._
- **Why does `TestTunel` connect `Tunel` to `test_controle_ir.py`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._