# Graph Report - Dialogue-flow  (2026-11-23)

## Corpus Check
- 122 files · ~173,558 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 2563 nodes · 5801 edges · 140 communities (93 shown, 47 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 439 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `c6b56dba`
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
- TestExecutorObjetivo
- TestSonarFrequencia
- test_controle_ir.py
- steps
- painel.py
- TestTelaPorArquivo
- TestServidorMCP
- subprocess
- Catalogo
- protocolos.py
- test_objetivo.py
- _extrair_imagens
- Instalador (instalar.sh)
- Tela
- Pacote do celular dist/controle-ir.zip
- subprocess
- objetivo.py
- e2e.cjs
- json
- steps
- tela/principal.py
- Controlador
- json
- descobrir_rede/principal.py
- normalizar
- cli.py
- _ferramentas_piloto
- schema.sql
- normalizar
- hashlib
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
- Execucao
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- exec_cli
- autorizar.js
- app.js
- Canal
- novo_servico
- HANDOFF.md
- modos/principal.py
- TestPiloto
- time
- .anotar
- ErroEmissor
- TestSono
- _objetivo
- Passagem de bastão do Dialogue-flow
- Politica
- normalizar
- CelularFalso
- local.cjs
- TestExecucao
- piloto.py
- servico.py
- Vigias
- Cerebros
- BluetoothAdapter
- Piloto
- Motor
- TestArmacao
- ._laco
- re
- Celular
- Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude
- TestVigia
- android.bluetooth.le.ScanResult
- Sinal
- PlanoTest
- TestProtocolos
- Problemas já resolvidos (para não repetir)
- .main
- observador.py
- _iniciar
- bluetooth/principal.py
- BluetoothDevice
- modulo_embutido
- Segurança do controle-ir: administração externa, armação e auditoria
- Bluetooth.java
- rotina
- TestParidadeDoBloqueio
- atualizar_conhecimento.sh
- gree_variante.py
- criar_servidor
- TestPilotoVisao
- TestLigacaoNoServicoDaTela
- ambiente_missao.py
- Contribuir com o Dialogue-flow
- Bluetooth
- ar do quarto (ar-condicionado Gree GWH09KF)
- Notificador
- Ar condicionado quarto 2 — Brastemp Clean (protocolo TCL112)
- ar do escritório (ar-condicionado Carrier)
- Tunel
- TestResumoInstrucoes
- TestCapacidades
- TestLeitorJava
- _Servidor
- .startScan
- inicio_automatico
- Origens
- AttributionSource
- construir_app_bluetooth.sh script
- Autonomia do planejador no POCO
- Process
- TestFormatos
- calcular
- re
- tv do quarto (TV Samsung)
- CelularWeb
- atualizar
- tcl112.py

## God Nodes (most connected - your core abstractions)
1. `Servico` - 62 edges
2. `Celular` - 47 edges
3. `f()` - 43 edges
4. `main()` - 38 edges
5. `Tela` - 37 edges
6. `Descoberta` - 37 edges
7. `Sinal` - 37 edges
8. `TestTelaPorArquivo` - 36 edges
9. `Catalogo` - 35 edges
10. `TestExecutorObjetivo` - 32 edges

## Surprising Connections (you probably didn't know these)
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `ampliar_catalogo()`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/cli.py
- `3a. Central de Controle (1.0.24, implementada) — `painel/`` --references--> `TestPainel`  [EXTRACTED]
  docs/seguranca.md → testes/test_controle_ir.py
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (140 total, 47 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.05
Nodes (82): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+74 more)

### Community 1 - "Descoberta"
Cohesion: 0.13
Nodes (3): agora(), Descoberta, ErroDescoberta

### Community 2 - "TestPainel"
Cohesion: 0.18
Nodes (4): TestPainel, do_GET(), do_POST(), _r()

### Community 3 - "Conexao"
Cohesion: 0.20
Nodes (4): carregar_memoria(), ao_texto(), Conexao, _confianca()

### Community 4 - "Sinal"
Cohesion: 0.20
Nodes (7): _classes(), ErroSinal, impressao_bruta(), limitar_duracao(), normalizar_pulsos(), pronto_para_pulsos(), _quadros()

### Community 5 - "shutil"
Cohesion: 0.35
Nodes (6): carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar()

### Community 6 - "Controlador"
Cohesion: 0.18
Nodes (6): hora_legivel(), Etapa, executar(), Plano, normalizar_valor(), valores_equivalentes()

### Community 7 - ".passo"
Cohesion: 0.07
Nodes (18): achar(), achar_regra(), els_fn(), casas_xadrez(), classe_janela(), compactos(), elementos(), escapar_input_text() (+10 more)

### Community 9 - "TestSonarFrequencia"
Cohesion: 0.06
Nodes (8): _carregar(), _Resposta, TestDescobrirRedeSemWifi, TestDiagnosticoRede, urlopen(), TestSonarFrequencia, testar(), TestTermometroSemResposta

### Community 10 - "test_controle_ir.py"
Cohesion: 0.06
Nodes (9): checksum(), empacotar(), fontes(), verificar(), main(), preparar(), TestApkAtualizado, TestManifesto (+1 more)

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "painel.py"
Cohesion: 0.13
Nodes (11): _b64(), estado_valido(), _eventos_novos(), gravar(), _http(), ler(), parear(), Sincronizador (+3 more)

### Community 15 - "subprocess"
Cohesion: 0.18
Nodes (10): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+2 more)

