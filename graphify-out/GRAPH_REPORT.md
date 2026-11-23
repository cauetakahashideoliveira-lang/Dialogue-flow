# Graph Report - Dialogue-flow  (2026-11-23)

## Corpus Check
- 95 files · ~144,038 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 1978 nodes · 4546 edges · 98 communities (70 shown, 28 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 324 edges (avg confidence: 0.87)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `a419f2ff`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- test_controle_ir.py
- TestPainel
- Conexao
- Aparelhos
- Sinal
- Controlador
- .passo
- capacidades.py
- TestExecucao
- Politica
- steps
- _executar
- TestTelaPorArquivo
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- os
- Descoberta
- execucao.py
- Servico
- normalizar
- Instalador (instalar.sh)
- Tela
- HANDOFF.md
- Tunel
- TestOuvirBipe
- e2e.cjs
- json
- steps
- TestVocabulario
- aplicar_regras
- Catalogo
- descobrir_rede/principal.py
- cli.py
- tela/principal.py
- termometro/principal.py
- schema.sql
- painel.py
- ps4/principal.py
- package.json
- TestSono
- sonar/principal.py
- TestImagemNoMcp
- TestPrincipal
- test_god_mode.py
- sinais.py
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
- Conexao
- TestPiloto
- diagnostico_rede/principal.py
- CLAUDE.md
- .test_canal_repassa_chamada_e_aviso
- gree_variante.py
- _iniciar
- Passagem de bastão do Dialogue-flow
- 4. Mapa de oportunidades
- resumo_para_instrucoes
- criar_servidor
- local.cjs
- TestGodModeStmEPontuacao
- EmissorTermux
- .decidir
- ServidorMCP
- Cerebros
- Autonomia do planejador no POCO
- Piloto
- Motor
- piloto.py
- protocolos.py
- tela/principal.py
- PlanoTest
- atualizar
- caminho_log
- Sincronizador
- godmode-tracker.js
- pacote.py
- _jar
- TestArmacao
- PS4: controle completo e jogador que aprende (capacidade `ps4`, 1.0.66+)
- TestObservador
- TestProtocolos
- jogador.py
- _Servidor
- TestTermometro
- _janela_curta
- Contribuir com o Dialogue-flow
- scripts
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
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py
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

## Communities (98 total, 28 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.08
Nodes (59): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+51 more)

### Community 1 - "test_controle_ir.py"
Cohesion: 0.09
Nodes (10): capacidades(), _curto(), _faixa_txt(), hora_legivel(), _linhas_aparelho(), resumo_aparelho(), executar(), ErroEmissor (+2 more)

### Community 2 - "TestPainel"
Cohesion: 0.10
Nodes (15): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono (+7 more)

### Community 4 - "Aparelhos"
Cohesion: 0.21
Nodes (3): Aparelhos, ErroAparelho, Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper)

### Community 5 - "Sinal"
Cohesion: 0.21
Nodes (15): adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos() (+7 more)

### Community 6 - "Controlador"
Cohesion: 0.12
Nodes (8): Controlador, Etapa, Plano, normalizar_valor(), valores_equivalentes(), catalogo_base(), TestCatalogo, TestControle

### Community 7 - ".passo"
Cohesion: 0.10
Nodes (11): achar(), compactos(), eventos(), _Executor, els_fn(), relevantes(), _Falha, foco() (+3 more)

### Community 8 - "capacidades.py"
Cohesion: 0.06
Nodes (19): modulo_embutido(), abrir(), configurar(), estudar(), ler_preferencias(), mostrar(), Preferencias, apps_usando() (+11 more)

### Community 10 - "Politica"
Cohesion: 0.20
Nodes (6): armar_cli(), painel_cli(), Politica, estado_valido(), ler(), fim_do_dia()

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "_executar"
Cohesion: 0.18
Nodes (8): executar(), _executar(), main(), reflexos(), _regras(), _resumo_volta(), rotina(), gravar()

### Community 14 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.17
Nodes (12): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade, 8. Próximos experimentos (ordem sugerida) (+4 more)

### Community 15 - "os"
Cohesion: 0.18
Nodes (10): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+2 more)

