"""Disposable signed-release tests. Run only on an authorized remote runner."""
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('automatic', ROOT / 'scripts/automatic-panel-updates.py')
automatic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(automatic)


class AutomaticUpdates(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.installed = 'v0.1.0-installtest.38'
        self.target = 'v0.1.0-installtest.39'
        (self.root / '.env').write_text(f'BIFROST_VERSION={self.installed}\nBIFROST_POSTGRES_RUNTIME=alpine17-v1\n')
        self.policy = {'enabled': True, 'channel': 'testing'}
        self.write_policy()
        self.key = self.root / 'private.pem'
        self.public = self.root / 'public.pem'
        subprocess.run(['openssl', 'genpkey', '-algorithm', 'ed25519', '-out', str(self.key)], check=True, capture_output=True)
        subprocess.run(['openssl', 'pkey', '-in', str(self.key), '-pubout', '-out', str(self.public)], check=True, capture_output=True)
        der = subprocess.run(['openssl', 'pkey', '-pubin', '-in', str(self.public), '-outform', 'DER'], check=True, capture_output=True).stdout
        self.signer = hashlib.sha256(der).hexdigest()
        self.release = {'tag_name': self.target, 'draft': False, 'prerelease': True}
        self.script = f'#!/bin/bash\nVERSION={self.target}\n# BIFROST_UNATTENDED_UPDATE=1\n'.encode()
        self.verifier = (ROOT / 'scripts/release-manifest.py').read_bytes()
        now = dt.datetime.now(dt.timezone.utc)
        self.statement = {'schemaVersion': 1, 'version': self.target, 'signerSha256': self.signer,
                          'privateSourceSha': 'a' * 40, 'publicSourceSha': 'b' * 40,
                          'createdAt': now.isoformat(), 'expiresAt': (now + dt.timedelta(days=1)).isoformat(),
                          'artifacts': [self.artifact('release-manifest.py', self.verifier), self.artifact('update.sh', self.script),
                                        self.artifact(f'bifrost-linux-amd64-{self.target}.tar.gz', b'fixture bundle')]}
        self.sign_statement()
        self.addCleanup(patch.stopall)
        patch.object(automatic, 'SIGNER', self.signer).start()
        patch.object(automatic, 'fetch', side_effect=self.fetch).start()
        patch.object(automatic.shutil, 'disk_usage', return_value=shutil._ntuple_diskusage(100 * 1024**3, 0, 100 * 1024**3)).start()

    def artifact(self, name, data):
        return {'name': name, 'size': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

    def write_policy(self):
        (self.root / 'automatic-update-policy.json').write_text(json.dumps(self.policy))

    def sign_statement(self):
        manifest = self.root / 'manifest.json'
        signature = self.root / 'manifest.sig'
        manifest.write_text(json.dumps(self.statement))
        subprocess.run(['openssl', 'pkeyutl', '-sign', '-inkey', str(self.key), '-rawin', '-in', str(manifest), '-out', str(signature)], check=True, capture_output=True)
        self.assets = {'release-signing-public.pem': self.public.read_bytes(), 'release-manifest.json': manifest.read_bytes(),
                       'release-manifest.sig': signature.read_bytes(), 'release-manifest.py': self.verifier, 'update.sh': self.script}

    def fetch(self, url, limit):
        data = json.dumps([self.release]).encode() if '/releases?' in url else self.assets[url.rsplit('/', 1)[1]]
        self.assertLessEqual(len(data), limit)
        return data

    def test_signed_read_only_plan_never_executes_updater(self):
        original = automatic.subprocess.run
        with patch.object(automatic.subprocess, 'run', wraps=original) as run:
            automatic.check(self.root)
        self.assertFalse(any(call.args[0][0] == '/bin/bash' for call in run.call_args_list))
        self.assertEqual(json.loads((self.root / 'automatic-update-status.json').read_text())['event'], 'ready')

    def test_apply_uses_only_authenticated_script_and_exact_expected_version(self):
        original = automatic.subprocess.run
        calls = []
        def execute(args, **kwargs):
            if args[0] != '/bin/bash': return original(args, **kwargs)
            calls.append((args, kwargs))
            self.assertEqual(Path(args[1]).read_bytes(), self.script)
            (self.root / '.env').write_text(f'BIFROST_VERSION={self.target}\nBIFROST_POSTGRES_RUNTIME=alpine17-v1\n')
            return subprocess.CompletedProcess(args, 0)
        with patch.object(automatic.subprocess, 'run', side_effect=execute):
            automatic.check(self.root, apply=True)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0][2:], ['--unattended', self.installed])
        self.assertNotIn('shell', calls[0][1])
        self.assertEqual(json.loads((self.root / 'automatic-update-status.json').read_text())['event'], 'completed')

    def test_downgrade_is_never_selected(self):
        self.release['tag_name'] = 'v0.1.0-installtest.37'
        automatic.check(self.root)
        self.assertEqual(json.loads((self.root / 'automatic-update-status.json').read_text())['event'], 'current')

    def test_channel_changes_require_explicit_manual_transition(self):
        self.policy['channel'] = 'stable'
        self.write_policy()
        with self.assertRaises(ValueError): automatic.check(self.root)

    def test_opt_out_prevents_release_fetch(self):
        self.policy['enabled'] = False
        self.write_policy()
        with self.assertRaises(ValueError): automatic.check(self.root, apply=True)
        automatic.fetch.assert_not_called()

    def test_corrupt_signature_rejected(self):
        self.assets['release-manifest.sig'] = b'x' * 64
        with self.assertRaises(subprocess.CalledProcessError): automatic.check(self.root)

    def test_untrusted_signer_rejected(self):
        with patch.object(automatic, 'SIGNER', 'f' * 64):
            with self.assertRaises(ValueError): automatic.check(self.root)

    def test_modified_verifier_never_executes(self):
        self.assets['release-manifest.py'] += b'\nraise RuntimeError("untrusted execution")\n'
        with self.assertRaises(ValueError): automatic.check(self.root)

    def test_modified_updater_rejected(self):
        self.assets['update.sh'] += b'\nexit 0\n'
        with self.assertRaises(ValueError): automatic.check(self.root)

    def test_expired_release_rejected(self):
        self.statement['expiresAt'] = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)).isoformat()
        self.sign_statement()
        with self.assertRaises(ValueError): automatic.check(self.root)

    def test_interrupted_update_blocks_retry(self):
        (self.root / 'update-journal.json').write_text(json.dumps({'phase': 'failed'}))
        with self.assertRaises(ValueError): automatic.check(self.root, apply=True)
        automatic.fetch.assert_not_called()

    def test_storage_budget_refuses_before_apply(self):
        automatic.shutil.disk_usage.return_value = shutil._ntuple_diskusage(1, 0, 1)
        with self.assertRaises(ValueError): automatic.check(self.root, apply=True)

    def test_retained_checkpoints_are_never_pruned(self):
        backups = self.root / 'update-backups'
        backups.mkdir()
        for name in ('first', 'second', 'third'): (backups / name).mkdir()
        with self.assertRaises(ValueError): automatic.check(self.root, apply=True)
        self.assertEqual(len(list(backups.iterdir())), 3)

    def test_unattended_marker_requires_signed_support(self):
        self.script = self.script.replace(b'# BIFROST_UNATTENDED_UPDATE=1\n', b'')
        self.statement['artifacts'][1] = self.artifact('update.sh', self.script)
        self.sign_statement()
        with self.assertRaises(ValueError): automatic.check(self.root, apply=True)

    def test_download_destinations_reject_credentials_localhost_and_http(self):
        for url in ('http://github.com/file', 'https://127.0.0.1/file', 'https://user@github.com/file', 'https://github.com:444/file'):
            with self.subTest(url=url), self.assertRaises(ValueError): automatic.approved(url)

    def test_enable_rejects_implicit_channel_transition_before_writing_policy(self):
        with self.assertRaises(ValueError): automatic.configure(self.root, True, 'stable')
        self.assertEqual(json.loads((self.root / 'automatic-update-policy.json').read_text()), self.policy)

    def test_timer_is_local_user_scoped_and_does_not_catch_up_missed_windows(self):
        (self.root / 'scripts').mkdir()
        (self.root / 'scripts/automatic-panel-updates.py').write_text('# fixture')
        with patch.object(automatic.Path, 'home', return_value=self.root), patch.object(automatic.subprocess, 'run') as run:
            automatic.configure(self.root, True, 'testing')
        timer = (self.root / '.config/systemd/user/bifrost-panel-update.timer').read_text()
        self.assertIn('Persistent=false', timer)
        self.assertIn('04:00:00', timer)
        self.assertEqual(run.call_args_list[-1].args[0], ['systemctl', '--user', 'enable', '--now', 'bifrost-panel-update.timer'])

    def test_failed_timer_setup_revokes_saved_permission(self):
        (self.root / 'scripts').mkdir()
        (self.root / 'scripts/automatic-panel-updates.py').write_text('# fixture')
        with patch.object(automatic.Path, 'home', return_value=self.root), patch.object(automatic.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, 'systemctl')):
            with self.assertRaises(subprocess.CalledProcessError): automatic.configure(self.root, True, 'testing')
        self.assertFalse(json.loads((self.root / 'automatic-update-policy.json').read_text())['enabled'])

    def test_failure_diagnostics_are_actionable_and_do_not_echo_untrusted_text(self):
        self.assertEqual(automatic.failure_code(ValueError('Insufficient free storage for staged update and recovery.')), 'storage-low')
        self.assertEqual(automatic.failure_code(subprocess.CalledProcessError(1, ['/bin/bash', '/private/path'])), 'update-apply-failed')
        self.assertEqual(automatic.failure_code(ValueError('token=synthetic-secret /private/path')), 'release-verification-or-local-state-invalid')


if __name__ == '__main__': unittest.main()
