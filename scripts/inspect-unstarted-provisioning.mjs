// Read-only operator review of a retained, never-started Torch installer.
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
export function neverStarted(state){return state?.Status==='initialized'&&state.Running===false&&state.Paused===false&&state.Restarting===false&&state.Pid===0&&/^0001-01-01T00:00:00(?:\.0+)?Z$/.test(state.StartedAt)&&/^0001-01-01T00:00:00(?:\.0+)?Z$/.test(state.FinishedAt);}
export async function inspectUnstarted(instanceId,digest){
 assert.equal(process.platform,'linux');assert.ok(process.getuid?.()>0);assert.equal(process.execPath,NODE);
 assert.match(instanceId,/^[a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12}$/);assert.match(digest,/^sha256:[a-f0-9]{64}$/);
 const unit=join(home,'.config/systemd/user/bifrost-host-agent.service');
 const info=await lstat(unit);assert.ok(info.isFile()&&!info.isSymbolicLink()&&info.uid===process.getuid()&&info.nlink===1&&(info.mode&0o077)===0);
 const text=await readFile(unit,'utf8');
 const hash=hashes.find(hash=>text.includes(`ExecStart=${NODE} ${home}/.local/opt/bifrost-host-agent-${hash}/dist/main.js\n`));assert.ok(hash);
 const pkg=join(home,'.local/opt',`bifrost-host-agent-${hash}`);assert.equal(await realpath(pkg),pkg);
 const {loadConfig,assertNoSymlinkDirectory}=await import(pathToFileURL(join(pkg,'dist/config.js')));
 const {readPrivateFile}=await import(pathToFileURL(join(pkg,'dist/security.js')));
 const {hostBlueprints}=await import(pathToFileURL(join(pkg,'dist/provisioning.js')));
 const {assertOciProcessConfinement,parseBifrostContainerInspection}=await import(pathToFileURL(join(pkg,'dist/provider.js')));
 const {validateProvisionRequest}=await import(pathToFileURL(join(pkg,'node_modules/@bifrost/contracts/dist/provisioning-node.js')));
 const config=await loadConfig(join(home,'.config/bifrost-host-agent/host-agent.json'));assert.equal(config.profiles.length,0);assert.ok(config.provisioning);
 const root=join(config.provisioning.root,instanceId);await assertNoSymlinkDirectory(root);
 const manifest=JSON.parse(await readPrivateFile(join(root,'provision.json'),'Retained manifest'));
 const request=JSON.parse(manifest.request);assert.equal(request.instanceId,instanceId);assert.equal(request.blueprintDigest,digest);
 const approved=(await hostBlueprints(config)).find(b=>b.digest===digest&&b.manifest.id==='space-engineers-1-torch');assert.ok(approved);
 validateProvisionRequest(approved.manifest,request);
 const b=approved.manifest,p=manifest.profile;
 assert.equal(p.instanceId,instanceId);assert.equal(p.provider,'oci');assert.equal(p.runtime,'linux-wine-container');assert.equal(p.containerName,`bifrost-${instanceId}`);assert.equal(p.instanceDataRoot,root);
 const expected={imageId:b.imageId,dataRoot:root,runAsUser:`${b.uid}:${b.gid}`,usernsMode:`keep-id:uid=${b.uid},gid=${b.gid}`,networkName:`bifrost-${instanceId}`,maxMemoryBytes:request.memoryBytes,maxMemorySwapBytes:request.memoryBytes,maxShmBytes:16777216,maxNanoCpus:request.nanoCpus,maxPids:1024,mounts:[{source:join(root,'files'),destination:'/bifrost/files',readOnly:false}],tmpfs:[{destination:'/tmp',maxSizeBytes:67108864},{destination:'/run',maxSizeBytes:16777216}],publishedPorts:request.ports.map(port=>({hostIp:config.provisioning.hostIp,hostPort:port.hostPort,containerPort:b.ports.find(p=>p.id===port.id).containerPort,protocol:b.ports.find(p=>p.id===port.id).protocol}))};
 assert.deepEqual(p.sandbox,expected);
 const temporary={...p,containerName:`bifrost-install-${instanceId}`,sandbox:{...expected,publishedPorts:[],mounts:[{source:join(root,'server'),destination:'/bifrost/server',readOnly:false},{source:join(root,'downloads'),destination:'/bifrost/downloads',readOnly:false}],tmpfs:[{destination:'/tmp',maxSizeBytes:1073741824},{destination:'/run',maxSizeBytes:16777216}]}};
 const podman=async args=>(await exec('/usr/bin/podman',args,{timeout:15000,maxBuffer:1024*1024})).stdout;
 const raw=await podman(['container','inspect',temporary.containerName]);const values=JSON.parse(raw);assert.equal(values.length,1);const c=values[0];assert.ok(neverStarted(c.State));assert.match(c.Id,/^[a-f0-9]{64}$/);assert.ok(c.OCIConfigPath.endsWith(`/overlay-containers/${c.Id}/userdata/config.json`));
 const confinement=await podman(['unshare',process.execPath,join(pkg,'dist/oci-confinement-reader.js'),c.OCIConfigPath,c.Id,String(process.getuid())]);
 assertOciProcessConfinement(confinement,temporary);const inspected=parseBifrostContainerInspection(raw,temporary,true);assert.equal(inspected.state,'initialized');
 try{await podman(['container','exists',p.containerName]);throw Error('Game exists');}catch(error){assert.equal(error.code,1);}
 const counts={};for(const name of ['server','downloads']){await assertNoSymlinkDirectory(join(root,name));counts[name]=(await readdir(join(root,name))).length;}
 const lock=JSON.parse(await readPrivateFile(join(config.provisioning.root,'.provision-lock.json'),'Provisioning lock'));assert.equal(lock.instanceId,instanceId);assert.equal(lock.blueprintDigest,digest);
 return {readOnly:true,instanceId,approvedTorchManifest:true,initializedInstallerNeverStarted:true,fullContainerSandboxVerified:true,zeroOciCapabilitiesVerified:true,activePinnedNodeReaderWorks:true,gameContainerAbsent:true,profileCount:0,retainedLockMatches:true,retainedDirectoryEntryCounts:counts};
}
if(process.argv[1]==='-'||process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href){
 try{assert.equal(process.argv.length,4);console.log(JSON.stringify(await inspectUnstarted(process.argv[2],process.argv[3]),null,2));}
 catch(error){console.log(JSON.stringify({readOnly:true,reviewPassed:false,code:['ENOENT','EACCES','EPERM'].includes(error?.code)?error.code:'REVIEW_REFUSED'}));process.exitCode=1;}
}
