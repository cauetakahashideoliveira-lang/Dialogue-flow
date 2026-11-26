# Graph Report - Dialogue-flow  (2026-11-26)

## Corpus Check
- 137 files · ~190,566 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 2768 nodes · 6298 edges · 158 communities (91 shown, 67 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 486 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `85d51a4f`
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
- subprocess
- re
- e2e.cjs
- nome_da_chamada
- steps
- tela/principal.py
- Controlador
- Tunel
- descobrir_rede/principal.py
- .executar
- cli.py
- godmode-tracker.js
- Tarefas
- formatos.py
- piloto.py
- broadlink_para_pulsos
- TestOuvirBipe
- os
- ServidorMCP
- TestSegundoPlano
- test_god_mode.py
- Registro
- webauthn.js
- session-start.sh
- TestEstadoCelularSemProc
- Execucao
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- test_agente_pc.py
- autorizar.js
- app.js
- Canal
- TestTela
- analisar.py
- modos/principal.py
- TestPiloto
- ver
- .anotar
- ErroEmissor
- TestSono
- _objetivo
- Passagem de bastão do Dialogue-flow
- rish
- Servico
- CelularFalso
- local.cjs
- TestAgentePC
- test_objetivo.py
- servico.py
- vigia.py
- Piloto
- BluetoothAdapter
- TestTermometro
- _privado
- TestArmacao
- TestRegioesWeb
- scripts
- Celular
- Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude
- TestVigia
- android.bluetooth.le.ScanResult
- TestProtocolos
- PlanoTest
- TestObservador
- Problemas já resolvidos (para não repetir)
- Looper
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
- TestLeitorJava
- _Servidor
- .startScan
- agente_pc/cli.py
- Origens
- AttributionSource
- construir_app_bluetooth.sh script
- TestServidorMCP
- Process
- elementos
- ServidorMCP
- f
- tv do quarto (TV Samsung)
- Cerebros
- atualizar
- tcl112.py
- .test_memoria_guarda_so_o_caminho_certo_sem_desvios
- Motor
- abrir
- Sinal
- .visao
- Aparelhos
- hashlib
- Conexao
- Grafo
- ._laco
- Canal
- criar_servidor
- PC na Central de Controle (agente do PC)
- pacote.py
- .test_atualizar_sem_ref_sai_do_head_destacado
- unicodedata

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
- `Regressões: cada erro vira um teste` --references--> `CanalPC`  [INFERRED]
  docs/regressoes.md → pc/agente_pc/cli.py
- `PC na Central de Controle (agente do PC)` --references--> `verificar_requisicao()`  [INFERRED]
  docs/pc.md → controle-ir/controle_ir/painel.py
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (158 total, 67 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.08
Nodes (65): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+57 more)

### Community 1 - "Descoberta"
Cohesion: 0.07
Nodes (17): agora(), Descoberta, ErroDescoberta, criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS() (+9 more)

### Community 2 - "TestPainel"
Cohesion: 0.10
Nodes (15): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono (+7 more)

### Community 4 - "Sinal"
Cohesion: 0.10
Nodes (10): broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta(), normalizar_pulsos(), pronto_para_pulsos(), pulsos_para_broadlink(), _quadros() (+2 more)

### Community 5 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+10 more)

### Community 6 - "Controlador"
Cohesion: 0.21
Nodes (4): Etapa, Plano, normalizar_valor(), valores_equivalentes()

### Community 7 - "agir"
Cohesion: 0.08
Nodes (15): achar(), achar_regra(), els_fn(), casas_xadrez(), compactos(), eventos(), _Executor, els_fn() (+7 more)

### Community 9 - "TestSonarFrequencia"
Cohesion: 0.06
Nodes (8): _carregar(), _Resposta, TestDescobrirRedeSemWifi, TestDiagnosticoRede, urlopen(), TestSonarFrequencia, testar(), TestTermometroSemResposta

### Community 10 - "test_controle_ir.py"
Cohesion: 0.07
Nodes (6): hora_legivel(), executar(), main(), preparar(), TestApkAtualizado, TestManifesto

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "painel.py"
Cohesion: 0.05
Nodes (19): exec_cli(), painel_cli(), Autorizacao, gerar_segredo(), Politica, totp(), _b64(), estado_valido() (+11 more)

### Community 14 - "ligar"
Cohesion: 0.13
Nodes (10): CanalPC, estado(), ligar(), reduzir(), log(), manter_acordado(), gravar(), ler() (+2 more)

### Community 15 - "json"
Cohesion: 0.14
Nodes (20): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+12 more)

