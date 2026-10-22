// Real published Test 35/36 archives and compiled preflights; disposable Linux
// files owned by a non-root account. Only systemd actions are simulated.
import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, rm, symlink, lstat, readdir, chmod } from 'node:fs/promises';
import { join, dirname } from 'node:path';
import { tmpdir } from 'node:os';
import { randomUUID, createHash } from 'node:crypto';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';
import { upgradeAutomaticHost, managedUnit, setupUnit, downloadMatchedPackage, parseAgentState, agentIsStopped, inspectAgentState, OLD, NEW } from '../scripts/upgrade-automatic-host-testing36.mjs';
const exec = promisify(execFile);
const bytes = () => readFile(process.env.BIFROST_TEST36_HOST_ARCHIVE);
const digest = b => createHash('sha256').update(b).digest('hex');
const runningState=()=>({ActiveState:'active',SubState:'running',MainPID:'1234',ControlGroup:'/fixture-agent',TasksCurrent:'1',Job:'',Result:'success',ExecMainCode:'0',ExecMainStatus:'0'});
const stoppedState=()=>({ActiveState:'inactive',SubState:'dead',MainPID:'0',ControlGroup:'',TasksCurrent:'[not set]',Job:'',Result:'success',ExecMainCode:'1',ExecMainStatus:'0'});
const reportedTimeoutState=()=>({...stoppedState(),ActiveState:'failed',SubState:'failed',Result:'timeout'});
async function fixture() {
  assert.notEqual(process.getuid(),0,'These tests require a non-root Linux account.');
  const home = await mkdtemp(join(tmpdir(),'.bifrost36-upgrade-'));
  for (const p of ['.config','.config/systemd','.config/systemd/user','.config/bifrost-host-agent','.local','.local/opt','.local/state','.local/state/bifrost-host-agent','.local/share','.local/share/bifrost-instances']) await mkdir(join(home,p),{mode:0o700});
  // Match the real mkdir -p installer layout rather than an all-0700 fixture.
  for (const p of ['.config','.config/systemd','.local','.local/state']) await chmod(join(home,p),0o755);
  const unit = join(home,'.config/systemd/user/bifrost-host-agent.service');
  const setup = join(home,'.config/systemd/user/bifrost-instance-setup.service');
  const config = join(home,'.config/bifrost-host-agent/host-agent.json');
  const bootstrap = join(home,'.config/bifrost-host-agent/local-bootstrap.json');
  const token = join(home,'.local/state/bifrost-host-agent/host.token');
  const ledger = join(home,'.local/state/bifrost-host-agent/job-ledger.json');
  const world = join(home,'.local/share/bifrost-instances/retained-world.sbc');
  // Build installed service bytes from the actual published Test 35 installer,
  // independently of the updater's expected-template builders.
  const installer=(await readFile(join(dirname(process.env.BIFROST_TEST35_HOST_ARCHIVE),'install.sh'),'utf8')).replaceAll('\r\n','\n');
  const installedUnit=name=>installer.split(`cat > "$stage/${name}" <<UNIT\n`)[1].split('\nUNIT')[0].replaceAll('$node_root','/opt/bifrost-node-v24.19.0').replaceAll('$package_root',join(home,'.local/opt',`bifrost-host-agent-${OLD}`)).replaceAll('$game_home',home)+'\n';
  await writeFile(unit,installedUnit('bifrost-host-agent.service'),{mode:0o600}); await writeFile(setup,installedUnit('bifrost-instance-setup.service'),{mode:0o600});
  await writeFile(bootstrap,'SYNTHETIC_RETAINED_BOOTSTRAP',{mode:0o600}); await writeFile(token,'SYNTHETIC_PRIVATE_TOKEN',{mode:0o600});
  const state = {controlPlaneUrl:'https://fixture.invalid',hostId:randomUUID(),tokenFile:token,ledgerFile:ledger,jobVerificationKeys:[{keyId:'ed25519-sha256:'+'1'.repeat(64),publicKeyFile:join(home,'fixture-key.pem')}],heartbeatSeconds:30,profiles:[]};
  await writeFile(config,JSON.stringify(state),{mode:0o600}); await writeFile(ledger,'{}',{mode:0o600}); await writeFile(world,'RETAINED_WORLD_AND_PLAYER_DATA',{mode:0o600});
  const old = join(home,'.local/opt',`bifrost-host-agent-${OLD}`);
  assert.equal(digest(await readFile(process.env.BIFROST_TEST35_HOST_ARCHIVE)),OLD);
  await exec('/usr/bin/python3',['-c',`import os,pathlib,sys,zipfile
p=pathlib.Path(sys.argv[2]);p.mkdir(mode=0o700)
with zipfile.ZipFile(sys.argv[1]) as z:z.extractall(p)
for root,dirs,files in os.walk(p):
 for d in dirs:(pathlib.Path(root)/d).chmod(0o700)
 for f in files:(pathlib.Path(root)/f).chmod(0o600)
`,process.env.BIFROST_TEST35_HOST_ARCHIVE,old]);
  const actions = [], stages = [];
  const options = {home,node:process.execPath,packageBytes:bytes,inspectAgent:async()=>actions.lastIndexOf('stop')>actions.lastIndexOf('start')?stoppedState():runningState(),systemctl:async args=>{actions.push(args[0]);},setupInactive:async()=>{},waitForStartup:async()=>{},onStage:s=>stages.push(s)};
  return {home,unit,setup,bootstrap,config,token,ledger,world,state,old,actions,stages,options,cleanup:()=>rm(home,{recursive:true,force:true})};
}
test('bounded production download permits only expected HTTPS final hosts',async()=>{
  const archive = await bytes();
  assert.equal(digest(archive),NEW);
  const downloaded = await downloadMatchedPackage(async(url,options)=>{assert.equal(url,'https://github.com/troainc/Bifrost-Server-Manager-Public/releases/download/v0.1.0-installtest.36/bifrost-linux-host-agent.zip');assert.ok(options.signal instanceof AbortSignal);return {ok:true,url:'https://release-assets.githubusercontent.com/host.zip',body:[archive.subarray(0,100),archive.subarray(100)]};});
  assert.deepEqual(downloaded,archive);
  for (const r of [{ok:false,url:'https://github.com/error',body:[]},{ok:true,url:'http://github.com/host.zip',body:[]},{ok:true,url:'https://unknown.invalid/host.zip',body:[]},{ok:true,url:'https://secret@github.com/host.zip',body:[]},{ok:true,url:'https://github.com/host.zip',body:[Buffer.alloc(2097153)]}]) await assert.rejects(downloadMatchedPackage(async()=>r));
});
test('published compiled package updates only Agent unit; identities, worker, bootstrap, ledger, world and old package survive',async()=>{
  const f = await fixture();try {
    const paths = [f.config,f.token,f.bootstrap,f.setup,f.ledger,f.world,join(f.old,'dist/main.js')];
    const before = await Promise.all(paths.map(p=>readFile(p)));
    const result = await upgradeAutomaticHost(f.options);
    assert.equal(result.serviceActive,true); assert.equal(result.heartbeatVerificationPending,true);
    assert.equal(await readFile(f.unit,'utf8'),managedUnit(f.home,NEW));
    for (let i=0;i<paths.length;i++) assert.deepEqual(await readFile(paths[i]),before[i]);
    assert.equal(await readFile(f.unit+'.before-testing36','utf8'),managedUnit(f.home,OLD));
    assert.deepEqual(f.actions,['is-active','stop','daemon-reload','start','is-active']);
    const again = await upgradeAutomaticHost(f.options);assert.equal(again.alreadyUpdated,true);
    await assert.rejects(lstat(f.ledger+'.lock'),{code:'ENOENT'});
    await assert.rejects(lstat(join(f.home,'.local/state/bifrost-host-agent/update-testing36.lock')),{code:'ENOENT'});
  } finally { await f.cleanup(); }
});
test('wrong package checksum and custom Agent unit refuse before a service stop',async()=>{
  const f=await fixture();try {
    await assert.rejects(upgradeAutomaticHost({...f.options,packageBytes:async()=>Buffer.from('WRONG')}),/checksum/);assert.deepEqual(f.actions,[]);
    await writeFile(f.unit,managedUnit(f.home,OLD)+'# custom\n');
    await assert.rejects(upgradeAutomaticHost(f.options),/exact Test 35/);assert.deepEqual(f.actions,[]);
  } finally { await f.cleanup(); }
});
test('custom setup worker and active setup each refuse before a service stop',async()=>{
  const f=await fixture();try {
    await writeFile(f.setup,setupUnit(f.home,OLD)+'# custom\n');await assert.rejects(upgradeAutomaticHost(f.options),/setup service differs/);
    await writeFile(f.setup,setupUnit(f.home,OLD));await assert.rejects(upgradeAutomaticHost({...f.options,setupInactive:async()=>{throw new Error('Setup active');}}),/Setup active/);
    assert.deepEqual(f.actions,[]);
  } finally { await f.cleanup(); }
});
test('real compiled preflight refuses a running ledger before service stop',async()=>{
  const f=await fixture();try {await writeFile(f.ledger,JSON.stringify({[randomUUID()]:'running'}));await assert.rejects(upgradeAutomaticHost(f.options));assert.deepEqual(f.actions,['is-active']);assert.equal(await readFile(f.unit,'utf8'),managedUnit(f.home,OLD));} finally {await f.cleanup();}
});
test('existing job lock is retained and refuses before stopping the Agent',async()=>{
  const f=await fixture();try {await writeFile(f.ledger+'.lock','RETAINED_LOCK',{mode:0o600});await assert.rejects(upgradeAutomaticHost(f.options));assert.deepEqual(f.actions,['is-active']);assert.equal(await readFile(f.ledger+'.lock','utf8'),'RETAINED_LOCK');} finally {await f.cleanup();}
});
test('another update lock is retained without a service stop',async()=>{
  const f=await fixture();try {const lock=join(f.home,'.local/state/bifrost-host-agent/update-testing36.lock');await writeFile(lock,'RETAINED_UPDATE',{mode:0o600});await assert.rejects(upgradeAutomaticHost(f.options));assert.deepEqual(f.actions,['is-active']);assert.equal(await readFile(lock,'utf8'),'RETAINED_UPDATE');} finally {await f.cleanup();}
});
test('brief idle queue-poll lock is allowed to finish without forced removal',async()=>{
  const f=await fixture();let timer;try {
    await writeFile(f.ledger+'.lock','QUEUE_POLL',{mode:0o600});
    const options={...f.options,onStage:s=>{f.stages.push(s);if(s==='idle-ledger-lock')timer=setTimeout(()=>rm(f.ledger+'.lock'),100);}};
    assert.equal((await upgradeAutomaticHost(options)).serviceActive,true);
    assert.equal(await readFile(f.unit,'utf8'),managedUnit(f.home,NEW));
  } finally {clearTimeout(timer);await f.cleanup();}
});
test('startup failure restores exact prior unit and restarts old Agent without game commands',async()=>{
  const f=await fixture();let starts=0;try {
    await assert.rejects(upgradeAutomaticHost({...f.options,systemctl:async args=>{f.actions.push(args[0]);if(args[0]==='start'&&++starts===1)throw new Error('synthetic startup refusal');}}),/synthetic startup/);
    assert.equal(await readFile(f.unit,'utf8'),managedUnit(f.home,OLD));assert.equal(starts,2);assert.equal(await readFile(f.token,'utf8'),'SYNTHETIC_PRIVATE_TOKEN');
  } finally {await f.cleanup();}
});
test('failed post-start readiness also restores old Agent unit',async()=>{
  const f=await fixture();let checks=0;try {
    await assert.rejects(upgradeAutomaticHost({...f.options,systemctl:async args=>{f.actions.push(args[0]);if(args[0]==='is-active'&&++checks===2)throw new Error('failed startup readiness');}}),/readiness/);
    assert.equal(await readFile(f.unit,'utf8'),managedUnit(f.home,OLD));assert.equal(f.actions.filter(x=>x==='start').length,2);
  } finally {await f.cleanup();}
});
test('concurrent enrollment change is retained and prevents replacement or restart',async()=>{
  const f=await fixture();try {
    await assert.rejects(upgradeAutomaticHost({...f.options,systemctl:async args=>{f.actions.push(args[0]);if(args[0]==='stop')await writeFile(f.config,JSON.stringify({...f.state,hostId:randomUUID()}));}}),/Protected state changed/);
    assert.equal(await readFile(f.unit,'utf8'),managedUnit(f.home,OLD));assert.equal(f.actions.includes('start'),false);assert.notEqual(JSON.parse(await readFile(f.config)).hostId,f.state.hostId);
  } finally {await f.cleanup();}
});
test('retained package with altered file refuses before any further service stop',async()=>{
  const f=await fixture();try {
    await upgradeAutomaticHost(f.options);f.actions.length=0;
    await writeFile(join(f.home,'.local/opt',`bifrost-host-agent-${NEW}`,'INSTALL.md'),'ALTERED');
    await assert.rejects(upgradeAutomaticHost(f.options));assert.deepEqual(f.actions,['is-active']);
  } finally {await f.cleanup();}
});
test('retained modified preflight is rejected without executing it',async()=>{
  const f=await fixture();try {
    await upgradeAutomaticHost(f.options);f.actions.length=0;
    const marker=join(f.home,'MUST_NOT_EXECUTE');
    await writeFile(join(f.home,'.local/opt',`bifrost-host-agent-${NEW}`,'dist/preflight-upgrade.js'),`import {writeFileSync} from 'node:fs'; writeFileSync(${JSON.stringify(marker)},'UNSAFE');`);
    await assert.rejects(upgradeAutomaticHost(f.options));
    await assert.rejects(lstat(marker),{code:'ENOENT'});assert.deepEqual(f.actions,['is-active']);
  } finally {await f.cleanup();}
});
test('diagnostic mode verifies download without executing retained code or changing files/services',async()=>{
  const f=await fixture();try {
    const before=await readdir(join(f.home,'.local/opt'));const result=await upgradeAutomaticHost({...f.options,diagnoseOnly:true});
    assert.equal(result.readOnly,true);assert.equal(result.newPackagePreflightPending,true);assert.equal(result.matchedDownloadVerified,true);assert.deepEqual(await readdir(join(f.home,'.local/opt')),before);assert.deepEqual(f.actions,['is-active']);assert.equal(await readFile(f.unit,'utf8'),managedUnit(f.home,OLD));
  } finally {await f.cleanup();}
});
test('symlinked unit parent and token refuse before any service access',async()=>{
  const f=await fixture();try {
    await rm(f.token);await symlink(f.world,f.token);await assert.rejects(upgradeAutomaticHost(f.options));assert.deepEqual(f.actions,[]);
    await rm(join(f.home,'.config/systemd/user'),{recursive:true});await symlink(join(f.home,'.config/bifrost-host-agent'),join(f.home,'.config/systemd/user'));await assert.rejects(upgradeAutomaticHost(f.options));assert.deepEqual(f.actions,[]);
  } finally {await f.cleanup();}
});
test('group-writable intermediate directory refuses without changing its permissions',async()=>{
  const f=await fixture();try {
    const directory=join(f.home,'.config');await chmod(directory,0o770);
    await assert.rejects(upgradeAutomaticHost(f.options),/validation/);
    assert.deepEqual(f.actions,[]);assert.equal((await lstat(directory)).mode&0o777,0o770);
  } finally {await f.cleanup();}
});
test('production entry point refuses another account/runtime without disclosing private state',async()=>{
  await assert.rejects(exec(process.execPath,[fileURLToPath(new URL('../scripts/upgrade-automatic-host-testing36.mjs',import.meta.url))]),error=>error.code===1&&error.stderr.includes('Credentials and game files were preserved')&&!error.stderr.includes('SYNTHETIC_PRIVATE_TOKEN'));
});
test('actual reported timeout state is accepted only as fully stopped',async()=>{
  const state=reportedTimeoutState();
  assert.equal(agentIsStopped(parseAgentState(Object.entries(state).map(([k,v])=>`${k}=${v}`).join('\n'))),true);
  for(const changed of [{MainPID:'123'},{ControlGroup:'/remaining-processes'},{TasksCurrent:'1'},{Job:'12'},{ExecMainStatus:'9'},{ActiveState:'deactivating'},{Result:'signal'}])assert.equal(agentIsStopped({...state,...changed}),false);
  assert.throws(()=>parseAgentState('ActiveState=failed'),/Incomplete/);
  assert.throws(()=>parseAgentState('ActiveState=failed\nActiveState=active'),/Duplicate/);
});
test('production status adapter asks for bounded fixed fields without credentials/logs',async()=>{
  const state=reportedTimeoutState();const actual=await inspectAgentState(async(binary,args,options)=>{
    assert.equal(binary,'/usr/bin/systemctl');assert.deepEqual(args.slice(0,3),['--user','show','bifrost-host-agent.service']);assert.equal(options.timeout,15000);
    return {stdout:Object.entries(state).map(([k,v])=>`${k}=${v}`).join('\n')};
  });assert.deepEqual(actual,state);
});
test('explicit stopped recovery reuses retained candidate and never repeats stop',async()=>{
  const f=await fixture();try {
    const options={...f.options,resumeStopped:true,inspectAgent:async()=>f.actions.includes('start')?runningState():reportedTimeoutState()};
    // Exercise a real staged candidate from the previous failed attempt.
    await assert.rejects(upgradeAutomaticHost({...f.options,systemctl:async args=>{f.actions.push(args[0]);if(args[0]==='stop')throw new Error('stop timeout');},inspectAgent:async()=>runningState()}));
    f.actions.length=0;
    assert.equal((await upgradeAutomaticHost(options)).serviceActive,true);
    assert.deepEqual(f.actions,['daemon-reload','start','is-active']);
    assert.equal(await readFile(f.unit,'utf8'),managedUnit(f.home,NEW));
    assert.equal(await readFile(f.world,'utf8'),'RETAINED_WORLD_AND_PLAYER_DATA');
    assert.equal((await upgradeAutomaticHost(options)).alreadyUpdated,true);
  }finally{await f.cleanup();}
});
test('stopped old Agent requires explicit recovery and rejects residual/pending processes',async()=>{
  const f=await fixture();try {
    await assert.rejects(upgradeAutomaticHost({...f.options,inspectAgent:async()=>reportedTimeoutState()}));
    for(const changed of [{MainPID:'123'},{ControlGroup:'/remaining'},{Job:'1'},{TasksCurrent:'2'}])await assert.rejects(upgradeAutomaticHost({...f.options,resumeStopped:true,inspectAgent:async()=>({...reportedTimeoutState(),...changed})}));
    assert.deepEqual(f.actions,[]);assert.equal(await readFile(f.unit,'utf8'),managedUnit(f.home,OLD));
  }finally{await f.cleanup();}
});
test('stop-call failure proceeds only after independent proof of completed shutdown',async()=>{
  const f=await fixture();try {
    const result=await upgradeAutomaticHost({...f.options,systemctl:async args=>{f.actions.push(args[0]);if(args[0]==='stop')throw new Error('systemd timeout');},inspectAgent:async()=>f.actions.lastIndexOf('stop')>f.actions.lastIndexOf('start')?reportedTimeoutState():runningState()});
    assert.equal(result.serviceActive,true);assert.equal(await readFile(f.unit,'utf8'),managedUnit(f.home,NEW));
  }finally{await f.cleanup();}
});
test('stopped recovery startup failure restores old unit and leaves original stopped state',async()=>{
  const f=await fixture();try {
    await assert.rejects(upgradeAutomaticHost({...f.options,resumeStopped:true,inspectAgent:async()=>reportedTimeoutState(),systemctl:async args=>{f.actions.push(args[0]);if(args[0]==='start')throw new Error('startup refusal');}}),/startup refusal/);
    assert.equal(await readFile(f.unit,'utf8'),managedUnit(f.home,OLD));assert.equal(f.actions.filter(x=>x==='start').length,1);
  }finally{await f.cleanup();}
});
