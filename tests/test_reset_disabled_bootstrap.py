"""No production connections: disabled pre-enrollment and paired reset guards."""
import importlib.util,json,os,pathlib,subprocess,sys,tempfile,unittest
from unittest.mock import patch

@unittest.skipUnless(sys.platform=='linux','Linux service-owner reset')
class DisabledBootstrapReset(unittest.TestCase):
 def setUp(self):
  spec=importlib.util.spec_from_file_location('reset_disabled',pathlib.Path(__file__).parents[1]/'scripts/reset-automatic-instance.py')
  self.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.m)
  self.temp=tempfile.TemporaryDirectory();self.home=pathlib.Path(self.temp.name)
  root=self.home/'.local/share/bifrost';(root/'secrets').mkdir(parents=True,mode=0o700)
  (root/'.env').write_text('BIFROST_NODE_ROLE=instance\nBIFROST_PUBLIC_URL=https://10.0.0.1:8443\n')
  (root/'secrets/local-host-bootstrap.json').write_text('{"enabled":false}')
  subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','1','-subj','/CN=reset-disabled-fixture','-keyout',str(self.home/'key'),'-out',str(root/'secrets/panel-cert.pem')],check=True,capture_output=True)
  self.root=root;self.certificate=(root/'secrets/panel-cert.pem').read_text()
  self.plan=dict(component='panel',containers=[],fingerprint='original')
 def tearDown(self):self.temp.cleanup()
 def review(self):
  with patch.object(self.m,'panel_review',return_value=self.plan.copy()):return self.m.panel_prejoin_review(self.home,os.getuid(),True)
 def test_old_prejoin_refusal_reproduced_and_auto_matches_exact_origin_certificate(self):
  with patch.object(self.m,'panel_review',return_value=self.plan.copy()),self.assertRaisesRegex(RuntimeError,'does not own'):self.m.panel_prejoin_review(self.home,os.getuid())
  plan=self.review()
  self.assertEqual(plan['bootstrapState'],'disabled')
  self.assertEqual(plan['panelIdentity'],self.m.panel_identity('https://10.0.0.1:8443',self.certificate))
  self.assertNotEqual(plan['panelIdentity'],self.m.panel_identity('https://other.invalid:8443',self.certificate))
 def test_disabled_requires_exact_false_record_and_valid_certificate(self):
  for value in [{'enabled':False,'token':'retained'},{'enabled':0},{'enabled':False,'unknown':True}]:
   (self.root/'secrets/local-host-bootstrap.json').write_text(json.dumps(value))
   with self.assertRaisesRegex(RuntimeError,'does not own'):self.review()
  (self.root/'secrets/local-host-bootstrap.json').write_text('{"enabled":false}')
  (self.root/'secrets/panel-cert.pem').write_text('not a certificate')
  with self.assertRaises(self.m.ssl.SSLError):self.review()
 def test_changed_bootstrap_refuses_panel_cleanup(self):
  expected=self.review();(self.root/'secrets/local-host-bootstrap.json').write_text('{"enabled":true,"token":"'+'a'*64+'"}')
  with patch.object(self.m,'panel_review',return_value=self.plan.copy()),patch.object(self.m,'panel_apply') as cleanup,self.assertRaisesRegex(RuntimeError,'review changed'):
   self.m.panel_prejoin_apply(self.home,os.getuid(),expected,True)
  cleanup.assert_not_called()
 def run_root(self,argv,plans,confirmation=None,tty=True):
  with patch.object(self.m.sys,'argv',['reset',argv]),patch.object(self.m.os,'getuid',return_value=0),patch.object(self.m,'account_environment',return_value=(type('User',(),dict(pw_uid=1234))(),{})),patch.object(self.m.pathlib.Path,'exists',return_value=True),patch.object(self.m,'child',side_effect=plans) as child,patch.object(self.m.sys.stdin,'isatty',return_value=tty),patch('builtins.input',return_value=confirmation):
   return self.m.main(),child.call_args_list
 def pair(self):return (dict(component='game-prejoin',containers=[],panelIdentity='same',binding='token'),dict(component='panel',containers=[],panelIdentity='same',bootstrapState='disabled'))
 def test_auto_disabled_root_success_rechecks_both_then_uses_scoped_components(self):
  game,panel=self.pair();result,calls=self.run_root('--apply-auto-reset',[game,panel,game,panel,{},{}],'WIPE ALL')
  self.assertTrue(result['resetCompleted'])
  self.assertEqual([c.args[:2] for c in calls],[('bifrost-games','--component-auto-review'),('bifrost','--component-prejoin-any-review'),('bifrost-games','--component-prejoin-review'),('bifrost','--component-prejoin-any-review'),('bifrost-games','--component-prejoin-apply'),('bifrost','--component-prejoin-any-apply')])
 def test_auto_refuses_mismatched_identity_cancel_no_tty_and_changed_pair(self):
  game,panel=self.pair()
  for argv,plans,confirmation,tty,message in [('--review-auto',[game,dict(panel,panelIdentity='other')],None,True,'another panel'),('--apply-auto-reset',[game,panel],'CANCEL',True,'cancelled'),('--apply-auto-reset',[game,panel],'WIPE ALL',False,'interactive'),('--apply-auto-reset',[game,panel,dict(game,binding='changed')],'WIPE ALL',True,'review changed')]:
   with self.subTest(message=message),self.assertRaisesRegex(RuntimeError,message):self.run_root(argv,plans,confirmation,tty)
 def test_auto_enrolled_uses_existing_full_review_and_never_prejoin(self):
  game=dict(component='game',containers=[]);panel=dict(component='panel',containers=[])
  result,calls=self.run_root('--review-auto',[game,panel])
  self.assertTrue(result['readOnly']);self.assertEqual(calls[-1].args,('bifrost','--component-review'))
