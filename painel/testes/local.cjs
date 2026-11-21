// Inicia a Central e o E2E com D1, KV, Durable Object e código de cadastro próprios da rodada.
const { randomBytes } = require('node:crypto');
const { spawn } = require('node:child_process');
const { once } = require('node:events');
const { mkdtemp, rm } = require('node:fs/promises');
const { tmpdir } = require('node:os');
const path = require('node:path');
const { unstable_dev } = require('wrangler');

async function testar() {
  const estado = await mkdtemp(path.join(tmpdir(), 'central-e2e-'));
  const codigo = randomBytes(24).toString('hex');
  let worker;
  try {
    worker = await unstable_dev('src/index.js', {
      config: 'wrangler.jsonc', local: true, ip: '127.0.0.1', port: 0,
      persistTo: estado, vars: { CODIGO_INICIAL: codigo }, envFiles: [],
      experimental: { disableExperimentalWarning: true, watch: false },
    });
    const teste = spawn(process.execPath, ['testes/e2e.cjs', `http://localhost:${worker.port}`], {
      stdio: 'inherit', env: { ...process.env, E2E_ESTADO: estado, E2E_CODIGO: codigo },
    });
    const [status] = await once(teste, 'exit');
    process.exitCode = status ?? 1;
  } finally {
    if (worker) await worker.stop();
    await rm(estado, { recursive: true, force: true });
  }
}

testar().catch(erro => { console.error(erro); process.exitCode = 1; });
