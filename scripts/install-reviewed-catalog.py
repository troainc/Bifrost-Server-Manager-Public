"""Verify the pinned publisher's signature binding the exact public catalog bytes.
Controller and Host additionally verify every recipe's signature and schema.
"""
import base64,hashlib,json,pathlib,re,stat,subprocess,sys,tempfile

def install(source,expected_key,destination):
    source=pathlib.Path(source).absolute();destination=pathlib.Path(destination).absolute()
    if source.resolve()!=source or destination.resolve()!=destination:
        raise ValueError('Catalog paths must not traverse links')
    def read(name,limit):
        path=source/name;info=path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_size>limit:
            raise ValueError('Catalog input must be a bounded regular file')
        data=path.read_bytes()
        if b'PRIVATE KEY' in data:raise ValueError('Private keys are not distribution inputs')
        return data
    release_bytes=read('catalog-release.json',65536);release=json.loads(release_bytes)
    catalog=read('provisioning-catalog.json',1048576);keys=read('provisioning-trust.json',65536)
    trust=json.loads(keys)
    if not isinstance(trust,dict) or list(trust)!=[expected_key] or not isinstance(trust[expected_key],str):raise ValueError('Use one exact pinned public publisher key')
    pem=trust[expected_key]
    if not pem.startswith('-----BEGIN PUBLIC KEY-----\n') or not pem.strip().endswith('-----END PUBLIC KEY-----'):raise ValueError('Expected public Ed25519 key')
    der=base64.b64decode(''.join(pem.strip().splitlines()[1:-1]),validate=True)
    if len(der)!=44 or not der.startswith(bytes.fromhex('302a300506032b6570032100')) or 'ed25519-sha256:'+hashlib.sha256(der).hexdigest()!=expected_key:
        raise ValueError('Publisher key identity/type differs')
    if not isinstance(release,dict) or set(release)!={'signedPayload','signature'} or not re.fullmatch(r'[A-Za-z0-9_-]{1,65536}',release.get('signedPayload','')) or not re.fullmatch(r'[A-Za-z0-9_-]{86}',release.get('signature','')):
        raise ValueError('Invalid signed catalog release')
    decode=lambda value:base64.urlsafe_b64decode(value+'='*((-len(value))%4))
    payload=decode(release['signedPayload']);signature=decode(release['signature'])
    with tempfile.TemporaryDirectory(prefix='.bifrost-public-catalog-',dir=destination) as temp:
        temp=pathlib.Path(temp)
        for name,data in [('public.pem',pem.encode()),('payload',payload),('signature',signature)]:
            (temp/name).write_bytes(data);(temp/name).chmod(0o600)
        result=subprocess.run(['openssl','pkeyutl','-verify','-pubin','-inkey',str(temp/'public.pem'),'-rawin','-in',str(temp/'payload'),'-sigfile',str(temp/'signature')],capture_output=True,timeout=15)
        if result.returncode:raise ValueError('Catalog release signature is invalid')
    metadata=json.loads(payload)
    if metadata.get('schemaVersion')!=1 or metadata.get('publisherKeyId')!=expected_key:
        raise ValueError('Catalog publisher differs from the explicit approved identity')
    if hashlib.sha256(catalog).hexdigest()!=metadata.get('catalogSha256') or hashlib.sha256(keys).hexdigest()!=metadata.get('trustSha256'):
        raise ValueError('Catalog handoff hashes differ')
    records=json.loads(catalog)
    if not isinstance(records,list) or not 1<=len(records)<=64:raise ValueError('Catalog must contain reviewed targets')
    targets=[]
    for r in records:
        if not isinstance(r,dict) or set(r)!={'manifest','digest','keyId','signature'} or r['keyId']!=expected_key or not isinstance(r['manifest'],dict) or not r['manifest'].get('download') or 'windows' in r['manifest']:
            raise ValueError('Only signed Linux download records are distribution inputs')
        targets.append({'id':r['manifest']['id'],'digest':r['digest']})
    if metadata.get('targets')!=targets:raise ValueError('Catalog target list differs')
    # Only these three public data files are copied; never arbitrary siblings or source.
    for name,data in [('provisioning-catalog.json',catalog),('provisioning-trust.json',keys),('catalog-release.json',release_bytes)]:
        output=destination/name
        if output.exists() or output.is_symlink():raise ValueError('Destination must not replace existing catalog/policy')
    for name,data in [('provisioning-catalog.json',catalog),('provisioning-trust.json',keys),('catalog-release.json',release_bytes)]:
        with (destination/name).open('xb') as f:f.write(data)
        (destination/name).chmod(0o644)
    return targets

if __name__=='__main__':
    if len(sys.argv)!=4:raise SystemExit('Usage: install-reviewed-catalog.py APPROVED-DATA-DIRECTORY EXPECTED-PUBLISHER-KEY-ID NEW-DESTINATION-DIRECTORY')
    print(json.dumps({'installed':install(*sys.argv[1:])}))
