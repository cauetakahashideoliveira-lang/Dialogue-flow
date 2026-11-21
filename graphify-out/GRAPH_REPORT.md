# Graph Report - Dialogue-flow  (2026-11-21)

## Corpus Check
- 115 files · ~153,319 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 2250 nodes · 5069 edges · 132 communities (82 shown, 50 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 385 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `1c7e059f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- json
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
- observador.py
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
- ServidorMCP
- main
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
- Ajudante
- HANDOFF.md
- hashlib
- TestPiloto
- agora
- .anotar
- navegar
- time
- _iniciar
- Passagem de bastão do Dialogue-flow
- Notificador
- TestServidorMCP
- f
- local.cjs
- TestEstadoCelularSemProc
- ._api
- piloto.py
- criar_servidor
- Cerebros
- BluetoothAdapter
- Piloto
- Motor
- TestArmacao
- Problemas já resolvidos (para não repetir)
- ErroSinal
- tela/principal.py
- TestSegundoPlano
- modulo_embutido
- android.bluetooth.le.ScanResult
- _executar
- _Resposta
- TestResumoSemRepeticao
- modulo_embutido
- .main
- analisar.py
- TestObservador
- bluetooth/principal.py
- BluetoothDevice
- _Servidor
- abrirCanal
- Bluetooth.java
- TestTermometroSemResposta
- novo_servico
- atualizar_conhecimento.sh
- Canal
- shutil
- TestParidadeDoBloqueio
- cli.py
- ar do quarto (ar-condicionado Gree GWH09KF)
- aplicar_regras
- Contribuir com o Dialogue-flow
- Bluetooth
- TestProtocolos
- catalogo_base
- ._fila_teclas
- tv do quarto (TV Samsung)
- TestSono
- TestAtualizacaoRecompila
- TestVocabulario
- TestLeitorJava
- TestGodModeStmEPontuacao
- .startScan
- sys
- TestDescobrirRedeSemWifi
- AttributionSource
- construir_app_bluetooth.sh script
- TestRepositorio
- Process
- CLAUDE.md
- abrir_console

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
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper)` --conceptually_related_to--> `ler_flipper()`  [INFERRED]
  docs/aparelhos/README.md → controle-ir/controle_ir/formatos.py
- `variante()` --implements--> `Variante Gree a partir da captura real (troca só os bits)`  [INFERRED]
  ferramentas/gree_variante.py → docs/aparelhos/quarto/ar-do-quarto.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (132 total, 50 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.10
Nodes (26): aleatorio(), assinar(), assinarRequisicao(), BAIXO_RISCO, bloqueioNaBorda(), chaves(), config(), cookie() (+18 more)

### Community 1 - "json"
Cohesion: 0.08
Nodes (12): capacidades(), _curto(), _faixa_txt(), _linhas_aparelho(), resumo_aparelho(), resumo_instrucoes(), _classes(), impressao_bruta() (+4 more)

### Community 2 - "TestPainel"
Cohesion: 0.09
Nodes (16): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 2. Etapa 0 — armação diária local (1.0.23, implementada), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1) (+8 more)

### Community 4 - "normalizar"
Cohesion: 0.15
Nodes (12): Aparelhos, ErroAparelho, chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar(), sem_acentos() (+4 more)

### Community 5 - "Servico"
Cohesion: 0.11
Nodes (4): ErroUso, Servico, Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105), Perfil Gree Unknown (catálogo nº 102), descartado

### Community 6 - "Controlador"
Cohesion: 0.08
Nodes (11): Controlador, Etapa, Plano, Emissor, EmissorSimulado, EmissorTermux, ErroEmissor, normalizar_valor() (+3 more)

### Community 7 - ".passo"
Cohesion: 0.11
Nodes (9): achar(), eventos(), _Executor, els_fn(), relevantes(), _Falha, foco(), _Interrompido (+1 more)

### Community 8 - "Celular"
Cohesion: 0.11
Nodes (6): _carregar(), Celular, el(), TestExecutorObjetivo, decidir(), escolher()

### Community 10 - "Politica"
Cohesion: 0.23
Nodes (4): armar_cli(), painel_cli(), Politica, fim_do_dia()

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "canal.py"
Cohesion: 0.29
Nodes (5): filtro(), ler_recortes(), main(), reduzir(), validar_recorte()

### Community 14 - "Catalogo"
Cohesion: 0.11
Nodes (11): Catalogo, estado_representativo(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), normalizar_marca(), _unzip() (+3 more)

### Community 15 - "os"
Cohesion: 0.13
Nodes (12): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+4 more)

### Community 16 - "Descoberta"
Cohesion: 0.13
Nodes (5): agora(), hora_legivel(), executar(), Descoberta, ErroDescoberta

### Community 17 - "Sinal"
Cohesion: 0.13
Nodes (19): adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos() (+11 more)

### Community 18 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.06
Nodes (34): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+26 more)

### Community 19 - "Registro"
Cohesion: 0.21
Nodes (5): ErroCapacidade, _hash(), _manifesto(), Registro, capacidade_cli()

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 22 - "grade"
Cohesion: 0.08
Nodes (19): _abrir(), calma(), classe_janela(), dentro(), elementos(), em_anuncio(), fechar_anuncio(), tocar() (+11 more)

