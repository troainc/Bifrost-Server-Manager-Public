"""Disposable checks for non-root, bounded package extraction and recovery."""
import pathlib,subprocess,sys,tempfile,unittest,zipfile,os,stat
ROOT=pathlib.Path(__file__).resolve().parents[1]
SCRIPT=(ROOT/'install.sh').read_text()
EXTRACT=SCRIPT.split("<<'AUTO_HOST_ZIP_PY'\n",1)[1].split('\nAUTO_HOST_ZIP_PY',1)[0]
class AutomaticHost(unittest.TestCase):
 def run_extract(self,root,entries):
  archive=root/'host.zip'
  with zipfile.ZipFile(archive,'w') as z:
   for name,contents in entries:z.writestr(name,contents)
  return subprocess.run([sys.executable,'-',str(archive),str(root/'package')],input=EXTRACT,text=True,capture_output=True)
 def test_atomic_extract_and_exact_restart(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d).resolve();entries=[('dist/main.js','compiled'),('dist/automatic-instance-setup.js','worker')]
   first=self.run_extract(root,entries);self.assertEqual(first.returncode,0,first.stderr)
   second=self.run_extract(root,entries);self.assertEqual(second.returncode,0,second.stderr)
   self.assertEqual((root/'package/dist/main.js').read_text(),'compiled')
   changed=self.run_extract(root,[('dist/main.js','modified')]);self.assertNotEqual(changed.returncode,0)
   self.assertEqual((root/'package/dist/main.js').read_text(),'compiled')
 def test_unsafe_names_and_links_never_extract(self):
  for name in ['../escape','/absolute','dist/../escape','dist\\escape','dist/C:drive','dist//empty']:
   with tempfile.TemporaryDirectory() as d:
    root=pathlib.Path(d).resolve();self.assertNotEqual(self.run_extract(root,[(name,'bad')]).returncode,0)
    self.assertFalse((root/'package').exists())
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d).resolve();archive=root/'host.zip';entry=zipfile.ZipInfo('link');entry.external_attr=(stat.S_IFLNK|0o777)<<16
   with zipfile.ZipFile(archive,'w') as z:z.writestr(entry,'outside')
   r=subprocess.run([sys.executable,'-',str(archive),str(root/'package')],input=EXTRACT,text=True,capture_output=True)
   self.assertNotEqual(r.returncode,0);self.assertFalse((root/'package').exists())
if __name__=='__main__':unittest.main()
