# Graph Report - Dialogue-flow  (2026-11-22)

## Corpus Check
- 118 files · ~164,170 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 3, .ir 3, .jsonl 2)

## Summary
- 2397 nodes · 5460 edges · 122 communities (78 shown, 44 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 416 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `0389999d`
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
- test_controle_ir.py
- steps
- painel.py
- TestTelaPorArquivo
- TestServidorMCP
- subprocess
- Catalogo
- protocolos.py
- package.json
- TestImagemNoMcp
- Instalador (instalar.sh)
- Tela
- Pacote do celular dist/controle-ir.zip
- subprocess
- re
- e2e.cjs
- json
- steps
- tela/principal.py
- Servico
- json
- descobrir_rede/principal.py
- Sincronizador
- cli.py
- _ferramentas_piloto
- schema.sql
- normalizar
- canal.py
- TestGreeVariante
- TestOuvirBipe
- sonar/principal.py
- ServidorMCP
- capacidades.py
- test_god_mode.py
- time
- webauthn.js
- session-start.sh
- hashlib
- Execucao
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- exec_cli
- autorizar.js
- app.js
- Canal
- test_controle_ir.py
- HANDOFF.md
- modos/principal.py
- TestPiloto
- time
- .anotar
- observador.py
- TestSono
- godmode-tracker.js
- Passagem de bastão do Dialogue-flow
- Politica
- normalizar
- test_consistencia.py
- local.cjs
- TestExecucao
- piloto.py
- grade
- Cerebros
- BluetoothAdapter
- Piloto
- Motor
- TestArmacao
- ._laco
- _rodar_bloco
- android.bluetooth.le.ScanResult
- PlanoTest
- TestProtocolos
- Problemas já resolvidos (para não repetir)
- Looper
- canal.py
- bluetooth/principal.py
- BluetoothDevice
- Bluetooth.java
- atualizar_conhecimento.sh
- gree_variante.py
- criar_servidor
- analisar.py
- armado
- Contribuir com o Dialogue-flow
- Bluetooth
- Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105)
- nome_da_chamada
- scripts
- .controlar
- Tunel
- grade
- TestLeitorJava
- resolver_grade
- .startScan
- AttributionSource
- construir_app_bluetooth.sh script
- Autonomia do planejador no POCO
- Process
- test_bluetooth.py
- re
- tv do quarto (TV Samsung)
- ._api
- construir_catalogo.py

## God Nodes (most connected - your core abstractions)
1. `Servico` - 62 edges
2. `Celular` - 40 edges
3. `f()` - 38 edges
4. `main()` - 38 edges
5. `Tela` - 37 edges
6. `Descoberta` - 37 edges
7. `Sinal` - 37 edges
8. `TestTelaPorArquivo` - 36 edges
9. `Catalogo` - 35 edges
10. `TestExecutorObjetivo` - 32 edges

## Surprising Connections (you probably didn't know these)
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py
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

## Communities (122 total, 44 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.08
Nodes (59): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+51 more)

### Community 1 - "Descoberta"
Cohesion: 0.13
Nodes (3): agora(), Descoberta, ErroDescoberta

### Community 2 - "TestPainel"
Cohesion: 0.09
Nodes (15): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono (+7 more)

### Community 3 - "Conexao"
Cohesion: 0.24
Nodes (3): carregar_memoria(), Conexao, _texto_do_evento()

### Community 4 - "Sinal"
Cohesion: 0.12
Nodes (12): nome_canonico(), broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta(), impressao_protocolo(), limitar_duracao(), normalizar_pulsos() (+4 more)

### Community 5 - "shutil"
Cohesion: 0.35
Nodes (6): carga_cpu_1min(), js(), ler(), ligado_ha_horas(), main(), rodar()

### Community 6 - "Controlador"
Cohesion: 0.13
Nodes (8): hora_legivel(), Controlador, Etapa, executar(), Plano, normalizar_valor(), valores_equivalentes(), TestControle

### Community 7 - ".passo"
Cohesion: 0.09
Nodes (11): achar(), achar_regra(), escapar_input_text(), eventos(), _Executor, els_fn(), relevantes(), _Falha (+3 more)

