# Regressões: cada erro vira um teste

Um sistema bom aprende com os próprios erros. Por isso, toda falha corrigida recebe três coisas:

1. **Uma linha nesta tabela**, com código, data, sintoma, causa, correção e teste.
2. **Um teste que falha sem a correção.** Desfaça a correção uma vez e confira que o teste pega o defeito. Um teste
   que passa com ou sem a correção não protege nada.
3. **O teste no CI** (`.github/workflows/verificar.yml`, jobs `servico` e `central`).

O mesmo erro não pode voltar pelo mesmo motivo.

Prefixos:
- **C**: Central (`painel/`), testada no e2e `painel/testes/e2e.cjs`.
- **A**: agente do PC (`pc/agente_pc`), em `testes/test_agente_pc.py`.
- **S**: serviço do celular (`controle-ir`).

O kit de diagnóstico do PC (inventário, benchmark, rede…) fica no repositório Roblox, em `docs/regressoes.md` de lá.

| Código | Data | Sintoma | Causa | Correção | Teste |
|---|---|---|---|---|---|
| C1 | 25/11 | Com o serviço do celular parado, o conector inteiro caía (405 / tempo esgotado) | A Central ia para o túnel ngrok morto (404) e não tinha plano B | `initialize` e `tools/list` respondidos com o PC quando o celular não responde (#27) | e2e "celular fora do ar e túnel devolvendo 404: initialize e tools/list seguem com o PC" |
| C2 | 26/11 | "PC fora do ar" em toda chamada, com o agente conectado ("canal conectado à Central" no `agente.log`) | O Wi-Fi piscou e a conexão velha ficou em CLOSING no Durable Object. A Central pegava a última de `getWebSockets()`, que não tem ordem garantida e ainda inclui conexões fechando | `socket()` ignora CLOSING/CLOSED e escolhe a batida mais recente (2026-11-26.2/.3) | e2e "conexão fantasma (PC congelado sem fechar) e reconexão: a Central usa a conexão aberta mais recente" |
| C3 | 26/11 | Chamada feita durante uma queda de segundos do Wi-Fi voltava "PC fora do ar" na hora | Sem nova tentativa: o PC reconecta em ~3 s, mas a chamada já tinha falhado | Espera o canal voltar (até 10 s) e repete uma vez a mesma requisição, com a mesma assinatura (o PC recusa reenvio: nunca executa duas vezes) | e2e "PC caiu e voltou no meio: a Central esperou o canal e repetiu a chamada" |
| A1 | 25/11 | O PC não voltou depois de um deploy da Central (pc-1.0.0) | Uma exceção inesperada matava o laço do canal | `CanalPC` reinicia o laço; reconexão em até 1 min (#29) | (e2e "o PC original descongela e volta a atender pelo canal" cobre a reconexão) |
| A2 | 26/11 | `pc_atualizar` sem `ref` falhava depois de um `pc_atualizar(ref=…)` | O repositório ficava com HEAD destacado e o `git pull` recusava | Volta para a branch padrão do origin antes do pull | `test_atualizar_sem_ref_sai_do_head_destacado` (repositório git de verdade) |
| A3 | 26/11 | `PermissionError` no `agente.log` e chamada presa até o limite de espera | O antivírus segurava o `.ps1` da tarefa; o `unlink` lançava exceção e o evento de fim nunca era sinalizado | `unlink` protegido; o fim é sinalizado sempre | `test_ps1_preso_nao_derruba_o_fim_da_tarefa` (falha sem a correção: "pedir ficou preso 10.0 s") |
| A4 | 26/11 | Botão "Ligar Agente PC" sem saber se o PC está na Central | O `/saude` não dizia nada do canal | `/saude` com `canal: {conectado, erro}` | `test_saude_mostra_o_canal_quando_informado` |
| A5 | 26/11 | `pc_consultar` dizia "node: false, ollama: false" depois de instalados | O laço `iniciar.ps1` mantinha o PATH do logon | PATH relido do registro a cada volta do laço | `test_iniciar_rele_o_path_a_cada_volta` |
| S1 | 25/11 | `empacotar.sh --verificar` quebrou ao editar `canal.py` para o PC | O pacote do celular não pode mudar sem nova versão | Correção só em `pc/agente_pc/cli.py` (`CanalPC`) | CI `servico`: `bash ferramentas/empacotar.sh --verificar` |
| S2 | 25/11 | Paridade quebrada das ferramentas que sempre respondem | `pc_*` entrou em `SEMPRE` por engano | `SEMPRE_PC` separado | `test_consistencia.test_pc_mesmas_ferramentas_sempre_liberadas` |
