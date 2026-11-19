# Graph Report - Dialogue-flow  (2026-11-19)

## Corpus Check
- 70 files · ~116,631 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 3, .ir 3, .gz 1)

## Summary
- 1507 nodes · 3597 edges · 82 communities (57 shown, 25 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 268 edges (avg confidence: 0.86)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `b4107d7f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- test_controle_ir.py
- TestPainel
- agir
- normalizar
- sys
- Controlador
- .passo
- re
- tela/principal.py
- Servico
- exec_cli
- package.json
- TestTelaPorArquivo
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- os
- Servico
- sinais.py
- _rodar_bloco
- mcp.py
- Instalador (instalar.sh)
- Tela
- Licenças dos dados
- Tunel
- TestSegundoPlano
- e2e.cjs
- json
- TestImagemNoMcp
- Registro
- gree_variante.py
- descobrir_rede/principal.py
- cli.py
- executar
- termometro/principal.py
- painel.py
- Politica
- TestOuvirBipe
- Canal
- TestSonar
- criar_servidor
- Sinal
- .controlar
- test_god_mode.py
- protocolos.py
- webauthn.js
- session-start.sh
- formatos.py
- console
- _iniciar
- Execucao
- autorizar.js
- app.js
- TestExecucao
- time
- ar do escritório (ar-condicionado Carrier)
- Problemas já resolvidos (para não repetir)
- TestArmacao
- TestCapacidades
- TestTela
- .test_canal_repassa_chamada_e_aviso
- main
- foco
- observador.py
- TestObservador
- Notificador
- Reenvios
- sys
- subprocess
- ar do quarto (ar-condicionado Gree GWH09KF)
- TestProtocolos
- time
- CLAUDE.md
- Sincronizador
- aparelhos.py
- Canal
- TestDescoberta
- catalogo_base
- TestGreeVariante

## God Nodes (most connected - your core abstractions)
1. `Servico` - 51 edges
2. `Descoberta` - 36 edges
3. `Sinal` - 36 edges
4. `TestTelaPorArquivo` - 35 edges
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

## Communities (82 total, 25 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.10
Nodes (58): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+50 more)

### Community 2 - "TestPainel"
Cohesion: 0.09
Nodes (15): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono (+7 more)

### Community 3 - "agir"
Cohesion: 0.11
Nodes (9): agir(), _contar(), eventos(), historico(), _Interrompido, _janela_curta(), janela_nova(), _linha_do_tempo() (+1 more)

### Community 4 - "normalizar"
Cohesion: 0.14
Nodes (14): Aparelhos, ErroAparelho, comando(), chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar() (+6 more)

### Community 5 - "sys"
Cohesion: 0.15
Nodes (11): filtro(), ler_recortes(), main(), reduzir(), validar_recorte(), _resumo_volta(), rotina(), gravar() (+3 more)

### Community 6 - "Controlador"
Cohesion: 0.09
Nodes (12): hora_legivel(), Controlador, Etapa, executar(), Plano, Emissor, EmissorSimulado, EmissorTermux (+4 more)

### Community 7 - ".passo"
Cohesion: 0.15
Nodes (6): achar(), compactos(), _Executor, relevantes(), _Falha, _injetar()

### Community 8 - "re"
Cohesion: 0.13
Nodes (11): bloqueados(), botao_fechar(), casas_xadrez(), escapar_input_text(), foto(), _linhas_do_passo(), normalizar(), reflexos() (+3 more)

### Community 9 - "tela/principal.py"
Cohesion: 0.09
Nodes (20): _caixa(), _chave(), _conflitos(), curto(), diferenca(), diferenca_curta(), elementos(), grade() (+12 more)

### Community 10 - "Servico"
Cohesion: 0.12
Nodes (4): ErroUso, Servico, Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas), 2. Etapa 0 — armação diária local (1.0.23, implementada)

### Community 11 - "exec_cli"
Cohesion: 0.19
Nodes (4): exec_cli(), Autorizacao, gerar_segredo(), totp()

### Community 12 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, @simplewebauthn/browser@14.0.0, wrangler@4.165.0, name (+10 more)

### Community 14 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.06
Nodes (33): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+25 more)

### Community 15 - "os"
Cohesion: 0.14
Nodes (12): js(), rodar(), analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela() (+4 more)

### Community 16 - "Servico"
Cohesion: 0.06
Nodes (14): agora(), Catalogo, estado_representativo(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), normalizar_marca() (+6 more)

### Community 17 - "sinais.py"
Cohesion: 0.13
Nodes (11): sinais_pronto(), broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta(), normalizar_pulsos(), pronto_para_pulsos(), pulsos_para_broadlink() (+3 more)

### Community 18 - "_rodar_bloco"
Cohesion: 0.40
Nodes (3): app_em_foco(), _bloqueio_de_toque(), _rodar_bloco()

### Community 19 - "mcp.py"
Cohesion: 0.11
Nodes (4): resumo_para_instrucoes(), resumo_instrucoes(), ServidorMCP, TestResumoInstrucoes

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 25 - "e2e.cjs"
Cohesion: 0.09
Nodes (14): flagPath, fs, os, path, celular(), { chromium }, { execFileSync, spawn }, fs (+6 more)

### Community 26 - "json"
Cohesion: 0.23
Nodes (12): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+4 more)

### Community 28 - "TestImagemNoMcp"
Cohesion: 0.18
Nodes (4): _extrair_imagens(), varrer(), TestImagemNoMcp, TestImagensAninhadas

### Community 29 - "Registro"
Cohesion: 0.19
Nodes (6): ErroCapacidade, _hash(), _manifesto(), modulo_embutido(), Registro, capacidade_cli()

### Community 30 - "gree_variante.py"
Cohesion: 0.19
Nodes (11): exportar_jsonl(), checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main() (+3 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.18
Nodes (9): classificar(), ficha_upnp(), ip_do_wifi(), main(), sondar(), ssdp(), tcp(), udp() (+1 more)

### Community 32 - "cli.py"
Cohesion: 0.14
Nodes (14): arquivo_boot(), boot_ativado(), caminho_log(), _carimbo_catalogo(), catalogo_atual(), criar_atalhos(), iniciar_em_segundo_plano(), inicio_automatico() (+6 more)

### Community 33 - "executar"
Cohesion: 0.16
Nodes (9): _abrir(), atividade_no_topo(), classe_janela(), dentro(), em_anuncio(), executar(), fechar_anuncio(), main() (+1 more)

### Community 34 - "termometro/principal.py"
Cohesion: 0.33
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 35 - "painel.py"
Cohesion: 0.13
Nodes (11): painel_cli(), _b64(), estado_valido(), _eventos_novos(), gravar(), _http(), ler(), parear() (+3 more)

### Community 36 - "Politica"
Cohesion: 0.26
Nodes (3): armar_cli(), Politica, fim_do_dia()

### Community 38 - "Canal"
Cohesion: 0.13
Nodes (3): Canal, _mascarar(), WebSocket

### Community 39 - "TestSonar"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 40 - "criar_servidor"
Cohesion: 0.33
Nodes (12): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), local_ok() (+4 more)

### Community 41 - "Sinal"
Cohesion: 0.15
Nodes (7): escrever_flipper(), exportar(), sinal(), _sinal_smartir(), impressao_protocolo(), limitar_duracao(), Sinal

### Community 42 - ".controlar"
Cohesion: 0.31
Nodes (7): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung), Catálogo instalado: base + ampliado (9.380 perfis)

### Community 43 - "test_god_mode.py"
Cohesion: 0.06
Nodes (7): _Base, _ComServidor, _Servidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos, TestGodModeStmEPontuacao

### Community 44 - "protocolos.py"
Cohesion: 0.17
Nodes (15): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+7 more)

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 47 - "formatos.py"
Cohesion: 0.22
Nodes (12): adicionar_comando(), ErroFormato, _hex_le(), importar_texto(), indice_comandos(), ler_flipper(), ler_sinal_texto(), ler_smartir() (+4 more)

### Community 48 - "console"
Cohesion: 0.24
Nodes (12): _api(), carregar_config(), _cfg_caminho(), console(), url_quando_pronta(), estado_servidor(), parar_servico(), _pid_do_servico() (+4 more)

### Community 49 - "_iniciar"
Cohesion: 0.23
Nodes (11): _aviso(), iniciar(), _iniciar(), ao_mudar_url(), encerrar(), gravar_estado(), reduzir(), mostrar_url() (+3 more)

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.28
Nodes (14): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+6 more)

### Community 54 - "time"
Cohesion: 0.14
Nodes (15): Ajudante, _ajudante(), _apagar(), captura(), dump_ui(), estado_rapido(), foto_rapida(), _jar() (+7 more)

### Community 55 - "ar do escritório (ar-condicionado Carrier)"
Cohesion: 0.36
Nodes (8): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Cômodo: Escritório, Cômodo: Laboratório, Cômodo: Quarto, Índice de aparelhos (cômodo → aparelho → controle), Aparelhos salvos

### Community 56 - "Problemas já resolvidos (para não repetir)"
Cohesion: 0.16
Nodes (16): Anúncio dos testes (v1.0.1), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026), Frases (+8 more)

### Community 57 - "TestArmacao"
Cohesion: 0.19
Nodes (3): armado(), permitido(), TestArmacao

### Community 59 - "TestTela"
Cohesion: 0.11
Nodes (3): novo_servico(), TestTela, TestTermometro

### Community 61 - "main"
Cohesion: 0.23
Nodes (4): ampliar_catalogo(), atualizar(), main(), Origens

### Community 62 - "foco"
Cohesion: 0.19
Nodes (8): achar_regra(), aplicar_regras(), els_fn(), bloqueado(), calma(), els_fn(), foco(), regra_vale()

### Community 63 - "observador.py"
Cohesion: 0.21
Nodes (7): apps_usando(), _capacidades_rodando(), em_uso(), quadro(), recursos_do_comando(), _tarefas(), _tela()

### Community 68 - "subprocess"
Cohesion: 0.31
Nodes (5): analisar_sonar(), gerar_tom(), main(), testar(), volume_musica()

### Community 70 - "ar do quarto (ar-condicionado Gree GWH09KF)"
Cohesion: 0.20
Nodes (8): Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50), Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105), Perfil Gree Unknown (catálogo nº 102), descartado, Ligar/desligar diretos (energia_ligar 0x99, energia_desligar 0x98)

### Community 74 - "time"
Cohesion: 0.38
Nodes (8): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi()

### Community 75 - "CLAUDE.md"
Cohesion: 0.27
Nodes (4): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, empacotar.sh script

### Community 77 - "aparelhos.py"
Cohesion: 0.36
Nodes (5): capacidades(), _curto(), _faixa_txt(), _linhas_aparelho(), resumo_aparelho()

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 456 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `cli.py`, `test_controle_ir.py`, `normalizar`, `Controlador`, `ar do quarto (ar-condicionado Gree GWH09KF)`, `criar_servidor`, `Sinal`, `formatos.py`, `Servico`, `_iniciar`, `Execucao`, `mcp.py`, `TestDescoberta`, `TestTela`, `Registro`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `Servico` (e.g. with `ServidorMCP` and `criar_servidor()`) actually correct?**
  _`Servico` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.09830508474576272 - nodes in this community are weakly interconnected._
- **Why does `criar_servidor()` connect `criar_servidor` to `cli.py`, `test_controle_ir.py`, `Reenvios`, `TestPainel`, `Controlador`, `Servico`, `formatos.py`, `_iniciar`, `mcp.py`, `TestTela`, `main`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Descoberta` (e.g. with `Catalogo` and `ErroEmissor`) actually correct?**
  _`Descoberta` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Should `test_controle_ir.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1140819964349376 - nodes in this community are weakly interconnected._