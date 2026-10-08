import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,readFile,readdir,lstat,rm,symlink,link} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {publicWorldSetting,repairWorldFiles} from '../scripts/enable-torch-world-multiplayer.mjs';
const xml=Buffer.from('<?xml version="1.0"?><World><Name>Preserved world</Name><Settings><OnlineMode>OFFLINE</OnlineMode><MaxPlayers>4</MaxPlayers></Settings><Players>keep me</Players></World>');
test('only the exact multiplayer setting changes, and public worlds retain their bytes',()=>{
  const changed=publicWorldSetting(xml);assert.equal(changed.before,'OFFLINE');assert.equal(changed.after.toString(),xml.toString().replace('OFFLINE','PUBLIC'));
  assert.deepEqual(publicWorldSetting(changed.after).after,changed.after);
  for(const value of ['<World/>','<OnlineMode>FRIENDS</OnlineMode>','<OnlineMode>OFFLINE</OnlineMode><OnlineMode>OFFLINE</OnlineMode>','<!--<OnlineMode>OFFLINE</OnlineMode>--><OnlineMode>OFFLINE</OnlineMode>','<!DOCTYPE World><OnlineMode>OFFLINE</OnlineMode>'])assert.throws(()=>publicWorldSetting(Buffer.from(value)));
});
async function fixture(fn){
 const root=await mkdtemp(join(tmpdir(),'bifrost-world-repair-')),world=join(root,'world'),evidence=join(root,'evidence');
 try{await mkdir(world,{mode:0o700});await mkdir(evidence,{mode:0o700});for(const name of ['Sandbox.sbc','Sandbox_config.sbc'])await writeFile(join(world,name),xml,{mode:0o600});await fn({root,world,evidence});}
 finally{await rm(root,{recursive:true,force:true});}
}
const linux={skip:process.platform!=='linux'};
test('both originals are preserved before changing their modes; repeat is inert',linux,async()=>fixture(async({world,evidence})=>{
 const result=await repairWorldFiles(world,evidence,async()=>{});assert.equal(result.repairCompleted,true);
 for(const name of ['Sandbox.sbc','Sandbox_config.sbc']){assert.deepEqual(await readFile(join(evidence,result.backupRef,name)),xml);assert.deepEqual(await readFile(join(world,name)),publicWorldSetting(xml).after);assert.equal((await lstat(join(evidence,result.backupRef,name))).mode&0o777,0o600);}
 const before=await readdir(evidence);assert.equal((await repairWorldFiles(world,evidence,async()=>{})).alreadyPublic,true);assert.deepEqual(await readdir(evidence),before);
}));
test('malformed second file leaves both originals untouched and creates no evidence',linux,async()=>fixture(async({world,evidence})=>{
 const bad=Buffer.from('<World/>');await writeFile(join(world,'Sandbox_config.sbc'),bad);await assert.rejects(repairWorldFiles(world,evidence,async()=>{}));assert.deepEqual(await readFile(join(world,'Sandbox.sbc')),xml);assert.deepEqual(await readFile(join(world,'Sandbox_config.sbc')),bad);assert.deepEqual(await readdir(evidence),[]);
}));
test('running runtime guard refuses before creating evidence or changing files',linux,async()=>fixture(async({world,evidence})=>{
 await assert.rejects(repairWorldFiles(world,evidence,async()=>{throw new Error('runtime still running');}));assert.deepEqual(await readFile(join(world,'Sandbox.sbc')),xml);assert.deepEqual(await readdir(evidence),[]);
}));
test('concurrent file change is preserved rather than overwritten',linux,async()=>fixture(async({world,evidence})=>{
 let calls=0;const concurrent=Buffer.from('<World><OnlineMode>PUBLIC</OnlineMode><Name>Concurrent owner edit</Name></World>');
 await assert.rejects(repairWorldFiles(world,evidence,async()=>{if(++calls===2)await writeFile(join(world,'Sandbox.sbc'),concurrent);}),error=>error.rollbackCompleted===true);
 assert.deepEqual(await readFile(join(world,'Sandbox.sbc')),concurrent);assert.deepEqual(await readFile(join(world,'Sandbox_config.sbc')),xml);
}));
test('failure between replacements restores the first original and retains backups',linux,async()=>fixture(async({world,evidence})=>{
 let calls=0;let error;try{await repairWorldFiles(world,evidence,async()=>{if(++calls===3)throw new Error('injected failure');});}catch(value){error=value;}
 assert.equal(error.rollbackCompleted,true);for(const name of ['Sandbox.sbc','Sandbox_config.sbc']){assert.deepEqual(await readFile(join(world,name)),xml);assert.deepEqual(await readFile(join(evidence,error.backupRef,name)),xml);}assert.equal((await readdir(world)).length,2);
}));
test('symlink and hard-linked world files are rejected without changes',linux,async()=>{
 for(const kind of ['symlink','hardlink'])await fixture(async({root,world,evidence})=>{
  const target=join(root,'outside.xml');await writeFile(target,xml,{mode:0o600});const path=join(world,'Sandbox.sbc');await rm(path);if(kind==='symlink')await symlink(target,path);else await link(target,path);
  await assert.rejects(repairWorldFiles(world,evidence,async()=>{}));assert.deepEqual(await readFile(target),xml);assert.deepEqual(await readdir(evidence),[]);
 });
});