### Community 16 - "Descoberta"
Cohesion: 0.13
Nodes (3): agora(), Descoberta, ErroDescoberta

### Community 17 - "execucao.py"
Cohesion: 0.18
Nodes (7): consultar_modelo(), contexto(), executar(), planejar(), RespostaDePlanoInvalida, armado(), permitido()

### Community 18 - "Servico"
Cohesion: 0.05
Nodes (13): ErroCapacidade, _hash(), _manifesto(), Registro, capacidade_cli(), Emissor, EmissorSimulado, classificar() (+5 more)

### Community 19 - "normalizar"
Cohesion: 0.16
Nodes (15): normalizar_marca(), ler_sinal_texto(), _traduz(), categoria_canonica(), chaves_de_teste(), interpretar(), normalizar(), _por_regex() (+7 more)

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 22 - "HANDOFF.md"
Cohesion: 0.25
Nodes (3): Comparação do planejador de missões no POCO, Rodada, Licenças dos dados de controle

### Community 25 - "e2e.cjs"
Cohesion: 0.13
Nodes (11): celular(), { chromium }, { execFileSync, spawn }, filhos, fs, nodeCrypto, os, PASTA (+3 more)

### Community 26 - "json"
Cohesion: 0.19
Nodes (16): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+8 more)

### Community 27 - "steps"
Cohesion: 0.11
Nodes (17): jobs, pacote, name, on, push, workflow_dispatch, runs-on, steps (+9 more)

### Community 29 - "aplicar_regras"
Cohesion: 0.22
Nodes (6): achar_regra(), aplicar_regras(), els_fn(), tocar(), _injetar(), regra_vale()

### Community 30 - "Catalogo"
Cohesion: 0.11
Nodes (11): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), _unzip() (+3 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.18
Nodes (9): classificar(), ficha_upnp(), ip_do_wifi(), main(), sondar(), ssdp(), tcp(), udp() (+1 more)

### Community 32 - "cli.py"
Cohesion: 0.13
Nodes (27): ampliar_catalogo(), _api(), arquivo_boot(), boot_ativado(), _carimbo_catalogo(), carregar_config(), catalogo_atual(), _cfg_caminho() (+19 more)

### Community 33 - "tela/principal.py"
Cohesion: 0.10
Nodes (20): atividade_no_topo(), bloqueado(), bloqueados(), casas_xadrez(), escolher(), foto(), _ferramentas_piloto(), aguardar() (+12 more)

### Community 34 - "termometro/principal.py"
Cohesion: 0.33
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 35 - "schema.sql"
Cohesion: 0.12
Nodes (15): aparelhos, chamadas, config, convites, credenciais, desafios, estado, eventos (+7 more)

### Community 36 - "painel.py"
Cohesion: 0.15
Nodes (8): _b64(), _eventos_novos(), gravar(), _http(), parear(), sincronizar(), verificar(), verificar_requisicao()

### Community 37 - "ps4/principal.py"
Cohesion: 0.15
Nodes (22): cmd_comando(), fundo(), cmd_habilidade(), cmd_jogador(), codificar(), Estado, executar(), _gravar() (+14 more)

### Community 38 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+10 more)

### Community 39 - "TestSono"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 40 - "sonar/principal.py"
Cohesion: 0.12
Nodes (9): js(), rodar(), analisar_sonar(), gerar_tom(), main(), testar(), volume_musica(), arquivos_cc0() (+1 more)

### Community 41 - "TestImagemNoMcp"
Cohesion: 0.18
Nodes (4): _extrair_imagens(), varrer(), TestImagemNoMcp, TestImagensAninhadas

### Community 42 - "TestPrincipal"
Cohesion: 0.07
Nodes (6): ConexaoFalsa, Gravador, _mod(), TestComandos, TestJogador, TestPrincipal

### Community 43 - "test_god_mode.py"
Cohesion: 0.11
Nodes (5): _Base, _ComServidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos

### Community 44 - "sinais.py"
Cohesion: 0.08
Nodes (13): sinal(), broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta(), limitar_duracao(), normalizar_pulsos(), pronto_para_pulsos() (+5 more)

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 47 - "f"
Cohesion: 0.15
Nodes (6): filtro(), ler_recortes(), main(), reduzir(), validar_recorte(), _jpeg()

### Community 49 - "exec_cli"
Cohesion: 0.24
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
Cohesion: 0.13
Nodes (18): agir(), _ajudante(), _apagar(), app_em_foco(), _bloqueio_de_toque(), captura(), dump_ui(), escapar_input_text() (+10 more)

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 58 - "diagnostico_rede/principal.py"
Cohesion: 0.30
Nodes (9): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi() (+1 more)

### Community 59 - "CLAUDE.md"
Cohesion: 0.27
Nodes (4): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, empacotar.sh script

### Community 61 - "gree_variante.py"
Cohesion: 0.05
Nodes (49): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50) (+41 more)

