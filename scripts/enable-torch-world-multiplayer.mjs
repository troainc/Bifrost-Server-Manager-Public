// Explicit repair of an existing, stopped Torch world's multiplayer setting.
// Leaves lifecycle control with the Controller. Never prints config, tokens or logs.
import assert from 'node:assert/strict';
import {readFile, lstat, realpath, open, mkdir, rename, unlink} from 'node:fs/promises';
import {join, dirname, resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash, randomUUID} from 'node:crypto';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {userInfo} from 'node:os';
import {constants} from 'node:fs';

const home='/home/bifrost-games', node='/opt/bifrost-node-v24.19.0/bin/node';
const packageHash='be6b513956e2c89b0160e4152c87c2b926512e6e36f9e25ad220929763861178';
const pkg=join(home,'.local/opt',`bifrost-host-agent-${packageHash}`);
const configPath=join(home,'.config/bifrost-host-agent/host-agent.json');
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const exec=promisify(execFile);
const podman=async args=>(await exec('/usr/bin/podman',args,{timeout:15000,maxBuffer:1024*1024})).stdout;

export function publicWorldSetting(bytes){
  const text=bytes.toString('utf8');
  assert.ok(Buffer.from(text).equals(bytes),'World XML must be UTF-8.');
  assert.ok(!/<!DOCTYPE|<!ENTITY/i.test(text)&&![...text.matchAll(/<!--[\s\S]*?-->/g)].some(match=>match[0].includes('<OnlineMode>')),'Ambiguous XML settings.');
  const tags=[...text.matchAll(/<OnlineMode>\s*([^<]+?)\s*<\/OnlineMode>/g)];
  assert.equal(tags.length,1,'Expected exactly one world OnlineMode.');
  const before=tags[0][1].trim();
  assert.ok(['OFFLINE','PUBLIC'].includes(before),'Only an offline/public test world may be repaired.');
  const after=before==='PUBLIC'?bytes:Buffer.from(text.replace(/(<OnlineMode>\s*)OFFLINE(\s*<\/OnlineMode>)/,'$1PUBLIC$2'));
  assert.equal(after.toString().match(/<OnlineMode>\s*([^<]+?)\s*<\/OnlineMode>/)[1].trim(),'PUBLIC');
  return {before,after};
}

async function directory(path){
  assert.equal(await realpath(path),resolve(path),'Directory path must not traverse links.');
  const info=await lstat(path);assert.ok(info.isDirectory()&&!info.isSymbolicLink());
  assert.equal(info.uid,process.getuid());assert.equal(info.mode&0o022,0);
}
async function worldFile(path){
  await directory(dirname(path));const info=await lstat(path);
  assert.ok(info.isFile()&&!info.isSymbolicLink()&&info.nlink===1&&info.size>0&&info.size<=64*1024*1024);
  assert.equal(info.uid,process.getuid());assert.equal(info.mode&0o022,0);
  const handle=await open(path,constants.O_RDONLY|constants.O_NOFOLLOW);
  try{const current=await handle.stat();assert.equal(current.ino,info.ino);assert.equal(current.dev,info.dev);return {bytes:await handle.readFile(),mode:info.mode&0o777};}
  finally{await handle.close();}
}
async function writeNew(path,bytes,mode=0o600){
  const handle=await open(path,'wx',mode);try{await handle.writeFile(bytes);await handle.chmod(mode);await handle.sync();}finally{await handle.close();}
}
async function syncDirectory(path){const handle=await open(path,'r');try{await handle.sync();}finally{await handle.close();}}

export async function repairWorldFiles(world,evidenceRoot,guard){
  await directory(world);const entries=[];
  for(const name of ['Sandbox.sbc','Sandbox_config.sbc']){
    const path=join(world,name),original=await worldFile(path),patch=publicWorldSetting(original.bytes);
    entries.push({name,path,...original,...patch});
  }
  await guard();
  if(entries.every(entry=>entry.before==='PUBLIC'))return {repairCompleted:true,alreadyPublic:true,worldFiles:entries.map(entry=>({file:entry.name,before:entry.before,after:'PUBLIC'}))};
  const backupRef=randomUUID(),evidence=join(evidenceRoot,backupRef),temporary=[],written=[];
  await mkdir(evidence,{mode:0o700});await directory(evidence);
  try{
    for(const entry of entries)await writeNew(join(evidence,entry.name),entry.bytes);
    await writeNew(join(evidence,'repair.json'),Buffer.from(JSON.stringify({worldFiles:entries.map(entry=>({file:entry.name,originalSha256:sha(entry.bytes),replacementSha256:sha(entry.after),mode:entry.mode})),createdAt:new Date().toISOString()})));
    await syncDirectory(evidence);await syncDirectory(evidenceRoot);
    for(const entry of entries){
      assert.equal(sha((await worldFile(entry.path)).bytes),sha(entry.bytes),'World changed during preparation.');
      if(entry.before==='PUBLIC')continue;
      const path=join(world,`.bifrost-online-${backupRef}-${entry.name}`);await writeNew(path,entry.after,entry.mode);temporary.push(path);entry.temporary=path;
    }
    for(const entry of entries){
      await guard();assert.equal(sha((await worldFile(entry.path)).bytes),sha(entry.bytes),'World changed before replacement.');
      if(entry.temporary){await rename(entry.temporary,entry.path);written.push(entry);await syncDirectory(world);}
    }
    await guard();for(const entry of entries)assert.equal(sha((await worldFile(entry.path)).bytes),sha(entry.after));
    return {repairCompleted:true,originalWorldFilesPreserved:true,backupRef,worldFiles:entries.map(entry=>({file:entry.name,before:entry.before,after:'PUBLIC'}))};
  }catch(error){
    let rollbackCompleted=true;
    try{
      await guard();
      for(const entry of written.reverse()){
        assert.equal(sha((await worldFile(entry.path)).bytes),sha(entry.after),'Refusing to overwrite a concurrent world change.');
        const path=join(world,`.bifrost-rollback-${backupRef}-${entry.name}`);temporary.push(path);await writeNew(path,entry.bytes,entry.mode);await rename(path,entry.path);await syncDirectory(world);
      }
    }catch{rollbackCompleted=false;}
    throw Object.assign(error,{backupRef,rollbackCompleted});
  }finally{for(const path of temporary)await unlink(path).catch(error=>{if(error.code!=='ENOENT')throw error;});}
}

