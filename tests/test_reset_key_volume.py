import importlib.util,json,pathlib,tempfile,unittest,os
from unittest.mock import patch

class KeyVolumeTests(unittest.TestCase):
 def setUp(self):
  spec=importlib.util.spec_from_file_location('reset_keys',pathlib.Path(__file__).parents[1]/'scripts/reset-automatic-instance.py')
  self.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.m)
  self.temp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.temp.name)
  root=self.root/'.local/share/bifrost';root.mkdir(parents=True,mode=0o700)
  (root/'.env').write_text('BIFROST_NODE_ROLE=instance\n');(root/'compose.yaml').write_text('services: {}\n')
 def tearDown(self):self.temp.cleanup()
 def check(self,volumes,mounts=None,foreign=False,external=False):
  model=dict(name='bifrost',services={name:{} for name in self.m.SERVICES},volumes={name:dict(name='bifrost_'+name) for name in volumes})
  model['services']['control-plane']['volumes']=mounts or []
  if external:model['volumes']['controller_key_data']['external']=True
  def inspect(args,**kwargs):return ['rootless'] if 'info' in args else model
  def run(args,**kwargs):
   if args[1:3]==['volume','inspect']:
    name=args[-1];value=json.dumps([{'Labels':{'com.docker.compose.project':'bifrost','com.docker.compose.volume':name.removeprefix('bifrost_')}}])
   elif foreign and 'volume=bifrost_controller_key_data' in args:value='a'*64+'\n'
   else:value=''
   return type('Result',(),dict(stdout=value,returncode=0))()
  with patch.object(self.m,'json_run',side_effect=inspect),patch.object(self.m,'run',side_effect=run):return self.m.panel_review(self.root,os.getuid())
 def test_legacy_and_exact_new_volume(self):
  self.assertEqual(len(self.check(['postgres_data','branding_data'])['volumes']),2)
  self.assertEqual(len(self.check(['postgres_data','branding_data','controller_key_data'],[{'type':'volume','source':'controller_key_data','target':'/var/lib/bifrost/keys'}])['volumes']),3)
 def test_foreign_mount_and_unknown_volume_refused(self):
  for mounts in [[],[{'type':'bind','source':'/foreign','target':'/var/lib/bifrost/keys'}],[{'type':'volume','source':'controller_key_data','target':'/foreign'}]]:
   with self.assertRaisesRegex(RuntimeError,'managed-key mount'):self.check(['postgres_data','branding_data','controller_key_data'],mounts)
  with self.assertRaisesRegex(RuntimeError,'panel volumes'):self.check(['postgres_data','branding_data','foreign'])
 def test_shared_or_external_key_volume_refused(self):
  mount=[{'type':'volume','source':'controller_key_data','target':'/var/lib/bifrost/keys'}]
  for flags in [dict(foreign=True),dict(external=True)]:
   with self.assertRaisesRegex(RuntimeError,'shared|External'):self.check(['postgres_data','branding_data','controller_key_data'],mount,**flags)
