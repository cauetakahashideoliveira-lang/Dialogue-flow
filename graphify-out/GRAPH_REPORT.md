# Graph Report - Dialogue-flow  (2026-11-20)

## Corpus Check
- 71 files · ~123,934 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 3, .ir 3, .gz 1)

## Summary
- 1622 nodes · 3816 edges · 90 communities (59 shown, 31 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 287 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `a9cae1d4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- time
- TestPainel
- Conexao
- re
- Sinal
- Controlador
- .passo
- capacidades.py
- Servico
- Politica
- .aplicar_reflexo
- time
- TestTelaPorArquivo
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- os
- Servico
- Sinal
- Aparelhos
- main
- Instalador (instalar.sh)
- Tela
- Licenças dos dados
- Tunel
- TestSegundoPlano
- e2e.cjs
- json
- test_controle_ir.py
- emissor.py
- gree_variante.py
- descobrir_rede/principal.py
- cli.py
- tela/principal.py
- termometro/principal.py
- servidor.py
- painel.py
- TestOuvirBipe
- package.json
- TestSono
- sonar/principal.py
- _extrair_imagens
- novo_servico
- test_god_mode.py
- protocolos.py
- webauthn.js
- session-start.sh
- f
- TestTela
- exec_cli
- Variante Gree a partir da captura real (troca só os bits)
- autorizar.js
- app.js
- Sinal
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
- Reenvios
- resolver_grade
- construir_catalogo.py
- piloto.py
- Cerebros
- Piloto
- ._laco_xadrez
- ._api
- Notificador
- Canal
- eventos
- .decidir
- TestGreeVariante
- TestTermometro
- TestServidorMCP
- _modelos_do_teclado
- rotina
- armado
- Fluxo para criar um botão novo (gerar, enviar_sinal, perguntar, salvar)
- _plano

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

## Communities (90 total, 31 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.10
Nodes (58): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+50 more)

### Community 1 - "time"
Cohesion: 0.17
Nodes (6): capacidades(), _curto(), ErroAparelho, _faixa_txt(), _linhas_aparelho(), resumo_aparelho()

### Community 2 - "TestPainel"
Cohesion: 0.09
Nodes (15): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono (+7 more)

### Community 4 - "re"
Cohesion: 0.21
Nodes (11): comando(), chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar(), sem_acentos(), slug() (+3 more)

### Community 5 - "Sinal"
Cohesion: 0.23
Nodes (13): adicionar_comando(), ErroFormato, _hex_le(), importar_texto(), indice_comandos(), ler_flipper(), ler_sinal_texto(), ler_smartir() (+5 more)

### Community 6 - "Controlador"
Cohesion: 0.10
Nodes (12): executar(), main(), hora_legivel(), Controlador, Etapa, executar(), Plano, EmissorSimulado (+4 more)

### Community 7 - ".passo"
Cohesion: 0.13
Nodes (9): achar(), achar_regra(), botao_fechar(), compactos(), _Executor, relevantes(), _Falha, _injetar() (+1 more)

### Community 8 - "capacidades.py"
Cohesion: 0.10
Nodes (13): ErroCapacidade, _hash(), _manifesto(), modulo_embutido(), Registro, capacidade_cli(), apps_usando(), _capacidades_rodando() (+5 more)

### Community 9 - "Servico"
Cohesion: 0.05
Nodes (20): resumo_instrucoes(), classificar(), Execucao, ServidorMCP, ErroUso, Servico, criar_servidor(), _corpo() (+12 more)

### Community 10 - "Politica"
Cohesion: 0.20
Nodes (6): armar_cli(), painel_cli(), Politica, estado_valido(), ler(), fim_do_dia()

### Community 11 - ".aplicar_reflexo"
Cohesion: 0.16
Nodes (8): aplicar_regras(), els_fn(), calma(), els_fn(), reflexos(), _regex_bloqueados(), regra_vale(), _regras()

### Community 12 - "time"
Cohesion: 0.12
Nodes (24): _abrir(), agir(), _ajudante(), app_em_foco(), _bloqueio_de_toque(), dentro(), dump_ui(), em_anuncio() (+16 more)

### Community 14 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.06
Nodes (33): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+25 more)

### Community 15 - "os"
Cohesion: 0.18
Nodes (10): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+2 more)

### Community 16 - "Servico"
Cohesion: 0.06
Nodes (15): agora(), Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper() (+7 more)

### Community 17 - "Sinal"
Cohesion: 0.13
Nodes (12): sinais_pronto(), broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta(), impressao_protocolo(), normalizar_pulsos(), pronto_para_pulsos() (+4 more)

### Community 19 - "main"
Cohesion: 0.15
Nodes (10): ampliar_catalogo(), arquivo_boot(), atualizar(), boot_ativado(), criar_atalhos(), inicio_automatico(), main(), pasta_atalhos() (+2 more)

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
Cohesion: 0.15
Nodes (4): catalogo_base(), TestCatalogo, TestSegundoPlano, abrir_console()

### Community 25 - "e2e.cjs"
Cohesion: 0.09
Nodes (14): flagPath, fs, os, path, celular(), { chromium }, { execFileSync, spawn }, fs (+6 more)

### Community 26 - "json"
Cohesion: 0.23
Nodes (12): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+4 more)

### Community 28 - "test_controle_ir.py"
Cohesion: 0.12
Nodes (3): TestObservador, TestProtocolos, TestVocabulario

### Community 29 - "emissor.py"
Cohesion: 0.18
Nodes (3): Emissor, EmissorTermux, ErroEmissor

### Community 30 - "gree_variante.py"
Cohesion: 0.22
Nodes (10): checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main(), perfil() (+2 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.18
Nodes (9): classificar(), ficha_upnp(), ip_do_wifi(), main(), sondar(), ssdp(), tcp(), udp() (+1 more)

### Community 32 - "cli.py"
Cohesion: 0.13
Nodes (20): _api(), caminho_log(), _carimbo_catalogo(), carregar_config(), catalogo_atual(), _cfg_caminho(), console(), url_quando_pronta() (+12 more)

### Community 33 - "tela/principal.py"
Cohesion: 0.10
Nodes (23): atividade_no_topo(), bloqueado(), bloqueados(), casas_xadrez(), _chave(), _contar(), curto(), diferenca() (+15 more)

### Community 34 - "termometro/principal.py"
Cohesion: 0.33
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 36 - "painel.py"
Cohesion: 0.06
Nodes (12): Canal, _mascarar(), WebSocket, _b64(), _eventos_novos(), gravar(), _http(), parear() (+4 more)

### Community 38 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, @simplewebauthn/browser@14.0.0, wrangler@4.165.0, name (+10 more)

### Community 39 - "TestSono"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 40 - "sonar/principal.py"
Cohesion: 0.20
Nodes (7): js(), rodar(), analisar_sonar(), gerar_tom(), main(), testar(), volume_musica()

### Community 41 - "_extrair_imagens"
Cohesion: 0.40
Nodes (3): _extrair_imagens(), varrer(), TestImagensAninhadas

### Community 43 - "test_god_mode.py"
Cohesion: 0.06
Nodes (7): _Base, _ComServidor, _Servidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos, TestGodModeStmEPontuacao

### Community 44 - "protocolos.py"
Cohesion: 0.17
Nodes (15): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+7 more)

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 47 - "f"
Cohesion: 0.22
Nodes (8): filtro(), ler_recortes(), main(), reduzir(), validar_recorte(), gravar_memoria(), progresso_txt(), f()

### Community 49 - "exec_cli"
Cohesion: 0.24
Nodes (3): exec_cli(), Autorizacao, gerar_segredo()

### Community 50 - "Variante Gree a partir da captura real (troca só os bits)"
Cohesion: 0.40
Nodes (3): Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105), Perfil Gree Unknown (catálogo nº 102), descartado

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.28
Nodes (14): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+6 more)

### Community 53 - "Sinal"
Cohesion: 0.19
Nodes (5): escrever_flipper(), exportar(), sinal(), limitar_duracao(), Sinal

### Community 54 - "time"
Cohesion: 0.22
Nodes (7): Ajudante, _apagar(), captura(), foto_rapida(), _jar(), _jpeg(), _pasta_troca()

### Community 56 - "Problemas já resolvidos (para não repetir)"
Cohesion: 0.19
Nodes (15): Anúncio dos testes (v1.0.1), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026), Frases (+7 more)

### Community 57 - "TestPiloto"
Cohesion: 0.10
Nodes (7): TestPiloto, do_POST(), local(), elementos(), mover(), tocar(), robo()

### Community 58 - "diagnostico_rede/principal.py"
Cohesion: 0.36
Nodes (8): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi()

### Community 59 - "CLAUDE.md"
Cohesion: 0.27
Nodes (4): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, empacotar.sh script

### Community 61 - "ar do escritório (ar-condicionado Carrier)"
Cohesion: 0.23
Nodes (12): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Ligar/desligar diretos (energia_ligar 0x99, energia_desligar 0x98), Cômodo: Escritório (+4 more)

### Community 62 - "_iniciar"
Cohesion: 0.23
Nodes (11): _aviso(), iniciar(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir(), mostrar_url() (+3 more)

### Community 63 - "tv do quarto (TV Samsung)"
Cohesion: 0.21
Nodes (9): Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50), Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung), Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas) (+1 more)

### Community 67 - "resolver_grade"
Cohesion: 0.25
Nodes (5): _caixa(), _conflitos(), resolver_grade(), busca(), resolver_sudoku()

### Community 70 - "piloto.py"
Cohesion: 0.18
Nodes (4): fen(), quem_mexeu(), tabuleiro_txt(), _texto_do_evento()

### Community 76 - "._api"
Cohesion: 0.22
Nodes (5): ao_texto(), _confianca(), corpo_api(), ler_chave(), prompt_quiz()

### Community 79 - "eventos"
Cohesion: 0.11
Nodes (7): classe_janela(), eventos(), historico(), _Interrompido, _janela_curta(), janela_nova(), _linha_do_tempo()

### Community 80 - ".decidir"
Cohesion: 0.48
Nodes (3): chave_quiz(), norm(), quiz_da_tela()

### Community 84 - "_modelos_do_teclado"
Cohesion: 0.40
Nodes (3): _modelos_do_teclado(), teclado_da_grade(), _teclado_parado()

### Community 85 - "rotina"
Cohesion: 0.33
Nodes (4): _resumo_volta(), rotina(), gravar(), _rotinas()

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 496 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Catalogo` connect `Servico` to `time`, `Sinal`, `main`, `Sinal`, `_iniciar`, `tv do quarto (TV Samsung)`?**
  _High betweenness centrality (0.043) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `Servico` (e.g. with `ServidorMCP` and `criar_servidor()`) actually correct?**
  _`Servico` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.09830508474576272 - nodes in this community are weakly interconnected._
- **Why does `criar_servidor()` connect `Servico` to `cli.py`, `Reenvios`, `servidor.py`, `TestPainel`, `novo_servico`, `Aparelhos`, `main`, `_iniciar`, `tv do quarto (TV Samsung)`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Should `TestPainel` be split into smaller, more focused modules?**
  _Cohesion score 0.09359605911330049 - nodes in this community are weakly interconnected._
- **Why does `TestTelaPorArquivo` connect `TestTelaPorArquivo` to `test_controle_ir.py`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._