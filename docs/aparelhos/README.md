# Aparelhos cadastrados — índice para agentes

Fonte única para operar os aparelhos do usuário pelo conector **Controle master** (MCP do celular POCO).
Cada aparelho tem **um arquivo próprio** dentro da pasta do seu cômodo, com perfil, comandos verificados,
sinais extras e ressalvas. Atualizado em 17/11/2026.

## Mapa: cômodo → aparelho → controle

| Cômodo | Nome exato no conector | Aparelho físico | Perfil (controle) | Ficha |
|---|---|---|---|---|
| Quarto | `ar do quarto` | Ar-condicionado **Gree** GWH09KF | SmartIR `climate/1184` "Gree GWH09KF" (catálogo nº 105) + oscilação, visor e turbo gerados | [quarto/ar-do-quarto.md](quarto/ar-do-quarto.md) |
| Quarto | `tv do quarto` | TV **Samsung** (Samsung32, endereço 0x07) | Flipper-IRDB "Samsung TV Full" (catálogo nº 2331) + ligar/desligar diretos + macro Netflix | [quarto/tv-do-quarto.md](quarto/tv-do-quarto.md) |
| Escritório | `ar do escritório` | Ar-condicionado **Carrier** | SmartIR "Carrier Unknown" (catálogo nº 94) | [escritorio/ar-do-escritorio.md](escritorio/ar-do-escritorio.md) |
| Laboratório | `ar condicionado laboratório` | Ar-condicionado **Midea** | o mesmo "Carrier Unknown" (nº 94) + oscilação do perfil Ferroli/York | [laboratorio/ar-condicionado-laboratorio.md](laboratorio/ar-condicionado-laboratorio.md) |

Os arquivos `.ir` ao lado de cada ficha guardam, no formato Flipper, os sinais **adicionados pelo usuário**
(o resto vem do perfil do catálogo). Servem para restaurar um aparelho com `importar` ou
`editar_aparelho(adicionar_comando={conteudo})`.

## Regras para qualquer agente

1. **Use o nome exato da tabela.** "quarto" sozinho é ambíguo (há ar e TV no quarto). Pedido sem cômodo
   ("ligue o ar"): pergunte qual, ou use o único aparelho daquele tipo se só houver um.
2. **Valores aceitos:** a partir do servidor 1.0.6, as instruções do conector já trazem o resumo de cada aparelho
   (valores, faixas, teclas, botões criados, macros, observação); se o pedido couber nele, chame `controlar`
   direto. Chame `opcoes(aparelho)` para o último estado enviado ou para o que não estiver no resumo (no
   servidor 1.0.5 ou anterior, chame sempre antes de comandar). Faixas de temperatura diferem
   (Gree 16–30 °C, Carrier 17–30 °C).
3. **Ar-condicionado é "estado completo":** cada sinal leva modo + temperatura + ventilação juntos.
   Para mudar um valor, mande só esse valor (`controlar(definir={temperatura: 22})`); o resto vem do último envio.
4. **`sinal_enviado` não é confirmação física.** Diga "sinal enviado" e deixe o usuário confirmar.
5. **Recurso que o perfil não tem** (ex.: oscilação no ar do escritório): explique a limitação, não troque a
   escolha do usuário. Se ele pedir para criar o botão, siga a seção "Criar um botão novo".
6. **Ar do escritório e ar do laboratório usam os mesmos códigos** (perfil nº 94): se os dois estiverem ao
   alcance do celular, um comando para um também chega ao outro.

7. **Conector sem resposta:** o usuário liga o serviço só quando vai usar (bateria). Peça para tocar no atalho
   **Ligar Controle IR** da tela inicial e tente de novo em alguns segundos.

## Criar um botão novo (o que funcionou nesta instalação)

- **Ar-condicionado Gree:** não chute quadros pelo protocolo genérico. Parta do sinal real do perfil e troque
  só os bits: `python3 ferramentas/gree_variante.py --modo frio --ventilacao automatica --temperatura 16 --oscilar`
  (ou `--visor-desligado`). Envie com `enviar_sinal(sinal={frequencia, pulsos})`, pergunte se funcionou e só
  então salve com `editar_aparelho(adicionar_comando={nome, funcao, sinal})`.
- **TV Samsung:** códigos Samsung32 no endereço 0x07 (`enviar_sinal(sinal={protocolo:"Samsung32", endereco:7,
  comando:N})`). Teste um por vez, pergunte, e salve o que funcionou. Não varra códigos desconhecidos às cegas:
  a faixa contém comandos ocultos (menu de serviço).
- **Sequências** (ex.: abrir um app): `editar_aparelho(macro={nome, passos:[{teclas:[...]}]})`. As teclas de
  um passo saem com 0,45 s de intervalo.
- `editar_aparelho` com um sinal que o perfil já tem **não duplica**: a resposta (a partir da versão com a
  correção de 17/11) diz "nada adicionado" e aponta a chave existente — use essa chave.

## Manter este índice

Ao cadastrar, renomear ou testar um aparelho: atualize a linha da tabela, a ficha do aparelho e
`docs/estado-atual.md`; depois `graphify update .` para o grafo refletir a mudança. Ressalvas que mudam como
operar (ex.: "os botões extras fixam 16 °C") também vão para `editar_aparelho(observacao="…")`: assim chegam a
qualquer conversa pelo resumo do conector, mesmo sem acesso a este repositório.