### Community 8 - "Celular"
Cohesion: 0.06
Nodes (7): _carregar(), Celular, el(), TestExecutorObjetivo, decidir(), escolher(), TestPilotoVisao

### Community 9 - "TestSonarFrequencia"
Cohesion: 0.06
Nodes (8): _carregar(), _Resposta, TestDescobrirRedeSemWifi, TestDiagnosticoRede, urlopen(), TestSonarFrequencia, testar(), TestTermometroSemResposta

### Community 10 - "test_controle_ir.py"
Cohesion: 0.09
Nodes (8): capacidades(), _curto(), _faixa_txt(), _linhas_aparelho(), resumo_aparelho(), resumo_compacto(), resumo_para_instrucoes(), main()

### Community 11 - "steps"
Cohesion: 0.11
Nodes (20): runs-on, steps, jobs, central, servico, name, on, pull_request (+12 more)

### Community 12 - "painel.py"
Cohesion: 0.20
Nodes (11): painel_cli(), _b64(), estado_valido(), _eventos_novos(), gravar(), _http(), ler(), parear() (+3 more)

### Community 15 - "subprocess"
Cohesion: 0.18
Nodes (10): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+2 more)

### Community 16 - "Catalogo"
Cohesion: 0.11
Nodes (10): Catalogo, estado_representativo(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), normalizar_marca(), _unzip() (+2 more)

### Community 17 - "protocolos.py"
Cohesion: 0.17
Nodes (14): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+6 more)

### Community 18 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, playwright@1.62.1, @simplewebauthn/browser@14.0.0, wrangler@4.165.0 (+10 more)

### Community 19 - "TestImagemNoMcp"
Cohesion: 0.18
Nodes (4): _extrair_imagens(), varrer(), TestImagemNoMcp, TestImagensAninhadas

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

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
Cohesion: 0.21
Nodes (12): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+4 more)

### Community 27 - "steps"
Cohesion: 0.11
Nodes (17): jobs, pacote, name, on, push, workflow_dispatch, runs-on, steps (+9 more)

### Community 28 - "tela/principal.py"
Cohesion: 0.09
Nodes (24): _chave(), classe_janela(), compactos(), _contar(), curto(), dentro(), diferenca(), diferenca_curta() (+16 more)

### Community 29 - "Servico"
Cohesion: 0.17
Nodes (3): EmissorSimulado, Servico, TestDescoberta

### Community 30 - "json"
Cohesion: 0.32
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.16
Nodes (11): classificar(), ficha_upnp(), ip_do_wifi(), ler_inventarios(), main(), sondar(), ssdp(), tcp() (+3 more)

### Community 33 - "cli.py"
Cohesion: 0.05
Nodes (54): ampliar_catalogo(), _api(), armar_cli(), arquivo_boot(), atualizar(), _aviso(), boot_ativado(), caminho_log() (+46 more)

### Community 34 - "_ferramentas_piloto"
Cohesion: 0.28
Nodes (7): casas_xadrez(), foto(), _ferramentas_piloto(), aguardar(), tabuleiro_local(), tela_chess(), vez_no_historico()

### Community 35 - "schema.sql"
Cohesion: 0.12
Nodes (15): aparelhos, chamadas, config, convites, credenciais, desafios, estado, eventos (+7 more)

### Community 36 - "normalizar"
Cohesion: 0.12
Nodes (19): adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos() (+11 more)

### Community 40 - "sonar/principal.py"
Cohesion: 0.23
Nodes (8): analisar_sonar(), escolher_e_testar(), frequencia_lembrada(), gerar_tom(), main(), sugestao_sem_tom(), testar(), volume_musica()

### Community 41 - "ServidorMCP"
Cohesion: 0.08
Nodes (4): resumo_instrucoes(), ServidorMCP, TestCapacidades, TestResumoInstrucoes

### Community 42 - "capacidades.py"
Cohesion: 0.05
Nodes (16): consultar_modelo(), contexto(), executar(), planejar(), RespostaDePlanoInvalida, ErroCapacidade, _hash(), _manifesto() (+8 more)