### Community 16 - "Catalogo"
Cohesion: 0.10
Nodes (15): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), normalizar_marca() (+7 more)

### Community 17 - "protocolos.py"
Cohesion: 0.15
Nodes (15): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+7 more)

### Community 18 - "test_objetivo.py"
Cohesion: 0.14
Nodes (7): CelularWeb, decidir(), TestObjetivoVisaoEGrafo, dec(), olh(), olhar(), web()

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

### Community 23 - "subprocess"
Cohesion: 0.29
Nodes (5): filtro(), ler_recortes(), main(), reduzir(), validar_recorte()

### Community 24 - "re"
Cohesion: 0.15
Nodes (14): area_cega(), busca(), concluido(), interruptor(), melhor(), no_retangulo(), norm(), palavras() (+6 more)

### Community 25 - "e2e.cjs"
Cohesion: 0.13
Nodes (11): celular(), { chromium }, { execFileSync, spawn }, filhos, fs, nodeCrypto, os, PASTA (+3 more)

### Community 27 - "steps"
Cohesion: 0.11
Nodes (17): jobs, pacote, name, on, push, workflow_dispatch, runs-on, steps (+9 more)

### Community 28 - "tela/principal.py"
Cohesion: 0.06
Nodes (26): botao_fechar(), _caixa(), _carregar_objetivo(), _chave(), classe_janela(), _conflitos(), _contar(), dentro() (+18 more)

### Community 29 - "Controlador"
Cohesion: 0.22
Nodes (4): Controlador, EmissorSimulado, TestControle, TestDescoberta

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.09
Nodes (21): classificar(), ficha_upnp(), ip_do_wifi(), ler_inventarios(), main(), sondar(), ssdp(), tcp() (+13 more)

### Community 32 - ".executar"
Cohesion: 0.13
Nodes (13): assinatura(), Executor, assinar(), cega_de(), fim(), ler_resposta(), regioes(), inteiro() (+5 more)

### Community 33 - "cli.py"
Cohesion: 0.14
Nodes (26): ampliar_catalogo(), _api(), armar_cli(), arquivo_boot(), boot_ativado(), _carimbo_catalogo(), carregar_config(), catalogo_atual() (+18 more)

### Community 34 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

### Community 35 - "Tarefas"
Cohesion: 0.14
Nodes (4): decodificar(), preparar(), _sem_janela(), Tarefas

### Community 36 - "formatos.py"
Cohesion: 0.13
Nodes (24): adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos() (+16 more)

### Community 37 - "piloto.py"
Cohesion: 0.12
Nodes (8): calcular(), ev(), escolher_pela_conta(), fen(), minha_cor(), quem_mexeu(), tabuleiro_txt(), _texto_do_evento()

### Community 40 - "os"
Cohesion: 0.07
Nodes (28): guardar(), carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar(), analisar() (+20 more)

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

### Community 49 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.11
Nodes (18): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+10 more)

### Community 50 - "test_agente_pc.py"
Cohesion: 0.13
Nodes (4): _resultado(), varrer(), rodar_ps(), b64u()

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.26
Nodes (15): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+7 more)

### Community 53 - "Canal"
Cohesion: 0.10
Nodes (3): Canal, _mascarar(), WebSocket

### Community 55 - "analisar.py"
Cohesion: 0.15
Nodes (11): agenda(), analisar(), extras(), percentil95(), Comparação do planejador de missões no POCO, Rodada, Autonomia do planejador no POCO, Dados e reprodução (+3 more)

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
Cohesion: 0.10
Nodes (5): BluetoothDevice, ScanRecord, ScanResult, ParcelUuid, SparseArray

### Community 60 - "ErroEmissor"
Cohesion: 0.20
Nodes (3): Emissor, EmissorTermux, ErroEmissor

