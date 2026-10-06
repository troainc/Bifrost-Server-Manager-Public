"""Exercise public role parsing without installing or removing anything."""
import pathlib, subprocess, unittest, tempfile, json, re, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
class NodeRoles(unittest.TestCase):
 def select(self,*arguments):
  script=(ROOT/'install.sh').read_text()
  start=script.index('HOST_FLAGS=()');end=script.index('if [[ "${1:-}" == --reinstall ]]; then',start)
  fragment=script[start:end]
  harness='set -Eeuo pipefail\nfail(){ echo "$*" >&2; exit 2; }\ninstall_instance_host(){ printf "host:%s\\n" "${HOST_FLAGS[*]}"; }\n'+fragment+'\nprintf "%s:%s:%s\\n" "$BIFROST_INSTALL_ROLE" "${BIFROST_REINSTALL:-0}" "$#"\n'
  return subprocess.run(['bash','-c',harness,'test',*arguments],capture_output=True,text=True)
 def test_three_roles_are_distinct(self):
  for role in ['controller','instance','hybrid']:
   result=self.select('--'+role);self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(result.stdout.strip(),role+':0:0')
 def test_reset_keeps_explicit_role(self):
  for role in ['controller','instance','hybrid']:
   result=self.select('--'+role,'--reinstall');self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(result.stdout.strip(),role+':1:0')
 def test_host_only_is_not_a_new_controller(self):
  result=self.select('--host','--upgrade');self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(result.stdout.strip(),'host:--upgrade')
 def test_fresh_join_is_distinct_and_cannot_replace_existing_host(self):
  result=self.select('--host','--join-instance');self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(result.stdout.strip(),'host:--join-instance')
  for flags in [('--host','--join-instance','--upgrade'),('--host','--join-instance','--re-enroll')]:self.assertNotEqual(self.select(*flags).returncode,0)
 def test_unknown_flags_fail_before_installation(self):
  for flags in [('--instance','--host'),('--hybrid','--unknown'),('--host','--reinstall')]:self.assertNotEqual(self.select(*flags).returncode,0)
 def test_generated_panel_configuration_records_chosen_role(self):
  script=(ROOT/'install.sh').read_text(); marker='python3 - "$INSTALL_DIR" "$address" "$port" "$scratch/networks.json" "$BIFROST_INSTALL_ROLE" <<\'PY\'\n'
  python=script.split(marker,1)[1].split('\nPY\n',1)[0]
  for role in ['controller','instance','hybrid']:
   with tempfile.TemporaryDirectory() as temporary:
    root=pathlib.Path(temporary);(root/'.env.example').write_text((ROOT/'.env.example').read_text());(root/'networks.json').write_text('[]')
    subprocess.run([sys.executable,'-',str(root),'192.168.1.50','8443',str(root/'networks.json'),role],input=python,text=True,check=True)
    values=dict(line.split('=',1) for line in (root/'.env').read_text().splitlines() if '=' in line and not line.startswith('#'))
    self.assertEqual(values['BIFROST_NODE_ROLE'],role);self.assertEqual(values['BIFROST_PUBLIC_URL'],'https://192.168.1.50:8443')
if __name__=='__main__':unittest.main()
