"""Real offline signature/checksum/extraction stages; no accounts/services/network."""
import os,pathlib,subprocess,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
SCRIPT=(ROOT/'install.sh').read_text(encoding='utf-8')
BOOTSTRAP=SCRIPT.split('# BEGIN SIGNED_RELEASE_BOOTSTRAP\n',1)[1].split('# END SIGNED_RELEASE_BOOTSTRAP',1)[0]
CHECKSUM='verify_matched_host_checksum() {'+SCRIPT.split('verify_matched_host_checksum() {',1)[1].split('\nprepare_automatic_instance_host()',1)[0]
EXTRACT=SCRIPT.split("<<'AUTO_HOST_ZIP_PY'\n",1)[1].split('\nAUTO_HOST_ZIP_PY',1)[0]

@unittest.skipUnless(sys.platform=='linux' and os.environ.get('BIFROST_TEST51_RELEASE_DIRECTORY'),'Exact immutable Test 51 fixtures and Linux required')
class SignedHostChecksumStage(unittest.TestCase):
 def run_stage(self,tamper=False):
  with tempfile.TemporaryDirectory(prefix='signed-host-stage-')as d:
   root=pathlib.Path(d);stage=root/'stage';stage.mkdir(mode=0o755);parent=root/'owned-packages';parent.mkdir(mode=0o700)
   script='set -Eeuo pipefail\nVERSION=v0.1.0-installtest.51\nfail(){ printf "%s\\n" "$*" >&2; exit 2; }\n'+BOOTSTRAP+'\n'+CHECKSUM+'\n'
   script+='stage="$1"\nexport BIFROST_RELEASE_DIRECTORY="$2"\nfetch_release_asset bifrost-linux-host-agent.zip "$stage/host.zip"\nfetch_release_asset SHA256SUMS "$stage/SHA256SUMS"\n'
   if tamper:script+='printf X >> "$stage/host.zip"\n'
   script+='verify_signed_release "$stage" host.zip bifrost-linux-host-agent.zip\nverify_matched_host_checksum "$stage"\nprintf "checksum-stage-passed\\n"\n'
   result=subprocess.run(['bash','-c',script,'fixture',str(stage),os.environ['BIFROST_TEST51_RELEASE_DIRECTORY']],text=True,capture_output=True)
   if result.returncode==0:
    extracted=subprocess.run([sys.executable,'-',str(stage/'host.zip'),str(parent/'agent')],input=EXTRACT,text=True,capture_output=True)
    self.assertEqual(extracted.returncode,0,extracted.stderr)
    self.assertTrue((parent/'agent/dist/main.js').is_file())
    self.assertTrue((parent/'agent/dist/configure-se2-provisioning.js').is_file())
   return result
 def test_actual_published_crlf_inventory_signature_checksum_and_extraction(self):
  self.assertNotEqual(os.getuid(),0,'Run the signed extraction stage as an unprivileged user')
  result=self.run_stage();self.assertEqual(result.returncode,0,result.stderr);self.assertIn('checksum-stage-passed',result.stdout)
 def test_tampered_host_fails_signature_before_checksum_or_extraction(self):
  result=self.run_stage(True);self.assertNotEqual(result.returncode,0);self.assertNotIn('checksum-stage-passed',result.stdout)
 def test_old_filter_reproduces_actual_no_formatted_lines_failure(self):
  directory=os.environ['BIFROST_TEST51_RELEASE_DIRECTORY']
  result=subprocess.run(['bash','-o','pipefail','-c',"sed 's/  bifrost-linux-host-agent.zip$/  host.zip/' \"$1/SHA256SUMS\" | grep -E '^[a-f0-9]{64}  host.zip$' | sha256sum --check --status",'fixture',directory],text=True,capture_output=True)
  self.assertNotEqual(result.returncode,0);self.assertIn('no properly formatted checksum lines',result.stderr)
