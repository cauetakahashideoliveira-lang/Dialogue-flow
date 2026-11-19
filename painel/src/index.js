// Painel da Casa — administração do controle-ir fora do agente (docs/seguranca.md, Etapa 1).
// Dono: passkeys (WebAuthn, SimpleWebAuthn). Celular: token de aparelho + estado ASSINADO (Ed25519) que ele confere
// com a chave pública fixada no pareamento. Nada aqui é alcançável pelas ferramentas do conector.
import {
  generateAuthenticationOptions, generateRegistrationOptions, verifyAuthenticationResponse,
  verifyRegistrationResponse,
} from '@simplewebauthn/server';
import { isoBase64URL } from '@simplewebauthn/server/helpers';

const SESSAO_MAX = 12 * 3600, SESSAO_OCIOSA = 30 * 60, PASSKEY_FRESCA = 120, DESAFIO = 300, PAREAMENTO = 600;
const HORAS_MAX = 24;
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
async function registrar(env, origem, tipo, dados = {}) {
  const ult = await env.DB.prepare('SELECT hash FROM eventos ORDER BY id DESC LIMIT 1').first();
  const anterior = ult ? ult.hash : 'inicio';
  const quando = agora(), corpo = JSON.stringify(dados).slice(0, 2000);
  const hash = await sha256(`${anterior}|${quando}|${origem}|${tipo}|${corpo}`);
  await env.DB.prepare('INSERT INTO eventos (quando, origem, tipo, dados, hash, hash_anterior) VALUES (?, ?, ?, ?, ?, ?)')
    .bind(quando, origem, tipo, corpo, hash, anterior).run();
}

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
async function chaves(env) {
  let priv = await config(env, 'chave_privada'), pub = await config(env, 'chave_publica');
  if (!priv) {
    const par = await crypto.subtle.generateKey({ name: 'Ed25519' }, true, ['sign', 'verify']);
    priv = isoBase64URL.fromBuffer(new Uint8Array(await crypto.subtle.exportKey('pkcs8', par.privateKey)));
    pub = isoBase64URL.fromBuffer(new Uint8Array(await crypto.subtle.exportKey('raw', par.publicKey)));
    await definir(env, 'chave_privada', priv);
    await definir(env, 'chave_publica', pub);
  }
  const chave = await crypto.subtle.importKey('pkcs8', isoBase64URL.toBuffer(priv), { name: 'Ed25519' }, false, ['sign']);
  return { chave, pub };
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
    await env.DB.prepare('DELETE FROM convites WHERE hash = ?').bind(h).run();
  } else if (!fresca(s)) {
    return erro('para cadastrar outro aparelho, entre com uma passkey já cadastrada (há menos de 2 min)', 403);
  }
  const { rpID } = rp(req);
  const existentes = await env.DB.prepare('SELECT id, transportes FROM credenciais WHERE revogada = 0').all();
  const opcoes = await generateRegistrationOptions({
    rpName: 'Painel da Casa', rpID, userName: 'dono', userDisplayName: 'Dono',
    userID: enc.encode('dono'), attestationType: 'none',
    authenticatorSelection: { residentKey: 'required', userVerification: 'required' },
    excludeCredentials: existentes.results.map(c => ({ id: c.id, transports: c.transportes ? JSON.parse(c.transportes) : undefined })),
  });
  const id = await guardarDesafio(env, opcoes.challenge, 'registro', s ? s.hash : null);
  return json({ desafio_id: id, opcoes });
}

async function registroVerificar(env, req, corpo) {
  const d = await consumirDesafio(env, corpo.desafio_id, 'registro');
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
  return await env.DB.prepare('SELECT * FROM estado WHERE aparelho = ?').bind(aparelho).first()
    || { aparelho, seq: 0, armado_ate: 0, travado: 0, desarmado_permite: 'ir' };
}
async function mudarEstado(env, aparelho, mudanca, por, motivo) {
  const e = { ...(await estadoDe(env, aparelho)), ...mudanca };
  e.seq += 1;
  await env.DB.prepare(`INSERT INTO estado (aparelho, seq, armado_ate, travado, desarmado_permite, motivo, alterado_por, alterado_em)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?) ON CONFLICT(aparelho) DO UPDATE SET seq = excluded.seq, armado_ate = excluded.armado_ate,
    travado = excluded.travado, desarmado_permite = excluded.desarmado_permite, motivo = excluded.motivo,
    alterado_por = excluded.alterado_por, alterado_em = excluded.alterado_em`)
    .bind(aparelho, e.seq, e.armado_ate, e.travado, e.desarmado_permite, motivo, por, agora()).run();
  await registrar(env, 'painel', 'estado_alterado', { aparelho, seq: e.seq, armado_ate: e.armado_ate, travado: e.travado,
    desarmado_permite: e.desarmado_permite, motivo });
  return e;
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
    } else if (acao === 'desarmado_permite') {
      const v = corpo.valor === 'nada' ? 'nada' : 'ir';
      if (v === 'ir' && !fresca(s)) return erro('confirme com a digital para liberar o infravermelho desarmado', 403);
      feitos.push(await mudarEstado(env, ap, { desarmado_permite: v }, por, `desarmado permite ${v}`));
    }
  }
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

