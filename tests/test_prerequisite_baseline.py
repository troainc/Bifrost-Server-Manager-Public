import datetime
import hashlib
import importlib.util
import io
import json
import pathlib
import subprocess
import tarfile
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / 'scripts/verify-prerequisite-baseline.py'
SPEC = importlib.util.spec_from_file_location('baseline_verifier', SCRIPT)
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class BaselineVerifier(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name) / 'candidate'
        self.root.mkdir()
        self.key = pathlib.Path(self.temp.name) / 'private.pem'
        subprocess.run(['openssl', 'genpkey', '-algorithm', 'ED25519', '-out', str(self.key)], check=True, capture_output=True)
        public = self.root / 'release-signing-public.pem'
        subprocess.run(['openssl', 'pkey', '-in', str(self.key), '-pubout', '-out', str(public)], check=True, capture_output=True)
        der = subprocess.check_output(['openssl', 'pkey', '-pubin', '-in', str(public), '-outform', 'DER'])
        self.pin = hashlib.sha256(der).hexdigest()
        for name in VERIFIER.ASSETS:
            (self.root / name).write_bytes(b'synthetic signed evidence')
        self.assessment = {'schemaVersion': 1, 'unresolvedFindings': 0, 'productionApproved': False, 'manualAcceptanceComplete': False}
        (self.root / 'security-assessment.json').write_text(json.dumps(self.assessment))
        self.archive()
        now = datetime.datetime.now(datetime.timezone.utc)
        self.manifest = {'schemaVersion': 1, 'version': VERIFIER.VERSION, 'signerSha256': self.pin, 'privateSourceSha': 'a' * 40, 'publicSourceSha': 'b' * 40, 'createdAt': now.isoformat(), 'expiresAt': (now + datetime.timedelta(days=1)).isoformat()}
        self.sign()

    def tearDown(self):
        self.temp.cleanup()

    def archive(self, extra=None):
        with tarfile.open(self.root / 'prerequisite-baseline.tar.gz', 'w:gz') as target:
            for name in VERIFIER.TOOLS:
                info = tarfile.TarInfo(name)
                payload = b'#!/bin/sh\nfixture' if name.endswith('.sh') else b'\x7fELF\x02\x01' + bytes(12) + b'\x3e\x00'
                info.size = len(payload)
                info.mode = 0o500
                target.addfile(info, io.BytesIO(payload))
            if extra:
                info = tarfile.TarInfo(extra)
                info.size = 4
                info.mode = 0o500
                target.addfile(info, io.BytesIO(b'evil'))

    def sign(self):
        self.manifest['artifacts'] = [{'name': name, 'size': (self.root / name).stat().st_size, 'sha256': hashlib.sha256((self.root / name).read_bytes()).hexdigest()} for name in sorted(VERIFIER.ASSETS)]
        (self.root / 'release-manifest.json').write_text(json.dumps(self.manifest))
        subprocess.run(['openssl', 'pkeyutl', '-sign', '-inkey', str(self.key), '-rawin', '-in', str(self.root / 'release-manifest.json'), '-out', str(self.root / 'release-manifest.sig')], check=True, capture_output=True)

    def test_signed_complete_baseline_verifies_without_installing(self):
        before = set(self.root.rglob('*'))
        result = VERIFIER.verify_baseline(self.root, self.pin)
        self.assertEqual(result['version'], VERIFIER.VERSION)
        self.assertEqual(set(self.root.rglob('*')), before)

    def test_changed_payload_wrong_signer_and_wrong_product_refuse(self):
        with self.assertRaises(ValueError):
            VERIFIER.verify_baseline(self.root, '0' * 64)
        path = self.root / 'prerequisite-baseline.tar.gz'
        path.write_bytes(path.read_bytes() + b'changed')
        with self.assertRaises(ValueError):
            VERIFIER.verify_baseline(self.root, self.pin)
        self.archive()
        self.manifest['version'] = 'v0.1.0-installtest.34'
        self.sign()
        with self.assertRaises(ValueError):
            VERIFIER.verify_baseline(self.root, self.pin)

    def test_even_a_signed_traversal_or_unlisted_tool_refuses(self):
        for name in ('../escape', 'docker/unreviewed-tool'):
            self.archive(name)
            self.sign()
            with self.assertRaises(ValueError):
                VERIFIER.verify_baseline(self.root, self.pin)

    def test_missing_signature_and_linked_payload_refuse(self):
        signature = self.root / 'release-manifest.sig'
        signature.unlink()
        with self.assertRaises((ValueError, OSError)):
            VERIFIER.verify_baseline(self.root, self.pin)
        self.sign()
        original = self.root / 'security-evidence.tar.gz'
        retained = pathlib.Path(self.temp.name) / 'retained'
        original.rename(retained)
        original.symlink_to(retained)
        with self.assertRaises(ValueError):
            VERIFIER.verify_baseline(self.root, self.pin)

    def test_signed_unresolved_or_production_approval_cannot_pass(self):
        for field, value in [('unresolvedFindings', 1), ('unresolvedFindings', False), ('productionApproved', True), ('manualAcceptanceComplete', True)]:
            invalid = {**self.assessment, field: value}
            (self.root / 'security-assessment.json').write_text(json.dumps(invalid))
            self.sign()
            with self.assertRaises(ValueError):
                VERIFIER.verify_baseline(self.root, self.pin)
