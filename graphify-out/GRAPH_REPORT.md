# Graph Report - Dialogue-flow  (2026-11-21)

## Corpus Check
- 110 files · ~145,997 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 2100 nodes · 4793 edges · 122 communities (78 shown, 44 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 355 edges (avg confidence: 0.87)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `0f701616`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- pathlib
- TestPainel
- Conexao
- ErroUso
- analisar.py
- Controlador
- .passo
- Registro
- TestSonarFrequencia
- Politica
- steps
- diagnostico_rede/principal.py
- TestTelaPorArquivo
- pacote.py
- os
- Descoberta
- Sinal
- Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude
- main
- Instalador (instalar.sh)
- Tela
- Pacote do celular dist/controle-ir.zip
- Tunel
- Controlador
- e2e.cjs
- json
- steps
- tela/principal.py
- re
- ErroSinal
- descobrir_rede/principal.py
- Servico
- grade
- termometro/principal.py
- schema.sql
- painel.py
- Execucao
- package.json
- TestOuvirBipe
- sonar/principal.py
- mcp.py
- Sinal
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
- time
- Autonomia do planejador no POCO
- Variante Gree a partir da captura real (troca só os bits)
- TestPiloto
- TestCapacidades
- .anotar
- .test_canal_repassa_chamada_e_aviso
- .controlar
- _iniciar
- Passagem de bastão do Dialogue-flow
- bluetooth/principal.py
- TestGreeVariante
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
- TestGodModeStmEPontuacao
- Problemas já resolvidos (para não repetir)
- ErroUso
- _executar
- PlanoTest
- caminho_log
- Emissor
- TestSono
- godmode-tracker.js
- Ajudante
- estudo_xadrez.py
- .main
- criar_servidor
- TestObservador
- gree_variante.py
- BluetoothDevice
- _Servidor
- servico.py
- TestServidorMCP
- scripts
- novo_servico
- atualizar_conhecimento.sh
- armado
- shutil
- TestParidadeDoBloqueio
- cli.py
- Autonomia do planejador no POCO
- TestExecucao
- Contribuir com o Dialogue-flow
- Bluetooth
- TestProtocolos
- _rodar_bloco
- test_controle_ir.py
- tv do quarto (TV Samsung)
- TestLeitorJava
- Origens
- .startScan
- TestArmacao
- AttributionSource
- ScanCallback
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

## Communities (122 total, 44 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.08
Nodes (59): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+51 more)

### Community 2 - "TestPainel"
Cohesion: 0.09
Nodes (16): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 2. Etapa 0 — armação diária local (1.0.23, implementada), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1) (+8 more)

### Community 5 - "analisar.py"
Cohesion: 0.36
Nodes (5): agenda(), analisar(), extras(), percentil95(), Rodada

### Community 6 - "Controlador"
Cohesion: 0.23
Nodes (4): Etapa, Plano, normalizar_valor(), valores_equivalentes()

### Community 7 - ".passo"
Cohesion: 0.11
Nodes (8): eventos(), _Executor, els_fn(), relevantes(), _Falha, foco(), _Interrompido, sequencia()

### Community 8 - "Registro"
Cohesion: 0.05
Nodes (18): ErroCapacidade, _hash(), _manifesto(), modulo_embutido(), Registro, capacidade_cli(), apps_usando(), _capacidades_rodando() (+10 more)

### Community 9 - "TestSonarFrequencia"
Cohesion: 0.07
Nodes (7): _carregar(), _Resposta, TestDiagnosticoRede, urlopen(), TestSonarFrequencia, testar(), TestTermometroSemResposta

### Community 10 - "Politica"
Cohesion: 0.19
Nodes (8): armar_cli(), _aviso(), exec_cli(), encerrar(), reduzir(), _termux(), Politica, fim_do_dia()

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "diagnostico_rede/principal.py"
Cohesion: 0.36
Nodes (8): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi()

### Community 14 - "pacote.py"
Cohesion: 0.36
Nodes (4): checksum(), empacotar(), fontes(), verificar()

### Community 15 - "os"
Cohesion: 0.18
Nodes (10): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+2 more)

### Community 16 - "Descoberta"
Cohesion: 0.05
Nodes (25): agora(), Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper() (+17 more)

### Community 17 - "Sinal"
Cohesion: 0.18
Nodes (18): adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos() (+10 more)

### Community 18 - "Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude"
Cohesion: 0.12
Nodes (16): Botão Stockfish para estudos, Capacidades plugáveis (ferramentas novas sem mexer no núcleo), Cobertura dos testes, Como funciona, Conectar ao ChatGPT ou ao Claude, Descoberta, Desenvolvimento, Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude (+8 more)