### Community 16 - "Catalogo"
Cohesion: 0.12
Nodes (11): Catalogo, estado_representativo(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), normalizar_marca(), _unzip() (+3 more)

### Community 17 - "protocolos.py"
Cohesion: 0.15
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 18 - "test_objetivo.py"
Cohesion: 0.12
Nodes (10): _carregar(), estado_da_captura(), decidir(), escolher(), TestObjetivoVisaoEGrafo, dec(), jul(), olh() (+2 more)

### Community 19 - "_extrair_imagens"
Cohesion: 0.40
Nodes (3): _extrair_imagens(), varrer(), TestImagensAninhadas

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 23 - "subprocess"
Cohesion: 0.27
Nodes (5): filtro(), ler_recortes(), main(), reduzir(), validar_recorte()

### Community 24 - "objetivo.py"
Cohesion: 0.07
Nodes (26): area_cega(), assinatura(), busca(), concluido(), Executor, assinar(), cega_de(), fim() (+18 more)

### Community 25 - "e2e.cjs"
Cohesion: 0.09
Nodes (15): flagPath, fs, os, path, celular(), { chromium }, { execFileSync, spawn }, filhos (+7 more)

### Community 26 - "json"
Cohesion: 0.23
Nodes (12): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+4 more)

### Community 27 - "steps"
Cohesion: 0.11
Nodes (17): jobs, pacote, name, on, push, workflow_dispatch, runs-on, steps (+9 more)

### Community 28 - "tela/principal.py"
Cohesion: 0.06
Nodes (36): _abrir(), botao_fechar(), _caixa(), calma(), _carregar_objetivo(), _chave(), _conflitos(), _contar() (+28 more)

### Community 29 - "Controlador"
Cohesion: 0.22
Nodes (4): Controlador, EmissorSimulado, TestControle, TestDescoberta

### Community 30 - "json"
Cohesion: 0.29
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.08
Nodes (25): agenda(), analisar(), extras(), percentil95(), Comparação do planejador de missões no POCO, Rodada, classificar(), ficha_upnp() (+17 more)

### Community 32 - "normalizar"
Cohesion: 0.16
Nodes (12): categoria_canonica(), chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar(), sem_acentos(), slug() (+4 more)

### Community 33 - "cli.py"
Cohesion: 0.11
Nodes (27): ampliar_catalogo(), _api(), armar_cli(), caminho_log(), _carimbo_catalogo(), carregar_config(), catalogo_atual(), _cfg_caminho() (+19 more)

### Community 34 - "_ferramentas_piloto"
Cohesion: 0.22
Nodes (8): atividade_no_topo(), _ferramentas_piloto(), aguardar(), tabuleiro_local(), tela_chess(), tocar(), partida_contra_robo(), vez_no_historico()

### Community 35 - "schema.sql"
Cohesion: 0.12
Nodes (15): aparelhos, chamadas, config, convites, credenciais, desafios, estado, eventos (+7 more)

### Community 36 - "normalizar"
Cohesion: 0.19
Nodes (16): adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos() (+8 more)

### Community 38 - "broadlink_para_pulsos"
Cohesion: 0.14
Nodes (3): broadlink_para_pulsos(), TestGreeVariante, TestTcl112

### Community 40 - "sonar/principal.py"
Cohesion: 0.23
Nodes (8): analisar_sonar(), escolher_e_testar(), frequencia_lembrada(), gerar_tom(), main(), sugestao_sem_tom(), testar(), volume_musica()

