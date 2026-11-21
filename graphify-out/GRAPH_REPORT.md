# Graph Report - Dialogue-flow  (2026-11-21)

## Corpus Check
- 110 files · ~147,010 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 2120 nodes · 4805 edges · 124 communities (76 shown, 48 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 357 edges (avg confidence: 0.87)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `85360db0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- pathlib
- TestPainel
- Conexao
- normalizar
- analisar.py
- Controlador
- .passo
- Servico
- TestSonarFrequencia
- Politica
- steps
- diagnostico_rede/principal.py
- TestTelaPorArquivo
- Catalogo
- os
- Descoberta
- Sinal
- Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude
- capacidades.py
- Instalador (instalar.sh)
- Tela
- Execucao
- Tunel
- TestSegundoPlano
- e2e.cjs
- json
- steps
- tela/principal.py
- grade
- Sinal
- descobrir_rede/principal.py
- gree_variante.py
- .aplicar_reflexo
- termometro/principal.py
- schema.sql
- painel.py
- re
- package.json
- TestOuvirBipe
- sonar/principal.py
- _extrair_imagens
- observador.py
- test_god_mode.py
- protocolos.py
- webauthn.js
- session-start.sh
- TestTunel
- ambiente_missao.py
- exec_cli
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- autorizar.js
- app.js
- Canal
- Ajudante
- Autonomia do planejador no POCO
- ParcelUuid
- TestPiloto
- TestCapacidades
- .anotar
- .test_canal_repassa_chamada_e_aviso
- tv do quarto (TV Samsung)
- _iniciar
- Passagem de bastão do Dialogue-flow
- .decidir
- TestSonar
- f
- local.cjs
- test_consistencia.py
- ._api
- piloto.py
- ServidorMCP
- Cerebros
- BluetoothAdapter
- Piloto
- Motor
- verificar_cliente_mcp.py
- Problemas já resolvidos (para não repetir)
- normalizar
- f
- PlanoTest
- resolver_grade
- android.bluetooth.le.ScanResult
- TestImagemNoMcp
- godmode-tracker.js
- pacote.py
- modulo_embutido
- .main
- Autonomia do planejador no POCO
- TestObservador
- bluetooth/principal.py
- BluetoothDevice
- _Servidor
- servico.py
- criar_servidor
- scripts
- TestTela
- atualizar_conhecimento.sh
- TestTermometro
- shutil
- TestParidadeDoBloqueio
- cli.py
- Fluxo para criar um botão novo (gerar, enviar_sinal, perguntar, salvar)
- atualizar
- Contribuir com o Dialogue-flow
- Bluetooth
- TestProtocolos
- catalogo_base
- test_controle_ir.py
- Macro abrir Netflix (inicio_3 + ok)
- TestSono
- resumo_para_instrucoes
- Pacote do celular dist/controle-ir.zip
- TestLeitorJava
- novo_servico
- .startScan
- AttributionSource
- Process

## God Nodes (most connected - your core abstractions)
1. `Servico` - 63 edges
2. `Sinal` - 39 edges
3. `main()` - 38 edges
4. `Tela` - 37 edges
5. `Descoberta` - 37 edges
6. `TestTelaPorArquivo` - 36 edges
7. `Catalogo` - 35 edges
8. `criar_servidor()` - 31 edges
9. `f()` - 30 edges
10. `_iniciar()` - 28 edges

## Surprising Connections (you probably didn't know these)
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `ampliar_catalogo()`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/cli.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper)` --conceptually_related_to--> `ler_flipper()`  [INFERRED]
  docs/aparelhos/README.md → controle-ir/controle_ir/formatos.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (124 total, 48 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.08
Nodes (59): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+51 more)

### Community 1 - "pathlib"
Cohesion: 0.13
Nodes (3): preparar(), TestManifesto, TestGodModeStmEPontuacao

### Community 2 - "TestPainel"
Cohesion: 0.10
Nodes (15): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono (+7 more)

### Community 4 - "normalizar"
Cohesion: 0.14
Nodes (13): Aparelhos, ErroAparelho, chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar(), sem_acentos() (+5 more)

### Community 5 - "analisar.py"
Cohesion: 0.38
Nodes (4): agenda(), analisar(), extras(), percentil95()

### Community 6 - "Controlador"
Cohesion: 0.16
Nodes (7): Controlador, Etapa, Plano, EmissorSimulado, normalizar_valor(), valores_equivalentes(), TestControle

### Community 7 - ".passo"
Cohesion: 0.10
Nodes (9): achar(), achar_regra(), compactos(), eventos(), _Executor, relevantes(), _Falha, _Interrompido (+1 more)

### Community 8 - "Servico"
Cohesion: 0.12
Nodes (4): ErroUso, Servico, 2. Etapa 0 — armação diária local (1.0.23, implementada), TestDescoberta

### Community 9 - "TestSonarFrequencia"
Cohesion: 0.06
Nodes (8): _carregar(), _Resposta, TestDescobrirRedeSemWifi, TestDiagnosticoRede, urlopen(), TestSonarFrequencia, testar(), TestTermometroSemResposta

### Community 10 - "Politica"
Cohesion: 0.26
Nodes (3): armar_cli(), Politica, fim_do_dia()

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "diagnostico_rede/principal.py"
Cohesion: 0.40
Nodes (8): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi()

### Community 14 - "Catalogo"
Cohesion: 0.13
Nodes (11): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), _unzip() (+3 more)

