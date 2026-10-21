import importlib.util
import io
import os
import pathlib
import tarfile
import tempfile
import unittest
from unittest import mock

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / 'scripts/prepare-testing-prerequisites.py'
SPEC = importlib.util.spec_from_file_location('testing_prerequisites', SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TestingPrerequisites(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = pathlib.Path(self.temporary.name).resolve()
        self.home = self.root / 'home'
        self.home.mkdir(mode=0o700)
        self.assets = self.root / 'assets'
        self.assets.mkdir(mode=0o700)
        with tarfile.open(self.assets / 'prerequisite-baseline.tar.gz', 'w:gz') as archive:
            for name in MODULE.BASELINE.TOOLS:
                value = ('signed-fixture:' + name).encode()
                info = tarfile.TarInfo(name)
                info.size = len(value)
                info.mode = 0o500
                archive.addfile(info, io.BytesIO(value))

    def test_signature_failure_precedes_all_executable_writes(self):
        with mock.patch.object(MODULE.BASELINE, 'verify_baseline', side_effect=ValueError('tampered')):
            with self.assertRaises(ValueError):
                MODULE.install_verified(self.assets, self.home)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_retains_existing_tool_without_partial_installation(self):
        (self.home / 'bin').mkdir(mode=0o700)
        existing = self.home / 'bin/docker'
        existing.write_bytes(b'retained-runtime')
        with mock.patch.object(MODULE.BASELINE, 'verify_baseline'):
            with self.assertRaises(ValueError):
                MODULE.install_verified(self.assets, self.home)
        self.assertEqual(existing.read_bytes(), b'retained-runtime')
        self.assertEqual(list((self.home / 'bin').iterdir()), [existing])
        self.assertFalse((self.home / '.docker').exists())

    @unittest.skipUnless(os.name == 'posix', 'Linux path/ownership contracts')
    def test_refuses_linked_or_writable_executable_directory(self):
        outside = self.root / 'outside'
        outside.mkdir(mode=0o700)
        (self.home / 'bin').symlink_to(outside)
        with mock.patch.object(MODULE.BASELINE, 'verify_baseline'):
            with self.assertRaises(ValueError):
                MODULE.install_verified(self.assets, self.home)
        self.assertEqual(list(outside.iterdir()), [])

    @unittest.skipUnless(os.name == 'posix', 'Linux path/ownership contracts')
    def test_complete_new_install_has_exact_private_tool_bytes_and_modes(self):
        with mock.patch.object(MODULE.BASELINE, 'verify_baseline') as verification:
            MODULE.install_verified(self.assets, self.home)
        verification.assert_called_once_with(self.assets)
        files = [path for path in self.home.rglob('*') if path.is_file()]
        self.assertEqual(len(files), 12)
        for name in MODULE.BASELINE.TOOLS:
            path = (self.home / '.docker/cli-plugins/docker-compose' if name == 'docker-compose'
                    else self.home / 'bin' / pathlib.PurePosixPath(name).name)
            self.assertEqual(path.read_bytes(), ('signed-fixture:' + name).encode())
            self.assertEqual(path.stat().st_mode & 0o777, 0o500)

    def test_rejects_foreign_downloads_and_cleartext_redirects(self):
        for url in ('http://github.com/file', 'https://github.com.evil.test/file',
                    'https://github.com:8443/file', 'https://user@github.com/file'):
            with self.assertRaises(ValueError):
                MODULE.approved(url)
        MODULE.approved('https://release-assets.githubusercontent.com/file')

    def test_requires_testing_consent_before_network_or_runtime_changes(self):
        with mock.patch('sys.argv', [str(SCRIPT)]), mock.patch.object(MODULE, 'fetch') as download:
            with self.assertRaises(ValueError):
                MODULE.main()
        download.assert_not_called()

    @unittest.skipUnless(os.name == 'posix', 'Linux runtime detection')
    def test_existing_runtime_is_retained_before_download(self):
        with mock.patch('sys.argv', [str(SCRIPT), '--accept-testing-build']), \
                mock.patch.object(MODULE.os, 'getuid', return_value=1000), \
                mock.patch.object(MODULE.platform, 'system', return_value='Linux'), \
                mock.patch.object(MODULE.platform, 'machine', return_value='x86_64'), \
                mock.patch.object(MODULE.shutil, 'which', return_value='/usr/bin/docker'), \
                mock.patch.object(MODULE, 'fetch') as download:
            with self.assertRaises(ValueError):
                MODULE.main()
        download.assert_not_called()