### Community 62 - "_iniciar"
Cohesion: 0.18
Nodes (9): _aviso(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir(), mostrar_url(), _termux() (+1 more)

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 64 - "4. Mapa de oportunidades"
Cohesion: 0.33
Nodes (6): 4. Mapa de oportunidades, Casa e rede, Celular e Android, Computadores, nuvem e agentes, O próprio sistema, Observar o resultado (agir → medir → ajustar)

### Community 66 - "criar_servidor"
Cohesion: 0.09
Nodes (16): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), local_ok() (+8 more)

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 69 - "EmissorTermux"
Cohesion: 0.47
Nodes (3): relatar_uso(), EmissorTermux, Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz)

### Community 70 - ".decidir"
Cohesion: 0.39
Nodes (3): chave_quiz(), norm(), quiz_da_tela()

### Community 73 - "Autonomia do planejador no POCO"
Cohesion: 0.40
Nodes (5): Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente

### Community 76 - "piloto.py"
Cohesion: 0.11
Nodes (9): ao_texto(), _confianca(), corpo_api(), fen(), ler_chave(), minha_cor(), prompt_quiz(), quem_mexeu() (+1 more)

### Community 77 - "protocolos.py"
Cohesion: 0.15
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 79 - "tela/principal.py"
Cohesion: 0.07
Nodes (30): _abrir(), botao_fechar(), _caixa(), calma(), _chave(), classe_janela(), _conflitos(), _contar() (+22 more)

### Community 82 - "caminho_log"
Cohesion: 0.20
Nodes (6): caminho_log(), criar_atalhos(), pasta_atalhos(), _redirecionar_para_log(), _registrar(), _seguir_log()

### Community 84 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

### Community 85 - "pacote.py"
Cohesion: 0.36
Nodes (4): checksum(), empacotar(), fontes(), verificar()

### Community 88 - "PS4: controle completo e jogador que aprende (capacidade `ps4`, 1.0.66+)"
Cohesion: 0.29
Nodes (6): Instalação no Termux (uma vez, com o sistema armado), Jogador que aprende (`acao=jogador`), Limites medidos/esperados, Preparo (uma vez), PS4: controle completo e jogador que aprende (capacidade `ps4`, 1.0.66+), Uso

### Community 91 - "jogador.py"
Cohesion: 0.05
Nodes (21): agenda(), analisar(), extras(), percentil95(), botao(), ErroComando, executar(), lado() (+13 more)

### Community 94 - "_janela_curta"
Cohesion: 0.40
Nodes (3): historico(), _janela_curta(), _linha_do_tempo()

### Community 95 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

### Community 96 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, deploy, dev, test:e2e

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 644 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `cli.py`, `test_controle_ir.py`, `criar_servidor`, `Aparelhos`, `Controlador`, `ServidorMCP`, `sinais.py`, `Descoberta`, `TestTela`, `normalizar`, `Catalogo`, `gree_variante.py`, `_iniciar`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 16 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.08208955223880597 - nodes in this community are weakly interconnected._
- **Why does `Descoberta` connect `Descoberta` to `test_controle_ir.py`, `sinais.py`, `Servico`, `normalizar`, `Catalogo`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `Sinal` (e.g. with `Catalogo` and `Descoberta`) actually correct?**
  _`Sinal` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_controle_ir.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08928571428571429 - nodes in this community are weakly interconnected._