### Community 15 - "os"
Cohesion: 0.18
Nodes (10): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+2 more)

### Community 16 - "Descoberta"
Cohesion: 0.13
Nodes (3): agora(), Descoberta, ErroDescoberta

### Community 17 - "Sinal"
Cohesion: 0.14
Nodes (19): adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos() (+11 more)

### Community 18 - "Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude"
Cohesion: 0.12
Nodes (16): Botão Stockfish para estudos, Capacidades plugáveis (ferramentas novas sem mexer no núcleo), Cobertura dos testes, Como funciona, Conectar ao ChatGPT ou ao Claude, Descoberta, Desenvolvimento, Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude (+8 more)

### Community 19 - "capacidades.py"
Cohesion: 0.19
Nodes (5): ErroCapacidade, _hash(), _manifesto(), Registro, capacidade_cli()

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 24 - "TestSegundoPlano"
Cohesion: 0.07
Nodes (13): modulo_embutido(), apps_usando(), _capacidades_rodando(), em_uso(), quadro(), recursos_do_comando(), _tarefas(), _tela() (+5 more)

### Community 25 - "e2e.cjs"
Cohesion: 0.13
Nodes (11): celular(), { chromium }, { execFileSync, spawn }, filhos, fs, nodeCrypto, os, PASTA (+3 more)

### Community 26 - "json"
Cohesion: 0.21
Nodes (12): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+4 more)

### Community 27 - "steps"
Cohesion: 0.11
Nodes (17): jobs, pacote, name, on, push, workflow_dispatch, runs-on, steps (+9 more)

### Community 28 - "tela/principal.py"
Cohesion: 0.09
Nodes (31): gravar_memoria(), _ajudante(), _apagar(), app_em_foco(), _bloqueio_de_toque(), captura(), _chave(), _contar() (+23 more)

### Community 29 - "grade"
Cohesion: 0.08
Nodes (19): _abrir(), atividade_no_topo(), botao_fechar(), casas_xadrez(), classe_janela(), elementos(), em_anuncio(), foto() (+11 more)

### Community 30 - "Sinal"
Cohesion: 0.09
Nodes (11): broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta(), limitar_duracao(), normalizar_pulsos(), pronto_para_pulsos(), pulsos_para_broadlink() (+3 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.16
Nodes (11): classificar(), ficha_upnp(), ip_do_wifi(), ler_inventarios(), main(), sondar(), ssdp(), tcp() (+3 more)

### Community 32 - "gree_variante.py"
Cohesion: 0.23
Nodes (10): checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main(), perfil() (+2 more)

### Community 33 - ".aplicar_reflexo"
Cohesion: 0.13
Nodes (10): aplicar_regras(), els_fn(), calma(), els_fn(), tocar(), _injetar(), _modelos_do_teclado(), regra_vale() (+2 more)

### Community 34 - "termometro/principal.py"
Cohesion: 0.32
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 35 - "schema.sql"
Cohesion: 0.12
Nodes (15): aparelhos, chamadas, config, convites, credenciais, desafios, estado, eventos (+7 more)

### Community 36 - "painel.py"
Cohesion: 0.12
Nodes (12): painel_cli(), _b64(), estado_valido(), _eventos_novos(), gravar(), _http(), ler(), parear() (+4 more)

### Community 37 - "re"
Cohesion: 0.15
Nodes (5): janela_nova(), _regex_bloqueados(), tabuleiro_curto(), vez_no_historico(), classificar()

### Community 38 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+10 more)

### Community 40 - "sonar/principal.py"
Cohesion: 0.23
Nodes (8): analisar_sonar(), escolher_e_testar(), frequencia_lembrada(), gerar_tom(), main(), sugestao_sem_tom(), testar(), volume_musica()

### Community 41 - "_extrair_imagens"
Cohesion: 0.22
Nodes (3): _extrair_imagens(), varrer(), TestImagensAninhadas

### Community 42 - "observador.py"
Cohesion: 0.18
Nodes (4): relatar_uso(), Emissor, EmissorTermux, ErroEmissor

### Community 43 - "test_god_mode.py"
Cohesion: 0.11
Nodes (5): _Base, _ComServidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos

### Community 44 - "protocolos.py"
Cohesion: 0.13
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 48 - "ambiente_missao.py"
Cohesion: 0.17
Nodes (7): consultar_modelo(), contexto(), executar(), planejar(), RespostaDePlanoInvalida, armado(), permitido()

### Community 49 - "exec_cli"
Cohesion: 0.11
Nodes (5): exec_cli(), Autorizacao, gerar_segredo(), totp(), TestExecucao

### Community 50 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.11
Nodes (18): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+10 more)

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.26
Nodes (15): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+7 more)

