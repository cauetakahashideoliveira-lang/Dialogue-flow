// Painel da Casa — interface. A digital (passkey) é pedida para entrar e de novo antes de aumentar poder.
const $ = id => document.getElementById(id);
const { startRegistration, startAuthentication } = window.SimpleWebAuthnBrowser;
let dados = null;

function aviso(txt, tipo = '') { $('msg').textContent = txt; $('msg').className = tipo || 'suave'; }
async function api(rota, corpo = {}) {
  const r = await fetch(`/api/${rota}`, { method: 'POST', credentials: 'same-origin',
    headers: { 'content-type': 'application/json', 'x-painel': '1' }, body: JSON.stringify(corpo) });
  const j = await r.json().catch(() => ({ erro: `HTTP ${r.status}` }));
  if (!r.ok) throw Object.assign(new Error(j.erro || `HTTP ${r.status}`), { status: r.status });
  return j;
}
const hora = t => t ? new Date(t * 1000).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' }) : '—';
const ha = t => { if (!t) return 'nunca'; const s = Math.max(0, Math.round(Date.now() / 1000 - t));
  return s < 90 ? `há ${s} s` : s < 5400 ? `há ${Math.round(s / 60)} min` : `há ${Math.round(s / 3600)} h`; };
function el(tag, txt, cls) { const e = document.createElement(tag); if (txt != null) e.textContent = txt; if (cls) e.className = cls; return e; }

// O Safari (iPad/iPhone) só abre o Face ID se o pedido da passkey vier logo depois do toque. Por isso as opções
// do desafio são buscadas ANTES (ao abrir a página e depois de cada uso) e a digital vem antes da ação.
let preLogin = null, preLoginEm = 0, digitalEm = 0;
function prepararLogin() {
  api('login/opcoes').then(p => { preLogin = p; preLoginEm = Date.now(); }).catch(() => { preLogin = null; });
}
async function digital() {  // confirmação com passkey (entrar ou renovar antes de uma ação sensível)
  let p = preLogin && Date.now() - preLoginEm < 240000 ? preLogin : null;
  preLogin = null;
  try {
    if (!p) p = await api('login/opcoes');
    const resposta = await startAuthentication({ optionsJSON: p.opcoes });
    const r = await api('login/verificar', { desafio_id: p.desafio_id, resposta });
    digitalEm = Date.now();
    return r;
  } finally { prepararLogin(); }
}
async function comDigital(fn) {
  if (Date.now() - digitalEm > 100000) await digital();  // a digital primeiro, ainda dentro do toque
  try { return await fn(); } catch (e) {
    if (e.status !== 403 || !/digital/.test(e.message)) throw e;
    digitalEm = 0;  // no Chrome dá para pedir de novo aqui; no Safari, o toque seguinte resolve
    try { await digital(); } catch { throw new Error('confirme a digital de novo: toque outra vez no botão'); }
    return fn();
  }
}

function render() {
  $('entrar').classList.toggle('escondido', !!dados); $('logado').classList.toggle('escondido', !dados);
  if (!dados) return;
  const cel = $('celulares'); cel.replaceChildren();
  const ativos = dados.aparelhos.filter(a => !a.revogado);
  if (!ativos.length) cel.append(el('p', 'Nenhum celular cadastrado ainda.', 'suave'));
  for (const a of ativos) {
    const e = a.estado, agora = dados.agora;
    const travado = e.travado, armado = !travado && e.armado_ate > agora;
    const st = el('div', travado ? 'TRAVADO (emergência)' : armado ? `ARMADO até ${hora(e.armado_ate)}` : 'Desarmado',
      `estado ${travado ? 'perigo-t' : armado ? 'alerta' : 'ok'}`);
    const ap = el('div', a.aplicado ? '✓ aplicado no celular' : '… pendente: o celular ainda não confirmou', a.aplicado ? 'ok' : 'alerta');
    cel.append(el('strong', a.nome), st, ap,
      el('p', `Último contato ${ha(a.ultimo_contato)} · versão ${a.versao || '?'} · desarmado permite: ${e.desarmado_permite === 'ir' ? 'infravermelho' : 'só consulta'}`, 'suave'));
    $('permite').value = e.desarmado_permite;
    const rv = el('button', `Revogar ${a.nome}`, 'sec');
    rv.onclick = () => acao(() => comDigital(() => api('revogar', { tipo: 'aparelho', id: a.id })), 'Celular revogado');
    cel.append(rv);
  }
  $('enderecoConector').textContent = dados.conector || '';
  const cel0 = ativos[0];
  $('celularMcp').textContent = !cel0 ? '' : cel0.estado.tem_mcp
    ? `✓ o celular informou o endereço dele ${ha(cel0.estado.mcp_url_em)}: o painel repassa as chamadas, assinadas`
    : '… aguardando o celular informar o endereço (precisa da versão 1.0.26 ou mais nova)';
  $('soPainel').checked = !!(cel0 && cel0.estado.so_pelo_painel);
  $('soPainel').disabled = !cel0;
  const ac = $('acessos'); ac.replaceChildren();
  if (!dados.acessos.length) ac.append(el('li', 'Nenhum acesso autorizado ainda.', 'suave'));
  for (const g of dados.acessos) {
    const li = el('li', `${g.cliente} → ${g.destino || '?'} · autorizado ${ha(g.criado)}`);
    const b = el('button', 'Revogar acesso', 'sec');
    b.onclick = () => acao(() => api('acesso/revogar', { id: g.id }), 'Acesso revogado');
    li.append(b); ac.append(li);
  }
  const pk = $('passkeys'); pk.replaceChildren();
  for (const p of dados.passkeys.filter(p => !p.revogada)) {
    const li = el('li', `${p.nome}${p.sua ? ' (esta sessão)' : ''} · último uso ${ha(p.ultimo_uso)}`);
    if (!p.sua) { const b = el('button', 'Revogar', 'sec'); b.onclick = () => acao(() => comDigital(() => api('revogar', { tipo: 'passkey', id: p.id })), 'Passkey revogada'); li.append(b); }
    pk.append(li);
  }
  const ev = $('eventos'); ev.replaceChildren();
  for (const e of dados.eventos) {
    let d = ''; try { const o = JSON.parse(e.dados || '{}'); d = Object.entries(o).filter(([k]) => !['quando'].includes(k)).map(([k, v]) => `${k}: ${typeof v === 'object' ? JSON.stringify(v) : v}`).join(' · '); } catch { d = e.dados; }
    ev.append(el('li', `${hora(e.quando)} · ${e.origem} · ${e.tipo}${d ? ' — ' + d.slice(0, 220) : ''}`, 'suave'));
  }
}

