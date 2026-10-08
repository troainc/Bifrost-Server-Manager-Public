import test from 'node:test';
import assert from 'node:assert/strict';
import { neverStarted, neverStartedFailures, retainedRequest, reviewFailure } from '../scripts/inspect-unstarted-provisioning.mjs';
test('read-only review accepts only initialized, never-started, non-running installer state',()=>{
 const state={Status:'initialized',Running:false,Paused:false,Restarting:false,Pid:0,StartedAt:'0001-01-01T00:00:00Z',FinishedAt:'0001-01-01T00:00:00Z'};
 assert.equal(neverStarted(state),true);
 // Podman's OCI init process has a PID before its workload is started.
 for(const Pid of [1,9876,1234567,2147483647])assert.equal(neverStarted({...state,Pid}),true);
 for(const changed of [{Status:'exited'},{Status:'created'},{Status:'running'},{Running:true},{Paused:true},{Restarting:true},{Pid:-1},{Pid:'9876'},{Pid:null},{Pid:1.5},{Pid:2147483648},{StartedAt:'2026-10-08T10:00:00Z'},{FinishedAt:'2026-10-08T10:00:00Z'},{StartedAt:null}])assert.equal(neverStarted({...state,...changed}),false);
 assert.equal(neverStarted(undefined),false);
 assert.deepEqual(neverStartedFailures({...state,Running:true,Pid:-1}),['Running','Pid']);
});
test('retained request uses the shipped canonical object without parsing or copying it',()=>{
 const request={blueprintId:'space-engineers-1-torch',blueprintDigest:`sha256:${'a'.repeat(64)}`,instanceId:'11111111-1111-4111-8111-111111111111',displayName:'Fixture Torch Test',memoryBytes:8589934592,nanoCpus:3000000000,ports:[{id:'game',hostPort:27016}]};
 assert.equal(retainedRequest({request,profile:{}}),request);
 for(const request of [null,undefined,[],JSON.stringify({instanceId:'example'}),42])assert.throws(()=>retainedRequest({request}));
 assert.throws(()=>retainedRequest(null));
});
test('review failures disclose only fixed check names and allowlisted codes',()=>{
 const secret='example-private-data';
 for(const code of ['ENOENT','EACCES','EPERM'])assert.deepEqual(reviewFailure('retained-manifest',{code,message:secret,stderr:secret}),{readOnly:true,reviewPassed:false,stage:'retained-manifest',code});
 assert.deepEqual(reviewFailure(secret,{code:secret,message:secret,stderr:secret}),{readOnly:true,reviewPassed:false,stage:'unknown-check',code:'REVIEW_REFUSED'});
 for(const stage of ['installer-never-started','pinned-node-oci-reader','oci-process-confinement','installer-container-sandbox','retained-lock-binding'])assert.equal(reviewFailure(stage,Error(secret)).stage,stage);
 assert.deepEqual(reviewFailure('installer-never-started',{failedStateChecks:['Running','StartedAt']}),{readOnly:true,reviewPassed:false,stage:'installer-never-started',code:'REVIEW_REFUSED',failedStateChecks:['Running','StartedAt']});
 assert.equal(Object.hasOwn(reviewFailure('installer-never-started',{failedStateChecks:[secret]}),'failedStateChecks'),false);
});
