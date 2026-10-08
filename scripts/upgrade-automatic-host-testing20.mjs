// Narrow preserving update for the verified testing 18 automatic Host service.
// It never changes enrollment, game files, catalog policy or the setup worker.
import { readFile, writeFile, lstat, mkdir, mkdtemp, rename, open } from 'node:fs/promises';
import { join, dirname, resolve } from 'node:path';
import { userInfo } from 'node:os';
import { createHash } from 'node:crypto';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { pathToFileURL } from 'node:url';
const exec = promisify(execFile);
const OLD = 'f6603eff0b696a2841d2cc51d4362e21f5fcd04f674ab5cc2052f611534fbea1';
const NEW = '9408da9bac948edc3063fbd5e97019e07c99d30084d961d390d68f8191969504';
const NODE = '/opt/bifrost-node-v24.19.0/bin/node';
const PACKAGE_URL = 'https://github.com/troainc/Bifrost-Server-Manager-Public/releases/download/v0.1.0-installtest.20/bifrost-linux-host-agent.zip';
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
export const managedUnit = (home, digest) => `[Unit]\nDescription=Bifrost local game Host Agent\n[Service]\nExecStart=${NODE} ${home}/.local/opt/bifrost-host-agent-${digest}/dist/main.js\nEnvironment=BIFROST_HOST_AGENT_CONFIG=${home}/.config/bifrost-host-agent/host-agent.json\nRestart=on-failure\nRestartSec=10\nUMask=0077\n[Install]\nWantedBy=default.target\n`;
async function privatePath(path, directory = false) {
  const s = await lstat(path);
  if (s.uid !== process.getuid() || s.isSymbolicLink() || (directory ? !s.isDirectory() : !s.isFile() || s.nlink !== 1) || (s.mode & 0o077)) throw new Error('An existing private path failed ownership or mode validation.');
  if (!directory && s.size > 1024 * 1024) throw new Error('An existing state file exceeds the inspection bound.');
}
async function absent(path) { try { await lstat(path); throw new Error('Existing lock or destination requires operator review.'); } catch (e) { if (e.code !== 'ENOENT') throw e; } }
async function atomic(path, bytes) {
  const temporary = `${path}.testing20-next`;
  const fd = await open(temporary, 'wx', 0o600);
  try { await fd.writeFile(bytes); await fd.sync(); } finally { await fd.close(); }
  await rename(temporary, path);
}
export async function downloadMatchedPackage(fetchPackage = fetch) {
  const r = await fetchPackage(PACKAGE_URL, { signal: AbortSignal.timeout(120000) });
  const finalUrl = new URL(r.url);
  if (!r.ok || finalUrl.protocol !== 'https:' || finalUrl.username || finalUrl.password || !['github.com', 'release-assets.githubusercontent.com', 'objects.githubusercontent.com'].includes(finalUrl.hostname)) throw new Error('Matched HTTPS package download failed.');
  const chunks = []; let size = 0;
  for await (const chunk of r.body) { size += chunk.length; if (size > 2 * 1024 * 1024) throw new Error('Host package exceeds the download bound.'); chunks.push(chunk); }
  return Buffer.concat(chunks);
}
const unzip = `import os,pathlib,stat,sys,zipfile
archive,destination=sys.argv[1:]
with zipfile.ZipFile(archive) as z:
 names=set();total=0
 for entry in z.infolist():
  p=pathlib.PurePosixPath(entry.filename);mode=entry.external_attr>>16
  if p.is_absolute() or not p.parts or '..' in p.parts or '\\\\' in entry.filename or entry.filename in names or (stat.S_IFMT(mode) not in (0,stat.S_IFDIR,stat.S_IFREG)):raise SystemExit('Unsafe package member')
  names.add(entry.filename);total+=entry.file_size
  if total>32*1024*1024 or len(names)>10000:raise SystemExit('Package bounds exceeded')
 # Only the exact verified archive is extracted into a fresh private directory.
 pathlib.Path(destination).mkdir(mode=0o700)
 for entry in z.infolist():
  p=pathlib.Path(destination).joinpath(*pathlib.PurePosixPath(entry.filename).parts)
  if entry.is_dir():p.mkdir(mode=0o700,parents=True,exist_ok=True);continue
  p.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
  with p.open('xb') as f:f.write(z.read(entry))
  p.chmod(0o600)
`;
// Options are dependency injection for disposable tests, not command-line input.
export async function upgradeAutomaticHost({ home = '/home/bifrost-games', node = NODE, packageBytes = downloadMatchedPackage, diagnoseOnly = false, onStage = () => {}, systemctl = async args => { await exec('/usr/bin/systemctl', ['--user', ...args], { timeout: 120000, maxBuffer: 4096 }); }, preflight = async (packageRoot, config) => { await exec(node, [join(packageRoot, 'dist/preflight-upgrade.js'), config], { timeout: 30000, maxBuffer: 4096 }); } } = {}) {
  onStage('private-path-validation');
  const unit = join(home, '.config/systemd/user/bifrost-host-agent.service');
  const config = join(home, '.config/bifrost-host-agent/host-agent.json');
  const token = join(home, '.local/state/bifrost-host-agent/host.token');
  for (const dir of [home, join(home,'.config'), join(home,'.config/systemd'), dirname(unit), dirname(config), join(home,'.local'), join(home,'.local/opt'), join(home,'.local/state'), dirname(token)]) await privatePath(dir, true);
  for (const file of [unit, config, token]) await privatePath(file);
  const oldUnit = await readFile(unit);
  onStage('managed-unit-validation');
  if (oldUnit.equals(Buffer.from(managedUnit(home, NEW)))) {
    const existing = join(home,'.local/opt',`bifrost-host-agent-${NEW}`); await privatePath(existing,true);
    await privatePath(join(existing,'.bifrost-package-sha256'));
    if ((await readFile(join(existing,'.bifrost-package-sha256'),'utf8')).trim() !== NEW) throw new Error('Existing package destination differs.');
    await preflight(existing,config); await systemctl(['is-active','--quiet','bifrost-host-agent.service']);
    return { updatedTo:'v0.1.0-installtest.20', alreadyUpdated:true, serviceActive:true, enrollmentPreserved:true, gameFilesChanged:false, heartbeatVerificationPending:true };
  }
  if (!oldUnit.equals(Buffer.from(managedUnit(home, OLD)))) throw new Error('This helper accepts only the exact testing 18 automatic Host service; existing service preserved.');
  onStage('state-path-validation');
  const state = JSON.parse(await readFile(config, 'utf8'));
  if (state.tokenFile !== token || state.ledgerFile !== join(home,'.local/state/bifrost-host-agent/job-ledger.json')) throw new Error('Custom state paths require operator review.');
  const preserved = [hash(await readFile(config)), hash(await readFile(token))];
  onStage('matched-package-download');
  const bytes = await packageBytes();
  onStage('matched-package-checksum');
  if (hash(bytes) !== NEW) throw new Error('Matched testing 20 Host archive checksum failed.');
  if (diagnoseOnly) {
    onStage('existing-compiled-preflight');
    await preflight(join(home,'.local/opt',`bifrost-host-agent-${OLD}`),config);
    onStage('existing-service-readiness');
    await systemctl(['is-active','--quiet','bifrost-host-agent.service']);
    const destination=join(home,'.local/opt',`bifrost-host-agent-${NEW}`);
    let packageDestinationPresent=false;
    try {
      await lstat(destination);packageDestinationPresent=true;
      onStage('existing-new-package-validation');
      await privatePath(destination,true);await privatePath(join(destination,'.bifrost-package-sha256'));
      if((await readFile(join(destination,'.bifrost-package-sha256'),'utf8')).trim()!==NEW)throw new Error('Existing package destination differs.');
      onStage('new-compiled-preflight');await preflight(destination,config);
    } catch(error) {if(error.code!=='ENOENT'||packageDestinationPresent)throw error;}
    return {readOnly:true,matchedDownloadVerified:true,currentServiceActive:true,packageDestinationPresent,gameFilesChanged:false};
  }
  onStage('private-package-preparation');
  const packageRoot = join(home, '.local/opt', `bifrost-host-agent-${NEW}`);
  const stage = await mkdtemp(join(home, '.local/opt/.testing20-stage-'));
  const archive = join(stage, 'host.zip'); await writeFile(archive, bytes, { mode: 0o600 });
  try { await lstat(packageRoot); await privatePath(packageRoot, true); if ((await readFile(join(packageRoot,'.bifrost-package-sha256'),'utf8')).trim() !== NEW) throw new Error('Existing package destination differs.'); }
  catch (e) { if (e.code !== 'ENOENT') throw e; await absent(packageRoot); await exec('/usr/bin/python3', ['-c', unzip, archive, packageRoot], { timeout: 30000, maxBuffer: 4096 }); await writeFile(join(packageRoot,'.bifrost-package-sha256'),`${NEW}\n`,{flag:'wx',mode:0o600}); }
  onStage('compiled-preflight');
  await preflight(packageRoot, config);
  onStage('existing-service-readiness');
  await systemctl(['is-active', '--quiet', 'bifrost-host-agent.service']);
  let stopped = false, replaced = false;
  try {
    onStage('service-stop');
    await systemctl(['stop', 'bifrost-host-agent.service']); stopped = true;
    onStage('stopped-state-recheck');
    await preflight(packageRoot, config);
    await absent(`${state.ledgerFile}.lock`);
    for (const file of [unit, config, token]) await privatePath(file);
    if (!(await readFile(unit)).equals(oldUnit) || hash(await readFile(config)) !== preserved[0] || hash(await readFile(token)) !== preserved[1]) throw new Error('Service or enrollment changed during preparation.');
    onStage('unit-backup-and-replacement');
    const backup = `${unit}.before-testing20`;
    try { await writeFile(backup, oldUnit, { flag: 'wx', mode: 0o600 }); }
    catch (e) { if (e.code !== 'EEXIST') throw e; await privatePath(backup); if (!(await readFile(backup)).equals(oldUnit)) throw new Error('Existing unit backup differs.'); }
    await atomic(unit, Buffer.from(managedUnit(home, NEW))); replaced = true;
    onStage('new-service-start');
    await systemctl(['daemon-reload']); await systemctl(['start', 'bifrost-host-agent.service']); await systemctl(['is-active', '--quiet', 'bifrost-host-agent.service']);
  } catch (e) {
    if (stopped) {
      onStage('preserving-service-recovery');
      // Never restart over an unresolved job/lock, or overwrite a concurrently changed unit.
      if (replaced) { await systemctl(['stop','bifrost-host-agent.service']).catch(()=>{}); if (!(await readFile(unit)).equals(Buffer.from(managedUnit(home,NEW)))) throw new Error('Unit changed during recovery; stopped for operator review.'); await atomic(unit, oldUnit); await systemctl(['daemon-reload']); }
      await preflight(packageRoot, config); await absent(`${state.ledgerFile}.lock`); await systemctl(['start','bifrost-host-agent.service']);
    }
    throw e;
  }
  return { updatedTo: 'v0.1.0-installtest.20', serviceActive: true, enrollmentPreserved: true, previousPackagePreserved: true, gameFilesChanged: false, heartbeatVerificationPending: true };
}
if (process.argv[1] === '-' || process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  let stage = 'account-and-runtime-validation';
  try {
    if (process.platform !== 'linux' || process.getuid() === 0 || userInfo().username !== 'bifrost-games' || process.execPath !== NODE || process.versions.node !== '24.19.0') throw new Error('Run the matched helper as bifrost-games using its existing pinned Node runtime.');
    for (const path of ['/opt','/opt/bifrost-node-v24.19.0','/opt/bifrost-node-v24.19.0/bin',NODE]) {
      const runtime = await lstat(path); if (runtime.isSymbolicLink() || (path === NODE ? !runtime.isFile() : !runtime.isDirectory()) || runtime.uid !== 0 || runtime.mode & 0o022) throw new Error('Pinned runtime ownership failed.');
    }
    if(process.argv.length>3 || process.argv.length===3 && process.argv[2]!=='--diagnose')throw new Error('Unsupported helper argument.');
    console.log(JSON.stringify(await upgradeAutomaticHost({diagnoseOnly:process.argv[2]==='--diagnose',onStage: value => {stage=value;}}), null, 2));
  } catch (error) {
    // Only fixed stages and allowlisted machine error codes are disclosed.
    const allowed = new Set(['ENOENT','EACCES','EPERM','EEXIST','ENOSPC','ETIMEDOUT','ECONNREFUSED','ENOTFOUND','EAI_AGAIN','CERT_HAS_EXPIRED','UNABLE_TO_VERIFY_LEAF_SIGNATURE','UNABLE_TO_GET_ISSUER_CERT_LOCALLY','ERR_TLS_CERT_ALTNAME_INVALID','DEPTH_ZERO_SELF_SIGNED_CERT']);
    const code = allowed.has(error?.code) ? error.code : allowed.has(error?.cause?.code) ? error.cause.code : 'CHECK_REFUSED';
    console.error(`Bifrost: automatic Host update did not complete. Stage: ${stage}; code: ${code}. Existing credentials and game files were preserved; inspect local service state before continuing.`); process.exitCode = 1;
  }
}
