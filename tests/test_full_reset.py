"""Linux-only disposable filesystem and runtime-boundary reset regressions."""
import importlib.util
import json
import os
import pathlib
import sys
import tempfile
import unittest
import subprocess
from unittest.mock import patch


@unittest.skipUnless(sys.platform == "linux", "Linux reset helper uses dedicated Unix accounts")
class FullResetTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("full_reset", pathlib.Path(__file__).parents[1] / "scripts/reset-automatic-instance.py")
        self.m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.m)
        self.temp = tempfile.TemporaryDirectory(prefix="bifrost-reset-test-")
        self.root = pathlib.Path(self.temp.name)
        self.uid = os.getuid()

    def tearDown(self):
        self.temp.cleanup()

    def test_canonical_target_refuses_link_and_preserves_outside_data(self):
        outside = self.root / "outside"
        outside.mkdir(mode=0o700)
        marker = outside / "keep"
        marker.write_text("preserved")
        link = self.root / "target"
        link.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(RuntimeError):
            self.m.delete_tree(str(link), self.uid)
        self.assertEqual(marker.read_text(), "preserved")

    def test_leaf_links_are_unlinked_without_following(self):
        outside = self.root / "outside"
        outside.mkdir(mode=0o700)
        marker = outside / "keep"
        marker.write_text("preserved")
        target = self.root / "target"
        target.mkdir(mode=0o700)
        (target / "escape").symlink_to(outside, target_is_directory=True)
        self.m.delete_tree(str(target), self.uid)
        self.assertFalse(target.exists())
        self.assertEqual(marker.read_text(), "preserved")

    def test_writable_directory_and_linked_private_file_refuse(self):
        target = self.root / "target"
        target.mkdir(mode=0o777)
        target.chmod(0o777)
        with self.assertRaises(RuntimeError):
            self.m.safe_directory(target, self.uid)
        target.chmod(0o700)
        private = target / "config"
        private.write_text("private")
        private.chmod(0o600)
        os.link(private, target / "alias")
        with self.assertRaises(RuntimeError):
            self.m.private_file(private, self.uid)
        self.assertEqual(private.read_text(), "private")

    def test_custom_unit_exec_and_environment_refuse(self):
        package = "/home/bifrost-games/.local/opt/bifrost-host-agent-" + "a" * 64
        unit = ("[Unit]\nDescription=Bifrost local game Host Agent\n[Service]\n" +
                f"ExecStart={self.m.NODE} {package}/dist/main.js\n" +
                "Environment=BIFROST_HOST_AGENT_CONFIG=/home/bifrost-games/.config/bifrost-host-agent/host-agent.json\n" +
                "Restart=on-failure\nRestartSec=10\nUMask=0077\n[Install]\nWantedBy=default.target\n")
        self.m.check_game_unit(unit.encode(), package, False)
        for altered in (unit.replace("dist/main.js", "dist/foreign.js"), unit + "Environment=FOREIGN=1\n"):
            with self.assertRaises(RuntimeError):
                self.m.check_game_unit(altered.encode(), package, False)

    def test_changed_review_refuses_before_shutdown_or_cleanup(self):
        with patch.object(self.m, "game_review", return_value={"changed": True}), patch.object(self.m, "run") as command:
            with self.assertRaises(RuntimeError):
                self.m.game_apply(self.root, self.uid, {"changed": False})
            command.assert_not_called()

    def test_foreign_game_container_refuses_complete_review(self):
        home = pathlib.Path('/home/bifrost-games')
        state = home / '.local/state/bifrost-host-agent'
        package = str(home / '.local/opt') + '/bifrost-host-agent-' + 'a' * 64
        config = dict(provisioning=dict(root=str(home / '.local/share/bifrost-instances')),
                      tokenFile=str(state / 'host.token'), ledgerFile=str(state / 'job-ledger.json'))
        def file_bytes(path, *args):
            if path.name == 'host-agent.json':
                return json.dumps(config).encode()
            if path.name == 'job-ledger.json':
                return b'{}'
            return f'ExecStart={self.m.NODE} {package}/dist/main.js\n'.encode()
        def command(args, **kwargs):
            output = ('FragmentPath=' + str(home / '.config/systemd/user' / args[3]) + '\nDropInPaths=\n') if 'show' in args else 'a' * 64 + '\n'
            return type('Result', (), dict(stdout=output, returncode=0))()
        def inspected(args, **kwargs):
            if 'info' in args:
                return dict(host=dict(security=dict(rootless=True)))
            return [dict(Config=dict(Labels={}), Name='foreign')]
        with patch.object(self.m, 'private_file', side_effect=file_bytes), patch.object(self.m, 'safe_directory'), patch.object(self.m, 'check_game_unit'), patch.object(self.m, 'run', side_effect=command), patch.object(self.m, 'json_run', side_effect=inspected), patch.object(self.m.os.path, 'lexists', return_value=False):
            with self.assertRaisesRegex(RuntimeError, 'Foreign container'):
                self.m.game_review(home, self.uid)

    def test_panel_volume_shared_with_foreign_container_refuses(self):
        root = self.root / '.local/share/bifrost'
        root.mkdir(parents=True, mode=0o700)
        (root / '.env').write_text('BIFROST_NODE_ROLE=instance\n')
        (root / 'compose.yaml').write_text('services: {}\n')
        model = dict(name='bifrost', services={key: {} for key in self.m.SERVICES},
                     volumes={key: dict(name='bifrost_' + key) for key in ('postgres_data', 'branding_data')})
        def inspected(args, **kwargs):
            return ['name=rootless'] if 'info' in args else model
        def command(args, **kwargs):
            if 'volume' in args and 'inspect' in args:
                output = json.dumps([dict(Labels={'com.docker.compose.project': 'bifrost', 'com.docker.compose.volume': 'postgres_data'})])
            elif any(value.startswith('volume=') for value in args):
                output = 'b' * 64 + '\n'
            else:
                output = ''
            return type('Result', (), dict(stdout=output, returncode=0))()
        with patch.object(self.m, 'json_run', side_effect=inspected), patch.object(self.m, 'run', side_effect=command):
            with self.assertRaisesRegex(RuntimeError, 'shared with another workload'):
                self.m.panel_review(self.root, self.uid)

    def test_shutdown_refusal_preserves_files_and_releases_own_lock(self):
        state = self.root / ".local/state/bifrost-host-agent"
        state.mkdir(parents=True, mode=0o700)
        marker = state / "host.token"
        marker.write_text("preserve")
        plan = dict(containers=["a" * 64], networks=[], images=[], units=[], trees=[str(state)])
        with patch.object(self.m, "game_review", return_value=plan), patch.object(self.m, "json_run", return_value=[{"State": {"Running": True}}]), patch.object(self.m, "run", side_effect=RuntimeError("stop refused")):
            with self.assertRaises(RuntimeError):
                self.m.game_apply(self.root, self.uid, plan)
        self.assertEqual(marker.read_text(), "preserve")
        self.assertFalse((state / "job-ledger.json.lock").exists())

    def test_game_stop_before_agent_and_no_force_cleanup(self):
        state = self.root / ".local/state/bifrost-host-agent"
        state.mkdir(parents=True, mode=0o700)
        plan = dict(containers=["a" * 64], networks=[], images=[], units=[], trees=[str(state)])
        calls = []
        states = iter([[{"State": {"Running": True}}], [{"State": {"Running": False, "Paused": False, "Pid": 0}}]])
        def command(args, **kwargs):
            calls.append((args, kwargs))
            output = ("a" * 64 + "\n") if "ps" in args else "inactive\n" if "show" in args else ""
            return type("Result", (), {"stdout": output, "returncode": 0})()
        with patch.object(self.m, "game_review", return_value=plan), patch.object(self.m, "json_run", side_effect=lambda args: next(states)), patch.object(self.m, "run", side_effect=command):
            self.m.game_apply(self.root, self.uid, plan)
        self.assertLess(next(i for i, (args, _) in enumerate(calls) if "stop" in args), next(i for i, (args, _) in enumerate(calls) if "disable" in args))
        self.assertEqual(next(options["timeout"] for args, options in calls if "disable" in args), 150)
        self.assertFalse(any("--force" in args or "prune" in args or "reset" in args for args, _ in calls))
        self.assertFalse(state.exists())

    def prejoin_fixture(self):
        home = self.root / 'game'
        config = home / '.config/bifrost-host-agent'
        units = home / '.config/systemd/user'
        config.mkdir(parents=True, mode=0o700)
        units.mkdir(parents=True, mode=0o700)
        package = '/home/bifrost-games/.local/opt/bifrost-host-agent-' + 'a' * 64
        (config / 'local-bootstrap.json').write_text(json.dumps(dict(version=1, enableReviewedCatalog=True,
            local='https://10.0.0.1:8443', token='a' * 64, certificate='public test fixture')))
        for unit in self.m.UNITS:
            (units / unit).write_text(f'ExecStart={self.m.NODE} {package}/dist/main.js\n')
        calls = []
        def command(args, **kwargs):
            calls.append(args)
            output = ('inactive\n' if '--value' in args else 'FragmentPath=' + str(units / args[3]) + '\nDropInPaths=\n') if 'show' in args else ''
            return type('Result', (), dict(stdout=output, returncode=0))()
        def inspected(args, **kwargs):
            return dict(host=dict(security=dict(rootless=True))) if 'info' in args else []
        return home, config, units, calls, command, inspected

    def test_unenrolled_fixture_reproduces_old_reset_failure_and_new_review_succeeds(self):
        home, config, units, _, command, inspected = self.prejoin_fixture()
        with self.assertRaises(FileNotFoundError):
            self.m.game_review(home, self.uid)
        # Package path/template boundaries are simulated; the config and tree
        # checks use real Linux files, including the absent pre-enrollment state.
        original_safe = self.m.safe_directory
        def safe(path, uid):
            if str(path).startswith('/home/bifrost-games/.local/opt/'):
                return
            original_safe(path, uid)
        with patch.object(self.m, 'safe_directory', side_effect=safe), patch.object(self.m, 'check_game_unit'), patch.object(self.m, 'bootstrap_binding', return_value='bound'), patch.object(self.m, 'run', side_effect=command), patch.object(self.m, 'json_run', side_effect=inspected):
            result = self.m.prejoin_review(home, self.uid)
        self.assertEqual(result['component'], 'game-prejoin')
        self.assertEqual(result['containers'], [])
        self.assertEqual(result['binding'], 'bound')

    def test_prejoin_refuses_enrollment_markers_and_links_before_runtime_commands(self):
        home, config, *_ = self.prejoin_fixture()
        state = home / '.local/state/bifrost-host-agent'
        state.mkdir(parents=True, mode=0o700)
        paths = [config / 'host-agent.json', *(state / name for name in ('instance-join.json', 'host.token', 'job-ledger.json', 'job-ledger.json.lock'))]
        for path in paths:
            with self.subTest(path=path.name), patch.object(self.m, 'run') as command:
                path.symlink_to(self.root / 'missing')
                with self.assertRaisesRegex(RuntimeError, 'enrollment or work has started'):
                    self.m.prejoin_review(home, self.uid)
                command.assert_not_called()
                path.unlink()

    def test_prejoin_refuses_unknown_config_world_data_and_foreign_runtime(self):
        home, config, units, _, command, inspected = self.prejoin_fixture()
        world = home / '.local/share/bifrost-instances'
        world.mkdir(parents=True, mode=0o700)
        original_safe = self.m.safe_directory
        def safe(path, uid):
            if not str(path).startswith('/home/bifrost-games/.local/opt/'):
                original_safe(path, uid)
        with patch.object(self.m, 'safe_directory', side_effect=safe), patch.object(self.m, 'check_game_unit'), patch.object(self.m, 'bootstrap_binding', return_value='bound'), patch.object(self.m, 'run', side_effect=command), patch.object(self.m, 'json_run', side_effect=inspected):
            (config / 'foreign.json').write_text('preserve')
            with self.assertRaisesRegex(RuntimeError, 'Unknown Host configuration'):
                self.m.prejoin_review(home, self.uid)
            (config / 'foreign.json').unlink()
            (world / 'world').write_text('preserve')
            with self.assertRaisesRegex(RuntimeError, 'Existing Host data'):
                self.m.prejoin_review(home, self.uid)
            self.assertEqual((world / 'world').read_text(), 'preserve')
            (world / 'world').unlink()
            def foreign(args, **kwargs):
                return type('Result', (), dict(stdout='a' * 64 if 'ps' in args else command(args, **kwargs).stdout))()
            with patch.object(self.m, 'run', side_effect=foreign):
                with self.assertRaisesRegex(RuntimeError, 'Existing game containers'):
                    self.m.prejoin_review(home, self.uid)
            def volumes(args, **kwargs):
                return [dict(name='foreign')] if 'volume' in args else inspected(args, **kwargs)
            with patch.object(self.m, 'json_run', side_effect=volumes):
                with self.assertRaisesRegex(RuntimeError, 'Existing game volumes'):
                    self.m.prejoin_review(home, self.uid)
            def networks(args, **kwargs):
                return [dict(name='foreign')] if 'network' in args else inspected(args, **kwargs)
            with patch.object(self.m, 'json_run', side_effect=networks):
                with self.assertRaisesRegex(RuntimeError, 'Foreign game network'):
                    self.m.prejoin_review(home, self.uid)

    def test_prejoin_shutdown_rechecks_before_removing_prepared_files(self):
        home, config, units, calls, command, _ = self.prejoin_fixture()
        plan = dict(component='game-prejoin', containers=[], units=[str(units / name) for name in self.m.UNITS], trees=[str(config)])
        with patch.object(self.m, 'prejoin_review', return_value=plan), patch.object(self.m, 'run', side_effect=command):
            self.m.prejoin_apply(home, self.uid, plan)
        self.assertFalse(config.exists())
        self.assertFalse(any((units / name).exists() for name in self.m.UNITS))
        self.assertEqual(calls[0][2], 'disable')
        self.assertEqual(calls[-1][2], 'daemon-reload')

    def test_prejoin_advancing_during_shutdown_preserves_files(self):
        home, config, units, _, command, _ = self.prejoin_fixture()
        plan = dict(units=[str(units / name) for name in self.m.UNITS], trees=[str(config)])
        with patch.object(self.m, 'prejoin_review', side_effect=[plan, dict(advanced=True)]), patch.object(self.m, 'run', side_effect=command):
            with self.assertRaisesRegex(RuntimeError, 'advanced during shutdown'):
                self.m.prejoin_apply(home, self.uid, plan)
        self.assertTrue((config / 'local-bootstrap.json').exists())
        self.assertTrue(all((units / name).exists() for name in self.m.UNITS))

    def test_prejoin_service_stop_refusal_preserves_files(self):
        home, config, units, _, _, _ = self.prejoin_fixture()
        plan = dict(units=[str(units / name) for name in self.m.UNITS], trees=[str(config)])
        with patch.object(self.m, 'prejoin_review', return_value=plan), patch.object(self.m, 'run', side_effect=RuntimeError('stop refused')):
            with self.assertRaisesRegex(RuntimeError, 'stop refused'):
                self.m.prejoin_apply(home, self.uid, plan)
        self.assertTrue((config / 'local-bootstrap.json').exists())

    def test_prejoin_requires_panel_binding_and_interactive_confirmation(self):
        game = dict(containers=[], binding='game', component='game-prejoin')
        panel = dict(containers=[], binding='other', component='panel')
        with patch.object(self.m.sys, 'argv', ['reset', '--apply-prejoin-reset']), patch.object(self.m.os, 'getuid', return_value=0), patch.object(self.m, 'account_environment', return_value=(type('User', (), dict(pw_uid=1234))(), {})), patch.object(self.m.pathlib.Path, 'exists', return_value=True), patch.object(self.m, 'child', side_effect=[game, panel]) as child:
            with self.assertRaisesRegex(RuntimeError, 'belongs to another panel'):
                self.m.main()
            self.assertEqual(child.call_count, 2)
        panel['binding'] = 'game'
        with patch.object(self.m.sys, 'argv', ['reset', '--apply-prejoin-reset']), patch.object(self.m.os, 'getuid', return_value=0), patch.object(self.m, 'account_environment', return_value=(type('User', (), dict(pw_uid=1234))(), {})), patch.object(self.m.pathlib.Path, 'exists', return_value=True), patch.object(self.m, 'child', side_effect=[game, panel]) as child, patch.object(self.m.sys.stdin, 'isatty', return_value=False):
            with self.assertRaisesRegex(RuntimeError, 'interactive terminal'):
                self.m.main()
            self.assertEqual(child.call_count, 2)

    def test_bootstrap_binding_validates_certificate_and_changes_with_panel(self):
        cert = self.root / 'cert.pem'
        subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-days', '1', '-subj', '/CN=reset-test', '-keyout', str(self.root / 'key.pem'), '-out', str(cert)], check=True, capture_output=True)
        value = dict(local='https://10.0.0.1:8443', token='a' * 64, certificate=cert.read_text())
        original = self.m.bootstrap_binding(value)
        self.assertNotEqual(original, self.m.bootstrap_binding(dict(value, token='b' * 64)))
        for invalid in (dict(value, local='http://10.0.0.1'), dict(value, local='https://10.0.0.1/path'), dict(value, token='short'), dict(value, certificate='invalid')):
            with self.subTest(invalid=invalid['local']), self.assertRaises((RuntimeError, self.m.ssl.SSLError)):
                self.m.bootstrap_binding(invalid)


if __name__ == "__main__":
    unittest.main()
