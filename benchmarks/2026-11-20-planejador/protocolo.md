# Comparação do planejador de missões no POCO

A unidade de teste é uma chamada real da capacidade `tela` com `acao=missao` pelo conector Controle Geral. A execução usa o catálogo e a política do POCO, o Claude Sonnet 5.5 com esforço alto e o despachante de produção. Os 40 pedidos em `casos.tsv` são consultas. Os dez casos iniciados com I não são realizáveis a partir das opções disponíveis. O pedido é a única parte do caso enviada ao planejador. A lista de operações esperadas serve exclusivamente à avaliação.

## Rodada

1. Obtenha a agenda com `agenda()` de `analisar.py`. Ela usa uma semente fixa e embaralha separadamente as duas repetições.
2. Execute as 80 chamadas de uma versão em sequência. Para cada pedido envie `{"nome":"tela","argumentos":{"acao":"missao","texto":pedido}}`. Cronometre da emissão ao retorno. Repita a agenda idêntica com a segunda versão. O teste usa blocos por versão porque cada instalação reinicia o serviço no único POCO.
3. Confira a ordem exata das operações e os recibos. Bateria exige uma porcentagem numérica; capacidades exige uma lista; política exige o campo booleano travado e o perfil; servidor exige os objetos servidor e catálogo; progresso exige estado e contador de perfis testados. Pedidos impossíveis exigem estado interrompido e nenhuma operação. Guarde só o tipo de resultado e se a conferência passou. Não grave valores de autenticação, bateria, aparelhos, permissões ou inventário.
4. Uma falha de transporte tem resultado próprio e não é uma recusa correta. Se a sessão terminar, preserve essa tentativa e retome no próximo caso após restabelecer a conexão.
5. Leia os registros com `python analisar.py`. O relatório verifica unicidade por versão, caso e repetição. O critério definido antes da coleta é pelo menos 54 de 60 pedidos viáveis, interrupção correta nos 20 inviáveis e zero operações extras. Ordem errada, omissão e falta de recibo também reprovam o caso.

Cada pedido só exercita as cinco opções de consulta disponíveis por padrão. Duas repetições de um mesmo texto não são dois objetivos independentes. Diferenças de rede e carga da API entre os blocos podem afetar comparações de latência.
