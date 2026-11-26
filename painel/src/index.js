// Central de Controle — administração do controle-ir fora do agente (docs/seguranca.md, Etapa 1).
// Dono: passkeys (WebAuthn, SimpleWebAuthn). Celular: token de aparelho + estado ASSINADO (Ed25519) que ele confere
// com a chave pública fixada no pareamento. Nada aqui é alcançável pelas ferramentas do conector.
import {
  generateAuthenticationOptions, generateRegistrationOptions, verifyAuthenticationResponse,
  verifyRegistrationResponse,
} from '@simplewebauthn/server';
import { isoBase64URL } from '@simplewebauthn/server/helpers';
import { AuthorizationError, CimdFetchError, OAuthProvider } from '@cloudflare/workers-oauth-provider';
import { DurableObject } from 'cloudflare:workers';

const SESSAO_MAX = 12 * 3600, SESSAO_OCIOSA = 30 * 60, PASSKEY_FRESCA = 120, DESAFIO = 300, PAREAMENTO = 600;
const HORAS_MAX = 24;
const VERSAO_CENTRAL = '2026-11-26.5';  // suba a cada mudança da Central (aparece em /versao)
const agora = () => Math.floor(Date.now() / 1000);
const enc = new TextEncoder();

// ---------------------------------------------------------------- esquema (criado sozinho na 1ª requisição)
const ESQUEMA = `
CREATE TABLE IF NOT EXISTS config (k TEXT PRIMARY KEY, v TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS credenciais (
  id TEXT PRIMARY KEY, chave TEXT NOT NULL, contador INTEGER NOT NULL DEFAULT 0, transportes TEXT,
  nome TEXT NOT NULL, criada INTEGER NOT NULL, ultimo_uso INTEGER, revogada INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS desafios (id TEXT PRIMARY KEY, desafio TEXT NOT NULL, tipo TEXT NOT NULL,
  sessao TEXT, expira INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS sessoes (hash TEXT PRIMARY KEY, credencial TEXT NOT NULL, criada INTEGER NOT NULL,
  ultimo INTEGER NOT NULL, passkey_em INTEGER NOT NULL, expira INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS pareamentos (hash TEXT PRIMARY KEY, expira INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS aparelhos (id TEXT PRIMARY KEY, nome TEXT NOT NULL, token_hash TEXT NOT NULL UNIQUE,
  criado INTEGER NOT NULL, ultimo_contato INTEGER, versao TEXT, aplicado_seq INTEGER NOT NULL DEFAULT 0,
  aplicado_em INTEGER, revogado INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS estado (aparelho TEXT PRIMARY KEY, seq INTEGER NOT NULL, armado_ate INTEGER NOT NULL,
  travado INTEGER NOT NULL, desarmado_permite TEXT NOT NULL, motivo TEXT, alterado_por TEXT, alterado_em INTEGER);
CREATE TABLE IF NOT EXISTS eventos (id INTEGER PRIMARY KEY AUTOINCREMENT, quando INTEGER NOT NULL,
  origem TEXT NOT NULL, tipo TEXT NOT NULL, dados TEXT, hash TEXT NOT NULL, hash_anterior TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS tentativas (chave TEXT PRIMARY KEY, n INTEGER NOT NULL, janela INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS convites (hash TEXT PRIMARY KEY, expira INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS recebimentos (aparelho TEXT PRIMARY KEY, arquivo TEXT NOT NULL, ate INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS extras (aparelho TEXT PRIMARY KEY, so_pelo_painel INTEGER NOT NULL DEFAULT 0,
  mcp_url TEXT, mcp_url_em INTEGER);
CREATE TABLE IF NOT EXISTS chamadas (id INTEGER PRIMARY KEY AUTOINCREMENT, quando INTEGER NOT NULL,
  ferramenta TEXT NOT NULL, resumo TEXT, motivo TEXT, recursos TEXT, status TEXT, ms INTEGER);
CREATE TABLE IF NOT EXISTS observacao (aparelho TEXT PRIMARY KEY, observar_ate INTEGER NOT NULL DEFAULT 0,
  ao_vivo_ate INTEGER NOT NULL DEFAULT 0, em_uso TEXT, em_uso_em INTEGER);
CREATE TABLE IF NOT EXISTS quadros (aparelho TEXT PRIMARY KEY, jpeg TEXT NOT NULL, quando INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS ferramentas_pc (aparelho TEXT PRIMARY KEY, lista TEXT NOT NULL, quando INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS ferramentas_celular (aparelho TEXT PRIMARY KEY, ferramentas TEXT, inicio TEXT, em INTEGER);
CREATE TABLE IF NOT EXISTS efetivo (aparelho TEXT PRIMARY KEY, dados TEXT NOT NULL, quando INTEGER NOT NULL);
`;
let esquemaPronto = false;
async function inicializar(env) {
  if (esquemaPronto) return;
  await env.DB.batch(ESQUEMA.split(';').map(q => q.trim()).filter(Boolean).map(q => env.DB.prepare(q)));
  esquemaPronto = true;
}

// ---------------------------------------------------------------- utilidades
const json = (dados, status = 200, extra = {}) => new Response(JSON.stringify(dados), {
  status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store', ...extra },
});
const erro = (msg, status = 400) => json({ erro: msg }, status);
const aleatorio = (n = 32) => isoBase64URL.fromBuffer(crypto.getRandomValues(new Uint8Array(n)));
async function sha256(txt) {
  return isoBase64URL.fromBuffer(new Uint8Array(await crypto.subtle.digest('SHA-256', enc.encode(txt))));
}
function iguais(a, b) {  // comparação em tempo constante
  const x = enc.encode(String(a)), y = enc.encode(String(b));
  if (x.length !== y.length) return false;
  let d = 0;
  for (let i = 0; i < x.length; i++) d |= x[i] ^ y[i];
  return d === 0;
}
const cookie = (req, nome) => (req.headers.get('cookie') || '').split(/;\s*/)
  .map(c => c.split('=')).find(([k]) => k === nome)?.[1];

async function config(env, k, padrao = null) {
  const r = await env.DB.prepare('SELECT v FROM config WHERE k = ?').bind(k).first();
  return r ? r.v : padrao;
}
const definir = (env, k, v) => env.DB.prepare('INSERT INTO config (k, v) VALUES (?, ?) ON CONFLICT(k) DO UPDATE SET v = ?')
  .bind(k, v, v).run();

// auditoria do painel: encadeada por hash (cada linha cobre a anterior); só o Worker escreve
// Histórico encadeado: cada INSERT só vale se o topo da cadeia for o esperado, e o lote inteiro roda numa
// transação (batch). Se outra gravação entrou no meio, nada é gravado e o lote é refeito sobre o topo novo.
const ACRESCENTA = `INSERT INTO eventos (quando, origem, tipo, dados, hash, hash_anterior) SELECT ?, ?, ?, ?, ?, ?
  WHERE COALESCE((SELECT hash FROM eventos ORDER BY id DESC LIMIT 1), 'inicio') = ?`;
async function registrarVarios(env, itens, extras = []) {
  for (let tentativa = 0; tentativa < 4; tentativa++) {
    const ult = await env.DB.prepare('SELECT hash FROM eventos ORDER BY id DESC LIMIT 1').first();
    let anterior = ult ? ult.hash : 'inicio';
    const quando = agora(), stmts = [];
    for (const { origem, tipo, dados } of itens) {
      const corpo = JSON.stringify(dados ?? {}).slice(0, 2000);
      const hash = await sha256(`${anterior}|${quando}|${origem}|${tipo}|${corpo}`);
      stmts.push(env.DB.prepare(ACRESCENTA).bind(quando, origem, tipo, corpo, hash, anterior, anterior));
      anterior = hash;
    }
    if (!stmts.length) { if (extras.length) await env.DB.batch(extras); return; }
    const r = await env.DB.batch([...stmts, ...extras]);
    if (r[0].meta.changes) return;
  }
  throw new Error('histórico ocupado; tente de novo');
}
const registrar = (env, origem, tipo, dados = {}) => registrarVarios(env, [{ origem, tipo, dados }]);

async function limitar(env, req, rota, max = 10) {  // limite simples por IP e minuto
  const ip = req.headers.get('cf-connecting-ip') || 'local';
  const janela = Math.floor(agora() / 60), chave = `${rota}|${ip}`;
  const r = await env.DB.prepare('SELECT n, janela FROM tentativas WHERE chave = ?').bind(chave).first();
  const n = r && r.janela === janela ? r.n + 1 : 1;
  await env.DB.prepare('INSERT INTO tentativas (chave, n, janela) VALUES (?, ?, ?) ON CONFLICT(chave) DO UPDATE SET n = ?, janela = ?')
    .bind(chave, n, janela, n, janela).run();
  return n <= max;
}

// ---------------------------------------------------------------- chave de assinatura (Ed25519)
let chavesCache = null;  // a chave não muda: guardada na memória do Worker (poupa 2 consultas por chamada)
async function chaves(env) {
  if (chavesCache) return chavesCache;
  let priv = await config(env, 'chave_privada'), pub = await config(env, 'chave_publica');
  if (!priv) {
    const par = await crypto.subtle.generateKey({ name: 'Ed25519' }, true, ['sign', 'verify']);
    priv = isoBase64URL.fromBuffer(new Uint8Array(await crypto.subtle.exportKey('pkcs8', par.privateKey)));
    pub = isoBase64URL.fromBuffer(new Uint8Array(await crypto.subtle.exportKey('raw', par.publicKey)));
    await definir(env, 'chave_privada', priv);
    await definir(env, 'chave_publica', pub);
  }
  const chave = await crypto.subtle.importKey('pkcs8', isoBase64URL.toBuffer(priv), { name: 'Ed25519' }, false, ['sign']);
  chavesCache = { chave, pub };
  return chavesCache;
}
async function sha256hex(bytes) {
  return [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))].map(b => b.toString(16).padStart(2, '0')).join('');
}
async function assinarRequisicao(env, bytes) {  // o celular confere com a chave pública fixada no pareamento
  const { chave } = await chaves(env);
  const ts = agora(), nonce = aleatorio(12), msg = `${ts}.${nonce}.${await sha256hex(bytes)}`;
  return `${ts}.${nonce}.${isoBase64URL.fromBuffer(new Uint8Array(await crypto.subtle.sign({ name: 'Ed25519' }, chave, enc.encode(msg))))}`;
}
async function assinar(env, objeto) {
  const { chave } = await chaves(env);
  const texto = JSON.stringify(objeto);
  const sig = new Uint8Array(await crypto.subtle.sign({ name: 'Ed25519' }, chave, enc.encode(texto)));
  return { estado: texto, assinatura: isoBase64URL.fromBuffer(sig) };
}