### Community 24 - "objetivo.py"
Cohesion: 0.18
Nodes (10): assinatura(), concluido(), fim(), melhor(), norm(), proibido(), rotulo(), sistema() (+2 more)

### Community 25 - "e2e.cjs"
Cohesion: 0.09
Nodes (15): flagPath, fs, os, path, celular(), { chromium }, { execFileSync, spawn }, filhos (+7 more)

### Community 26 - "json"
Cohesion: 0.23
Nodes (12): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+4 more)

### Community 27 - "steps"
Cohesion: 0.11
Nodes (17): jobs, pacote, name, on, push, workflow_dispatch, runs-on, steps (+9 more)

### Community 28 - "time"
Cohesion: 0.14
Nodes (17): agir(), _ajudante(), _apagar(), app_em_foco(), _bloqueio_de_toque(), captura(), dump_ui(), escapar_input_text() (+9 more)

### Community 30 - "observador.py"
Cohesion: 0.19
Nodes (8): relatar_uso(), apps_usando(), _capacidades_rodando(), em_uso(), quadro(), recursos_do_comando(), _tarefas(), _tela()

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.16
Nodes (11): classificar(), ficha_upnp(), ip_do_wifi(), ler_inventarios(), main(), sondar(), ssdp(), tcp() (+3 more)

### Community 32 - "gree_variante.py"
Cohesion: 0.20
Nodes (11): exportar_jsonl(), checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main() (+3 more)

### Community 33 - "json"
Cohesion: 0.29
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 34 - "exec_cli"
Cohesion: 0.24
Nodes (3): exec_cli(), Autorizacao, gerar_segredo()

### Community 35 - "schema.sql"
Cohesion: 0.12
Nodes (15): aparelhos, chamadas, config, convites, credenciais, desafios, estado, eventos (+7 more)

### Community 36 - "painel.py"
Cohesion: 0.21
Nodes (10): _b64(), estado_valido(), _eventos_novos(), gravar(), _http(), ler(), parear(), sincronizar() (+2 more)

### Community 37 - "re"
Cohesion: 0.15
Nodes (7): botao_fechar(), janela_nova(), reflexos(), _regex_bloqueados(), _regras(), tabuleiro_curto(), vez_no_historico()

### Community 38 - "package.json"
Cohesion: 0.10
Nodes (23): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+15 more)

### Community 40 - "sonar/principal.py"
Cohesion: 0.22
Nodes (9): analisar_sonar(), escolher_e_testar(), frequencia_lembrada(), gerar_tom(), lembrar(), main(), sugestao_sem_tom(), testar() (+1 more)

### Community 41 - "ServidorMCP"
Cohesion: 0.05
Nodes (9): PlanoTest, resumo_para_instrucoes(), _extrair_imagens(), varrer(), ServidorMCP, TestCapacidades, TestImagemNoMcp, TestImagensAninhadas (+1 more)

### Community 42 - "main"
Cohesion: 0.14
Nodes (16): ampliar_catalogo(), _api(), carregar_config(), _cfg_caminho(), console(), url_quando_pronta(), estado_servidor(), main() (+8 more)

### Community 43 - "test_god_mode.py"
Cohesion: 0.11
Nodes (5): _Base, _ComServidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos

### Community 44 - "protocolos.py"
Cohesion: 0.16
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 48 - "ambiente_missao.py"
Cohesion: 0.24
Nodes (6): consultar_modelo(), contexto(), escolher(), executar(), planejar(), RespostaDePlanoInvalida

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
Cohesion: 0.19
Nodes (6): Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente, Licenças dos dados de controle

### Community 56 - "hashlib"
Cohesion: 0.16
Nodes (10): compilar(), guardar(), gravar_memoria(), _jar(), fontes(), impressao(), checksum(), empacotar() (+2 more)

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 58 - "agora"
Cohesion: 0.26
Nodes (23): acaoDono(), ackCelular(), agora(), autorizar(), consumirDesafio(), erro(), fresca(), guardarDesafio() (+15 more)

### Community 59 - ".anotar"
Cohesion: 0.13
Nodes (4): ScanRecord, ScanResult, ParcelUuid, SparseArray

### Community 60 - "navegar"
Cohesion: 0.14
Nodes (15): atividade_no_topo(), bloqueado(), bloqueados(), casas_xadrez(), foto(), _ferramentas_piloto(), aguardar(), tabuleiro_local() (+7 more)

### Community 61 - "time"
Cohesion: 0.21
Nodes (9): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi() (+1 more)

### Community 62 - "_iniciar"
Cohesion: 0.23
Nodes (11): _aviso(), iniciar(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir(), mostrar_url() (+3 more)

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 65 - "TestServidorMCP"
Cohesion: 0.17
Nodes (3): julgar_depois(), Reenvios, TestServidorMCP

### Community 66 - "f"
Cohesion: 0.32
Nodes (4): Executor, gravar(), progresso_txt(), f()

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 69 - "._api"
Cohesion: 0.22
Nodes (5): ao_texto(), _confianca(), corpo_api(), ler_chave(), prompt_quiz()

### Community 70 - "piloto.py"
Cohesion: 0.14
Nodes (7): chave_quiz(), fen(), norm(), quem_mexeu(), quiz_da_tela(), tabuleiro_txt(), _texto_do_evento()

### Community 71 - "criar_servidor"
Cohesion: 0.24
Nodes (13): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), local_ok() (+5 more)

