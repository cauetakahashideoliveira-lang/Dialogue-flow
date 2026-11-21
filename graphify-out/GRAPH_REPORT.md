# Graph Report - Dialogue-flow  (2026-11-21)

## Corpus Check
- 90 files · ~138,763 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 1896 nodes · 4361 edges · 94 communities (72 shown, 22 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 318 edges (avg confidence: 0.87)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `810a2ee6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- test_controle_ir.py
- TestPainel
- Conexao
- Aparelhos
- Catalogo
- Controlador
- .passo
- Servico
- TestSonarFrequencia
- Politica
- steps
- fechar_anuncio
- TestTelaPorArquivo
- Problemas já resolvidos (para não repetir)
- os
- Descoberta
- Sinal
- Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude
- main
- Instalador (instalar.sh)
- Tela
- HANDOFF.md
- Tunel
- TestSegundoPlano
- e2e.cjs
- json
- steps
- analisar.py
- re
- tv do quarto (TV Samsung)
- descobrir_rede/principal.py
- diagnostico_rede/principal.py
- agir
- termometro/principal.py
- schema.sql
- painel.py
- Canal
- package.json
- novo_servico
- sonar/principal.py
- _extrair_imagens
- observador.py
- test_god_mode.py
- protocolos.py
- webauthn.js
- session-start.sh
- TestImagemNoMcp
- ambiente_missao.py
- exec_cli
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- autorizar.js
- app.js
- Canal
- time
- TestAtualizacaoRecompila
- TestPiloto
- TestCapacidades
- CLAUDE.md
- .test_canal_repassa_chamada_e_aviso
- ar do quarto (ar-condicionado Gree GWH09KF)
- _iniciar
- Passagem de bastão do Dialogue-flow
- TestExecucao
- resumo_para_instrucoes
- local.cjs
- test_consistencia.py
- piloto.py
- ServidorMCP
- Cerebros
- .decidir
- Piloto
- Motor
- Notificador
- vocabulario.py
- tela/principal.py
- PlanoTest
- TestGreeVariante
- Sincronizador
- godmode-tracker.js
- pacote.py
- modulo_embutido
- TestServidorMCP
- TestObservador
- _Servidor
- servico.py
- gree_variante.py
- scripts
- Variante Gree a partir da captura real (troca só os bits)
- atualizar_conhecimento.sh
- shutil
- TestParidadeDoBloqueio
- cli.py

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
- `variante()` --implements--> `Variante Gree a partir da captura real (troca só os bits)`  [INFERRED]
  ferramentas/gree_variante.py → docs/aparelhos/quarto/ar-do-quarto.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (94 total, 22 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.10
Nodes (58): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+50 more)

### Community 1 - "test_controle_ir.py"
Cohesion: 0.06
Nodes (7): _classes(), impressao_bruta(), pulsos_para_broadlink(), _quadros(), main(), preparar(), TestGodModeStmEPontuacao

### Community 2 - "TestPainel"
Cohesion: 0.10
Nodes (15): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono (+7 more)

### Community 3 - "Conexao"
Cohesion: 0.20
Nodes (4): ao_texto(), Conexao, _confianca(), _texto_do_evento()

### Community 5 - "Catalogo"
Cohesion: 0.10
Nodes (11): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), _unzip() (+3 more)

### Community 6 - "Controlador"
Cohesion: 0.09
Nodes (12): hora_legivel(), Controlador, Etapa, executar(), Plano, Emissor, EmissorSimulado, EmissorTermux (+4 more)

### Community 7 - ".passo"
Cohesion: 0.11
Nodes (7): compactos(), eventos(), _Executor, els_fn(), relevantes(), _Falha, _Interrompido

### Community 8 - "Servico"
Cohesion: 0.05
Nodes (24): ErroCapacidade, _hash(), _manifesto(), Registro, capacidade_cli(), classificar(), Execucao, ErroUso (+16 more)

### Community 9 - "TestSonarFrequencia"
Cohesion: 0.08
Nodes (7): _carregar(), _Resposta, TestDiagnosticoRede, urlopen(), TestSonarFrequencia, testar(), TestTermometroSemResposta

### Community 10 - "Politica"
Cohesion: 0.26
Nodes (3): armar_cli(), Politica, fim_do_dia()

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "fechar_anuncio"
Cohesion: 0.12
Nodes (12): _abrir(), achar(), achar_regra(), aplicar_regras(), els_fn(), botao_fechar(), escapar_input_text(), fechar_anuncio() (+4 more)

### Community 14 - "Problemas já resolvidos (para não repetir)"
Cohesion: 0.19
Nodes (14): Anúncio dos testes (v1.0.1), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026), Frases (+6 more)

### Community 15 - "os"
Cohesion: 0.16
Nodes (11): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+3 more)

### Community 16 - "Descoberta"
Cohesion: 0.13
Nodes (3): agora(), Descoberta, ErroDescoberta

### Community 17 - "Sinal"
Cohesion: 0.09
Nodes (21): adicionar_comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), indice_comandos(), ler_flipper(), ler_sinal_texto() (+13 more)

### Community 18 - "Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude"
Cohesion: 0.12
Nodes (16): Botão Stockfish para estudos, Capacidades plugáveis (ferramentas novas sem mexer no núcleo), Cobertura dos testes, Como funciona, Conectar ao ChatGPT ou ao Claude, Descoberta, Desenvolvimento, Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude (+8 more)

### Community 19 - "main"
Cohesion: 0.29
Nodes (10): _api(), carregar_config(), console(), url_quando_pronta(), estado_servidor(), parar_servico(), _porta_ativa(), _saude() (+2 more)

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 22 - "HANDOFF.md"
Cohesion: 0.13
Nodes (11): Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente, Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição (+3 more)

### Community 23 - "Tunel"
Cohesion: 0.11
Nodes (3): Tunel, TestArmacao, TestTunel

### Community 24 - "TestSegundoPlano"
Cohesion: 0.08
Nodes (7): catalogo_base(), TestCatalogo, TestRepositorio, TestSegundoPlano, abrir_console(), reiniciado(), TestStockfishLocal

### Community 25 - "e2e.cjs"
Cohesion: 0.13
Nodes (11): celular(), { chromium }, { execFileSync, spawn }, filhos, fs, nodeCrypto, os, PASTA (+3 more)

### Community 26 - "json"
Cohesion: 0.18
Nodes (17): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+9 more)

### Community 27 - "steps"
Cohesion: 0.11
Nodes (17): jobs, pacote, name, on, push, workflow_dispatch, runs-on, steps (+9 more)

### Community 28 - "analisar.py"
Cohesion: 0.31
Nodes (6): agenda(), analisar(), extras(), percentil95(), Comparação do planejador de missões no POCO, Rodada

### Community 29 - "re"
Cohesion: 0.10
Nodes (16): atividade_no_topo(), casas_xadrez(), classe_janela(), em_anuncio(), foto(), _ferramentas_piloto(), aguardar(), tabuleiro_local() (+8 more)

### Community 30 - "tv do quarto (TV Samsung)"
Cohesion: 0.31
Nodes (8): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung), Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas), Catálogo instalado: base + ampliado (9.380 perfis)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.18
Nodes (9): classificar(), ficha_upnp(), ip_do_wifi(), main(), sondar(), ssdp(), tcp(), udp() (+1 more)

### Community 32 - "diagnostico_rede/principal.py"
Cohesion: 0.36
Nodes (8): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi()

### Community 33 - "agir"
Cohesion: 0.12
Nodes (18): agir(), bloqueado(), bloqueados(), _bloqueio_de_toque(), _contar(), executar(), _executar(), escolher() (+10 more)

### Community 34 - "termometro/principal.py"
Cohesion: 0.29
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

### Community 39 - "novo_servico"
Cohesion: 0.05
Nodes (7): _carregar_cap(), novo_servico(), TestOuvirBipe, TestSonar, TestSono, TestTela, TestTermometro

### Community 40 - "sonar/principal.py"
Cohesion: 0.22
Nodes (9): analisar_sonar(), escolher_e_testar(), frequencia_lembrada(), gerar_tom(), lembrar(), main(), sugestao_sem_tom(), testar() (+1 more)

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
Cohesion: 0.15
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 48 - "ambiente_missao.py"
Cohesion: 0.17
Nodes (8): consultar_modelo(), contexto(), escolher(), executar(), planejar(), RespostaDePlanoInvalida, armado(), permitido()

### Community 49 - "exec_cli"
Cohesion: 0.24
Nodes (3): exec_cli(), Autorizacao, gerar_segredo()

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

### Community 54 - "time"
Cohesion: 0.12
Nodes (17): Ajudante, _ajudante(), _apagar(), app_em_foco(), captura(), dump_ui(), estado_rapido(), foto_rapida() (+9 more)

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 59 - "CLAUDE.md"
Cohesion: 0.27
Nodes (4): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, empacotar.sh script

### Community 61 - "ar do quarto (ar-condicionado Gree GWH09KF)"
Cohesion: 0.21
Nodes (13): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Ligar/desligar diretos (energia_ligar 0x99, energia_desligar 0x98) (+5 more)

### Community 62 - "_iniciar"
Cohesion: 0.36
Nodes (8): _aviso(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir(), mostrar_url(), _termux()

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 68 - "test_consistencia.py"
Cohesion: 0.14
Nodes (4): _estado_celular(), TestEstadoCelularSemProc, TestFerramentasDaMissao, TestResumoSemRepeticao

### Community 70 - "piloto.py"
Cohesion: 0.14
Nodes (5): corpo_api(), fen(), minha_cor(), quem_mexeu(), tabuleiro_txt()

### Community 73 - ".decidir"
Cohesion: 0.48
Nodes (3): chave_quiz(), norm(), quiz_da_tela()

### Community 78 - "vocabulario.py"
Cohesion: 0.14
Nodes (18): normalizar_marca(), comando(), importar_texto(), ler_smartir(), novo_perfil(), _traduz(), categoria_canonica(), chaves_de_teste() (+10 more)

### Community 79 - "tela/principal.py"
Cohesion: 0.07
Nodes (27): _caixa(), calma(), _chave(), _conflitos(), curto(), dentro(), diferenca(), diferenca_curta() (+19 more)

### Community 84 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

### Community 85 - "pacote.py"
Cohesion: 0.19
Nodes (6): arquivos_cc0(), main(), checksum(), empacotar(), fontes(), verificar()

### Community 86 - "modulo_embutido"
Cohesion: 0.39
Nodes (5): modulo_embutido(), abrir(), estudar(), mostrar(), piloto_local()

### Community 88 - "TestServidorMCP"
Cohesion: 0.13
Nodes (4): julgar_depois(), Origens, Reenvios, TestServidorMCP

### Community 89 - "TestObservador"
Cohesion: 0.12
Nodes (3): TestObservador, TestProtocolos, TestVocabulario

### Community 93 - "servico.py"
Cohesion: 0.21
Nodes (6): capacidades(), _curto(), ErroAparelho, _faixa_txt(), _linhas_aparelho(), resumo_aparelho()

### Community 94 - "gree_variante.py"
Cohesion: 0.23
Nodes (10): checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main(), perfil() (+2 more)

### Community 96 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, deploy, dev, test:e2e

### Community 97 - "Variante Gree a partir da captura real (troca só os bits)"
Cohesion: 0.21
Nodes (5): Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50), Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105), Perfil Gree Unknown (catálogo nº 102), descartado, Problemas já resolvidos (para não repetir), Versão do servidor (celular 1.0.4, repositório 1.0.5)

### Community 100 - "shutil"
Cohesion: 0.14
Nodes (11): carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar(), filtro(), ler_recortes() (+3 more)

### Community 102 - "cli.py"
Cohesion: 0.10
Nodes (24): ampliar_catalogo(), arquivo_boot(), atualizar(), boot_ativado(), caminho_log(), _carimbo_catalogo(), catalogo_atual(), _cfg_caminho() (+16 more)

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 628 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `Variante Gree a partir da captura real (troca só os bits)`, `test_controle_ir.py`, `Aparelhos`, `Catalogo`, `cli.py`, `ServidorMCP`, `Controlador`, `_extrair_imagens`, `novo_servico`, `vocabulario.py`, `Descoberta`, `Sinal`, `tv do quarto (TV Samsung)`, `servico.py`, `_iniciar`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `Servico` (e.g. with `ServidorMCP` and `Aparelhos`) actually correct?**
  _`Servico` has 17 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.09830508474576272 - nodes in this community are weakly interconnected._
- **Why does `TestPiloto` connect `TestPiloto` to `test_controle_ir.py`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Should `test_controle_ir.py` be split into smaller, more focused modules?**
  _Cohesion score 0.06253652834599649 - nodes in this community are weakly interconnected._
- **Why does `TestPainel` connect `TestPainel` to `test_controle_ir.py`, `novo_servico`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._