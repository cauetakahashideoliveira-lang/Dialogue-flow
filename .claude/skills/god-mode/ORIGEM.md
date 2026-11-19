# Origem da skill god-mode

- **Projeto original:** [elder-plinius/G0DM0D3](https://github.com/elder-plinius/G0DM0D3), commit `f630176`
  (15/07/2026), licença **AGPL-3.0** (texto em `LICENSE-G0DM0D3.txt`).
- **O que é o original:** uma interface de chat com vários modelos (OpenRouter, Venice ou servidor local), feita
  para "liberar" os modelos: parte das funções existe para contornar as proteções deles.
- **O que esta pasta é:** um porte para Python (só biblioteca padrão) das funções que não dependem disso, com o
  Claude Code no lugar da interface web.

## Recurso por recurso

| Recurso do G0DM0D3 | Onde fica no original | Situação na skill | Depende de serviço externo? |
|---|---|---|---|
| Chat com vários provedores (60 modelos OpenRouter, Venice, local) | `index.html`, `api/routes/chat.ts` | `perguntar` (OpenRouter, `--provedor local` ou `outro`) | Sim: OpenRouter (chave paga) ou um servidor local |
| **ULTRAPLINIAN** (corrida de modelos em 5 camadas + pontuação) | `api/lib/ultraplinian.ts` | `comparar`, com as mesmas camadas e tempos (mínimo 5, +5 s, limite 45 s, 25 s por modelo, 2 repetições em 429); **pontuação neutra** | Sim: OpenRouter ou servidor local |
| **CONSORTIUM** (um modelo orquestrador sintetiza as respostas) | `api/lib/consortium.ts` | Fluxo da skill: o próprio Claude lê as respostas salvas e sintetiza | Só as respostas dos modelos |
| **AutoTune** (20 contextos → parâmetros de amostragem) | `index.html` | `autotune`, igual ao original + padrões em português | Não |
| Aprendizado do AutoTune por notas (média móvel) | `src/lib/autotune-feedback.ts` | `nota` e `aprendizado`, estendido aos 20 contextos | Não |
| **STM** (hedge reducer, direct mode, casual mode) | `src/stm/modules.ts` | `stm`, + equivalentes em português | Não |
| Modelos locais (Ollama, LM Studio, llama.cpp, vLLM) | `LOCAL_MODELS.md` | `--provedor local` (`GOD_MODE_LOCAL_URL`) | Servidor na máquina do usuário |
| **GODMODE CLASSIC** (5 combinações modelo + prompt de jailbreak) | `src/lib/libertas.ts`, `godmode-prompt.ts` | **Não integrado**: são prompts para contornar as proteções dos modelos | — |
| Prompt de sistema "GODMODE" e diretiva "nunca recuse" (`DEPTH_DIRECTIVE`) | `godmode-prompt.ts`, `ultraplinian.ts` | **Não integrado**, pelo mesmo motivo | — |
| "Boost GODMODE" de parâmetros ("mais direto/sem censura") | `ultraplinian.ts`, `index.html` | **Não integrado** (o AutoTune daqui não aplica o boost) | — |
| **Parseltongue** (33 técnicas de ofuscação de palavras-gatilho) | `src/lib/parseltongue.ts` | **Não integrado**: serve para escapar dos filtros de segurança | — |
| Critério "anti-recusa" da pontuação (25 dos 100 pontos) | `scoreResponse` | **Removido**; recusa só aparece como aviso `possivel_recusa` | — |
| Classificador de dano, telemetria e dataset no Hugging Face | `classify*.ts`, `telemetry.ts`, `functions/`, `api/lib/hf-*.ts` | **Não integrado**: a skill não envia nada além das chamadas de modelo pedidas | — |
| Interface web, frontend React, servidor Express, Docker, Cloudflare | `index.html`, `src/`, `api/`, `Dockerfile*` | Fica no app original; aqui a interface é o Claude Code | — |
| Histórico no navegador, temas, personas, easter eggs, visão de imagens | `index.html`, `src/components/` | Fica no app original (o Claude já lê imagens) | — |

## Mudanças em relação ao código original

- **AutoTune:** sem o boost GODMODE; padrões em português usados quando a mensagem parece português; conversa
  longa aumenta só a penalidade de repetição (como no `index.html`); aprendizado só na estratégia `adaptive`.
- **STM:** maiúscula só onde a remoção abriu uma frase (o original capitalizava toda linha que começasse em
  minúscula e apagava o recuo, o que estraga código); `\b` depois dos preâmbulos (o original cortava "Surely" em "ly").
- **Pontuação:** comprimento 25 + estrutura 20 + objetividade 15 + relevância 15, normalizado para 0–100; a
  relevância compara palavras sem pontuação.
- **Chamadas:** sem `HTTP-Referer`/`X-Title` do godmod3.ai (vai `X-Title: god-mode (Claude Code)`); confere a chave
  em `/key` antes de enviar a pergunta; teto de custo estimado pelos preços públicos; pula modelos fora do catálogo.

## Licença

`god_mode.py` deriva de código AGPL-3.0 e segue essa licença. Se você distribuir esse arquivo, ou oferecê-lo a
outras pessoas pela rede, precisa oferecer também o código-fonte dele sob a AGPL-3.0. `SKILL.md`, `ORIGEM.md` e
`testes/test_god_mode.py` foram escritos para esta adaptação.
