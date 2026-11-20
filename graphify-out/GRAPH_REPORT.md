# Graph Report - Dialogue-flow  (2026-11-20)

## Corpus Check
- 72 files · ~125,886 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 3, .ir 3, .gz 1)

## Summary
- 1641 nodes · 3832 edges · 93 communities (57 shown, 36 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 282 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `0f6ff2d9`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- time
- TestPainel
- Conexao
- normalizar
- Sinal
- Controlador
- .passo
- capacidades.py
- Execucao
- Politica
- Catalogo
- grade
- TestTelaPorArquivo
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- os
- Servico
- Sinal
- Servico
- main
- Instalador (instalar.sh)
- Tela
- Licenças dos dados
- Tunel
- TestSegundoPlano
- e2e.cjs
- json
- test_controle_ir.py
- re
- gree_variante.py
- descobrir_rede/principal.py
- cli.py
- tela/principal.py
- termometro/principal.py
- painel.py
- TestOuvirBipe
- package.json
- TestSono
- sonar/principal.py
- TestImagemNoMcp
- observador.py
- test_god_mode.py
- protocolos.py
- webauthn.js
- session-start.sh
- f
- TestTela
- exec_cli
- ar do quarto (ar-condicionado Gree GWH09KF)
- autorizar.js
- app.js
- Canal
- time
- TestCapacidades
- Problemas já resolvidos (para não repetir)
- TestPiloto
- diagnostico_rede/principal.py
- CLAUDE.md
- .test_canal_repassa_chamada_e_aviso
- ar do escritório (ar-condicionado Carrier)
- _iniciar
- tv do quarto (TV Samsung)
- TestExecucao
- resumo_para_instrucoes
- criar_servidor
- resolver_grade
- construir_catalogo.py
- piloto.py
- ServidorMCP
- Cerebros
- Piloto
- ._laco_xadrez
- ._api
- Notificador
- EmissorSimulado
- tela/principal.py
- .decidir
- TestGreeVariante
- TestTermometro
- Sincronizador
- WebSocket
- verificar_cliente_mcp.py
- armado
- Problemas já resolvidos (para não repetir)
- TestArmacao
- TestObservador
- TestProtocolos

## God Nodes (most connected - your core abstractions)
1. `Servico` - 51 edges
2. `TestTelaPorArquivo` - 36 edges
3. `Descoberta` - 36 edges
4. `Sinal` - 36 edges
5. `Tela` - 34 edges
6. `Catalogo` - 34 edges
7. `main()` - 32 edges
8. `criar_servidor()` - 29 edges
9. `_iniciar()` - 28 edges
10. `normalizar()` - 26 edges

## Surprising Connections (you probably didn't know these)
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `variante()` --implements--> `Variante Gree a partir da captura real (troca só os bits)`  [INFERRED]
  ferramentas/gree_variante.py → docs/aparelhos/quarto/ar-do-quarto.md
- `Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper)` --conceptually_related_to--> `ler_flipper()`  [INFERRED]
  docs/aparelhos/README.md → controle-ir/controle_ir/formatos.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `ampliar_catalogo()`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/cli.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (93 total, 36 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.08
Nodes (59): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+51 more)

### Community 1 - "time"
Cohesion: 0.24
Nodes (6): capacidades(), _curto(), ErroAparelho, _faixa_txt(), _linhas_aparelho(), resumo_aparelho()

### Community 2 - "TestPainel"
Cohesion: 0.09
Nodes (15): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono (+7 more)

### Community 4 - "normalizar"
Cohesion: 0.12
Nodes (15): Aparelhos, normalizar_marca(), categoria_canonica(), chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar() (+7 more)

### Community 5 - "Sinal"
Cohesion: 0.13
Nodes (19): adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos() (+11 more)

### Community 6 - "Controlador"
Cohesion: 0.09
Nodes (10): Controlador, Etapa, executar(), Plano, Emissor, EmissorTermux, ErroEmissor, normalizar_valor() (+2 more)

### Community 7 - ".passo"
Cohesion: 0.12
Nodes (5): _Executor, relevantes(), _Falha, _Interrompido, _janela_curta()

### Community 8 - "capacidades.py"
Cohesion: 0.21
Nodes (5): ErroCapacidade, _hash(), _manifesto(), Registro, capacidade_cli()

### Community 10 - "Politica"
Cohesion: 0.20
Nodes (6): armar_cli(), painel_cli(), Politica, estado_valido(), ler(), fim_do_dia()

### Community 11 - "Catalogo"
Cohesion: 0.12
Nodes (11): Catalogo, estado_representativo(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), _unzip(), _zip() (+3 more)

### Community 12 - "grade"
Cohesion: 0.10
Nodes (20): _abrir(), _ajudante(), aplicar_regras(), els_fn(), calma(), dentro(), eventos(), els_fn() (+12 more)

### Community 14 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.04
Nodes (46): 10. Segurança — o essencial (detalhes: `docs/seguranca.md`), 11. Continuar em OUTRO repositório, 12. Próximos passos sugeridos, 1. O que é, 2. Arquitetura, 3. Mapa do repositório, 4. Desenvolver e testar, 5. Publicar no celular (o ciclo que se repete) (+38 more)

### Community 15 - "os"
Cohesion: 0.11
Nodes (11): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+3 more)

