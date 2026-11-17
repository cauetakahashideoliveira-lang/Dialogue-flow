# Graph Report - Dialogue-flow  (2026-11-17)

## Corpus Check
- 30 files · ~34,610 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 516 nodes · 1399 edges · 18 communities (13 shown, 5 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 165 edges (avg confidence: 0.88)
- Token cost: 157,587 input · 0 output

## Community Hubs (Navigation)
- Catálogo e linha de comando
- Sinais e formatos IR
- Módulos do pacote controle-ir
- Planejador e vocabulário
- Instalação, contexto e gerador Gree
- Descoberta automática
- Servidor MCP e serviço
- Aparelhos: cômodo → aparelho → controle
- Protocolos IR
- Emissor infravermelho
- Armazenamento de aparelhos
- README do projeto
- Túnel HTTPS
- Testes do gerador Gree
- Testes do servidor MCP
- Instalador (instalar.sh)
- Testes de protocolos
- Licenças dos dados

## God Nodes (most connected - your core abstractions)
1. `Servico` - 49 edges
2. `Sinal` - 39 edges
3. `Descoberta` - 37 edges
4. `Catalogo` - 35 edges
5. `Controlador` - 27 edges
6. `criar_servidor()` - 25 edges
7. `normalizar()` - 24 edges
8. `EmissorSimulado` - 23 edges
9. `iniciar()` - 22 edges
10. `agora()` - 18 edges

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
- **Fluxo de descoberta com número falado (buscar, pausar, retestar, confirmar)** — docs_estado_atual_anuncio_por_voz, controle_ir_controle_ir_servico_servico_buscar, controle_ir_controle_ir_servico_servico_pausar, controle_ir_controle_ir_servico_servico_retestar, controle_ir_controle_ir_servico_servico_confirmar [INFERRED 0.85]
- **Regras para qualquer agente que opere os aparelhos** — docs_aparelhos_readme_regra_nome_exato_no_conector, docs_aparelhos_readme_regra_opcoes_antes_de_comandar, docs_aparelhos_readme_estado_completo, docs_aparelhos_readme_sinal_enviado_nao_e_confirmacao, docs_aparelhos_readme_regra_recurso_ausente_no_perfil, docs_aparelhos_readme_codigos_compartilhados_perfil_94 [EXTRACTED 1.00]
- **Criação de botão novo: gerar variante, testar com enviar_sinal, salvar com editar_aparelho** — docs_aparelhos_readme_criar_botao_novo, ferramentas_gree_variante, docs_aparelhos_quarto_ar_do_quarto_variante_gree_da_captura_real, controle_ir_controle_ir_servico_servico_enviar_sinal, controle_ir_controle_ir_servico_servico_editar_aparelho [INFERRED 0.85]

## Communities (18 total, 5 thin omitted)

### Community 0 - "Catálogo e linha de comando"
Cohesion: 0.07
Nodes (27): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), _unzip() (+19 more)

### Community 1 - "Sinais e formatos IR"
Cohesion: 0.07
Nodes (31): adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto(), indice_comandos() (+23 more)

### Community 2 - "Módulos do pacote controle-ir"
Cohesion: 0.07
Nodes (9): capacidades(), hora_legivel(), resumo_aparelho(), main(), preparar(), catalogo_base(), novo_servico(), TestCatalogo (+1 more)

### Community 3 - "Planejador e vocabulário"
Cohesion: 0.09
Nodes (19): normalizar_marca(), Controlador, Etapa, executar(), Plano, _traduz(), categoria_canonica(), chaves_de_teste() (+11 more)

### Community 4 - "Instalação, contexto e gerador Gree"
Cohesion: 0.08
Nodes (30): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, Anúncio dos testes (v1.0.1), Catálogo instalado: base + ampliado (9.380 perfis), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude (+22 more)

### Community 5 - "Descoberta automática"
Cohesion: 0.13
Nodes (4): agora(), Descoberta, ErroDescoberta, termo_por_chave()

### Community 6 - "Servidor MCP e serviço"
Cohesion: 0.12
Nodes (15): EmissorSimulado, ServidorMCP, Servico, criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS() (+7 more)

### Community 7 - "Aparelhos: cômodo → aparelho → controle"
Cohesion: 0.10
Nodes (23): ErroUso, ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50) (+15 more)

### Community 8 - "Protocolos IR"
Cohesion: 0.13
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 9 - "Emissor infravermelho"
Cohesion: 0.20
Nodes (3): Emissor, EmissorTermux, ErroEmissor

### Community 10 - "Armazenamento de aparelhos"
Cohesion: 0.24
Nodes (4): Aparelhos, ErroAparelho, progresso_txt(), f()

### Community 11 - "README do projeto"
Cohesion: 0.17
Nodes (11): Como funciona, Conectar ao Claude, Controle IR do POCO + Claude, Descoberta, Desenvolvimento, Instalação (uma etapa por vez), O que foi verificado e o que depende do seu POCO, Por que Termux e não um APK (+3 more)

### Community 15 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 115 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Servidor MCP e serviço` to `Catálogo e linha de comando`, `Sinais e formatos IR`, `Módulos do pacote controle-ir`, `Planejador e vocabulário`, `Descoberta automática`, `Aparelhos: cômodo → aparelho → controle`, `Emissor infravermelho`, `Armazenamento de aparelhos`?**
  _High betweenness centrality (0.158) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `Servico` (e.g. with `ServidorMCP` and `Aparelhos`) actually correct?**
  _`Servico` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Catálogo e linha de comando` be split into smaller, more focused modules?**
  _Cohesion score 0.06599597585513078 - nodes in this community are weakly interconnected._
- **Why does `Sinal` connect `Sinais e formatos IR` to `Catálogo e linha de comando`, `Módulos do pacote controle-ir`, `Planejador e vocabulário`, `Descoberta automática`, `Servidor MCP e serviço`, `Protocolos IR`, `Emissor infravermelho`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `Sinal` (e.g. with `Catalogo` and `Descoberta`) actually correct?**
  _`Sinal` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `Sinais e formatos IR` be split into smaller, more focused modules?**
  _Cohesion score 0.0703962703962704 - nodes in this community are weakly interconnected._