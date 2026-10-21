#!/usr/bin/env python3
"""Bind classic/config and containerd/index image IDs to the exact saved archive."""
import importlib.util,json,pathlib,re,sys
spec=importlib.util.spec_from_file_location('archive_verifier',pathlib.Path(__file__).with_name('verify-image-archive.py'))
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
archive,lock,output=map(pathlib.Path,sys.argv[1:])
expected=json.loads(lock.read_text());identities=module.archive_identities(archive)
if not isinstance(expected,dict)or len(expected)!=3:raise SystemExit('Exactly three locked image subjects required.')
result={}
for tag,configuration in expected.items():
    item=identities.get(tag)
    if not re.fullmatch(r'sha256:[a-f0-9]{64}',configuration)or not item or item['config']!=configuration:raise SystemExit('Image archive/lock subject mismatch.')
    result[tag]={'config':configuration,'ids':sorted(item['ids'])}
with output.open('x',encoding='utf8')as handle:json.dump(result,handle,indent=2);handle.write('\n')
