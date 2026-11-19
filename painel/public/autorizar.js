// Consentimento OAuth: o Claude só ganha acesso depois da sua digital (passkey) nesta página.
const { startAuthentication } = window.SimpleWebAuthnBrowser;
const $ = id => document.getElementById(id);
const handle = $('pedido').dataset.handle;
const msg = (txt, cls = 'suave') => { $('msg').textContent = txt; $('msg').className = cls; };
async function api(rota, corpo = {}) {
  const r = await fetch(rota, { method: 'POST', credentials: 'same-origin',
    headers: { 'content-type': 'application/json', 'x-painel': '1' }, body: JSON.stringify(corpo) });
  const j = await r.json().catch(() => ({ erro: `HTTP ${r.status}` }));
  if (!r.ok) throw new Error(j.erro || `HTTP ${r.status}`);
  return j;
}
// o Safari só abre o Face ID/Touch ID logo depois do toque: o desafio é buscado antes
let pre = null;
const preparar = () => api('/api/login/opcoes').then(p => { pre = p; }).catch(() => { pre = null; });
async function digital() {
  let p = pre; pre = null;
  try {
    if (!p) p = await api('/api/login/opcoes');
    const resposta = await startAuthentication({ optionsJSON: p.opcoes });
    return await api('/api/login/verificar', { desafio_id: p.desafio_id, resposta });
  } finally { preparar(); }
}
async function decidir(decisao) {
  msg('…');
  try {
    if (decisao === 'autorizar') await digital();
    const r = await api('/authorize', { handle, decisao });
    msg(decisao === 'autorizar' ? 'Autorizado. Voltando ao Claude…' : 'Negado.', 'suave');
    location.href = r.redirectTo;
  } catch (e) { msg(e.message, 'perigo'); }
}
$('btAutorizar')?.addEventListener('click', () => decidir('autorizar'));
$('btNegar').addEventListener('click', () => decidir('negar'));
preparar();
