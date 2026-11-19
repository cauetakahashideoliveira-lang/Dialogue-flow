# Graph Report - Dialogue-flow  (2026-11-19)

## Corpus Check
- 69 files · ~104,033 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 3, .ir 3, .gz 1)

## Summary
- 1368 nodes · 3272 edges · 73 communities (44 shown, 29 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 268 edges (avg confidence: 0.87)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `b075f4d0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- servico.py
- TestPainel
- descoberta.py
- cli.py
- sys
- .planejar
- .passo
- ServidorMCP
- tela/principal.py
- subprocess
- time
- emissor.py
- TestTelaPorArquivo
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- shutil
- Politica
- sinais.py
- TestExecucao
- Catalogo
- Instalador (instalar.sh)
- Tela
- Licenças dos dados
- Tunel
- TestSegundoPlano
- e2e.cjs
- json
- test_controle_ir.py
- Registro
- gree_variante.py
- descobrir_rede/principal.py
- time
- execucao.py
- termometro/principal.py
- painel.py
- TestTela
- TestOuvirBipe
- armado
- TestSonar
- Servico
- normalizar
- TestArmacao
- test_god_mode.py
- protocolos.py
- webauthn.js
- session-start.sh
- TestServidorMCP
- formatos.py
- test_god_mode.py
- Sincronizador
- autorizar.js
- app.js
- .controlar
- agir
- armar_cli
- _Servidor
- TestImagemNoMcp
- TestCapacidades
- TestTermometro
- _rodar_bloco
- Aparelhos
- resumo_para_instrucoes
- Sinal
- _extrair_imagens
- _Interrompido
- novo_servico
- Ajudante
- TestGreeVariante

## God Nodes (most connected - your core abstractions)
1. `Servico` - 62 edges
2. `Descoberta` - 37 edges
3. `Sinal` - 37 edges
4. `Catalogo` - 35 edges
5. `main()` - 32 edges
6. `criar_servidor()` - 27 edges
7. `Controlador` - 26 edges
8. `normalizar()` - 26 edges
9. `_iniciar()` - 26 edges
10. `Tela` - 24 edges

## Surprising Connections (you probably didn't know these)
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `variante()` --implements--> `Variante Gree a partir da captura real (troca só os bits)`  [INFERRED]
  ferramentas/gree_variante.py → docs/aparelhos/quarto/ar-do-quarto.md
- `Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper)` --conceptually_related_to--> `ler_flipper()`  [INFERRED]
  docs/aparelhos/README.md → controle-ir/controle_ir/formatos.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (73 total, 29 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.07
Nodes (71): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, @simplewebauthn/browser@14.0.0, wrangler@4.165.0, name (+63 more)

### Community 1 - "servico.py"
Cohesion: 0.19
Nodes (8): capacidades(), _curto(), ErroAparelho, _faixa_txt(), hora_legivel(), _linhas_aparelho(), resumo_aparelho(), executar()

### Community 2 - "TestPainel"
Cohesion: 0.08
Nodes (26): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), local_ok() (+18 more)

### Community 4 - "cli.py"
Cohesion: 0.06
Nodes (41): ampliar_catalogo(), _api(), arquivo_boot(), atualizar(), boot_ativado(), caminho_log(), _carimbo_catalogo(), carregar_config() (+33 more)

### Community 5 - "sys"
Cohesion: 0.16
Nodes (11): filtro(), ler_recortes(), main(), reduzir(), validar_recorte(), bloqueados(), reflexos(), _regex_bloqueados() (+3 more)

### Community 6 - ".planejar"
Cohesion: 0.09
Nodes (11): executar(), main(), Controlador, Etapa, Plano, Emissor, EmissorSimulado, normalizar_valor() (+3 more)

### Community 7 - ".passo"
Cohesion: 0.13
Nodes (8): achar(), compactos(), eventos(), _Executor, relevantes(), _Falha, _injetar(), normalizar()

### Community 9 - "tela/principal.py"
Cohesion: 0.12
Nodes (15): _chave(), _contar(), curto(), diferenca(), diferenca_curta(), elementos(), historico(), _janela_curta() (+7 more)

### Community 10 - "subprocess"
Cohesion: 0.20
Nodes (7): js(), rodar(), analisar_sonar(), gerar_tom(), main(), testar(), volume_musica()

### Community 11 - "time"
Cohesion: 0.25
Nodes (10): _apagar(), captura(), dump_ui(), estado_rapido(), foto_rapida(), _jpeg(), _ler(), observar() (+2 more)

### Community 14 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.06
Nodes (33): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+25 more)

### Community 15 - "shutil"
Cohesion: 0.18
Nodes (10): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+2 more)

### Community 17 - "sinais.py"
Cohesion: 0.13
Nodes (11): sinais_pronto(), broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta(), normalizar_pulsos(), pronto_para_pulsos(), pulsos_para_broadlink() (+3 more)

### Community 19 - "Catalogo"
Cohesion: 0.16
Nodes (9): Catalogo, estado_representativo(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), _unzip(), _zip() (+1 more)

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
Cohesion: 0.23
Nodes (12): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+4 more)

### Community 28 - "test_controle_ir.py"
Cohesion: 0.12
Nodes (3): TestObservador, TestProtocolos, TestVocabulario

### Community 29 - "Registro"
Cohesion: 0.10
Nodes (13): ErroCapacidade, _hash(), _manifesto(), modulo_embutido(), Registro, capacidade_cli(), apps_usando(), _capacidades_rodando() (+5 more)

### Community 30 - "gree_variante.py"
Cohesion: 0.14
Nodes (13): exportar_jsonl(), arquivos_cc0(), main(), checksum(), ErroGree, flipper(), gerar(), _indice_espaco() (+5 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.17
Nodes (9): classificar(), ficha_upnp(), ip_do_wifi(), main(), sondar(), ssdp(), tcp(), udp() (+1 more)

### Community 32 - "time"
Cohesion: 0.21
Nodes (8): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi()

### Community 33 - "execucao.py"
Cohesion: 0.21
Nodes (5): exec_cli(), Autorizacao, classificar(), gerar_segredo(), totp()

### Community 34 - "termometro/principal.py"
Cohesion: 0.33
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 35 - "painel.py"
Cohesion: 0.18
Nodes (11): painel_cli(), _b64(), estado_valido(), _eventos_novos(), gravar(), _http(), ler(), parear() (+3 more)

### Community 38 - "armado"
Cohesion: 0.31
Nodes (3): armado(), permitido(), 2. Etapa 0 — armação diária local (1.0.23, implementada)

### Community 39 - "TestSonar"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 40 - "Servico"
Cohesion: 0.06
Nodes (6): agora(), Descoberta, ErroDescoberta, Execucao, ErroUso, Servico

### Community 41 - "normalizar"
Cohesion: 0.23
Nodes (11): chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar(), sem_acentos(), slug(), _t() (+3 more)

### Community 43 - "test_god_mode.py"
Cohesion: 0.11
Nodes (5): _Base, _ComServidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos

### Community 44 - "protocolos.py"
Cohesion: 0.16
Nodes (15): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+7 more)

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 48 - "formatos.py"
Cohesion: 0.25
Nodes (12): adicionar_comando(), comando(), ErroFormato, _hex_le(), importar_texto(), indice_comandos(), ler_flipper(), ler_sinal_texto() (+4 more)

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.28
Nodes (14): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+6 more)

### Community 53 - ".controlar"
Cohesion: 0.05
Nodes (44): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF) (+36 more)

### Community 54 - "agir"
Cohesion: 0.24
Nodes (9): agir(), _ajudante(), bloqueado(), calma(), escapar_input_text(), foco(), _linhas_do_passo(), sequencia() (+1 more)

### Community 55 - "armar_cli"
Cohesion: 0.50
Nodes (3): armar_cli(), _aviso(), _termux()

### Community 60 - "_rodar_bloco"
Cohesion: 0.40
Nodes (3): app_em_foco(), _bloqueio_de_toque(), _rodar_bloco()

### Community 61 - "Aparelhos"
Cohesion: 0.15
Nodes (3): Aparelhos, normalizar_marca(), categoria_canonica()

### Community 63 - "Sinal"
Cohesion: 0.16
Nodes (7): escrever_flipper(), exportar(), sinal(), _sinal_smartir(), impressao_protocolo(), limitar_duracao(), Sinal

### Community 65 - "_extrair_imagens"
Cohesion: 0.40
Nodes (3): _extrair_imagens(), varrer(), TestImagensAninhadas

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 405 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `descoberta.py`, `servico.py`, `TestPainel`, `descoberta.py`, `cli.py`, `novo_servico`, `.planejar`, `armado`, `ServidorMCP`, `normalizar`, `emissor.py`, `sinais.py`, `Registro`, `Catalogo`, `.controlar`, `Aparelhos`, `Sinal`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.06738245094409478 - nodes in this community are weakly interconnected._
- **Why does `Sinal` connect `Sinal` to `servico.py`, `descoberta.py`, `.planejar`, `Servico`, `normalizar`, `emissor.py`, `formatos.py`, `sinais.py`, `Catalogo`, `.controlar`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `Descoberta` (e.g. with `Catalogo` and `ErroEmissor`) actually correct?**
  _`Descoberta` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Should `TestPainel` be split into smaller, more focused modules?**
  _Cohesion score 0.07549361207897794 - nodes in this community are weakly interconnected._