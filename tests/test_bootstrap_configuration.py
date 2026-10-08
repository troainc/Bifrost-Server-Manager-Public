"""Run only in an explicitly disposable Linux container with fixture accounts."""
import json, os, pathlib, pwd, subprocess, sys, tempfile, unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CODE = (ROOT / 'install.sh').read_text().split("<<'AUTO_HOST_CONFIG_PY'\n", 1)[1].split('\nAUTO_HOST_CONFIG_PY', 1)[0]
DISPOSABLE = sys.platform == 'linux' and os.getuid() == 0 and os.environ.get('BIFROST_INSTALLER_DISPOSABLE_ROOT') == '1'

@unittest.skipUnless(DISPOSABLE, 'Requires disposable Linux root fixture, never the operator machine')
class BootstrapConfiguration(unittest.TestCase):
    def setUp(self):
        self.panel_uid = pwd.getpwnam('bifrost').pw_uid
        self.game_uid = pwd.getpwnam('bifrost-games').pw_uid
        self.assertGreaterEqual(self.panel_uid, 1000)
        self.assertNotEqual(self.panel_uid, self.game_uid)
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.root.chmod(0o755)
        self.panel = self.root / 'panel'
        self.game = self.root / 'games'
        for base, uid in [(self.panel, self.panel_uid), (self.game, self.game_uid)]:
            base.mkdir(mode=0o700)
            os.chown(base, uid, uid)
        (self.panel / 'secrets').mkdir(mode=0o700)
        os.chown(self.panel / 'secrets', self.panel_uid, self.panel_uid)
        for path in [self.game / '.config', self.game / '.config/bifrost-host-agent']:
            path.mkdir(mode=0o700)
            os.chown(path, self.game_uid, self.game_uid)
        self.secret = self.panel / 'secrets/local-host-bootstrap.json'
        self.bootstrap = self.game / '.config/bifrost-host-agent/local-bootstrap.json'
        self.write(self.panel / '.env', 'BIFROST_NODE_ROLE=instance\nBIFROST_PUBLIC_URL=https://192.0.2.50:8443\n')
        self.write(self.panel / 'secrets/panel-cert.pem', '-----BEGIN CERTIFICATE-----\nfixture-public-only\n-----END CERTIFICATE-----\n')
        self.write(self.secret, json.dumps({'enabled': False}))

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, path, data):
        path.write_text(data)
        path.chmod(0o600)
        os.chown(path, self.panel_uid, self.panel_uid)

    def run_setup(self):
        return subprocess.run([sys.executable, '-', str(self.panel), str(self.panel_uid), str(self.game), str(self.game_uid)], input=CODE, text=True, capture_output=True)

    def test_exact_resume_and_interrupted_panel_activation(self):
        result = self.run_setup()
        self.assertEqual(result.returncode, 0, result.stderr)
        original = self.bootstrap.read_bytes()
        local = json.loads(original)
        self.assertEqual(local['token'], json.loads(self.secret.read_text())['token'])
        self.assertEqual(self.bootstrap.stat().st_uid, self.game_uid)
        self.assertEqual(self.bootstrap.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.secret.stat().st_uid, self.panel_uid)
        self.assertEqual(self.secret.stat().st_mode & 0o777, 0o644)
        self.assertEqual(self.run_setup().returncode, 0)
        self.write(self.secret, json.dumps({'enabled': False}))
        self.assertEqual(self.run_setup().returncode, 0)
        self.assertEqual(self.bootstrap.read_bytes(), original)
        self.assertEqual(json.loads(self.secret.read_text())['token'], local['token'])

    def test_mismatched_capability_preserves_both_files(self):
        self.assertEqual(self.run_setup().returncode, 0)
        self.write(self.secret, json.dumps({'enabled': True, 'token': 'X' * 64}))
        before = self.secret.read_bytes(), self.bootstrap.read_bytes()
        self.assertNotEqual(self.run_setup().returncode, 0)
        self.assertEqual((self.secret.read_bytes(), self.bootstrap.read_bytes()), before)

    def test_private_key_and_symlink_refused(self):
        cert = self.panel / 'secrets/panel-cert.pem'
        self.write(cert, '-----BEGIN CERTIFICATE-----\nPRIVATE KEY\n')
        self.assertNotEqual(self.run_setup().returncode, 0)
        self.assertFalse(self.bootstrap.exists())
        cert.unlink()
        cert.symlink_to(self.panel / '.env')
        self.assertNotEqual(self.run_setup().returncode, 0)
        self.assertFalse(self.bootstrap.exists())

if __name__ == '__main__':
    unittest.main()
