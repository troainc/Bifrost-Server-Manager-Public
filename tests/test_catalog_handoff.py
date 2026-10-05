import base64,hashlib,importlib.util,json,pathlib,subprocess,tempfile,unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('catalog_handoff',ROOT/'scripts/install-reviewed-catalog.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
def openssl(*args):return subprocess.run(['openssl',*map(str,args)],check=True,capture_output=True).stdout
def b64(data):return base64.urlsafe_b64encode(data).decode().rstrip('=')

class CatalogHandoff(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='.bifrost-catalog-test-',dir=ROOT);self.addCleanup(self.temp.cleanup)
        self.root=pathlib.Path(self.temp.name).resolve();self.source=self.root/'source';self.source.mkdir();self.dest=self.root/'dest';self.dest.mkdir()
        key=self.root/'test-only-private.pem';openssl('genpkey','-algorithm','ed25519','-out',key)
        pem=openssl('pkey','-in',key,'-pubout');der=openssl('pkey','-in',key,'-pubout','-outform','DER')
        self.key='ed25519-sha256:'+hashlib.sha256(der).hexdigest()
        # Synthetic data-only record: real per-recipe contracts are exercised in the private repository.
        records=[{'manifest':{'id':'test-only','download':{'gameId':'minecraft-java'}},'digest':'sha256:'+'a'*64,'keyId':self.key,'signature':'b'*86}]
        catalog=json.dumps(records).encode();trust=json.dumps({self.key:pem.decode()}).encode()
        metadata={'schemaVersion':1,'publisherKeyId':self.key,'catalogSha256':hashlib.sha256(catalog).hexdigest(),'trustSha256':hashlib.sha256(trust).hexdigest(),'targets':[{'id':'test-only','digest':records[0]['digest']}]}
        payload=json.dumps(metadata).encode();(self.root/'payload').write_bytes(payload)
        signature=openssl('pkeyutl','-sign','-inkey',key,'-rawin','-in',self.root/'payload')
        for name,data in [('provisioning-catalog.json',catalog),('provisioning-trust.json',trust),('catalog-release.json',json.dumps({'signedPayload':b64(payload),'signature':b64(signature)}).encode())]:(self.source/name).write_bytes(data)
    def test_valid_signed_handoff_copies_only_public_data(self):
        (self.source/'private-should-not-copy.pem').write_text('PRIVATE KEY')
        module.install(self.source,self.key,self.dest)
        self.assertEqual(sorted(p.name for p in self.dest.iterdir()),['catalog-release.json','provisioning-catalog.json','provisioning-trust.json'])
        with self.assertRaises(ValueError):module.install(self.source,self.key,self.dest)
    def test_changed_catalog_cannot_be_authorized_by_rehashing_unsigned_metadata(self):
        p=self.source/'provisioning-catalog.json';p.write_bytes(p.read_bytes()+b' ')
        with self.assertRaisesRegex(ValueError,'hashes'):module.install(self.source,self.key,self.dest)
        self.assertEqual(list(self.dest.iterdir()),[])
    def test_wrong_publisher_and_forged_signature_are_rejected(self):
        with self.assertRaises(ValueError):module.install(self.source,'ed25519-sha256:'+'f'*64,self.dest)
        p=self.source/'catalog-release.json';release=json.loads(p.read_bytes());release['signature']='A'*86;p.write_text(json.dumps(release))
        with self.assertRaisesRegex(ValueError,'signature'):module.install(self.source,self.key,self.dest)
    def test_private_key_marker_never_enters_package(self):
        (self.source/'provisioning-trust.json').write_text('PRIVATE KEY')
        with self.assertRaisesRegex(ValueError,'Private keys'):module.install(self.source,self.key,self.dest)

if __name__=='__main__':unittest.main()
