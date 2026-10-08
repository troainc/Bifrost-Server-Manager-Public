// Operator recovery of a retained, never-started Torch installer.
// --review is read-only; --apply-reviewed repeats review before scoped recovery.
// No logs, environment, credentials, file contents or full inspection are printed.
import { readFile, readdir, lstat, realpath } from 'node:fs/promises';
import { join, resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import assert from 'node:assert/strict';
const exec=promisify(execFile),home='/home/bifrost-games';
const hashes=['9408da9bac948edc3063fbd5e97019e07c99d30084d961d390d68f8191969504','be6b513956e2c89b0160e4152c87c2b926512e6e36f9e25ad220929763861178'];
const NODE='/opt/bifrost-node-v24.19.0/bin/node';
export function neverStartedFailures(state){
 // Podman init creates the OCI init process and records its PID before start.
 // A positive init PID is not proof that the installer workload has executed.
 // Keep explicit initialized/non-running flags and zero lifecycle timestamps;
 // the full OCI identity, process and sandbox checks still follow separately.
 const zeroTime=value=>typeof value==='string'&&/^0001-01-01T00:00:00(?:\.0+)?Z$/.test(value);
 const checks={Status:state?.Status==='initialized',Running:state?.Running===false,Paused:state?.Paused===false,Restarting:state?.Restarting===false,Pid:Number.isSafeInteger(state?.Pid)&&state.Pid>=0&&state.Pid<=2147483647,StartedAt:zeroTime(state?.StartedAt),FinishedAt:zeroTime(state?.FinishedAt)};
 return Object.keys(checks).filter(key=>!checks[key]);
}
export function neverStarted(state){return neverStartedFailures(state).length===0;}
export function retainedRequest(manifest){
 // canonicalProvision returns an object, as stored by the shipped Agent.
 const request=manifest?.request;
 assert.ok(request&&typeof request==='object'&&!Array.isArray(request));
 return request;
}
export async function inspectUnstarted(instanceId,digest,onStage=()=>{}){
 onStage('operator-runtime');
 assert.equal(process.platform,'linux');assert.ok(process.getuid?.()>0);assert.equal(process.execPath,NODE);
 assert.match(instanceId,/^[a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12}$/);assert.match(digest,/^sha256:[a-f0-9]{64}$/);
 onStage('protected-service-unit');const unit=join(home,'.config/systemd/user/bifrost-host-agent.service');
 const info=await lstat(unit);assert.ok(info.isFile()&&!info.isSymbolicLink()&&info.uid===process.getuid()&&info.nlink===1&&(info.mode&0o077)===0);
 const text=await readFile(unit,'utf8');
 const hash=hashes.find(hash=>text.includes(`ExecStart=${NODE} ${home}/.local/opt/bifrost-host-agent-${hash}/dist/main.js\n`));assert.ok(hash);
 onStage('matched-package');const pkg=join(home,'.local/opt',`bifrost-host-agent-${hash}`);assert.equal(await realpath(pkg),pkg);
 const {loadConfig,assertNoSymlinkDirectory}=await import(pathToFileURL(join(pkg,'dist/config.js')));
 const {readPrivateFile}=await import(pathToFileURL(join(pkg,'dist/security.js')));
 const {hostBlueprints}=await import(pathToFileURL(join(pkg,'dist/provisioning.js')));
 const {assertOciProcessConfinement,parseBifrostContainerInspection}=await import(pathToFileURL(join(pkg,'dist/provider.js')));
 const {validateProvisionRequest}=await import(pathToFileURL(join(pkg,'node_modules/@bifrost/contracts/dist/provisioning-node.js')));
 onStage('protected-host-config');const config=await loadConfig(join(home,'.config/bifrost-host-agent/host-agent.json'));assert.equal(config.profiles.length,0);assert.ok(config.provisioning);
 onStage('retained-manifest');
 const root=join(config.provisioning.root,instanceId);await assertNoSymlinkDirectory(root);
 const manifest=JSON.parse(await readPrivateFile(join(root,'provision.json'),'Retained manifest'));
 const request=retainedRequest(manifest);assert.equal(request.instanceId,instanceId);assert.equal(request.blueprintDigest,digest);
 onStage('approved-torch-recipe');
 const approved=(await hostBlueprints(config)).find(b=>b.digest===digest&&b.manifest.id==='space-engineers-1-torch');assert.ok(approved);
 validateProvisionRequest(approved.manifest,request);
 onStage('retained-profile');const b=approved.manifest,p=manifest.profile;
 assert.equal(p.instanceId,instanceId);assert.equal(p.provider,'oci');assert.equal(p.runtime,'linux-wine-container');assert.equal(p.containerName,`bifrost-${instanceId}`);assert.equal(p.instanceDataRoot,root);
 const expected={imageId:b.imageId,dataRoot:root,runAsUser:`${b.uid}:${b.gid}`,usernsMode:`keep-id:uid=${b.uid},gid=${b.gid}`,networkName:`bifrost-${instanceId}`,maxMemoryBytes:request.memoryBytes,maxMemorySwapBytes:request.memoryBytes,maxShmBytes:16777216,maxNanoCpus:request.nanoCpus,maxPids:1024,mounts:[{source:join(root,'files'),destination:'/bifrost/files',readOnly:false}],tmpfs:[{destination:'/tmp',maxSizeBytes:67108864},{destination:'/run',maxSizeBytes:16777216}],publishedPorts:request.ports.map(port=>({hostIp:config.provisioning.hostIp,hostPort:port.hostPort,containerPort:b.ports.find(p=>p.id===port.id).containerPort,protocol:b.ports.find(p=>p.id===port.id).protocol}))};
 onStage('retained-sandbox');assert.deepEqual(p.sandbox,expected);
 const temporary={...p,containerName:`bifrost-install-${instanceId}`,sandbox:{...expected,publishedPorts:[],mounts:[{source:join(root,'server'),destination:'/bifrost/server',readOnly:false},{source:join(root,'downloads'),destination:'/bifrost/downloads',readOnly:false}],tmpfs:[{destination:'/tmp',maxSizeBytes:1073741824},{destination:'/run',maxSizeBytes:16777216}]}};
 const podman=async args=>(await exec('/usr/bin/podman',args,{timeout:15000,maxBuffer:1024*1024})).stdout;
 onStage('installer-inspection');const raw=await podman(['container','inspect',temporary.containerName]);const values=JSON.parse(raw);assert.equal(values.length,1);const c=values[0];
 onStage('installer-never-started');const failedStateChecks=neverStartedFailures(c.State);if(failedStateChecks.length)throw Object.assign(new Error('Installer pre-start state was not established.'),{failedStateChecks});
 onStage('installer-oci-identity');assert.match(c.Id,/^[a-f0-9]{64}$/);assert.ok(c.OCIConfigPath.endsWith(`/overlay-containers/${c.Id}/userdata/config.json`));
 onStage('pinned-node-oci-reader');
 const confinement=await podman(['unshare',process.execPath,join(pkg,'dist/oci-confinement-reader.js'),c.OCIConfigPath,c.Id,String(process.getuid())]);
 onStage('oci-process-confinement');assertOciProcessConfinement(confinement,temporary);
 onStage('installer-container-sandbox');const inspected=parseBifrostContainerInspection(raw,temporary,true);assert.equal(inspected.state,'initialized');
 onStage('game-container-absence');
 try{await podman(['container','exists',p.containerName]);throw Error('Game exists');}catch(error){assert.equal(error.code,1);}
 onStage('retained-directory-counts');const counts={};for(const name of ['server','downloads']){await assertNoSymlinkDirectory(join(root,name));counts[name]=(await readdir(join(root,name))).length;}
 onStage('retained-lock-binding');
 const lock=JSON.parse(await readPrivateFile(join(config.provisioning.root,'.provision-lock.json'),'Provisioning lock'));assert.equal(lock.instanceId,instanceId);assert.equal(lock.blueprintDigest,digest);
 return {readOnly:true,reviewPassed:true,instanceId,approvedTorchManifest:true,initializedInstallerNeverStarted:true,installerInitPidPresent:c.State.Pid>0,fullContainerSandboxVerified:true,zeroOciCapabilitiesVerified:true,activePinnedNodeReaderWorks:true,gameContainerAbsent:true,profileCount:0,retainedLockMatches:true,retainedDirectoryEntryCounts:counts};
}
const stages=new Set(['arguments','operator-runtime','protected-service-unit','matched-package','protected-host-config','retained-manifest','approved-torch-recipe','retained-profile','retained-sandbox','installer-inspection','installer-never-started','installer-oci-identity','pinned-node-oci-reader','oci-process-confinement','installer-container-sandbox','game-container-absence','retained-directory-counts','retained-lock-binding']);
export function reviewFailure(stage,error){
 const allowedStateFields=new Set(['Status','Running','Paused','Restarting','Pid','StartedAt','FinishedAt']);
 const failedStateChecks=stage==='installer-never-started'&&Array.isArray(error?.failedStateChecks)&&error.failedStateChecks.length>0&&error.failedStateChecks.length<=7&&error.failedStateChecks.every(key=>allowedStateFields.has(key))?error.failedStateChecks:undefined;
 return {readOnly:true,reviewPassed:false,stage:stages.has(stage)?stage:'unknown-check',code:['ENOENT','EACCES','EPERM'].includes(error?.code)?error.code:'REVIEW_REFUSED',...(failedStateChecks?{failedStateChecks}:{})};
}

// Recovery additions to the separately reviewed public read-only reviewer above.
import {createHash, randomUUID} from 'node:crypto';
import {open, mkdir, rename, readlink} from 'node:fs/promises';
import {dirname, basename} from 'node:path';
import {userInfo} from 'node:os';
const RECOVERY_PACKAGE=join(home,'.local/opt',`bifrost-host-agent-${hashes[1]}`);
const CONFIG_PATH=join(home,'.config/bifrost-host-agent/host-agent.json');
const UNIT_PATH=join(home,'.config/systemd/user/bifrost-host-agent.service');
const TOKEN_PATH=join(home,'.local/state/bifrost-host-agent/host.token');
const LEDGER_PATH=join(home,'.local/state/bifrost-host-agent/job-ledger.json');
const RECOVERY_UNIT=`[Unit]\nDescription=Bifrost local game Host Agent\n[Service]\nExecStart=${NODE} ${RECOVERY_PACKAGE}/dist/main.js\nEnvironment=BIFROST_HOST_AGENT_CONFIG=${CONFIG_PATH}\nRestart=on-failure\nRestartSec=10\nUMask=0077\n[Install]\nWantedBy=default.target\n`;
const digestBytes=bytes=>createHash('sha256').update(bytes).digest('hex');
const podmanRecovery=async args=>(await exec('/usr/bin/podman',args,{timeout:15000,maxBuffer:1024*1024})).stdout;
const controlRecovery=async args=>(await exec('/usr/bin/systemctl',['--user',...args],{timeout:120000,maxBuffer:4096})).stdout;
async function recoveryBindings(){
 const {loadConfig,assertNoSymlinkDirectory}=await import(pathToFileURL(join(RECOVERY_PACKAGE,'dist/config.js')));
 const security=await import(pathToFileURL(join(RECOVERY_PACKAGE,'dist/security.js')));
 const ledger=await import(pathToFileURL(join(RECOVERY_PACKAGE,'dist/ledger-lock.js')));
 const {preflightUpgrade}=await import(pathToFileURL(join(RECOVERY_PACKAGE,'dist/preflight-upgrade.js')));
 return {config:await loadConfig(CONFIG_PATH),assertNoSymlinkDirectory,...security,...ledger,preflightUpgrade};
}
async function privateBytes(path){
 const s=await lstat(path);assert.ok(s.isFile()&&!s.isSymbolicLink()&&s.uid===process.getuid()&&s.nlink===1&&(s.mode&0o077)===0&&s.size<=1024*1024);
 return readFile(path);
}
async function controlFingerprints(){
 const result={};for(const path of [UNIT_PATH,CONFIG_PATH,TOKEN_PATH,LEDGER_PATH])result[path]=digestBytes(await privateBytes(path));return result;
}
async function treeFingerprint(root){
 const result={};let entries=0,bytes=0;
 async function visit(path){
  assert.ok(++entries<=4096);const s=await lstat(path);assert.ok(s.uid===process.getuid()&&!s.isSymbolicLink()&&(s.mode&0o077)===0);
  if(s.isDirectory()){result[path]=[s.uid,s.mode];for(const name of (await readdir(path)).sort())await visit(join(path,name));}
  else{assert.ok(s.isFile()&&s.nlink===1&&s.size<=1024*1024);bytes+=s.size;assert.ok(bytes<=32*1024*1024);result[path]=[s.uid,s.mode,digestBytes(await readFile(path))];}
 }
 await visit(root);return result;
}
async function maybeOperationRoot(bindings,root,instanceId){
 const parent=join(root,'.operations'),path=join(parent,instanceId);
 try{await lstat(parent);await bindings.assertNoSymlinkDirectory(parent);}catch(error){if(error.code==='ENOENT')return null;throw error;}
 try{await lstat(path);}catch(error){if(error.code==='ENOENT')return null;throw error;}
 await bindings.assertNoSymlinkDirectory(path);assert.deepEqual(await readdir(path),[]);await treeFingerprint(path);return path;
}
export function validateRecoveryLedger(value){
 assert.ok(value&&typeof value==='object'&&!Array.isArray(value));
 // Never erase a replay marker, running job, or unrelated completed job.
 assert.deepEqual(Object.keys(value),[]);
}
export function validateRecoveryNetwork(network,instanceId){
 assert.ok(network&&network.name===`bifrost-${instanceId}`&&/^[a-f0-9]{64}$/.test(network.id));
 assert.equal(network.labels?.['io.bifrost.instance-id'],instanceId);assert.equal(network.driver,'bridge');
 const attached=Object.hasOwn(network,'containers')?network.containers:{};assert.ok(attached&&typeof attached==='object'&&!Array.isArray(attached));
 // An initialized installer has not joined a running workload network.
 assert.deepEqual(Object.keys(attached),[]);
}
export async function planUnstartedRecovery(instanceId,digest,onStage=()=>{}){
 onStage('complete-read-only-review');const reviewed=await inspectUnstarted(instanceId,digest);
 assert.deepEqual(reviewed.retainedDirectoryEntryCounts,{server:0,downloads:0});
 onStage('testing21-bindings');const bindings=await recoveryBindings();
 const unit=await privateBytes(UNIT_PATH);assert.deepEqual(unit,Buffer.from(RECOVERY_UNIT));
 const {config}=bindings;assert.equal(config.tokenFile,TOKEN_PATH);assert.equal(config.ledgerFile,LEDGER_PATH);
 const root=config.provisioning.root;assert.ok(resolve(root).startsWith(`${home}/`)&&resolve(root)===root);
 await bindings.assertNoSymlinkDirectory(root);
 const instanceRoot=join(root,instanceId),lockPath=join(root,'.provision-lock.json');
 onStage('idle-ledger');validateRecoveryLedger(JSON.parse((await privateBytes(LEDGER_PATH)).toString()));
 onStage('retained-tree');
 assert.deepEqual((await readdir(instanceRoot)).sort(),['downloads','files','provision.json','server']);
 const tree=await treeFingerprint(instanceRoot),operationRoot=await maybeOperationRoot(bindings,root,instanceId);
 const lock=await privateBytes(lockPath);
 assert.equal(JSON.parse(lock.toString()).instanceId,instanceId);assert.equal(JSON.parse(lock.toString()).blueprintDigest,digest);
 onStage('sole-installer-identity');
 const containers=JSON.parse(await podmanRecovery(['container','inspect',`bifrost-install-${instanceId}`]));assert.equal(containers.length,1);
 const installer=containers[0];assert.ok(neverStarted(installer.State));assert.match(installer.Id,/^[a-f0-9]{64}$/);
 const all=(await podmanRecovery(['ps','--all','--external','--no-trunc','--format','{{.ID}}'])).trim().split(/\r?\n/).filter(Boolean);
 assert.deepEqual(all,[installer.Id]);
 onStage('unused-owned-network');
 const networks=JSON.parse(await podmanRecovery(['network','inspect',`bifrost-${instanceId}`]));assert.equal(networks.length,1);validateRecoveryNetwork(networks[0],instanceId);
 onStage('same-filesystem-evidence');const stateRoot=dirname(LEDGER_PATH);await bindings.assertNoSymlinkDirectory(stateRoot);
 assert.equal((await lstat(instanceRoot)).dev,(await lstat(stateRoot)).dev);
 return {summary:{readOnly:true,reviewPassed:true,recoveryReady:true,instanceId,neverStartedInstallerVerified:true,emptyInstallerDirectories:true,onlyRetainedInstallerPresent:true,ownedNetworkUnused:true,jobLedgerEmpty:true,retainedFilesWillBeArchived:true},bindings,instanceRoot,operationRoot,lockPath,lock,tree,control:await controlFingerprints(),installer,network:networks[0],unit};
}
async function assertNoOtherAgentProcess(){
 for(const name of await readdir('/proc')){
  if(!/^\d+$/.test(name)||Number(name)===process.pid)continue;const path=join('/proc',name);
  try{if((await lstat(path)).uid!==process.getuid())continue;const executable=await readlink(join(path,'exe'));
   if(!['node','nodejs'].includes(basename(executable)))continue;
   const argv=(await readFile(join(path,'cmdline'),'utf8')).split('\0');assert.ok(!argv.some(arg=>arg.endsWith('/dist/main.js')));
  }catch(error){if(['ENOENT','ESRCH'].includes(error.code))continue;throw error;}
 }
}
async function syncRecoveryDirectory(path){const fd=await open(path,'r');try{await fd.sync();}finally{await fd.close();}}
async function saveRecoveryEvidence(path,bytes){const fd=await open(path,'wx',0o600);try{await fd.writeFile(bytes);await fd.sync();}finally{await fd.close();}}
async function verifyAbsent(args){try{await podmanRecovery(args);}catch(error){assert.equal(error.code,1);return;}throw Error('Expected exact runtime absence');}
const recoveryStageNames=new Set(['arguments','runtime','complete-read-only-review','testing21-bindings','idle-ledger','retained-tree','sole-installer-identity','unused-owned-network','same-filesystem-evidence','ledger-lock','active-service','service-stop','stopped-service','stopped-full-recheck','private-evidence','final-state-recheck','installer-remove','network-remove','retained-tree-archive','lock-archive','service-restart']);
export async function recoverUnstarted(instanceId,digest,{onStage=()=>{},systemctl=controlRecovery,assertProcesses=assertNoOtherAgentProcess}={}){
 // Dependency injections are only for disposable tests, never CLI options.
 let trackedStage;const stageSink=onStage;onStage=value=>{trackedStage=value;stageSink(value);};
 const initial=await planUnstartedRecovery(instanceId,digest,onStage);
 onStage('ledger-lock');const release=await initial.bindings.acquireLedgerLock(LEDGER_PATH);assert.ok(release,'An Agent process owns the ledger lock; do not remove it.');
 let stopped=false,recovered=false,evidenceRef;
 try{
  onStage('active-service');assert.equal((await systemctl(['is-active','bifrost-host-agent.service'])).trim(),'active');
  const locked=await planUnstartedRecovery(instanceId,digest,onStage);assert.deepEqual(locked.control,initial.control);assert.deepEqual(locked.tree,initial.tree);
  onStage('service-stop');await systemctl(['stop','bifrost-host-agent.service']);stopped=true;
  onStage('stopped-service');
  const properties=Object.fromEntries((await systemctl(['show','bifrost-host-agent.service','--property=ActiveState,SubState,MainPID,ControlPID'])).trim().split(/\r?\n/).map(line=>line.split('=')));
  assert.deepEqual(properties,{ActiveState:'inactive',SubState:'dead',MainPID:'0',ControlPID:'0'});await assertProcesses();
  onStage('stopped-full-recheck');const current=await planUnstartedRecovery(instanceId,digest,onStage);
  assert.deepEqual(current.control,initial.control);assert.deepEqual(current.tree,initial.tree);assert.equal(current.installer.Id,initial.installer.Id);assert.equal(current.network.id,initial.network.id);assert.deepEqual(current.lock,initial.lock);
  onStage('private-evidence');const evidenceParent=join(dirname(LEDGER_PATH),'recovery');await current.bindings.ensurePrivateStateDirectory(evidenceParent);
  evidenceRef=`${instanceId}-${randomUUID()}`;const evidence=join(evidenceParent,evidenceRef);await mkdir(evidence,{mode:0o700});
  for(const [name,bytes] of [['service-unit',current.unit],['host-config',await privateBytes(CONFIG_PATH)],['job-ledger',await privateBytes(LEDGER_PATH)],['container-inspection',Buffer.from(JSON.stringify(current.installer))],['network-inspection',Buffer.from(JSON.stringify(current.network))]])await saveRecoveryEvidence(join(evidence,name),bytes);
  await syncRecoveryDirectory(evidence);await syncRecoveryDirectory(evidenceParent);
  onStage('final-state-recheck');const final=await planUnstartedRecovery(instanceId,digest,onStage);assert.deepEqual(final.control,initial.control);assert.deepEqual(final.tree,initial.tree);assert.equal(final.installer.Id,current.installer.Id);assert.equal(final.network.id,current.network.id);
  onStage('installer-remove');await podmanRecovery(['rm','--force',current.installer.Id]);await verifyAbsent(['container','exists',current.installer.Id]);await verifyAbsent(['container','exists',`bifrost-${instanceId}`]);
  onStage('network-remove');assert.equal((await podmanRecovery(['ps','--all','--external','--no-trunc','--format','{{.ID}}'])).trim(),'');
  const networks=JSON.parse(await podmanRecovery(['network','inspect',`bifrost-${instanceId}`]));assert.equal(networks.length,1);validateRecoveryNetwork(networks[0],instanceId);assert.equal(networks[0].id,current.network.id);
  await podmanRecovery(['network','rm',current.network.id]);await verifyAbsent(['network','exists',`bifrost-${instanceId}`]);
  onStage('retained-tree-archive');assert.deepEqual(await controlFingerprints(),initial.control);assert.deepEqual(await treeFingerprint(current.instanceRoot),initial.tree);assert.deepEqual(await privateBytes(current.lockPath),initial.lock);
  await rename(current.instanceRoot,join(evidence,'instance'));await syncRecoveryDirectory(dirname(current.instanceRoot));await syncRecoveryDirectory(evidence);
  if(current.operationRoot){assert.deepEqual(await readdir(current.operationRoot),[]);await rename(current.operationRoot,join(evidence,'operations'));await syncRecoveryDirectory(dirname(current.operationRoot));await syncRecoveryDirectory(evidence);}
  onStage('lock-archive');assert.deepEqual(await privateBytes(current.lockPath),initial.lock);await rename(current.lockPath,join(evidence,'provision-lock.json'));await syncRecoveryDirectory(dirname(current.lockPath));await syncRecoveryDirectory(evidence);
  recovered=true;
 }catch(error){error.recoveryStage=trackedStage;error.recoveryEvidenceRef=evidenceRef;error.runtimeRecoveryCompleted=recovered;throw error;}finally{
  await release();
  if(stopped){onStage('service-restart');try{assert.deepEqual(await controlFingerprints(),initial.control);await initial.bindings.preflightUpgrade(CONFIG_PATH);await systemctl(['start','bifrost-host-agent.service']);assert.equal((await systemctl(['is-active','bifrost-host-agent.service'])).trim(),'active');}catch(error){error.recoveryStage='service-restart';error.recoveryEvidenceRef=evidenceRef;error.runtimeRecoveryCompleted=recovered;throw error;}}
 }
 return {recoveryCompleted:recovered,instanceId,serviceActive:true,enrollmentPreserved:true,configurationPreserved:true,jobLedgerUnchanged:true,retainedFilesArchived:true,evidenceRef,controllerReconciliationPending:true,gameRetryQueued:false};
}
export function recoveryFailure(stage,error,applyRequested=false){
 const failureStage=error?.recoveryStage??stage;
 const evidenceRef=typeof error?.recoveryEvidenceRef==='string'&&/^[a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12}-[a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12}$/.test(error.recoveryEvidenceRef)?error.recoveryEvidenceRef:undefined;
 return {readOnly:!applyRequested,recoveryCompleted:false,stage:recoveryStageNames.has(failureStage)?failureStage:'complete-read-only-review',code:['ENOENT','EACCES','EPERM','ENOSPC'].includes(error?.code)?error.code:'RECOVERY_REFUSED',...(applyRequested?{runtimeRecoveryCompleted:error?.runtimeRecoveryCompleted===true,serviceStateVerificationRequired:true}:{}),...(evidenceRef?{evidenceRef}:{})};
}
if(process.argv[1]==='-'||process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href){
 let stage='arguments',applyRequested=false;
 try{
  assert.equal(process.argv.length,5);const [mode,instanceId,digest]=process.argv.slice(2);assert.ok(['--review','--apply-reviewed'].includes(mode));applyRequested=mode==='--apply-reviewed';
  stage='runtime';assert.equal(userInfo().username,'bifrost-games');assert.equal(process.execPath,NODE);assert.equal(process.versions.node,'24.19.0');assert.ok(process.getuid()>0);
  for(const path of ['/opt','/opt/bifrost-node-v24.19.0','/opt/bifrost-node-v24.19.0/bin',NODE]){const s=await lstat(path);assert.ok(!s.isSymbolicLink()&&(path===NODE?s.isFile():s.isDirectory())&&s.uid===0&&(s.mode&0o022)===0);}
  const onStage=value=>{stage=value;};const result=mode==='--review'?(await planUnstartedRecovery(instanceId,digest,onStage)).summary:await recoverUnstarted(instanceId,digest,{onStage});console.log(JSON.stringify(result,null,2));
 }catch(error){console.log(JSON.stringify(recoveryFailure(stage,error,applyRequested)));process.exitCode=1;}
}
