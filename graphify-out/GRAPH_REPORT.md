# Graph Report - Dialogue-flow  (2026-11-21)

## Corpus Check
- 115 files · ~158,712 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 2309 nodes · 5222 edges · 127 communities (78 shown, 49 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 401 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `45261935`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- Descoberta
- TestPainel
- Conexao
- Sinal
- shutil
- Controlador
- .passo
- Celular
- TestSonarFrequencia
- pathlib
- steps
- painel.py
- TestTelaPorArquivo
- test_controle_ir.py
- subprocess
- Catalogo
- protocolos.py
- package.json
- TestImagemNoMcp
- Instalador (instalar.sh)
- Tela
- cli.py
- subprocess
- re
- e2e.cjs
- json
- steps
- tela/principal.py
- Servico
- _iniciar
- descobrir_rede/principal.py
- gree_variante.py
- servidor.py
- TestParidadeDoBloqueio
- schema.sql
- normalizar
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- Notificador
- TestOuvirBipe
- sonar/principal.py
- ServidorMCP
- capacidades.py
- test_god_mode.py
- diagnostico_rede/principal.py
- webauthn.js
- session-start.sh
- subprocess
- ambiente_missao.py
- Aparelhos
- exec_cli
- autorizar.js
- app.js
- canal.py
- TestTermometro
- HANDOFF.md
- termometro/principal.py
- TestPiloto
- os
- .anotar
- Segurança do controle-ir: administração externa, armação e auditoria
- TestSono
- godmode-tracker.js
- Passagem de bastão do Dialogue-flow
- Politica
- TestProtocolos
- criar_servidor
- local.cjs
- TestExecucao
- piloto.py
- _ajudante
- main
- Cerebros
- BluetoothAdapter
- Piloto
- Motor
- TestArmacao
- ._laco
- TestPilotoVisao
- _ferramentas_piloto
- TestSegundoPlano
- ErroEmissor
- android.bluetooth.le.ScanResult
- tv do quarto (TV Samsung)
- PlanoTest
- .controlar
- Reenvios
- .main
- atualizar
- Ajudante
- bluetooth/principal.py
- BluetoothDevice
- _Servidor
- resumo_para_instrucoes
- Bluetooth.java
- TestCapacidades
- novo_servico
- atualizar_conhecimento.sh
- Estado atual da instalação (17/11/2026)
- catalogo_base
- TestVocabulario
- TestServidorMCP
- armado
- test_consistencia.py
- Contribuir com o Dialogue-flow
- Bluetooth
- calcular
- TestGreeVariante
- scripts
- .test_sincronizar_com_painel_falso
- Tunel
- TestObservador
- TestLeitorJava
- CLAUDE.md
- .startScan
- AttributionSource
- construir_app_bluetooth.sh script
- Process
- f

## God Nodes (most connected - your core abstractions)
1. `Servico` - 62 edges
2. `Celular` - 40 edges
3. `main()` - 38 edges
4. `Tela` - 37 edges
5. `Descoberta` - 37 edges
6. `Sinal` - 37 edges
7. `TestTelaPorArquivo` - 36 edges
8. `Catalogo` - 35 edges
9. `f()` - 35 edges
10. `TestExecutorObjetivo` - 32 edges

## Surprising Connections (you probably didn't know these)
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
- `3a. Central de Controle (1.0.24, implementada) — `painel/`` --references--> `TestPainel`  [EXTRACTED]
  docs/seguranca.md → testes/test_controle_ir.py
- `variante()` --implements--> `Variante Gree a partir da captura real (troca só os bits)`  [INFERRED]
  ferramentas/gree_variante.py → docs/aparelhos/quarto/ar-do-quarto.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (127 total, 49 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.08
Nodes (59): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+51 more)

### Community 1 - "Descoberta"
Cohesion: 0.13
Nodes (3): agora(), Descoberta, ErroDescoberta

### Community 3 - "Conexao"
Cohesion: 0.24
Nodes (3): carregar_memoria(), Conexao, _texto_do_evento()

### Community 4 - "Sinal"
Cohesion: 0.09
Nodes (17): ErroFormato, escrever_flipper(), exportar(), _hex_le(), ler_sinal_texto(), sinal(), sinais_pronto(), _sinal_smartir() (+9 more)

### Community 5 - "shutil"
Cohesion: 0.36
Nodes (6): carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar()

### Community 6 - "Controlador"
Cohesion: 0.09
Nodes (9): Controlador, Etapa, Plano, Emissor, EmissorSimulado, normalizar_valor(), valores_equivalentes(), TestControle (+1 more)

### Community 7 - ".passo"
Cohesion: 0.10
Nodes (10): achar(), achar_regra(), eventos(), _Executor, els_fn(), relevantes(), _Falha, _Interrompido (+2 more)

### Community 8 - "Celular"
Cohesion: 0.08
Nodes (6): _carregar(), Celular, el(), TestExecutorObjetivo, decidir(), escolher()

### Community 9 - "TestSonarFrequencia"
Cohesion: 0.06
Nodes (8): _carregar(), _Resposta, TestDescobrirRedeSemWifi, TestDiagnosticoRede, urlopen(), TestSonarFrequencia, testar(), TestTermometroSemResposta

### Community 10 - "pathlib"
Cohesion: 0.12
Nodes (4): preparar(), TestApkAtualizado, TestManifesto, TestGodModeStmEPontuacao

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "painel.py"
Cohesion: 0.13
Nodes (11): painel_cli(), _b64(), estado_valido(), _eventos_novos(), gravar(), _http(), ler(), parear() (+3 more)

### Community 14 - "test_controle_ir.py"
Cohesion: 0.12
Nodes (11): capacidades(), _curto(), _faixa_txt(), hora_legivel(), _linhas_aparelho(), resumo_aparelho(), executar(), _classes() (+3 more)

### Community 15 - "subprocess"
Cohesion: 0.18
Nodes (10): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+2 more)

