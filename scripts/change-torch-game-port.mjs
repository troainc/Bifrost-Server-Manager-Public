// Operator-requested port change for a committed testing21 Torch instance.
// Retains the original stopped container and private configuration backups.
import assert from 'node:assert/strict';
import {readFile,lstat,realpath,open,rename,unlink,mkdir} from 'node:fs/promises';
import {join,dirname,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {createHash,randomUUID} from 'node:crypto';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {userInfo} from 'node:os';
import {constants} from 'node:fs';

const home='/home/bifrost-games',node='/opt/bifrost-node-v24.19.0/bin/node';
const pkg=join(home,'.local/opt/bifrost-host-agent-be6b513956e2c89b0160e4152c87c2b926512e6e36f9e25ad220929763861178');
const configPath=join(home,'.config/bifrost-host-agent/host-agent.json');
const service='bifrost-host-agent.service',exec=promisify(execFile);
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const run=async(executable,args,timeout=20000)=>{
  try{return (await exec(executable,args,{cwd:'/',timeout,maxBuffer:1024*1024})).stdout;}
  catch(error){error.failedCommand=executable==='/usr/bin/systemctl'?`service-${args[1]}`:executable==='/usr/bin/podman'?`podman-${args[0]}`:'runtime-command';if(typeof error.code==='number')error.commandExit=error.code;if(error.killed)error.commandTimedOut=true;throw error;}
};
const podman=(args,timeout)=>run('/usr/bin/podman',args,timeout);
const systemctl=async args=>{
  try{return await run('/usr/bin/systemctl',['--user',...args],120000);}
  catch(error){if(error.killed)error.portCode='SERVICE_TIMEOUT';throw error;}
};
const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));