### Community 19 - "main"
Cohesion: 0.23
Nodes (10): _api(), carregar_config(), console(), url_quando_pronta(), estado_servidor(), parar_servico(), _porta_ativa(), _saude() (+2 more)

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 24 - "Controlador"
Cohesion: 0.36
Nodes (3): Controlador, EmissorSimulado, TestControle

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
Cohesion: 0.08
Nodes (25): _chave(), compactos(), _contar(), curto(), dentro(), diferenca(), diferenca_curta(), elementos() (+17 more)

### Community 29 - "re"
Cohesion: 0.11
Nodes (17): achar(), achar_regra(), agir(), aplicar_regras(), els_fn(), bloqueado(), bloqueados(), botao_fechar() (+9 more)

### Community 30 - "ErroSinal"
Cohesion: 0.16
Nodes (9): broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta(), limitar_duracao(), normalizar_pulsos(), pronto_para_pulsos(), pulsos_para_broadlink() (+1 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.16
Nodes (11): classificar(), ficha_upnp(), ip_do_wifi(), ler_inventarios(), main(), sondar(), ssdp(), tcp() (+3 more)

### Community 33 - "grade"
Cohesion: 0.11
Nodes (11): _caixa(), calma(), _conflitos(), grade(), _ler_grade(), _modelos_do_teclado(), _plano(), resolver_grade() (+3 more)

### Community 34 - "termometro/principal.py"
Cohesion: 0.19
Nodes (10): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia() (+2 more)

### Community 35 - "schema.sql"
Cohesion: 0.12
Nodes (15): aparelhos, chamadas, config, convites, credenciais, desafios, estado, eventos (+7 more)

### Community 36 - "painel.py"
Cohesion: 0.12
Nodes (12): painel_cli(), _b64(), estado_valido(), _eventos_novos(), gravar(), _http(), ler(), parear() (+4 more)

### Community 38 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+10 more)

### Community 40 - "sonar/principal.py"
Cohesion: 0.22
Nodes (9): analisar_sonar(), escolher_e_testar(), frequencia_lembrada(), gerar_tom(), lembrar(), main(), sugestao_sem_tom(), testar() (+1 more)

### Community 41 - "mcp.py"
Cohesion: 0.10
Nodes (6): resumo_para_instrucoes(), resumo_instrucoes(), _extrair_imagens(), varrer(), TestImagensAninhadas, TestResumoInstrucoes

### Community 42 - "Sinal"
Cohesion: 0.20
Nodes (3): ler_sinal_texto(), Sinal, TestFormatos

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
Cohesion: 0.24
Nodes (6): consultar_modelo(), contexto(), escolher(), executar(), planejar(), RespostaDePlanoInvalida

### Community 49 - "exec_cli"
Cohesion: 0.14
Nodes (4): Autorizacao, classificar(), gerar_segredo(), totp()

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
Cohesion: 0.10
Nodes (3): Canal, _mascarar(), WebSocket

### Community 54 - "time"
Cohesion: 0.14
Nodes (18): _abrir(), _ajudante(), _apagar(), captura(), dump_ui(), estado_rapido(), fechar_anuncio(), tocar() (+10 more)

### Community 55 - "Autonomia do planejador no POCO"
Cohesion: 0.20
Nodes (4): Comparação do planejador de missões no POCO, Contexto para o Claude Code, Skill graphify (query, explain, path, update), Licenças dos dados de controle

### Community 56 - "Variante Gree a partir da captura real (troca só os bits)"
Cohesion: 0.21
Nodes (6): Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50), Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105), Perfil Gree Unknown (catálogo nº 102), descartado, Problemas já resolvidos (para não repetir), Versão do servidor (celular 1.0.4, repositório 1.0.5)

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 59 - ".anotar"
Cohesion: 0.13
Nodes (4): ScanRecord, ScanResult, ParcelUuid, SparseArray

### Community 61 - ".controlar"
Cohesion: 0.21
Nodes (13): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Ligar/desligar diretos (energia_ligar 0x99, energia_desligar 0x98), Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper) (+5 more)

### Community 62 - "_iniciar"
Cohesion: 0.26
Nodes (5): _iniciar(), ao_mudar_url(), gravar_estado(), mostrar_url(), Notificador

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 64 - "bluetooth/principal.py"
Cohesion: 0.17
Nodes (11): buscar(), classificar(), compilar(), distancia(), guardar(), ler_pareados_dumpsys(), main(), pareados_rapido() (+3 more)