// ---------------------------------------------------------------- sessão do dono
async function sessao(env, req) {
  const tok = cookie(req, 'painel');
  if (!tok) return null;
  const h = await sha256(tok), t = agora();
  const s = await env.DB.prepare('SELECT * FROM sessoes WHERE hash = ?').bind(h).first();
  if (!s || s.expira < t || s.ultimo + SESSAO_OCIOSA < t) return null;
  const cred = await env.DB.prepare('SELECT revogada FROM credenciais WHERE id = ?').bind(s.credencial).first();
  if (!cred || cred.revogada) return null;
  await env.DB.prepare('UPDATE sessoes SET ultimo = ? WHERE hash = ?').bind(t, h).run();
  return s;
}
async function novaSessao(env, credencial) {
  const tok = aleatorio(), t = agora();
  await env.DB.prepare('INSERT INTO sessoes (hash, credencial, criada, ultimo, passkey_em, expira) VALUES (?, ?, ?, ?, ?, ?)')
    .bind(await sha256(tok), credencial, t, t, t, t + SESSAO_MAX).run();
  return `painel=${tok}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=${SESSAO_MAX}`;
}
const fresca = s => s && agora() - s.passkey_em <= PASSKEY_FRESCA;

function rp(req) {
  const u = new URL(req.url);
  return { rpID: u.hostname, origem: u.origin };
}
async function guardarDesafio(env, desafio, tipo, sessaoHash = null) {
  const id = aleatorio(16);
  await env.DB.prepare('INSERT INTO desafios (id, desafio, tipo, sessao, expira) VALUES (?, ?, ?, ?, ?)')
    .bind(id, desafio, tipo, sessaoHash, agora() + DESAFIO).run();
  return id;
}
async function consumirDesafio(env, id, tipo) {  // uso único
  const d = await env.DB.prepare('SELECT * FROM desafios WHERE id = ? AND tipo = ?').bind(String(id || ''), tipo).first();
  if (!d) return null;
  await env.DB.prepare('DELETE FROM desafios WHERE id = ?').bind(d.id).run();
  return d.expira >= agora() ? d : null;
}

// ---------------------------------------------------------------- passkeys
async function registroOpcoes(env, req, corpo) {
  const total = (await env.DB.prepare('SELECT COUNT(*) AS n FROM credenciais WHERE revogada = 0').first()).n;
  const s = await sessao(env, req);
  let convite = null;
  if (total === 0) {  // primeira passkey: exige o código inicial definido pelo dono na Cloudflare
    if (!env.CODIGO_INICIAL || String(env.CODIGO_INICIAL).length < 12)
      return erro('defina o segredo CODIGO_INICIAL (12+ caracteres) no painel da Cloudflare', 503);
    if (!iguais(corpo.codigo_inicial || '', env.CODIGO_INICIAL)) {
      await registrar(env, 'painel', 'codigo_inicial_errado', {});
      return erro('código inicial incorreto', 403);
    }
  } else if (corpo.convite) {  // outro aparelho (ex.: iPad) com convite de uso único criado com a digital
    const h = await sha256(String(corpo.convite));
    const c = await env.DB.prepare('SELECT * FROM convites WHERE hash = ?').bind(h).first();
    if (!c || c.expira < agora()) {
      await registrar(env, 'painel', 'convite_recusado', {});
      return erro('convite inválido ou vencido', 403);
    }
    convite = h;  // só é gasto quando a passkey nova for aceita (uma tentativa que falha não queima o convite)
  } else if (!fresca(s)) {
    return erro('para cadastrar outro aparelho, entre com uma passkey já cadastrada (há menos de 2 min)', 403);
  }
  const { rpID } = rp(req);
  const existentes = await env.DB.prepare('SELECT id, transportes FROM credenciais WHERE revogada = 0').all();
  const opcoes = await generateRegistrationOptions({
    rpName: 'Central de Controle', rpID, userName: 'dono', userDisplayName: 'Dono',
    userID: enc.encode('dono'), attestationType: 'none',
    authenticatorSelection: { residentKey: 'required', userVerification: 'required' },
    excludeCredentials: existentes.results.map(c => ({ id: c.id, transports: c.transportes ? JSON.parse(c.transportes) : undefined })),
  });
  const id = await guardarDesafio(env, opcoes.challenge, convite ? 'registro_convite' : 'registro', convite || (s ? s.hash : null));
  return json({ desafio_id: id, opcoes });
}

async function registroVerificar(env, req, corpo) {
  const d = await consumirDesafio(env, corpo.desafio_id, 'registro') || await consumirDesafio(env, corpo.desafio_id, 'registro_convite');
  if (!d) return erro('desafio inválido ou vencido', 400);
  const { rpID, origem } = rp(req);
  let v;
  try {
    v = await verifyRegistrationResponse({ response: corpo.resposta, expectedChallenge: d.desafio,
      expectedOrigin: origem, expectedRPID: rpID, requireUserVerification: true });
  } catch (e) {
    return erro(`passkey recusada: ${e.message}`, 400);
  }
  if (!v.verified) return erro('passkey recusada', 400);
  if (d.tipo === 'registro_convite') {  // uso único, gasto agora (atômico)
    const g = await env.DB.prepare('DELETE FROM convites WHERE hash = ? AND expira >= ?').bind(d.sessao, agora()).run();
    if (!g.meta.changes) return erro('convite já usado ou vencido', 403);
  }
  const c = v.registrationInfo.credential;
  const nome = String(corpo.nome || 'aparelho').slice(0, 40);
  await env.DB.prepare('INSERT INTO credenciais (id, chave, contador, transportes, nome, criada) VALUES (?, ?, ?, ?, ?, ?)')
    .bind(c.id, isoBase64URL.fromBuffer(c.publicKey), c.counter, JSON.stringify(c.transports || []), nome, agora()).run();
  await registrar(env, 'painel', 'passkey_cadastrada', { nome, credencial: c.id.slice(0, 10) });
  return json({ ok: true }, 200, { 'set-cookie': await novaSessao(env, c.id) });
}

async function loginOpcoes(env, req) {
  const { rpID } = rp(req);
  const opcoes = await generateAuthenticationOptions({ rpID, userVerification: 'required', allowCredentials: [] });
  return json({ desafio_id: await guardarDesafio(env, opcoes.challenge, 'login'), opcoes });
}

async function loginVerificar(env, req, corpo) {
  const d = await consumirDesafio(env, corpo.desafio_id, 'login');
  if (!d) return erro('desafio inválido ou vencido', 400);
  const id = corpo.resposta?.id;
  const cred = await env.DB.prepare('SELECT * FROM credenciais WHERE id = ? AND revogada = 0').bind(String(id || '')).first();
  if (!cred) {
    await registrar(env, 'painel', 'login_recusado', { motivo: 'passkey desconhecida ou revogada' });
    return erro('passkey desconhecida ou revogada', 403);
  }
  const { rpID, origem } = rp(req);
  let v;
  try {
    v = await verifyAuthenticationResponse({ response: corpo.resposta, expectedChallenge: d.desafio,
      expectedOrigin: origem, expectedRPID: rpID, requireUserVerification: true,
      credential: { id: cred.id, publicKey: isoBase64URL.toBuffer(cred.chave), counter: cred.contador,
        transports: JSON.parse(cred.transportes || '[]') } });
  } catch (e) {
    await registrar(env, 'painel', 'login_recusado', { motivo: e.message.slice(0, 120) });
    return erro(`passkey recusada: ${e.message}`, 403);
  }
  if (!v.verified) return erro('passkey recusada', 403);
  await env.DB.prepare('UPDATE credenciais SET contador = ?, ultimo_uso = ? WHERE id = ?')
    .bind(v.authenticationInfo.newCounter, agora(), cred.id).run();
  const s = await sessao(env, req);
  if (s && s.credencial === cred.id) {  // confirmação com a digital dentro de uma sessão: renova a "frescura"
    await env.DB.prepare('UPDATE sessoes SET passkey_em = ? WHERE hash = ?').bind(agora(), s.hash).run();
    return json({ ok: true, confirmado: true });
  }
  await registrar(env, 'painel', 'login', { passkey: cred.nome });
  return json({ ok: true }, 200, { 'set-cookie': await novaSessao(env, cred.id) });
}

// ---------------------------------------------------------------- estado desejado de cada aparelho
async function estadoDe(env, aparelho) {
  const e = await env.DB.prepare('SELECT * FROM estado WHERE aparelho = ?').bind(aparelho).first()
    || { aparelho, seq: 0, armado_ate: 0, travado: 0, desarmado_permite: 'ir' };
  const x = await env.DB.prepare('SELECT so_pelo_painel, mcp_url, mcp_url_em FROM extras WHERE aparelho = ?').bind(aparelho).first();
  return { ...e, so_pelo_painel: x ? x.so_pelo_painel : 0, mcp_url_em: x ? x.mcp_url_em : null, tem_mcp: !!(x && x.mcp_url) };
}
async function mudarEstado(env, aparelho, mudanca, por, motivo) {
  const e = { ...(await estadoDe(env, aparelho)), ...mudanca };
  e.seq += 1;
  // a seq sobe no próprio banco (atômico): dois pedidos ao mesmo tempo (dois toques em armar) liam a mesma seq e
  // gravavam o mesmo número com conteúdos diferentes — o celular, que só aplica seq mais nova, ignorava o segundo
  const novo = await env.DB.prepare(`INSERT INTO estado (aparelho, seq, armado_ate, travado, desarmado_permite, motivo, alterado_por, alterado_em)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(aparelho) DO UPDATE SET seq = MAX(estado.seq + 1, excluded.seq), armado_ate = excluded.armado_ate,
    travado = excluded.travado, desarmado_permite = excluded.desarmado_permite, motivo = excluded.motivo,
    alterado_por = excluded.alterado_por, alterado_em = excluded.alterado_em RETURNING seq`)
    .bind(aparelho, e.seq, e.armado_ate, e.travado, e.desarmado_permite, motivo, por, agora()).first();
  if (novo && Number.isInteger(novo.seq)) e.seq = novo.seq;
  await registrar(env, 'painel', 'estado_alterado', { aparelho, seq: e.seq, armado_ate: e.armado_ate, travado: e.travado,
    desarmado_permite: e.desarmado_permite, motivo });
  return e;
}

