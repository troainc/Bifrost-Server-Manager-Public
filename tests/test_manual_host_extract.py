import pathlib,subprocess,sys,tempfile,unittest,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
SCRIPT=(ROOT/'install.sh').read_text()
EXTRACT=SCRIPT.split("<<'HOST_ZIP_PY'\n",1)[1].split('\nHOST_ZIP_PY',1)[0]
class ManualHostExtract(unittest.TestCase):
 def test_fresh_actual_manual_destination_is_promoted(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d).resolve();dest=root/'package';archive=root/'host.zip'
   with zipfile.ZipFile(archive,'w') as z:z.writestr('dist/main.js','compiled');z.writestr('install-agent.sh','verified installer')
   for attempt in range(2):
    result=subprocess.run([sys.executable,'-',str(archive),str(dest)],input=EXTRACT,text=True,capture_output=True)
    self.assertEqual(result.returncode,0,result.stderr);self.assertEqual((dest/'dist/main.js').read_text(),'compiled')
   (dest/'dist/main.js').write_text('retained changes')
   result=subprocess.run([sys.executable,'-',str(archive),str(dest)],input=EXTRACT,text=True,capture_output=True)
   self.assertNotEqual(result.returncode,0);self.assertEqual((dest/'dist/main.js').read_text(),'retained changes')
 def test_manual_invocation_does_not_precreate_destination(self):
  before=SCRIPT.split("<<'HOST_ZIP_PY'",1)[0].rsplit('install_instance_host()',1)[1]
  self.assertNotIn('mkdir -m 0700 "$package"',before)
 def test_retained_packages_work_without_python311_file_digest(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d).resolve();dest=root/'package';archive=root/'host.zip'
   with zipfile.ZipFile(archive,'w') as z:z.writestr('dist/main.js','compiled')
   for marker in ['HOST_ZIP_PY','AUTO_HOST_ZIP_PY']:
    actual=SCRIPT.split("<<'"+marker+"'\n",1)[1].split('\n'+marker,1)[0]
    compatible="import hashlib\nif hasattr(hashlib,'file_digest'):delattr(hashlib,'file_digest')\n"+actual
    for attempt in range(2):
     result=subprocess.run([sys.executable,'-',str(archive),str(dest)],input=compatible,text=True,capture_output=True)
     self.assertEqual(result.returncode,0,result.stderr)
if __name__=='__main__':unittest.main()