### Community 16 - "Servico"
Cohesion: 0.12
Nodes (4): agora(), hora_legivel(), Descoberta, ErroDescoberta

### Community 17 - "Sinal"
Cohesion: 0.13
Nodes (10): broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta(), limitar_duracao(), normalizar_pulsos(), pronto_para_pulsos(), pulsos_para_broadlink() (+2 more)

### Community 18 - "Servico"
Cohesion: 0.16
Nodes (3): ErroUso, Servico, 2. Etapa 0 — armação diária local (1.0.23, implementada)

### Community 19 - "main"
Cohesion: 0.20
Nodes (13): _api(), carregar_config(), _cfg_caminho(), console(), url_quando_pronta(), estado_servidor(), main(), parar_servico() (+5 more)

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 24 - "TestSegundoPlano"
Cohesion: 0.20
Nodes (3): TestRepositorio, TestSegundoPlano, abrir_console()

### Community 25 - "e2e.cjs"
Cohesion: 0.09
Nodes (14): flagPath, fs, os, path, celular(), { chromium }, { execFileSync, spawn }, fs (+6 more)

### Community 26 - "json"
Cohesion: 0.23
Nodes (12): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+4 more)

### Community 28 - "test_controle_ir.py"
Cohesion: 0.15
Nodes (3): catalogo_base(), TestCatalogo, TestVocabulario

### Community 29 - "re"
Cohesion: 0.16
Nodes (9): achar(), achar_regra(), agir(), botao_fechar(), escapar_input_text(), janela_nova(), _linhas_do_passo(), normalizar() (+1 more)

### Community 30 - "gree_variante.py"
Cohesion: 0.20
Nodes (11): exportar_jsonl(), checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main() (+3 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.18
Nodes (9): classificar(), ficha_upnp(), ip_do_wifi(), main(), sondar(), ssdp(), tcp(), udp() (+1 more)

### Community 32 - "cli.py"
Cohesion: 0.10
Nodes (18): arquivo_boot(), atualizar(), boot_ativado(), caminho_log(), _carimbo_catalogo(), catalogo_atual(), criar_atalhos(), iniciar_em_segundo_plano() (+10 more)

### Community 33 - "tela/principal.py"
Cohesion: 0.11
Nodes (15): atividade_no_topo(), bloqueado(), bloqueados(), casas_xadrez(), elementos(), foto(), _ferramentas_piloto(), aguardar() (+7 more)

### Community 34 - "termometro/principal.py"
Cohesion: 0.33
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 36 - "painel.py"
Cohesion: 0.17
Nodes (7): _b64(), gravar(), _http(), parear(), sincronizar(), verificar(), verificar_requisicao()

### Community 38 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, @simplewebauthn/browser@14.0.0, wrangler@4.165.0, name (+10 more)

### Community 39 - "TestSono"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 40 - "sonar/principal.py"
Cohesion: 0.20
Nodes (7): js(), rodar(), analisar_sonar(), gerar_tom(), main(), testar(), volume_musica()

### Community 41 - "TestImagemNoMcp"
Cohesion: 0.18
Nodes (4): _extrair_imagens(), varrer(), TestImagemNoMcp, TestImagensAninhadas

### Community 42 - "observador.py"
Cohesion: 0.18
Nodes (8): modulo_embutido(), apps_usando(), _capacidades_rodando(), em_uso(), quadro(), recursos_do_comando(), _tarefas(), _tela()

### Community 43 - "test_god_mode.py"
Cohesion: 0.06
Nodes (7): _Base, _ComServidor, _Servidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos, TestGodModeStmEPontuacao

### Community 44 - "protocolos.py"
Cohesion: 0.13
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 47 - "f"
Cohesion: 0.16
Nodes (11): filtro(), ler_recortes(), main(), reduzir(), validar_recorte(), carregar_memoria(), gravar_memoria(), reflexos() (+3 more)

### Community 49 - "exec_cli"
Cohesion: 0.19
Nodes (4): exec_cli(), Autorizacao, gerar_segredo(), totp()

### Community 50 - "ar do quarto (ar-condicionado Gree GWH09KF)"
Cohesion: 0.22
Nodes (8): Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50), Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105), Perfil Gree Unknown (catálogo nº 102), descartado, Ligar/desligar diretos (energia_ligar 0x99, energia_desligar 0x98)

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.28
Nodes (14): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+6 more)