// ---------------------------------------------------------------- canal direto com o celular (Durable Object)
// O celular abre um WebSocket para cá (com o token do aparelho) e o mantém aberto. As chamadas do Claude vão por ele
// (sem túnel) e a Central EMPURRA avisos ("sync": sincronize agora — armado, desarmado, painel aberto).
const canalDe = (env, aparelho) => env.CANAL.get(env.CANAL.idFromName(aparelho));
async function empurrar(env, aparelho, msg = { t: 'sync' }) {
  try { await canalDe(env, aparelho).fetch('https://canal/empurrar', { method: 'POST', body: JSON.stringify(msg) }); }
  catch { /* sem canal: o celular pega na próxima sincronização (até 30 s) */ }
}
async function estadoCanal(env, aparelho) {
  try { return await (await canalDe(env, aparelho).fetch('https://canal/estado')).json(); }
  catch { return { conectado: null }; }
}
async function abrirCanal(req, env) {
  if ((req.headers.get('upgrade') || '').toLowerCase() !== 'websocket') return erro('use WebSocket', 426);
  await inicializar(env);
  const ap = await aparelhoDoToken(env, req);
  if (!ap) return erro('aparelho não autorizado', 401);
  await env.DB.prepare('UPDATE aparelhos SET ultimo_contato = ? WHERE id = ?').bind(agora(), ap.id).run();
  return canalDe(env, ap.id).fetch(new Request('https://canal/conectar', req));
}

const CANAL_CAIU = 'CANAL_CAIU';  // a conexão caiu com a chamada pendente (vira 503: a Central espera e repete)
function idDoSocket(ws) { try { return ws.deserializeAttachment()?.id || null; } catch { return null; } }

export class Canal extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.pendentes = new Map();
    // as batidas do celular ("ping") são respondidas sem acordar o objeto: canal parado não custa nada
    this.ctx.setWebSocketAutoResponse(new WebSocketRequestResponsePair('ping', 'pong'));
  }
  socket() {  // o canal vivo: o celular bate ("ping") depois de 25 s parado; sem sinal de vida há 70 s, morreu calada
    // getWebSockets() ainda devolve a conexão que fechamos e cujo outro lado morreu sem responder (fica em CLOSING
    // até o runtime desistir), e a ordem da lista não é garantida: escolhe a conexão ABERTA com vida mais recente.
    // Antes pegava a última da lista, e uma conexão fantasma (o PC perdeu a internet no meio) escondia a nova.
    // Vida = batida, abertura OU qualquer mensagem do aparelho (ok/res): com chamadas seguidas o celular não bate, e
    // contar só a batida fazia a Central fechar como "mudo" um canal saudável no meio do tráfego.
    let ws = null, ultimo = 0;
    for (const s of this.ctx.getWebSockets()) {
      if (s.readyState === 2 || s.readyState === 3) continue;  // CLOSING/CLOSED (a fantasma); só pula o que está fechando
      const batida = this.ctx.getWebSocketAutoResponseTimestamp(s);
      const a = s.deserializeAttachment() || {};
      const t = Math.max(batida ? batida.getTime() : 0, a.desde || 0, a.ativo || 0);
      if (!ws || t > ultimo) { ws = s; ultimo = t; }
    }
    if (!ws) return null;
    if (Date.now() - ultimo > 70_000) { try { ws.close(4001, 'canal mudo'); } catch { } return null; }
    return ws;
  }
  async fetch(req) {
    const u = new URL(req.url);
    if (u.pathname === '/conectar') {
      for (const velho of this.ctx.getWebSockets()) {
        try { velho.close(4000, 'substituído por conexão nova'); } catch { }
        // o que ia pela conexão velha não volta mais por ela: falha já (a Central espera o canal novo e repete)
        const sock = idDoSocket(velho);
        if (sock) this.falharTudo(CANAL_CAIU, sock);
      }
      const [cliente, servidor] = Object.values(new WebSocketPair());
      this.ctx.acceptWebSocket(servidor);
      servidor.serializeAttachment({ desde: Date.now(), id: crypto.randomUUID() });
      return new Response(null, { status: 101, webSocket: cliente });
    }
    if (u.pathname === '/estado') {
      const ws = this.socket();
      return Response.json(ws ? { conectado: true, desde: ws.deserializeAttachment()?.desde || null } : { conectado: false });
    }
    if (u.pathname === '/empurrar') {
      const ws = this.socket();
      if (!ws) return new Response('sem canal', { status: 503 });
      try { ws.send(await req.text()); } catch { return new Response('canal caiu', { status: 503 }); }
      return new Response('ok');
    }
    if (u.pathname === '/rpc') {
      const ws = this.socket();
      if (!ws) return new Response('sem canal', { status: 503 });
      const id = crypto.randomUUID(), h = {};
      for (const k of ['x-painel-assinatura', 'content-type', 'accept', 'mcp-session-id', 'mcp-protocol-version'])
        if (req.headers.get(k)) h[k] = req.headers.get(k);
      const corpo = await req.text();
      const resposta = new Promise((ok, falha) => {
        const t = setTimeout(() => { this.pendentes.delete(id); falha(new Error('o celular não respondeu em 170 s')); }, 170_000);
        // o celular confirma o recebimento na hora; sem confirmação em 5 s, a conexão morreu sem avisar:
        // fecha e devolve 503 (a chamada não chegou, então é seguro ir pelo túnel; o celular ainda ignora reenvios)
        const sem = setTimeout(() => {
          this.pendentes.delete(id); clearTimeout(t);
          try { ws.close(4002, 'sem confirmação'); } catch { }
          falha(new Error('SEM_CONFIRMACAO'));
        }, 5000);
        this.pendentes.set(id, { ok, falha, t, sem, sock: idDoSocket(ws) });
      });
      try { ws.send(JSON.stringify({ t: 'req', id, h, b: corpo })); } catch {
        clearTimeout(this.pendentes.get(id)?.t); this.pendentes.delete(id);
        return new Response('canal caiu', { status: 503 });
      }
      try {
        const r = await resposta;
        return new Response(r.b ?? '', { status: r.s || 200, headers: { 'content-type': r.h?.['content-type'] || 'application/json' } });
      } catch (e) {
        if (e.message === 'SEM_CONFIRMACAO') return new Response('canal mudo', { status: 503 });
        // perdeu a conexão no meio: 503 também, para a Central esperar o canal e repetir o MESMO pedido (mesma
        // assinatura: se a primeira já tiver chegado, o aparelho recusa a repetição e nada roda duas vezes)
        if (e.message === CANAL_CAIU) return new Response('canal caiu no meio da chamada', { status: 503 });
        return Response.json({ jsonrpc: '2.0', id: null, error: { code: -32000, message: String(e.message || e) } }, { status: 504 });
      }
    }
    return new Response('rota desconhecida', { status: 404 });
  }
  async webSocketMessage(ws, msg) {
    try {  // qualquer mensagem do aparelho é sinal de vida (no máximo uma gravação por segundo)
      const a = ws.deserializeAttachment() || {}, t = Date.now();
      if (t - (a.ativo || 0) >= 1000) ws.serializeAttachment({ ...a, ativo: t });
    } catch { /* sem anexo: vale a batida */ }
    if (typeof msg !== 'string' || msg === 'ping' || msg === 'pong') return;
    let m;
    try { m = JSON.parse(msg); } catch { return; }
    const p = m && (m.t === 'res' || m.t === 'ok') ? this.pendentes.get(m.id) : null;
    if (!p) return;
    clearTimeout(p.sem);  // recebida pelo celular
    if (m.t === 'ok') return;
    clearTimeout(p.t);
    this.pendentes.delete(m.id);
    p.ok(m);
  }
  falharTudo(motivo, sock = null) {  // sock: só as chamadas que iam por aquela conexão
    for (const [id, p] of this.pendentes) {
      if (sock && p.sock !== sock) continue;
      clearTimeout(p.t); clearTimeout(p.sem); p.falha(new Error(motivo)); this.pendentes.delete(id);
    }
  }
  async webSocketClose(ws, code, reason) {
    try { ws.close(code, reason); } catch { }
    const sock = idDoSocket(ws);
    if (sock) this.falharTudo(CANAL_CAIU, sock);
    if (!this.socket()) this.falharTudo(CANAL_CAIU);
  }
  async webSocketError(ws) {
    const sock = idDoSocket(ws);
    if (sock) this.falharTudo(CANAL_CAIU, sock);
    if (!this.socket()) this.falharTudo(CANAL_CAIU);
  }
}

async function acaoDono(env, req, s, corpo, acao) {
  const aparelhos = (await env.DB.prepare('SELECT id FROM aparelhos WHERE revogado = 0').all()).results.map(a => a.id);
  const alvo = corpo.aparelho ? [String(corpo.aparelho)] : aparelhos;
  if (!alvo.length) return erro('nenhum celular cadastrado', 400);
  const por = (await env.DB.prepare('SELECT nome FROM credenciais WHERE id = ?').bind(s.credencial).first())?.nome || '?';
  const feitos = [];
  for (const ap of alvo) {
    if (!aparelhos.includes(ap)) return erro('aparelho desconhecido ou revogado', 404);
    if (acao === 'armar') {  // aumentar poder: exige a digital agora
      if (!fresca(s)) return erro('confirme com a digital antes de armar', 403);
      const t = agora();
      let ate = Number(corpo.ate) || 0;
      if (!ate) ate = t + Math.min(Math.max(Number(corpo.horas) || 1, 0.1), HORAS_MAX) * 3600;
      ate = Math.min(ate, t + HORAS_MAX * 3600);
      if (ate <= t) return erro('prazo inválido', 400);
      feitos.push(await mudarEstado(env, ap, { armado_ate: Math.floor(ate), travado: 0 }, por, 'armado pelo painel'));
    } else if (acao === 'desarmar') {  // reduzir poder: basta a sessão
      feitos.push(await mudarEstado(env, ap, { armado_ate: 0 }, por, 'desarmado pelo painel'));
    } else if (acao === 'emergencia') {
      feitos.push(await mudarEstado(env, ap, { armado_ate: 0, travado: 1 }, por, 'EMERGÊNCIA'));
    } else if (acao === 'so_pelo_painel') {  // ligar reduz poder (basta a sessão); desligar amplia (digital)
      const v = corpo.valor ? 1 : 0;
      if (!v && !fresca(s)) return erro('confirme com a digital para voltar a aceitar o conector direto', 403);
      await env.DB.prepare('INSERT INTO extras (aparelho, so_pelo_painel) VALUES (?, ?) ON CONFLICT(aparelho) DO UPDATE SET so_pelo_painel = ?')
        .bind(ap, v, v).run();
      feitos.push(await mudarEstado(env, ap, {}, por, v ? 'Claude só pelo painel' : 'Claude também direto'));
    } else if (acao === 'desarmado_permite') {
      const v = corpo.valor === 'nada' ? 'nada' : 'ir';
      if (v === 'ir' && !fresca(s)) return erro('confirme com a digital para liberar o infravermelho desarmado', 403);
      feitos.push(await mudarEstado(env, ap, { desarmado_permite: v }, por, `desarmado permite ${v}`));
    }
  }
  await Promise.all(alvo.map(ap => empurrar(env, ap)));  // o celular aplica NA HORA (antes: até 30 s)
  return json({ ok: true, estados: feitos });
}

