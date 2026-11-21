# Graph Report - Dialogue-flow  (2026-11-21)

## Corpus Check
- 115 files · ~155,154 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 2268 nodes · 5121 edges · 130 communities (71 shown, 59 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 388 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `7da74bcf`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- test_controle_ir.py
- TestPainel
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
- servico.py
- os
- Descoberta
- Sinal
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- navegar
- Instalador (instalar.sh)
- Tela
- grade
- subprocess
- objetivo.py
- e2e.cjs
- json
- steps
- time
- Registro
- time
- descobrir_rede/principal.py
- gree_variante.py
- TestBuscarNoCelular
- exec_cli
- schema.sql
- Sincronizador
- Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude
- package.json
- TestOuvirBipe
- sonar/principal.py
- ServidorMCP
- analisar.py
- test_god_mode.py
- protocolos.py
- webauthn.js
- session-start.sh
- catalogo_base
- armado
- TestExecucao
- tv do quarto (TV Samsung)
- autorizar.js
- app.js
- Canal
- _jar
- HANDOFF.md
- hashlib
- TestPiloto
- TestGreeVariante
- .anotar
- Execucao
- TestSono
- TestCanal
- Passagem de bastão do Dialogue-flow
- .decidir
- criar_servidor
- resolver_grade
- local.cjs
- TestEstadoCelularSemProc
- ._api
- piloto.py
- Autonomia do planejador no POCO
- Cerebros
- BluetoothAdapter
- Piloto
- Motor
- TestArmacao
- TestAppAuxiliar
- TestClassificacao
- tela/principal.py
- TestSegundoPlano
- 4. Mapa de oportunidades
- android.bluetooth.le.ScanResult
- fechar_anuncio
- PlanoTest
- godmode-tracker.js
- modulo_embutido
- Looper
- ErroEmissor
- TestObservador
- bluetooth/principal.py
- BluetoothClass
- _Servidor
- resumo_para_instrucoes
- Bluetooth.java
- TestCapacidades
- novo_servico
- atualizar_conhecimento.sh
- _carregar
- shutil
- TestParidadeDoBloqueio
- cli.py
- _linhas_do_passo
- TestResumoSemRepeticao
- Contribuir com o Dialogue-flow
- Bluetooth
- TestProtocolos
- TestTermometro
- TestFerramentasDaMissao
- TestAtualizacaoRecompila
- abrir_console
- TestVocabulario
- TestLeitorJava
- TestImagemNoMcp
- .startScan
- TestGodModeStmEPontuacao
- scripts
- AttributionSource
- construir_app_bluetooth.sh script
- TestRepositorio
- Process

## God Nodes (most connected - your core abstractions)
1. `Servico` - 62 edges
2. `main()` - 38 edges
3. `Tela` - 37 edges
4. `Descoberta` - 37 edges
5. `Sinal` - 37 edges
6. `TestTelaPorArquivo` - 36 edges
7. `Catalogo` - 35 edges
8. `f()` - 32 edges
9. `Celular` - 31 edges
10. `criar_servidor()` - 31 edges

## Surprising Connections (you probably didn't know these)
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py
- `Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper)` --conceptually_related_to--> `ler_flipper()`  [INFERRED]
  docs/aparelhos/README.md → controle-ir/controle_ir/formatos.py
- `variante()` --implements--> `Variante Gree a partir da captura real (troca só os bits)`  [INFERRED]
  ferramentas/gree_variante.py → docs/aparelhos/quarto/ar-do-quarto.md
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `ampliar_catalogo()`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/cli.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (130 total, 59 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.08
Nodes (59): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+51 more)

### Community 1 - "test_controle_ir.py"
Cohesion: 0.07
Nodes (4): main(), preparar(), TestApkAtualizado, TestManifesto

### Community 2 - "TestPainel"
Cohesion: 0.09
Nodes (15): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono (+7 more)

### Community 4 - "normalizar"
Cohesion: 0.23
Nodes (12): comando(), chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar(), sem_acentos(), slug() (+4 more)

### Community 5 - "Servico"
Cohesion: 0.14
Nodes (6): executar(), EmissorSimulado, ErroUso, Servico, Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas), TestDescoberta

### Community 6 - "Controlador"
Cohesion: 0.17
Nodes (6): Controlador, Etapa, Plano, normalizar_valor(), valores_equivalentes(), TestControle

### Community 7 - ".passo"
Cohesion: 0.11
Nodes (8): achar(), eventos(), _Executor, els_fn(), relevantes(), _Falha, _Interrompido, normalizar()

### Community 8 - "Celular"
Cohesion: 0.10
Nodes (6): _carregar(), Celular, el(), TestExecutorObjetivo, decidir(), escolher()

