"""Prepared Host updates may change only the matched managed-package path."""
import hashlib,pathlib,subprocess,sys,tempfile,unittest
SCRIPT=(pathlib.Path(__file__).resolve().parents[1]/'install.sh').read_text()
PAYLOAD=SCRIPT.split("python3 -c 'import hashlib,os,pathlib,re,stat,sys,tempfile\n",1)[1].split("' \"$1\"",1)[0]
PAYLOAD='import hashlib,os,pathlib,re,stat,sys,tempfile\n'+PAYLOAD
class PreparedHostUpgrade(unittest.TestCase):
 def run_payload(self,path,data,upgrade='1',phase='write'):
  return subprocess.run([sys.executable,'-c',PAYLOAD,str(path),upgrade,phase],input=data,text=True,capture_output=True)
 def test_check_then_upgrade_preserves_old_unit(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d).resolve()/'bifrost-instance-setup.service'
   old='ExecStart=/opt/bifrost-node-v24.19.0/bin/node /home/bifrost-games/.local/opt/bifrost-host-agent-'+('a'*64)+'/dist/automatic-instance-setup.js\n'
   new=old.replace('a'*64,'b'*64);p.write_text(old);p.chmod(0o600)
   checked=self.run_payload(p,new,phase='check');self.assertEqual(checked.returncode,0,checked.stderr);self.assertEqual(p.read_text(),old)
   changed=self.run_payload(p,new);self.assertEqual(changed.returncode,0,changed.stderr);self.assertEqual(p.read_text(),new)
   backup=p.with_name(p.name+'.prejoin-'+hashlib.sha256(old.encode()).hexdigest());self.assertEqual(backup.read_text(),old)
   self.assertEqual(self.run_payload(p,new).returncode,0)
 def test_non_upgrade_and_arbitrary_service_changes_refuse(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d).resolve()/'service'
   old='ExecStart=/home/bifrost-games/.local/opt/bifrost-host-agent-'+('a'*64)+'/dist/main.js\n';p.write_text(old);p.chmod(0o600)
   for data,upgrade in [(old.replace('a'*64,'b'*64),'0'),(old+'ExecStop=/bin/false\n','1'),(old.replace('/dist/main.js','/dist/arbitrary.js'),'1')]:
    result=self.run_payload(p,data,upgrade);self.assertNotEqual(result.returncode,0);self.assertEqual(p.read_text(),old)
 def test_missing_and_symlinked_units_refuse_upgrade(self):
  with tempfile.TemporaryDirectory() as d:
   p=pathlib.Path(d).resolve()/'service'
   self.assertNotEqual(self.run_payload(p,'template').returncode,0);self.assertFalse(p.exists())
   target=p.with_name('original');target.write_text('retained');target.chmod(0o600)
   try:p.symlink_to(target)
   except OSError:self.skipTest('Symlink creation unavailable')
   self.assertNotEqual(self.run_payload(p,'template').returncode,0);self.assertEqual(target.read_text(),'retained')
if __name__=='__main__':unittest.main()