### Community 66 - "f"
Cohesion: 0.15
Nodes (9): filtro(), ler_recortes(), main(), reduzir(), validar_recorte(), gravar(), progresso_txt(), f() (+1 more)

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
Cohesion: 0.16
Nodes (8): chave_quiz(), fen(), gravar_memoria(), norm(), quem_mexeu(), quiz_da_tela(), tabuleiro_txt(), _texto_do_evento()

### Community 77 - "Problemas já resolvidos (para não repetir)"
Cohesion: 0.17
Nodes (15): Anúncio dos testes (v1.0.1), Catálogo instalado: base + ampliado (9.380 perfis), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026) (+7 more)

### Community 79 - "_executar"
Cohesion: 0.11
Nodes (16): atividade_no_topo(), casas_xadrez(), classe_janela(), em_anuncio(), _executar(), escolher(), foto(), _ferramentas_piloto() (+8 more)

### Community 81 - "caminho_log"
Cohesion: 0.20
Nodes (6): caminho_log(), iniciar_em_segundo_plano(), mostrar_log(), _redirecionar_para_log(), _registrar(), _seguir_log()

### Community 82 - "Emissor"
Cohesion: 0.22
Nodes (3): relatar_uso(), Emissor, EmissorTermux

### Community 83 - "TestSono"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 84 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

### Community 86 - "estudo_xadrez.py"
Cohesion: 0.32
Nodes (8): abrir(), configurar(), estudar(), ler_preferencias(), mostrar(), piloto_local(), Preferencias, stockfish_local()

### Community 87 - ".main"
Cohesion: 0.18
Nodes (4): ScanSettings, Builder, Handler, Looper

### Community 88 - "criar_servidor"
Cohesion: 0.27
Nodes (13): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), local_ok() (+5 more)

### Community 90 - "gree_variante.py"
Cohesion: 0.23
Nodes (10): checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main(), perfil() (+2 more)

### Community 93 - "servico.py"
Cohesion: 0.18
Nodes (8): capacidades(), _curto(), _faixa_txt(), hora_legivel(), _linhas_aparelho(), resumo_aparelho(), executar(), ErroEmissor

### Community 94 - "TestServidorMCP"
Cohesion: 0.17
Nodes (3): julgar_depois(), Reenvios, TestServidorMCP

### Community 96 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, deploy, dev, test:e2e

### Community 97 - "novo_servico"
Cohesion: 0.09
Nodes (5): catalogo_base(), novo_servico(), TestCatalogo, TestTela, TestTermometro

### Community 100 - "shutil"
Cohesion: 0.35
Nodes (6): carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar()

### Community 102 - "cli.py"
Cohesion: 0.14
Nodes (18): ampliar_catalogo(), arquivo_boot(), atualizar(), boot_ativado(), _carimbo_catalogo(), catalogo_atual(), _cfg_caminho(), criar_atalhos() (+10 more)

### Community 103 - "Autonomia do planejador no POCO"
Cohesion: 0.40
Nodes (5): Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente

### Community 105 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

### Community 108 - "_rodar_bloco"
Cohesion: 0.40
Nodes (3): app_em_foco(), _bloqueio_de_toque(), _rodar_bloco()

### Community 110 - "tv do quarto (TV Samsung)"
Cohesion: 0.52
Nodes (6): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung)

### Community 114 - "TestLeitorJava"
Cohesion: 0.08
Nodes (5): _carregar(), TestBuscarNoCelular, TestClassificacao, TestLeitorJava, TestTelaDicaDoCampo

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 678 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **44 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `ErroUso`, `Controlador`, `Registro`, `Descoberta`, `Sinal`, `Controlador`, `ErroSinal`, `Execucao`, `mcp.py`, `Sinal`, `_iniciar`, `ServidorMCP`, `ErroUso`, `criar_servidor`, `servico.py`, `TestServidorMCP`, `novo_servico`, `cli.py`, `test_controle_ir.py`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.08208955223880597 - nodes in this community are weakly interconnected._
- **Why does `Execucao` connect `Execucao` to `Servico`, `TestExecucao`, `Descoberta`, `exec_cli`, `servico.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Should `TestPainel` be split into smaller, more focused modules?**
  _Cohesion score 0.0896551724137931 - nodes in this community are weakly interconnected._
- **Why does `TestTelaPorArquivo` connect `TestTelaPorArquivo` to `test_controle_ir.py`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._