### Community 9 - "TestSonarFrequencia"
Cohesion: 0.06
Nodes (8): _carregar(), _Resposta, TestDescobrirRedeSemWifi, TestDiagnosticoRede, urlopen(), TestSonarFrequencia, testar(), TestTermometroSemResposta

### Community 10 - "Politica"
Cohesion: 0.26
Nodes (3): painel_cli(), Politica, fim_do_dia()

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "canal.py"
Cohesion: 0.13
Nodes (11): nome_da_chamada(), _b64(), estado_valido(), _eventos_novos(), gravar(), _http(), ler(), parear() (+3 more)

### Community 14 - "servico.py"
Cohesion: 0.10
Nodes (9): Aparelhos, capacidades(), _curto(), ErroAparelho, _faixa_txt(), hora_legivel(), _linhas_aparelho(), resumo_aparelho() (+1 more)

### Community 15 - "os"
Cohesion: 0.18
Nodes (10): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+2 more)

### Community 16 - "Descoberta"
Cohesion: 0.06
Nodes (15): agora(), Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper() (+7 more)

### Community 17 - "Sinal"
Cohesion: 0.07
Nodes (29): adicionar_comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos(), ler_flipper() (+21 more)

### Community 18 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.17
Nodes (12): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade, 8. Próximos experimentos (ordem sugerida) (+4 more)

### Community 19 - "navegar"
Cohesion: 0.13
Nodes (18): atividade_no_topo(), bloqueado(), bloqueados(), casas_xadrez(), escolher(), foto(), _ferramentas_piloto(), aguardar() (+10 more)

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 22 - "grade"
Cohesion: 0.08
Nodes (17): achar_regra(), aplicar_regras(), els_fn(), calma(), elementos(), tocar(), grade(), _injetar() (+9 more)

### Community 23 - "subprocess"
Cohesion: 0.15
Nodes (8): filtro(), ler_recortes(), main(), reduzir(), validar_recorte(), _jpeg(), arquivos_cc0(), main()

### Community 24 - "objetivo.py"
Cohesion: 0.11
Nodes (16): assinatura(), busca(), concluido(), Executor, fim(), interruptor(), melhor(), norm() (+8 more)

### Community 25 - "e2e.cjs"
Cohesion: 0.13
Nodes (11): celular(), { chromium }, { execFileSync, spawn }, filhos, fs, nodeCrypto, os, PASTA (+3 more)

### Community 26 - "json"
Cohesion: 0.12
Nodes (24): guardar(), analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main() (+16 more)

### Community 27 - "steps"
Cohesion: 0.11
Nodes (17): jobs, pacote, name, on, push, workflow_dispatch, runs-on, steps (+9 more)

### Community 28 - "time"
Cohesion: 0.15
Nodes (19): _abrir(), agir(), _ajudante(), _apagar(), _bloqueio_de_toque(), captura(), dump_ui(), estado_rapido() (+11 more)

### Community 29 - "Registro"
Cohesion: 0.06
Nodes (20): consultar_modelo(), contexto(), executar(), planejar(), RespostaDePlanoInvalida, ErroCapacidade, _hash(), _manifesto() (+12 more)

### Community 30 - "time"
Cohesion: 0.28
Nodes (9): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi() (+1 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.16
Nodes (11): classificar(), ficha_upnp(), ip_do_wifi(), ler_inventarios(), main(), sondar(), ssdp(), tcp() (+3 more)

### Community 32 - "gree_variante.py"
Cohesion: 0.05
Nodes (29): Pacote do celular dist/controle-ir.zip, Tunel, Anúncio dos testes (v1.0.1), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz) (+21 more)

### Community 34 - "exec_cli"
Cohesion: 0.23
Nodes (3): exec_cli(), Autorizacao, gerar_segredo()

### Community 35 - "schema.sql"
Cohesion: 0.12
Nodes (15): aparelhos, chamadas, config, convites, credenciais, desafios, estado, eventos (+7 more)

### Community 37 - "Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude"
Cohesion: 0.12
Nodes (16): Botão Stockfish para estudos, Capacidades plugáveis (ferramentas novas sem mexer no núcleo), Cobertura dos testes, Como funciona, Conectar ao ChatGPT ou ao Claude, Descoberta, Desenvolvimento, Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude (+8 more)

### Community 38 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+10 more)

### Community 40 - "sonar/principal.py"
Cohesion: 0.22
Nodes (9): analisar_sonar(), escolher_e_testar(), frequencia_lembrada(), gerar_tom(), lembrar(), main(), sugestao_sem_tom(), testar() (+1 more)

### Community 42 - "analisar.py"
Cohesion: 0.42
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

