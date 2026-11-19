# Graph Report - Dialogue-flow  (2026-11-19)

## Corpus Check
- 69 files · ~105,080 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 3, .ir 3, .gz 1)

## Summary
- 1377 nodes · 3299 edges · 68 communities (47 shown, 21 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 268 edges (avg confidence: 0.87)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `1ed89e36`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- servico.py
- TestPainel
- descoberta.py
- cli.py
- sys
- Controlador
- .passo
- ServidorMCP
- tela/principal.py
- subprocess
- rish
- ErroEmissor
- TestTelaPorArquivo
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- shutil
- Descoberta
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
- observador.py
- gree_variante.py
- descobrir_rede/principal.py
- time
- package.json
- termometro/principal.py
- painel.py
- executar
- TestOuvirBipe
- ar do quarto (ar-condicionado Gree GWH09KF)
- TestSonar
- Servico
- normalizar
- tv do quarto (TV Samsung)
- test_god_mode.py
- protocolos.py
- webauthn.js
- session-start.sh
- TestServidorMCP
- formatos.py
- CLAUDE.md
- EmissorSimulado
- autorizar.js
- app.js
- Problemas já resolvidos (para não repetir)
- agir
- ar do escritório (ar-condicionado Carrier)
- TestObservador
- TestImagemNoMcp
- novo_servico
- TestTermometro
- _linhas_do_passo
- Aparelhos
- resumo_para_instrucoes
- Sinal
- TestProtocolos
- Ajudante

## God Nodes (most connected - your core abstractions)
1. `Servico` - 62 edges
2. `Descoberta` - 37 edges
3. `Sinal` - 37 edges
4. `Catalogo` - 35 edges
5. `main()` - 32 edges
6. `criar_servidor()` - 27 edges
7. `TestTelaPorArquivo` - 26 edges
8. `Controlador` - 26 edges
9. `_iniciar()` - 26 edges
10. `normalizar()` - 26 edges

## Surprising Connections (you probably didn't know these)
- `3b. Gateway OAuth na borda (1.0.26, implementada)` --references--> `TestPainel`  [INFERRED]
  docs/seguranca.md → testes/test_controle_ir.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `variante()` --implements--> `Variante Gree a partir da captura real (troca só os bits)`  [INFERRED]
  ferramentas/gree_variante.py → docs/aparelhos/quarto/ar-do-quarto.md
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `ampliar_catalogo()`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/cli.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (68 total, 21 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.11
Nodes (53): acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao(), autorizar() (+45 more)

### Community 1 - "servico.py"
Cohesion: 0.21
Nodes (8): capacidades(), _curto(), ErroAparelho, _faixa_txt(), hora_legivel(), _linhas_aparelho(), resumo_aparelho(), executar()

### Community 2 - "TestPainel"
Cohesion: 0.10
Nodes (14): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 3. Etapa 1 — painel externo com passkey, 3a. Central de Controle (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 3c. Transparência: atividade, tela ao vivo e “em uso agora” (1.0.29), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono, 6. Limites que nenhuma etapa remove (+6 more)

### Community 4 - "cli.py"
Cohesion: 0.06
Nodes (43): ampliar_catalogo(), _api(), armar_cli(), arquivo_boot(), atualizar(), _aviso(), boot_ativado(), caminho_log() (+35 more)

### Community 5 - "sys"
Cohesion: 0.21
Nodes (8): filtro(), ler_recortes(), main(), reduzir(), validar_recorte(), reflexos(), _regras(), f()

### Community 6 - "Controlador"
Cohesion: 0.25
Nodes (5): Controlador, Etapa, Plano, normalizar_valor(), valores_equivalentes()

### Community 7 - ".passo"
Cohesion: 0.11
Nodes (9): achar(), bloqueado(), calma(), eventos(), _Executor, relevantes(), _Falha, _Interrompido (+1 more)

### Community 9 - "tela/principal.py"
Cohesion: 0.11
Nodes (16): _chave(), compactos(), curto(), diferenca(), diferenca_curta(), elementos(), historico(), _janela_curta() (+8 more)

### Community 10 - "subprocess"
Cohesion: 0.12
Nodes (10): js(), rodar(), analisar_sonar(), gerar_tom(), main(), testar(), volume_musica(), _jar() (+2 more)

### Community 11 - "rish"
Cohesion: 0.22
Nodes (13): _ajudante(), _apagar(), app_em_foco(), captura(), dump_ui(), estado_rapido(), foco(), foto_rapida() (+5 more)

### Community 12 - "ErroEmissor"
Cohesion: 0.20
Nodes (3): Emissor, EmissorTermux, ErroEmissor

### Community 14 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.06
Nodes (33): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+25 more)

### Community 15 - "shutil"
Cohesion: 0.18
Nodes (10): analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela(), gravar(), gravar_json() (+2 more)

### Community 16 - "Descoberta"
Cohesion: 0.12
Nodes (3): agora(), Descoberta, ErroDescoberta

### Community 17 - "sinais.py"
Cohesion: 0.10
Nodes (11): broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta(), impressao_protocolo(), normalizar_pulsos(), pronto_para_pulsos(), pulsos_para_broadlink() (+3 more)

### Community 19 - "Catalogo"
Cohesion: 0.12
Nodes (11): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), _unzip() (+3 more)

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
Cohesion: 0.24
Nodes (11): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+3 more)

