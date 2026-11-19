# Graph Report - Dialogue-flow  (2026-11-19)

## Corpus Check
- 67 files · ~91,257 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 3, .ir 3, .gz 1)

## Summary
- 1181 nodes · 2878 edges · 58 communities (35 shown, 23 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 264 edges (avg confidence: 0.88)
- Token cost: 157,587 input · 0 output

## Graph Freshness
- Built from commit: `92279cee`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- index.js
- protocolos.py
- TestPainel
- Catalogo
- cli.py
- sys
- Serviço (operações MCP)
- Catalogo
- ServidorMCP
- tela/principal.py
- test_controle_ir.py
- sonar/principal.py
- normalizar
- TestTelaPorArquivo
- Modo deus — arquitetura evolutiva e mapa de oportunidades
- os
- TestSono
- Sinal
- emissor.py
- Servico
- Instalador (instalar.sh)
- TestVocabulario
- Licenças dos dados
- Tunel
- TestSegundoPlano
- e2e.cjs
- json
- exec_cli
- TestExecucao
- categoria_canonica
- gree_variante.py
- descobrir_rede/principal.py
- time
- Aparelhos
- termometro/principal.py
- painel.py
- novo_servico
- TestOuvirBipe
- formatos.py
- TestSonar
- armado
- package.json
- TestGreeVariante
- test_god_mode.py
- test_controle_ir.py
- webauthn.js
- session-start.sh
- execucao.py
- Fluxo para criar um botão novo (gerar, enviar_sinal, perguntar, salvar)
- Politica
- TestArmacao
- autorizar.js
- app.js
- Sincronizador
- resumo_para_instrucoes
- TestImagemNoMcp
- TestCapacidades
- TestTermometro

## God Nodes (most connected - your core abstractions)
1. `Servico` - 64 edges
2. `Sinal` - 39 edges
3. `Descoberta` - 37 edges
4. `Catalogo` - 35 edges
5. `main()` - 32 edges
6. `criar_servidor()` - 28 edges
7. `Controlador` - 27 edges
8. `normalizar()` - 26 edges
9. `_iniciar()` - 25 edges
10. `ErroUso` - 24 edges

## Surprising Connections (you probably didn't know these)
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `Catalogo`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/catalogo.py
- `Catálogo instalado: base + ampliado (9.380 perfis)` --conceptually_related_to--> `ampliar_catalogo()`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/cli.py
- `Túnel ngrok com domínio fixo` --conceptually_related_to--> `Tunel`  [INFERRED]
  docs/estado-atual.md → controle-ir/controle_ir/tunel.py
- `Arquivos .ir com os sinais adicionados pelo usuário (formato Flipper)` --conceptually_related_to--> `ler_flipper()`  [INFERRED]
  docs/aparelhos/README.md → controle-ir/controle_ir/formatos.py
- `variante()` --implements--> `Variante Gree a partir da captura real (troca só os bits)`  [INFERRED]
  ferramentas/gree_variante.py → docs/aparelhos/quarto/ar-do-quarto.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]

## Communities (58 total, 23 thin omitted)

### Community 0 - "index.js"
Cohesion: 0.12
Nodes (48): acaoDono(), ackCelular(), agora(), aleatorio(), aparelhoDoToken(), assinar(), assinarRequisicao(), autorizar() (+40 more)

### Community 1 - "protocolos.py"
Cohesion: 0.13
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 2 - "TestPainel"
Cohesion: 0.10
Nodes (13): 1. Diagnóstico (código da 1.0.22, auditoria de 19/11), 3. Etapa 1 — painel externo com passkey, 3a. Painel da Casa (1.0.24, implementada) — `painel/`, 3b. Gateway OAuth na borda (1.0.26, implementada), 4. Etapa 2 — endurecer a execução (depois da Etapa 1), 5. Decisões do dono, 6. Limites que nenhuma etapa remove, Planejado (próximas etapas) (+5 more)

### Community 3 - "Catalogo"
Cohesion: 0.10
Nodes (3): agora(), Descoberta, ErroDescoberta

### Community 4 - "cli.py"
Cohesion: 0.06
Nodes (43): ampliar_catalogo(), _api(), arquivo_boot(), atualizar(), _aviso(), boot_ativado(), caminho_log(), _carimbo_catalogo() (+35 more)

### Community 5 - "sys"
Cohesion: 0.23
Nodes (7): filtro(), ler_recortes(), main(), reduzir(), validar_recorte(), progresso_txt(), f()

### Community 6 - "Serviço (operações MCP)"
Cohesion: 0.08
Nodes (28): hora_legivel(), Controlador, Etapa, executar(), Plano, normalizar_valor(), valores_equivalentes(), ar do escritório (ar-condicionado Carrier) (+20 more)

### Community 7 - "Catalogo"
Cohesion: 0.14
Nodes (10): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), _unzip() (+2 more)

### Community 9 - "tela/principal.py"
Cohesion: 0.15
Nodes (21): achar(), agir(), _apagar(), app_em_foco(), bloqueado(), bloqueados(), _bloqueio_de_toque(), captura() (+13 more)

### Community 10 - "test_controle_ir.py"
Cohesion: 0.07
Nodes (12): capacidades(), _curto(), _faixa_txt(), _linhas_aparelho(), resumo_aparelho(), ErroCapacidade, _hash(), _manifesto() (+4 more)

### Community 11 - "sonar/principal.py"
Cohesion: 0.31
Nodes (5): analisar_sonar(), gerar_tom(), main(), testar(), volume_musica()

### Community 12 - "normalizar"
Cohesion: 0.23
Nodes (14): comando(), ler_smartir(), _traduz(), chaves_de_teste(), interpretar(), normalizar(), _por_regex(), _registrar() (+6 more)

