# Graph Report - Dialogue-flow  (2026-11-21)

## Corpus Check
- 90 files · ~139,029 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 12 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 1901 nodes · 4369 edges · 112 communities (72 shown, 40 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 318 edges (avg confidence: 0.87)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `42ff118c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- test_controle_ir.py
- TestPainel
- Conexao
- ErroUso
- Catalogo
- Controlador
- .passo
- Registro
- TestSonarFrequencia
- Politica
- steps
- re
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
- tela/principal.py
- _ferramentas_piloto
- tv do quarto (TV Samsung)
- diagnostico_rede/principal.py
- Servico
- agir
- termometro/principal.py
- schema.sql
- painel.py
- Execucao
- package.json
- TestOuvirBipe
- sonar/principal.py
- _extrair_imagens
- observador.py
- test_god_mode.py
- protocolos.py
- webauthn.js
- session-start.sh
- criar_servidor
- ambiente_missao.py
- exec_cli
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- autorizar.js
- app.js
- Canal
- time
- TestAtualizacaoRecompila
- ErroSinal
- TestPiloto
- TestCapacidades
- CLAUDE.md
- .test_canal_repassa_chamada_e_aviso
- ar do quarto (ar-condicionado Gree GWH09KF)
- _iniciar
- Passagem de bastão do Dialogue-flow
- TestExecucao
- resumo_para_instrucoes
- f
- local.cjs
- test_consistencia.py
- ._api
- piloto.py
- ServidorMCP
- Cerebros
- caminho_log
- Piloto
- Motor
- novo_servico
- Notificador
- vocabulario.py
- grade
- PlanoTest
- TestGreeVariante
- TestTunel
- TestSono
- godmode-tracker.js
- pacote.py
- modulo_embutido
- capacidades.py
- TestServidorMCP
- TestObservador
- TestArmacao
- .impressao
- _Servidor
- servico.py
- gree_variante.py
- TestFormatos
- scripts
- TestTela
- atualizar_conhecimento.sh
- TestTermometro
- shutil
- TestParidadeDoBloqueio
- cli.py
- 4. Mapa de oportunidades
- Autonomia do planejador no POCO
- Contribuir com o Dialogue-flow
- TestProtocolos
- atualizar
- execucao.py
- TestGodModeStmEPontuacao

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
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
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

## Communities (112 total, 40 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.08
Nodes (59): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+51 more)

### Community 1 - "test_controle_ir.py"
Cohesion: 0.09
Nodes (3): main(), preparar(), TestVocabulario

### Community 2 - "TestPainel"
Cohesion: 0.09
Nodes (16): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 2. Etapa 0 — armação diária local (1.0.23, implementada), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1) (+8 more)

### Community 4 - "ErroUso"
Cohesion: 0.16
Nodes (5): Aparelhos, ErroUso, slug(), Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper), Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas)

### Community 5 - "Catalogo"
Cohesion: 0.13
Nodes (9): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), _unzip() (+1 more)

### Community 6 - "Controlador"
Cohesion: 0.16
Nodes (7): Controlador, Etapa, Plano, EmissorSimulado, normalizar_valor(), valores_equivalentes(), TestControle

### Community 7 - ".passo"
Cohesion: 0.11
Nodes (7): compactos(), eventos(), _Executor, els_fn(), relevantes(), _Falha, _Interrompido

### Community 8 - "Registro"
Cohesion: 0.20
Nodes (5): ErroCapacidade, _hash(), _manifesto(), Registro, capacidade_cli()

### Community 9 - "TestSonarFrequencia"
Cohesion: 0.07
Nodes (7): _carregar(), _Resposta, TestDiagnosticoRede, urlopen(), TestSonarFrequencia, testar(), TestTermometroSemResposta

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "re"
Cohesion: 0.11
Nodes (13): achar(), achar_regra(), aplicar_regras(), els_fn(), botao_fechar(), janela_nova(), normalizar(), reflexos() (+5 more)

### Community 14 - "Problemas já resolvidos (para não repetir)"
Cohesion: 0.16
Nodes (16): Anúncio dos testes (v1.0.1), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026), Frases (+8 more)

### Community 15 - "os"
Cohesion: 0.18
Nodes (10): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+2 more)

### Community 16 - "Descoberta"
Cohesion: 0.12
Nodes (3): agora(), Descoberta, ErroDescoberta

### Community 17 - "Sinal"
Cohesion: 0.18
Nodes (19): adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos() (+11 more)

### Community 18 - "Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude"
Cohesion: 0.12
Nodes (16): Botão Stockfish para estudos, Capacidades plugáveis (ferramentas novas sem mexer no núcleo), Cobertura dos testes, Como funciona, Conectar ao ChatGPT ou ao Claude, Descoberta, Desenvolvimento, Dialogue-flow · Controle do Android pelo ChatGPT e pelo Claude (+8 more)

### Community 19 - "main"
Cohesion: 0.31
Nodes (7): console(), url_quando_pronta(), estado_servidor(), parar_servico(), _pid_do_servico(), _saude(), servico_ativo()

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 24 - "TestSegundoPlano"
Cohesion: 0.08
Nodes (7): catalogo_base(), TestCatalogo, TestRepositorio, TestSegundoPlano, abrir_console(), reiniciado(), TestStockfishLocal

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
Nodes (19): _caixa(), _chave(), _conflitos(), _contar(), curto(), diferenca(), diferenca_curta(), escapar_input_text() (+11 more)

### Community 29 - "_ferramentas_piloto"
Cohesion: 0.18
Nodes (10): atividade_no_topo(), casas_xadrez(), foto(), _ferramentas_piloto(), aguardar(), tabuleiro_local(), tela_chess(), tocar() (+2 more)

### Community 30 - "tv do quarto (TV Samsung)"
Cohesion: 0.27
Nodes (7): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung), Catálogo instalado: base + ampliado (9.380 perfis)

### Community 31 - "diagnostico_rede/principal.py"
Cohesion: 0.09
Nodes (23): agenda(), analisar(), extras(), percentil95(), Comparação do planejador de missões no POCO, Rodada, classificar(), ficha_upnp() (+15 more)

### Community 33 - "agir"
Cohesion: 0.15
Nodes (17): agir(), app_em_foco(), bloqueado(), bloqueados(), _bloqueio_de_toque(), _executar(), escolher(), foco() (+9 more)

### Community 34 - "termometro/principal.py"
Cohesion: 0.29
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

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

### Community 41 - "_extrair_imagens"
Cohesion: 0.40
Nodes (3): _extrair_imagens(), varrer(), TestImagensAninhadas

### Community 42 - "observador.py"
Cohesion: 0.10
Nodes (11): relatar_uso(), Emissor, EmissorTermux, ErroEmissor, apps_usando(), _capacidades_rodando(), em_uso(), quadro() (+3 more)

### Community 43 - "test_god_mode.py"
Cohesion: 0.11
Nodes (5): _Base, _ComServidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos

### Community 44 - "protocolos.py"
Cohesion: 0.17
Nodes (15): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+7 more)

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 47 - "criar_servidor"
Cohesion: 0.24
Nodes (13): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), local_ok() (+5 more)

### Community 48 - "ambiente_missao.py"
Cohesion: 0.17
Nodes (8): consultar_modelo(), contexto(), escolher(), executar(), planejar(), RespostaDePlanoInvalida, armado(), permitido()

### Community 50 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.17
Nodes (12): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade, 8. Próximos experimentos (ordem sugerida) (+4 more)

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
Cohesion: 0.13
Nodes (18): Ajudante, _ajudante(), _apagar(), captura(), dump_ui(), estado_rapido(), foto_rapida(), _jar() (+10 more)

### Community 56 - "ErroSinal"
Cohesion: 0.21
Nodes (5): broadlink_para_pulsos(), ErroSinal, limitar_duracao(), normalizar_pulsos(), pronto_para_pulsos()

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 59 - "CLAUDE.md"
Cohesion: 0.27
Nodes (4): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, empacotar.sh script

### Community 61 - "ar do quarto (ar-condicionado Gree GWH09KF)"
Cohesion: 0.14
Nodes (16): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50) (+8 more)

### Community 62 - "_iniciar"
Cohesion: 0.29
Nodes (9): armar_cli(), _aviso(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir(), mostrar_url() (+1 more)

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 66 - "f"
Cohesion: 0.24
Nodes (7): filtro(), ler_recortes(), main(), reduzir(), validar_recorte(), gravar(), f()

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 68 - "test_consistencia.py"
Cohesion: 0.14
Nodes (4): _estado_celular(), TestEstadoCelularSemProc, TestFerramentasDaMissao, TestResumoSemRepeticao

### Community 69 - "._api"
Cohesion: 0.22
Nodes (5): ao_texto(), _confianca(), corpo_api(), ler_chave(), prompt_quiz()

### Community 70 - "piloto.py"
Cohesion: 0.18
Nodes (7): chave_quiz(), fen(), gravar_memoria(), norm(), quem_mexeu(), quiz_da_tela(), _texto_do_evento()

### Community 73 - "caminho_log"
Cohesion: 0.20
Nodes (6): caminho_log(), iniciar_em_segundo_plano(), mostrar_log(), _redirecionar_para_log(), _registrar(), _seguir_log()

### Community 75 - "Motor"
Cohesion: 0.25
Nodes (3): minha_cor(), Motor, tabuleiro_txt()

### Community 78 - "vocabulario.py"
Cohesion: 0.14
Nodes (12): normalizar_marca(), categoria_canonica(), chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar(), sem_acentos() (+4 more)

### Community 79 - "grade"
Cohesion: 0.10
Nodes (15): _abrir(), calma(), classe_janela(), dentro(), elementos(), em_anuncio(), fechar_anuncio(), grade() (+7 more)

### Community 84 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

### Community 85 - "pacote.py"
Cohesion: 0.20
Nodes (7): _classes(), impressao_bruta(), _quadros(), checksum(), empacotar(), fontes(), verificar()

### Community 86 - "modulo_embutido"
Cohesion: 0.39
Nodes (5): modulo_embutido(), abrir(), estudar(), mostrar(), piloto_local()

### Community 88 - "TestServidorMCP"
Cohesion: 0.14
Nodes (3): Origens, Reenvios, TestServidorMCP

### Community 93 - "servico.py"
Cohesion: 0.16
Nodes (8): capacidades(), _curto(), ErroAparelho, _faixa_txt(), hora_legivel(), _linhas_aparelho(), resumo_aparelho(), executar()

### Community 94 - "gree_variante.py"
Cohesion: 0.15
Nodes (12): arquivos_cc0(), main(), checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes() (+4 more)

### Community 96 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, deploy, dev, test:e2e

### Community 100 - "shutil"
Cohesion: 0.24
Nodes (6): carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar()

### Community 102 - "cli.py"
Cohesion: 0.16
Nodes (21): ampliar_catalogo(), _api(), arquivo_boot(), boot_ativado(), _carimbo_catalogo(), carregar_config(), catalogo_atual(), _cfg_caminho() (+13 more)

### Community 103 - "4. Mapa de oportunidades"
Cohesion: 0.33
Nodes (6): 4. Mapa de oportunidades, Casa e rede, Celular e Android, Computadores, nuvem e agentes, O próprio sistema, Observar o resultado (agir → medir → ajustar)

### Community 104 - "Autonomia do planejador no POCO"
Cohesion: 0.40
Nodes (5): Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente

### Community 105 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 629 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **40 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `test_controle_ir.py`, `ErroUso`, `Catalogo`, `Controlador`, `Registro`, `Descoberta`, `Sinal`, `tv do quarto (TV Samsung)`, `Execucao`, `observador.py`, `criar_servidor`, `ErroSinal`, `ar do quarto (ar-condicionado Gree GWH09KF)`, `_iniciar`, `ServidorMCP`, `novo_servico`, `capacidades.py`, `servico.py`, `cli.py`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `Servico` (e.g. with `ServidorMCP` and `Aparelhos`) actually correct?**
  _`Servico` has 17 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.08208955223880597 - nodes in this community are weakly interconnected._
- **Why does `Tunel` connect `Tunel` to `shutil`, `cli.py`, `Problemas já resolvidos (para não repetir)`, `TestTunel`, `TestArmacao`, `_iniciar`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Should `test_controle_ir.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0944741532976827 - nodes in this community are weakly interconnected._
- **Why does `Catalogo` connect `Catalogo` to `Servico`, `cli.py`, `vocabulario.py`, `Descoberta`, `Sinal`, `tv do quarto (TV Samsung)`, `ErroSinal`, `.impressao`, `servico.py`, `_iniciar`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._