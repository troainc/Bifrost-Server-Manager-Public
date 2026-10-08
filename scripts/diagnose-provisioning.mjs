// Read-only inspection of the enrolled Host. No reset, retry, removal or credential output.
import { constants } from 'node:fs';
import { open,lstat,realpath,statfs } from 'node:fs/promises';
import { join,dirname,resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';
const home='/home/bifrost-games';
const uuid=/^[a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12}$/;
const exec=promisify(execFile);
export function summarizeConfig(config){
 const profiles=Array.isArray(config?.profiles)?config.profiles.slice(0,256):[];
 return {hostId:uuid.test(config?.hostId)?config.hostId:null,profiles:profiles.map(profile=>({instanceId:uuid.test(profile?.instanceId)?profile.instanceId:null})),profileCount:profiles.length,provisioningConfigured:!!config?.provisioning};
}
export function summarizeLedger(ledger){
 if(!ledger||typeof ledger!=='object'||Array.isArray(ledger))return [];
 return Object.entries(ledger).filter(([id])=>uuid.test(id)).slice(-100).map(([jobId,state])=>({jobId,state:['running','complete'].includes(state)?state:'unknown'}));
}
export function summarizeContainer(value,id){
 const item=Array.isArray(value)&&value.length===1?value[0]:undefined;
 const states=['created','configured','running','paused','restarting','stopping','stopped','exited','dead'];
 return {present:!!item,state:states.includes(item?.State?.Status)?item.State.Status:'unknown',exitCode:Number.isSafeInteger(item?.State?.ExitCode)?item.State.ExitCode:null,matchesManagedIdentity:item?.Config?.Labels?.['io.bifrost.instance-id']===id&&item?.Config?.Labels?.['io.bifrost.managed-by']==='bifrost'};
}
export function summarizeManifest(value){
 const request=typeof value?.request==='string'?JSON.parse(value.request):value?.request;
 return {instanceId:uuid.test(request?.instanceId)?request.instanceId:null,blueprintDigest:/^sha256:[a-f0-9]{64}$/.test(request?.blueprintDigest)?request.blueprintDigest:null};
}
function classify(error){return ['ENOENT','EACCES','EPERM'].includes(error?.code)?error.code:'CHECK_FAILED';}
async function safeChain(path){
 const directory=dirname(resolve(path));if(await realpath(directory)!==directory)throw new Error('Linked ancestor');
 let current=directory;
 while(true){const info=await lstat(current);if(!info.isDirectory()||info.isSymbolicLink()||((info.mode&0o022)!==0&&(info.mode&0o1000)===0))throw new Error('Unsafe ancestor');const parent=dirname(current);if(parent===current)break;current=parent;}
}
async function privateJson(path){
 await safeChain(path);
 const file=await open(path,constants.O_RDONLY|constants.O_NOFOLLOW);
 try{const info=await file.stat();if(!info.isFile()||info.uid!==process.getuid()||(info.mode&0o077)!==0||info.nlink!==1||info.size>1048576)throw new Error('Unsafe private file');return JSON.parse(await file.readFile('utf8'));}finally{await file.close();}
}
async function presence(path){try{await safeChain(path);const info=await lstat(path);return {present:true,regular:info.isFile()&&!info.isSymbolicLink(),ownedByGameAccount:info.uid===process.getuid()};}catch(error){return {present:false,checkError:classify(error)};}}
export async function diagnose(instanceId){
 if(instanceId!==undefined&&!uuid.test(instanceId))throw new Error("Expected a game instance UUID");
 if(process.platform!=='linux'||typeof process.getuid!=='function'||process.getuid()===0)throw new Error('Run as the existing bifrost-games service account');
 const config=await privateJson(join(home,'.config/bifrost-host-agent/host-agent.json'));
 const output={readOnly:true,...summarizeConfig(config),ledger:[],lock:{present:false},instances:[]};
 try{output.ledger=summarizeLedger(await privateJson(join(home,'.local/state/bifrost-host-agent/job-ledger.json')));}catch(error){output.ledgerCheckError=classify(error);}
 const root=config?.provisioning?.root;
 if(typeof root==='string'&&root===resolve(root)){
  try{const lock=await privateJson(join(root,'.provision-lock.json'));output.lock={present:true,instanceId:uuid.test(lock?.instanceId)?lock.instanceId:null};}catch(error){output.lock={present:false,checkError:classify(error)};}
  const ids=[...new Set([instanceId,output.lock.instanceId,...output.profiles.map(profile=>profile.instanceId)].filter(id=>uuid.test(id)))].slice(0,64);
  try{const filesystem=await statfs(root);output.freeStorageBytes=Number(filesystem.bavail)*Number(filesystem.bsize);}catch(error){output.storageCheckError=classify(error);}
  for(const instanceId of ids){
   const instance={instanceId,files:{},container:{present:false},installer:{present:false}};
   for(const name of ['provision.json','download-receipt.json','activated-profile.json'])instance.files[name]=await presence(join(root,instanceId,name));
   try{instance.manifest=summarizeManifest(await privateJson(join(root,instanceId,'provision.json')));}catch(error){instance.manifestCheckError=classify(error);}
   try{const response=await exec('/usr/bin/podman',['container','inspect',`bifrost-${instanceId}`],{cwd:home,timeout:15000,maxBuffer:1048576});instance.container=summarizeContainer(JSON.parse(response.stdout),instanceId);}catch{instance.container={present:false,checkError:'INSPECT_UNAVAILABLE'};}
   try{const response=await exec('/usr/bin/podman',['container','inspect',`bifrost-install-${instanceId}`],{cwd:home,timeout:15000,maxBuffer:1048576});instance.installer=summarizeContainer(JSON.parse(response.stdout),instanceId);}catch{instance.installer={present:false,checkError:'INSPECT_UNAVAILABLE'};}
   output.instances.push(instance);
  }
 }
 console.log(JSON.stringify(output,null,2));return output;
}
if(process.argv[1]==='-'||(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href))await diagnose(process.argv[2]).catch(error=>{console.log(JSON.stringify({readOnly:true,checkError:classify(error)}));process.exitCode=1;});