### Community 76 - "TestArmacao"
Cohesion: 0.21
Nodes (3): armado(), permitido(), TestArmacao

### Community 77 - "Problemas já resolvidos (para não repetir)"
Cohesion: 0.15
Nodes (17): Anúncio dos testes (v1.0.1), Catálogo instalado: base + ampliado (9.380 perfis), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026) (+9 more)

### Community 78 - "ErroSinal"
Cohesion: 0.10
Nodes (7): broadlink_para_pulsos(), ErroSinal, limitar_duracao(), normalizar_pulsos(), pronto_para_pulsos(), TestFormatos, TestGreeVariante

### Community 79 - "tela/principal.py"
Cohesion: 0.08
Nodes (24): _caixa(), _chave(), compactos(), _conflitos(), _contar(), curto(), diferenca(), diferenca_curta() (+16 more)

### Community 83 - "_executar"
Cohesion: 0.17
Nodes (10): _executar(), escolher(), _modulo_piloto(), objetivo(), abrir(), aplicar_regras(), decidir(), elementos() (+2 more)

### Community 84 - "_Resposta"
Cohesion: 0.17
Nodes (3): _Resposta, TestDiagnosticoRede, urlopen()

### Community 86 - "modulo_embutido"
Cohesion: 0.40
Nodes (6): abrir(), configurar(), estudar(), ler_preferencias(), mostrar(), Preferencias

### Community 87 - ".main"
Cohesion: 0.19
Nodes (4): ScanSettings, Builder, Handler, Looper

### Community 88 - "analisar.py"
Cohesion: 0.31
Nodes (6): agenda(), analisar(), extras(), percentil95(), Comparação do planejador de missões no POCO, Rodada

### Community 90 - "bluetooth/principal.py"
Cohesion: 0.12
Nodes (17): buscar(), buscar_app(), buscar_shell(), classificar(), distancia(), _ler_marca(), ler_pareados_dumpsys(), ler_registro() (+9 more)

### Community 93 - "abrirCanal"
Cohesion: 0.28
Nodes (9): abrirCanal(), aparelhoDoToken(), canalDe(), empurrar(), estadoCanal(), estadoDe(), estadoParaCelular(), inicializar() (+1 more)

### Community 97 - "novo_servico"
Cohesion: 0.11
Nodes (3): novo_servico(), TestTela, TestTermometro

### Community 100 - "shutil"
Cohesion: 0.24
Nodes (6): carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar()

### Community 102 - "cli.py"
Cohesion: 0.11
Nodes (17): arquivo_boot(), atualizar(), boot_ativado(), caminho_log(), _carimbo_catalogo(), catalogo_atual(), criar_atalhos(), iniciar_em_segundo_plano() (+9 more)

### Community 103 - "ar do quarto (ar-condicionado Gree GWH09KF)"
Cohesion: 0.16
Nodes (15): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50) (+7 more)

### Community 104 - "aplicar_regras"
Cohesion: 0.33
Nodes (4): achar_regra(), aplicar_regras(), els_fn(), regra_vale()

### Community 105 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

### Community 106 - "Bluetooth"
Cohesion: 0.15
Nodes (3): Runnable, Bluetooth, Runnable

### Community 110 - "tv do quarto (TV Samsung)"
Cohesion: 0.43
Nodes (7): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung), Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas)

### Community 111 - "TestSono"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 115 - "TestLeitorJava"
Cohesion: 0.05
Nodes (7): _carregar(), TestAppAuxiliar, TestBuscarNoCelular, TestClassificacao, TestCompilar, TestLeitorJava, TestTelaDicaDoCampo

### Community 118 - "sys"
Cohesion: 0.09
Nodes (3): TestApkAtualizado, TestManifesto, TestFerramentasDaMissao

### Community 127 - "CLAUDE.md"
Cohesion: 0.27
Nodes (4): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, empacotar.sh script

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 727 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **50 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TestTelaPorArquivo` connect `TestTelaPorArquivo` to `json`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.09788359788359788 - nodes in this community are weakly interconnected._
- **Why does `Servico` connect `Servico` to `json`, `novo_servico`, `normalizar`, `cli.py`, `Controlador`, `criar_servidor`, `ServidorMCP`, `Catalogo`, `ErroSinal`, `Descoberta`, `Sinal`, `Registro`, `Execucao`, `_iniciar`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Should `json` be split into smaller, more focused modules?**
  _Cohesion score 0.07686932215234102 - nodes in this community are weakly interconnected._
- **Why does `Modo deus — arquitetura evolutiva e mapa de oportunidades` connect `Modo deus — arquitetura evolutiva e mapa de oportunidades` to `HANDOFF.md`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._