### Community 28 - "test_controle_ir.py"
Cohesion: 0.14
Nodes (3): catalogo_base(), TestCatalogo, TestVocabulario

### Community 29 - "observador.py"
Cohesion: 0.19
Nodes (7): apps_usando(), _capacidades_rodando(), em_uso(), quadro(), recursos_do_comando(), _tarefas(), _tela()

### Community 30 - "gree_variante.py"
Cohesion: 0.23
Nodes (10): checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main(), perfil() (+2 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.18
Nodes (8): classificar(), ficha_upnp(), ip_do_wifi(), main(), sondar(), tcp(), udp(), vivos()

### Community 32 - "time"
Cohesion: 0.17
Nodes (10): ssdp(), analisar(), dns(), download(), gateway(), main(), ping(), rodar() (+2 more)

### Community 33 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, @simplewebauthn/browser@14.0.0, wrangler@4.165.0, name (+10 more)

### Community 34 - "termometro/principal.py"
Cohesion: 0.36
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 35 - "painel.py"
Cohesion: 0.06
Nodes (20): exec_cli(), painel_cli(), Autorizacao, gerar_segredo(), Politica, _b64(), estado_valido(), _eventos_novos() (+12 more)

### Community 36 - "executar"
Cohesion: 0.30
Nodes (3): executar(), main(), TestControle

### Community 38 - "ar do quarto (ar-condicionado Gree GWH09KF)"
Cohesion: 0.22
Nodes (8): Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50), Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105), Perfil Gree Unknown (catálogo nº 102), descartado, Ligar/desligar diretos (energia_ligar 0x99, energia_desligar 0x98)

### Community 39 - "TestSonar"
Cohesion: 0.16
Nodes (3): _carregar_cap(), TestSonar, TestSono

### Community 40 - "Servico"
Cohesion: 0.05
Nodes (23): ErroCapacidade, _hash(), _manifesto(), modulo_embutido(), Registro, capacidade_cli(), classificar(), Execucao (+15 more)

### Community 41 - "normalizar"
Cohesion: 0.17
Nodes (13): normalizar_marca(), _traduz(), categoria_canonica(), chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar() (+5 more)

### Community 42 - "tv do quarto (TV Samsung)"
Cohesion: 0.24
Nodes (7): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung), Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas)

### Community 43 - "test_god_mode.py"
Cohesion: 0.06
Nodes (7): _Base, _ComServidor, _Servidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos, TestGodModeStmEPontuacao

### Community 44 - "protocolos.py"
Cohesion: 0.16
Nodes (15): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+7 more)

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 48 - "formatos.py"
Cohesion: 0.16
Nodes (18): adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos() (+10 more)

### Community 49 - "CLAUDE.md"
Cohesion: 0.27
Nodes (4): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, empacotar.sh script

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.28
Nodes (14): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+6 more)

### Community 53 - "Problemas já resolvidos (para não repetir)"
Cohesion: 0.15
Nodes (17): Anúncio dos testes (v1.0.1), Catálogo instalado: base + ampliado (9.380 perfis), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026) (+9 more)

### Community 54 - "agir"
Cohesion: 0.14
Nodes (10): agir(), bloqueados(), _bloqueio_de_toque(), _contar(), dentro(), _injetar(), janela_nova(), _regex_bloqueados() (+2 more)

### Community 55 - "ar do escritório (ar-condicionado Carrier)"
Cohesion: 0.36
Nodes (8): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Cômodo: Escritório, Cômodo: Laboratório, Cômodo: Quarto, Índice de aparelhos (cômodo → aparelho → controle), Aparelhos salvos

### Community 57 - "TestImagemNoMcp"
Cohesion: 0.18
Nodes (4): _extrair_imagens(), varrer(), TestImagemNoMcp, TestImagensAninhadas

### Community 58 - "novo_servico"
Cohesion: 0.11
Nodes (3): novo_servico(), TestCapacidades, TestTela

### Community 63 - "Sinal"
Cohesion: 0.21
Nodes (3): sinal(), limitar_duracao(), Sinal

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 408 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **21 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `servico.py`, `descoberta.py`, `cli.py`, `Controlador`, `ar do quarto (ar-condicionado Gree GWH09KF)`, `ServidorMCP`, `tv do quarto (TV Samsung)`, `ErroEmissor`, `Descoberta`, `formatos.py`, `sinais.py`, `Catalogo`, `EmissorSimulado`, `novo_servico`, `Aparelhos`, `Sinal`?**
  _High betweenness centrality (0.072) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Servico` (e.g. with `Aparelhos` and `ErroAparelho`) actually correct?**
  _`Servico` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.1063973063973064 - nodes in this community are weakly interconnected._
- **Why does `TestPainel` connect `TestPainel` to `Descoberta`, `test_controle_ir.py`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `Descoberta` (e.g. with `Catalogo` and `ErroEmissor`) actually correct?**
  _`Descoberta` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Should `TestPainel` be split into smaller, more focused modules?**
  _Cohesion score 0.09788359788359788 - nodes in this community are weakly interconnected._