### Community 14 - "Modo deus — arquitetura evolutiva e mapa de oportunidades"
Cohesion: 0.06
Nodes (33): 10. Hipóteses de produto (a investigar), 1. O que mais surpreende (com fundamento), 2. Gargalo principal e o primeiro avanço (implementado), 3. Arquitetura evolutiva, 4. Mapa de oportunidades, 5. Conexões que mais aumentam a capacidade de criar conexões, 6. Limites reais (onde está a barreira), 7. Autonomia com responsabilidade (+25 more)

### Community 15 - "os"
Cohesion: 0.12
Nodes (12): js(), rodar(), analisar(), comparar(), comparar_ruido(), decodificar(), detectar_bipes(), filtrar_janela() (+4 more)

### Community 17 - "Sinal"
Cohesion: 0.11
Nodes (12): sinal(), broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta(), limitar_duracao(), normalizar_pulsos(), pronto_para_pulsos() (+4 more)

### Community 18 - "emissor.py"
Cohesion: 0.18
Nodes (3): Emissor, EmissorTermux, ErroEmissor

### Community 19 - "Servico"
Cohesion: 0.07
Nodes (20): EmissorSimulado, Execucao, ErroUso, Servico, criar_servidor(), _corpo(), do_DELETE(), do_GET() (+12 more)

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

### Community 25 - "e2e.cjs"
Cohesion: 0.09
Nodes (14): flagPath, fs, os, path, celular(), { chromium }, { execFileSync, spawn }, fs (+6 more)

### Community 26 - "json"
Cohesion: 0.21
Nodes (12): analisar_trecho(), comandar_ar(), gravar_json(), laco(), ler_json(), _linhas(), main(), _quadros_db() (+4 more)

### Community 30 - "gree_variante.py"
Cohesion: 0.06
Nodes (32): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, Anúncio dos testes (v1.0.1), Catálogo instalado: base + ampliado (9.380 perfis), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude (+24 more)

### Community 31 - "descobrir_rede/principal.py"
Cohesion: 0.18
Nodes (9): classificar(), ficha_upnp(), ip_do_wifi(), main(), sondar(), ssdp(), tcp(), udp() (+1 more)

### Community 32 - "time"
Cohesion: 0.36
Nodes (8): analisar(), dns(), download(), gateway(), main(), ping(), rodar(), wifi()

### Community 34 - "termometro/principal.py"
Cohesion: 0.36
Nodes (8): avaliar(), bateria(), gravar(), historico(), ler_conf(), main(), medir(), tendencia()

### Community 35 - "painel.py"
Cohesion: 0.21
Nodes (10): _b64(), estado_valido(), _eventos_novos(), gravar(), _http(), ler(), parear(), sincronizar() (+2 more)

### Community 38 - "formatos.py"
Cohesion: 0.17
Nodes (15): adicionar_comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos(), ler_flipper() (+7 more)

### Community 40 - "armado"
Cohesion: 0.31
Nodes (3): armado(), permitido(), 2. Etapa 0 — armação diária local (1.0.23, implementada)

### Community 41 - "package.json"
Cohesion: 0.13
Nodes (18): dependencies, @cloudflare/workers-oauth-provider@1.2.4, @simplewebauthn/server@14.1.0, description, devDependencies, @simplewebauthn/browser@14.0.0, wrangler@4.165.0, name (+10 more)

### Community 43 - "test_god_mode.py"
Cohesion: 0.06
Nodes (7): _Base, _ComServidor, _Servidor, TestGodModeAprendizado, TestGodModeAutoTune, TestGodModeModelos, TestGodModeStmEPontuacao

### Community 44 - "test_controle_ir.py"
Cohesion: 0.12
Nodes (3): catalogo_base(), TestCatalogo, TestProtocolos

### Community 45 - "webauthn.js"
Cohesion: 0.15
Nodes (9): a(), f(), g(), n(), o(), p(), r(), s (+1 more)

### Community 47 - "execucao.py"
Cohesion: 0.29
Nodes (3): classificar(), gerar_segredo(), fim_do_dia()

### Community 49 - "Politica"
Cohesion: 0.31
Nodes (3): armar_cli(), painel_cli(), Politica

### Community 51 - "autorizar.js"
Cohesion: 0.73
Nodes (5): api(), decidir(), digital(), msg(), preparar()

### Community 52 - "app.js"
Cohesion: 0.30
Nodes (13): acao(), api(), aviso(), carregar(), comDigital(), conviteNaUrl, digital(), el() (+5 more)

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 337 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servico` to `Aparelhos`, `Catalogo`, `cli.py`, `novo_servico`, `Serviço (operações MCP)`, `Catalogo`, `ServidorMCP`, `armado`, `test_controle_ir.py`, `formatos.py`, `normalizar`, `Fluxo para criar um botão novo (gerar, enviar_sinal, perguntar, salvar)`, `Sinal`, `emissor.py`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `Servico` (e.g. with `ServidorMCP` and `Aparelhos`) actually correct?**
  _`Servico` has 17 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `index.js` be split into smaller, more focused modules?**
  _Cohesion score 0.12 - nodes in this community are weakly interconnected._
- **Why does `Descoberta` connect `Catalogo` to `Catalogo`, `test_controle_ir.py`, `Sinal`, `emissor.py`, `Servico`, `categoria_canonica`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `Sinal` (e.g. with `Catalogo` and `Descoberta`) actually correct?**
  _`Sinal` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `protocolos.py` be split into smaller, more focused modules?**
  _Cohesion score 0.13105413105413105 - nodes in this community are weakly interconnected._