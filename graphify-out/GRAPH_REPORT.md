# Graph Report - Dialogue-flow  (2026-11-20)

## Corpus Check
- 71 files · ~121,946 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 3, .ir 3, .gz 1)

## Summary
- 1589 nodes · 3749 edges · 79 communities (53 shown, 26 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 274 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `f74e9db6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- test_controle_ir.py
- TestPainel
- piloto.py
- normalizar
- f
- Controlador
- .passo
- package.json
- grade
- Servico
- TestArmacao
- Catalogo
- TestTelaPorArquivo
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- os
- Servico
- Sinal
- Aparelhos
- ServidorMCP
- Instalador (instalar.sh)
- Tela
- Licenças dos dados
- Tunel
- TestSegundoPlano
- e2e.cjs
- json
- TestVocabulario
- exec_cli
- gree_variante.py
- descobrir_rede/principal.py
- cli.py
- tela/principal.py
- termometro/principal.py
- Politica
- painel.py
- TestOuvirBipe
- Canal
- TestSono
- ErroEmissor
- TestImagemNoMcp
- observador.py
- test_god_mode.py
- protocolos.py
- webauthn.js
- session-start.sh
- rotina
- TestTela
- console
- ar do quarto (ar-condicionado Gree GWH09KF)
- autorizar.js
- app.js
- TestExecucao
- re
- TestCapacidades
- Problemas já resolvidos (para não repetir)
- TestPiloto
- _iniciar
- CLAUDE.md
- .test_canal_repassa_chamada_e_aviso
- ar do escritório (ar-condicionado Carrier)
- main
- tv do quarto (TV Samsung)
- os
- resumo_para_instrucoes
- Reenvios
- resolver_grade
- subprocess
- TestProtocolos
- Notificador
- Canal
- bloqueados
- TestObservador
- TestGreeVariante
- TestTermometro

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
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
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

## Communities (79 total, 26 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.10
Nodes (58): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+50 more)

### Community 1 - "test_controle_ir.py"
Cohesion: 0.09
Nodes (9): capacidades(), _curto(), _faixa_txt(), hora_legivel(), _linhas_aparelho(), resumo_aparelho(), executar(), main() (+1 more)

### Community 2 - "TestPainel"
Cohesion: 0.09
Nodes (15): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono (+7 more)

### Community 3 - "piloto.py"
Cohesion: 0.06
Nodes (12): Cerebros, ao_texto(), chave_quiz(), Conexao, _confianca(), corpo_api(), ler_chave(), norm() (+4 more)

### Community 4 - "normalizar"
Cohesion: 0.13
Nodes (22): adicionar_comando(), comando(), ErroFormato, importar_texto(), indice_comandos(), ler_flipper(), ler_sinal_texto(), ler_smartir() (+14 more)

### Community 5 - "f"
Cohesion: 0.27
Nodes (5): filtro(), ler_recortes(), main(), reduzir(), validar_recorte()

### Community 6 - "Controlador"
Cohesion: 0.09
Nodes (9): Controlador, Etapa, Plano, Emissor, EmissorSimulado, normalizar_valor(), valores_equivalentes(), TestControle (+1 more)

### Community 7 - ".passo"
Cohesion: 0.11
Nodes (6): achar(), eventos(), _Executor, relevantes(), _Falha, _Interrompido

### Community 8 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, @simplewebauthn/browser@14.0.0, wrangler@4.165.0, name (+10 more)

### Community 9 - "grade"
Cohesion: 0.09
Nodes (16): achar_regra(), _ajudante(), aplicar_regras(), els_fn(), calma(), estado_rapido(), els_fn(), foco() (+8 more)

### Community 10 - "Servico"
Cohesion: 0.05
Nodes (25): ErroCapacidade, _hash(), _manifesto(), modulo_embutido(), Registro, capacidade_cli(), classificar(), Execucao (+17 more)

### Community 12 - "Catalogo"
Cohesion: 0.11
Nodes (10): Catalogo, estado_representativo(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), normalizar_marca(), _unzip() (+2 more)

### Community 14 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.06
Nodes (33): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+25 more)

### Community 15 - "os"
Cohesion: 0.11
Nodes (13): js(), rodar(), analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela() (+5 more)

### Community 16 - "Servico"
Cohesion: 0.13
Nodes (4): agora(), Descoberta, ErroDescoberta, termo_por_chave()

### Community 17 - "Sinal"
Cohesion: 0.09
Nodes (18): escrever_flipper(), exportar(), _hex_le(), sinal(), sinais_pronto(), _sinal_smartir(), broadlink_para_pulsos(), _classes() (+10 more)

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 24 - "TestSegundoPlano"
Cohesion: 0.15
Nodes (4): catalogo_base(), TestCatalogo, TestSegundoPlano, abrir_console()

### Community 25 - "e2e.cjs"
Cohesion: 0.09
Nodes (14): flagPath, fs, os, path, celular(), { chromium }, { execFileSync, spawn }, fs (+6 more)

### Community 26 - "json"
Cohesion: 0.18
Nodes (16): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+8 more)

### Community 29 - "exec_cli"
Cohesion: 0.19
Nodes (4): exec_cli(), Autorizacao, gerar_segredo(), totp()

### Community 30 - "gree_variante.py"
Cohesion: 0.19
Nodes (11): exportar_jsonl(), checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main() (+3 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.14
Nodes (17): classificar(), ficha_upnp(), ip_do_wifi(), main(), sondar(), ssdp(), tcp(), udp() (+9 more)

### Community 32 - "cli.py"
Cohesion: 0.12
Nodes (17): ampliar_catalogo(), arquivo_boot(), boot_ativado(), caminho_log(), _carimbo_catalogo(), catalogo_atual(), criar_atalhos(), iniciar_em_segundo_plano() (+9 more)

### Community 33 - "tela/principal.py"
Cohesion: 0.10
Nodes (22): casas_xadrez(), _chave(), compactos(), _contar(), curto(), dentro(), diferenca(), diferenca_curta() (+14 more)

### Community 34 - "termometro/principal.py"
Cohesion: 0.33
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 35 - "Politica"
Cohesion: 0.16
Nodes (6): armar_cli(), painel_cli(), Politica, armado(), fim_do_dia(), permitido()

### Community 36 - "painel.py"
Cohesion: 0.10
Nodes (11): _b64(), estado_valido(), _eventos_novos(), gravar(), _http(), ler(), parear(), Sincronizador (+3 more)

### Community 38 - "Canal"
Cohesion: 0.13
Nodes (3): Canal, _mascarar(), WebSocket

### Community 39 - "TestSono"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 41 - "TestImagemNoMcp"
Cohesion: 0.18
Nodes (4): _extrair_imagens(), varrer(), TestImagemNoMcp, TestImagensAninhadas

### Community 42 - "observador.py"
Cohesion: 0.21
Nodes (7): apps_usando(), _capacidades_rodando(), em_uso(), quadro(), recursos_do_comando(), _tarefas(), _tela()

### Community 43 - "test_god_mode.py"
Cohesion: 0.06
Nodes (7): _Base, _ComServidor, _Servidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos, TestGodModeStmEPontuacao

### Community 44 - "protocolos.py"
Cohesion: 0.15
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 47 - "rotina"
Cohesion: 0.22
Nodes (6): executar(), main(), _resumo_volta(), rotina(), gravar(), _rotinas()

### Community 49 - "console"
Cohesion: 0.24
Nodes (12): _api(), carregar_config(), _cfg_caminho(), console(), url_quando_pronta(), estado_servidor(), parar_servico(), _pid_do_servico() (+4 more)

### Community 50 - "ar do quarto (ar-condicionado Gree GWH09KF)"
Cohesion: 0.27
Nodes (7): Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50), Ligar/desligar diretos (energia_ligar 0x99, energia_desligar 0x98), Cômodo: Quarto

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.28
Nodes (14): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+6 more)

### Community 54 - "re"
Cohesion: 0.11
Nodes (19): _abrir(), agir(), app_em_foco(), atividade_no_topo(), _bloqueio_de_toque(), botao_fechar(), classe_janela(), dump_ui() (+11 more)

### Community 56 - "Problemas já resolvidos (para não repetir)"
Cohesion: 0.17
Nodes (16): Anúncio dos testes (v1.0.1), Catálogo instalado: base + ampliado (9.380 perfis), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026) (+8 more)

### Community 57 - "TestPiloto"
Cohesion: 0.15
Nodes (4): TestPiloto, do_POST(), local(), elementos()

### Community 58 - "_iniciar"
Cohesion: 0.23
Nodes (11): _aviso(), iniciar(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir(), mostrar_url() (+3 more)

### Community 59 - "CLAUDE.md"
Cohesion: 0.27
Nodes (4): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, empacotar.sh script

### Community 61 - "ar do escritório (ar-condicionado Carrier)"
Cohesion: 0.42
Nodes (7): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Cômodo: Escritório, Cômodo: Laboratório, Índice de aparelhos (cômodo → aparelho → controle), Aparelhos salvos

### Community 62 - "main"
Cohesion: 0.23
Nodes (3): atualizar(), main(), Origens

### Community 63 - "tv do quarto (TV Samsung)"
Cohesion: 0.23
Nodes (8): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung), Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas), Versão do servidor (celular 1.0.4, repositório 1.0.5)

### Community 64 - "os"
Cohesion: 0.24
Nodes (6): Ajudante, _apagar(), captura(), foto_rapida(), _jpeg(), _pasta_troca()

### Community 67 - "resolver_grade"
Cohesion: 0.25
Nodes (5): _caixa(), _conflitos(), resolver_grade(), busca(), resolver_sudoku()

### Community 68 - "subprocess"
Cohesion: 0.16
Nodes (7): analisar_sonar(), gerar_tom(), main(), testar(), volume_musica(), arquivos_cc0(), main()

### Community 79 - "bloqueados"
Cohesion: 0.19
Nodes (10): bloqueado(), bloqueados(), _ferramentas_piloto(), aguardar(), tocar(), _modulo_piloto(), piloto(), _privado() (+2 more)

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 484 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `cli.py`, `test_controle_ir.py`, `normalizar`, `Controlador`, `Servico`, `TestTela`, `Aparelhos`, `ServidorMCP`, `_iniciar`, `tv do quarto (TV Samsung)`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `Servico` (e.g. with `ServidorMCP` and `criar_servidor()`) actually correct?**
  _`Servico` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.09830508474576272 - nodes in this community are weakly interconnected._
- **Why does `TestTelaPorArquivo` connect `TestTelaPorArquivo` to `test_controle_ir.py`?**
  _High betweenness centrality (0.028) - this node is a cross-community bridge._
- **Should `test_controle_ir.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09371980676328502 - nodes in this community are weakly interconnected._
- **Why does `criar_servidor()` connect `Servico` to `cli.py`, `test_controle_ir.py`, `Reenvios`, `TestPainel`, `normalizar`, `TestTela`, `ServidorMCP`, `_iniciar`, `main`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._