"""Exercise the installer's actual Host checksum reader on bytes, not text I/O."""
import hashlib,pathlib,subprocess,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
SCRIPT=(ROOT/'install.sh').read_text(encoding='utf-8')
CODE=SCRIPT.split("<<'MATCHED_HOST_CHECKSUM_PY'\n",1)[1].split('\nMATCHED_HOST_CHECKSUM_PY',1)[0]

class MatchedHostChecksum(unittest.TestCase):
 def check(self,inventory,archive=b'signed synthetic Host ZIP'):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);(root/'SHA256SUMS').write_bytes(inventory);(root/'host.zip').write_bytes(archive)
   return subprocess.run([sys.executable,'-',str(root)],input=CODE,text=True,capture_output=True)
 def line(self,archive=b'signed synthetic Host ZIP'):
  return hashlib.sha256(archive).hexdigest().encode()+b'  bifrost-linux-host-agent.zip'
 def test_lf_crlf_and_final_line_without_newline(self):
  for ending in [b'\n',b'\r\n',b'']:
   with self.subTest(ending=ending):self.assertEqual(self.check(b'0'*64+b'  unrelated.tar.gz\n'+self.line()+ending).returncode,0)
 def test_mixed_line_endings_are_accepted(self):
  self.assertEqual(self.check(b'0'*64+b'  other.zip\r\n'+self.line()+b'\n').returncode,0)
 def test_missing_duplicate_malformed_or_wrong_checksum_refuses(self):
  valid=self.line()
  for data in [b'',b'\n',b'0'*64+b'  other.zip\n',valid+b'\n'+valid+b'\r\n',valid.replace(b'  ',b' '),valid[:10]+b'\r'+valid[10:],b'0'*64+b'  bifrost-linux-host-agent.zip\n']:
   with self.subTest(data=data):self.assertNotEqual(self.check(data).returncode,0)
 def test_changed_zip_refuses_for_both_line_endings(self):
  for ending in [b'\n',b'\r\n']:self.assertNotEqual(self.check(self.line()+ending,b'tampered archive').returncode,0)
 def test_published_test51_inventory_is_accepted_if_fixture_is_present(self):
  import os
  directory=os.environ.get('BIFROST_TEST51_RELEASE_DIRECTORY')
  if not directory:self.skipTest('Exact immutable Test 51 fixtures not supplied')
  root=pathlib.Path(directory)
  result=self.check((root/'SHA256SUMS').read_bytes(),(root/'bifrost-linux-host-agent.zip').read_bytes())
  self.assertEqual(result.returncode,0,result.stderr)
 def test_signature_verification_still_precedes_the_checksum_reader(self):
  body=SCRIPT.split('prepare_automatic_instance_host() {',1)[1]
  self.assertLess(body.index('verify_signed_release "$stage" host.zip'),body.index('verify_matched_host_checksum "$stage"'))

if __name__=='__main__':unittest.main()