export async function enableStoppedTorchWorld(instanceId,digest,onStage=()=>{}){
  onStage('operator-runtime');assert.equal(process.platform,'linux');assert.equal(process.execPath,node);assert.ok(process.getuid()>0);assert.equal(userInfo().username,'bifrost-games');
  assert.match(instanceId,/^[a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12}$/);assert.match(digest,/^sha256:[a-f0-9]{64}$/);
  onStage('protected-agent-package');assert.equal(await realpath(pkg),pkg);
  const unit=await readFile(join(home,'.config/systemd/user/bifrost-host-agent.service'),'utf8');assert.ok(unit.includes(`ExecStart=${node} ${pkg}/dist/main.js\n`));
  const {loadConfig,assertNoSymlinkDirectory}=await import(pathToFileURL(join(pkg,'dist/config.js')));
  const {readPrivateFile,ensurePrivateStateDirectory}=await import(pathToFileURL(join(pkg,'dist/security.js')));
  const {hostBlueprints}=await import(pathToFileURL(join(pkg,'dist/provisioning.js')));
  const {inspectBifrostContainer}=await import(pathToFileURL(join(pkg,'dist/provider.js')));
  const {acquireLedgerLock}=await import(pathToFileURL(join(pkg,'dist/ledger-lock.js')));
  onStage('active-profile');const configBytes=await readPrivateFile(configPath,'Host config'),config=await loadConfig(configPath);
  const profiles=config.profiles.filter(profile=>profile.instanceId===instanceId);assert.equal(profiles.length,1);const profile=profiles[0];
  assert.equal(profile.provider,'oci');assert.equal(profile.runtime,'linux-wine-container');assert.equal(profile.containerName,`bifrost-${instanceId}`);
  assert.equal(profile.instanceDataRoot,join(config.provisioning.root,instanceId));assert.equal(profile.instanceFilesRoot,join(profile.instanceDataRoot,'files'));
  onStage('approved-torch-world');const approved=(await hostBlueprints(config)).find(entry=>entry.digest===digest&&entry.manifest.id==='space-engineers-1-torch');assert.ok(approved);assert.equal(profile.sandbox.imageId,approved.manifest.imageId);
  await assertNoSymlinkDirectory(profile.instanceFilesRoot);
  const manifest=JSON.parse(await readPrivateFile(join(profile.instanceDataRoot,'provision.json'),'Provisioning manifest'));assert.equal(manifest.request.instanceId,instanceId);assert.equal(manifest.request.blueprintDigest,digest);
  const dedicated=await worldFile(join(profile.instanceFilesRoot,'Instance/SpaceEngineers-Dedicated.cfg'));assert.equal(publicWorldSetting(dedicated.bytes).before,'PUBLIC');
  onStage('exclusive-agent-ledger');const release=await acquireLedgerLock(config.ledgerFile);assert.ok(release,'Agent is busy; leave its lock intact.');
  try{
    const ledger=JSON.parse(await readPrivateFile(config.ledgerFile,'Job ledger'));assert.ok(!Object.values(ledger).includes('running'),'Agent has an unfinished job.');
    let containerId;
    const guard=async()=>{
      onStage('stopped-runtime');assert.equal(sha(await readPrivateFile(configPath,'Host config')),sha(configBytes));
      const raw=await podman(['container','inspect',profile.containerName]);const containers=JSON.parse(raw);assert.equal(containers.length,1);const state=containers[0].State;
      assert.ok(['exited','stopped'].includes(state.Status)&&state.Running===false&&state.Paused===false&&state.Restarting===false&&state.Pid===0,'Stop the exact game before repairing its world.');
      const verified=await inspectBifrostContainer(raw,profile);assert.match(verified.id,/^[a-f0-9]{64}$/);if(containerId)assert.equal(verified.id,containerId);else containerId=verified.id;
    };
    await guard();const world=join(profile.instanceFilesRoot,'Instance/Saves/BifrostWorld');await assertNoSymlinkDirectory(world);
    const evidenceRoot=join(home,'.local/state/bifrost-host-agent/world-multiplayer-repairs');await ensurePrivateStateDirectory(evidenceRoot);
    onStage('preserved-world-settings');const result=await repairWorldFiles(world,evidenceRoot,guard);
    return {...result,instanceId,gameStopped:true,hostConfigurationPreserved:true,gameStartQueued:false};
  }finally{await release();}
}
if(process.argv[2]){
  let stage='arguments';
  try{assert.equal(process.argv.length,5);assert.equal(process.argv[2],'--enable-stopped-world');const result=await enableStoppedTorchWorld(process.argv[3],process.argv[4],value=>{stage=value;});console.log(JSON.stringify(result,null,2));}
  catch(error){console.log(JSON.stringify({repairCompleted:false,stage,code:['ENOENT','EACCES','EPERM','EEXIST'].includes(error.code)?error.code:'REPAIR_REFUSED',...(error.backupRef?{backupRef:error.backupRef,rollbackCompleted:error.rollbackCompleted}:{})}));process.exitCode=1;}
}
