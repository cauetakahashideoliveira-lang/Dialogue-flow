// Teste de ponta a ponta do Painel da Casa contra o Worker local (wrangler dev) e o código real do celular.
// Uso: (em painel/) npm run dev em outro terminal com --var CODIGO_INICIAL:codigo-de-teste-123; depois
//      node testes/e2e.cjs http://localhost:8787
// A "digital" é o autenticador virtual do Chromium (CDP WebAuthn), com verificação do usuário.
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs'), os = require('os'), path = require('path');

const BASE = process.argv[2] || 'http://localhost:8787';
const RAIZ = path.resolve(__dirname, '..', '..');
const PASTA = fs.mkdtempSync(path.join(os.tmpdir(), 'celular-'));
let falhas = 0;
const ok = (cond, txt) => { console.log(`${cond ? '✔' : '✘'} ${txt}`); if (!cond) falhas++; };

function celular(codigoPy) {  // roda o código real do controle-ir (controle_ir.painel) numa pasta temporária
  const py = `import json,sys\nfrom controle_ir import painel\nfrom controle_ir.execucao import Politica\nP=${JSON.stringify(PASTA)}\n${codigoPy}`;
  return JSON.parse(execFileSync('python3', ['-c', py], { env: { ...process.env, PYTHONPATH: path.join(RAIZ, 'controle-ir') } }).toString());
}
const sincronizar = () => celular(`r=painel.sincronizar(P,'e2e')\nprint(json.dumps({**r,'efetiva':{k:Politica(P).efetiva().get(k) for k in ('armado_ate','travado','painel_seq')}}))`);
async function semSessao(rota, corpo = {}, cab = {}) {
  const r = await fetch(`${BASE}/api/${rota}`, { method: 'POST', headers: { 'content-type': 'application/json', 'x-painel': '1', ...cab }, body: JSON.stringify(corpo) });
  return r.status;
}

