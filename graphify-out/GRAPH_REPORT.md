# Graph Report - Dialogue-flow  (2026-11-21)

## Corpus Check
- 115 files · ~156,771 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 2278 nodes · 5154 edges · 141 communities (80 shown, 61 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 394 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `8f8a3086`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- TestGodModeStmEPontuacao
- TestPainel
- Conexao
- normalizar
- shutil
- Controlador
- .passo
- Celular
- TestSonarFrequencia
- sys
- steps
- canal.py
- TestTelaPorArquivo
- servico.py
- subprocess
- Descoberta
- Sinal
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- os
- Instalador (instalar.sh)
- Tela
- ErroUso
- subprocess
- objetivo.py
- e2e.cjs
- json
- steps
- tela/principal.py
- Registro
- tv do quarto (TV Samsung)
- descobrir_rede/principal.py
- gree_variante.py
- Execucao
- Catalogo
- schema.sql
- formatos.py
- Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude
- package.json
- TestOuvirBipe
- sonar/principal.py
- ServidorMCP
- diagnostico_rede/principal.py
- test_god_mode.py
- protocolos.py
- webauthn.js
- session-start.sh
- Origens
- ambiente_missao.py
- caminho_log
- exec_cli
- autorizar.js
- app.js
- Canal
- Servico
- HANDOFF.md
- termometro/principal.py
- TestPiloto
- _jar
- .anotar
- TestSono
- construir_catalogo.py
- Passagem de bastão do Dialogue-flow
- Politica
- TestServidorMCP
- criar_servidor
- local.cjs
- TestExecucao
- piloto.py
- TestStockfishLocal
- diagnostico_rede/principal.py
- Cerebros
- BluetoothAdapter
- Piloto
- Motor
- TestArmacao
- observador.py
- emissor.py
- _ajudante
- TestSegundoPlano
- EmissorSimulado
- android.bluetooth.le.ScanResult
- _iniciar
- PlanoTest
- Sincronizador
- modulo_embutido
- Looper
- cli.py
- TestObservador
- bluetooth/principal.py
- BluetoothClass
- _Servidor
- resumo_para_instrucoes
- Bluetooth.java
- TestCapacidades
- novo_servico
- atualizar_conhecimento.sh
- Estado atual da instalação (17/11/2026)
- godmode-tracker.js
- TestParidadeDoBloqueio
- Autonomia do planejador no POCO
- Reenvios
- test_consistencia.py
- Contribuir com o Dialogue-flow
- Bluetooth
- TestProtocolos
- Notificador
- tv do quarto (TV Samsung)
- TestLeitorJava
- Tunel
- resolver_grade
- test_controle_ir.py
- TestBuscarNoCelular
- capacidades.py
- .startScan
- TestAppAuxiliar
- scripts
- AttributionSource
- construir_app_bluetooth.sh script
- TestClassificacao
- Process
- re
- TestTunel
- rish
- TestImagemNoMcp
- TestGreeVariante
- _carregar
- Pacote do celular dist/controle-ir.zip
- _linhas_do_passo
- TestTelaDicaDoCampo
- TestRepositorio
- abrir_console

## God Nodes (most connected - your core abstractions)
1. `Servico` - 62 edges
2. `main()` - 38 edges
3. `Tela` - 37 edges
4. `Descoberta` - 37 edges
5. `Sinal` - 37 edges
6. `TestTelaPorArquivo` - 36 edges
7. `Celular` - 36 edges
8. `Catalogo` - 35 edges
9. `f()` - 34 edges
10. `criar_servidor()` - 31 edges

## Surprising Connections (you probably didn't know these)
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py
- `Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper)` --conceptually_related_to--> `ler_flipper()`  [INFERRED]
  docs/aparelhos/README.md → controle-ir/controle_ir/formatos.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `ampliar_catalogo()`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/cli.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (141 total, 61 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.08
Nodes (59): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+51 more)

### Community 2 - "TestPainel"
Cohesion: 0.09
Nodes (15): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono (+7 more)

### Community 3 - "Conexao"
Cohesion: 0.18
Nodes (5): carregar_memoria(), ao_texto(), Conexao, _confianca(), _texto_do_evento()

### Community 4 - "normalizar"
Cohesion: 0.17
Nodes (11): normalizar_marca(), categoria_canonica(), chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar(), sem_acentos() (+3 more)

### Community 5 - "shutil"
Cohesion: 0.36
Nodes (6): carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar()

### Community 6 - "Controlador"
Cohesion: 0.15
Nodes (6): Controlador, Etapa, Plano, normalizar_valor(), valores_equivalentes(), TestControle

### Community 7 - ".passo"
Cohesion: 0.09
Nodes (10): achar(), achar_regra(), compactos(), eventos(), _Executor, relevantes(), _Falha, _Interrompido (+2 more)

### Community 8 - "Celular"
Cohesion: 0.08
Nodes (6): _carregar(), Celular, el(), TestExecutorObjetivo, decidir(), escolher()

### Community 9 - "TestSonarFrequencia"
Cohesion: 0.06
Nodes (8): _carregar(), _Resposta, TestDescobrirRedeSemWifi, TestDiagnosticoRede, urlopen(), TestSonarFrequencia, testar(), TestTermometroSemResposta

### Community 10 - "sys"
Cohesion: 0.10
Nodes (4): main(), preparar(), TestApkAtualizado, TestManifesto

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "canal.py"
Cohesion: 0.20
Nodes (11): painel_cli(), _b64(), estado_valido(), _eventos_novos(), gravar(), _http(), ler(), parear() (+3 more)

### Community 14 - "servico.py"
Cohesion: 0.15
Nodes (8): capacidades(), _curto(), ErroAparelho, _faixa_txt(), hora_legivel(), _linhas_aparelho(), resumo_aparelho(), executar()

### Community 15 - "subprocess"
Cohesion: 0.18
Nodes (10): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+2 more)

