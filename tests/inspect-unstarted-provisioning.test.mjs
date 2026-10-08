import test from 'node:test';
import assert from 'node:assert/strict';
import { neverStarted } from '../scripts/inspect-unstarted-provisioning.mjs';
test('read-only review accepts only initialized, never-started, non-running installer state',()=>{
 const state={Status:'initialized',Running:false,Paused:false,Restarting:false,Pid:0,StartedAt:'0001-01-01T00:00:00Z',FinishedAt:'0001-01-01T00:00:00Z'};
 assert.equal(neverStarted(state),true);
 for(const changed of [{Status:'exited'},{Status:'created'},{Status:'running'},{Running:true},{Paused:true},{Restarting:true},{Pid:1},{StartedAt:'2026-10-08T10:00:00Z'},{FinishedAt:'2026-10-08T10:00:00Z'},{StartedAt:null}])assert.equal(neverStarted({...state,...changed}),false);
 assert.equal(neverStarted(undefined),false);
});