### Community 43 - "test_god_mode.py"
Cohesion: 0.07
Nodes (7): _Base, _ComServidor, _Servidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos, TestGodModeStmEPontuacao

### Community 44 - "time"
Cohesion: 0.40
Nodes (8): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi()

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 47 - "hashlib"
Cohesion: 0.22
Nodes (6): fontes(), impressao(), checksum(), empacotar(), fontes(), verificar()

### Community 49 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.06
Nodes (34): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+26 more)

### Community 50 - "exec_cli"
Cohesion: 0.19
Nodes (5): exec_cli(), Autorizacao, classificar(), gerar_segredo(), totp()

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.26
Nodes (15): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+7 more)

### Community 54 - "test_controle_ir.py"
Cohesion: 0.07
Nodes (6): catalogo_base(), novo_servico(), TestCatalogo, TestObservador, TestTela, TestTermometro

### Community 55 - "HANDOFF.md"
Cohesion: 0.20
Nodes (4): Comparação do planejador de missões no POCO, Contexto para o Claude Code, Skill graphify (query, explain, path, update), Licenças dos dados de controle

### Community 56 - "modos/principal.py"
Cohesion: 0.09
Nodes (26): Android, aplicar_toque(), aplicar_volume(), atalho(), _avisar(), _chave(), _cond(), definir() (+18 more)

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 58 - "time"
Cohesion: 0.14
Nodes (14): guardar(), lembrar(), Ajudante, _apagar(), captura(), dump_ui(), foto_rapida(), _jar() (+6 more)

### Community 59 - ".anotar"
Cohesion: 0.10
Nodes (5): BluetoothDevice, ScanRecord, ScanResult, ParcelUuid, SparseArray

### Community 60 - "observador.py"
Cohesion: 0.10
Nodes (11): relatar_uso(), Emissor, EmissorTermux, ErroEmissor, apps_usando(), _capacidades_rodando(), em_uso(), quadro() (+3 more)

### Community 61 - "TestSono"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 62 - "godmode-tracker.js"
Cohesion: 0.22
Nodes (4): flagPath, fs, os, path

### Community 63 - "Passagem de bastão do Dialogue-flow"
Cohesion: 0.13
Nodes (15): Arquitetura, Central de Controle no Cloudflare, Configuração por instalação, Continuar em OUTRO repositório, Desenvolver e testar, Mapa do repositório, Missões, rotas e piloto, O que aconteceu até aqui (+7 more)

### Community 65 - "normalizar"
Cohesion: 0.10
Nodes (16): Aparelhos, ErroAparelho, ErroUso, chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar() (+8 more)

### Community 66 - "test_consistencia.py"
Cohesion: 0.05
Nodes (10): _conjunto_js(), _estado_celular(), TestAtualizacaoRecompila, TestEstadoCelularSemProc, TestFerramentasDaMissao, TestParidadeDoBloqueio, TestResumoSemRepeticao, _carregar() (+2 more)

### Community 67 - "local.cjs"
Cohesion: 0.13
Nodes (7): { mkdtemp, rm }, { once }, path, { randomBytes }, { spawn }, { tmpdir }, { unstable_dev }

### Community 69 - "piloto.py"
Cohesion: 0.11
Nodes (9): caixa_da_pergunta(), calcular(), ev(), escolher_pela_conta(), fen(), gravar_memoria(), minha_cor(), quem_mexeu() (+1 more)

### Community 70 - "grade"
Cohesion: 0.11
Nodes (15): _abrir(), _ajudante(), botao_fechar(), calma(), estado_rapido(), fechar_anuncio(), tocar(), _injetar() (+7 more)

### Community 74 - "Piloto"
Cohesion: 0.19
Nodes (3): ler_chave(), Piloto, p()

### Community 77 - "._laco"
Cohesion: 0.31
Nodes (3): chave_quiz(), norm(), quiz_da_tela()

### Community 86 - "Problemas já resolvidos (para não repetir)"
Cohesion: 0.19
Nodes (15): Anúncio dos testes (v1.0.1), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026), Frases (+7 more)