### Community 16 - "Descoberta"
Cohesion: 0.13
Nodes (4): agora(), Descoberta, ErroDescoberta, termo_por_chave()

### Community 17 - "Sinal"
Cohesion: 0.10
Nodes (12): broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta(), impressao_protocolo(), limitar_duracao(), normalizar_pulsos(), pronto_para_pulsos() (+4 more)

### Community 18 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.11
Nodes (18): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+10 more)

### Community 19 - "os"
Cohesion: 0.13
Nodes (22): guardar(), lembrar(), gravar_memoria(), bloqueado(), bloqueados(), _executar(), escolher(), _modulo_piloto() (+14 more)

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 22 - "ErroUso"
Cohesion: 0.18
Nodes (4): Aparelhos, slug(), Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper), Versão do servidor (celular 1.0.4, repositório 1.0.5)

### Community 23 - "subprocess"
Cohesion: 0.27
Nodes (5): filtro(), ler_recortes(), main(), reduzir(), validar_recorte()

### Community 24 - "objetivo.py"
Cohesion: 0.11
Nodes (16): assinatura(), busca(), concluido(), Executor, fim(), interruptor(), melhor(), norm() (+8 more)

### Community 25 - "e2e.cjs"
Cohesion: 0.13
Nodes (11): celular(), { chromium }, { execFileSync, spawn }, filhos, fs, nodeCrypto, os, PASTA (+3 more)

### Community 26 - "json"
Cohesion: 0.23
Nodes (12): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+4 more)

### Community 27 - "steps"
Cohesion: 0.11
Nodes (17): jobs, pacote, name, on, push, workflow_dispatch, runs-on, steps (+9 more)

### Community 28 - "tela/principal.py"
Cohesion: 0.09
Nodes (21): _chave(), curto(), diferenca(), diferenca_curta(), elementos(), executar(), historico(), _janela_curta() (+13 more)

### Community 29 - "Registro"
Cohesion: 0.20
Nodes (5): ErroCapacidade, _hash(), _manifesto(), Registro, capacidade_cli()

