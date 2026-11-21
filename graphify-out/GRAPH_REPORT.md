# Graph Report - Dialogue-flow  (2026-11-21)

## Corpus Check
- 88 files · ~136,263 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 1820 nodes · 4231 edges · 99 communities (65 shown, 34 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 311 edges (avg confidence: 0.87)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `48584139`
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
- agir
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
- gree_variante.py
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
- TestTela
- exec_cli
- Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude
- autorizar.js
- app.js
- Canal
- os
- TestCapacidades
- Problemas já resolvidos (para não repetir)
- TestPiloto
- diagnostico_rede/principal.py
- CLAUDE.md
- .test_canal_repassa_chamada_e_aviso
- tv do quarto (TV Samsung)
- _iniciar
- Passagem de bastão do Dialogue-flow
- TestExecucao
- resumo_para_instrucoes
- criar_servidor
- local.cjs
- capacidades.py
- EmissorTermux
- piloto.py
- ServidorMCP
- Cerebros
- novo_servico
- Piloto
- Motor
- ._api
- Notificador
- TestTunel
- tela/principal.py
- PlanoTest
- TestGreeVariante
- TestTermometro
- Sincronizador
- godmode-tracker.js
- pacote.py
- modulo_embutido
- Canal
- TestArmacao
- TestObservador
- TestProtocolos
- analisar.py
- _Servidor
- _modelos_do_teclado
- Contribuir com o Dialogue-flow
- scripts
- TestFormatos
- atualizar_conhecimento.sh

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
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `ampliar_catalogo()`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/cli.py
- `Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper)` --conceptually_related_to--> `ler_flipper()`  [INFERRED]
  docs/aparelhos/README.md → controle-ir/controle_ir/formatos.py
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (99 total, 34 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.10
Nodes (58): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+50 more)

### Community 1 - "test_controle_ir.py"
Cohesion: 0.09
Nodes (11): capacidades(), _curto(), _faixa_txt(), hora_legivel(), _linhas_aparelho(), resumo_aparelho(), resumo_para_instrucoes(), executar() (+3 more)

### Community 2 - "TestPainel"
Cohesion: 0.06
Nodes (23): consultar_modelo(), contexto(), escolher(), executar(), planejar(), RespostaDePlanoInvalida, armado(), permitido() (+15 more)

### Community 4 - "ErroUso"
Cohesion: 0.11
Nodes (8): Aparelhos, ErroAparelho, ErroUso, slug(), Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105), Perfil Gree Unknown (catálogo nº 102), descartado, Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper), Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas)

### Community 5 - "Sinal"
Cohesion: 0.19
Nodes (18): adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos() (+10 more)

### Community 6 - "Controlador"
Cohesion: 0.17
Nodes (6): Controlador, Etapa, Plano, normalizar_valor(), valores_equivalentes(), TestControle

### Community 7 - ".passo"
Cohesion: 0.11
Nodes (7): compactos(), eventos(), _Executor, els_fn(), relevantes(), _Falha, _Interrompido

### Community 8 - "capacidades.py"
Cohesion: 0.18
Nodes (6): ErroCapacidade, _hash(), _manifesto(), Registro, capacidade_cli(), 2. Etapa 0 — armação diária local (1.0.23, implementada)

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "agir"
Cohesion: 0.12
Nodes (24): _abrir(), agir(), _ajudante(), app_em_foco(), _bloqueio_de_toque(), calma(), classe_janela(), dump_ui() (+16 more)

### Community 14 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.11
Nodes (18): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+10 more)

### Community 15 - "os"
Cohesion: 0.13
Nodes (12): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+4 more)

### Community 16 - "Descoberta"
Cohesion: 0.05
Nodes (25): agora(), Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper() (+17 more)

### Community 17 - "Sinal"
Cohesion: 0.17
Nodes (10): broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta(), limitar_duracao(), normalizar_pulsos(), pronto_para_pulsos(), pulsos_para_broadlink() (+2 more)

### Community 18 - "Servico"
Cohesion: 0.18
Nodes (3): EmissorSimulado, Servico, TestDescoberta

### Community 19 - "main"
Cohesion: 0.22
Nodes (12): _api(), carregar_config(), _cfg_caminho(), console(), url_quando_pronta(), estado_servidor(), parar_servico(), _porta_ativa() (+4 more)

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 22 - "HANDOFF.md"
Cohesion: 0.18
Nodes (6): Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente, Licenças dos dados de controle

### Community 24 - "TestSegundoPlano"
Cohesion: 0.08
Nodes (7): catalogo_base(), TestCatalogo, TestRepositorio, TestSegundoPlano, abrir_console(), reiniciado(), TestStockfishLocal

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
Cohesion: 0.10
Nodes (14): achar(), achar_regra(), aplicar_regras(), els_fn(), botao_fechar(), escapar_input_text(), janela_nova(), _linhas_do_passo() (+6 more)