// ---------------------------------------------------------------- celulares
async function aparelhoDoToken(env, req) {
  const m = /^Bearer (.+)$/.exec(req.headers.get('authorization') || '');
  if (!m) return null;
  return await env.DB.prepare('SELECT * FROM aparelhos WHERE token_hash = ? AND revogado = 0').bind(await sha256(m[1])).first();
}

async function parearCelular(env, req, corpo) {
  if (!await limitar(env, req, 'parear', 5)) return erro('muitas tentativas; espere um minuto', 429);
  const h = await sha256(String(corpo.codigo || '').toUpperCase().replace(/[^A-Z0-9]/g, ''));
  const p = await env.DB.prepare('SELECT * FROM pareamentos WHERE hash = ?').bind(h).first();
  if (!p || p.expira < agora()) {
    await registrar(env, 'painel', 'pareamento_recusado', {});
    return erro('código de pareamento inválido ou vencido', 403);
  }
  await env.DB.prepare('DELETE FROM pareamentos WHERE hash = ?').bind(h).run();
  const id = aleatorio(9), token = aleatorio(32), nome = String(corpo.nome || 'celular').slice(0, 40);
  await env.DB.prepare('INSERT INTO aparelhos (id, nome, token_hash, criado, versao) VALUES (?, ?, ?, ?, ?)')
    .bind(id, nome, await sha256(token), agora(), String(corpo.versao || '').slice(0, 20)).run();
  await mudarEstado(env, id, {}, 'pareamento', 'celular cadastrado (desarmado)');
  await registrar(env, 'painel', 'celular_cadastrado', { aparelho: id, nome });
  return json({ aparelho: id, token, chave_publica: (await chaves(env)).pub });
}

async function quadroDoCelular(env, req, corpo) {  // tela ao vivo: só aceito enquanto o dono estiver assistindo
  const ap = await aparelhoDoToken(env, req);
  if (!ap) return erro('aparelho não autorizado', 401);
  const o = await env.DB.prepare('SELECT ao_vivo_ate FROM observacao WHERE aparelho = ?').bind(ap.id).first();
  if (!o || o.ao_vivo_ate < agora()) {
    await env.DB.prepare('DELETE FROM quadros WHERE aparelho = ?').bind(ap.id).run();
    return erro('ninguém assistindo', 409);
  }
  const jpeg = typeof corpo.jpeg === 'string' ? corpo.jpeg : '';
  if (!jpeg || jpeg.length > 400_000 || !/^[A-Za-z0-9+/=]+$/.test(jpeg)) return erro('quadro inválido', 400);
  await env.DB.prepare(`INSERT INTO quadros (aparelho, jpeg, quando) VALUES (?, ?, ?) ON CONFLICT(aparelho)
    DO UPDATE SET jpeg = excluded.jpeg, quando = excluded.quando`).bind(ap.id, jpeg, agora()).run();
  return json({ ok: true });
}

async function estadoParaCelular(env, req) {
  const ap = await aparelhoDoToken(env, req);
  if (!ap) return erro('aparelho não autorizado', 401);
  await env.DB.prepare('UPDATE aparelhos SET ultimo_contato = ? WHERE id = ?').bind(agora(), ap.id).run();
  const e = await estadoDe(env, ap.id);
  const o = await env.DB.prepare('SELECT observar_ate, ao_vivo_ate FROM observacao WHERE aparelho = ?').bind(ap.id).first();
  return json({ ...(await assinar(env, { v: 1, aparelho: ap.id, seq: e.seq, armado_ate: e.armado_ate, travado: e.travado,
    desarmado_permite: e.desarmado_permite, so_pelo_painel: e.so_pelo_painel, emitido_em: agora() })),
    observar_ate: o ? o.observar_ate : 0, ao_vivo_ate: o ? o.ao_vivo_ate : 0, canal: true });  // esta Central tem canal direto
}

const CHAVES_EFETIVO = ['armado', 'travado', 'trava_local', 'vetado'];
async function ackCelular(env, req, corpo) {
  const ap = await aparelhoDoToken(env, req);
  if (!ap) return erro('aparelho não autorizado', 401);
  const seq = Number(corpo.seq) || 0;
  await env.DB.prepare('UPDATE aparelhos SET aplicado_seq = MAX(aplicado_seq, ?), aplicado_em = ?, versao = ? WHERE id = ?')
    .bind(seq, agora(), String(corpo.versao || ap.versao || '').slice(0, 20), ap.id).run();
  // estado REAL do aparelho (pode estar travado ou vetado localmente): só as quatro chaves, todas booleanas; o resto é
  // ignorado. Sem efetivo válido (cliente antigo), apaga o anterior para o painel não mostrar um retrato velho.
  const ef = corpo.efetivo;
  if (ef && typeof ef === 'object' && !Array.isArray(ef) && CHAVES_EFETIVO.every(k => typeof ef[k] === 'boolean'))
    await env.DB.prepare(`INSERT INTO efetivo (aparelho, dados, quando) VALUES (?, ?, ?) ON CONFLICT(aparelho)
      DO UPDATE SET dados = excluded.dados, quando = excluded.quando`)
      .bind(ap.id, JSON.stringify({ ...Object.fromEntries(CHAVES_EFETIVO.map(k => [k, ef[k]])), seq }), agora()).run();
  else await env.DB.prepare('DELETE FROM efetivo WHERE aparelho = ?').bind(ap.id).run();
  if (corpo.em_uso && typeof corpo.em_uso === 'object') {  // o que está em uso no celular agora
    const txt = JSON.stringify(corpo.em_uso).slice(0, 6000);
    await env.DB.prepare(`INSERT INTO observacao (aparelho, em_uso, em_uso_em) VALUES (?, ?, ?) ON CONFLICT(aparelho)
      DO UPDATE SET em_uso = excluded.em_uso, em_uso_em = excluded.em_uso_em`).bind(ap.id, txt, agora()).run();
  }
  const url = typeof corpo.mcp_url === 'string' ? corpo.mcp_url.slice(0, 400) : '';
  if (/^https:\/\/[^\s/]+\/mcp\/\S+$/.test(url) || /^http:\/\/(127\.0\.0\.1|localhost)(:\d+)?\/mcp\/\S+$/.test(url))
    await env.DB.prepare(`INSERT INTO extras (aparelho, mcp_url, mcp_url_em) VALUES (?, ?, ?) ON CONFLICT(aparelho)
      DO UPDATE SET mcp_url = excluded.mcp_url, mcp_url_em = excluded.mcp_url_em`).bind(ap.id, url, agora()).run();
  // até 30 eventos por envio, gravados numa só transação; `_fim` (posição no arquivo do celular) evita repetidos
  // quando a resposta anterior se perdeu e o celular reenviou o mesmo trecho
  let eventos = Array.isArray(corpo.eventos) ? corpo.eventos.slice(0, 30) : [];
  const arquivo = String(corpo.arquivo || '');
  const rec = await env.DB.prepare('SELECT arquivo, ate FROM recebimentos WHERE aparelho = ?').bind(ap.id).first();
  let ate = rec && rec.arquivo === arquivo && !eventos.some(e => e && e.evento === 'auditoria_local_encolheu') ? rec.ate : 0;
  eventos = eventos.filter(e => e && typeof e === 'object' && !(Number(e._fim) > 0 && Number(e._fim) <= ate));
  for (const e of eventos) if (Number(e._fim) > ate) ate = Number(e._fim);
  const marca = env.DB.prepare('INSERT INTO recebimentos (aparelho, arquivo, ate) VALUES (?, ?, ?) ON CONFLICT(aparelho) DO UPDATE SET arquivo = ?, ate = ?')
    .bind(ap.id, arquivo, ate, arquivo, ate);
  await registrarVarios(env, eventos.map(ev => ({ origem: `celular:${ap.id}`, tipo: String(ev.evento || 'evento').slice(0, 40), dados: ev })), [marca]);
  return json({ ok: true, recebidos: eventos.length });
}

async function painel(env, s, origem) {
  const aps = (await env.DB.prepare('SELECT id, nome, criado, ultimo_contato, versao, aplicado_seq, aplicado_em, revogado FROM aparelhos ORDER BY criado').all()).results;
  const t = agora();
  for (const a of aps) {
    a.estado = await estadoDe(env, a.id);
    const o = await env.DB.prepare('SELECT * FROM observacao WHERE aparelho = ?').bind(a.id).first();
    a.em_uso = o && o.em_uso ? JSON.parse(o.em_uso) : null;
    a.em_uso_em = o ? o.em_uso_em : null;
    a.ao_vivo_ate = o ? o.ao_vivo_ate : 0;
    if (!a.revogado && (!o || o.observar_ate < t + 60)) {  // painel aberto: o celular manda o relatório completo
      await env.DB.prepare(`INSERT INTO observacao (aparelho, observar_ate) VALUES (?, ?) ON CONFLICT(aparelho)
        DO UPDATE SET observar_ate = excluded.observar_ate`).bind(a.id, t + 120).run();
      if (!o || o.observar_ate < t) await empurrar(env, a.id);  // acabou de abrir: relatório agora, não em 30 s
    }
    a.canal = a.revogado ? { conectado: false } : await estadoCanal(env, a.id);
    // "aplicado" só depois que o aparelho confirmar a seq E, se ele relatar o estado real, se esse estado concordar
    // com a Central (travado ou vetado no próprio celular não é "aplicado")
    const ef = await env.DB.prepare('SELECT dados, quando FROM efetivo WHERE aparelho = ?').bind(a.id).first();
    a.efetivo = ef ? { ...JSON.parse(ef.dados), em: ef.quando } : null;
    const armadaNaCentral = !a.estado.travado && a.estado.armado_ate > t;
    if (a.efetivo) {
      // o relato vale para a seq que o aparelho confirmou: com um estado mais novo ainda não buscado, é retrato velho
      // (o cartão diz "pendente", não "veto local"); e o armado do relato acaba junto com a janela assinada
      a.efetivo.atual = Number(a.efetivo.seq) >= a.estado.seq;
      if (a.efetivo.armado && a.efetivo.atual && a.estado.armado_ate <= t) a.efetivo.armado = false;
    }
    a.efetivo_concorda = !a.efetivo || !a.efetivo.atual
      || (a.efetivo.travado === !!a.estado.travado && a.efetivo.armado === armadaNaCentral);
    a.aplicado = a.aplicado_seq >= a.estado.seq && a.efetivo_concorda;
  }
  const creds = (await env.DB.prepare('SELECT id, nome, criada, ultimo_uso, revogada FROM credenciais ORDER BY criada').all()).results;
  const eventos = (await env.DB.prepare('SELECT id, quando, origem, tipo, dados FROM eventos ORDER BY id DESC LIMIT 150').all()).results;
  const acessos = env.OAUTH_PROVIDER ? (await env.OAUTH_PROVIDER.listUserGrants(DONO)).items.map(g => ({
    id: g.id, cliente: g.metadata?.cliente || g.clientId, destino: g.metadata?.destino || '', criado: g.createdAt,
  })) : [];
  return json({ agora: agora(), aparelhos: aps, passkeys: creds.map(c => ({ ...c, id: c.id.slice(0, 10), sua: c.id === s.credencial })),
    eventos, acessos, digital_recente: fresca(s),
    chamadas: (await env.DB.prepare('SELECT * FROM chamadas ORDER BY id DESC LIMIT 80').all()).results });
}

