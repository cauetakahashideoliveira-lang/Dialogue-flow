# Graph Report - Dialogue-flow  (2026-11-17)

## Corpus Check
- 8 files · ~34,800 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 518 nodes · 1402 edges · 23 communities (17 shown, 6 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 165 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Catálogo e linha de comando
- Formatos e vocabulário
- Módulos do pacote controle-ir
- Descoberta automática
- Sinais IR
- Planejador de pedidos
- Serviço (operações MCP)
- Protocolos IR
- Servidor MCP
- Instalação no celular
- Gerador de variantes Gree
- Ramo: ar do quarto (Gree)
- Emissor infravermelho
- Índice e cômodos + ar do escritório e do laboratório (Carrier nº 94)
- README do projeto
- Contexto para agentes (CLAUDE.md)
- Armazenamento de aparelhos
- Ramo: tv do quarto (Samsung)
- Notificador (voz)
- Túnel HTTPS
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

## Communities (23 total, 6 thin omitted)

### Community 0 - "Catálogo e linha de comando"
Cohesion: 0.07
Nodes (28): Catalogo, estado_representativo(), exportar_jsonl(), importar_flipper(), importar_jsonl(), importar_smartir(), metadados_flipper(), _unzip() (+20 more)

### Community 1 - "Formatos e vocabulário"
Cohesion: 0.08
Nodes (32): normalizar_marca(), adicionar_comando(), comando(), ErroFormato, escrever_flipper(), exportar(), _hex_le(), importar_texto() (+24 more)

### Community 2 - "Módulos do pacote controle-ir"
Cohesion: 0.07
Nodes (10): capacidades(), hora_legivel(), resumo_aparelho(), ErroEmissor, main(), preparar(), catalogo_base(), novo_servico() (+2 more)

### Community 3 - "Descoberta automática"
Cohesion: 0.13
Nodes (4): agora(), Descoberta, ErroDescoberta, termo_por_chave()

### Community 4 - "Sinais IR"
Cohesion: 0.09
Nodes (11): broadlink_para_pulsos(), _classes(), ErroSinal, impressao_bruta(), limitar_duracao(), normalizar_pulsos(), pronto_para_pulsos(), pulsos_para_broadlink() (+3 more)

### Community 5 - "Planejador de pedidos"
Cohesion: 0.16
Nodes (7): Controlador, Etapa, executar(), Plano, normalizar_valor(), valores_equivalentes(), TestControle

### Community 6 - "Serviço (operações MCP)"
Cohesion: 0.17
Nodes (5): EmissorSimulado, ErroUso, Servico, Macros de sequência (editar_aparelho(macro=...), 0,45 s entre teclas), TestDescoberta

### Community 7 - "Protocolos IR"
Cohesion: 0.13
Nodes (16): _bits_bytes_lsb(), _bits_lsb(), codificar(), decodificar(), ErroProtocolo, EspecPDWM, _int_lsb(), _juntar_niveis() (+8 more)

### Community 8 - "Servidor MCP"
Cohesion: 0.14
Nodes (13): ServidorMCP, criar_servidor(), _corpo(), do_DELETE(), do_GET(), do_OPTIONS(), do_POST(), _json() (+5 more)

### Community 9 - "Instalação no celular"
Cohesion: 0.16
Nodes (16): Anúncio dos testes (v1.0.1), Celular, Conector Controle master (MCP sem login, URL com segredo), Conector no Claude, Correção do curl CANNOT LINK EXECUTABLE (apt update && apt full-upgrade), Emissor IR do celular (30, 33, 36, 38, 40 e 56 kHz), Estado atual da instalação (17/11/2026), Frases (+8 more)

### Community 10 - "Gerador de variantes Gree"
Cohesion: 0.23
Nodes (10): checksum(), ErroGree, flipper(), gerar(), _indice_espaco(), ler_bytes(), main(), perfil() (+2 more)

### Community 11 - "Ramo: ar do quarto (Gree)"
Cohesion: 0.22
Nodes (8): Tecla de oscilação do perfil Ferroli/York (oscilacao_alternar), ar do quarto (ar-condicionado Gree GWH09KF), Extra modo_turbo: turbo + oscilação + visor apagado (quadro 49 00 10 50 01 20 00 50), Extra oscilacao_alternar do Gree (quadro 49 00 20 50 01 20 00 50), Extra x_luz: visor desligado (quadro 09 00 00 50 00 20 00 50), Perfil SmartIR climate/1184 Gree GWH09KF (catálogo nº 105), Perfil Gree Unknown (catálogo nº 102), descartado, Ligar/desligar diretos (energia_ligar 0x99, energia_desligar 0x98)

### Community 13 - "Índice e cômodos + ar do escritório e do laboratório (Carrier nº 94)"
Cohesion: 0.29
Nodes (8): ar do escritório (ar-condicionado Carrier), Perfil SmartIR Carrier Unknown (catálogo nº 94), ar condicionado laboratório (ar-condicionado Midea), Cômodo: Escritório, Cômodo: Laboratório, Cômodo: Quarto, Índice de aparelhos (cômodo → aparelho → controle), Aparelhos salvos

### Community 14 - "README do projeto"
Cohesion: 0.17
Nodes (11): Como funciona, Conectar ao Claude, Controle IR do POCO + Claude, Descoberta, Desenvolvimento, Instalação (uma etapa por vez), O que foi verificado e o que depende do seu POCO, Por que Termux e não um APK (+3 more)

### Community 15 - "Contexto para agentes (CLAUDE.md)"
Cohesion: 0.27
Nodes (4): Contexto para o Claude Code, Skill graphify (query, explain, path, update), Pacote do celular dist/controle-ir.zip, empacotar.sh script

### Community 17 - "Ramo: tv do quarto (Samsung)"
Cohesion: 0.31
Nodes (7): Macro abrir Netflix (inicio_3 + ok), Macro abrir YouTube (pendente), Perfil Flipper-IRDB Samsung TV Full (catálogo nº 2331), Protocolo Samsung32, endereço 0x07, Smart Hub 0x79 (tecla inicio_3), tv do quarto (TV Samsung), Catálogo instalado: base + ampliado (9.380 perfis)

### Community 20 - "Instalador (instalar.sh)"
Cohesion: 0.70
Nodes (4): etapa(), falha(), ok(), instalar.sh script

## Knowledge Gaps
- **1 isolated node(s):** `Versão do servidor (celular 1.0.4, repositório 1.0.5)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 116 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Servico` connect `Serviço (operações MCP)` to `Catálogo e linha de comando`, `Formatos e vocabulário`, `Módulos do pacote controle-ir`, `Descoberta automática`, `Sinais IR`, `Planejador de pedidos`, `Servidor MCP`, `Índice e cômodos + ar do escritório e do laboratório (Carrier nº 94)`, `Armazenamento de aparelhos`?**
  _High betweenness centrality (0.157) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `Servico` (e.g. with `ServidorMCP` and `Aparelhos`) actually correct?**
  _`Servico` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Versão do servidor (celular 1.0.4, repositório 1.0.5)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Catálogo e linha de comando` be split into smaller, more focused modules?**
  _Cohesion score 0.07412587412587412 - nodes in this community are weakly interconnected._
- **Why does `Sinal` connect `Formatos e vocabulário` to `Catálogo e linha de comando`, `Módulos do pacote controle-ir`, `Descoberta automática`, `Sinais IR`, `Planejador de pedidos`, `Serviço (operações MCP)`, `Protocolos IR`, `Emissor infravermelho`?**
  _High betweenness centrality (0.112) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `Sinal` (e.g. with `Catalogo` and `Descoberta`) actually correct?**
  _`Sinal` has 6 INFERRED edges - model-reasoned connections that need verification._
- **Should `Formatos e vocabulário` be split into smaller, more focused modules?**
  _Cohesion score 0.07645687645687646 - nodes in this community are weakly interconnected._