### Community 30 - "gree_variante.py"
Cohesion: 0.21
Nodes (10): checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main(), perfil() (+2 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.18
Nodes (9): classificar(), ficha_upnp(), ip_do_wifi(), main(), sondar(), ssdp(), tcp(), udp() (+1 more)

### Community 32 - "cli.py"
Cohesion: 0.11
Nodes (22): ampliar_catalogo(), arquivo_boot(), atualizar(), boot_ativado(), caminho_log(), _carimbo_catalogo(), catalogo_atual(), criar_atalhos() (+14 more)

### Community 33 - "tela/principal.py"
Cohesion: 0.11
Nodes (18): atividade_no_topo(), bloqueado(), bloqueados(), casas_xadrez(), elementos(), escolher(), foto(), _ferramentas_piloto() (+10 more)

### Community 34 - "termometro/principal.py"
Cohesion: 0.33
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 35 - "schema.sql"
Cohesion: 0.12
Nodes (15): aparelhos, chamadas, config, convites, credenciais, desafios, estado, eventos (+7 more)

### Community 36 - "painel.py"
Cohesion: 0.20
Nodes (11): painel_cli(), _b64(), estado_valido(), _eventos_novos(), gravar(), _http(), ler(), parear() (+3 more)

### Community 38 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+10 more)

### Community 40 - "sonar/principal.py"
Cohesion: 0.14
Nodes (9): js(), rodar(), analisar_sonar(), gerar_tom(), main(), testar(), volume_musica(), arquivos_cc0() (+1 more)

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
Cohesion: 0.13
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 47 - "f"
Cohesion: 0.15
Nodes (5): filtro(), ler_recortes(), main(), reduzir(), validar_recorte()

### Community 49 - "exec_cli"
Cohesion: 0.23
Nodes (3): exec_cli(), Autorizacao, gerar_segredo()

### Community 50 - "Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude"
Cohesion: 0.12
Nodes (16): Botão Stockfish para estudos, Capacidades plugáveis (ferramentas novas sem mexer no núcleo), Cobertura dos testes, Como funciona, Conectar ao ChatGPT ou ao Claude, Descoberta, Desenvolvimento, Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude (+8 more)

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.26
Nodes (15): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+7 more)

### Community 53 - "Canal"
Cohesion: 0.13
Nodes (3): Canal, _mascarar(), WebSocket

### Community 54 - "os"
Cohesion: 0.17
Nodes (11): Ajudante, _apagar(), captura(), curto(), diferenca_curta(), foto_rapida(), _jar(), _jpeg() (+3 more)

### Community 56 - "Problemas já resolvidos (para não repetir)"
Cohesion: 0.19
Nodes (15): Anúncio dos testes (v1.0.1), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026), Frases (+7 more)

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 58 - "diagnostico_rede/principal.py"
Cohesion: 0.30
Nodes (9): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi() (+1 more)

### Community 59 - "CLAUDE.md"
Cohesion: 0.27
Nodes (4): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, empacotar.sh script

### Community 61 - "tv do quarto (TV Samsung)"
Cohesion: 0.11
Nodes (22): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50) (+14 more)

### Community 62 - "_iniciar"
Cohesion: 0.29
Nodes (9): armar_cli(), _aviso(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir(), mostrar_url() (+1 more)

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle (Cloudflare), Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 66 - "criar_servidor"
Cohesion: 0.09
Nodes (16): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), local_ok() (+8 more)

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 70 - "piloto.py"
Cohesion: 0.18
Nodes (7): chave_quiz(), fen(), gravar_memoria(), norm(), quem_mexeu(), quiz_da_tela(), _texto_do_evento()

### Community 75 - "Motor"
Cohesion: 0.25
Nodes (3): minha_cor(), Motor, tabuleiro_txt()

### Community 76 - "._api"
Cohesion: 0.22
Nodes (5): ao_texto(), _confianca(), corpo_api(), ler_chave(), prompt_quiz()

### Community 79 - "tela/principal.py"
Cohesion: 0.07
Nodes (22): _caixa(), _chave(), _conflitos(), _contar(), dentro(), diferenca(), executar(), historico() (+14 more)

### Community 84 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

### Community 85 - "pacote.py"
Cohesion: 0.33
Nodes (4): checksum(), empacotar(), fontes(), verificar()

### Community 86 - "modulo_embutido"
Cohesion: 0.39
Nodes (5): modulo_embutido(), abrir(), estudar(), mostrar(), piloto_local()

### Community 91 - "analisar.py"
Cohesion: 0.29
Nodes (6): agenda(), analisar(), extras(), percentil95(), Comparação do planejador de missões no POCO, Rodada

### Community 93 - "_modelos_do_teclado"
Cohesion: 0.40
Nodes (3): _modelos_do_teclado(), teclado_da_grade(), _teclado_parado()

### Community 95 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

### Community 96 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, deploy, dev, test:e2e

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 592 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **34 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `cli.py`, `test_controle_ir.py`, `criar_servidor`, `ErroUso`, `Sinal`, `Controlador`, `ServidorMCP`, `capacidades.py`, `Execucao`, `novo_servico`, `Descoberta`, `Sinal`, `tv do quarto (TV Samsung)`, `_iniciar`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `Servico` (e.g. with `ServidorMCP` and `Aparelhos`) actually correct?**
  _`Servico` has 17 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.09830508474576272 - nodes in this community are weakly interconnected._
- **Why does `TestTelaPorArquivo` connect `TestTelaPorArquivo` to `test_controle_ir.py`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `Sinal` (e.g. with `Catalogo` and `Descoberta`) actually correct?**
  _`Sinal` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_controle_ir.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08734693877551021 - nodes in this community are weakly interconnected._