### Community 48 - "armado"
Cohesion: 0.32
Nodes (3): armado(), permitido(), 2. Etapa 0 — armação diária local (1.0.23, implementada)

### Community 50 - "tv do quarto (TV Samsung)"
Cohesion: 0.10
Nodes (25): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50) (+17 more)

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.26
Nodes (15): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+7 more)

### Community 53 - "Canal"
Cohesion: 0.10
Nodes (3): Canal, _mascarar(), WebSocket

### Community 55 - "HANDOFF.md"
Cohesion: 0.26
Nodes (3): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Licenças dos dados de controle

### Community 56 - "hashlib"
Cohesion: 0.19
Nodes (7): _jar(), fontes(), impressao(), checksum(), empacotar(), fontes(), verificar()

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 59 - ".anotar"
Cohesion: 0.10
Nodes (5): BluetoothDevice, ScanRecord, ScanResult, ParcelUuid, SparseArray

### Community 61 - "TestSono"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 64 - ".decidir"
Cohesion: 0.39
Nodes (3): chave_quiz(), norm(), quiz_da_tela()

### Community 65 - "criar_servidor"
Cohesion: 0.08
Nodes (16): julgar_depois(), criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json() (+8 more)

### Community 66 - "resolver_grade"
Cohesion: 0.25
Nodes (5): _caixa(), _conflitos(), resolver_grade(), busca(), resolver_sudoku()

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 69 - "._api"
Cohesion: 0.22
Nodes (5): ao_texto(), _confianca(), corpo_api(), ler_chave(), prompt_quiz()

### Community 70 - "piloto.py"
Cohesion: 0.15
Nodes (5): fen(), minha_cor(), quem_mexeu(), tabuleiro_txt(), _texto_do_evento()

### Community 71 - "Autonomia do planejador no POCO"
Cohesion: 0.22
Nodes (7): Comparação do planejador de missões no POCO, Rodada, Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente

### Community 79 - "tela/principal.py"
Cohesion: 0.07
Nodes (28): app_em_foco(), botao_fechar(), _chave(), compactos(), _contar(), curto(), dentro(), diferenca() (+20 more)

### Community 81 - "4. Mapa de oportunidades"
Cohesion: 0.33
Nodes (6): 4. Mapa de oportunidades, Casa e rede, Celular e Android, Computadores, nuvem e agentes, O próprio sistema, Observar o resultado (agir → medir → ajustar)

### Community 83 - "fechar_anuncio"
Cohesion: 0.20
Nodes (8): classe_janela(), em_anuncio(), objetivo(), abrir(), aplicar_regras(), bloqueado(), elementos(), recolher()

### Community 85 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

### Community 86 - "modulo_embutido"
Cohesion: 0.47
Nodes (6): abrir(), configurar(), estudar(), ler_preferencias(), mostrar(), Preferencias

### Community 88 - "ErroEmissor"
Cohesion: 0.20
Nodes (3): Emissor, EmissorTermux, ErroEmissor

### Community 90 - "bluetooth/principal.py"
Cohesion: 0.11
Nodes (18): buscar(), buscar_app(), buscar_shell(), classificar(), compilar(), distancia(), _ler_marca(), ler_pareados_dumpsys() (+10 more)

### Community 100 - "shutil"
Cohesion: 0.36
Nodes (6): carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar()

### Community 102 - "cli.py"
Cohesion: 0.06
Nodes (47): ampliar_catalogo(), _api(), armar_cli(), arquivo_boot(), atualizar(), _aviso(), boot_ativado(), caminho_log() (+39 more)

### Community 105 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

### Community 106 - "Bluetooth"
Cohesion: 0.15
Nodes (5): Runnable, Bluetooth, Runnable, ScanSettings, Builder

### Community 116 - "TestImagemNoMcp"
Cohesion: 0.18
Nodes (4): _extrair_imagens(), varrer(), TestImagemNoMcp, TestImagensAninhadas

### Community 119 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, deploy, dev, test:e2e

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 733 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **59 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `criar_servidor`, `test_controle_ir.py`, `normalizar`, `cli.py`, `Controlador`, `ServidorMCP`, `TestTermometro`, `servico.py`, `Descoberta`, `Sinal`, `armado`, `ErroEmissor`, `Execucao`, `Registro`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.08208955223880597 - nodes in this community are weakly interconnected._
- **Why does `TestPiloto` connect `TestPiloto` to `test_controle_ir.py`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Should `test_controle_ir.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07188778492109878 - nodes in this community are weakly interconnected._
- **Why does `Cerebros` connect `Cerebros` to `.decidir`, `Piloto`, `._api`, `piloto.py`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._