async function estadoParaCelular(env, req) {
  const ap = await aparelhoDoToken(env, req);
  if (!ap) return erro('aparelho não autorizado', 401);
  await env.DB.prepare('UPDATE aparelhos SET ultimo_contato = ? WHERE id = ?').bind(agora(), ap.id).run();
  const e = await estadoDe(env, ap.id);
  return json(await assinar(env, { v: 1, aparelho: ap.id, seq: e.seq, armado_ate: e.armado_ate, travado: e.travado,
    desarmado_permite: e.desarmado_permite, emitido_em: agora() }));
}

async function ackCelular(env, req, corpo) {
  const ap = await aparelhoDoToken(env, req);
  if (!ap) return erro('aparelho não autorizado', 401);
  const seq = Number(corpo.seq) || 0;
  await env.DB.prepare('UPDATE aparelhos SET aplicado_seq = MAX(aplicado_seq, ?), aplicado_em = ?, versao = ? WHERE id = ?')
    .bind(seq, agora(), String(corpo.versao || ap.versao || '').slice(0, 20), ap.id).run();
  const eventos = Array.isArray(corpo.eventos) ? corpo.eventos.slice(0, 200) : [];
  for (const ev of eventos) await registrar(env, `celular:${ap.id}`, String(ev.evento || 'evento').slice(0, 40), ev);
  return json({ ok: true, recebidos: eventos.length });
}

async function painel(env, s) {
  const aps = (await env.DB.prepare('SELECT id, nome, criado, ultimo_contato, versao, aplicado_seq, aplicado_em, revogado FROM aparelhos ORDER BY criado').all()).results;
  for (const a of aps) {
    a.estado = await estadoDe(env, a.id);
    a.aplicado = a.aplicado_seq >= a.estado.seq;  // só mostra como aplicado depois que o celular confirmar
  }
  const creds = (await env.DB.prepare('SELECT id, nome, criada, ultimo_uso, revogada FROM credenciais ORDER BY criada').all()).results;
  const eventos = (await env.DB.prepare('SELECT id, quando, origem, tipo, dados FROM eventos ORDER BY id DESC LIMIT 150').all()).results;
  return json({ agora: agora(), aparelhos: aps, passkeys: creds.map(c => ({ ...c, id: c.id.slice(0, 10), sua: c.id === s.credencial })),
    eventos, digital_recente: fresca(s) });
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

// ---------------------------------------------------------------- roteador
export default {
  async fetch(req, env) {
    const u = new URL(req.url), rota = u.pathname, metodo = req.method;
    if (!rota.startsWith('/api/')) return env.ASSETS.fetch(req);
    try {
      await inicializar(env);
      // rotas do celular (token de aparelho)
      if (rota === '/api/celular/parear' && metodo === 'POST') return await parearCelular(env, req, await req.json());
      if (rota === '/api/celular/estado' && metodo === 'GET') return await estadoParaCelular(env, req);
      if (rota === '/api/celular/ack' && metodo === 'POST') return await ackCelular(env, req, await req.json());
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
      if (rota === '/api/painel') return await painel(env, s);
      if (rota === '/api/sair') {
        await env.DB.prepare('DELETE FROM sessoes WHERE hash = ?').bind(s.hash).run();
        return json({ ok: true }, 200, { 'set-cookie': 'painel=; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=0' });
      }
      if (['/api/armar', '/api/desarmar', '/api/emergencia', '/api/desarmado_permite'].includes(rota))
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
      return erro('rota desconhecida', 404);
    } catch (e) {
      return erro(`falha interna: ${e.message}`, 500);
    }
  },
};
