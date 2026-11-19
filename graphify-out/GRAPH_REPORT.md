# Graph Report - Dialogue-flow  (2026-11-19)

## Corpus Check
- 70 files · ~115,832 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 3, .ir 3, .gz 1)

## Summary
- 1499 nodes · 3596 edges · 73 communities (46 shown, 27 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 280 edges (avg confidence: 0.87)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `f71d0e23`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- servico.py
- TestPainel
- ErroUso
- Canal
- sys
- Controlador
- _Executor
- re
- tela/principal.py
- Servico
- Ajudante
- package.json
- TestTelaPorArquivo
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- os
- Servico
- _Servidor
- _rodar_bloco
- ServidorMCP
- Instalador (instalar.sh)
- Tela
- Licenças dos dados
- Tunel
- TestSegundoPlano
- e2e.cjs
- json
- _extrair_imagens
- Registro
- gree_variante.py
- descobrir_rede/principal.py
- cli.py
- agir
- termometro/principal.py
- painel.py
- Sinal
- TestOuvirBipe
- test_god_mode.py
- TestSonar
- criar_servidor
- resolver_grade
- .controlar
- test_god_mode.py
- protocolos.py
- webauthn.js
- session-start.sh
- formatos.py
- sinais.py
- CLAUDE.md
- Execucao
- autorizar.js
- app.js
- TestExecucao
- time
- ar do quarto (ar-condicionado Gree GWH09KF)
- resumo_para_instrucoes
- Canal
- TestCapacidades
- TestTela
- .test_canal_repassa_chamada_e_aviso
- ErroEmissor
- TestTermometro
- servidor.py
- test_controle_ir.py
- TestSono
- novo_servico
- diagnostico_rede/principal.py
- subprocess
- TestGreeVariante

## God Nodes (most connected - your core abstractions)
1. `Servico` - 52 edges
2. `Descoberta` - 36 edges
3. `Sinal` - 36 edges
4. `Tela` - 34 edges
5. `TestTelaPorArquivo` - 34 edges
6. `Catalogo` - 34 edges
7. `main()` - 32 edges
8. `criar_servidor()` - 29 edges
9. `_iniciar()` - 28 edges
10. `normalizar()` - 26 edges

## Surprising Connections (you probably didn't know these)
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `ampliar_catalogo()`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/cli.py
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
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

## Communities (73 total, 27 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.10
Nodes (58): abrirCanal(), acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao() (+50 more)

### Community 1 - "servico.py"
Cohesion: 0.15
Nodes (7): capacidades(), _curto(), _faixa_txt(), hora_legivel(), _linhas_aparelho(), resumo_aparelho(), executar()

### Community 2 - "TestPainel"
Cohesion: 0.09
Nodes (15): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 3d. Canal direto celular ↔ Central (1.0.46 + PR da Central), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono (+7 more)

### Community 3 - "ErroUso"
Cohesion: 0.17
Nodes (5): Aparelhos, ErroAparelho, ErroUso, slug(), Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper)

### Community 4 - "Canal"
Cohesion: 0.13
Nodes (3): Canal, _mascarar(), WebSocket

### Community 5 - "sys"
Cohesion: 0.21
Nodes (8): filtro(), ler_recortes(), main(), reduzir(), validar_recorte(), gravar(), progresso_txt(), f()

### Community 6 - "Controlador"
Cohesion: 0.09
Nodes (9): Controlador, Etapa, Plano, Emissor, EmissorSimulado, Reenvios, normalizar_valor(), valores_equivalentes() (+1 more)

### Community 7 - "_Executor"
Cohesion: 0.08
Nodes (12): bloqueado(), compactos(), eventos(), _Executor, els_fn(), relevantes(), _Falha, _injetar() (+4 more)

### Community 8 - "re"
Cohesion: 0.11
Nodes (14): achar(), achar_regra(), aplicar_regras(), els_fn(), atividade_no_topo(), bloqueados(), botao_fechar(), escapar_input_text() (+6 more)

### Community 9 - "tela/principal.py"
Cohesion: 0.09
Nodes (21): _abrir(), _chave(), classe_janela(), _contar(), curto(), dentro(), diferenca(), diferenca_curta() (+13 more)

### Community 12 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, @simplewebauthn/browser@14.0.0, wrangler@4.165.0, name (+10 more)

### Community 14 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.06
Nodes (33): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+25 more)

### Community 15 - "os"
Cohesion: 0.18
Nodes (10): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+2 more)

### Community 16 - "Servico"
Cohesion: 0.05
Nodes (25): agora(), Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper() (+17 more)

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 21 - "Tela"
Cohesion: 0.07
Nodes (4): Tela, UiAutomation.OnAccessibilityEventListener, Thread, Thread

### Community 23 - "Tunel"
Cohesion: 0.09
Nodes (16): Tunel, Anúncio dos testes (v1.0.1), Catálogo instalado: base + ampliado (9.380 perfis), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026) (+8 more)

### Community 24 - "TestSegundoPlano"
Cohesion: 0.15
Nodes (4): catalogo_base(), TestCatalogo, TestSegundoPlano, abrir_console()