### Community 16 - "Catalogo"
Cohesion: 0.10
Nodes (12): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), normalizar_marca() (+4 more)

### Community 17 - "protocolos.py"
Cohesion: 0.15
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 18 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+10 more)

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 22 - "cli.py"
Cohesion: 0.13
Nodes (20): _api(), caminho_log(), carregar_config(), _cfg_caminho(), console(), url_quando_pronta(), estado_servidor(), iniciar_em_segundo_plano() (+12 more)

### Community 23 - "subprocess"
Cohesion: 0.27
Nodes (5): filtro(), ler_recortes(), main(), reduzir(), validar_recorte()

### Community 24 - "re"
Cohesion: 0.12
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
Cohesion: 0.06
Nodes (30): _caixa(), _chave(), compactos(), _conflitos(), _contar(), curto(), dentro(), diferenca() (+22 more)

### Community 29 - "Servico"
Cohesion: 0.06
Nodes (11): ErroCapacidade, _hash(), _manifesto(), Registro, capacidade_cli(), Execucao, ErroUso, Servico (+3 more)

### Community 30 - "_iniciar"
Cohesion: 0.27
Nodes (10): _aviso(), _carimbo_catalogo(), catalogo_atual(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir() (+2 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.16
Nodes (11): classificar(), ficha_upnp(), ip_do_wifi(), ler_inventarios(), main(), sondar(), ssdp(), tcp() (+3 more)

### Community 32 - "gree_variante.py"
Cohesion: 0.23
Nodes (10): checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main(), perfil() (+2 more)

### Community 35 - "schema.sql"
Cohesion: 0.12
Nodes (15): aparelhos, chamadas, config, convites, credenciais, desafios, estado, eventos (+7 more)

### Community 36 - "normalizar"
Cohesion: 0.14
Nodes (21): adicionar_comando(), comando(), importar_texto(), indice_comandos(), ler_flipper(), ler_smartir(), novo_perfil(), _traduz() (+13 more)

### Community 37 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.06
Nodes (34): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+26 more)

### Community 40 - "sonar/principal.py"
Cohesion: 0.23
Nodes (8): analisar_sonar(), escolher_e_testar(), frequencia_lembrada(), gerar_tom(), main(), sugestao_sem_tom(), testar(), volume_musica()

### Community 42 - "capacidades.py"
Cohesion: 0.18
Nodes (4): resumo_instrucoes(), _extrair_imagens(), varrer(), TestImagensAninhadas

### Community 43 - "test_god_mode.py"
Cohesion: 0.11
Nodes (5): _Base, _ComServidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos

### Community 44 - "diagnostico_rede/principal.py"
Cohesion: 0.36
Nodes (8): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi()

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 47 - "subprocess"
Cohesion: 0.19
Nodes (6): arquivos_cc0(), main(), checksum(), empacotar(), fontes(), verificar()

### Community 48 - "ambiente_missao.py"
Cohesion: 0.25
Nodes (5): consultar_modelo(), contexto(), executar(), planejar(), RespostaDePlanoInvalida

### Community 50 - "exec_cli"
Cohesion: 0.19
Nodes (4): exec_cli(), Autorizacao, gerar_segredo(), totp()

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.26
Nodes (15): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+7 more)

### Community 53 - "canal.py"
Cohesion: 0.05
Nodes (11): agenda(), analisar(), extras(), percentil95(), Rodada, Canal, _mascarar(), nome_da_chamada() (+3 more)

### Community 55 - "HANDOFF.md"
Cohesion: 0.17
Nodes (7): Comparação do planejador de missões no POCO, Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente, Licenças dos dados de controle

### Community 56 - "termometro/principal.py"
Cohesion: 0.29
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 58 - "os"
Cohesion: 0.12
Nodes (23): lembrar(), agir(), _ajudante(), _apagar(), app_em_foco(), bloqueado(), _bloqueio_de_toque(), captura() (+15 more)

### Community 59 - ".anotar"
Cohesion: 0.11
Nodes (5): BluetoothDevice, ScanRecord, ScanResult, ParcelUuid, SparseArray

### Community 60 - "Segurança do controle-ir: administração externa, armação e auditoria"
Cohesion: 0.18
Nodes (11): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono (+3 more)

