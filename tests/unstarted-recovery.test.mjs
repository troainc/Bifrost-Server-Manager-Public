import test from 'node:test';
import assert from 'node:assert/strict';
import {validateRecoveryLedger,validateRecoveryNetwork,recoveryFailure} from '../scripts/recover-unstarted-provisioning.mjs';
const id='11111111-1111-4111-8111-111111111111';
test('recovery never clears a running, completed or malformed local job ledger',()=>{
 assert.doesNotThrow(()=>validateRecoveryLedger({}));
 for(const value of [null,undefined,[],{[id]:'running'},{[id]:'complete'},'{}'])assert.throws(()=>validateRecoveryLedger(value));
});
test('network recovery requires exact identity, owned instance label, bridge driver and no foreign workload',()=>{
 const network={id:'a'.repeat(64),name:`bifrost-${id}`,driver:'bridge',labels:{'io.bifrost.instance-id':id}};
 assert.doesNotThrow(()=>validateRecoveryNetwork(network,id));
 for(const change of [{id:'invalid'},{name:'unrelated'},{driver:'host'},{labels:{}},{labels:{'io.bifrost.instance-id':'22222222-2222-4222-8222-222222222222'}},{containers:{foreign:{}}},{containers:[]},{containers:null}])assert.throws(()=>validateRecoveryNetwork({...network,...change},id));
});
test('only the bound never-started installer may be attached before removal; afterwards the network must be empty',()=>{
 const installer={Id:'a'.repeat(64),State:{Status:'initialized',Running:false,Paused:false,Restarting:false,Pid:1234,StartedAt:'0001-01-01T00:00:00Z',FinishedAt:'0001-01-01T00:00:00Z'}};
 const network={id:'c'.repeat(64),name:`bifrost-${id}`,driver:'bridge',labels:{'io.bifrost.instance-id':id},containers:{[installer.Id]:{name:`bifrost-install-${id}`,interfaces:{}}}};
 assert.doesNotThrow(()=>validateRecoveryNetwork(network,id,installer));
 assert.throws(()=>validateRecoveryNetwork(network,id));
 for(const changed of [{...installer,Id:'b'.repeat(64)},{...installer,State:{...installer.State,Running:true}},{...installer,State:{...installer.State,StartedAt:'2026-01-01T00:00:00Z'}}])assert.throws(()=>validateRecoveryNetwork(network,id,changed));
 for(const containers of [{...network.containers,['b'.repeat(64)]:{name:'foreign'}},{[installer.Id]:{name:'foreign'}},{['b'.repeat(64)]:{name:`bifrost-install-${id}`}}])assert.throws(()=>validateRecoveryNetwork({...network,containers},id,installer));
});
test('failed recovery reports bounded stage and preservation status without raw errors or secrets',()=>{
 const privateValue='SYNTHETIC_PRIVATE_VALUE';
 const result=recoveryFailure('installer-remove',{message:privateValue,stderr:privateValue,recoveryEvidenceRef:privateValue},true);
 assert.equal(result.readOnly,false);assert.equal(result.serviceStateVerificationRequired,true);assert.equal(JSON.stringify(result).includes(privateValue),false);
 assert.equal(recoveryFailure('private-value',{}).stage,'complete-read-only-review');
 const evidence=`${id}-22222222-2222-4222-8222-222222222222`;
 assert.equal(recoveryFailure('service-restart',{runtimeRecoveryCompleted:true,recoveryEvidenceRef:evidence},true).runtimeRecoveryCompleted,true);
 assert.equal(recoveryFailure('service-restart',{recoveryEvidenceRef:evidence},true).evidenceRef,evidence);
 assert.deepEqual(recoveryFailure('unused-owned-network',{failedNetworkChecks:['attachments']}).failedNetworkChecks,['attachments']);
 assert.equal(JSON.stringify(recoveryFailure('unused-owned-network',{failedNetworkChecks:[privateValue]})).includes(privateValue),false);
});
