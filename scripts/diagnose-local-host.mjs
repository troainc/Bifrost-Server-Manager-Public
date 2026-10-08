// Read-only testing 17 diagnostics. Never print private tickets, tokens or receipts.
import { constants } from 'node:fs';
import { open, lstat } from 'node:fs/promises';
import { request } from 'node:https';
import { X509Certificate } from 'node:crypto';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

const home = '/home/bifrost-games';
const stages = new Set(['idle', 'pending', 'approved', 'paired', 'denied', 'expired', 'revoked']);
export function summarizeStatus(value, status) {
  return {
    httpStatus: status,
    stage: stages.has(value?.stage) ? value.stage : 'unknown',
    joinTicketPresent: typeof value?.ticket === 'string' && /^[A-Za-z0-9_-]{64}$/.test(value.ticket),
    parentIdentityPresent: typeof value?.parentId === 'string' && /^[0-9a-f-]{36}$/i.test(value.parentId),
  };
}
export function classifyError(error) {
  const code = typeof error?.code === 'string' ? error.code : '';
  return /^(?:EACCES|ENOENT|ECONNREFUSED|ECONNRESET|ENETUNREACH|EHOSTUNREACH|ETIMEDOUT|ENOTFOUND|EAI_AGAIN|ERR_TLS_CERT_ALTNAME_INVALID|DEPTH_ZERO_SELF_SIGNED_CERT|SELF_SIGNED_CERT_IN_CHAIN|UNABLE_TO_VERIFY_LEAF_SIGNATURE|CERT_HAS_EXPIRED)$/.test(code) ? code : 'CHECK_FAILED';
}
async function fileState(path) {
  try {
    const info = await lstat(path);
    return { exists: true, regular: info.isFile() && !info.isSymbolicLink(), ownedByGameAccount: info.uid === process.getuid(), privateMode: (info.mode & 0o077) === 0 };
  } catch (error) {
    if (error.code === 'ENOENT') return { exists: false };
    return { checkError: classifyError(error) };
  }
}
async function localStatus(bootstrap) {
  const origin = new URL(bootstrap.local);
  if (origin.protocol !== 'https:' || origin.origin !== bootstrap.local || origin.username || origin.password) throw new Error('Invalid local origin');
  if (typeof bootstrap.certificate !== 'string' || bootstrap.certificate.includes('PRIVATE KEY')) throw new Error('Invalid public certificate');
  new X509Certificate(bootstrap.certificate);
  if (!/^[A-Za-z0-9_-]{64}$/.test(bootstrap.token ?? '')) throw new Error('Invalid private capability');
  return new Promise((resolveResult, reject) => {
    const req = request(new URL('/api/node/local-host', origin), { method: 'GET', ca: bootstrap.certificate,
      rejectUnauthorized: true, headers: { accept: 'application/json', authorization: 'Bearer ' + bootstrap.token } }, response => {
      let bytes = 0; const chunks = [];
      response.on('data', chunk => { bytes += chunk.length; if (bytes > 16384) req.destroy(new Error('Oversized response')); else chunks.push(chunk); });
      response.on('error', reject);
      response.on('end', () => {
        try { resolveResult(summarizeStatus(JSON.parse(Buffer.concat(chunks).toString('utf8')), response.statusCode)); }
        catch { resolveResult({ httpStatus: response.statusCode, stage: 'non-json-response', joinTicketPresent: false }); }
      });
    });
    const timeout = setTimeout(() => req.destroy(Object.assign(new Error('Timeout'), { code: 'ETIMEDOUT' })), 20000);
    req.on('close', () => clearTimeout(timeout)); req.on('error', reject); req.end();
  });
}
export async function diagnose() {
  if (process.platform !== 'linux' || typeof process.getuid !== 'function' || process.getuid() === 0) throw new Error('Run this read-only diagnostic under bifrost-games, not root');
  const output = { readOnly: true, accountNonRoot: true, files: {} };
  for (const [name, path] of [
    ['bootstrap', home + '/.config/bifrost-host-agent/local-bootstrap.json'],
    ['hostConfig', home + '/.config/bifrost-host-agent/host-agent.json'],
    ['hostToken', home + '/.local/state/bifrost-host-agent/host.token'],
    ['joinReceipt', home + '/.local/state/bifrost-host-agent/instance-join.json'],
    ['ledger', home + '/.local/state/bifrost-host-agent/job-ledger.json'],
    ['ledgerLock', home + '/.local/state/bifrost-host-agent/job-ledger.json.lock'],
  ]) output.files[name] = await fileState(path);
  try {
    const handle = await open(home + '/.config/bifrost-host-agent/local-bootstrap.json', constants.O_RDONLY | constants.O_NOFOLLOW);
    let bootstrap;
    try {
      const info = await handle.stat();
      if (!info.isFile() || info.uid !== process.getuid() || (info.mode & 0o077) !== 0 || info.nlink !== 1 || info.size > 32768) throw new Error('Unsafe bootstrap');
      bootstrap = JSON.parse(await handle.readFile('utf8'));
    } finally { await handle.close(); }
    output.localSetup = await localStatus(bootstrap);
  } catch (error) { output.localSetup = { checkError: classifyError(error) }; }
  console.log(JSON.stringify(output, null, 2));
}
// Supports both a normal file and root piping the reviewed source to the
// isolated game account's Node stdin, without granting access to root/troa home.
if (process.argv[1] === '-' || (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href)) {
  await diagnose().catch(error => { console.log(JSON.stringify({ readOnly: true, checkError: classifyError(error) })); process.exitCode = 1; });
}