### Community 25 - "e2e.cjs"
Cohesion: 0.09
Nodes (14): flagPath, fs, os, path, celular(), { chromium }, { execFileSync, spawn }, fs (+6 more)

### Community 26 - "json"
Cohesion: 0.27
Nodes (11): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+3 more)

### Community 28 - "_extrair_imagens"
Cohesion: 0.40
Nodes (3): _extrair_imagens(), varrer(), TestImagensAninhadas

### Community 29 - "Registro"
Cohesion: 0.10
Nodes (13): ErroCapacidade, _hash(), _manifesto(), modulo_embutido(), Registro, capacidade_cli(), apps_usando(), _capacidades_rodando() (+5 more)

### Community 30 - "gree_variante.py"
Cohesion: 0.15
Nodes (12): arquivos_cc0(), main(), checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes() (+4 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.12
Nodes (9): classificar(), ficha_upnp(), ip_do_wifi(), main(), sondar(), ssdp(), tcp(), udp() (+1 more)

### Community 32 - "cli.py"
Cohesion: 0.05
Nodes (44): ampliar_catalogo(), _api(), armar_cli(), arquivo_boot(), atualizar(), _aviso(), boot_ativado(), caminho_log() (+36 more)

### Community 33 - "agir"
Cohesion: 0.15
Nodes (14): agir(), _ajudante(), app_em_foco(), calma(), em_anuncio(), estado_rapido(), executar(), fechar_anuncio() (+6 more)

### Community 34 - "termometro/principal.py"
Cohesion: 0.33
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 35 - "painel.py"
Cohesion: 0.05
Nodes (21): exec_cli(), painel_cli(), Autorizacao, gerar_segredo(), Politica, _b64(), estado_valido(), _eventos_novos() (+13 more)

### Community 36 - "Sinal"
Cohesion: 0.18
Nodes (6): escrever_flipper(), exportar(), sinal(), _sinal_smartir(), limitar_duracao(), Sinal

### Community 40 - "criar_servidor"
Cohesion: 0.33
Nodes (12): criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json(), local_ok() (+4 more)

### Community 41 - "resolver_grade"
Cohesion: 0.25
Nodes (5): _caixa(), _conflitos(), resolver_grade(), busca(), resolver_sudoku()

### Community 42 - ".controlar"
Cohesion: 0.13
Nodes (8): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung), Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas), Versão do servidor (celular 1.0.4, repositório 1.0.5)

### Community 43 - "test_god_mode.py"
Cohesion: 0.11
Nodes (5): _Base, _ComServidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos

### Community 44 - "protocolos.py"
Cohesion: 0.15
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 47 - "formatos.py"
Cohesion: 0.25
Nodes (12): adicionar_comando(), comando(), ErroFormato, _hex_le(), importar_texto(), indice_comandos(), ler_flipper(), ler_sinal_texto() (+4 more)

### Community 48 - "sinais.py"
Cohesion: 0.13
Nodes (11): sinais_pronto(), broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta(), normalizar_pulsos(), pronto_para_pulsos(), pulsos_para_broadlink() (+3 more)

### Community 49 - "CLAUDE.md"
Cohesion: 0.27
Nodes (4): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, empacotar.sh script

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.28
Nodes (14): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+6 more)

### Community 54 - "time"
Cohesion: 0.15
Nodes (13): trecho_do_microfone(), _apagar(), captura(), dump_ui(), foto_rapida(), _jar(), _jpeg(), _ler() (+5 more)

### Community 55 - "ar do quarto (ar-condicionado Gree GWH09KF)"
Cohesion: 0.15
Nodes (18): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50) (+10 more)

### Community 63 - "servidor.py"
Cohesion: 0.13
Nodes (3): resumo_instrucoes(), main(), preparar()

### Community 64 - "test_controle_ir.py"
Cohesion: 0.12
Nodes (3): TestObservador, TestProtocolos, TestVocabulario

### Community 67 - "diagnostico_rede/principal.py"
Cohesion: 0.36
Nodes (8): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi()

### Community 68 - "subprocess"
Cohesion: 0.20
Nodes (7): js(), rodar(), analisar_sonar(), gerar_tom(), main(), testar(), volume_musica()

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 452 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TestTelaPorArquivo` connect `TestTelaPorArquivo` to `test_controle_ir.py`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `Servico` (e.g. with `ServidorMCP` and `criar_servidor()`) actually correct?**
  _`Servico` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.09830508474576272 - nodes in this community are weakly interconnected._
- **Why does `Servico` connect `Servico` to `cli.py`, `servico.py`, `novo_servico`, `ErroUso`, `painel.py`, `Controlador`, `criar_servidor`, `.controlar`, `Servico`, `Execucao`, `ServidorMCP`, `ar do quarto (ar-condicionado Gree GWH09KF)`, `Registro`, `servidor.py`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Descoberta` (e.g. with `Catalogo` and `ErroEmissor`) actually correct?**
  _`Descoberta` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Should `TestPainel` be split into smaller, more focused modules?**
  _Cohesion score 0.0896551724137931 - nodes in this community are weakly interconnected._