async function carregar() {
  try { dados = await api('painel'); } catch (e) { dados = null; if (e.status !== 401) aviso(e.message, 'perigo-t'); }
  render();
}
async function acao(fn, ok) {
  try { aviso('…'); await fn(); aviso(ok, 'ok'); } catch (e) { aviso(e.message, 'perigo-t'); }
  await carregar();
}
const meiaNoite = () => { const d = new Date(); d.setHours(24, 0, 0, 0); return Math.floor(d / 1000); };

$('btEntrar').onclick = () => acao(digital, 'Entrou');
$('btPrimeiro').onclick = () => acao(async () => {
  const { desafio_id, opcoes } = await api('registro/opcoes', { codigo_inicial: $('codigoInicial').value });
  const resposta = await startRegistration({ optionsJSON: opcoes });
  await api('registro/verificar', { desafio_id, resposta, nome: $('nomePasskey').value || 'primeiro aparelho' });
}, 'Passkey cadastrada');
$('btNovaPasskey').onclick = () => acao(() => comDigital(async () => {
  const nome = prompt('Nome do aparelho desta passkey (ex.: iPad):') || 'aparelho';
  const { desafio_id, opcoes } = await api('registro/opcoes', {});
  const resposta = await startRegistration({ optionsJSON: opcoes });
  await api('registro/verificar', { desafio_id, resposta, nome });
}), 'Passkey cadastrada');
$('btConvite').onclick = () => acao(() => comDigital(async () => {
  const { convite, expira_em_min } = await api('convite');
  const link = `${location.origin}/#convite=${convite}`;
  $('convite').replaceChildren(el('span', `Abra no outro aparelho em até ${expira_em_min} min (uso único): `), el('code', link));
}), 'Convite criado');
const conviteNaUrl = new URLSearchParams(location.hash.slice(1)).get('convite');
let preConvite = null;
const prepararConvite = () => api('registro/opcoes', { convite: conviteNaUrl })
  .then(p => { preConvite = p; }).catch(e => aviso(e.message, 'perigo-t'));
if (conviteNaUrl) { $('aceitarConvite').classList.remove('escondido'); prepararConvite(); }
$('btAceitar').onclick = () => acao(async () => {
  const p = preConvite || await api('registro/opcoes', { convite: conviteNaUrl });
  preConvite = null;
  try {
    const resposta = await startRegistration({ optionsJSON: p.opcoes });
    await api('registro/verificar', { desafio_id: p.desafio_id, resposta, nome: $('nomeConvite').value || 'iPad' });
  } catch (e) { prepararConvite(); throw e; }  // o convite continua valendo: é só tocar de novo
  history.replaceState(null, '', '/'); $('aceitarConvite').classList.add('escondido');
}, 'Digital deste aparelho cadastrada');
$('btArmarDia').onclick = () => acao(() => comDigital(() => api('armar', { ate: meiaNoite() })), 'Armado até a meia-noite');
$('btArmar2').onclick = () => acao(() => comDigital(() => api('armar', { horas: 2 })), 'Armado por 2 h');
$('btDesarmar').onclick = () => acao(() => api('desarmar'), 'Desarmado');
$('btEmergencia').onclick = () => { if (confirm('Cortar todo o acesso agora? Só volta armando de novo com a digital.')) acao(() => api('emergencia'), 'EMERGÊNCIA aplicada'); };
$('soPainel').onchange = e => acao(() => e.target.checked ? api('so_pelo_painel', { valor: 1 })
  : comDigital(() => api('so_pelo_painel', { valor: 0 })), e.target.checked ? 'Agora o Claude só entra pelo painel' : 'Conector direto aceito de novo');
$('permite').onchange = e => acao(() => comDigital(() => api('desarmado_permite', { valor: e.target.value })), 'Atualizado');
$('btParear').onclick = () => acao(() => comDigital(async () => {
  const { codigo, expira_em_min } = await api('celular/codigo');
  $('pareamento').replaceChildren(el('span', `No Termux do celular, em até ${expira_em_min} min: `), el('code', `controle-ir painel parear ${location.origin} ${codigo}`));
}), 'Código criado');
$('btIntegridade').onclick = () => acao(async () => { const r = await api('integridade'); if (!r.ok) throw new Error(`histórico alterado no evento ${r.quebra_em}`); aviso(`Histórico íntegro (${r.eventos} eventos)`, 'ok'); }, 'Histórico íntegro');
$('btSair').onclick = () => acao(() => api('sair'), 'Saiu');
prepararLogin();
carregar();
setInterval(() => { if (dados && !document.hidden) carregar(); }, 15000);
