import test from 'node:test';
import assert from 'node:assert/strict';
import {changeServerPort,changeProfilePort} from '../scripts/change-torch-game-port.mjs';
test('changes only ServerPort and preserves all other dedicated configuration bytes',()=>{
  const before=Buffer.from('<Config>\r\n<ServerPort>27016</ServerPort><SteamPort>8766</SteamPort><World>Keep</World>\r\n</Config>');
  assert.equal(changeServerPort(before,27016,2750).toString(),before.toString().replace('27016','2750'));
});
test('refuses ambiguous, unexpected and out-of-range port settings',()=>{
  for(const xml of ['<ServerPort>1234</ServerPort>','<ServerPort>27016</ServerPort><ServerPort>27016</ServerPort>','<!--<ServerPort>27016</ServerPort>--><ServerPort>27016</ServerPort>','<!DOCTYPE x><ServerPort>27016</ServerPort>'])assert.throws(()=>changeServerPort(Buffer.from(xml),27016,2750));
  for(const port of [0,1023,65536,1.5])assert.throws(()=>changeServerPort(Buffer.from('<ServerPort>27016</ServerPort>'),27016,port));
});
test('updates both container and host allocation, all approved package bindings, and leaves Steam/resources intact',()=>{
  const old={sandbox:{imageId:'UNCHANGED',maxMemoryBytes:8192,publishedPorts:[{hostIp:'0.0.0.0',hostPort:27016,containerPort:27016,protocol:'udp'},{hostIp:'0.0.0.0',hostPort:8766,containerPort:8766,protocol:'udp'}]},operations:{packages:[{blueprint:{id:'space-engineers-1-torch',gamePort:27016,steamPort:8766}},{blueprint:{schemaVersion:2,id:'space-engineers-1-torch',ports:[{id:'game',port:27016,protocol:'udp'},{id:'steam',port:8766,protocol:'udp'}]}}]}};
  const before=structuredClone(old),next=changeProfilePort(old,27016,2750);assert.deepEqual(old,before);assert.deepEqual(next.sandbox.publishedPorts[0],{hostIp:'0.0.0.0',hostPort:2750,containerPort:2750,protocol:'udp'});assert.deepEqual(next.sandbox.publishedPorts[1],old.sandbox.publishedPorts[1]);assert.equal(next.operations.packages[0].blueprint.gamePort,2750);assert.equal(next.operations.packages[1].blueprint.ports[0].port,2750);assert.equal(next.sandbox.imageId,old.sandbox.imageId);
});
test('refuses port collisions and unrelated game package bindings',()=>{
  const old={sandbox:{publishedPorts:[{hostPort:27016,containerPort:27016,protocol:'udp'},{hostPort:8766,containerPort:8766,protocol:'udp'}]}};assert.throws(()=>changeProfilePort(old,27016,8766));assert.throws(()=>changeProfilePort({...old,operations:{packages:[{blueprint:{id:'another-game'}}]}},27016,2750));
});