### Community 41 - "ServidorMCP"
Cohesion: 0.14
Nodes (3): resumo_instrucoes(), ServidorMCP, TestImagemNoMcp

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

### Community 49 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.11
Nodes (18): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+10 more)

### Community 50 - "exec_cli"
Cohesion: 0.23
Nodes (3): exec_cli(), Autorizacao, gerar_segredo()

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
Cohesion: 0.22
Nodes (3): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Licenças dos dados de controle

### Community 56 - "modos/principal.py"
Cohesion: 0.09
Nodes (26): Android, aplicar_toque(), aplicar_volume(), atalho(), _avisar(), _chave(), _cond(), definir() (+18 more)

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 58 - "time"
Cohesion: 0.10
Nodes (18): lembrar(), gravar_memoria(), Ajudante, _apagar(), _bloqueio_de_toque(), captura(), dump_ui(), estado_rapido() (+10 more)

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
Cohesion: 0.11
Nodes (17): _json_da_resposta(), _julgar(), julgar(), _modelo_do_nivel(), _objetivo(), abrir(), aplicar_regras(), bloqueado() (+9 more)

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 64 - "Politica"
Cohesion: 0.26
Nodes (3): painel_cli(), Politica, fim_do_dia()

### Community 65 - "normalizar"
Cohesion: 0.10
Nodes (6): Aparelhos, ErroAparelho, ErroUso, Servico, Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper), Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas)

### Community 66 - "CelularFalso"
Cohesion: 0.17
Nodes (3): _carregar(), CelularFalso, TestModos

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 69 - "piloto.py"
Cohesion: 0.12
Nodes (7): caixa_da_pergunta(), corpo_api(), fen(), minha_cor(), quem_mexeu(), tabuleiro_txt(), _texto_do_evento()

### Community 70 - "servico.py"
Cohesion: 0.19
Nodes (7): capacidades(), _curto(), _faixa_txt(), _linhas_aparelho(), resumo_aparelho(), resumo_compacto(), resumo_para_instrucoes()

### Community 72 - "Cerebros"
Cohesion: 0.15
Nodes (3): Cerebros, julgar_depois(), prompt_quiz()

### Community 74 - "Piloto"
Cohesion: 0.19
Nodes (3): ler_chave(), Piloto, p()

### Community 77 - "._laco"
Cohesion: 0.31
Nodes (3): chave_quiz(), norm(), quiz_da_tela()

### Community 78 - "re"
Cohesion: 0.17
Nodes (8): janela_nova(), _regex_bloqueados(), tabuleiro_curto(), disparou(), norm(), numero(), satisfaz(), validar()

### Community 80 - "Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude"
Cohesion: 0.12
Nodes (16): Botão Stockfish para estudos, Capacidades plugáveis (ferramentas novas sem mexer no núcleo), Cobertura dos testes, Como funciona, Conectar ao ChatGPT ou ao Claude, Descoberta, Desenvolvimento, Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude (+8 more)

### Community 81 - "TestVigia"
Cohesion: 0.22
Nodes (3): _carregar(), Relogio, TestVigia

### Community 83 - "Sinal"
Cohesion: 0.23
Nodes (3): sinal(), _sinal_smartir(), Sinal

### Community 85 - "TestProtocolos"
Cohesion: 0.12
Nodes (3): TestObservador, TestProtocolos, TestVocabulario

### Community 86 - "Problemas já resolvidos (para não repetir)"
Cohesion: 0.16
Nodes (16): Anúncio dos testes (v1.0.1), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026), Frases (+8 more)

### Community 87 - ".main"
Cohesion: 0.17
Nodes (4): ScanSettings, Builder, Handler, Looper

### Community 88 - "observador.py"
Cohesion: 0.21
Nodes (8): relatar_uso(), apps_usando(), _capacidades_rodando(), em_uso(), quadro(), recursos_do_comando(), _tarefas(), _tela()

### Community 89 - "_iniciar"
Cohesion: 0.24
Nodes (10): avisar(), _aviso(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir(), mostrar_url() (+2 more)

### Community 90 - "bluetooth/principal.py"
Cohesion: 0.11
Nodes (19): buscar(), buscar_app(), buscar_shell(), classificar(), compilar(), distancia(), guardar(), _ler_marca() (+11 more)

### Community 92 - "modulo_embutido"
Cohesion: 0.33
Nodes (8): modulo_embutido(), abrir(), configurar(), estudar(), ler_preferencias(), mostrar(), piloto_local(), Preferencias

### Community 93 - "Segurança do controle-ir: administração externa, armação e auditoria"
Cohesion: 0.17
Nodes (12): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 2. Etapa 0 — armação diária local (1.0.23, implementada), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1) (+4 more)