export function changeServerPort(bytes,oldPort,newPort){
  const text=bytes.toString('utf8');assert.ok(Buffer.from(text).equals(bytes));
  assert.ok(!/<!DOCTYPE|<!ENTITY/i.test(text));
  assert.ok(![...text.matchAll(/<!--[\s\S]*?-->/g)].some(match=>match[0].includes('<ServerPort>')));
  const tags=[...text.matchAll(/<ServerPort>\s*(\d+)\s*<\/ServerPort>/g)];
  assert.equal(tags.length,1);assert.equal(Number(tags[0][1]),oldPort);
  assert.ok(Number.isInteger(newPort)&&newPort>=1024&&newPort<=65535);
  return Buffer.from(text.replace(/(<ServerPort>\s*)\d+(\s*<\/ServerPort>)/,`$1${newPort}$2`));
}
export function changeProfilePort(original,oldPort,newPort){
  const profile=structuredClone(original),ports=profile.sandbox.publishedPorts;
  const game=ports.filter(port=>port.protocol==='udp'&&port.hostPort===oldPort&&port.containerPort===oldPort);
  assert.equal(game.length,1);assert.ok(!ports.some(port=>port.hostPort===newPort||port.containerPort===newPort));
  game[0].hostPort=newPort;game[0].containerPort=newPort;
  for(const item of profile.operations?.packages??[]){
    const binding=item.blueprint;if(!binding)continue;assert.equal(binding.id,'space-engineers-1-torch');
    if(binding.schemaVersion){const allocated=binding.ports.filter(port=>port.id==='game');assert.equal(allocated.length,1);assert.equal(allocated[0].port,oldPort);allocated[0].port=newPort;}
    else{assert.equal(binding.gamePort,oldPort);binding.gamePort=newPort;}
  }
  return profile;
}
async function safeFile(path){
  assert.equal(await realpath(dirname(path)),resolve(dirname(path)));
  const info=await lstat(path);assert.ok(info.isFile()&&!info.isSymbolicLink()&&info.nlink===1&&info.size<=4*1024*1024);
  assert.equal(info.uid,process.getuid());assert.equal(info.mode&0o022,0);
  const handle=await open(path,constants.O_RDONLY|constants.O_NOFOLLOW);
  try{const current=await handle.stat();assert.equal(current.ino,info.ino);assert.equal(current.dev,info.dev);return {path,bytes:await handle.readFile(),mode:info.mode&0o777};}finally{await handle.close();}
}
async function writeNew(path,bytes,mode=0o600){const handle=await open(path,'wx',mode);try{await handle.writeFile(bytes);await handle.chmod(mode);await handle.sync();}finally{await handle.close();}}
async function syncDir(path){const handle=await open(path,'r');try{await handle.sync();}finally{await handle.close();}}
async function replaceFile(entry,expected,replacement,validate=async()=>{}){
  assert.equal(hash((await safeFile(entry.path)).bytes),hash(expected),'Concurrent configuration change.');
  const next=`${entry.path}.${randomUUID()}.next`;
  try{await writeNew(next,replacement,entry.mode);await validate(next);assert.equal(hash((await safeFile(entry.path)).bytes),hash(expected));await rename(next,entry.path);await syncDir(dirname(entry.path));}finally{await unlink(next).catch(error=>{if(error.code!=='ENOENT')throw error;});}
}
export async function changeTorchPort(instanceId,digest,newPort,report=()=>{}){
  let stage='operator-runtime';const at=value=>{stage=value;report({stage:value});};
  assert.equal(process.platform,'linux');assert.equal(process.execPath,node);assert.ok(process.getuid()>0);assert.equal(userInfo().username,'bifrost-games');
  assert.match(instanceId,/^[a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12}$/);assert.match(digest,/^sha256:[a-f0-9]{64}$/);
  assert.ok(Number.isInteger(newPort)&&newPort>=1024&&newPort<=65535&&newPort!==8766);
  at('protected-agent-package');assert.equal(await realpath(pkg),pkg);
  const unit=await readFile(join(home,'.config/systemd/user',service),'utf8');assert.ok(unit.includes(`ExecStart=${node} ${pkg}/dist/main.js\n`));
  const {loadConfig,assertNoSymlinkDirectory}=await import(pathToFileURL(join(pkg,'dist/config.js')));
  const {readPrivateFile,ensurePrivateStateDirectory}=await import(pathToFileURL(join(pkg,'dist/security.js')));
  const {hostBlueprints,createContainerArguments}=await import(pathToFileURL(join(pkg,'dist/provisioning.js')));
  const {inspectBifrostContainer}=await import(pathToFileURL(join(pkg,'dist/provider.js')));
  const {acquireLedgerLock}=await import(pathToFileURL(join(pkg,'dist/ledger-lock.js')));
  at('committed-profile');const configEntry=await safeFile(configPath),config=await loadConfig(configPath);
  const profiles=config.profiles.filter(profile=>profile.instanceId===instanceId);assert.equal(profiles.length,1);const oldProfile=profiles[0];
  assert.equal(oldProfile.provider,'oci');assert.equal(oldProfile.runtime,'linux-wine-container');assert.equal(oldProfile.containerName,`bifrost-${instanceId}`);
  assert.equal(oldProfile.instanceDataRoot,join(config.provisioning.root,instanceId));assert.equal(oldProfile.instanceFilesRoot,join(oldProfile.instanceDataRoot,'files'));
  await assertNoSymlinkDirectory(oldProfile.instanceFilesRoot);
  const approved=(await hostBlueprints(config)).find(item=>item.digest===digest&&item.manifest.id==='space-engineers-1-torch');assert.ok(approved);const blueprint=approved.manifest;
  assert.equal(oldProfile.sandbox.imageId,blueprint.imageId);assert.deepEqual(blueprint.args,[]);
  const raw=await podman(['container','inspect',oldProfile.containerName]);const oldRuntime=await inspectBifrostContainer(raw,oldProfile);assert.match(oldRuntime.id,/^[a-f0-9]{64}$/);
  assert.ok(['running','exited','stopped'].includes(oldRuntime.state));
  const game=oldProfile.sandbox.publishedPorts.filter(port=>port.protocol==='udp'&&port.containerPort!==8766);assert.equal(game.length,1);assert.equal(game[0].hostPort,game[0].containerPort);const oldPort=game[0].hostPort;
  const dedicated=await safeFile(join(oldProfile.instanceFilesRoot,'Instance/SpaceEngineers-Dedicated.cfg'));
  if(oldPort===newPort){changeServerPort(dedicated.bytes,oldPort,newPort);return {portChanged:true,alreadyConfigured:true,gamePort:newPort};}
  assert.ok(!config.profiles.some(profile=>profile!==oldProfile&&profile.sandbox?.publishedPorts.some(port=>port.hostPort===newPort&&port.protocol==='udp')));
  for(const path of ['/proc/net/udp','/proc/net/udp6']){
    const sockets=await readFile(path,'utf8');assert.ok(!sockets.split('\n').slice(1).some(line=>Number.parseInt(line.trim().split(/\s+/)[1]?.split(':')[1]??'',16)===newPort),'Requested UDP port is already occupied.');
  }
  const replacement=changeProfilePort(oldProfile,oldPort,newPort),nextConfig=structuredClone(config);nextConfig.profiles[nextConfig.profiles.findIndex(profile=>profile.instanceId===instanceId)]=replacement;
  const entries=[{...dedicated,after:changeServerPort(dedicated.bytes,oldPort,newPort)}];
  for(const name of ['provision.json','activated-profile.json']){
    const entry=await safeFile(join(oldProfile.instanceDataRoot,name)),record=JSON.parse(entry.bytes);
    assert.equal(record.request.instanceId,instanceId);assert.equal(record.request.blueprintDigest,digest);assert.equal(record.profile.instanceId,instanceId);assert.equal(record.profile.sandbox.imageId,blueprint.imageId);
    record.profile=changeProfilePort(record.profile,oldPort,newPort);entries.push({...entry,after:Buffer.from(JSON.stringify(record,null,2))});
  }
  entries.push({...configEntry,after:Buffer.from(JSON.stringify(nextConfig,null,2)),validate:loadConfig});
  const tokenHash=hash(await readPrivateFile(config.tokenFile,'Enrollment token')),ledgerHash=hash(await readPrivateFile(config.ledgerFile,'Agent ledger'));
  assert.equal((await systemctl(['is-active',service])).trim(),'active');
  at('exclusive-agent-ledger');const release=await acquireLedgerLock(config.ledgerFile);assert.ok(release,'Agent is busy; preserve its lock.');
  const backupRef=randomUUID(),retainedName=`bifrost-port-backup-${instanceId}-${backupRef}`;
  let agentStopped=false,renameAttempted=false,newAttempted=false,newId,committed=false,backupSaved=false,failure;
  try{
    assert.equal(hash(await readPrivateFile(config.ledgerFile,'Agent ledger')),ledgerHash);
    assert.ok(!Object.values(JSON.parse(await readPrivateFile(config.ledgerFile,'Agent ledger'))).includes('running'));
    at('preserving-control-state');const evidenceRoot=join(home,'.local/state/bifrost-host-agent/port-changes');await ensurePrivateStateDirectory(evidenceRoot);const evidence=join(evidenceRoot,backupRef);await mkdir(evidence,{mode:0o700});await ensurePrivateStateDirectory(evidence);
    for(const [index,entry] of entries.entries())await writeNew(join(evidence,`${index}.original`),entry.bytes,entry.mode);
    await writeNew(join(evidence,'change.json'),Buffer.from(JSON.stringify({instanceId,oldPort,newPort,oldContainerId:oldRuntime.id,retainedName,files:entries.map(entry=>({path:entry.path,originalSha256:hash(entry.bytes),replacementSha256:hash(entry.after)}))},null,2)));await syncDir(evidence);await syncDir(evidenceRoot);backupSaved=true;
    at('stopping-game');if(oldRuntime.state==='running')await podman(['stop','--time','60',oldRuntime.id],90000);
    at('inspecting-stopped-game');const stoppedRaw=await podman(['container','inspect',oldRuntime.id]),stopped=JSON.parse(stoppedRaw)[0].State;
    at('verifying-stopped-container');await inspectBifrostContainer(stoppedRaw,oldProfile);
    at('verifying-stopped-state');
    assert.ok(['exited','stopped'].includes(stopped.Status)&&stopped.Running===false&&stopped.Paused===false&&stopped.Restarting===false&&stopped.Pid===0);
    // Quiesce the workload while its original user-service context still exists.
    // The ledger lock already prevents the Agent from leasing another action.
    at('stopping-agent');agentStopped=true;await systemctl(['stop',service]);
    // Torch may persist its dedicated config during graceful shutdown. Preserve
    // those final bytes; only its ServerPort changes.
    entries[0]={...await safeFile(dedicated.path)};entries[0].after=changeServerPort(entries[0].bytes,oldPort,newPort);
    await writeNew(join(evidence,'dedicated-stopped.original'),entries[0].bytes,entries[0].mode);
    at('updating-port-state');for(const entry of entries)await replaceFile(entry,entry.bytes,entry.after,entry.validate);
    await loadConfig(configPath);
    at('retaining-original-container');renameAttempted=true;await podman(['rename',oldRuntime.id,retainedName]);
    at('creating-replacement-container');const args=createContainerArguments(replacement,blueprint.executable,[]);args.splice(args.indexOf('--entrypoint'),0,'--workdir','/bifrost/files');newAttempted=true;
    newId=(await podman(args)).trim();assert.match(newId,/^[a-f0-9]{64}$/);await podman(['init',newId]);await inspectBifrostContainer(await podman(['container','inspect',newId]),replacement);
    at('starting-game');await podman(['start',newId]);const deadline=Date.now()+blueprint.readiness.timeoutSeconds*1000;let ready=false,lastReport=Date.now();
    while(Date.now()<deadline){
      const inspected=await inspectBifrostContainer(await podman(['container','inspect',newId]),replacement);assert.equal(inspected.id,newId);assert.equal(inspected.state,'running');
      const logs=await podman(['logs','--tail','200',newId]);if(logs.includes(blueprint.readiness.marker)){ready=true;break;}
      if(Date.now()-lastReport>=30000){report({stage:'waiting-for-game-readiness'});lastReport=Date.now();}await wait(2000);
    }
    assert.ok(ready,'Game readiness timeout.');assert.equal(hash(await readPrivateFile(config.tokenFile,'Enrollment token')),tokenHash);assert.equal(hash(await readPrivateFile(config.ledgerFile,'Agent ledger')),ledgerHash);committed=true;
    at('restarting-agent');await systemctl(['start',service]);assert.equal((await systemctl(['is-active',service])).trim(),'active');agentStopped=false;
    return {portChanged:true,gameReady:true,gamePort:newPort,containerPort:newPort,serviceActive:true,worldPreserved:true,enrollmentPreserved:true,jobLedgerUnchanged:true,originalContainerRetained:true,backupRef,heartbeatVerificationPending:true};
  }catch(error){
    const failureStage=stage;
    let rollbackCompleted=!backupSaved;
    if(!committed&&backupSaved){try{
      at('rolling-back');
      if(newAttempted){let raw;try{raw=await podman(['container','inspect',replacement.containerName]);}catch(failure){if(failure.code!==1&&failure.code!==125)throw failure;}
        if(raw){const verified=await inspectBifrostContainer(raw,replacement);if(newId)assert.equal(verified.id,newId);await podman(['stop','--time','60',verified.id],90000);await podman(['rm',verified.id]);}
      }
      if(renameAttempted){const original=JSON.parse(await podman(['container','inspect',oldRuntime.id]))[0];const name=original.Name?.replace(/^\//,'');assert.ok([oldProfile.containerName,retainedName].includes(name));if(name===retainedName)await podman(['rename',oldRuntime.id,oldProfile.containerName]);}
      for(const entry of [...entries].reverse()){const current=hash((await safeFile(entry.path)).bytes);if(current===hash(entry.after))await replaceFile(entry,entry.after,entry.bytes,entry.validate);else assert.equal(current,hash(entry.bytes),'Concurrent change prevents rollback.');}
      await loadConfig(configPath);const restored=await inspectBifrostContainer(await podman(['container','inspect',oldRuntime.id]),oldProfile);if(oldRuntime.state==='running'&&restored.state!=='running')await podman(['start',oldRuntime.id]);rollbackCompleted=true;
    }catch{rollbackCompleted=false;}}
    failure=Object.assign(error,{stage:failureStage,rollbackCompleted,committed,backupRef:backupSaved?backupRef:undefined});throw failure;
  }finally{
    let cleanupError;
    try{await release();}catch(error){if(failure)failure.ledgerReleaseCompleted=false;else cleanupError=Object.assign(error,{stage:'ledger-release',backupRef,committed});}
    if(agentStopped){try{await systemctl(['start',service]);assert.equal((await systemctl(['is-active',service])).trim(),'active');if(failure)failure.serviceRestored=true;}catch(error){if(failure)failure.serviceRestored=false;else cleanupError=Object.assign(error,{stage:'service-restart',backupRef,committed});}}
    if(cleanupError)throw cleanupError;
  }
}
if(process.argv[2]){
  try{assert.equal(process.argv.length,6);assert.equal(process.argv[2],'--set-game-port');const result=await changeTorchPort(process.argv[3],process.argv[4],Number(process.argv[5]),report=>console.log(JSON.stringify(report)));console.log(JSON.stringify(result,null,2));}
  catch(error){console.log(JSON.stringify({portChanged:false,stage:error.stage??'preflight',code:error.portCode==='SERVICE_TIMEOUT'?'SERVICE_TIMEOUT':['ENOENT','EACCES','EPERM','EEXIST'].includes(error.code)?error.code:'PORT_CHANGE_REFUSED',...(error.backupRef?{backupRef:error.backupRef,rollbackCompleted:error.rollbackCompleted,committed:error.committed}:{}),...(error.failedCommand?{failedCommand:error.failedCommand}:{}),...(error.commandExit===undefined?{}:{commandExit:error.commandExit}),...(error.commandTimedOut?{commandTimedOut:true}:{}),...(error.serviceRestored===undefined?{}:{serviceRestored:error.serviceRestored}),...(error.ledgerReleaseCompleted===undefined?{}:{ledgerReleaseCompleted:error.ledgerReleaseCompleted})}));process.exitCode=1;}
}
