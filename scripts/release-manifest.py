#!/usr/bin/env python3
"""Verify an offline Ed25519-signed, version-bound customer release manifest."""
import argparse
import datetime
import hashlib
import json
import pathlib
import re
import subprocess
import time

def sha256(path):
    digest=hashlib.sha256()
    with path.open('rb') as data:
        for chunk in iter(lambda:data.read(1024*1024),b''):digest.update(chunk)
    return digest.hexdigest()

def verify(manifest,signature,public_key,expected_signer,version,assets,now=None):
    for path,limit in ((manifest,1024*1024),(signature,64),(public_key,4096)):
        if path.is_symlink()or not path.is_file()or path.stat().st_nlink!=1 or not 0<path.stat().st_size<=limit:raise ValueError('Unsafe release verification input.')
    if not re.fullmatch('[a-f0-9]{64}',expected_signer):raise ValueError('Trusted signer fingerprint required.')
    der=subprocess.run(['openssl','pkey','-pubin','-in',str(public_key),'-outform','DER'],check=True,capture_output=True).stdout
    if len(der)!=44 or not der.startswith(bytes.fromhex('302a300506032b6570032100'))or hashlib.sha256(der).hexdigest()!=expected_signer:raise ValueError('Untrusted release signing identity.')
    subprocess.run(['openssl','pkeyutl','-verify','-pubin','-inkey',str(public_key),'-rawin','-in',str(manifest),'-sigfile',str(signature)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    data=json.loads(manifest.read_text())
    required={'schemaVersion','version','signerSha256','privateSourceSha','publicSourceSha','createdAt','expiresAt','artifacts'}
    if not isinstance(data,dict)or set(data)!=required or data['schemaVersion']!=1 or data['version']!=version or data['signerSha256']!=expected_signer:raise ValueError('Release identity mismatch.')
    for key in ('privateSourceSha','publicSourceSha'):
        if not re.fullmatch('[a-f0-9]{40}',data[key]):raise ValueError('Release source revision is invalid.')
    stamp=time.time()if now is None else now
    issued=datetime.datetime.fromisoformat(data['createdAt'].replace('Z','+00:00')).timestamp()
    expires=datetime.datetime.fromisoformat(data['expiresAt'].replace('Z','+00:00')).timestamp()
    if issued>stamp+300 or expires<=stamp or expires<=issued or expires-issued>366*86400:raise ValueError('Release verification statement is expired or invalid.')
    if not isinstance(data['artifacts'],list)or not 1<=len(data['artifacts'])<=100:raise ValueError('Invalid artifact inventory.')
    inventory={}
    for item in data['artifacts']:
        if not isinstance(item,dict)or set(item)!={'name','sha256','size'}or not re.fullmatch('[A-Za-z0-9][A-Za-z0-9._-]{0,159}',item['name'])or '..'in item['name']or not re.fullmatch('[a-f0-9]{64}',item['sha256'])or type(item['size'])is not int or not 0<item['size']<=100*1024**3 or item['name']in inventory:raise ValueError('Invalid or duplicate release artifact.')
        inventory[item['name']]=item
    for name,path in assets.items():
        item=inventory.get(name)
        if not item or path.is_symlink()or not path.is_file()or path.stat().st_nlink!=1 or path.stat().st_size!=item['size']or sha256(path)!=item['sha256']:raise ValueError('Release artifact digest or size mismatch.')
    return data

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('manifest','signature','public-key'):parser.add_argument('--'+name,type=pathlib.Path,required=True)
    parser.add_argument('--expected-signer',required=True);parser.add_argument('--version',required=True);parser.add_argument('--asset',action='append',default=[])
    args=parser.parse_args();assets={}
    for asset in args.asset:
        name,path=asset.split('=',1)
        if name in assets:raise ValueError('Duplicate requested artifact.')
        assets[name]=pathlib.Path(path)
    if not assets:raise ValueError('At least one artifact must be verified.')
    verify(args.manifest,args.signature,args.public_key,args.expected_signer,args.version,assets)
    print('Verified offline release signature, source identities, version and exact artifact bytes.')

if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,TypeError,OSError,subprocess.SubprocessError):raise SystemExit('Release signature/provenance verification failed; installation refused.')