### Community 54 - "time"
Cohesion: 0.13
Nodes (13): Ajudante, _apagar(), captura(), dump_ui(), estado_rapido(), foto_rapida(), _jar(), _jpeg() (+5 more)

### Community 56 - "Problemas já resolvidos (para não repetir)"
Cohesion: 0.19
Nodes (14): Anúncio dos testes (v1.0.1), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026), Frases (+6 more)

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 58 - "diagnostico_rede/principal.py"
Cohesion: 0.36
Nodes (8): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi()

### Community 61 - "ar do escritório (ar-condicionado Carrier)"
Cohesion: 0.36
Nodes (8): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Cômodo: Escritório, Cômodo: Laboratório, Cômodo: Quarto, Índice de aparelhos (cômodo → aparelho → controle), Aparelhos salvos

### Community 62 - "_iniciar"
Cohesion: 0.23
Nodes (11): _aviso(), iniciar(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir(), mostrar_url() (+3 more)

### Community 63 - "tv do quarto (TV Samsung)"
Cohesion: 0.36
Nodes (7): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung), Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas)

### Community 66 - "criar_servidor"
Cohesion: 0.12
Nodes (14): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), local_ok() (+6 more)

### Community 67 - "resolver_grade"
Cohesion: 0.25
Nodes (5): _caixa(), _conflitos(), resolver_grade(), busca(), resolver_sudoku()

### Community 70 - "piloto.py"
Cohesion: 0.15
Nodes (4): fen(), minha_cor(), quem_mexeu(), tabuleiro_txt()

### Community 76 - "._api"
Cohesion: 0.22
Nodes (5): ao_texto(), _confianca(), corpo_api(), ler_chave(), prompt_quiz()

### Community 79 - "tela/principal.py"
Cohesion: 0.08
Nodes (23): app_em_foco(), _bloqueio_de_toque(), _chave(), classe_janela(), compactos(), _contar(), curto(), diferenca() (+15 more)

### Community 80 - ".decidir"
Cohesion: 0.48
Nodes (3): chave_quiz(), norm(), quiz_da_tela()

### Community 87 - "Problemas já resolvidos (para não repetir)"
Cohesion: 0.22
Nodes (4): Pacote do celular dist/controle-ir.zip, Problemas já resolvidos (para não repetir), Versão do servidor (celular 1.0.4, repositório 1.0.5), empacotar.sh script

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 510 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **36 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TestPainel` connect `TestPainel` to `test_controle_ir.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `Servico` (e.g. with `ServidorMCP` and `criar_servidor()`) actually correct?**
  _`Servico` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.08208955223880597 - nodes in this community are weakly interconnected._
- **Why does `Servico` connect `Servico` to `cli.py`, `time`, `criar_servidor`, `servidor.py`, `normalizar`, `Sinal`, `Controlador`, `ServidorMCP`, `capacidades.py`, `Execucao`, `TestExecucao`, `EmissorSimulado`, `Servico`, `ar do quarto (ar-condicionado Gree GWH09KF)`, `verificar_cliente_mcp.py`, `_iniciar`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Should `TestPainel` be split into smaller, more focused modules?**
  _Cohesion score 0.0896551724137931 - nodes in this community are weakly interconnected._
- **Why does `Catalogo` connect `Catalogo` to `time`, `normalizar`, `Sinal`, `Servico`, `Sinal`, `main`, `descoberta.py`, `_iniciar`?**
  _High betweenness centrality (0.031) - this node is a cross-community bridge._