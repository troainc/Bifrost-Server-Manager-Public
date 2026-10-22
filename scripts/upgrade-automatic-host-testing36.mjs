// Narrow Test 35 -> Test 36 update of an enrolled installer-managed Host.
// Panel, enrollment, setup worker, catalog policy and game files are never written.
import { lstat, realpath, mkdtemp, open, rename, unlink } from 'node:fs/promises';
import { constants } from 'node:fs';
import { join, dirname, resolve } from 'node:path';
import { userInfo } from 'node:os';
import { createHash, randomUUID } from 'node:crypto';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { pathToFileURL } from 'node:url';
const exec = promisify(execFile);
export const OLD = '53f28e0dc131ad83a53f13b59c8359175aa0e92b86926660adc7d83b5ef00d4e';
export const NEW = '5aa8e9e80e2cbb89419c88a005bb5c9207f09aa9932e4a43aa96879bcb8793ad';
const NODE = '/opt/bifrost-node-v24.19.0/bin/node';
const URL = 'https://github.com/troainc/Bifrost-Server-Manager-Public/releases/download/v0.1.0-installtest.36/bifrost-linux-host-agent.zip';
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
export const managedUnit = (home, digest) => `[Unit]\nDescription=Bifrost local game Host Agent\n[Service]\nExecStart=${NODE} ${home}/.local/opt/bifrost-host-agent-${digest}/dist/main.js\nEnvironment=BIFROST_HOST_AGENT_CONFIG=${home}/.config/bifrost-host-agent/host-agent.json\nRestart=on-failure\nRestartSec=10\nUMask=0077\n[Install]\nWantedBy=default.target\n`;
export const setupUnit = (home, digest) => `[Unit]\nDescription=Bifrost automatic Instance connection\n[Service]\nExecStart=${NODE} ${home}/.local/opt/bifrost-host-agent-${digest}/dist/automatic-instance-setup.js ${home}/.config/bifrost-host-agent/local-bootstrap.json\nWorkingDirectory=${home}/.local/opt/bifrost-host-agent-${digest}\nRestart=on-failure\nRestartSec=10\nUMask=0077\nNoNewPrivileges=true\n[Install]\nWantedBy=default.target\n`;
async function privatePath(path, directory = false, requirePrivate = true) {
  const s = await lstat(path);
  const forbiddenMode = directory && !requirePrivate ? 0o022 : 0o077;
  if (s.uid !== process.getuid() || s.isSymbolicLink() || (directory ? !s.isDirectory() : !s.isFile() || s.nlink !== 1) || (s.mode & forbiddenMode) || (!directory && s.size > 1048576)) throw new Error('Private path validation failed.');
  if (directory && await realpath(path) !== resolve(path)) throw new Error('Private directory traverses a link.');
}
async function privateBytes(path) {
  const fd = await open(path, constants.O_RDONLY | constants.O_NOFOLLOW);
  try {
    const s = await fd.stat();
    if (!s.isFile() || s.uid !== process.getuid() || s.nlink !== 1 || (s.mode & 0o077) || s.size > 1048576) throw new Error('Private file validation failed.');
    return await fd.readFile();
  } finally { await fd.close(); }
}
async function absent(path) {
  try { await lstat(path); } catch (e) { if (e.code === 'ENOENT') return; throw e; }
  throw new Error('Existing lock or destination requires operator review.');
}
async function ownLock(path) {
  const fd = await open(path, 'wx', 0o600);
  const owner = randomUUID(), identity = await fd.stat();
  try { await fd.writeFile(JSON.stringify({ owner, pid: process.pid })); await fd.sync(); }
  catch (error) { await fd.close(); throw error; }
  return async () => {
    try {
      const current = await lstat(path);
      if (current.ino !== identity.ino || current.dev !== identity.dev || JSON.parse(await privateBytes(path)).owner !== owner) throw new Error('Lock ownership changed; preserving it.');
      await unlink(path);
    } finally { await fd.close(); }
  };
}
async function atomic(path, bytes) {
  const temporary = `${path}.testing36-next`;
  const fd = await open(temporary, 'wx', 0o600);
  try { await fd.writeFile(bytes); await fd.sync(); } finally { await fd.close(); }
  await rename(temporary, path);
  const directory = await open(dirname(path), constants.O_RDONLY | constants.O_DIRECTORY);
  try { await directory.sync(); } finally { await directory.close(); }
}
export async function downloadMatchedPackage(fetchPackage = fetch) {
  const r = await fetchPackage(URL, { signal: AbortSignal.timeout(120000), redirect: 'follow' });
  const finalUrl = new globalThis.URL(r.url);
  if (!r.ok || !r.body || finalUrl.protocol !== 'https:' || finalUrl.username || finalUrl.password || !['github.com', 'release-assets.githubusercontent.com', 'objects.githubusercontent.com'].includes(finalUrl.hostname)) throw new Error('Matched HTTPS download failed.');
  const chunks = []; let size = 0;
  for await (const chunk of r.body) { size += chunk.length; if (size > 2 * 1024 * 1024) throw new Error('Package download bound exceeded.'); chunks.push(chunk); }
  return Buffer.concat(chunks);
}
// Verify an existing tree against every entry in the pinned archive. Fresh trees
// are extracted privately and renamed only after successful comparison.
const unpack = `import hashlib,os,pathlib,stat,sys,zipfile
archive,destination,mode=sys.argv[1:]
root=pathlib.Path(destination)
if root.resolve()!=root or root.is_symlink():raise SystemExit('Unsafe package root')
if mode=='extract':root.mkdir(mode=0o700)
seen=set();total=0;files=set()
with zipfile.ZipFile(archive) as z:
 entries=z.infolist()
 if not entries or len(entries)>10000:raise SystemExit('Package count bound')
 for entry in entries:
  name=entry.filename;p=pathlib.PurePosixPath(name);kind=stat.S_IFMT(entry.external_attr>>16)
  if not name or name.startswith('/') or '\\\\' in name or ':' in name or any(x in ('','.','..') for x in name.rstrip('/').split('/')) or name.casefold() in seen or kind not in (0,stat.S_IFDIR,stat.S_IFREG):raise SystemExit('Unsafe package member')
  seen.add(name.casefold());total+=entry.file_size
  if total>32*1024*1024 or entry.file_size>16*1024*1024:raise SystemExit('Package size bound')
  target=root.joinpath(*p.parts)
  if mode=='extract':
   if entry.is_dir():target.mkdir(mode=0o700,parents=True,exist_ok=True);continue
   target.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
   fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
   with os.fdopen(fd,'wb') as out:out.write(z.read(entry))
  current=root
  for part in p.parts:
   current=current/part
   if current.is_symlink():raise SystemExit('Linked package member')
  info=target.lstat()
  if info.st_uid!=os.getuid() or info.st_mode&0o077:raise SystemExit('Package ownership/mode')
  if entry.is_dir():
   if not stat.S_ISDIR(info.st_mode):raise SystemExit('Expected package directory')
  else:
   if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_size!=entry.file_size:raise SystemExit('Package member size/type')
   if hashlib.sha256(target.read_bytes()).digest()!=hashlib.sha256(z.read(entry)).digest():raise SystemExit('Package member differs')
   files.add(target)
 for current,dirs,names in os.walk(root,followlinks=False):
  for name in dirs:
   p=pathlib.Path(current)/name
   if p.is_symlink():raise SystemExit('Unexpected package link')
  for name in names:
   p=pathlib.Path(current)/name
   if p not in files and p!=root/'.bifrost-package-sha256':raise SystemExit('Unexpected package file')
`;
const systemctlDefault = async args => { await exec('/usr/bin/systemctl', ['--user', ...args], { timeout: 90000, maxBuffer: 4096 }); };
async function setupInactiveDefault() {
  try { const { stdout } = await exec('/usr/bin/systemctl', ['--user', 'show', 'bifrost-instance-setup.service', '-p', 'ActiveState', '--value'], { timeout: 10000, maxBuffer: 1024 }); if (stdout.trim() !== 'inactive') throw new Error('Setup worker must be inactive.'); }
  catch { throw new Error('Completed, inactive automatic setup is required.'); }
}
// Injection is for disposable import-based tests; the CLI accepts no paths,
// commands, versions, URLs or security overrides.
export async function upgradeAutomaticHost({ home = '/home/bifrost-games', node = NODE, packageBytes = downloadMatchedPackage, diagnoseOnly = false, onStage = () => {}, systemctl = systemctlDefault, setupInactive = setupInactiveDefault, waitForStartup = async () => new Promise(r => setTimeout(r, 3000)), preflight = async (root, config) => { await exec(node, [join(root, 'dist/preflight-upgrade.js'), config], { timeout: 30000, maxBuffer: 4096 }); } } = {}) {
  onStage('private-path-validation');
  const unit = join(home, '.config/systemd/user/bifrost-host-agent.service');
  const setup = join(home, '.config/systemd/user/bifrost-instance-setup.service');
  const bootstrap = join(home, '.config/bifrost-host-agent/local-bootstrap.json');
  const config = join(home, '.config/bifrost-host-agent/host-agent.json');
  const token = join(home, '.local/state/bifrost-host-agent/host.token');
  const ledger = join(home, '.local/state/bifrost-host-agent/job-ledger.json');
  await privatePath(home,true);
  for (let ancestor=dirname(home);;ancestor=dirname(ancestor)) {
    const s=await lstat(ancestor);
    if (!s.isDirectory() || s.isSymbolicLink() || ![0,process.getuid()].includes(s.uid) || ((s.mode & 0o022) && !(s.mode & 0o1000))) throw new Error('Unsafe home ancestor.');
    if (dirname(ancestor)===ancestor) break;
  }
  // mkdir -p -m 0700 applies that mode to the final directory; the installer
  // legitimately creates 0755 intermediate parents within this private home.
  for (const dir of [join(home,'.config'),join(home,'.config/systemd'),join(home,'.local'),join(home,'.local/state')]) await privatePath(dir,true,false);
  for (const dir of [dirname(unit),dirname(config),join(home,'.local/opt'),dirname(token)]) await privatePath(dir,true);
  const original = new Map();
  for (const file of [unit, setup, bootstrap, config, token]) original.set(file, await privateBytes(file));
  const oldUnit = original.get(unit), alreadyUpdated = oldUnit.equals(Buffer.from(managedUnit(home, NEW)));
  if (!alreadyUpdated && !oldUnit.equals(Buffer.from(managedUnit(home, OLD)))) throw new Error('Only the exact Test 35 automatic Host service is supported.');
  if (!original.get(setup).equals(Buffer.from(setupUnit(home, OLD)))) throw new Error('Automatic setup service differs; preserving it.');
  const state = JSON.parse(original.get(config));
  if (state.tokenFile !== token || state.ledgerFile !== ledger) throw new Error('Custom state paths require operator review.');
  await setupInactive();
  onStage('matched-package-download');
  const bytes = await packageBytes();
  if (hash(bytes) !== NEW) throw new Error('Matched Test 36 archive checksum failed.');
  const existingRoot = join(home,'.local/opt',`bifrost-host-agent-${alreadyUpdated ? NEW : OLD}`);
  await privatePath(existingRoot, true);
  // Never execute a retained candidate before comparing its entire tree with
  // the pinned archive. The verified NEW preflight validates existing state.
  onStage('existing-service-readiness');
  await systemctl(['is-active','--quiet','bifrost-host-agent.service']);
  if (diagnoseOnly) return { readOnly:true, matchedDownloadVerified:true, currentServiceActive:true, alreadyUpdated, newPackagePreflightPending:true, serviceReplacementPending:!alreadyUpdated, gameFilesChanged:false };
  const releaseUpdate = await ownLock(join(dirname(token), 'update-testing36.lock'));
  try {
    const stage = await mkdtemp(join(home,'.local/opt/.testing36-stage-'));
    const archive = join(stage, 'host.zip');
    const fd = await open(archive, 'wx', 0o600); try { await fd.writeFile(bytes); await fd.sync(); } finally { await fd.close(); }
    const packageRoot = join(home,'.local/opt',`bifrost-host-agent-${NEW}`);
    let present = false;
    try { await lstat(packageRoot); present = true; } catch (error) { if (error.code !== 'ENOENT') throw error; }
    if (present) {
      await privatePath(packageRoot, true);
      if ((await privateBytes(join(packageRoot,'.bifrost-package-sha256'))).toString().trim() !== NEW) throw new Error('Retained package marker differs.');
      await exec('/usr/bin/python3', ['-c', unpack, archive, packageRoot, 'verify'], { timeout:30000, maxBuffer:4096 });
    } else {
      const extracted = join(stage, 'package');
      await exec('/usr/bin/python3', ['-c', unpack, archive, extracted, 'extract'], { timeout:30000, maxBuffer:4096 });
      const marker = await open(join(extracted,'.bifrost-package-sha256'), 'wx', 0o600); try { await marker.writeFile(`${NEW}\n`); await marker.sync(); } finally { await marker.close(); }
      await absent(packageRoot); await rename(extracted, packageRoot);
    }
    onStage('new-compiled-preflight'); await preflight(packageRoot,config);
    for (const [file, expected] of original) if (!(await privateBytes(file)).equals(expected)) throw new Error('State changed during preparation.');
    if (alreadyUpdated) return { updatedTo:'v0.1.0-installtest.36', alreadyUpdated:true, serviceActive:true, enrollmentPreserved:true, gameFilesChanged:false, heartbeatVerificationPending:true };
    onStage('idle-ledger-lock');
    // An idle Agent briefly owns this lock while checking its queue. Allow a
    // five-second retry window; never remove or overwrite its lock.
    let releaseLedger;
    const idleDeadline=Date.now()+5000;
    for (;;) {
      try { releaseLedger=await ownLock(`${ledger}.lock`);break; }
      catch(error) {
        if (error.code!=='EEXIST' || Date.now()>=idleDeadline) throw error;
        await preflight(packageRoot,config);
        if (Date.now()>=idleDeadline) throw error;
        await new Promise(r=>setTimeout(r,250));
      }
    }
    let stopped = false, replaced = false;
    try {
      await preflight(packageRoot,config); await setupInactive();
      onStage('agent-service-stop'); await systemctl(['stop','bifrost-host-agent.service']); stopped = true;
      await preflight(packageRoot,config); await setupInactive();
      for (const [file, expected] of original) if (!(await privateBytes(file)).equals(expected)) throw new Error('State changed while stopping; preserve it for review.');
      const backup = `${unit}.before-testing36`;
      try { const backupFd = await open(backup, 'wx', 0o600); try { await backupFd.writeFile(oldUnit); await backupFd.sync(); } finally { await backupFd.close(); } }
      catch (error) { if (error.code !== 'EEXIST' || !(await privateBytes(backup)).equals(oldUnit)) throw error; }
      onStage('agent-unit-replacement'); await atomic(unit,Buffer.from(managedUnit(home,NEW))); replaced = true;
      await systemctl(['daemon-reload']); await systemctl(['start','bifrost-host-agent.service']);
      await waitForStartup(); await systemctl(['is-active','--quiet','bifrost-host-agent.service']);
      for (const [file, expected] of original) if (file !== unit && !(await privateBytes(file)).equals(expected)) throw new Error('Protected state changed during startup.');
    } catch (error) {
      if (stopped) {
        onStage('preserving-agent-recovery');
        if (replaced) {
          await systemctl(['stop','bifrost-host-agent.service']);
          if (!(await privateBytes(unit)).equals(Buffer.from(managedUnit(home,NEW)))) throw new Error('Service changed during recovery; left stopped for review.');
          await atomic(unit,oldUnit); await systemctl(['daemon-reload']);
        }
        // Do not restart against changed credentials, a running job or setup.
        for (const [file, expected] of original) if (!(await privateBytes(file)).equals(expected)) throw new Error('Protected state changed; Agent left stopped for review.');
        await preflight(packageRoot,config); await setupInactive();
        await systemctl(['start','bifrost-host-agent.service']);
      }
      throw error;
    } finally { await releaseLedger(); }
    return { updatedTo:'v0.1.0-installtest.36', serviceActive:true, enrollmentPreserved:true, previousPackagePreserved:true, gameFilesChanged:false, setupWorkerChanged:false, heartbeatVerificationPending:true };
  } finally { await releaseUpdate(); }
}
if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  let stage = 'account-and-runtime-validation';
  try {
    if (process.platform !== 'linux' || process.getuid() === 0 || userInfo().username !== 'bifrost-games' || process.execPath !== NODE || process.versions.node !== '24.19.0') throw new Error('Use the prepared game account and pinned runtime.');
    for (const path of ['/opt','/opt/bifrost-node-v24.19.0','/opt/bifrost-node-v24.19.0/bin',NODE]) {
      const s = await lstat(path); if (s.isSymbolicLink() || (path === NODE ? !s.isFile() : !s.isDirectory()) || s.uid !== 0 || (s.mode & 0o022)) throw new Error('Runtime ownership failed.');
    }
    if (process.argv.length > 3 || process.argv.length === 3 && process.argv[2] !== '--diagnose') throw new Error('Unsupported argument.');
    process.chdir('/home/bifrost-games');
    stage = 'rootless-runtime-check';
    const {stdout} = await exec('/usr/bin/podman',['info','--format','{{.Host.Security.Rootless}}'],{cwd:'/home/bifrost-games',timeout:20000,maxBuffer:4096});
    if (stdout.trim() !== 'true') throw new Error('Rootless Podman is required.');
    console.log(JSON.stringify(await upgradeAutomaticHost({diagnoseOnly:process.argv[2] === '--diagnose', onStage:value=>{stage=value;console.log(`Bifrost Host update: ${value}`);}}),null,2));
  } catch (error) {
    const allowed = new Set(['ENOENT','EACCES','EPERM','EEXIST','ENOSPC','ETIMEDOUT','ECONNREFUSED','ENOTFOUND','EAI_AGAIN','CERT_HAS_EXPIRED','UNABLE_TO_VERIFY_LEAF_SIGNATURE','UNABLE_TO_GET_ISSUER_CERT_LOCALLY','ERR_TLS_CERT_ALTNAME_INVALID','DEPTH_ZERO_SELF_SIGNED_CERT']);
    const code = allowed.has(error?.code) ? error.code : allowed.has(error?.cause?.code) ? error.cause.code : 'CHECK_REFUSED';
    console.error(`Bifrost: automatic Host update did not complete. Stage: ${stage}; code: ${code}. Credentials and game files were preserved. Do not reset or re-enroll; report this stage for review.`); process.exitCode = 1;
  }
}