### Community 61 - "TestSono"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 62 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 64 - "Politica"
Cohesion: 0.26
Nodes (3): armar_cli(), Politica, fim_do_dia()

### Community 66 - "criar_servidor"
Cohesion: 0.24
Nodes (13): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), local_ok() (+5 more)

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 69 - "piloto.py"
Cohesion: 0.12
Nodes (7): caixa_da_pergunta(), _confianca(), fen(), gravar_memoria(), minha_cor(), quem_mexeu(), tabuleiro_txt()

### Community 70 - "_ajudante"
Cohesion: 0.08
Nodes (21): _abrir(), aplicar_regras(), els_fn(), botao_fechar(), calma(), classe_janela(), em_anuncio(), escolher() (+13 more)

### Community 71 - "main"
Cohesion: 0.14
Nodes (12): ampliar_catalogo(), arquivo_boot(), boot_ativado(), criar_atalhos(), iniciar(), inicio_automatico(), main(), pasta_atalhos() (+4 more)

### Community 72 - "Cerebros"
Cohesion: 0.12
Nodes (5): Cerebros, ao_texto(), julgar_depois(), corpo_api(), prompt_quiz()

### Community 74 - "Piloto"
Cohesion: 0.19
Nodes (3): ler_chave(), Piloto, p()

### Community 77 - "._laco"
Cohesion: 0.36
Nodes (3): chave_quiz(), norm(), quiz_da_tela()

### Community 79 - "_ferramentas_piloto"
Cohesion: 0.11
Nodes (15): atividade_no_topo(), bloqueados(), casas_xadrez(), escapar_input_text(), foto(), _ferramentas_piloto(), aguardar(), tabuleiro_local() (+7 more)

### Community 80 - "TestSegundoPlano"
Cohesion: 0.06
Nodes (20): modulo_embutido(), relatar_uso(), abrir(), configurar(), estudar(), ler_preferencias(), mostrar(), Preferencias (+12 more)

### Community 83 - "tv do quarto (TV Samsung)"
Cohesion: 0.21
Nodes (9): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung), Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas), Catálogo instalado: base + ampliado (9.380 perfis) (+1 more)

### Community 85 - ".controlar"
Cohesion: 0.17
Nodes (14): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50) (+6 more)

### Community 87 - ".main"
Cohesion: 0.17
Nodes (4): ScanSettings, Builder, Handler, Looper

### Community 90 - "bluetooth/principal.py"
Cohesion: 0.09
Nodes (22): buscar(), buscar_app(), buscar_shell(), classificar(), compilar(), distancia(), guardar(), _ler_marca() (+14 more)

### Community 99 - "Estado atual da instalação (17/11/2026)"
Cohesion: 0.19
Nodes (15): Anúncio dos testes (v1.0.1), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026), Frases (+7 more)

### Community 104 - "test_consistencia.py"
Cohesion: 0.11
Nodes (5): _estado_celular(), TestAtualizacaoRecompila, TestEstadoCelularSemProc, TestFerramentasDaMissao, TestResumoSemRepeticao

### Community 105 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

### Community 106 - "Bluetooth"
Cohesion: 0.15
Nodes (4): Busca, Runnable, Bluetooth, Runnable

### Community 107 - "calcular"
Cohesion: 0.40
Nodes (3): calcular(), ev(), escolher_pela_conta()

### Community 109 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, deploy, dev, test:e2e

### Community 110 - ".test_sincronizar_com_painel_falso"
Cohesion: 0.60
Nodes (3): do_GET(), do_POST(), _r()

### Community 115 - "TestLeitorJava"
Cohesion: 0.05
Nodes (7): _carregar(), TestAppAuxiliar, TestBuscarNoCelular, TestClassificacao, TestCompilar, TestLeitorJava, TestTelaDicaDoCampo

### Community 116 - "CLAUDE.md"
Cohesion: 0.27
Nodes (4): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, empacotar.sh script

### Community 129 - "f"
Cohesion: 0.13
Nodes (12): executar(), _executar(), main(), reflexos(), _regex_bloqueados(), _regras(), _resumo_volta(), rotina() (+4 more)

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 752 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **49 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `Descoberta`, `servidor.py`, `criar_servidor`, `normalizar`, `Sinal`, `Controlador`, `novo_servico`, `ServidorMCP`, `capacidades.py`, `pathlib`, `test_controle_ir.py`, `Catalogo`, `Aparelhos`, `ErroEmissor`, `tv do quarto (TV Samsung)`, `.controlar`, `cli.py`, `_iniciar`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.08208955223880597 - nodes in this community are weakly interconnected._
- **Why does `TestTelaPorArquivo` connect `TestTelaPorArquivo` to `test_controle_ir.py`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Should `Descoberta` be split into smaller, more focused modules?**
  _Cohesion score 0.1346153846153846 - nodes in this community are weakly interconnected._
- **Why does `Catalogo` connect `Catalogo` to `Descoberta`, `Sinal`, `main`, `test_controle_ir.py`, `tv do quarto (TV Samsung)`, `Servico`, `_iniciar`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._