async function integridade(env) {  // confere a cadeia de hashes da auditoria
  const evs = (await env.DB.prepare('SELECT * FROM eventos ORDER BY id').all()).results;
  let anterior = 'inicio';
  for (const e of evs) {
    const h = await sha256(`${anterior}|${e.quando}|${e.origem}|${e.tipo}|${e.dados}`);
    if (e.hash_anterior !== anterior || e.hash !== h) return { ok: false, quebra_em: e.id };
    anterior = e.hash;
  }
  return { ok: true, eventos: evs.length };
}

// ---------------------------------------------------------------- roteador do painel (o que não é OAuth nem /mcp)
const painelApp = {
  async fetch(req, env) {
    const u = new URL(req.url), rota = u.pathname, metodo = req.method;
    if (rota === '/authorize') {
      await inicializar(env);
      return await autorizar(req, env, u);
    }
    // versão publicada (sem segredo nenhum): para conferir de fora se o deploy chegou
    if (rota === '/versao') return json({ central: VERSAO_CENTRAL, recursos: ['pc', 'pc-sem-celular', 'pc-ponte'] });
    if (!rota.startsWith('/api/')) return env.ASSETS.fetch(req);
    try {
      await inicializar(env);
      // rotas do celular (token de aparelho)
      if (rota === '/api/celular/parear' && metodo === 'POST') return await parearCelular(env, req, await req.json());
      if (rota === '/api/celular/estado' && metodo === 'GET') return await estadoParaCelular(env, req);
      if (rota === '/api/celular/ack' && metodo === 'POST') return await ackCelular(env, req, await req.json());
      if (rota === '/api/celular/quadro' && metodo === 'POST') return await quadroDoCelular(env, req, await req.json());
      // rotas do dono (navegador): só POST com cabeçalho próprio e mesma origem (anti-CSRF)
      if (metodo !== 'POST') return erro('método não permitido', 405);
      if (req.headers.get('x-painel') !== '1' || (req.headers.get('origin') && req.headers.get('origin') !== u.origin))
        return erro('origem não permitida', 403);
      if (!await limitar(env, req, rota.split('/')[2], 30)) return erro('muitas tentativas; espere um minuto', 429);
      const corpo = await req.json().catch(() => ({}));
      if (rota === '/api/registro/opcoes') return await registroOpcoes(env, req, corpo);
      if (rota === '/api/registro/verificar') return await registroVerificar(env, req, corpo);
      if (rota === '/api/login/opcoes') return await loginOpcoes(env, req);
      if (rota === '/api/login/verificar') return await loginVerificar(env, req, corpo);
      const s = await sessao(env, req);
      if (!s) return erro('entre com a passkey', 401);
      if (rota === '/api/painel') {
        const r = await painel(env, s);
        const d = await r.json();
        return json({ ...d, conector: `${u.origin}/mcp` });
      }
      if (rota === '/api/sair') {
        await env.DB.prepare('DELETE FROM sessoes WHERE hash = ?').bind(s.hash).run();
        return json({ ok: true }, 200, { 'set-cookie': 'painel=; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=0' });
      }
      if (['/api/armar', '/api/desarmar', '/api/emergencia', '/api/desarmado_permite', '/api/so_pelo_painel'].includes(rota))
        return await acaoDono(env, req, s, corpo, rota.slice(5));
      if (rota === '/api/convite') {
        if (!fresca(s)) return erro('confirme com a digital para convidar outro aparelho', 403);
        const convite = aleatorio(18);
        await env.DB.prepare('INSERT INTO convites (hash, expira) VALUES (?, ?)').bind(await sha256(convite), agora() + PAREAMENTO).run();
        await registrar(env, 'painel', 'convite_criado', {});
        return json({ convite, expira_em_min: PAREAMENTO / 60 });
      }
      if (rota === '/api/celular/codigo') {
        if (!fresca(s)) return erro('confirme com a digital para cadastrar um celular', 403);
        const codigo = aleatorio(8).toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 8).padEnd(8, 'X');
        await env.DB.prepare('INSERT INTO pareamentos (hash, expira) VALUES (?, ?)').bind(await sha256(codigo), agora() + PAREAMENTO).run();
        await registrar(env, 'painel', 'codigo_pareamento_criado', {});
        return json({ codigo, expira_em_min: PAREAMENTO / 60 });
      }
      if (rota === '/api/revogar') {
        if (!fresca(s)) return erro('confirme com a digital para revogar', 403);
        if (corpo.tipo === 'aparelho') {
          await env.DB.prepare('UPDATE aparelhos SET revogado = 1 WHERE id = ?').bind(String(corpo.id)).run();
          await empurrar(env, String(corpo.id));
        } else if (corpo.tipo === 'passkey') {
          const ativas = (await env.DB.prepare('SELECT COUNT(*) AS n FROM credenciais WHERE revogada = 0').first()).n;
          if (ativas <= 1) return erro('não dá para revogar a última passkey (você perderia o painel)', 400);
          const r = await env.DB.prepare("UPDATE credenciais SET revogada = 1 WHERE substr(id, 1, 10) = ?").bind(String(corpo.id)).run();
          if (!r.meta.changes) return erro('passkey não encontrada', 404);
        } else return erro('tipo deve ser aparelho ou passkey', 400);
        await registrar(env, 'painel', 'revogado', { tipo: corpo.tipo, id: String(corpo.id).slice(0, 12) });
        return json({ ok: true });
      }
      if (rota === '/api/integridade') return json(await integridade(env));
      if (rota === '/api/tela/ao_vivo') {  // ligar renova por 2 min (a página renova enquanto estiver aberta)
        const ap = (await env.DB.prepare(`SELECT id FROM aparelhos a WHERE revogado = 0 AND ${NAO_PC} ORDER BY criado LIMIT 1`).first())?.id;
        if (!ap) return erro('nenhum celular cadastrado', 400);
        const ate = corpo.ligar ? agora() + 120 : 0;
        await env.DB.prepare(`INSERT INTO observacao (aparelho, ao_vivo_ate, observar_ate) VALUES (?, ?, ?) ON CONFLICT(aparelho)
          DO UPDATE SET ao_vivo_ate = excluded.ao_vivo_ate, observar_ate = MAX(observar_ate, excluded.observar_ate)`)
          .bind(ap, ate, ate).run();
        if (!corpo.ligar) await env.DB.prepare('DELETE FROM quadros WHERE aparelho = ?').bind(ap).run();
        else if (corpo.inicio) { await registrar(env, 'painel', 'tela_ao_vivo', { aparelho: ap }); await empurrar(env, ap); }
        return json({ ok: true, ao_vivo_ate: ate });
      }
      if (rota === '/api/tela/quadro') {
        const q = await env.DB.prepare(`SELECT q.jpeg, q.quando FROM quadros q JOIN observacao o ON o.aparelho = q.aparelho
          WHERE o.ao_vivo_ate > ? ORDER BY q.quando DESC LIMIT 1`).bind(agora()).first();
        return json(q || { jpeg: null });
      }
      if (rota === '/api/acesso/revogar') {  // tira o acesso de um cliente OAuth (o Claude): vale na hora, na borda
        await env.OAUTH_PROVIDER.revokeGrant(String(corpo.id || ''), DONO);
        await registrar(env, 'painel', 'acesso_revogado', { id: String(corpo.id || '').slice(0, 16) });
        return json({ ok: true });
      }
      return erro('rota desconhecida', 404);
    } catch (e) {
      return erro(`falha interna: ${e.message}`, 500);
    }
  },
};

