import test from 'node:test';
import assert from 'node:assert/strict';
import {summarizeConfig,summarizeLedger,summarizeContainer,summarizeManifest} from '../scripts/diagnose-provisioning.mjs';
test('read-only diagnostics omit credentials, filenames, commands, image credentials and container environment',()=>{
 const id='755552ce-a981-41c6-9227-62821bd9ddd6',secret='DO_NOT_PRINT_TOKEN';
 const config=summarizeConfig({hostId:id,token:secret,tokenFile:secret,profiles:[{instanceId:id,displayName:secret,containerName:secret}],provisioning:{root:secret}});
 const ledger=summarizeLedger({[id]:'running',secret});
 const container=summarizeContainer([{Config:{Env:[secret],Cmd:[secret],Labels:{'io.bifrost.instance-id':id,'io.bifrost.managed-by':'bifrost',secret}},State:{Status:'exited',Error:secret}}],id);
 assert.equal(JSON.stringify({config,ledger,container}).includes(secret),false);assert.equal(container.matchesManagedIdentity,true);assert.equal(container.state,'exited');assert.equal(config.profileCount,1);
 assert.equal(summarizeConfig({hostId:secret,profiles:[{instanceId:secret}]}).hostId,null);
 assert.equal(summarizeContainer([{State:{Status:secret}}],id).state,'unknown');
 const manifest=summarizeManifest({request:JSON.stringify({instanceId:id,blueprintDigest:'sha256:'+'a'.repeat(64),displayName:secret}),profile:{token:secret}});
 assert.equal(manifest.instanceId,id);assert.equal(JSON.stringify(manifest).includes(secret),false);
 assert.equal(summarizeContainer([{State:{Status:'exited',ExitCode:17,Error:secret}}],id).exitCode,17);
});
