# Graph Report - Dialogue-flow  (2026-11-21)

## Corpus Check
- 113 files · ~149,029 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 2170 nodes · 4926 edges · 129 communities (75 shown, 54 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 364 edges (avg confidence: 0.87)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `0a8e7ac5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- json
- TestPainel
- Conexao
- normalizar
- analisar.py
- Controlador
- .passo
- modulo_embutido
- TestSonarFrequencia
- Politica
- steps
- diagnostico_rede/principal.py
- TestTelaPorArquivo
- Catalogo
- os
- Servico
- Sinal
- Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude
- capacidades.py
- Instalador (instalar.sh)
- Tela
- fechar_anuncio
- Tunel
- TestSegundoPlano
- e2e.cjs
- json
- steps
- rish
- elementos
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
- os
- CLAUDE.md
- hashlib
- TestPiloto
- TestCapacidades
- .anotar
- .test_canal_repassa_chamada_e_aviso
- ar do quarto (ar-condicionado Gree GWH09KF)
- _iniciar
- Passagem de bastão do Dialogue-flow
- Notificador
- novo_servico
- f
- local.cjs
- TestEstadoCelularSemProc
- ._api
- piloto.py
- ServidorMCP
- Cerebros
- BluetoothAdapter
- Piloto
- Motor
- TestArmacao
- Problemas já resolvidos (para não repetir)
- TestGreeVariante
- f
- PlanoTest
- tela/principal.py
- android.bluetooth.le.ScanResult
- godmode-tracker.js
- TestResumoSemRepeticao
- modulo_embutido
- Looper
- Autonomia do planejador no POCO
- TestObservador
- bluetooth/principal.py
- BluetoothClass
- _Servidor
- Aparelhos
- criar_servidor
- Bluetooth.java
- scripts
- TestTela
- atualizar_conhecimento.sh
- TestTermometro
- shutil
- TestParidadeDoBloqueio
- cli.py
- ar do escritório (ar-condicionado Carrier)
- atualizar
- Contribuir com o Dialogue-flow
- Bluetooth
- TestProtocolos
- catalogo_base
- canal.py
- tv do quarto (TV Samsung)
- TestSono
- TestAtualizacaoRecompila
- TestVocabulario
- TestLeitorJava
- TestGodModeStmEPontuacao
- .startScan
- TestFerramentasDaMissao
- TestRepositorio
- AttributionSource
- construir_app_bluetooth.sh script
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
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
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

## Communities (129 total, 54 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.08
Nodes (59): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+51 more)

### Community 1 - "json"
Cohesion: 0.07
Nodes (10): capacidades(), _curto(), _faixa_txt(), _linhas_aparelho(), resumo_aparelho(), resumo_para_instrucoes(), main(), preparar() (+2 more)

### Community 2 - "TestPainel"
Cohesion: 0.09
Nodes (16): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 2. Etapa 0 — armação diária local (1.0.23, implementada), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1) (+8 more)

### Community 4 - "normalizar"
Cohesion: 0.15
Nodes (10): normalizar_marca(), categoria_canonica(), chaves_de_teste(), normalizar(), _por_regex(), _registrar(), sem_acentos(), _t() (+2 more)

### Community 5 - "analisar.py"
Cohesion: 0.38
Nodes (4): agenda(), analisar(), extras(), percentil95()

### Community 6 - "Controlador"
Cohesion: 0.09
Nodes (11): Controlador, Etapa, executar(), Plano, Emissor, EmissorSimulado, EmissorTermux, ErroEmissor (+3 more)

### Community 7 - ".passo"
Cohesion: 0.08
Nodes (15): achar(), achar_regra(), casas_xadrez(), eventos(), _Executor, els_fn(), relevantes(), foto() (+7 more)

### Community 9 - "TestSonarFrequencia"
Cohesion: 0.06
Nodes (8): _carregar(), _Resposta, TestDescobrirRedeSemWifi, TestDiagnosticoRede, urlopen(), TestSonarFrequencia, testar(), TestTermometroSemResposta

### Community 10 - "Politica"
Cohesion: 0.20
Nodes (3): armar_cli(), Politica, fim_do_dia()

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "diagnostico_rede/principal.py"
Cohesion: 0.40
Nodes (8): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi()

### Community 14 - "Catalogo"
Cohesion: 0.15
Nodes (10): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), _unzip() (+2 more)

### Community 15 - "os"
Cohesion: 0.18
Nodes (10): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+2 more)

### Community 16 - "Servico"
Cohesion: 0.06
Nodes (8): agora(), Descoberta, ErroDescoberta, classificar(), Execucao, Servico, termo_por_chave(), TestDescoberta

### Community 17 - "Sinal"
Cohesion: 0.12
Nodes (21): adicionar_comando(), comando(), ErroFormato, exportar(), _hex_le(), importar_texto(), indice_comandos(), ler_flipper() (+13 more)

### Community 18 - "Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude"
Cohesion: 0.12
Nodes (16): Botão Stockfish para estudos, Capacidades plugáveis (ferramentas novas sem mexer no núcleo), Cobertura dos testes, Como funciona, Conectar ao ChatGPT ou ao Claude, Descoberta, Desenvolvimento, Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude (+8 more)

### Community 19 - "capacidades.py"
Cohesion: 0.15
Nodes (5): ErroCapacidade, _hash(), _manifesto(), Registro, capacidade_cli()

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 22 - "fechar_anuncio"
Cohesion: 0.18
Nodes (8): _abrir(), calma(), classe_janela(), dentro(), em_anuncio(), fechar_anuncio(), tabuleiro_curto(), _ver_depois()

### Community 24 - "TestSegundoPlano"
Cohesion: 0.24
Nodes (3): TestSegundoPlano, abrir_console(), reiniciado()

### Community 25 - "e2e.cjs"
Cohesion: 0.13
Nodes (11): celular(), { chromium }, { execFileSync, spawn }, filhos, fs, nodeCrypto, os, PASTA (+3 more)

### Community 26 - "json"
Cohesion: 0.21
Nodes (12): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+4 more)

### Community 27 - "steps"
Cohesion: 0.11
Nodes (17): jobs, pacote, name, on, push, workflow_dispatch, runs-on, steps (+9 more)

### Community 28 - "rish"
Cohesion: 0.15
Nodes (12): _ajudante(), app_em_foco(), _bloqueio_de_toque(), dump_ui(), estado_rapido(), historico(), _ler(), observar() (+4 more)

### Community 29 - "elementos"
Cohesion: 0.27
Nodes (7): atividade_no_topo(), elementos(), _ferramentas_piloto(), aguardar(), tabuleiro_local(), tela_chess(), partida_contra_robo()

### Community 30 - "Sinal"
Cohesion: 0.09
Nodes (16): escrever_flipper(), sinal(), _sinal_smartir(), nome_canonico(), broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta() (+8 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.16
Nodes (11): classificar(), ficha_upnp(), ip_do_wifi(), ler_inventarios(), main(), sondar(), ssdp(), tcp() (+3 more)

### Community 32 - "gree_variante.py"
Cohesion: 0.23
Nodes (10): checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main(), perfil() (+2 more)

### Community 33 - ".aplicar_reflexo"
Cohesion: 0.16
Nodes (8): aplicar_regras(), els_fn(), tocar(), _injetar(), _modelos_do_teclado(), regra_vale(), teclado_da_grade(), _teclado_parado()

### Community 34 - "termometro/principal.py"
Cohesion: 0.29
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 35 - "schema.sql"
Cohesion: 0.12
Nodes (15): aparelhos, chamadas, config, convites, credenciais, desafios, estado, eventos (+7 more)

### Community 36 - "painel.py"
Cohesion: 0.12
Nodes (12): painel_cli(), _b64(), estado_valido(), _eventos_novos(), gravar(), _http(), ler(), parear() (+4 more)

### Community 37 - "re"
Cohesion: 0.15
Nodes (10): botao_fechar(), reflexos(), _regex_bloqueados(), _regras(), _resumo_volta(), rotina(), gravar(), _rotinas() (+2 more)

### Community 38 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+10 more)

### Community 40 - "sonar/principal.py"
Cohesion: 0.22
Nodes (9): analisar_sonar(), escolher_e_testar(), frequencia_lembrada(), gerar_tom(), lembrar(), main(), sugestao_sem_tom(), testar() (+1 more)

### Community 41 - "_extrair_imagens"
Cohesion: 0.40
Nodes (3): _extrair_imagens(), varrer(), TestImagensAninhadas

### Community 42 - "observador.py"
Cohesion: 0.19
Nodes (8): relatar_uso(), apps_usando(), _capacidades_rodando(), em_uso(), quadro(), recursos_do_comando(), _tarefas(), _tela()

### Community 43 - "test_god_mode.py"
Cohesion: 0.11
Nodes (5): _Base, _ComServidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos

### Community 44 - "protocolos.py"
Cohesion: 0.16
Nodes (14): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+6 more)

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 48 - "ambiente_missao.py"
Cohesion: 0.17
Nodes (8): consultar_modelo(), contexto(), escolher(), executar(), planejar(), RespostaDePlanoInvalida, armado(), permitido()

### Community 49 - "exec_cli"
Cohesion: 0.13
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

### Community 54 - "os"
Cohesion: 0.22
Nodes (7): Ajudante, _apagar(), captura(), foto_rapida(), _jar(), _jpeg(), _pasta_troca()

### Community 56 - "hashlib"
Cohesion: 0.23
Nodes (6): fontes(), impressao(), checksum(), empacotar(), fontes(), verificar()

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 59 - ".anotar"
Cohesion: 0.10
Nodes (5): BluetoothDevice, ScanRecord, ScanResult, ParcelUuid, SparseArray

### Community 61 - "ar do quarto (ar-condicionado Gree GWH09KF)"
Cohesion: 0.22
Nodes (8): Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50), Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105), Perfil Gree Unknown (catálogo nº 102), descartado, Ligar/desligar diretos (energia_ligar 0x99, energia_desligar 0x98)

### Community 62 - "_iniciar"
Cohesion: 0.23
Nodes (11): _aviso(), iniciar(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir(), mostrar_url() (+3 more)

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 66 - "f"
Cohesion: 0.17
Nodes (7): filtro(), ler_recortes(), main(), reduzir(), validar_recorte(), arquivos_cc0(), main()

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 69 - "._api"
Cohesion: 0.22
Nodes (5): ao_texto(), _confianca(), corpo_api(), ler_chave(), prompt_quiz()

### Community 70 - "piloto.py"
Cohesion: 0.13
Nodes (9): chave_quiz(), fen(), gravar_memoria(), minha_cor(), norm(), quem_mexeu(), quiz_da_tela(), tabuleiro_txt() (+1 more)

### Community 71 - "ServidorMCP"
Cohesion: 0.11
Nodes (4): resumo_instrucoes(), ServidorMCP, TestImagemNoMcp, TestResumoInstrucoes

### Community 77 - "Problemas já resolvidos (para não repetir)"
Cohesion: 0.14
Nodes (17): Pacote do celular dist/controle-ir.zip, Anúncio dos testes (v1.0.1), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026) (+9 more)

### Community 79 - "f"
Cohesion: 0.19
Nodes (14): agir(), bloqueado(), bloqueados(), _executar(), escolher(), foco(), grade(), _modulo_piloto() (+6 more)

### Community 81 - "tela/principal.py"
Cohesion: 0.08
Nodes (20): _caixa(), _chave(), compactos(), _conflitos(), _contar(), curto(), diferenca(), diferenca_curta() (+12 more)

### Community 84 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

### Community 86 - "modulo_embutido"
Cohesion: 0.47
Nodes (6): abrir(), configurar(), estudar(), ler_preferencias(), mostrar(), Preferencias

### Community 88 - "Autonomia do planejador no POCO"
Cohesion: 0.16
Nodes (8): Comparação do planejador de missões no POCO, Rodada, Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente, Licenças dos dados de controle

### Community 90 - "bluetooth/principal.py"
Cohesion: 0.11
Nodes (19): buscar(), buscar_app(), buscar_shell(), classificar(), compilar(), distancia(), guardar(), _ler_marca() (+11 more)

### Community 93 - "Aparelhos"
Cohesion: 0.20
Nodes (3): Aparelhos, ErroAparelho, hora_legivel()

### Community 94 - "criar_servidor"
Cohesion: 0.09
Nodes (16): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), local_ok() (+8 more)

### Community 96 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, deploy, dev, test:e2e

### Community 100 - "shutil"
Cohesion: 0.24
Nodes (6): carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar()

### Community 102 - "cli.py"
Cohesion: 0.10
Nodes (31): ampliar_catalogo(), _api(), arquivo_boot(), boot_ativado(), caminho_log(), _carimbo_catalogo(), carregar_config(), catalogo_atual() (+23 more)

### Community 103 - "ar do escritório (ar-condicionado Carrier)"
Cohesion: 0.31
Nodes (8): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Cômodo: Escritório, Cômodo: Laboratório, Cômodo: Quarto, Índice de aparelhos (cômodo → aparelho → controle), Aparelhos salvos

### Community 105 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

### Community 106 - "Bluetooth"
Cohesion: 0.15
Nodes (5): Runnable, Bluetooth, Runnable, ScanSettings, Builder

### Community 110 - "tv do quarto (TV Samsung)"
Cohesion: 0.43
Nodes (7): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung), Catálogo instalado: base + ampliado (9.380 perfis)

### Community 115 - "TestLeitorJava"
Cohesion: 0.05
Nodes (7): _carregar(), TestAppAuxiliar, TestBuscarNoCelular, TestClassificacao, TestCompilar, TestLeitorJava, TestTelaDicaDoCampo

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 698 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **54 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `json`, `TestPainel`, `novo_servico`, `normalizar`, `cli.py`, `ServidorMCP`, `Controlador`, `Catalogo`, `Sinal`, `capacidades.py`, `Sinal`, `criar_servidor`, `Aparelhos`, `_iniciar`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.08208955223880597 - nodes in this community are weakly interconnected._
- **Why does `TestPiloto` connect `TestPiloto` to `json`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Should `json` be split into smaller, more focused modules?**
  _Cohesion score 0.06734867860187553 - nodes in this community are weakly interconnected._
- **Why does `Execucao` connect `Servico` to `json`, `exec_cli`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._