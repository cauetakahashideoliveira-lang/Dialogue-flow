# PS4: controle completo e jogador que aprende (capacidade `ps4`, 1.0.109+)

O celular vira um DualShock 4 virtual pela rede (Remote Play, biblioteca `pyremoteplay` 0.7.6, base no Chiaki),
com todos os botões, os dois analógicos e a imagem do jogo. Sem hardware extra e sem custo.
Só para jogo offline (contra a máquina): bot contra pessoas viola os termos da PSN.

## Instalação no Termux (uma vez, com o sistema armado)
```
pkg install -y python-cryptography ffmpeg clang
pip install 'pyee<9' async_timeout netifaces av pyremoteplay==0.7.6
```
A `pyremoteplay` está parada desde 2022: sem `pyee<9` e `async_timeout` ela não importa (conferido em 23/11/2026).
`acao=diagnostico` diz o que falta.

## Preparo (uma vez)
1. No PS4: Ajustes → Ajustes da conexão do Remote Play → Ativar Remote Play; e Economia de energia → Recursos no
   modo de repouso → Permanecer conectado à Internet + Ativar ligar o PS4 pela rede.
2. `acao=conta` devolve o link de login da PSN; o usuário entra, copia o endereço da página em branco e o Claude
   chama `acao=conta url=...` (o link vale poucos minutos). Alternativa: `conta_id` (id numérico) + `nome`.
3. `acao=procurar` acha o PS4 e guarda o ip.
4. No PS4: Ajustes da conexão do Remote Play → Adicionar dispositivo → PIN; `acao=parear pin=...`.

Arquivos: `~/.controle-ir/ps4/` (perfis.json com a chave de pareamento, ps4.json, habilidades.json, jogadores/).

## Uso
- `ligar`, `conectar` (720p/60 por padrão), `quadro` (imagem do jogo), `comando`, `parar`, `desconectar`, `repouso`.
- Comandos: `{"botao":"x","ms":80}`, `{"segurar":"r2"}`/`{"soltar":"r2"}`, `{"juntos":["l1","r1"]}`,
  `{"analogico":"esquerdo","x":0,"y":-1,"ms":500}` ou `{"analogico":"direito","angulo":90,"forca":0.6}` (90° e
  y −1 = cima), `{"esperar":300}`, `{"repetir":3,"passos":[...]}`, `{"habilidade":"nome"}`; texto curto:
  `"x x r2:600 esperar:300 l1+r1"`. Comando com mais de 40 s roda em segundo plano (`estado`, `parar`).
- Habilidades (`acao=habilidade modo=salvar|listar|ver|apagar|rodar`): ações reutilizáveis, o vocabulário do jogador.

## Jogador que aprende (`acao=jogador`)
Laço no celular: quadro → situação (16x9 colorido; quadros parecidos = mesmo estado) → habilidade (Q-learning +
curiosidade UCB + demonstrações) → recompensa pelos detectores da tela → aprende. Memória por jogo em
`jogadores/<jogo>/memoria.json`; tudo gravado em `gravacao.jsonl` + quadros-chave.

- Detectores (recompensa): `barra` (fração de uma cor numa região: vida, energia), `cor_aparece` (+1 quando a cor
  surge: tela de vitória), `brilho`, `mudanca` (movimento/progresso). Região em frações `[x,y,l,a]`; `peso`
  negativo = ruim. Calibre com `modo=detectores` (mostra a medida no quadro atual).
- O Claude é o técnico: `relatorio` (política, valor por habilidade, `melhorando`), `revisar` (quadros das jogadas
  mais marcantes), `nota valor=±1` (feedback), e reescreve as habilidades. `comando demonstrar=true` com
  `{habilidade}` ensina por exemplo.

## Limites medidos/esperados
- Remote Play soma ~100–200 ms de rede e vídeo; o jogador decide a cada jogada (habilidade + `intervalo_ms`).
  Bom para menus, turnos, estratégia, rotinas (farm, corrida contra o tempo); reflexo puro (tiro, luta) não.
- Teto maior exigiria hardware (placa de captura + Pico/GP2040-CE com autenticação) — fora do escopo sem custo.
- Ainda não testado com o PS4 real (falta instalar no Termux e parear).