### Community 96 - "rotina"
Cohesion: 0.18
Nodes (7): executar(), main(), _resumo_volta(), retomar_vigias(), rotina(), gravar(), _rotinas()

### Community 99 - "gree_variante.py"
Cohesion: 0.20
Nodes (11): exportar_jsonl(), checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main() (+3 more)

### Community 100 - "criar_servidor"
Cohesion: 0.24
Nodes (13): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), local_ok() (+5 more)

### Community 104 - "ambiente_missao.py"
Cohesion: 0.18
Nodes (7): consultar_modelo(), contexto(), executar(), planejar(), RespostaDePlanoInvalida, armado(), permitido()

### Community 105 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

### Community 106 - "Bluetooth"
Cohesion: 0.15
Nodes (4): Busca, Runnable, Bluetooth, Runnable

### Community 107 - "ar do quarto (ar-condicionado Gree GWH09KF)"
Cohesion: 0.20
Nodes (8): Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50), Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105), Perfil Gree Unknown (catálogo nº 102), descartado, Ligar/desligar diretos (energia_ligar 0x99, energia_desligar 0x98)

### Community 109 - "Ar condicionado quarto 2 — Brastemp Clean (protocolo TCL112)"
Cohesion: 0.22
Nodes (8): Ar condicionado quarto 2 — Brastemp Clean (protocolo TCL112), Como foi identificado (22/11), Formato (TCL112, 2 quadros de 14 bytes, LSB primeiro, 38 kHz), Frases, Parâmetros do perfil, Regenerar o perfil no celular, Ressalvas, Testado no aparelho

### Community 110 - "ar do escritório (ar-condicionado Carrier)"
Cohesion: 0.36
Nodes (8): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Cômodo: Escritório, Cômodo: Laboratório, Cômodo: Quarto, Índice de aparelhos (cômodo → aparelho → controle), Aparelhos salvos

### Community 115 - "TestLeitorJava"
Cohesion: 0.05
Nodes (7): _carregar(), TestAppAuxiliar, TestBuscarNoCelular, TestClassificacao, TestCompilar, TestLeitorJava, TestTelaDicaDoCampo

### Community 118 - "inicio_automatico"
Cohesion: 0.33
Nodes (6): arquivo_boot(), boot_ativado(), criar_atalhos(), inicio_automatico(), pasta_atalhos(), script_boot()

### Community 125 - "Autonomia do planejador no POCO"
Cohesion: 0.40
Nodes (5): Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente

### Community 128 - "calcular"
Cohesion: 0.40
Nodes (3): calcular(), ev(), escolher_pela_conta()

### Community 129 - "re"
Cohesion: 0.12
Nodes (26): agir(), _ajudante(), aplicar_regras(), app_em_foco(), bloqueado(), bloqueados(), _executar(), escolher() (+18 more)

### Community 133 - "tv do quarto (TV Samsung)"
Cohesion: 0.31
Nodes (7): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung), Catálogo instalado: base + ampliado (9.380 perfis)

### Community 136 - "tcl112.py"
Cohesion: 0.17
Nodes (11): arquivos_cc0(), main(), broadlink(), ErroTcl, estado(), _hex(), main(), perfil() (+3 more)

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 829 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **47 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `normalizar` to `normalizar`, `cli.py`, `Descoberta`, `Sinal`, `criar_servidor`, `servico.py`, `Controlador`, `ServidorMCP`, `test_controle_ir.py`, `ar do quarto (ar-condicionado Gree GWH09KF)`, `Registro`, `Catalogo`, `Execucao`, `Sinal`, `novo_servico`, `_iniciar`, `ErroEmissor`, `Controlador`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.051839464882943144 - nodes in this community are weakly interconnected._
- **Why does `criar_servidor()` connect `criar_servidor` to `cli.py`, `normalizar`, `TestPainel`, `ServidorMCP`, `test_controle_ir.py`, `TestServidorMCP`, `novo_servico`, `Origens`, `_iniciar`, `modulo_embutido`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Should `Descoberta` be split into smaller, more focused modules?**
  _Cohesion score 0.1346153846153846 - nodes in this community are weakly interconnected._
- **Why does `Tunel` connect `Tunel` to `cli.py`, `TestArmacao`, `Problemas já resolvidos (para não repetir)`, `_iniciar`, `time`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._