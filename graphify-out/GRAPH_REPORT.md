# Graph Report - Dialogue-flow  (2026-11-21)

## Corpus Check
- 115 files · ~153,086 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 2245 nodes · 5058 edges · 129 communities (75 shown, 54 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 384 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `3db1f5e1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- json
- criar_servidor
- Conexao
- normalizar
- Servico
- Controlador
- .passo
- Celular
- TestSonarFrequencia
- Politica
- steps
- canal.py
- TestTelaPorArquivo
- Catalogo
- os
- Descoberta
- Sinal
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- Registro
- Instalador (instalar.sh)
- Tela
- grade
- Tunel
- objetivo.py
- e2e.cjs
- json
- steps
- time
- Execucao
- ErroEmissor
- descobrir_rede/principal.py
- gree_variante.py
- json
- exec_cli
- schema.sql
- painel.py
- re
- package.json
- TestOuvirBipe
- sonar/principal.py
- TestImagemNoMcp
- carregar_config
- test_god_mode.py
- protocolos.py
- webauthn.js
- session-start.sh
- Sincronizador
- ambiente_missao.py
- TestExecucao
- TestCanal
- autorizar.js
- app.js
- Canal
- os
- HANDOFF.md
- hashlib
- TestPiloto
- TestCapacidades
- .anotar
- construir_catalogo.py
- ar do quarto (ar-condicionado Gree GWH09KF)
- _iniciar
- Passagem de bastão do Dialogue-flow
- Notificador
- resumo_para_instrucoes
- main
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
- tela/principal.py
- PlanoTest
- resolver_grade
- android.bluetooth.le.ScanResult
- .decidir
- godmode-tracker.js
- TestResumoSemRepeticao
- modulo_embutido
- Looper
- TestObservador
- bluetooth/principal.py
- BluetoothClass
- _Servidor
- Aparelhos
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
- armado
- tv do quarto (TV Samsung)
- TestSono
- TestAtualizacaoRecompila
- TestVocabulario
- TestLeitorJava
- TestGodModeStmEPontuacao
- .startScan
- TestFerramentasDaMissao
- AttributionSource
- construir_app_bluetooth.sh script
- Process
- CLAUDE.md

## God Nodes (most connected - your core abstractions)
1. `Servico` - 62 edges
2. `main()` - 38 edges
3. `Tela` - 37 edges
4. `Descoberta` - 37 edges
5. `Sinal` - 37 edges
6. `TestTelaPorArquivo` - 36 edges
7. `Catalogo` - 35 edges
8. `f()` - 32 edges
9. `criar_servidor()` - 31 edges
10. `_iniciar()` - 28 edges

## Surprising Connections (you probably didn't know these)
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
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
Cohesion: 0.06
Nodes (10): capacidades(), _curto(), _faixa_txt(), _linhas_aparelho(), resumo_aparelho(), resumo_instrucoes(), main(), preparar() (+2 more)

### Community 2 - "criar_servidor"
Cohesion: 0.05
Nodes (30): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), local_ok() (+22 more)

### Community 4 - "normalizar"
Cohesion: 0.17
Nodes (17): comando(), importar_texto(), ler_smartir(), novo_perfil(), _traduz(), categoria_canonica(), chaves_de_teste(), interpretar() (+9 more)

### Community 5 - "Servico"
Cohesion: 0.12
Nodes (5): EmissorSimulado, ErroUso, Servico, Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas), TestDescoberta

### Community 6 - "Controlador"
Cohesion: 0.14
Nodes (8): hora_legivel(), Controlador, Etapa, executar(), Plano, normalizar_valor(), valores_equivalentes(), TestControle

### Community 7 - ".passo"
Cohesion: 0.10
Nodes (9): compactos(), eventos(), _Executor, els_fn(), relevantes(), _Falha, foco(), _Interrompido (+1 more)

### Community 8 - "Celular"
Cohesion: 0.12
Nodes (6): _carregar(), Celular, el(), TestExecutorObjetivo, decidir(), escolher()

### Community 9 - "TestSonarFrequencia"
Cohesion: 0.06
Nodes (8): _carregar(), _Resposta, TestDescobrirRedeSemWifi, TestDiagnosticoRede, urlopen(), TestSonarFrequencia, testar(), TestTermometroSemResposta

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "canal.py"
Cohesion: 0.15
Nodes (6): filtro(), ler_recortes(), main(), reduzir(), validar_recorte(), nome_da_chamada()

### Community 14 - "Catalogo"
Cohesion: 0.09
Nodes (10): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), normalizar_marca() (+2 more)

### Community 15 - "os"
Cohesion: 0.17
Nodes (11): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+3 more)

### Community 16 - "Descoberta"
Cohesion: 0.13
Nodes (3): agora(), Descoberta, ErroDescoberta

### Community 17 - "Sinal"
Cohesion: 0.08
Nodes (22): adicionar_comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), indice_comandos(), ler_flipper(), ler_sinal_texto() (+14 more)

### Community 18 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.06
Nodes (34): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+26 more)

### Community 19 - "Registro"
Cohesion: 0.05
Nodes (18): ErroCapacidade, _hash(), _manifesto(), modulo_embutido(), Registro, capacidade_cli(), apps_usando(), _capacidades_rodando() (+10 more)

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 22 - "grade"
Cohesion: 0.07
Nodes (23): _abrir(), calma(), classe_janela(), dentro(), elementos(), em_anuncio(), fechar_anuncio(), tocar() (+15 more)

### Community 24 - "objetivo.py"
Cohesion: 0.15
Nodes (10): assinatura(), concluido(), Executor, fim(), melhor(), norm(), proibido(), rotulo() (+2 more)

### Community 25 - "e2e.cjs"
Cohesion: 0.13
Nodes (11): celular(), { chromium }, { execFileSync, spawn }, filhos, fs, nodeCrypto, os, PASTA (+3 more)

### Community 26 - "json"
Cohesion: 0.17
Nodes (12): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+4 more)

### Community 27 - "steps"
Cohesion: 0.11
Nodes (17): jobs, pacote, name, on, push, workflow_dispatch, runs-on, steps (+9 more)

### Community 28 - "time"
Cohesion: 0.11
Nodes (17): agir(), _ajudante(), app_em_foco(), _bloqueio_de_toque(), dump_ui(), escapar_input_text(), estado_rapido(), aguardar() (+9 more)

### Community 30 - "ErroEmissor"
Cohesion: 0.17
Nodes (5): relatar_uso(), Emissor, EmissorTermux, ErroEmissor, Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.08
Nodes (25): agenda(), analisar(), extras(), percentil95(), Comparação do planejador de missões no POCO, Rodada, classificar(), ficha_upnp() (+17 more)

### Community 32 - "gree_variante.py"
Cohesion: 0.23
Nodes (10): checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main(), perfil() (+2 more)

### Community 33 - "json"
Cohesion: 0.32
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 34 - "exec_cli"
Cohesion: 0.23
Nodes (3): exec_cli(), Autorizacao, gerar_segredo()

### Community 35 - "schema.sql"
Cohesion: 0.12
Nodes (15): aparelhos, chamadas, config, convites, credenciais, desafios, estado, eventos (+7 more)

### Community 36 - "painel.py"
Cohesion: 0.20
Nodes (11): painel_cli(), _b64(), estado_valido(), _eventos_novos(), gravar(), _http(), ler(), parear() (+3 more)

### Community 37 - "re"
Cohesion: 0.11
Nodes (12): achar(), achar_regra(), aplicar_regras(), els_fn(), botao_fechar(), casas_xadrez(), foto(), janela_nova() (+4 more)

### Community 38 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+10 more)

### Community 40 - "sonar/principal.py"
Cohesion: 0.22
Nodes (9): analisar_sonar(), escolher_e_testar(), frequencia_lembrada(), gerar_tom(), lembrar(), main(), sugestao_sem_tom(), testar() (+1 more)

### Community 41 - "TestImagemNoMcp"
Cohesion: 0.18
Nodes (4): _extrair_imagens(), varrer(), TestImagemNoMcp, TestImagensAninhadas

### Community 42 - "carregar_config"
Cohesion: 0.29
Nodes (10): _api(), carregar_config(), console(), url_quando_pronta(), estado_servidor(), parar_servico(), _porta_ativa(), _saude() (+2 more)

### Community 43 - "test_god_mode.py"
Cohesion: 0.11
Nodes (5): _Base, _ComServidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos

### Community 44 - "protocolos.py"
Cohesion: 0.15
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 48 - "ambiente_missao.py"
Cohesion: 0.23
Nodes (5): consultar_modelo(), contexto(), executar(), planejar(), RespostaDePlanoInvalida

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.26
Nodes (15): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+7 more)

### Community 53 - "Canal"
Cohesion: 0.10
Nodes (3): Canal, _mascarar(), WebSocket

### Community 54 - "os"
Cohesion: 0.24
Nodes (6): Ajudante, _apagar(), captura(), foto_rapida(), _jpeg(), _pasta_troca()

### Community 55 - "HANDOFF.md"
Cohesion: 0.19
Nodes (6): Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente, Licenças dos dados de controle

### Community 56 - "hashlib"
Cohesion: 0.15
Nodes (10): _jar(), _classes(), impressao_bruta(), _quadros(), fontes(), impressao(), checksum(), empacotar() (+2 more)

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 59 - ".anotar"
Cohesion: 0.10
Nodes (5): BluetoothDevice, ScanRecord, ScanResult, ParcelUuid, SparseArray

### Community 61 - "ar do quarto (ar-condicionado Gree GWH09KF)"
Cohesion: 0.20
Nodes (8): Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50), Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105), Perfil Gree Unknown (catálogo nº 102), descartado, Ligar/desligar diretos (energia_ligar 0x99, energia_desligar 0x98)

### Community 62 - "_iniciar"
Cohesion: 0.20
Nodes (12): armar_cli(), _aviso(), iniciar(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir() (+4 more)

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 66 - "main"
Cohesion: 0.17
Nodes (8): ampliar_catalogo(), _carimbo_catalogo(), catalogo_atual(), main(), _pid_do_servico(), progresso_txt(), reconstruir_catalogo(), Origens

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 69 - "._api"
Cohesion: 0.22
Nodes (5): ao_texto(), _confianca(), corpo_api(), ler_chave(), prompt_quiz()

### Community 70 - "piloto.py"
Cohesion: 0.15
Nodes (5): fen(), minha_cor(), quem_mexeu(), tabuleiro_txt(), _texto_do_evento()

### Community 77 - "Problemas já resolvidos (para não repetir)"
Cohesion: 0.16
Nodes (16): Anúncio dos testes (v1.0.1), Catálogo instalado: base + ampliado (9.380 perfis), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Estado atual da instalação (17/11/2026), Frases (+8 more)

### Community 79 - "tela/principal.py"
Cohesion: 0.08
Nodes (36): atividade_no_topo(), bloqueado(), bloqueados(), _chave(), _contar(), curto(), diferenca(), diferenca_curta() (+28 more)

### Community 81 - "resolver_grade"
Cohesion: 0.25
Nodes (5): _caixa(), _conflitos(), resolver_grade(), busca(), resolver_sudoku()

### Community 83 - ".decidir"
Cohesion: 0.48
Nodes (3): chave_quiz(), norm(), quiz_da_tela()

### Community 84 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

### Community 86 - "modulo_embutido"
Cohesion: 0.42
Nodes (7): abrir(), configurar(), estudar(), ler_preferencias(), mostrar(), piloto_local(), Preferencias

### Community 90 - "bluetooth/principal.py"
Cohesion: 0.11
Nodes (19): buscar(), buscar_app(), buscar_shell(), classificar(), compilar(), distancia(), guardar(), _ler_marca() (+11 more)

### Community 96 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, deploy, dev, test:e2e

### Community 100 - "shutil"
Cohesion: 0.35
Nodes (6): carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar()

### Community 102 - "cli.py"
Cohesion: 0.14
Nodes (14): arquivo_boot(), boot_ativado(), caminho_log(), _cfg_caminho(), criar_atalhos(), iniciar_em_segundo_plano(), inicio_automatico(), mostrar_log() (+6 more)

### Community 103 - "ar do escritório (ar-condicionado Carrier)"
Cohesion: 0.36
Nodes (8): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Cômodo: Escritório, Cômodo: Laboratório, Cômodo: Quarto, Índice de aparelhos (cômodo → aparelho → controle), Aparelhos salvos

### Community 105 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

### Community 106 - "Bluetooth"
Cohesion: 0.15
Nodes (5): Runnable, Bluetooth, Runnable, ScanSettings, Builder

### Community 108 - "catalogo_base"
Cohesion: 0.17
Nodes (3): catalogo_base(), novo_servico(), TestCatalogo

### Community 109 - "armado"
Cohesion: 0.32
Nodes (3): armado(), permitido(), 2. Etapa 0 — armação diária local (1.0.23, implementada)

### Community 110 - "tv do quarto (TV Samsung)"
Cohesion: 0.36
Nodes (6): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung)

### Community 111 - "TestSono"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 115 - "TestLeitorJava"
Cohesion: 0.05
Nodes (7): _carregar(), TestAppAuxiliar, TestBuscarNoCelular, TestClassificacao, TestCompilar, TestLeitorJava, TestTelaDicaDoCampo

### Community 127 - "CLAUDE.md"
Cohesion: 0.27
Nodes (4): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, empacotar.sh script

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 726 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **54 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `json`, `criar_servidor`, `normalizar`, `cli.py`, `ServidorMCP`, `Controlador`, `catalogo_base`, `armado`, `Catalogo`, `Descoberta`, `Sinal`, `Execucao`, `Registro`, `ar do quarto (ar-condicionado Gree GWH09KF)`, `ErroEmissor`, `Aparelhos`, `_iniciar`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.08208955223880597 - nodes in this community are weakly interconnected._
- **Why does `Catalogo` connect `Catalogo` to `json`, `main`, `Servico`, `Problemas já resolvidos (para não repetir)`, `Descoberta`, `Sinal`, `_iniciar`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Should `json` be split into smaller, more focused modules?**
  _Cohesion score 0.061971830985915494 - nodes in this community are weakly interconnected._
- **Why does `TestSegundoPlano` connect `Registro` to `json`, `TestLeitorJava`, `catalogo_base`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._