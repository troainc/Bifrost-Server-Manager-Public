import datetime,hashlib,importlib.util,json,pathlib,subprocess,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('manifest',ROOT/'scripts/release-manifest.py');manifest=importlib.util.module_from_spec(spec);spec.loader.exec_module(manifest)
class SignedRelease(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.temp.name)
        self.private=self.root/'private.pem';self.public=self.root/'public.pem'
        subprocess.run(['openssl','genpkey','-algorithm','ED25519','-out',str(self.private)],check=True,capture_output=True)
        subprocess.run(['openssl','pkey','-in',str(self.private),'-pubout','-out',str(self.public)],check=True,capture_output=True)
        der=subprocess.check_output(['openssl','pkey','-pubin','-in',str(self.public),'-outform','DER'])
        self.identity=hashlib.sha256(der).hexdigest();self.asset=self.root/'package.bin';self.asset.write_bytes(b'synthetic exact candidate bytes')
        now=datetime.datetime.now(datetime.timezone.utc)
        self.data={'schemaVersion':1,'version':'v0.1.0-local.34','signerSha256':self.identity,'privateSourceSha':'a'*40,'publicSourceSha':'b'*40,'createdAt':now.isoformat(),'expiresAt':(now+datetime.timedelta(days=1)).isoformat(),'artifacts':[{'name':'package.bin','size':self.asset.stat().st_size,'sha256':hashlib.sha256(self.asset.read_bytes()).hexdigest()}]}
        self.path=self.root/'release-manifest.json';self.sig=self.root/'release-manifest.sig';self.sign()
    def tearDown(self):self.temp.cleanup()
    def sign(self):
        self.path.write_text(json.dumps(self.data))
        subprocess.run(['openssl','pkeyutl','-sign','-inkey',str(self.private),'-rawin','-in',str(self.path),'-out',str(self.sig)],check=True,capture_output=True)
    def verify(self,**kwargs):
        return manifest.verify(self.path,self.sig,self.public,kwargs.get('signer',self.identity),kwargs.get('version',self.data['version']),{'package.bin':self.asset},**({'now':kwargs['now']}if'now'in kwargs else{}))
    def test_exact_offline_signature_and_bytes_pass(self):self.assertEqual(self.verify()['privateSourceSha'],'a'*40)
    def test_changed_artifact_and_signature_refuse(self):
        self.asset.write_bytes(b'changed candidate')
        with self.assertRaises(ValueError):self.verify()
        self.asset.write_bytes(b'synthetic exact candidate bytes');self.sig.write_bytes(bytes(64))
        with self.assertRaises(subprocess.CalledProcessError):self.verify()
    def test_wrong_version_identity_and_expiry_refuse(self):
        with self.assertRaises(ValueError):self.verify(version='v0.1.0-wrong')
        with self.assertRaises(ValueError):self.verify(signer='0'*64)
        with self.assertRaises(ValueError):self.verify(now=datetime.datetime.now(datetime.timezone.utc).timestamp()+2*86400)
    def test_duplicate_paths_and_unexpected_fields_refuse_even_if_signed(self):
        self.data['artifacts']*=2;self.sign()
        with self.assertRaises(ValueError):self.verify()
        self.data['artifacts']=self.data['artifacts'][:1];self.data['downloadUrl']='https://untrusted.invalid';self.sign()
        with self.assertRaises(ValueError):self.verify()
    def test_unsafe_links_and_missing_signatures_refuse(self):
        self.sig.unlink()
        with self.assertRaises(ValueError):self.verify()
    def test_standalone_bootstraps_share_exact_trust_anchor_and_verifier(self):
        expected=(ROOT/'scripts/release-bootstrap.sh').read_text().strip()
        for name in ('install.sh','update.sh'):
            source=(ROOT/name).read_text();actual=source.split('# BEGIN SIGNED_RELEASE_BOOTSTRAP',1)[1].split('# END SIGNED_RELEASE_BOOTSTRAP',1)[0]
            self.assertEqual('# BEGIN SIGNED_RELEASE_BOOTSTRAP'+actual+'# END SIGNED_RELEASE_BOOTSTRAP',expected)