### Community 61 - "TestSono"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 62 - "_objetivo"
Cohesion: 0.09
Nodes (21): escolher(), _json_da_resposta(), _julgar(), julgar(), _modelo_do_nivel(), _modulo_piloto(), _objetivo(), abrir() (+13 more)

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 64 - "rish"
Cohesion: 0.13
Nodes (15): _abrir(), app_em_foco(), _bloqueio_de_toque(), dump_ui(), _eh_inicio(), estado_rapido(), tocar(), _ler() (+7 more)

### Community 65 - "Servico"
Cohesion: 0.14
Nodes (4): ErroUso, Servico, Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas), 2. Etapa 0 — armação diária local (1.0.23, implementada)

### Community 66 - "CelularFalso"
Cohesion: 0.17
Nodes (3): _carregar(), CelularFalso, TestModos

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 69 - "test_objetivo.py"
Cohesion: 0.29
Nodes (3): _carregar(), estado_da_captura(), TestAreaCegaComTeclado

### Community 70 - "servico.py"
Cohesion: 0.15
Nodes (8): capacidades(), _curto(), _faixa_txt(), _linhas_aparelho(), resumo_aparelho(), resumo_compacto(), resumo_para_instrucoes(), resumo_instrucoes()

### Community 71 - "vigia.py"
Cohesion: 0.14
Nodes (8): _converter(), disparou(), norm(), numero(), satisfaz(), validar(), Vigias, laco()

### Community 75 - "_privado"
Cohesion: 0.12
Nodes (11): analisar_web(), arvore(), andar(), historico(), _janela_curta(), ler_bounds(), _linha_do_tempo(), regioes() (+3 more)

### Community 78 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, deploy, dev, test:e2e

### Community 80 - "Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude"
Cohesion: 0.12
Nodes (16): Botão Stockfish para estudos, Capacidades plugáveis (ferramentas novas sem mexer no núcleo), Cobertura dos testes, Como funciona, Conectar ao ChatGPT ou ao Claude, Descoberta, Desenvolvimento, Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude (+8 more)

### Community 81 - "TestVigia"
Cohesion: 0.21
Nodes (3): _carregar(), Relogio, TestVigia

### Community 86 - "Problemas já resolvidos (para não repetir)"
Cohesion: 0.17
Nodes (15): Anúncio dos testes (v1.0.1), Catálogo instalado: base + ampliado (9.380 perfis), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026) (+7 more)

### Community 88 - "observador.py"
Cohesion: 0.16
Nodes (10): modulo_embutido(), relatar_uso(), _retomar_vigias(), apps_usando(), _capacidades_rodando(), em_uso(), quadro(), recursos_do_comando() (+2 more)

### Community 89 - "_iniciar"
Cohesion: 0.21
Nodes (12): avisar(), _aviso(), iniciar(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir() (+4 more)

### Community 90 - "bluetooth/principal.py"
Cohesion: 0.14
Nodes (15): buscar(), buscar_app(), classificar(), distancia(), _ler_marca(), ler_pareados_dumpsys(), main(), _marcar() (+7 more)

### Community 92 - "modulo_embutido"
Cohesion: 0.42
Nodes (5): configurar(), estudar(), ler_preferencias(), mostrar(), Preferencias

### Community 93 - "Ferramentas"
Cohesion: 0.14
Nodes (4): _caminho(), Ferramentas, escapar_sendkeys(), Tela

### Community 99 - "gree_variante.py"
Cohesion: 0.23
Nodes (10): checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main(), perfil() (+2 more)

### Community 104 - "ambiente_missao.py"
Cohesion: 0.18
Nodes (7): consultar_modelo(), contexto(), executar(), planejar(), RespostaDePlanoInvalida, armado(), permitido()

### Community 105 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

### Community 106 - "Bluetooth"
Cohesion: 0.15
Nodes (5): Runnable, Bluetooth, Runnable, ScanSettings, Builder

### Community 107 - "Variante Gree a partir da captura real (troca só os bits)"
Cohesion: 0.15
Nodes (7): Pacote do celular dist/controle-ir.zip, Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105), Perfil Gree Unknown (catálogo nº 102), descartado, Problemas já resolvidos (para não repetir), Versão do servidor (celular 1.0.4, repositório 1.0.5), empacotar.sh script

