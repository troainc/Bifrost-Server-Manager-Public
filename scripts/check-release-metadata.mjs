import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';import {resolve,dirname} from 'node:path';import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..'),read=path=>readFileSync(resolve(root,path),'utf8'),release=JSON.parse(read('release.json'));
assert.match(release.version,/^v\d+\.\d+\.\d+-alpha\.\d+$/);assert.equal(release.displayLabel,'Bifrost Control Plane · '+release.version+' - '+release.buildName);assert.equal(release.status,'candidate');
for(const path of ['install.sh','update.sh'])assert.ok(read(path).split(/\r?\n/).includes('VERSION='+release.version),'Version drift: '+path);
for(const line of ['BIFROST_VERSION='+release.version,'BIFROST_CONTROL_PLANE_IMAGE=bifrost/control-plane:'+release.version,'BIFROST_WEB_IMAGE=bifrost/web:'+release.version])assert.ok(read('.env.example').split(/\r?\n/).includes(line),'Environment version drift');
for(const path of ['README.md','CHANGELOG.md','CONTEXT.md','LOGS.md'])assert.ok(read(path).includes(release.version)&&read(path).includes(release.buildName),'Missing release identity: '+path);
assert.ok(read('CHANGELOG.md').includes('## '+release.version+' - '+release.buildName));console.log('PASS public candidate release identity: '+release.displayLabel);