### Community 53 - "Canal"
Cohesion: 0.13
Nodes (3): Canal, _mascarar(), WebSocket

### Community 55 - "Autonomia do planejador no POCO"
Cohesion: 0.26
Nodes (3): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Licenças dos dados de controle

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 59 - ".anotar"
Cohesion: 0.17
Nodes (3): ScanRecord, ScanResult, SparseArray

### Community 61 - "tv do quarto (TV Samsung)"
Cohesion: 0.13
Nodes (20): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50) (+12 more)

### Community 62 - "_iniciar"
Cohesion: 0.18
Nodes (9): _aviso(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir(), mostrar_url(), _termux() (+1 more)

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 64 - ".decidir"
Cohesion: 0.39
Nodes (3): chave_quiz(), norm(), quiz_da_tela()

### Community 66 - "f"
Cohesion: 0.27
Nodes (5): filtro(), ler_recortes(), main(), reduzir(), validar_recorte()

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 68 - "test_consistencia.py"
Cohesion: 0.11
Nodes (5): _estado_celular(), TestAtualizacaoRecompila, TestEstadoCelularSemProc, TestFerramentasDaMissao, TestResumoSemRepeticao

### Community 69 - "._api"
Cohesion: 0.22
Nodes (5): ao_texto(), _confianca(), corpo_api(), ler_chave(), prompt_quiz()

### Community 70 - "piloto.py"
Cohesion: 0.17
Nodes (5): fen(), minha_cor(), quem_mexeu(), tabuleiro_txt(), _texto_do_evento()

### Community 71 - "ServidorMCP"
Cohesion: 0.15
Nodes (3): resumo_instrucoes(), ServidorMCP, TestArmacao

### Community 77 - "Problemas já resolvidos (para não repetir)"
Cohesion: 0.17
Nodes (16): Anúncio dos testes (v1.0.1), Catálogo instalado: base + ampliado (9.380 perfis), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026) (+8 more)

### Community 79 - "f"
Cohesion: 0.10
Nodes (26): guardar(), lembrar(), agir(), bloqueado(), bloqueados(), executar(), _executar(), escolher() (+18 more)

### Community 81 - "resolver_grade"
Cohesion: 0.25
Nodes (5): _caixa(), _conflitos(), resolver_grade(), busca(), resolver_sudoku()

### Community 84 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

### Community 86 - "modulo_embutido"
Cohesion: 0.42
Nodes (7): abrir(), configurar(), estudar(), ler_preferencias(), mostrar(), piloto_local(), Preferencias

### Community 87 - ".main"
Cohesion: 0.19
Nodes (4): ScanSettings, Builder, Handler, Looper

### Community 88 - "Autonomia do planejador no POCO"
Cohesion: 0.22
Nodes (7): Comparação do planejador de missões no POCO, Rodada, Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente

### Community 90 - "bluetooth/principal.py"
Cohesion: 0.11
Nodes (15): buscar(), classificar(), compilar(), distancia(), ler_pareados_dumpsys(), ler_registro(), main(), pareados_rapido() (+7 more)

### Community 93 - "servico.py"
Cohesion: 0.17
Nodes (7): capacidades(), _curto(), _faixa_txt(), hora_legivel(), _linhas_aparelho(), resumo_aparelho(), executar()

### Community 94 - "criar_servidor"
Cohesion: 0.09
Nodes (17): julgar_depois(), criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json() (+9 more)

### Community 96 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, deploy, dev, test:e2e

### Community 100 - "shutil"
Cohesion: 0.36
Nodes (6): carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar()

### Community 102 - "cli.py"
Cohesion: 0.10
Nodes (32): ampliar_catalogo(), _api(), arquivo_boot(), boot_ativado(), caminho_log(), _carimbo_catalogo(), carregar_config(), catalogo_atual() (+24 more)

### Community 105 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

### Community 110 - "Macro abrir Netflix (inicio_3 + ok)"
Cohesion: 0.67
Nodes (4): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Smart Hub 0x79 (tecla inicio_3), Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas)

### Community 115 - "TestLeitorJava"
Cohesion: 0.06
Nodes (6): _carregar(), TestBuscarNoCelular, TestClassificacao, TestCompilar, TestLeitorJava, TestTelaDicaDoCampo

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 688 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **48 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TestPiloto` connect `TestPiloto` to `test_controle_ir.py`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.08208955223880597 - nodes in this community are weakly interconnected._
- **Why does `Servico` connect `Servico` to `pathlib`, `normalizar`, `Controlador`, `Catalogo`, `Descoberta`, `Sinal`, `capacidades.py`, `Execucao`, `Sinal`, `_extrair_imagens`, `observador.py`, `_iniciar`, `ServidorMCP`, `servico.py`, `criar_servidor`, `cli.py`, `Fluxo para criar um botão novo (gerar, enviar_sinal, perguntar, salvar)`, `test_controle_ir.py`, `novo_servico`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Should `pathlib` be split into smaller, more focused modules?**
  _Cohesion score 0.13230769230769232 - nodes in this community are weakly interconnected._
- **Why does `TestPainel` connect `TestPainel` to `Descoberta`, `test_controle_ir.py`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._