### Community 90 - "bluetooth/principal.py"
Cohesion: 0.11
Nodes (18): buscar(), buscar_app(), buscar_shell(), classificar(), compilar(), distancia(), _ler_marca(), ler_pareados_dumpsys() (+10 more)

### Community 99 - "gree_variante.py"
Cohesion: 0.19
Nodes (11): exportar_jsonl(), checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main() (+3 more)

### Community 100 - "criar_servidor"
Cohesion: 0.22
Nodes (14): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), local_ok() (+6 more)

### Community 102 - "analisar.py"
Cohesion: 0.33
Nodes (5): agenda(), analisar(), extras(), percentil95(), Rodada

### Community 104 - "armado"
Cohesion: 0.32
Nodes (3): armado(), permitido(), 2. Etapa 0 — armação diária local (1.0.23, implementada)

### Community 105 - "Contribuir com o Dialogue-flow"
Cohesion: 0.40
Nodes (5): Central de Controle em desenvolvimento, Contribuir com o Dialogue-flow, Fluxo de contribuição, Primeiro teste no computador ou na nuvem, Usar uma conta e um aparelho próprios

### Community 106 - "Bluetooth"
Cohesion: 0.15
Nodes (5): Runnable, Bluetooth, Runnable, ScanSettings, Builder

### Community 109 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, deploy, dev, test:e2e

### Community 110 - ".controlar"
Cohesion: 0.17
Nodes (14): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50) (+6 more)

### Community 114 - "grade"
Cohesion: 0.10
Nodes (12): aplicar_regras(), els_fn(), elementos(), grade(), ler_bounds(), _ler_grade(), _modelos_do_teclado(), _plano() (+4 more)

### Community 115 - "TestLeitorJava"
Cohesion: 0.05
Nodes (7): _carregar(), TestAppAuxiliar, TestBuscarNoCelular, TestClassificacao, TestCompilar, TestLeitorJava, TestTelaDicaDoCampo

### Community 116 - "resolver_grade"
Cohesion: 0.25
Nodes (5): _caixa(), _conflitos(), resolver_grade(), busca(), resolver_sudoku()

### Community 125 - "Autonomia do planejador no POCO"
Cohesion: 0.40
Nodes (5): Autonomia do planejador no POCO, Dados e reprodução, Próxima bateria, Revisões medidas, Robustez do componente

### Community 129 - "re"
Cohesion: 0.12
Nodes (22): agir(), app_em_foco(), atividade_no_topo(), bloqueado(), bloqueados(), _executar(), escolher(), foco() (+14 more)

### Community 133 - "tv do quarto (TV Samsung)"
Cohesion: 0.26
Nodes (8): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung), Catálogo instalado: base + ampliado (9.380 perfis), Versão do servidor (celular 1.0.4, repositório 1.0.5)

### Community 135 - "._api"
Cohesion: 0.25
Nodes (4): ao_texto(), _confianca(), corpo_api(), prompt_quiz()

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 778 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **44 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `normalizar`, `cli.py`, `Descoberta`, `normalizar`, `Sinal`, `Controlador`, `criar_servidor`, `armado`, `ServidorMCP`, `test_controle_ir.py`, `capacidades.py`, `Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105)`, `.controlar`, `Catalogo`, `Execucao`, `test_controle_ir.py`, `observador.py`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.08208955223880597 - nodes in this community are weakly interconnected._
- **Why does `Catalogo` connect `Catalogo` to `Descoberta`, `cli.py`, `normalizar`, `Sinal`, `tv do quarto (TV Samsung)`, `test_controle_ir.py`, `Servico`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Should `Descoberta` be split into smaller, more focused modules?**
  _Cohesion score 0.13048780487804879 - nodes in this community are weakly interconnected._
- **Why does `criar_servidor()` connect `criar_servidor` to `cli.py`, `normalizar`, `TestPainel`, `ServidorMCP`, `test_controle_ir.py`, `.controlar`, `TestServidorMCP`, `test_controle_ir.py`, `Servico`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._