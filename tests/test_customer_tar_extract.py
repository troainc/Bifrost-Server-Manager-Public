import io,pathlib,subprocess,sys,tarfile,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
SCRIPT=(ROOT/'install.sh').read_text()
CODE=SCRIPT.split('python3 - "$scratch/$bundle" "$scratch/package" <<\'PY\'\n',1)[1].split('\nPY',1)[0]
class CustomerTarExtraction(unittest.TestCase):
 def extract(self,entries):
  with tempfile.TemporaryDirectory() as directory:
   root=pathlib.Path(directory);archive=root/'payload.tgz';destination=root/'package'
   with tarfile.open(archive,'w:gz') as output:
    for name,kind in entries:
     entry=tarfile.TarInfo(name);entry.mode=0o7777
     if kind=='file':entry.size=4;output.addfile(entry,io.BytesIO(b'data'))
     elif kind=='directory':entry.type=tarfile.DIRTYPE;output.addfile(entry)
     else:entry.type=tarfile.SYMTYPE;entry.linkname='/etc';output.addfile(entry)
   result=subprocess.run([sys.executable,'-',str(archive),str(destination)],input=CODE,text=True,capture_output=True)
   files={p.relative_to(destination).as_posix():(p.read_bytes(),p.stat().st_mode&0o7777) for p in destination.rglob('*') if p.is_file()}
   return result,files
 def test_regular_contents_have_private_modes_without_tar_filter(self):
  result,files=self.extract([('.', 'directory'),('./config','directory'),('./config/test.txt','file')])
  self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(files,{'config/test.txt':(b'data',0o600)});self.assertNotIn('extractall(',CODE)
 def test_links_traversal_and_absolute_paths_are_rejected_before_writes(self):
  for name,kind in [('config','link'),('../outside','file'),('/outside','file')]:
   with self.subTest(name=name):
    result,files=self.extract([('first.txt','file'),(name,kind)]);self.assertNotEqual(result.returncode,0);self.assertEqual(files,{})
 def test_duplicate_normalized_paths_are_rejected_before_writes(self):
  result,files=self.extract([('./config/file','file'),('config/file','file')]);self.assertNotEqual(result.returncode,0);self.assertEqual(files,{})
if __name__=='__main__':unittest.main()