### Community 110 - ".controlar"
Cohesion: 0.19
Nodes (13): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50), Ligar/desligar diretos (energia_ligar 0x99, energia_desligar 0x98) (+5 more)

### Community 111 - "sistema.py"
Cohesion: 0.20
Nodes (11): cpu_uso(), discos(), _em_cache(), ligado_ha(), memoria(), nvidia(), placas_windows(), processador() (+3 more)

### Community 115 - "TestLeitorJava"
Cohesion: 0.05
Nodes (7): _carregar(), TestAppAuxiliar, TestBuscarNoCelular, TestClassificacao, TestCompilar, TestLeitorJava, TestTelaDicaDoCampo

### Community 118 - "agente_pc/cli.py"
Cohesion: 0.14
Nodes (6): arquivos_cc0(), main(), desligar(), main(), parear(), TestFerramentasDaMissao

### Community 125 - "TestServidorMCP"
Cohesion: 0.17
Nodes (3): julgar_depois(), Reenvios, TestServidorMCP

### Community 127 - "elementos"
Cohesion: 0.15
Nodes (10): atividade_no_topo(), elementos(), _ferramentas_piloto(), aguardar(), tabuleiro_local(), tela_chess(), partida_contra_robo(), teclado_da_grade() (+2 more)

### Community 129 - "f"
Cohesion: 0.12
Nodes (24): agir(), _ajudante(), aplicar_regras(), bloqueado(), bloqueados(), calma(), em_anuncio(), _executar() (+16 more)

### Community 133 - "tv do quarto (TV Samsung)"
Cohesion: 0.52
Nodes (6): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung)

### Community 136 - "tcl112.py"
Cohesion: 0.13
Nodes (17): Ar condicionado quarto 2 — Brastemp Clean (protocolo TCL112), Como foi identificado (22/11), Formato (TCL112, 2 quadros de 14 bytes, LSB primeiro, 38 kHz), Frases, Parâmetros do perfil, Regenerar o perfil no celular, Ressalvas, Testado no aparelho (+9 more)

### Community 140 - "abrir"
Cohesion: 0.15
Nodes (8): caminho_log(), iniciar_em_segundo_plano(), pasta_atalhos(), _redirecionar_para_log(), _registrar(), _seguir_log(), abrir(), piloto_local()

### Community 141 - "Sinal"
Cohesion: 0.23
Nodes (4): sinal(), impressao_protocolo(), limitar_duracao(), Sinal

### Community 142 - ".visao"
Cohesion: 0.18
Nodes (5): ao_texto(), _confianca(), corpo_api(), ler_chave(), prompt_quiz()

### Community 144 - "hashlib"
Cohesion: 0.22
Nodes (5): buscar_shell(), compilar(), ler_registro(), fontes(), impressao()

### Community 147 - "._laco"
Cohesion: 0.31
Nodes (3): chave_quiz(), norm(), quiz_da_tela()

### Community 149 - "criar_servidor"
Cohesion: 0.28
Nodes (4): criar_servidor(), do_GET(), do_POST(), _json()

### Community 150 - "PC na Central de Controle (agente do PC)"
Cohesion: 0.25
Nodes (7): Ferramentas, Instalar no PC, Limites, Manter ligado, PC na Central de Controle (agente do PC), Religar o PC e o botão "Ligar Agente PC", Testes

### Community 151 - "pacote.py"
Cohesion: 0.36
Nodes (4): checksum(), empacotar(), fontes(), verificar()

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 881 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **67 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Regressões: cada erro vira um teste` connect `Canal` to `TestParidadeDoBloqueio`, `ligar`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.08198757763975155 - nodes in this community are weakly interconnected._
- **Why does `Canal` connect `Canal` to `index.js`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Should `Descoberta` be split into smaller, more focused modules?**
  _Cohesion score 0.07451923076923077 - nodes in this community are weakly interconnected._
- **Why does `CanalPC` connect `ligar` to `Canal`, `agente_pc/cli.py`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._