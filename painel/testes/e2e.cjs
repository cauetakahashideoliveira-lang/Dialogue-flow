// Teste de ponta a ponta da Central de Controle contra o Worker local (wrangler dev) e o código real do celular.
// Em painel/, npm run test:e2e inicia o Worker e o banco local descartável.
// A "digital" é o autenticador virtual do Chromium (CDP WebAuthn), com verificação do usuário.
const { chromium } = require('playwright');
const { execFileSync, spawn } = require('child_process');
const nodeCrypto = require('crypto');
const fs = require('fs'), os = require('os'), path = require('path');

const BASE = process.argv[2] || 'http://localhost:8787';
const persistencia = process.env.E2E_ESTADO ? ['--persist-to', process.env.E2E_ESTADO] : [];
const codigoInicial = process.env.E2E_CODIGO || 'codigo-de-teste-123';
const RAIZ = path.resolve(__dirname, '..', '..');
const PASTA = fs.mkdtempSync(path.join(os.tmpdir(), 'celular-'));
let falhas = 0;
const filhos = [];
process.once('exit', () => {
  for (const p of filhos) if (!p.killed) p.kill();
  fs.rmSync(PASTA, { recursive: true, force: true });
});
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
  const navegador = await chromium.launch({ executablePath: process.env.E2E_CHROMIUM });
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
  await pagina.fill('#codigoInicial', codigoInicial);
  await pagina.fill('#nomePasskey', 'POCO (teste)');
  ok(/cadastrada/.test(await clicar('#btPrimeiro')), 'primeira passkey cadastrada com a digital');
  await pagina.waitForSelector('#logado:not(.escondido)');
  ok(await pagina.isVisible('#btEmergencia'), 'painel aberto depois da digital');
  ok(await semSessao('registro/opcoes', { codigo_inicial: codigoInicial }) === 403,
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

  // 4b. Etapa 1b: o Claude entra pelo painel (OAuth com a digital); o painel repassa ao celular, assinado
  const FALSO = `import json,sys\nfrom http.server import BaseHTTPRequestHandler, ThreadingHTTPServer\nfrom controle_ir import painel\nP=sys.argv[1];n={'chamadas':0}\nclass H(BaseHTTPRequestHandler):\n  def log_message(s,*a):pass\n  def _r(s,st,d):\n    b=json.dumps(d).encode();s.send_response(st);s.send_header('Content-Type','application/json');s.send_header('Content-Length',str(len(b)));s.end_headers();s.wfile.write(b)\n  def do_GET(s):s._r(200,n)\n  def do_POST(s):\n    b=s.rfile.read(int(s.headers['Content-Length']))\n    if s.path!='/mcp/segredo-teste':return s._r(401,{'erro':'segredo'})\n    if not painel.verificar_requisicao(P,s.headers.get('X-Painel-Assinatura'),b):return s._r(401,{'erro':'assinatura'})\n    m=json.loads(b)\n    if m.get('method')=='tools/list':return s._r(200,{'jsonrpc':'2.0','id':m.get('id'),'result':{'tools':[{'name':'controlar','inputSchema':{'type':'object'}}]}})\n    n['chamadas']+=1\n    s._r(200,{'jsonrpc':'2.0','id':m.get('id'),'result':{'content':[{'type':'text','text':json.dumps({'via':'celular','ferramenta':(m.get('params') or {}).get('name')})}]}})\nsrv=ThreadingHTTPServer(('127.0.0.1',0),H)\nprint(srv.server_port,flush=True)\nsrv.serve_forever()`;
  const falso = spawn('python3', ['-c', FALSO, PASTA], {
    env: { ...process.env, PYTHONPATH: path.join(RAIZ, 'controle-ir') }, stdio: ['ignore', 'pipe', 'inherit'],
  });
  filhos.push(falso);
  const linhas = require('node:readline').createInterface({ input: falso.stdout });
  const { value: porta } = await linhas[Symbol.asyncIterator]().next();
  linhas.close();
  if (!/^\d+$/.test(porta)) throw new Error('O celular simulado não iniciou');
  const endereco = `http://127.0.0.1:${porta}`;
  const chamadasNoCelular = async () => (await (await fetch(endereco)).json()).chamadas;
  celular(`r=painel.sincronizar(P,'e2e',url_mcp=lambda:'${endereco}/mcp/segredo-teste')\nprint(json.dumps(r))`);
  const semToken = await fetch(`${BASE}/mcp`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: '{}' });
  ok(semToken.status === 401 && /resource_metadata/.test(semToken.headers.get('www-authenticate') || ''), '/mcp sem token → 401 apontando para o OAuth');
  const meta = await (await fetch(`${BASE}/.well-known/oauth-protected-resource/mcp`)).json();
  ok(meta.resource === `${BASE}/mcp` && meta.authorization_servers?.length === 1, 'metadados OAuth publicados (RFC 9728)');
  const registrar = uris => fetch(`${BASE}/oauth/register`, { method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ client_name: 'Claude (teste)', redirect_uris: uris, token_endpoint_auth_method: 'none',
      grant_types: ['authorization_code', 'refresh_token'], response_types: ['code'] }) });
  ok((await registrar(['https://atacante.example/cb'])).status === 400, 'cliente com destino de terceiros não se registra');
  for (const retorno of ['connector_platform_oauth_redirect', 'connector/oauth/conector-de-teste']) {
    const url = 'https://chatgpt.com/' + retorno;
    const registro = await registrar([url]);
    const clienteChatGPT = await registro.json();
    ok(registro.ok && clienteChatGPT.redirect_uris?.includes(url), 'retorno do ChatGPT registrado: ' + retorno);
  }
  const cliente = await (await registrar(['https://claude.ai/api/mcp/auth_callback'])).json();
  const b64u = b => b.toString('base64').replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  const verificador = b64u(nodeCrypto.randomBytes(32));
  const desafioPkce = b64u(nodeCrypto.createHash('sha256').update(verificador).digest());
  const q = new URLSearchParams({ response_type: 'code', client_id: cliente.client_id, redirect_uri: 'https://claude.ai/api/mcp/auth_callback',
    code_challenge: desafioPkce, code_challenge_method: 'S256', state: 'st123', scope: 'controle', resource: `${BASE}/mcp` });
  let voltou = null;
  await pagina.route('https://claude.ai/**', r => { voltou = r.request().url(); r.fulfill({ status: 200, body: 'ok' }); });
  await pagina.goto(`${BASE}/authorize?${q}`);
  ok(/Claude \(teste\)/.test(await pagina.textContent('#pedido')) && /claude\.ai/.test(await pagina.textContent('#pedido')),
    'página de autorização mostra o app e o destino (claude.ai)');
  await pagina.click('#btAutorizar');
  for (let i = 0; i < 50 && !voltou; i++) await pagina.waitForTimeout(100);
  const cb = new URL(voltou || 'https://x/');
  ok(cb.searchParams.get('state') === 'st123' && cb.searchParams.get('code'), 'com a digital, o código volta para o Claude');
  const tok = await (await fetch(`${BASE}/oauth/token`, { method: 'POST', headers: { 'content-type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ grant_type: 'authorization_code', code: cb.searchParams.get('code'), redirect_uri: 'https://claude.ai/api/mcp/auth_callback',
      client_id: cliente.client_id, code_verifier: verificador, resource: `${BASE}/mcp` }) })).json();
  ok(!!tok.access_token, 'token OAuth emitido (PKCE)');
  const manutencao = corpo => fetch(`${BASE}/mcp`, {
    method: 'POST', headers: { authorization: `Bearer ${tok.access_token}`, 'content-type': 'application/json',
      accept: 'application/json' }, body: JSON.stringify({ jsonrpc: '2.0', ...corpo }),
  });
  const pong = await (await manutencao({ method: 'ping', id: 11 })).json();
  const inicializado = await manutencao({ method: 'notifications/initialized' });
  ok(pong.id === 11 && Object.keys(pong.result).length === 0 && inicializado.status === 202
    && await chamadasNoCelular() === 0, 'manutenção MCP termina na Central sem acordar o celular');
  const chamar = (nome, token = tok.access_token) => fetch(`${BASE}/mcp`, { method: 'POST',
    headers: { 'content-type': 'application/json', accept: 'application/json', authorization: `Bearer ${token}` },
    body: JSON.stringify({ jsonrpc: '2.0', id: 7, method: 'tools/call', params: { name: nome, arguments: {} } }) });
  let r = await (await chamar('executar_comando')).json();
  ok(/"via": ?"celular"/.test(r.result?.content?.[0]?.text || '') && await chamadasNoCelular() === 1,
    'armado: a chamada chega ao celular, com a assinatura do painel conferida pelo código real');
  // 4b'. Canal direto: o celular (código real: controle_ir.canal) disca para a Central e mantém o WebSocket aberto;
  //      as chamadas passam por ele (sem túnel) e os avisos da Central chegam na hora
  const MARCA = path.join(PASTA, 'acordou.txt');
  const acordadas = () => fs.existsSync(MARCA) ? fs.readFileSync(MARCA, 'utf8').length : 0;
  const esperar = async (cond, ms = 8000) => { const fim = Date.now() + ms; while (Date.now() < fim) { if (await cond()) return true; await new Promise(z => setTimeout(z, 150)); } return false; };
  const CANAL = `import sys,time,os\nfrom controle_ir.canal import Canal\nP=sys.argv[1]\nm=os.path.join(P,'acordou.txt')\ndef ac():\n  open(m,'a').write('x')\nCanal(P,${porta},'segredo-teste',ao_sincronizar=ac).iniciar()\nwhile True: time.sleep(1)`;
  let canal = spawn('python3', ['-c', CANAL, PASTA], { env: { ...process.env, PYTHONPATH: path.join(RAIZ, 'controle-ir') }, stdio: 'ignore' });
  filhos.push(canal);
  ok(await esperar(() => acordadas() >= 1), 'canal direto aberto pelo celular, com o token do aparelho');
  let rc = await chamar('controlar');
  let tc = await rc.json();
  ok(rc.headers.get('x-via') === 'canal' && /"via": ?"celular"/.test(tc.result?.content?.[0]?.text || '') && await chamadasNoCelular() === 2,
    'com o canal, a chamada vai por ele (sem túnel), ainda assinada pela Central e conferida no celular');
  await pagina.unroute('https://claude.ai/**');
  await pagina.goto(BASE); await pagina.waitForSelector('#logado:not(.escondido)');
  ok(/Claude \(teste\) → claude\.ai/.test(await pagina.textContent('#acessos')), 'painel lista o acesso autorizado');
  const versao = await (await fetch(`${BASE}/versao`)).json();
  ok(versao.recursos?.includes('pc-ponte') && /^\d{4}-\d{2}-\d{2}/.test(versao.central || ''), `/versao publica a versão da Central (${versao.central})`);
  // 4b''. PC (agente_pc, código real): segundo aparelho no MESMO conector, ferramentas pc_* pelo canal dele,
  //       com o estado de armado próprio
  const PASTA_PC = fs.mkdtempSync(path.join(os.tmpdir(), 'pc-'));
  const envPC = { ...process.env, AGENTE_PC_DIR: PASTA_PC, AGENTE_PC_PORTA: String(41000 + Math.floor(Math.random() * 9000)),
    PYTHONPATH: [path.join(RAIZ, 'pc'), path.join(RAIZ, 'controle-ir')].join(path.delimiter) };
  await clicar('#btParear');
  const codigoPC = (await pagina.textContent('#pareamento')).match(/ ([A-Z0-9]{8})$/)[1];
  execFileSync('python3', ['-m', 'agente_pc', 'parear', BASE, codigoPC, '--nome', 'PC-teste'], { env: envPC, stdio: 'ignore' });
  const agentePC = spawn('python3', ['-m', 'agente_pc', 'ligar'], { env: envPC, stdio: 'ignore' });
  filhos.push(agentePC);
  const chamarCom = (nome, args = {}) => fetch(`${BASE}/mcp`, { method: 'POST',
    headers: { 'content-type': 'application/json', accept: 'application/json', authorization: `Bearer ${tok.access_token}` },
    body: JSON.stringify({ jsonrpc: '2.0', id: 8, method: 'tools/call', params: { name: nome, arguments: args } }) });
  const textoDe = async resp => { const j = await resp.json(); return { j, d: JSON.parse(j.result?.content?.[0]?.text || '{}') }; };
  let pcOk = await esperar(async () => (await chamarCom('pc_consultar')).headers.get('x-via') === 'pc', 15000);
  ok(pcOk, 'PC pareado e conectado pelo canal: pc_consultar chega ao agente do PC');
  let { d: dc } = await textoDe(await chamarCom('pc_consultar'));
  ok(/^pc-/.test(dc.agente || '') && dc.seguranca?.armado === false && dc.pc?.memoria, 'pc_consultar: retrato do PC; recém-pareado, DESARMADO');
  const lista = await (await manutencao({ method: 'tools/list', id: 12 })).json();
  const nomes = (lista.result?.tools || []).map(t => t.name);
  ok(nomes.includes('controlar') && nomes.includes('pc_executar') && nomes.includes('pc_tela'),
    `um conector só: tools/list une as ferramentas do celular e as do PC (${nomes.length})`);
  let { j: jx } = await textoDe(await chamarCom('pc_executar', { comando: 'echo pc-ok' }));
  ok(jx.result?.structuredContent?.onde === 'painel' && /PC está DESARMADO/.test(jx.result?.content?.[0]?.text || ''),
    'PC desarmado: pc_executar barrado NA BORDA (estado do PC, não do celular)');
  await clicar('#btArmar2');
  pcOk = await esperar(async () => { const { d } = await textoDe(await chamarCom('pc_executar', { comando: 'echo pc-ok', aguardar: 20 }));
    return d.status === 'concluida' && /pc-ok/.test(d.saida?.texto || ''); }, 15000);
  ok(pcOk, 'armado com a digital: o comando roda no PC e a saída volta (assinatura conferida pelo agente)');
  const { d: dp } = await textoDe(await chamarCom('executar_capacidade', { nome: 'pc_executar', argumentos: { comando: 'echo via-ponte', aguardar: 20 } }));
  ok(dp.status === 'concluida' && /via-ponte/.test(dp.saida?.texto || '') && await chamadasNoCelular() === 2,
    'conversa antiga (sem pc_* na lista): executar_capacidade(nome="pc_executar") chega ao PC, não ao celular');
  await pagina.reload(); await pagina.waitForSelector('#logado:not(.escondido)');
  ok(/PC-teste/.test(await pagina.textContent('#celulares')) && /pc_executar/.test(await pagina.textContent('#chamadas')),
    'a Central lista o PC e as chamadas pc_* na Atividade');
  // celular fora do ar com túnel morto (ngrok sem o celular devolve 404): o conector continua de pé com o PC
  const MORTO = "from http.server import BaseHTTPRequestHandler as B, ThreadingHTTPServer as S\nclass H(B):\n  def log_message(s,*a):pass\n  def do_POST(s):\n    s.send_response(404);s.send_header('Content-Length','0');s.end_headers()\nsrv=S(('127.0.0.1',0),H)\nprint(srv.server_port,flush=True)\nsrv.serve_forever()";
  const morto = spawn('python3', ['-c', MORTO], { stdio: ['ignore', 'pipe', 'ignore'] });
  filhos.push(morto);
  const portaMorto = String(await new Promise(z => morto.stdout.once('data', z))).trim();
  celular(`r=painel.sincronizar(P,'e2e',url_mcp=lambda:'http://127.0.0.1:${portaMorto}/mcp/x')\nprint(json.dumps(r))`);
  canal.kill('SIGKILL');  // celular desligado (o canal some; a chamada não fica presa para chegar depois)
  const iniSem = await (await manutencao({ method: 'initialize', id: 15, params: { protocolVersion: '2025-06-18' } })).json();
  const listaSem = await (await manutencao({ method: 'tools/list', id: 16 })).json();
  const nomesSem = (listaSem.result?.tools || []).map(t => t.name);
  ok(iniSem.result?.serverInfo?.version === 'central' && nomesSem.includes('pc_executar') && !nomesSem.includes('controlar'),
    'celular fora do ar e túnel devolvendo 404: initialize e tools/list seguem com o PC (o conector não cai)');
  ok(/"agente": ?"pc-/.test((await (await chamarCom('pc_consultar')).json()).result?.content?.[0]?.text || ''),
    'e o PC responde normalmente com o celular fora do ar');
  celular(`r=painel.sincronizar(P,'e2e',url_mcp=lambda:'${endereco}/mcp/segredo-teste')\nprint(json.dumps(r))`);
  const antesVolta = acordadas();
  canal = spawn('python3', ['-c', CANAL, PASTA], { env: { ...process.env, PYTHONPATH: path.join(RAIZ, 'controle-ir') }, stdio: 'ignore' });
  filhos.push(canal);
  morto.kill();
  ok(await esperar(() => acordadas() > antesVolta, 20000), 'o celular volta e reabre o canal sozinho');
  agentePC.kill('SIGKILL');
  pcOk = await esperar(async () => /fora do ar/.test(JSON.stringify((await textoDe(await chamarCom('pc_consultar'))).d)), 90000);
  ok(pcOk, 'PC desligado: a chamada explica que ele está fora do ar (sem travar o conector)');
  const lista2 = await (await manutencao({ method: 'tools/list', id: 13 })).json();
  ok((lista2.result?.tools || []).some(t => t.name === 'pc_executar'), 'com o PC fora do ar, as ferramentas dele continuam na lista (última conhecida)');
  await clicar('text=Revogar PC-teste');
  const lista3 = await (await manutencao({ method: 'tools/list', id: 14 })).json();
  ok(!(lista3.result?.tools || []).some(t => t.name.startsWith('pc_')) && (await textoDe(await chamarCom('pc_consultar'))).j.result?.isError,
    'PC revogado na Central: as ferramentas pc_* somem e a chamada é recusada');
  fs.rmSync(PASTA_PC, { recursive: true, force: true });
  await new Promise(z => setTimeout(z, 600));

  const antesDoAviso = acordadas();
  await clicar('#btDesarmar');
  ok(await esperar(() => acordadas() > antesDoAviso, 3000), 'desarmar chega ao celular NA HORA pelo canal (antes: até 30 s)');
  r = await (await chamar('executar_comando')).json();
  ok(r.result?.structuredContent?.onde === 'painel' && await chamadasNoCelular() === 2, 'desarmado: terminal barrado NA BORDA (nem chega ao celular)');
  r = await (await chamar('controlar')).json();
  ok(/"via": ?"celular"/.test(r.result?.content?.[0]?.text || ''), 'desarmado: infravermelho continua passando');
  // 4c. Atividade, "em uso agora" e tela ao vivo (sem nenhuma aprovação a mais)
  await pagina.reload(); await pagina.waitForSelector('#logado:not(.escondido)');
  const ativ = await pagina.textContent('#chamadas');
  ok(/executar_comando/.test(ativ) && /barrado na Central/.test(ativ) && /controlar/.test(ativ) && /terminal/.test(ativ),
    'Atividade do Claude lista cada chamada (ok e barrada) com os recursos');
  const indicadorCanal = pagina.locator('#celulares .saude li').filter({ hasText: 'Canal direto' });
  ok(await indicadorCanal.locator('strong').textContent() === 'Conectado', 'a Central mostra o canal direto ativo');
  celular(`import os,time\nos.makedirs(os.path.join(P,'tarefas'),exist_ok=True)\nopen(os.path.join(P,'tarefas','9.json'),'w').write(json.dumps({'id':'9','status':'executando','comando':'termux-camera-photo -c 0 /tmp/x.jpg','inicio':time.time()}))\nfrom controle_ir import observador\nr=painel.sincronizar(P,'e2e',em_uso=lambda o,v: observador.em_uso(P,False,v))\nprint(json.dumps(r))`);
  await pagina.reload(); await pagina.waitForSelector('#logado:not(.escondido)');
  ok(/termux-camera-photo/.test(await pagina.textContent('#emUso')) && /câmera/.test(await pagina.textContent('#emUso')),
    '"Agora no celular" mostra o comando em execução e que ele usa a câmera');
  await pagina.click('#btTela'); await pagina.waitForTimeout(500);
  const jpg = 'iVBORw0KGgo' + 'A'.repeat(64);
  const tv = celular(`import time\nr=painel.sincronizar(P,'e2e')\ncfg=painel.ler(P)\nst,_=painel._http('POST',cfg['url']+'/api/celular/quadro',cfg['token'],{'jpeg':${JSON.stringify(jpg)}})\nprint(json.dumps({'ao_vivo':r['ao_vivo_ate']>time.time(),'st':st}))`);
  ok(tv.ao_vivo && tv.st === 200, 'com o painel assistindo, o celular recebe o pedido e envia o quadro');
  await pagina.waitForFunction(() => (document.querySelector('#telaImg').getAttribute('src') || '').startsWith('data:image/jpeg'), null, { timeout: 8000 });
  ok(true, 'o quadro aparece na Central');
  await pagina.click('#btTela'); await pagina.waitForTimeout(600);
  const tv2 = celular(`cfg=painel.ler(P)\nst,_=painel._http('POST',cfg['url']+'/api/celular/quadro',cfg['token'],{'jpeg':${JSON.stringify(jpg)}})\nprint(json.dumps({'st':st}))`);
  ok(tv2.st === 409, 'parou de assistir: o celular para de mandar e o último quadro é apagado');
  await pagina.check('#soPainel'); await pagina.waitForTimeout(800);
  ok(celular(`painel.sincronizar(P,'e2e')\nprint(json.dumps({'s':Politica(P).efetiva().get('so_pelo_painel')}))`).s === true,
    '"só pelo painel" chega ao celular pelo estado assinado');
  process.kill(canal.pid, 'SIGSTOP');  // celular congelado: a conexão parece aberta, mas ninguém responde
  let t0 = Date.now(), xc = await chamar('controlar');
  ok(xc.headers.get('x-via') === 'tunel' && xc.ok && Date.now() - t0 < 9000,
    `canal mudo (celular congelado): sem confirmação em 5 s, a chamada vai pelo túnel (${Date.now() - t0} ms)`);
  t0 = Date.now(); xc = await chamar('controlar');
  ok(xc.headers.get('x-via') === 'tunel' && Date.now() - t0 < 2000, 'depois disso o canal mudo é descartado: direto pelo túnel');
  canal.kill('SIGKILL');
  await pagina.click('text=Revogar acesso'); await pagina.waitForTimeout(800);
  ok((await chamar('controlar')).status === 401, 'acesso revogado no painel: o token para de valer na hora');
  falso.kill();

  // 5. Sem digital recente, armar é recusado; a interface pede a digital e conclui
  execFileSync('npx', ['wrangler', 'd1', 'execute', 'painel', '--local', ...persistencia, '--command', 'UPDATE sessoes SET passkey_em = passkey_em - 600'], { cwd: path.join(RAIZ, 'painel'), stdio: 'ignore' });
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
  await pagina.click(`text=Revogar POCO`); await pagina.waitForTimeout(800);
  s = sincronizar();
  ok(s.revogado === true && s.efetiva.armado_ate === 0, `celular ${ap} revogado: falha fechada, desarmado`);

  // 8. Histórico encadeado: íntegro, e a adulteração é detectada
  ok(/íntegro/.test(await clicar('#btIntegridade')), 'histórico íntegro');
  ok(/stado_alterado|EMERG/.test(await pagina.textContent('#eventos')), 'histórico mostra as mudanças de estado');
  execFileSync('npx', ['wrangler', 'd1', 'execute', 'painel', '--local', ...persistencia, '--command',
    `UPDATE eventos SET dados = '{"armado_ate":0,"adulterado":1}' WHERE id = (SELECT MIN(id) FROM eventos WHERE tipo = 'estado_alterado')`],
    { cwd: path.join(RAIZ, 'painel'), stdio: 'ignore' });
  ok(/alterado no evento \d+/.test(await clicar('#btIntegridade')), 'adulteração do histórico é detectada');

  await navegador.close();
  console.log(falhas ? `\n${falhas} falha(s)` : '\nTudo certo');
  process.exit(falhas ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
