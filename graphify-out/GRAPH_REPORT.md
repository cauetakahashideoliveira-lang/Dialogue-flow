# Graph Report - Dialogue-flow  (2026-11-23)

## Corpus Check
- 129 files · ~184,326 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 2763 nodes · 6196 edges · 148 communities (92 shown, 56 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 456 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `06c7b58e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- Descoberta
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- _privado
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
- grade
- json
- Catalogo
- protocolos.py
- test_objetivo.py
- TestImagemNoMcp
- Instalador (instalar.sh)
- Tela
- Execucao
- os
- re
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
- servico.py
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
- .executar
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
- vigia.py
- piloto.py
- CLAUDE.md
- Problemas já resolvidos (para não repetir)
- .main
- observador.py
- _iniciar
- bluetooth/principal.py
- BluetoothDevice
- modulo_embutido
- execucao.py
- Bluetooth.java
- Motor
- TestParidadeDoBloqueio
- atualizar_conhecimento.sh
- gree_variante.py
- Grafo
- TestPilotoVisao
- TestLigacaoNoServicoDaTela
- canal.py
- Contribuir com o Dialogue-flow
- Bluetooth
- Piloto
- godmode-tracker.js
- ._laco
- .controlar
- TestServidorMCP
- TestResumoInstrucoes
- ._api
- TestLeitorJava
- _Servidor
- .startScan
- Ar condicionado quarto 2 — Brastemp Clean (protocolo TCL112)
- TestCanal
- AttributionSource
- construir_app_bluetooth.sh script
- ErroEmissor
- Process
- PS4: controle completo e jogador que aprende (capacidade `ps4`, 1.0.109+)
- TestPrincipal
- tela/principal.py
- Origens
- TestFormatos
- termometro/principal.py
- tcl112.py
- .test_memoria_guarda_so_o_caminho_certo_sem_desvios
- TestTermometro
- 4. Mapa de oportunidades
- TestGreeVariante
- Autonomia do planejador no POCO
- fechar_anuncio
- PlanoTest
- scripts
- TestGodModeStmEPontuacao
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
- `3a. Central de Controle (1.0.24, implementada) — `painel/`` --references--> `TestPainel`  [EXTRACTED]
  docs/seguranca.md → testes/test_controle_ir.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (148 total, 56 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.08
Nodes (59): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+51 more)

### Community 1 - "Descoberta"
Cohesion: 0.13
Nodes (3): agora(), Descoberta, ErroDescoberta

### Community 2 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.17
Nodes (12): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade, 8. Próximos experimentos (ordem sugerida) (+4 more)

### Community 3 - "_privado"
Cohesion: 0.17
Nodes (8): analisar_web(), arvore(), andar(), ler_bounds(), regioes(), _privado(), regioes_visuais(), regioes_web()

### Community 4 - "Sinal"
Cohesion: 0.08
Nodes (28): adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos() (+20 more)

### Community 5 - "jogador.py"
Cohesion: 0.05
Nodes (21): agenda(), analisar(), extras(), percentil95(), botao(), ErroComando, executar(), lado() (+13 more)

### Community 6 - "Controlador"
Cohesion: 0.13
Nodes (8): hora_legivel(), Controlador, Etapa, executar(), Plano, normalizar_valor(), valores_equivalentes(), TestControle

### Community 7 - "agir"
Cohesion: 0.07
Nodes (17): achar(), achar_regra(), casas_xadrez(), elementos(), escapar_input_text(), eventos(), _Executor, els_fn() (+9 more)

### Community 9 - "TestSonarFrequencia"
Cohesion: 0.06
Nodes (8): _carregar(), _Resposta, TestDescobrirRedeSemWifi, TestDiagnosticoRede, urlopen(), TestSonarFrequencia, testar(), TestTermometroSemResposta

### Community 10 - "test_controle_ir.py"
Cohesion: 0.09
Nodes (7): resumo_instrucoes(), checksum(), empacotar(), fontes(), verificar(), TestApkAtualizado, TestManifesto

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "painel.py"
Cohesion: 0.12
Nodes (12): painel_cli(), _b64(), estado_valido(), _eventos_novos(), gravar(), _http(), ler(), parear() (+4 more)

### Community 14 - "grade"
Cohesion: 0.09
Nodes (15): aplicar_regras(), els_fn(), _caixa(), calma(), _conflitos(), grade(), _ler_grade(), _modelos_do_teclado() (+7 more)

### Community 15 - "json"
Cohesion: 0.23
Nodes (12): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+4 more)

### Community 16 - "Catalogo"
Cohesion: 0.10
Nodes (12): Catalogo, estado_representativo(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), normalizar_marca(), _unzip() (+4 more)

### Community 17 - "protocolos.py"
Cohesion: 0.16
Nodes (15): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+7 more)

### Community 18 - "test_objetivo.py"
Cohesion: 0.12
Nodes (9): CelularWeb, estado_da_captura(), decidir(), TestObjetivoVisaoEGrafo, dec(), jul(), olh(), olhar() (+1 more)

### Community 19 - "TestImagemNoMcp"
Cohesion: 0.17
Nodes (4): _extrair_imagens(), varrer(), TestImagemNoMcp, TestImagensAninhadas

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 23 - "os"
Cohesion: 0.12
Nodes (16): carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar(), analisar(), comparar() (+8 more)

### Community 24 - "re"
Cohesion: 0.13
Nodes (15): area_cega(), assinatura(), busca(), concluido(), interruptor(), melhor(), no_retangulo(), norm() (+7 more)

### Community 25 - "e2e.cjs"
Cohesion: 0.13
Nodes (11): celular(), { chromium }, { execFileSync, spawn }, filhos, fs, nodeCrypto, os, PASTA (+3 more)

### Community 26 - "f"
Cohesion: 0.13
Nodes (24): agir(), _ajudante(), app_em_foco(), bloqueado(), bloqueados(), _executar(), escolher(), foco() (+16 more)

### Community 27 - "steps"
Cohesion: 0.11
Nodes (17): jobs, pacote, name, on, push, workflow_dispatch, runs-on, steps (+9 more)

### Community 28 - "os"
Cohesion: 0.12
Nodes (18): guardar(), lembrar(), Ajudante, _apagar(), _bloqueio_de_toque(), captura(), dump_ui(), estado_rapido() (+10 more)

### Community 29 - "ps4/principal.py"
Cohesion: 0.14
Nodes (22): cmd_comando(), fundo(), cmd_habilidade(), cmd_jogador(), codificar(), Estado, executar(), _gravar() (+14 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.12
Nodes (19): classificar(), ficha_upnp(), ip_do_wifi(), ler_inventarios(), main(), sondar(), ssdp(), tcp() (+11 more)

### Community 32 - "TestPainel"
Cohesion: 0.09
Nodes (16): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 2. Etapa 0 — armação diária local (1.0.23, implementada), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1) (+8 more)

### Community 33 - "cli.py"
Cohesion: 0.10
Nodes (33): ampliar_catalogo(), _api(), arquivo_boot(), atualizar(), boot_ativado(), caminho_log(), _carimbo_catalogo(), carregar_config() (+25 more)

### Community 34 - "TestPrincipal"
Cohesion: 0.07
Nodes (7): ConexaoFalsa, Gravador, _mod(), TestComandos, TestCompatPyAV, TestConexaoLaco, TestJogador

### Community 35 - "schema.sql"
Cohesion: 0.12
Nodes (15): aparelhos, chamadas, config, convites, credenciais, desafios, estado, eventos (+7 more)

### Community 36 - "servico.py"
Cohesion: 0.10
Nodes (20): Aparelhos, capacidades(), _curto(), ErroAparelho, _faixa_txt(), _linhas_aparelho(), resumo_aparelho(), resumo_compacto() (+12 more)

### Community 37 - "Conexao"
Cohesion: 0.10
Nodes (7): compat_av(), _flag(), video_codec(), Conexao, _ligar_log(), _Memoria, ultimas_linhas()

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
Cohesion: 0.18
Nodes (6): ErroCapacidade, _hash(), _manifesto(), modulo_embutido(), Registro, capacidade_cli()

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 47 - "test_consistencia.py"
Cohesion: 0.11
Nodes (5): _estado_celular(), TestAtualizacaoRecompila, TestEstadoCelularSemProc, TestFerramentasDaMissao, TestResumoSemRepeticao

### Community 48 - ".executar"
Cohesion: 0.15
Nodes (12): Executor, assinar(), cega_de(), fim(), ler_resposta(), regioes(), inteiro(), numerico() (+4 more)

### Community 49 - "Politica"
Cohesion: 0.26
Nodes (3): armar_cli(), Politica, fim_do_dia()

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.26
Nodes (15): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+7 more)

### Community 53 - "Canal"
Cohesion: 0.11
Nodes (3): Canal, _mascarar(), WebSocket

### Community 55 - "HANDOFF.md"
Cohesion: 0.25
Nodes (3): Comparação do planejador de missões no POCO, Rodada, Licenças dos dados de controle

### Community 56 - "modos/principal.py"
Cohesion: 0.09
Nodes (26): Android, aplicar_toque(), aplicar_volume(), atalho(), _avisar(), _chave(), _cond(), definir() (+18 more)

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 58 - "_ferramentas_piloto"
Cohesion: 0.16
Nodes (10): atividade_no_topo(), classe_janela(), em_anuncio(), _ferramentas_piloto(), aguardar(), tabuleiro_local(), tela_chess(), tocar() (+2 more)

### Community 59 - ".anotar"
Cohesion: 0.11
Nodes (5): BluetoothDevice, ScanRecord, ScanResult, ParcelUuid, SparseArray

### Community 60 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+10 more)

### Community 61 - "TestSono"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 62 - "_objetivo"
Cohesion: 0.11
Nodes (16): _json_da_resposta(), _julgar(), julgar(), _modelo_do_nivel(), _objetivo(), abrir(), abrir_url(), aplicar_regras() (+8 more)

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 65 - "Servico"
Cohesion: 0.12
Nodes (5): ErroUso, Servico, Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105), Perfil Gree Unknown (catálogo nº 102), descartado, Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas)

### Community 66 - "CelularFalso"
Cohesion: 0.17
Nodes (3): _carregar(), CelularFalso, TestModos

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 70 - "test_controle_ir.py"
Cohesion: 0.06
Nodes (6): main(), preparar(), TestCanal, TestObservador, TestProtocolos, TestVocabulario

### Community 75 - "criar_servidor"
Cohesion: 0.30
Nodes (12): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), local_ok() (+4 more)

### Community 76 - "Conexao"
Cohesion: 0.24
Nodes (3): carregar_memoria(), Conexao, _texto_do_evento()

### Community 78 - "canal.py"
Cohesion: 0.13
Nodes (6): filtro(), ler_recortes(), main(), reduzir(), validar_recorte(), nome_da_chamada()

### Community 80 - "Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude"
Cohesion: 0.12
Nodes (16): Botão Stockfish para estudos, Capacidades plugáveis (ferramentas novas sem mexer no núcleo), Cobertura dos testes, Como funciona, Conectar ao ChatGPT ou ao Claude, Descoberta, Desenvolvimento, Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude (+8 more)

### Community 81 - "TestVigia"
Cohesion: 0.21
Nodes (3): _carregar(), Relogio, TestVigia

### Community 83 - "vigia.py"
Cohesion: 0.24
Nodes (6): _converter(), disparou(), norm(), numero(), satisfaz(), validar()

### Community 84 - "piloto.py"
Cohesion: 0.11
Nodes (9): caixa_da_pergunta(), calcular(), ev(), escolher_pela_conta(), fen(), gravar_memoria(), minha_cor(), quem_mexeu() (+1 more)

### Community 85 - "CLAUDE.md"
Cohesion: 0.27
Nodes (4): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, empacotar.sh script

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
Cohesion: 0.13
Nodes (12): avisar(), _aviso(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir(), mostrar_url() (+4 more)

### Community 90 - "bluetooth/principal.py"
Cohesion: 0.10
Nodes (20): buscar(), buscar_app(), buscar_shell(), classificar(), compilar(), distancia(), _ler_marca(), ler_pareados_dumpsys() (+12 more)

### Community 92 - "modulo_embutido"
Cohesion: 0.32
Nodes (8): abrir(), configurar(), estudar(), ler_preferencias(), mostrar(), piloto_local(), Preferencias, stockfish_local()

### Community 93 - "execucao.py"
Cohesion: 0.15
Nodes (5): exec_cli(), Autorizacao, classificar(), gerar_segredo(), totp()

### Community 99 - "gree_variante.py"
Cohesion: 0.16
Nodes (13): exportar_jsonl(), Problemas já resolvidos (para não repetir), Versão do servidor (celular 1.0.4, repositório 1.0.5), checksum(), ErroGree, flipper(), gerar(), _indice_espaco() (+5 more)

### Community 104 - "canal.py"
Cohesion: 0.16
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

### Community 108 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

### Community 109 - "._laco"
Cohesion: 0.31
Nodes (3): chave_quiz(), norm(), quiz_da_tela()

### Community 110 - ".controlar"
Cohesion: 0.13
Nodes (20): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50) (+12 more)

### Community 114 - "._api"
Cohesion: 0.25
Nodes (4): ao_texto(), _confianca(), corpo_api(), prompt_quiz()

### Community 115 - "TestLeitorJava"
Cohesion: 0.05
Nodes (7): _carregar(), TestAppAuxiliar, TestBuscarNoCelular, TestClassificacao, TestCompilar, TestLeitorJava, TestTelaDicaDoCampo

### Community 118 - "Ar condicionado quarto 2 — Brastemp Clean (protocolo TCL112)"
Cohesion: 0.22
Nodes (8): Ar condicionado quarto 2 — Brastemp Clean (protocolo TCL112), Como foi identificado (22/11), Formato (TCL112, 2 quadros de 14 bytes, LSB primeiro, 38 kHz), Frases, Parâmetros do perfil, Regenerar o perfil no celular, Ressalvas, Testado no aparelho

### Community 127 - "PS4: controle completo e jogador que aprende (capacidade `ps4`, 1.0.109+)"
Cohesion: 0.29
Nodes (6): Instalação no Termux (uma vez, com o sistema armado), Jogador que aprende (`acao=jogador`), Limites medidos/esperados, Preparo (uma vez), PS4: controle completo e jogador que aprende (capacidade `ps4`, 1.0.109+), Uso

### Community 129 - "tela/principal.py"
Cohesion: 0.08
Nodes (26): _carregar_objetivo(), _chave(), compactos(), _contar(), curto(), dentro(), diferenca(), diferenca_curta() (+18 more)

### Community 135 - "termometro/principal.py"
Cohesion: 0.29
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 136 - "tcl112.py"
Cohesion: 0.17
Nodes (11): arquivos_cc0(), main(), broadlink(), ErroTcl, estado(), _hex(), main(), perfil() (+3 more)

### Community 140 - "4. Mapa de oportunidades"
Cohesion: 0.33
Nodes (6): 4. Mapa de oportunidades, Casa e rede, Celular e Android, Computadores, nuvem e agentes, O próprio sistema, Observar o resultado (agir → medir → ajustar)

### Community 142 - "Autonomia do planejador no POCO"
Cohesion: 0.40
Nodes (5): Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente

### Community 143 - "fechar_anuncio"
Cohesion: 0.40
Nodes (3): _abrir(), botao_fechar(), fechar_anuncio()

### Community 145 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, deploy, dev, test:e2e

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 903 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **56 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `TestPrincipal`, `cli.py`, `Descoberta`, `servico.py`, `Sinal`, `test_controle_ir.py`, `Controlador`, `EmissorSimulado`, `ServidorMCP`, `criar_servidor`, `Registro`, `.controlar`, `Catalogo`, `Execucao`, `TestTela`, `_iniciar`, `ErroEmissor`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.08208955223880597 - nodes in this community are weakly interconnected._
- **Why does `ServidorMCP` connect `ServidorMCP` to `test_controle_ir.py`, `criar_servidor`, `PlanoTest`, `TestResumoInstrucoes`, `TestImagemNoMcp`, `TestTela`, `TestArmacao`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Should `Descoberta` be split into smaller, more focused modules?**
  _Cohesion score 0.12926829268292683 - nodes in this community are weakly interconnected._
- **Why does `TestTelaPorArquivo` connect `TestTelaPorArquivo` to `test_controle_ir.py`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._