### Community 30 - "tv do quarto (TV Samsung)"
Cohesion: 0.15
Nodes (16): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50) (+8 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.16
Nodes (11): classificar(), ficha_upnp(), ip_do_wifi(), ler_inventarios(), main(), sondar(), ssdp(), tcp() (+3 more)

### Community 32 - "gree_variante.py"
Cohesion: 0.22
Nodes (10): checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main(), perfil() (+2 more)

### Community 34 - "Catalogo"
Cohesion: 0.13
Nodes (9): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), _unzip() (+1 more)

### Community 35 - "schema.sql"
Cohesion: 0.12
Nodes (15): aparelhos, chamadas, config, convites, credenciais, desafios, estado, eventos (+7 more)

### Community 36 - "formatos.py"
Cohesion: 0.17
Nodes (18): adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos() (+10 more)

### Community 37 - "Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude"
Cohesion: 0.12
Nodes (16): Botão Stockfish para estudos, Capacidades plugáveis (ferramentas novas sem mexer no núcleo), Cobertura dos testes, Como funciona, Conectar ao ChatGPT ou ao Claude, Descoberta, Desenvolvimento, Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude (+8 more)

### Community 38 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+10 more)

### Community 40 - "sonar/principal.py"
Cohesion: 0.23
Nodes (8): analisar_sonar(), escolher_e_testar(), frequencia_lembrada(), gerar_tom(), main(), sugestao_sem_tom(), testar(), volume_musica()

### Community 42 - "diagnostico_rede/principal.py"
Cohesion: 0.20
Nodes (4): agenda(), analisar(), extras(), percentil95()

### Community 43 - "test_god_mode.py"
Cohesion: 0.11
Nodes (5): _Base, _ComServidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos

### Community 44 - "protocolos.py"
Cohesion: 0.17
Nodes (15): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+7 more)

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 48 - "ambiente_missao.py"
Cohesion: 0.18
Nodes (7): consultar_modelo(), contexto(), executar(), planejar(), RespostaDePlanoInvalida, armado(), permitido()

### Community 49 - "caminho_log"
Cohesion: 0.20
Nodes (6): caminho_log(), iniciar_em_segundo_plano(), mostrar_log(), _redirecionar_para_log(), _registrar(), _seguir_log()

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

### Community 54 - "Servico"
Cohesion: 0.15
Nodes (3): ErroUso, Servico, 2. Etapa 0 — armação diária local (1.0.23, implementada)

### Community 55 - "HANDOFF.md"
Cohesion: 0.26
Nodes (3): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Licenças dos dados de controle

### Community 56 - "termometro/principal.py"
Cohesion: 0.29
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 58 - "_jar"
Cohesion: 0.24
Nodes (6): Ajudante, _apagar(), captura(), foto_rapida(), _jar(), _pasta_troca()

### Community 59 - ".anotar"
Cohesion: 0.10
Nodes (5): BluetoothDevice, ScanRecord, ScanResult, ParcelUuid, SparseArray

### Community 61 - "TestSono"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 66 - "criar_servidor"
Cohesion: 0.30
Nodes (12): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), local_ok() (+4 more)

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 69 - "piloto.py"
Cohesion: 0.15
Nodes (7): chave_quiz(), fen(), minha_cor(), norm(), quem_mexeu(), quiz_da_tela(), tabuleiro_txt()

### Community 71 - "diagnostico_rede/principal.py"
Cohesion: 0.36
Nodes (8): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi()

### Community 72 - "Cerebros"
Cohesion: 0.15
Nodes (4): Cerebros, corpo_api(), ler_chave(), prompt_quiz()

### Community 77 - "observador.py"
Cohesion: 0.19
Nodes (8): relatar_uso(), apps_usando(), _capacidades_rodando(), em_uso(), quadro(), recursos_do_comando(), _tarefas(), _tela()

### Community 78 - "emissor.py"
Cohesion: 0.20
Nodes (3): Emissor, EmissorTermux, ErroEmissor