(async () => {
  const navegador = await chromium.launch();
  const pagina = await navegador.newPage();
  pagina.on('dialog', d => d.accept());
  const cdp = await pagina.context().newCDPSession(pagina);
  await cdp.send('WebAuthn.enable');
  await cdp.send('WebAuthn.addVirtualAuthenticator', { options: { protocol: 'ctap2', transport: 'internal',
    hasResidentKey: true, hasUserVerification: true, isUserVerified: true, automaticPresenceSimulation: true } });
  const msg = async () => (await pagina.textContent('#msg')).trim();
  const clicar = async (sel, espera = 'Entrou') => { await pagina.click(sel); await pagina.waitForFunction(
    () => !['…', ''].includes(document.querySelector('#msg').textContent.trim())); return msg(); };

  await pagina.goto(BASE);
  // 1. Conhecer a URL não dá acesso
  ok(await semSessao('painel') === 401, 'sem sessão: /api/painel → 401');
  ok(await semSessao('armar') === 401, 'sem sessão: armar → 401');
  ok((await fetch(`${BASE}/api/celular/estado`)).status === 401, 'celular sem token → 401');
  ok((await fetch(`${BASE}/api/celular/estado`, { headers: { authorization: 'Bearer inventado' } })).status === 401, 'token inventado → 401');
  ok(await semSessao('armar', {}, { origin: 'https://atacante.example' }) === 403, 'outra origem → 403');

  // 2. Primeira passkey exige o código inicial
  await pagina.click('summary');
  await pagina.fill('#codigoInicial', 'errado-errado-errado');
  ok(/incorreto/.test(await clicar('#btPrimeiro')), 'código inicial errado é recusado');
  await pagina.fill('#codigoInicial', 'codigo-de-teste-123');
  await pagina.fill('#nomePasskey', 'POCO (teste)');
  ok(/cadastrada/.test(await clicar('#btPrimeiro')), 'primeira passkey cadastrada com a digital');
  await pagina.waitForSelector('#logado:not(.escondido)');
  ok(await pagina.isVisible('#btEmergencia'), 'painel aberto depois da digital');
  ok(await semSessao('registro/opcoes', { codigo_inicial: 'codigo-de-teste-123' }) === 403,
    'depois da 1ª passkey, o código inicial não cadastra mais ninguém');

  // 2b. Segundo aparelho (iPad) só entra com convite de uso único criado com a digital
  ok(await semSessao('registro/opcoes', { convite: 'inventado' }) === 403, 'convite inventado é recusado');
  await clicar('#btConvite');
  const link = (await pagina.textContent('#convite')).match(/(https?:\S+#convite=\S+)/)[1];
  const ipad = await navegador.newContext(); const pIpad = await ipad.newPage();
  const cdp2 = await ipad.newCDPSession(pIpad); await cdp2.send('WebAuthn.enable');
  await cdp2.send('WebAuthn.addVirtualAuthenticator', { options: { protocol: 'ctap2', transport: 'internal',
    hasResidentKey: true, hasUserVerification: true, isUserVerified: true, automaticPresenceSimulation: true } });
  const conv0 = new URL(link).hash.split('=')[1];
  ok(await semSessao('registro/opcoes', { convite: conv0 }) === 200, 'tentativa que não conclui não gasta o convite');
  await pIpad.goto(link); await pIpad.fill('#nomeConvite', 'iPad (teste)'); await pIpad.click('#btAceitar');
  await pIpad.waitForSelector('#logado:not(.escondido)');
  ok(/iPad \(teste\)/.test(await pIpad.textContent('#passkeys')), 'iPad cadastrado pelo convite, com a digital dele');
  const conv = new URL(link).hash.split('=')[1];
  ok(await semSessao('registro/opcoes', { convite: conv }) === 403, 'o mesmo convite não serve duas vezes');
  await ipad.close();

  // 3. Cadastro do celular (código de uso único) e estado inicial desarmado
  await clicar('#btParear');
  const codigo = (await pagina.textContent('#pareamento')).match(/ ([A-Z0-9]{8})$/)[1];
  const par = celular(`cfg=painel.parear(P,${JSON.stringify(BASE)},${JSON.stringify(codigo)},'POCO','e2e')\np=Politica(P);x=p.ler();x['modo_painel']=True;p.gravar(x)\nprint(json.dumps({'ok':True}))`);
  ok(par.ok, 'celular pareado com o código');
  ok(celular(`\ntry:\n  painel.parear(P+'x',${JSON.stringify(BASE)},${JSON.stringify(codigo)},'X','e2e');print(json.dumps({'ok':True}))\nexcept ValueError as e:\n  print(json.dumps({'ok':False}))`).ok === false,
    'o mesmo código de pareamento não serve duas vezes');
  let s = sincronizar();
  ok(s.seq >= 1 && s.efetiva.armado_ate === 0, 'celular recém-cadastrado começa DESARMADO (estado assinado conferido)');

  // 3b. Histórico do celular: lotes de até 30 numa transação, sem repetir o que o painel já recebeu
  const h = celular(`import time,os\nq=time.strftime('%Y-%m-%d %H:%M:%S')\nopen(os.path.join(P,'auditoria.jsonl'),'a').write(''.join(json.dumps({'quando':q,'evento':'e2e_%d'%i})+'\\n' for i in range(45)))\na=painel.sincronizar(P,'e2e');cfg=painel.ler(P);o=cfg['offset']\nb=painel.sincronizar(P,'e2e')\ncfg=painel.ler(P);cfg['offset']=o;painel.gravar(P,cfg)\nc=painel.sincronizar(P,'e2e')\nprint(json.dumps([a['eventos_aceitos'],b['eventos_aceitos'],c['eventos_enviados'],c['eventos_aceitos']]))`);
  ok(h[0] === 30 && h[1] === 15, `histórico enviado em lotes (30 + 15): ${h}`);
  ok(h[2] === 15 && h[3] === 0, 'reenvio do mesmo trecho (resposta perdida) não duplica no painel');

  // 4. Armar com a digital; o painel só mostra "aplicado" depois que o celular confirma
  await clicar('#btArmar2');
  await pagina.reload(); await pagina.waitForSelector('#logado:not(.escondido)');
  ok(/pendente/.test(await pagina.textContent('#celulares')), 'antes de o celular buscar: "pendente"');
  s = sincronizar();
  ok(s.efetiva.armado_ate > Date.now() / 1000 + 7000, 'celular ARMADO por ~2 h pelo estado assinado');
  await pagina.reload(); await pagina.waitForSelector('#logado:not(.escondido)');
  ok(/aplicado no celular/.test(await pagina.textContent('#celulares')), 'depois da confirmação: "aplicado"');

  // 5. Sem digital recente, armar é recusado; a interface pede a digital e conclui
  execFileSync('npx', ['wrangler', 'd1', 'execute', 'painel', '--local', '--command', 'UPDATE sessoes SET passkey_em = passkey_em - 600'], { cwd: path.join(RAIZ, 'painel'), stdio: 'ignore' });
  const cookies = await pagina.context().cookies();
  const comSessao = (rota, corpo) => fetch(`${BASE}/api/${rota}`, { method: 'POST', headers: { 'content-type': 'application/json', 'x-painel': '1',
    cookie: cookies.map(c => `${c.name}=${c.value}`).join('; ') }, body: JSON.stringify(corpo) }).then(r => r.status);
  ok(await comSessao('armar', { horas: 1 }) === 403, 'sessão sem digital recente não arma (a ampliação exige a digital na hora)');
  ok(/Armado/.test(await clicar('#btArmarDia')), 'pela interface, a digital é pedida e o armar conclui');

  // 6. Emergência: o celular reduz na próxima busca
  await clicar('#btEmergencia');
  s = sincronizar();
  ok(s.travado === 1 && s.efetiva.travado === true, 'EMERGÊNCIA aplicada no celular (travado)');
  ok(celular(`\ntry:\n  Politica(P).armar();print(json.dumps({'ok':True}))\nexcept ValueError:\n  print(json.dumps({'ok':False}))`).ok === false,
    'pareado, o celular não arma sozinho (só o painel)');

  // 7. Revogar o celular corta na hora
  const ap = (await (await fetch(`${BASE}/api/painel`, { method: 'POST', headers: { 'content-type': 'application/json', 'x-painel': '1',
    cookie: cookies.map(c => `${c.name}=${c.value}`).join('; ') }, body: '{}' })).json()).aparelhos[0].id;
  await clicar('#btArmarDia');
  ok(sincronizar().efetiva.armado_ate > 0, 'armado de novo');
  pagina.once('dialog', d => d.accept());
  await pagina.click(`text=Revogar POCO`); await pagina.waitForTimeout(800);
  s = sincronizar();
  ok(s.revogado === true && s.efetiva.armado_ate === 0, `celular ${ap} revogado: falha fechada, desarmado`);

  // 8. Histórico encadeado: íntegro, e a adulteração é detectada
  ok(/íntegro/.test(await clicar('#btIntegridade')), 'histórico íntegro');
  ok(/stado_alterado|EMERG/.test(await pagina.textContent('#eventos')), 'histórico mostra as mudanças de estado');
  execFileSync('npx', ['wrangler', 'd1', 'execute', 'painel', '--local', '--command',
    `UPDATE eventos SET dados = '{"armado_ate":0,"adulterado":1}' WHERE id = (SELECT MIN(id) FROM eventos WHERE tipo = 'estado_alterado')`],
    { cwd: path.join(RAIZ, 'painel'), stdio: 'ignore' });
  ok(/alterado no evento \d+/.test(await clicar('#btIntegridade')), 'adulteração do histórico é detectada');

  await navegador.close();
  console.log(falhas ? `\n${falhas} falha(s)` : '\nTudo certo');
  process.exit(falhas ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