// ---------------------------------------------------------------- OAuth: o Claude entra pelo painel (Etapa 1b)
const DONO = 'dono';
const ESCOPO = 'controle';
function destinoPermitido(uri) {
  try {
    // O ChatGPT usa um retorno estável ou um caminho com o identificador do conector.
    if (typeof uri !== 'string') return false;
    if (/^https:\/\/chatgpt\.com\/(?:connector_platform_oauth_redirect|connector\/oauth\/[A-Za-z0-9_-]+)$/.test(uri.trim()) && uri === uri.trim()) return true;
    const x = new URL(uri);
    if (x.protocol === 'https:' && ['claude.ai', 'claude.com'].includes(x.hostname)) return true;
    return x.protocol === 'http:' && ['localhost', '127.0.0.1', '[::1]'].includes(x.hostname);
  } catch { return false; }
}
const escapar = v => String(v ?? '').replace(/[&<>"']/g, c => `&#${c.charCodeAt(0)};`);
const CSP_AUTORIZAR = "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'";

async function autorizar(req, env, u) {
  const oauth = env.OAUTH_PROVIDER;
  try {
    if (req.method === 'GET') {
      const pedido = await oauth.parseAuthRequest(req);
      const d = await oauth.describeConsent(pedido);
      const ok = destinoPermitido(d.redirectUri);
      const c = await oauth.beginConsent(pedido);
      c.headers.set('Content-Type', 'text/html; charset=utf-8');
      c.headers.set('Content-Security-Policy', CSP_AUTORIZAR);
      c.headers.set('Referrer-Policy', 'no-referrer');
      return new Response(paginaAutorizar(d, c.handle, ok), { headers: c.headers });
    }
    if (req.method !== 'POST') return erro('método não permitido', 405);
    if (req.headers.get('x-painel') !== '1' || req.headers.get('origin') !== u.origin) return erro('origem não permitida', 403);
    const corpo = await req.json().catch(() => ({}));
    const handle = String(corpo.handle || '');
    if (corpo.decisao !== 'autorizar') {
      const n = await oauth.denyConsent(req, handle);
      return json({ redirectTo: n.redirectTo }, 200, { 'set-cookie': n.headers.get('set-cookie') || '' });
    }
    const s = await sessao(env, req);
    if (!s) return erro('entre com a passkey', 401);
    if (!fresca(s)) return erro('confirme com a digital para autorizar', 403);
    const a = await oauth.approveConsent(req, handle, { scope: [ESCOPO] });
    if (!destinoPermitido(a.request.redirectUri)) {
      await registrar(env, 'painel', 'autorizacao_recusada', { destino: escapar(a.request.redirectUri).slice(0, 120) });
      return erro('destino não permitido: o acesso só pode ir para o Claude, o ChatGPT ou um app neste computador', 403);
    }
    const cli = await oauth.lookupClient(a.request.clientId).catch(() => null);
    const cliente = String(cli?.clientName || a.request.clientId).slice(0, 60);
    const destino = new URL(a.request.redirectUri).hostname;
    const por = (await env.DB.prepare('SELECT nome FROM credenciais WHERE id = ?').bind(s.credencial).first())?.nome || '?';
    const { redirectTo } = await oauth.completeAuthorization({
      request: a.request, userId: DONO, scope: a.request.scope,
      metadata: { cliente, destino, autorizado_por: por, em: agora() }, props: { passkey: s.credencial.slice(0, 10) },
    });
    await registrar(env, 'painel', 'conector_autorizado', { cliente, destino, por });
    return json({ redirectTo }, 200, { 'set-cookie': a.headers.get('set-cookie') || '' });
  } catch (e) {
    if (e instanceof AuthorizationError && e.redirectTo) return Response.redirect(e.redirectTo, 302);
    if (e instanceof AuthorizationError || e instanceof CimdFetchError) {
      const msg = e instanceof AuthorizationError ? (e.description || e.code) : 'não foi possível verificar este app';
      return new Response(`Pedido de autorização inválido: ${escapar(msg)}`, { status: 400, headers: { 'content-type': 'text/plain; charset=utf-8' } });
    }
    throw e;
  }
}

function paginaAutorizar(d, handle, ok) {
  const local = d.redirectIsLoopback
    ? '<p class="alerta">O acesso vai para um app <strong>neste computador</strong>. Continue só se você acabou de pedir isso nele (ex.: Claude Code).</p>' : '';
  const verificado = d.clientDomain ? `Publicado por <strong>${escapar(d.clientDomain)}</strong>.` : 'O nome do app foi informado por ele mesmo (não é verificado).';
  return `<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><title>Autorizar conector</title>
<style>:root{--fundo:#f6f7f9;--cartao:#fff;--texto:#15181d;--suave:#5d6571;--linha:#dfe3e8;--botao:#1f4fd8;--alerta:#b45309;--perigo:#c0262d}
@media (prefers-color-scheme: dark){:root{--fundo:#0f1115;--cartao:#181b21;--texto:#eceff3;--suave:#9aa3ae;--linha:#2a2f37;--botao:#4b74f0;--alerta:#f0a23b;--perigo:#ff5a5f}}
body{margin:0;background:var(--fundo);color:var(--texto);font:16px/1.45 system-ui,-apple-system,sans-serif}
main{max-width:560px;margin:0 auto;padding:16px}section{background:var(--cartao);border:1px solid var(--linha);border-radius:14px;padding:16px}
button{font:inherit;border:0;border-radius:10px;padding:14px;width:100%;margin:6px 0;background:var(--botao);color:#fff}
button.sec{background:transparent;color:var(--texto);border:1px solid var(--linha)}.alerta{color:var(--alerta)}.perigo{color:var(--perigo)}
.suave{color:var(--suave);font-size:.9rem}#msg{min-height:1.4em}</style></head><body><main>
<h1>Central de Controle</h1><section id="pedido" data-handle="${escapar(handle)}">
<h2>Autorizar <strong>${escapar(d.clientName)}</strong> a usar o Controle master?</h2>
<p>${verificado} O acesso vai para <strong>${escapar(d.redirectHost)}</strong>.</p>${local}
<p class="suave">O que ele poderá fazer continua limitado pelo painel: desarmado, só infravermelho e consulta; armado (com a sua digital), o resto. Você revoga este acesso no painel quando quiser.</p>
${ok ? '<button id="btAutorizar">Autorizar com a digital</button>' : '<p class="perigo"><strong>Destino não permitido.</strong> O acesso só pode ir para o Claude, o ChatGPT ou um app neste computador.</p>'}
<button id="btNegar" class="sec">Negar</button><p id="msg" class="suave" role="status"></p></section></main>
<script src="/webauthn.js"></script><script src="/autorizar.js"></script></body></html>`;
}

// ---------------------------------------------------------------- /mcp: repasse ao celular, com bloqueio na borda
// Mesmo critério do celular (controle_ir/seguranca.py): o que não passa aqui nem chega ao celular.
const SEMPRE = new Set(['consultar', 'politica', 'travar']);
const SEMPRE_PC = new Set(['pc_consultar', 'pc_travar']);  // igual a agente_pc/servidor.py
const BAIXO_RISCO = new Set([...SEMPRE, 'procurar_perfis', 'opcoes', 'controlar', 'registrar_estado', 'buscar', 'progresso',
  'pausar', 'retomar', 'retestar', 'confirmar', 'distinguir', 'salvar_aparelho', 'editar_aparelho', 'importar', 'exportar',
  'enviar_sinal']);
function bloqueioNaBorda(nome, e) {
  if (SEMPRE.has(nome)) return null;
  if (e.travado) return 'EMERGÊNCIA ativa na Central de Controle: só consultar, politica e travar respondem. Para voltar, arme pelo painel com a digital.';
  if (e.armado_ate > agora()) return null;
  if (e.desarmado_permite === 'ir' && BAIXO_RISCO.has(nome)) return null;
  return `o sistema está DESARMADO: “${nome}” precisa dele armado. Para usar, arme pela Central de Controle, com a digital.`;
}
const rpc = (id, result, status = 200) => json({ jsonrpc: '2.0', id: id ?? null, ...result }, status);

// ---------------------------------------------------------------- PC (agente_pc, docs/pc.md)
// O PC é um segundo aparelho da Central (versão "pc-…"), com estado de armado próprio. Fica no MESMO conector:
// tools/list une as ferramentas pc_* às do celular e cada tools/call pc_* vai pelo canal do PC, assinada.
const NAO_PC = "COALESCE(a.versao, '') NOT LIKE 'pc-%'";
const ehPC = nome => String(nome || '').startsWith('pc_');
const pcAtivo = env => env.DB.prepare(`SELECT a.id, e.armado_ate, e.travado FROM aparelhos a
  LEFT JOIN estado e ON e.aparelho = a.id WHERE a.revogado = 0 AND a.versao LIKE 'pc-%' ORDER BY a.criado DESC LIMIT 1`)
  .first().catch(() => null);
const resultadoTexto = (id, dados) => rpc(id, { result: { content: [{ type: 'text', text: JSON.stringify(dados) }],
  structuredContent: dados, isError: true } });
async function repassarPC(env, pc, bytes, assinatura) {  // 503 = o PC não está no canal agora
  try {
    return await canalDe(env, pc.id).fetch('https://canal/rpc', { method: 'POST', body: bytes,
      headers: { 'content-type': 'application/json', accept: 'application/json', 'x-painel-assinatura': assinatura || await assinarRequisicao(env, bytes) } });
  } catch { return new Response('sem canal', { status: 503 }); }
}
// O Wi-Fi do PC cai por segundos (26/11: 11 quedas em 24 h). Com 503, espera o canal voltar (até 10 s) e repete UMA vez
// a MESMA requisição com a MESMA assinatura: se a primeira tiver chegado (só a confirmação se perdeu), o PC recusa a
// repetição pela proteção contra reenvio — nunca executa duas vezes.
async function repassarPCComRetomada(env, pc, bytes) {
  const assinatura = await assinarRequisicao(env, bytes);
  const r = await repassarPC(env, pc, bytes, assinatura);
  if (r.status !== 503) return r;
  const fim = Date.now() + 10_000;
  while (Date.now() < fim) {
    await new Promise(z => setTimeout(z, 1000));
    if ((await estadoCanal(env, pc.id))?.conectado) return repassarPC(env, pc, bytes, assinatura);
  }
  return r;
}
async function ferramentasPC(env, pc) {
  // ao vivo; fora do ar, a última lista conhecida (a lista do conector é fixa por conversa: assim as ferramentas
  // do PC aparecem mesmo se ele estiver desligado na hora, e a chamada explica que ele está fora do ar)
  const r = await repassarPC(env, pc, enc.encode(JSON.stringify({ jsonrpc: '2.0', id: 'central', method: 'tools/list' })));
  if (r.ok) {
    try {
      const lista = ((await r.json())?.result?.tools || []).filter(t => ehPC(t?.name));
      if (lista.length) {
        await env.DB.prepare(`INSERT INTO ferramentas_pc (aparelho, lista, quando) VALUES (?, ?, ?) ON CONFLICT(aparelho)
          DO UPDATE SET lista = excluded.lista, quando = excluded.quando`).bind(pc.id, JSON.stringify(lista), agora()).run()
          .catch(() => {});
        return lista;
      }
    } catch { /* resposta estranha: usa a guardada */ }
  }
  try {
    const c = await env.DB.prepare('SELECT lista FROM ferramentas_pc WHERE aparelho = ?').bind(pc.id).first();
    return c ? JSON.parse(c.lista) : [];
  } catch { return []; }
}
async function chamarPC(env, ctx, pc, m, bytes, t0) {
  const nome = String(m.params?.name || ''), args = m.params?.arguments;
  const anotar = status => ctx.waitUntil(registrarChamada(env, nome, args, status, Date.now() - t0).catch(() => {}));
  if (!pc) {
    anotar('sem PC');
    return resultadoTexto(m.id, { erro: 'nenhum PC cadastrado na Central (instale o agente do PC: docs/pc.md)' });
  }
  const motivo = SEMPRE_PC.has(nome) ? null
    : bloqueioNaBorda(nome, { armado_ate: pc.armado_ate || 0, travado: pc.travado || 0, desarmado_permite: 'nada' });
  if (motivo) {
    await registrar(env, 'painel', 'bloqueado_na_borda', { ferramenta: nome.slice(0, 60), aparelho: 'PC' });
    anotar('bloqueado');
    return resultadoTexto(m.id, { erro: motivo.replace('o sistema está DESARMADO', 'o PC está DESARMADO'), bloqueado: true, onde: 'painel' });
  }
  const r = await repassarPCComRetomada(env, pc, bytes);
  if (r.status === 503) {
    anotar('PC fora do ar');
    return resultadoTexto(m.id, { erro: 'o PC está fora do ar: o agente não está conectado à Central (PC desligado, sem internet ou serviço parado)' });
  }
  anotar(`${r.ok ? 'ok' : `HTTP ${r.status}`} · PC`);
  if (r.status === 401) return resultadoTexto(m.id, { erro: recusouAssinatura('PC') });  // ex.: repetição após queda no meio
  return new Response(r.body, { status: r.status, headers: { 'content-type': r.headers.get('content-type') || 'application/json',
    'cache-control': 'no-store', 'x-via': 'pc' } });
}
function lerRpc(texto, tipo) {  // resposta JSON-RPC em JSON ou em SSE (a última linha "data:")
  if (!String(tipo || '').includes('event-stream')) return JSON.parse(texto);
  const dados = texto.split('\n').filter(l => l.startsWith('data:')).map(l => l.slice(5).trim()).filter(Boolean);
  return JSON.parse(dados[dados.length - 1]);
}
const inicioSemCelular = m => ({ protocolVersion: m.params?.protocolVersion || '2025-06-18', capabilities: { tools: {} },
  serverInfo: { name: 'controle-ir', title: 'Central de Controle', version: 'central' },
  instructions: 'O celular está fora do ar agora. O PC Windows do dono responde pelas ferramentas pc_* (desarmado: só pc_consultar e pc_travar). Responda em português.' });

// ---------------------------------------------------------------- celular: lista guardada (C4) e espera (C5)
// A lista de ferramentas é fixa por conversa: uma conversa aberta numa queda curta do celular (Central republicada,
// Wi-Fi piscando) ficava para sempre sem as ferramentas dele (26/11, duas vezes). A Central guarda a última lista
// boa e o último initialize do celular e, quando ele não responde, espera por ele e depois usa o que guardou.
const ESPERA_CELULAR = 10_000;
const AVISO_RECONECTANDO = 'Aviso da Central: o celular pode estar reconectando agora; as chamadas a ele esperam e tentam de novo sozinhas.';
async function comEsquema(env, fn) {  // tabela nova numa Central já em uso: cria o esquema e tenta de novo
  try { return await fn(); } catch (e) {
    if (!/no such table/i.test(String(e?.message || e))) throw e;
    esquemaPronto = false;
    await inicializar(env);
    return await fn();
  }
}
const guardarCelular = (env, aparelho, campo, valor) => comEsquema(env, () => env.DB.prepare(  // campo: ferramentas | inicio
  `INSERT INTO ferramentas_celular (aparelho, ${campo}, em) VALUES (?, ?, ?) ON CONFLICT(aparelho)
   DO UPDATE SET ${campo} = excluded.${campo}, em = excluded.em`).bind(aparelho, JSON.stringify(valor), agora()).run());
async function guardadoCelular(env, aparelho) {
  try {
    const g = await comEsquema(env, () => env.DB.prepare('SELECT ferramentas, inicio, em FROM ferramentas_celular WHERE aparelho = ?')
      .bind(aparelho).first());
    return g ? { ferramentas: g.ferramentas ? JSON.parse(g.ferramentas) : null, inicio: g.inicio ? JSON.parse(g.inicio) : null } : null;
  } catch { return null; }
}
function inicioGuardado(m, g, pc) {  // o initialize do celular, guardado, com uma linha curta no fim das instruções
  if (g.inicio) return { ...g.inicio, instructions: [g.inicio.instructions, AVISO_RECONECTANDO].filter(Boolean).join('\n') };
  return { ...inicioSemCelular(m), serverInfo: { name: 'controle-ir', title: 'Central de Controle', version: 'central' },
    instructions: [AVISO_RECONECTANDO, pc ? 'O PC Windows do dono responde pelas ferramentas pc_* (desarmado: só pc_consultar e pc_travar).' : '',
      'Responda em português.'].filter(Boolean).join(' ') };
}
const haQuanto = t => { const s = Math.max(0, agora() - t); return s < 90 ? `${s} s` : s < 5400 ? `${Math.round(s / 60)} min` : `${Math.round(s / 3600)} h`; };
const foraDoAr = ap => `o celular está fora do ar${ap.ultimo_contato ? ` (último contato com a Central há ${haQuanto(ap.ultimo_contato)})` : ''}:`
  + ` a Central esperou ${ESPERA_CELULAR / 1000} s pelo canal e tentou de novo. A lista de ferramentas continua valendo e as próximas`
  + ' chamadas tentam de novo sozinhas. Se persistir, abra o Termux no celular ou rode `controle-ir reiniciar`.';
// HTTP 401 do aparelho numa chamada = assinatura recusada (quase sempre a repetição de uma chamada que já tinha chegado
// antes de a conexão cair). Vai como resultado de erro: um 401 no /mcp faria o cliente achar que o login venceu.
const recusouAssinatura = onde => `o ${onde} recusou a assinatura da Central: provavelmente é a repetição de uma chamada que já tinha`
  + ' chegado antes de a conexão cair (ele não executa duas vezes). Ela pode ter sido executada: confira antes de repetir.';
const TUNEL_MORTO = new Set([404, 502, 503, 504]);  // ngrok sem o celular do outro lado (ERR_NGROK_3200 é 404) e afins
const ESPERAM = new Set(['tools/call', 'tools/list', 'initialize']);
async function pelaCanal(env, ap, cab, bruto) {  // null = sem canal agora (sem conexão, mudo ou caiu no meio)
  try {
    const r = await canalDe(env, ap.id).fetch('https://canal/rpc', { method: 'POST', headers: cab, body: bruto });
    return r.status === 503 ? null : r;
  } catch { return null; }
}
// 1º o canal direto; sem canal, o túnel (ngrok). Se nenhum servir, espera até 10 s o canal do celular voltar e repete
// UMA vez o MESMO pedido (mesmo id JSON-RPC e mesma assinatura, como o C3 do PC): se o primeiro tiver chegado, o
// celular recusa a repetição pela proteção contra reenvio — nunca executa duas vezes.
async function repassarCelular(env, ap, cab, bruto, metodo) {
  const r = await pelaCanal(env, ap, cab, bruto);
  if (r) return { r, via: 'canal' };
  let motivo = 'sem canal direto e sem túnel';
  if (ap.mcp_url) {
    try {
      const rt = await fetch(ap.mcp_url, { method: 'POST', headers: cab, body: bruto });
      const morto = metodo === 'tools/call' ? TUNEL_MORTO.has(rt.status) : ESPERAM.has(metodo) && !rt.ok;
      if (!morto) return { r: rt, via: 'túnel' };
      motivo = `o celular respondeu HTTP ${rt.status} pelo túnel`;
    } catch (err) { motivo = `o celular não respondeu pelo túnel: ${String(err.message || err).slice(0, 120)}`; }
  }
  if (!ESPERAM.has(metodo)) return { r: null, motivo };
  const fim = Date.now() + ESPERA_CELULAR;
  while (Date.now() < fim) {
    await new Promise(z => setTimeout(z, 1000));
    if ((await estadoCanal(env, ap.id))?.conectado) {
      const r2 = await pelaCanal(env, ap, cab, bruto);
      return r2 ? { r: r2, via: 'canal' } : { r: null, motivo };
    }
  }
  return { r: null, motivo };
}

// Atividade: cada chamada de ferramenta fica registrada (o que, por quê, quais recursos, resultado, tempo)
const RECURSOS_CAP = { foto: ['câmera'], tela: ['tela'], ouvir_bipe: ['microfone'], sono: ['microfone'],
  sonar: ['microfone', 'alto-falante'], termometro: ['sensores'], estado_celular: ['sensores'],
  descobrir_rede: ['rede'], diagnostico_rede: ['rede'] };
const PALAVRAS = { 'câmera': ['termux-camera', 'camera-photo'], microfone: ['termux-microphone', 'microphone-record', 'arecord'],
  'localização': ['termux-location'], tela: ['screencap', 'screenrecord', 'uiautomator', 'input tap', 'input text'],
  sms: ['termux-sms'], contatos: ['termux-contact'], rede: ['curl ', 'wget ', 'ping ', 'nmap'], pacotes: ['pkg ', 'pip ', 'apt '] };
function descrever(nome, args = {}) {
  const r = new Set();
  const cap = nome.startsWith('cap_') ? nome.slice(4) : nome === 'executar_capacidade' ? String(args.nome || '') : '';
  (RECURSOS_CAP[cap] || []).forEach(x => r.add(x));
  let resumo = '';
  if (nome.startsWith('pc_')) r.add('PC');
  if (nome === 'executar_comando' || nome === 'pc_executar') {
    r.add('terminal');
    const c = String(args.comando || '');
    for (const [k, ps] of Object.entries(PALAVRAS)) if (ps.some(p => c.toLowerCase().includes(p))) r.add(k);
    resumo = c;
  } else if (cap) {
    const a = nome === 'executar_capacidade' ? (args.argumentos || {}) : args;
    resumo = `${cap}${a.acao ? ' · ' + a.acao : ''}`;
  } else if (['controlar', 'enviar_sinal', 'buscar', 'retestar', 'confirmar'].includes(nome)) {
    r.add('infravermelho');
    if (args.ouvir) r.add('microfone');
    resumo = [args.aparelho, args.definir && JSON.stringify(args.definir), args.teclas && args.teclas.join(','), args.macro]
      .filter(Boolean).join(' · ');
  } else if (nome === 'atualizar_sistema' || nome === 'pc_atualizar') { r.add('sistema'); resumo = String(args.ref || '').slice(0, 12); }
  else if (nome === 'pc_tela' || nome === 'pc_entrada') { r.add('tela'); resumo = String(args.acao || 'captura'); }
  else if (['pc_escrever_arquivo', 'pc_editar_arquivo', 'pc_ler_arquivo', 'pc_listar'].includes(nome)) {
    r.add('arquivos'); resumo = String(args.caminho || '');
  }
  else resumo = JSON.stringify(args);
  return { resumo: resumo.slice(0, 200), motivo: String(args.motivo || '').slice(0, 200), recursos: [...r].join(',') };
}
async function registrarChamada(env, nome, args, status, ms) {
  const d = descrever(nome, args || {});
  await env.DB.prepare('INSERT INTO chamadas (quando, ferramenta, resumo, motivo, recursos, status, ms) VALUES (?, ?, ?, ?, ?, ?, ?)')
    .bind(agora(), nome.slice(0, 60), d.resumo, d.motivo, d.recursos, status, ms).run();
  if (Math.random() < 0.02) await env.DB.prepare('DELETE FROM chamadas WHERE quando < ?').bind(agora() - 30 * 86400).run();
}

const mcpApi = {
  async fetch(req, env, ctx) {
    const t0 = Date.now();
    if (req.method !== 'POST') return new Response(null, { status: 405, headers: { Allow: 'POST' } });
    const bruto = new Uint8Array(await req.arrayBuffer());
    if (bruto.length > 1_000_000) return rpc(null, { error: { code: -32600, message: 'corpo grande demais' } }, 413);
    let msg;
    try { msg = JSON.parse(new TextDecoder().decode(bruto)); } catch {
      return rpc(null, { error: { code: -32700, message: 'JSON inválido' } }, 400);
    }
    // Estas mensagens encerram aqui após a autenticação OAuth do recurso.
    if (msg?.jsonrpc === '2.0' && msg.method === 'ping' && msg.id != null)
      return rpc(msg.id, { result: {} });
    if (msg?.jsonrpc === '2.0' && msg.method === 'notifications/initialized' && msg.id == null)
      return new Response(null, { status: 202 });

    // O pareamento já criou o esquema. Evita repetir DDL na primeira chamada de cada isolate.
    const consultar = () => env.DB.prepare(`SELECT a.id, a.ultimo_contato, x.mcp_url, e.armado_ate, e.travado, e.desarmado_permite
      FROM aparelhos a LEFT JOIN extras x ON x.aparelho = a.id LEFT JOIN estado e ON e.aparelho = a.id
      WHERE a.revogado = 0 AND ${NAO_PC} ORDER BY a.criado LIMIT 1`).first();
    let ap;
    try { ap = await consultar(); } catch (e) {
      if (!/no such table/i.test(String(e.message || e))) throw e;
      await inicializar(env);
      ap = await consultar();
    }
    const unico = Array.isArray(msg) ? null : msg, metodo = unico?.method;
    const pc = await pcAtivo(env);
    if (metodo === 'tools/call' && ehPC(unico.params?.name)) return await chamarPC(env, ctx, pc, unico, bruto, t0);
    // Ponte para conversas abertas antes do PC existir (a lista de ferramentas é fixa por conversa):
    // executar_capacidade(nome="pc_…", argumentos={…}) vira a chamada pc_… e segue as mesmas regras (estado do PC,
    // assinatura, atividade)
    const capa = metodo === 'tools/call' && unico.params?.name === 'executar_capacidade' ? unico.params?.arguments : null;
    if (capa && ehPC(capa.nome)) {
      const m = { ...unico, params: { name: String(capa.nome), arguments: capa.argumentos || {} } };
      return await chamarPC(env, ctx, pc, m, enc.encode(JSON.stringify(m)), t0);
    }
    if (!ap) {
      if (pc && metodo === 'initialize') return rpc(unico.id, { result: inicioSemCelular(unico) });
      if (pc && metodo === 'tools/list') return rpc(unico.id, { result: { tools: await ferramentasPC(env, pc) } });
      return rpc(msg?.id, { error: { code: -32000, message: 'nenhum celular cadastrado na Central' } }, 503);
    }
    const listaPC = pc && metodo === 'tools/list' ? ferramentasPC(env, pc) : null;  // em paralelo com o celular
    const e = { armado_ate: ap.armado_ate || 0, travado: ap.travado || 0, desarmado_permite: ap.desarmado_permite || 'ir' };
    for (const m of Array.isArray(msg) ? msg : [msg]) {
      if (m?.method !== 'tools/call') continue;
      const nome = String(m.params?.name || '');
      const motivo = bloqueioNaBorda(nome, e);
      if (motivo) {
        await registrar(env, 'painel', 'bloqueado_na_borda', { ferramenta: nome.slice(0, 60) });
        await registrarChamada(env, nome, m.params?.arguments, 'bloqueado', 0);
        const texto = JSON.stringify({ erro: motivo, bloqueado: true, onde: 'painel' });
        return rpc(m.id, { result: { content: [{ type: 'text', text: texto }], structuredContent: JSON.parse(texto), isError: true } });
      }
    }
    const cab = { 'content-type': 'application/json', accept: req.headers.get('accept') || 'application/json, text/event-stream',
      'x-painel-assinatura': await assinarRequisicao(env, bruto), 'ngrok-skip-browser-warning': '1' };
    for (const h of ['mcp-session-id', 'mcp-protocol-version']) if (req.headers.get(h)) cab[h] = req.headers.get(h);
    // 1º o canal direto (conexão aberta pelo celular: sem túnel); sem canal, o túnel (ngrok); sem os dois, espera o
    // canal voltar e repete uma vez (C5)
    const inicioTransporte = Date.now();
    const chamada = (Array.isArray(msg) ? msg : [msg]).find(m => m?.method === 'tools/call');
    const lista = metodo === 'tools/list', inicio = metodo === 'initialize';
    let { r, via, motivo } = await repassarCelular(env, ap, cab, bruto, chamada ? 'tools/call' : metodo);
    // canal que respondeu com erro (ex.: 504) também é "celular fora do ar" para abrir a conversa e listar ferramentas
    if (r && !r.ok && (lista || inicio)) { motivo = `o celular respondeu HTTP ${r.status} pelo ${via}`; r = null; }
    if (!r) {
      // celular fora do ar: o que ele respondeu da última vez (C4) unido ao PC; sem nada guardado, só o PC (C1)
      const g = lista || inicio ? await guardadoCelular(env, ap.id) : null;
      if (lista && g?.ferramentas) return rpc(unico.id, { result: { tools: [...g.ferramentas.filter(t => !ehPC(t?.name)),
        ...(listaPC ? await listaPC : [])] } });
      if (inicio && (g?.inicio || g?.ferramentas)) return rpc(unico.id, { result: inicioGuardado(unico, g, pc) });
      if (pc && inicio) return rpc(unico.id, { result: inicioSemCelular(unico) });
      if (listaPC) return rpc(unico.id, { result: { tools: await listaPC } });
      if (chamada) {  // resultado de erro legível (não erro HTTP): a conversa continua e o Claude sabe o que houve
        ctx.waitUntil(registrarChamada(env, String(chamada.params?.name || '?'), chamada.params?.arguments, 'celular fora do ar',
          Date.now() - t0).catch(() => {}));
        return resultadoTexto(chamada.id, { erro: foraDoAr(ap), fora_do_ar: true, detalhe: motivo });
      }
      return rpc(msg?.id, { error: { code: -32000, message: `o celular está fora do ar (${motivo}): confira se o serviço controle-ir está ligado` } }, 503);
    }
    if (chamada) ctx.waitUntil(registrarChamada(env, String(chamada.params?.name || '?'), chamada.params?.arguments,
      `${r.ok ? 'ok' : `HTTP ${r.status}`} · ${via}`, Date.now() - t0).catch(() => {}));
    if (chamada && r.status === 401) return resultadoTexto(chamada.id, { erro: recusouAssinatura('celular') });
    const sai = { 'content-type': r.headers.get('content-type') || 'application/json', 'cache-control': 'no-store',
      'server-timing': `central;dur=${inicioTransporte - t0}, transporte;dur=${Date.now() - inicioTransporte}`,
      'x-via': via === 'canal' ? 'canal' : 'tunel' };  // cabeçalho só em ASCII
    if (r.headers.get('mcp-session-id')) sai['mcp-session-id'] = r.headers.get('mcp-session-id');
    if ((lista || inicio) && r.ok) {  // guarda o que o celular respondeu (C4) e une as ferramentas do PC às dele
      const texto = await r.text();
      try {
        const base = lerRpc(texto, sai['content-type']);
        if (inicio && base?.result?.serverInfo) ctx.waitUntil(guardarCelular(env, ap.id, 'inicio', base.result).catch(() => {}));
        if (lista && Array.isArray(base?.result?.tools)) {
          const doCelular = base.result.tools.filter(t => !ehPC(t?.name));
          if (doCelular.length) ctx.waitUntil(guardarCelular(env, ap.id, 'ferramentas', doCelular).catch(() => {}));
          const extra = listaPC ? await listaPC : [];
          if (extra.length) {
            base.result.tools = [...doCelular, ...extra];
            return new Response(JSON.stringify(base), { status: 200, headers: { ...sai, 'content-type': 'application/json' } });
          }
        }
      } catch { /* resposta que não dá para ler: vai como veio */ }
      return new Response(texto, { status: r.status, headers: sai });
    }
    return new Response(r.body, { status: r.status, headers: sai });
  },
};

// O provedor OAuth (biblioteca da Cloudflare) cuida de /.well-known, /oauth/register, /oauth/token e da checagem do
// token em /mcp. O recurso é a própria origem do Worker, por isso o provedor nasce na primeira requisição.
let provedor = null, origemDoProvedor = null;
function criarProvedor(origem) {
  return new OAuthProvider({
    apiRoute: '/mcp',
    apiHandler: mcpApi,
    defaultHandler: painelApp,
    authorizeEndpoint: '/authorize',
    tokenEndpoint: '/oauth/token',
    clientRegistrationEndpoint: '/oauth/register',
    scopesSupported: [ESCOPO],
    resourceMetadata: { resource: `${origem}/mcp`, authorization_servers: [origem] },
    accessTokenTTL: 3600,
    refreshTokenTTL: 30 * 86400,
    clientRegistrationCallback: ({ clientMetadata }) => {
      const uris = Array.isArray(clientMetadata.redirect_uris) ? clientMetadata.redirect_uris : [];
      if (!uris.length || !uris.every(destinoPermitido))
        return { code: 'invalid_redirect_uri', description: 'só o Claude, o ChatGPT ou um app local podem se registrar', status: 400 };
    },
  });
}
export default {
  fetch(req, env, ctx) {
    const u = new URL(req.url);
    if (u.pathname === '/api/celular/canal') return abrirCanal(req, env);
    const origem = u.origin;
    if (!provedor || origemDoProvedor !== origem) { provedor = criarProvedor(origem); origemDoProvedor = origem; }
    return provedor.fetch(req, env, ctx);
  },
};
