"""Exercise the real standalone bootstrap with ephemeral signer and local files."""
import datetime,hashlib,json,os,pathlib,subprocess,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
PIN='1dba79e7a3d2608b42a5324089d4db548567999210ffbf3dd96ce5cb63a92e6a'
class OfflineRelease(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.temp.name)
        self.assets=self.root/'signed release [local]';self.assets.mkdir()
        self.key=self.root/'private.pem'
        subprocess.run(['openssl','genpkey','-algorithm','ED25519','-out',str(self.key)],check=True,capture_output=True)
        public=self.assets/'release-signing-public.pem'
        subprocess.run(['openssl','pkey','-in',str(self.key),'-pubout','-out',str(public)],check=True,capture_output=True)
        der=subprocess.check_output(['openssl','pkey','-pubin','-in',str(public),'-outform','DER'])
        self.identity=hashlib.sha256(der).hexdigest()
        (self.assets/'install.sh').write_bytes(b'#!/bin/bash\nexit 99\n')
        (self.assets/'payload.bin').write_bytes(b'exact signed payload')
        (self.assets/'release-manifest.py').write_bytes((ROOT/'scripts/release-manifest.py').read_bytes())
        now=datetime.datetime.now(datetime.timezone.utc)
        self.statement={'schemaVersion':1,'version':'v0.1.0-installtest.34','signerSha256':self.identity,'privateSourceSha':'a'*40,'publicSourceSha':'b'*40,'createdAt':now.isoformat(),'expiresAt':(now+datetime.timedelta(days=1)).isoformat(),'artifacts':[{'name':p.name,'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in self.assets.iterdir()]}
        self.sign()
        self.bootstrap=(ROOT/'scripts/release-bootstrap.sh').read_text().replace(PIN,self.identity)
    def tearDown(self):self.temp.cleanup()
    def sign(self):
        (self.assets/'release-manifest.json').write_text(json.dumps(self.statement))
        subprocess.run(['openssl','pkeyutl','-sign','-inkey',str(self.key),'-rawin','-in',str(self.assets/'release-manifest.json'),'-out',str(self.assets/'release-manifest.sig')],check=True,capture_output=True)
    def run_bash(self,action,*args):
        source='set -Eeuo pipefail\nVERSION=v0.1.0-installtest.34\nfail(){ echo "$*" >&2;exit 2; }\n'+self.bootstrap+'\n'+action
        return subprocess.run(['bash','-c',source,'offline-test',*map(str,args)],capture_output=True,text=True,timeout=15,env={**os.environ,'BIFROST_RELEASE_DIRECTORY':str(self.assets),'TMPDIR':str(self.root)})
    def verify(self):return self.run_bash('verify_local_release "$1"',self.assets)
    def test_all_signed_local_assets_verify_without_executing_installer(self):
        result=self.verify();self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('PASS all signed local artifact hashes',result.stdout)
        self.assertIn('no account, service, database',result.stdout)
    def test_modified_payload_and_wrong_version_refuse(self):
        (self.assets/'payload.bin').write_bytes(b'changed')
        self.assertNotEqual(self.verify().returncode,0)
        (self.assets/'payload.bin').write_bytes(b'exact signed payload')
        self.statement['version']='v0.1.0-wrong';self.sign()
        self.assertNotEqual(self.verify().returncode,0)
    def test_changed_verifier_is_never_executed(self):
        sentinel=self.root/'must-not-exist'
        (self.assets/'release-manifest.py').write_text('from pathlib import Path;Path('+repr(str(sentinel))+').touch()')
        self.assertNotEqual(self.verify().returncode,0)
        self.assertFalse(sentinel.exists())
    def test_missing_metadata_and_wrong_signer_refuse(self):
        sig=self.assets/'release-manifest.sig';sig.unlink()
        self.assertNotEqual(self.verify().returncode,0)
        self.sign();self.bootstrap=self.bootstrap.replace(self.identity,'0'*64)
        self.assertNotEqual(self.verify().returncode,0)
    def test_asset_links_and_reused_destination_are_refused(self):
        installed=self.root/'existing';installed.write_bytes(b'retained')
        result=self.run_bash('fetch_release_asset payload.bin "$1"',installed)
        self.assertNotEqual(result.returncode,0);self.assertEqual(installed.read_bytes(),b'retained')
        source=self.assets/'install.sh';retained=self.root/'retained-installer';source.rename(retained)
        source.symlink_to(retained)
        self.assertNotEqual(self.verify().returncode,0)
        source.unlink();os.link(retained,source)
        self.assertNotEqual(self.verify().returncode,0)
    def test_relative_and_linked_source_directories_are_refused(self):
        result=self.run_bash('verify_local_release ./relative-missing')
        self.assertNotEqual(result.returncode,0)
        alias=self.root/'alias';alias.symlink_to(self.assets,target_is_directory=True)
        self.assertNotEqual(self.run_bash('verify_local_release "$1"',alias).returncode,0)

    def test_missing_prerequisites_decline_or_missing_compose_never_download_vendor_tools(self):
        source=(ROOT/'install.sh').read_text()
        sections=[(source.index('  if ! command -v dockerd-rootless-setuptool.sh'), '  export DOCKER_HOST='),(source.index('  if ! docker compose version >/dev/null'),'  mkdir -p "$HOME/.config/bifrost"')]
        for start,delimiter in sections:
            block=source[start:source.index(delimiter,start)]
            home=self.root/'prerequisite-home';home.mkdir(exist_ok=True)
            sentinel=home/'unexpected-download'
            helper=source[source.index('prepare_testing_prerequisites() {'):source.index('bootstrap_prerequisites() {')]
            harness='set -Eeuo pipefail\nfail(){ echo "$*" >&2;exit 2; }\ncommand(){ return 1; }\ndocker(){ return 1; }\nfetch(){ touch "$HOME/unexpected-download"; }\nfetch_release_asset(){ touch "$HOME/unexpected-download"; }\n'+helper+block
            result=subprocess.run(['bash','-c',harness],env={**os.environ,'HOME':str(home),'TMPDIR':str(self.root)},input='DECLINE\n',capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertRegex(result.stderr,'independently reviewed|independently reviewed, patched')
            self.assertFalse(sentinel.exists())

    def test_existing_rootless_runtime_is_used_without_download_or_reinstall(self):
        source=(ROOT/'install.sh').read_text()
        start=source.index('  if ! command -v dockerd-rootless-setuptool.sh')
        block=source[start:source.index('\n}\n',start)]
        home=self.root/'existing-runtime-home';home.mkdir()
        harness='''set -Eeuo pipefail
fail(){ echo "$*" >&2;exit 2; }
fetch(){ echo unexpected-download >&2;exit 90; }
dockerd-rootless-setuptool.sh(){ echo unexpected-reinstall >&2;exit 91; }
rootlesskit(){ return 0; }
docker(){
  if [[ "$*" == "info --format {{json .SecurityOptions}}" ]];then echo '["name=rootless"]';fi
  return 0
}
loginctl(){ echo yes; }
uid=1234
export XDG_RUNTIME_DIR="$HOME"
'''+block
        result=subprocess.run(['bash','-c',harness],env={**os.environ,'HOME':str(home),'TMPDIR':str(self.root)},capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('Prerequisites ready',result.stdout)
        self.assertIn('1234/docker.sock',(home/'.config/bifrost/environment.sh').read_text())
