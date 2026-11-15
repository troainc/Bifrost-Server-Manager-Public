import test from "node:test";
import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import vm from "node:vm";
function exitFor(code,version){let status=0;try{vm.runInNewContext(code,{process:{versions:{node:version},exit:n=>{status=n;throw new Error("fixture exit");}}},{timeout:100});}catch(e){assert.equal(e.message,"fixture exit");}return status;}
test("public Host admission refuses superseded patches",async()=>{const source=await readFile(new URL("../install.sh",import.meta.url),"utf8");const matches=[...source.matchAll(/-e '([^']*const \[major,minor,patch\][^']*)'/g)];assert.equal(matches.length,1);for(const version of ["24.22.1","24.22.2","25.0.0"])assert.notEqual(exitFor(matches[0][1],version),0,version);for(const version of ["24.22.3","24.23.0"])assert.equal(exitFor(matches[0][1],version),0,version);});