### Community 79 - "_ajudante"
Cohesion: 0.10
Nodes (19): _abrir(), _ajudante(), aplicar_regras(), els_fn(), calma(), _contar(), dentro(), els_fn() (+11 more)

### Community 83 - "_iniciar"
Cohesion: 0.21
Nodes (14): _aviso(), console(), url_quando_pronta(), estado_servidor(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado() (+6 more)

### Community 86 - "modulo_embutido"
Cohesion: 0.24
Nodes (9): modulo_embutido(), abrir(), configurar(), estudar(), ler_preferencias(), mostrar(), piloto_local(), Preferencias (+1 more)

### Community 88 - "cli.py"
Cohesion: 0.12
Nodes (25): ampliar_catalogo(), _api(), armar_cli(), arquivo_boot(), atualizar(), boot_ativado(), _carimbo_catalogo(), carregar_config() (+17 more)

### Community 90 - "bluetooth/principal.py"
Cohesion: 0.08
Nodes (24): buscar(), buscar_app(), buscar_shell(), classificar(), compilar(), distancia(), _ler_marca(), ler_pareados_dumpsys() (+16 more)

### Community 97 - "novo_servico"
Cohesion: 0.08
Nodes (5): catalogo_base(), novo_servico(), TestCatalogo, TestTela, TestTermometro

### Community 99 - "Estado atual da instalação (17/11/2026)"
Cohesion: 0.17
Nodes (16): Anúncio dos testes (v1.0.1), Catálogo instalado: base + ampliado (9.380 perfis), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026) (+8 more)

### Community 100 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

### Community 102 - "Autonomia do planejador no POCO"
Cohesion: 0.22
Nodes (7): Comparação do planejador de missões no POCO, Rodada, Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente

### Community 104 - "test_consistencia.py"
Cohesion: 0.11
Nodes (5): _estado_celular(), TestAtualizacaoRecompila, TestEstadoCelularSemProc, TestFerramentasDaMissao, TestResumoSemRepeticao

### Community 105 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

### Community 106 - "Bluetooth"
Cohesion: 0.15
Nodes (5): Runnable, Bluetooth, Runnable, ScanSettings, Builder

### Community 109 - "tv do quarto (TV Samsung)"
Cohesion: 0.43
Nodes (7): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung), Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas)

### Community 113 - "resolver_grade"
Cohesion: 0.25
Nodes (5): _caixa(), _conflitos(), resolver_grade(), busca(), resolver_sudoku()

### Community 116 - "capacidades.py"
Cohesion: 0.20
Nodes (4): resumo_instrucoes(), _extrair_imagens(), varrer(), TestImagensAninhadas

### Community 119 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, deploy, dev, test:e2e

### Community 127 - "re"
Cohesion: 0.11
Nodes (15): atividade_no_topo(), botao_fechar(), casas_xadrez(), classe_janela(), em_anuncio(), foto(), _ferramentas_piloto(), aguardar() (+7 more)

### Community 129 - "rish"
Cohesion: 0.14
Nodes (13): agir(), app_em_foco(), _bloqueio_de_toque(), dump_ui(), estado_rapido(), _ler(), observar(), rish() (+5 more)

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 738 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **61 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `Execucao`, `Catalogo`, `criar_servidor`, `novo_servico`, `Controlador`, `ServidorMCP`, `sys`, `servico.py`, `emissor.py`, `Descoberta`, `Sinal`, `test_controle_ir.py`, `_iniciar`, `capacidades.py`, `EmissorSimulado`, `ErroUso`, `cli.py`, `Registro`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.08208955223880597 - nodes in this community are weakly interconnected._
- **Why does `Catalogo` connect `Catalogo` to `Estado atual da instalação (17/11/2026)`, `normalizar`, `servico.py`, `Descoberta`, `Sinal`, `_iniciar`, `Servico`, `cli.py`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Should `TestPainel` be split into smaller, more focused modules?**
  _Cohesion score 0.09359605911330049 - nodes in this community are weakly interconnected._
- **Why does `TestSonarFrequencia` connect `TestSonarFrequencia` to `sys`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._