// Disposable non-root files plus the exact compiled testing 20 package.
import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, rm, symlink, lstat } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { randomUUID } from 'node:crypto';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
import { fileURLToPath } from 'node:url';
import { upgradeAutomaticHost, managedUnit } from '../scripts/upgrade-automatic-host-testing20.mjs';
const OLD='f6603eff0b696a2841d2cc51d4362e21f5fcd04f674ab5cc2052f611534fbea1',NEW='9408da9bac948edc3063fbd5e97019e07c99d30084d961d390d68f8191969504';
async function fixture() {
 const home=await mkdtemp(join(tmpdir(),'.bifrost-auto-upgrade-'));
 for(const p of ['.config','.config/systemd','.config/systemd/user','.config/bifrost-host-agent','.local','.local/opt','.local/state','.local/state/bifrost-host-agent'])await mkdir(join(home,p),{mode:0o700});
 const unit=join(home,'.config/systemd/user/bifrost-host-agent.service'),config=join(home,'.config/bifrost-host-agent/host-agent.json'),token=join(home,'.local/state/bifrost-host-agent/host.token'),ledger=join(home,'.local/state/bifrost-host-agent/job-ledger.json');
 await writeFile(unit,managedUnit(home,OLD),{mode:0o600}); await writeFile(token,'SYNTHETIC_PRIVATE_TOKEN',{mode:0o600});
 const state={controlPlaneUrl:'https://fixture.invalid',hostId:randomUUID(),tokenFile:token,ledgerFile:ledger,jobVerificationKeys:[{keyId:'ed25519-sha256:'+'1'.repeat(64),publicKeyFile:join(home,'fixture-key.pem')}],heartbeatSeconds:30,profiles:[]};
 await writeFile(config,JSON.stringify(state),{mode:0o600});await writeFile(ledger,'{}',{mode:0o600});
 const old=join(home,'.local/opt',`bifrost-host-agent-${OLD}`); await mkdir(old,{mode:0o700});await writeFile(join(old,'retained'),'OLD_PACKAGE',{mode:0o600});
 const actions=[];const options={home,node:process.execPath,packageBytes:()=>readFile(process.env.BIFROST_TEST20_HOST_ARCHIVE),systemctl:async args=>{actions.push(args[0]);}};
 return {home,unit,config,token,ledger,state,old,actions,options,cleanup:()=>rm(home,{recursive:true,force:true})};
}
test('exact compiled package updates only the known unit, preserves enrollment and old files, and is idempotent',async()=>{
 const f=await fixture();try{const before=await readFile(f.config);const result=await upgradeAutomaticHost(f.options);assert.equal(result.serviceActive,true);assert.equal(result.heartbeatVerificationPending,true);assert.equal(await readFile(f.unit,'utf8'),managedUnit(f.home,NEW));assert.deepEqual(await readFile(f.config),before);assert.equal(await readFile(f.token,'utf8'),'SYNTHETIC_PRIVATE_TOKEN');assert.equal(await readFile(join(f.old,'retained'),'utf8'),'OLD_PACKAGE');assert.equal(await readFile(f.unit+'.before-testing20','utf8'),managedUnit(f.home,OLD));assert.deepEqual(f.actions,['is-active','stop','daemon-reload','start','is-active']);const again=await upgradeAutomaticHost({...f.options,packageBytes:()=>{throw new Error('No redownload');}});assert.equal(again.alreadyUpdated,true);}finally{await f.cleanup();}
});
test('wrong archive and custom unit refuse before stopping the existing service',async()=>{
 const f=await fixture();try{await assert.rejects(upgradeAutomaticHost({...f.options,packageBytes:async()=>Buffer.from('WRONG')}),/checksum/);assert.equal(f.actions.length,0);await writeFile(f.unit,managedUnit(f.home,OLD)+'# custom\n');await assert.rejects(upgradeAutomaticHost(f.options),/exact testing 18/);assert.equal(f.actions.length,0);}finally{await f.cleanup();}
});
test('diagnostic mode verifies download and current preflight without staging or service changes',async()=>{
 const f=await fixture();try{await writeFile(join(f.old,'dist-placeholder'),'retained',{mode:0o600});const stages=[];const before=await readFile(f.unit);const result=await upgradeAutomaticHost({...f.options,diagnoseOnly:true,onStage:s=>stages.push(s),preflight:async()=>{}});assert.equal(result.readOnly,true);assert.equal(result.packageDestinationPresent,false);assert.deepEqual(f.actions,['is-active']);assert.deepEqual(await readFile(f.unit),before);await assert.rejects(lstat(join(f.home,'.local/opt',`bifrost-host-agent-${NEW}`)),{code:'ENOENT'});assert.ok(stages.includes('matched-package-download'));assert.ok(stages.includes('existing-compiled-preflight'));}finally{await f.cleanup();}
});
test('real compiled preflight refuses a running ledger before service stop',async()=>{
 const f=await fixture();try{await writeFile(f.ledger,JSON.stringify({[randomUUID()]:'running'}));await assert.rejects(upgradeAutomaticHost(f.options));assert.equal(f.actions.length,0);assert.equal(await readFile(f.unit,'utf8'),managedUnit(f.home,OLD));}finally{await f.cleanup();}
});
test('retained ledger lock is never removed or restarted over',async()=>{
 const f=await fixture();try{await writeFile(f.ledger+'.lock','RETAINED',{mode:0o600});await assert.rejects(upgradeAutomaticHost(f.options),/Existing lock/);assert.deepEqual(f.actions,['is-active','stop']);assert.equal(await readFile(f.ledger+'.lock','utf8'),'RETAINED');assert.equal(await readFile(f.unit,'utf8'),managedUnit(f.home,OLD));}finally{await f.cleanup();}
});
test('failed new service start restores the exact prior unit and restarts it',async()=>{
 const f=await fixture();let starts=0;try{await assert.rejects(upgradeAutomaticHost({...f.options,systemctl:async args=>{f.actions.push(args[0]);if(args[0]==='start'&&++starts===1)throw new Error('synthetic startup refusal');}}),/synthetic startup/);assert.equal(await readFile(f.unit,'utf8'),managedUnit(f.home,OLD));assert.equal(starts,2);assert.equal(await readFile(f.token,'utf8'),'SYNTHETIC_PRIVATE_TOKEN');}finally{await f.cleanup();}
});
test('concurrent enrollment change is preserved and blocks unit replacement',async()=>{
 const f=await fixture();try{await assert.rejects(upgradeAutomaticHost({...f.options,systemctl:async args=>{f.actions.push(args[0]);if(args[0]==='stop')await writeFile(f.config,JSON.stringify({...f.state,hostId:randomUUID()}));}}),/changed during preparation/);assert.equal(await readFile(f.unit,'utf8'),managedUnit(f.home,OLD));assert.notEqual(JSON.parse(await readFile(f.config,'utf8')).hostId,f.state.hostId);}finally{await f.cleanup();}
});
test('symlinked unit parent refuses before reading or changing a service',async()=>{
 const f=await fixture();try{await rm(join(f.home,'.config/systemd/user'),{recursive:true});await symlink(join(f.home,'.config/bifrost-host-agent'),join(f.home,'.config/systemd/user'));await assert.rejects(upgradeAutomaticHost(f.options),/validation/);assert.equal(f.actions.length,0);assert.equal((await lstat(join(f.home,'.config/systemd/user'))).isSymbolicLink(),true);}finally{await f.cleanup();}
});
test('production entry point refuses another account/runtime before any download or update',async()=>{
 await assert.rejects(promisify(execFile)(process.execPath,[fileURLToPath(new URL('../scripts/upgrade-automatic-host-testing20.mjs',import.meta.url))]),error=>error.code===1&&error.stderr.includes('Existing credentials and game files were preserved')&&!error.stderr.includes('SYNTHETIC_PRIVATE_TOKEN'));
});
