# Graph Report - Dialogue-flow  (2026-11-21)

## Corpus Check
- 89 files · ~137,385 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 1854 nodes · 4289 edges · 113 communities (77 shown, 36 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 311 edges (avg confidence: 0.87)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `80ca80d4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- test_controle_ir.py
- TestPainel
- Conexao
- ErroUso
- Sinal
- Controlador
- .passo
- capacidades.py
- Execucao
- Politica
- steps
- _ajudante
- TestTelaPorArquivo
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- os
- Descoberta
- Sinal
- Servico
- main
- Instalador (instalar.sh)
- Tela
- HANDOFF.md
- Tunel
- TestSegundoPlano
- e2e.cjs
- json
- steps
- TestVocabulario
- re
- subprocess
- descobrir_rede/principal.py
- cli.py
- tela/principal.py
- termometro/principal.py
- schema.sql
- painel.py
- TestOuvirBipe
- package.json
- TestSono
- sonar/principal.py
- _extrair_imagens
- observador.py
- test_god_mode.py
- protocolos.py
- webauthn.js
- session-start.sh
- f
- ambiente_missao.py
- exec_cli
- Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude
- autorizar.js
- app.js
- Canal
- time
- novo_servico
- sys
- TestPiloto
- diagnostico_rede/principal.py
- CLAUDE.md
- .test_canal_repassa_chamada_e_aviso
- gree_variante.py
- _iniciar
- Passagem de bastão do Dialogue-flow
- TestExecucao
- aparelhos.py
- criar_servidor
- local.cjs
- capacidades.py
- EmissorTermux
- piloto.py
- ServidorMCP
- Cerebros
- Piloto
- Motor
- ._api
- Notificador
- vocabulario.py
- tela/principal.py
- PlanoTest
- TestGreeVariante
- TestTermometro
- Sincronizador
- godmode-tracker.js
- pacote.py
- modulo_embutido
- Canal
- TestServidorMCP
- TestObservador
- TestProtocolos
- analisar.py
- _Servidor
- Controlador
- Catalogo
- Contribuir com o Dialogue-flow
- scripts
- Sinal
- atualizar_conhecimento.sh
- normalizar
- shutil
- TestParidadeDoBloqueio
- caminho_log
- WebSocket
- resolver_grade
- Origens
- catalogo_base
- 4. Mapa de oportunidades
- Autonomia do planejador no POCO
- execucao.py

## God Nodes (most connected - your core abstractions)
1. `Servico` - 64 edges
2. `Sinal` - 39 edges
3. `main()` - 38 edges
4. `Descoberta` - 37 edges
5. `Tela` - 36 edges
6. `TestTelaPorArquivo` - 36 edges
7. `Catalogo` - 35 edges
8. `criar_servidor()` - 31 edges
9. `_iniciar()` - 28 edges
10. `Controlador` - 27 edges

## Surprising Connections (you probably didn't know these)
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `ampliar_catalogo()`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/cli.py
- `Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper)` --conceptually_related_to--> `ler_flipper()`  [INFERRED]
  docs/aparelhos/README.md → controle-ir/controle_ir/formatos.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (113 total, 36 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.10
Nodes (58): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+50 more)

### Community 1 - "test_controle_ir.py"
Cohesion: 0.13
Nodes (3): hora_legivel(), main(), preparar()

### Community 2 - "TestPainel"
Cohesion: 0.10
Nodes (15): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono (+7 more)

### Community 3 - "Conexao"
Cohesion: 0.24
Nodes (3): carregar_memoria(), Conexao, _texto_do_evento()

### Community 4 - "ErroUso"
Cohesion: 0.15
Nodes (6): Aparelhos, ErroUso, Servico, slug(), Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper), Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas)

### Community 5 - "Sinal"
Cohesion: 0.19
Nodes (17): adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos() (+9 more)

### Community 6 - "Controlador"
Cohesion: 0.20
Nodes (5): Etapa, executar(), Plano, normalizar_valor(), valores_equivalentes()

### Community 7 - ".passo"
Cohesion: 0.10
Nodes (8): achar(), eventos(), _Executor, els_fn(), relevantes(), _Falha, _Interrompido, janela_nova()

### Community 8 - "capacidades.py"
Cohesion: 0.19
Nodes (5): ErroCapacidade, _hash(), _manifesto(), Registro, capacidade_cli()

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "_ajudante"
Cohesion: 0.10
Nodes (22): _abrir(), _ajudante(), aplicar_regras(), els_fn(), app_em_foco(), calma(), classe_janela(), _contar() (+14 more)

### Community 14 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.17
Nodes (12): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade, 8. Próximos experimentos (ordem sugerida) (+4 more)

### Community 15 - "os"
Cohesion: 0.18
Nodes (10): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+2 more)

### Community 16 - "Descoberta"
Cohesion: 0.20
Nodes (3): agora(), Descoberta, ErroDescoberta

### Community 17 - "Sinal"
Cohesion: 0.16
Nodes (9): broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta(), limitar_duracao(), normalizar_pulsos(), pronto_para_pulsos(), pulsos_para_broadlink() (+1 more)

### Community 19 - "main"
Cohesion: 0.29
Nodes (10): _api(), carregar_config(), console(), url_quando_pronta(), estado_servidor(), parar_servico(), _porta_ativa(), _saude() (+2 more)

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 23 - "Tunel"
Cohesion: 0.11
Nodes (3): Tunel, TestArmacao, TestTunel

### Community 24 - "TestSegundoPlano"
Cohesion: 0.10
Nodes (5): TestRepositorio, TestSegundoPlano, abrir_console(), reiniciado(), TestStockfishLocal

### Community 25 - "e2e.cjs"
Cohesion: 0.13
Nodes (11): celular(), { chromium }, { execFileSync, spawn }, filhos, fs, nodeCrypto, os, PASTA (+3 more)

### Community 26 - "json"
Cohesion: 0.23
Nodes (12): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+4 more)

### Community 27 - "steps"
Cohesion: 0.11
Nodes (17): jobs, pacote, name, on, push, workflow_dispatch, runs-on, steps (+9 more)

### Community 29 - "re"
Cohesion: 0.11
Nodes (12): achar_regra(), botao_fechar(), casas_xadrez(), escapar_input_text(), foto(), _linhas_do_passo(), normalizar(), reflexos() (+4 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.18
Nodes (9): classificar(), ficha_upnp(), ip_do_wifi(), main(), sondar(), ssdp(), tcp(), udp() (+1 more)

### Community 32 - "cli.py"
Cohesion: 0.14
Nodes (18): ampliar_catalogo(), arquivo_boot(), atualizar(), boot_ativado(), _carimbo_catalogo(), catalogo_atual(), _cfg_caminho(), criar_atalhos() (+10 more)

### Community 33 - "tela/principal.py"
Cohesion: 0.15
Nodes (16): gravar_memoria(), atividade_no_topo(), bloqueado(), bloqueados(), escolher(), _ferramentas_piloto(), aguardar(), tabuleiro_local() (+8 more)

### Community 34 - "termometro/principal.py"
Cohesion: 0.33
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 35 - "schema.sql"
Cohesion: 0.12
Nodes (15): aparelhos, chamadas, config, convites, credenciais, desafios, estado, eventos (+7 more)

### Community 36 - "painel.py"
Cohesion: 0.22
Nodes (10): painel_cli(), _b64(), estado_valido(), _eventos_novos(), gravar(), _http(), ler(), parear() (+2 more)

### Community 38 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+10 more)

### Community 39 - "TestSono"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 40 - "sonar/principal.py"
Cohesion: 0.31
Nodes (5): analisar_sonar(), gerar_tom(), main(), testar(), volume_musica()

### Community 41 - "_extrair_imagens"
Cohesion: 0.22
Nodes (3): _extrair_imagens(), varrer(), TestImagensAninhadas

### Community 42 - "observador.py"
Cohesion: 0.19
Nodes (8): relatar_uso(), apps_usando(), _capacidades_rodando(), em_uso(), quadro(), recursos_do_comando(), _tarefas(), _tela()

### Community 43 - "test_god_mode.py"
Cohesion: 0.11
Nodes (5): _Base, _ComServidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos

### Community 44 - "protocolos.py"
Cohesion: 0.13
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 47 - "f"
Cohesion: 0.27
Nodes (5): filtro(), ler_recortes(), main(), reduzir(), validar_recorte()

### Community 48 - "ambiente_missao.py"
Cohesion: 0.15
Nodes (8): consultar_modelo(), contexto(), executar(), planejar(), RespostaDePlanoInvalida, armado(), permitido(), 2. Etapa 0 — armação diária local (1.0.23, implementada)

### Community 50 - "Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude"
Cohesion: 0.12
Nodes (16): Botão Stockfish para estudos, Capacidades plugáveis (ferramentas novas sem mexer no núcleo), Cobertura dos testes, Como funciona, Conectar ao ChatGPT ou ao Claude, Descoberta, Desenvolvimento, Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude (+8 more)

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.26
Nodes (15): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+7 more)

### Community 54 - "time"
Cohesion: 0.13
Nodes (16): agir(), Ajudante, _apagar(), _bloqueio_de_toque(), captura(), dump_ui(), foto_rapida(), _jar() (+8 more)

### Community 55 - "novo_servico"
Cohesion: 0.10
Nodes (3): novo_servico(), TestCapacidades, TestTela

### Community 56 - "sys"
Cohesion: 0.13
Nodes (4): _estado_celular(), TestEstadoCelularSemProc, TestFerramentasDaMissao, TestResumoSemRepeticao

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 58 - "diagnostico_rede/principal.py"
Cohesion: 0.36
Nodes (8): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi()

### Community 59 - "CLAUDE.md"
Cohesion: 0.27
Nodes (4): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, empacotar.sh script

### Community 61 - "gree_variante.py"
Cohesion: 0.06
Nodes (49): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50) (+41 more)

### Community 62 - "_iniciar"
Cohesion: 0.29
Nodes (9): armar_cli(), _aviso(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir(), mostrar_url() (+1 more)

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 65 - "aparelhos.py"
Cohesion: 0.14
Nodes (8): capacidades(), _curto(), ErroAparelho, _faixa_txt(), _linhas_aparelho(), resumo_aparelho(), resumo_para_instrucoes(), TestResumoInstrucoes

### Community 66 - "criar_servidor"
Cohesion: 0.24
Nodes (13): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), local_ok() (+5 more)

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 69 - "EmissorTermux"
Cohesion: 0.20
Nodes (3): Emissor, EmissorTermux, ErroEmissor

### Community 70 - "piloto.py"
Cohesion: 0.17
Nodes (6): chave_quiz(), fen(), minha_cor(), norm(), quiz_da_tela(), tabuleiro_txt()

### Community 71 - "ServidorMCP"
Cohesion: 0.15
Nodes (3): resumo_instrucoes(), ServidorMCP, TestImagemNoMcp

### Community 76 - "._api"
Cohesion: 0.22
Nodes (5): ao_texto(), _confianca(), corpo_api(), ler_chave(), prompt_quiz()

### Community 78 - "vocabulario.py"
Cohesion: 0.21
Nodes (9): chaves_de_teste(), interpretar(), _por_regex(), _registrar(), sem_acentos(), _t(), Termo, termo_por_chave() (+1 more)

### Community 79 - "tela/principal.py"
Cohesion: 0.08
Nodes (24): _chave(), compactos(), curto(), diferenca(), diferenca_curta(), elementos(), estado_rapido(), executar() (+16 more)

### Community 84 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

### Community 85 - "pacote.py"
Cohesion: 0.25
Nodes (5): verificar_requisicao(), checksum(), empacotar(), fontes(), verificar()

### Community 86 - "modulo_embutido"
Cohesion: 0.39
Nodes (5): modulo_embutido(), abrir(), estudar(), mostrar(), piloto_local()

### Community 88 - "TestServidorMCP"
Cohesion: 0.19
Nodes (3): julgar_depois(), Reenvios, TestServidorMCP

### Community 91 - "analisar.py"
Cohesion: 0.31
Nodes (6): agenda(), analisar(), extras(), percentil95(), Comparação do planejador de missões no POCO, Rodada

### Community 93 - "Controlador"
Cohesion: 0.36
Nodes (3): Controlador, EmissorSimulado, TestControle

### Community 94 - "Catalogo"
Cohesion: 0.14
Nodes (11): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), _unzip() (+3 more)

### Community 95 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

### Community 96 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, deploy, dev, test:e2e

### Community 97 - "Sinal"
Cohesion: 0.20
Nodes (3): ler_sinal_texto(), Sinal, TestFormatos

### Community 99 - "normalizar"
Cohesion: 0.25
Nodes (3): normalizar_marca(), categoria_canonica(), normalizar()

### Community 100 - "shutil"
Cohesion: 0.35
Nodes (6): carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar()

### Community 102 - "caminho_log"
Cohesion: 0.20
Nodes (6): caminho_log(), iniciar_em_segundo_plano(), mostrar_log(), _redirecionar_para_log(), _registrar(), _seguir_log()

### Community 105 - "resolver_grade"
Cohesion: 0.25
Nodes (5): _caixa(), _conflitos(), resolver_grade(), busca(), resolver_sudoku()

### Community 109 - "4. Mapa de oportunidades"
Cohesion: 0.33
Nodes (6): 4. Mapa de oportunidades, Casa e rede, Celular e Android, Computadores, nuvem e agentes, O próprio sistema, Observar o resultado (agir → medir → ajustar)

### Community 110 - "Autonomia do planejador no POCO"
Cohesion: 0.40
Nodes (5): Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 610 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **36 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `ErroUso` to `test_controle_ir.py`, `Controlador`, `capacidades.py`, `Execucao`, `Descoberta`, `Sinal`, `Servico`, `cli.py`, `_extrair_imagens`, `ambiente_missao.py`, `novo_servico`, `_iniciar`, `aparelhos.py`, `criar_servidor`, `EmissorTermux`, `ServidorMCP`, `.painel`, `Controlador`, `Catalogo`, `Sinal`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `Servico` (e.g. with `ServidorMCP` and `Aparelhos`) actually correct?**
  _`Servico` has 17 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.09830508474576272 - nodes in this community are weakly interconnected._
- **Why does `TestTelaPorArquivo` connect `TestTelaPorArquivo` to `test_controle_ir.py`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Should `test_controle_ir.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1349206349206349 - nodes in this community are weakly interconnected._
- **Why does `Cerebros` connect `Cerebros` to `Piloto`, `Conexao`, `._api`, `piloto.py`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._