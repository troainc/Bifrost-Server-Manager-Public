"""Exercise installer/updater licensing configuration without running a deployment."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
OPENSSL = shutil.which('openssl') or 'C:/Program Files/Git/usr/bin/openssl.exe'


class LicenseSetup(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        (self.root/'config').mkdir()
        self.env = self.root/'.env'
        self.original = 'BIFROST_LICENSE_URL=https://old.invalid/api\nBIFROST_PRIVACY_REVIEW_APPROVED_AT=\nUNRELATED=value\n'
        self.env.write_text(self.original)
        self.key = self.root/'public.pem'
        self.private = self.root/'private.pem'
        subprocess.run([OPENSSL,'genpkey','-algorithm','EC','-pkeyopt','ec_paramgen_curve:P-256','-out',str(self.private)],check=True,capture_output=True)
        subprocess.run([OPENSSL,'pkey','-in',str(self.private),'-pubout','-out',str(self.key)],check=True,capture_output=True)
        self.destination = self.root/'config/license-signing-public.pem'
        self.destination.write_bytes(b'previous key')

    def configure(self, script, url, key=None):
        source=(REPO/script).read_text().split("<<'LICENSE_SETUP_PY'\n",1)[1].split('\nLICENSE_SETUP_PY',1)[0]
        env=dict(os.environ)
        env['PATH']=str(Path(OPENSSL).parent)+os.pathsep+env.get('PATH','')
        return subprocess.run([sys.executable,'-c',source,str(self.root),url,str(key or self.key)],env=env,capture_output=True,text=True)

    def test_valid_configuration_preserves_other_settings_and_does_not_approve_privacy(self):
        for script in ('install.sh','update.sh'):
            with self.subTest(script=script):
                result=self.configure(script,'https://bifrost.therealmsofasgard.com/api/')
                self.assertEqual(result.returncode,0,result.stderr)
                content=self.env.read_text()
                self.assertEqual(content.count('BIFROST_LICENSE_URL='),1)
                self.assertIn('BIFROST_LICENSE_URL=https://bifrost.therealmsofasgard.com/api\n',content)
                self.assertIn('BIFROST_PRIVACY_REVIEW_APPROVED_AT=\n',content)
                self.assertIn('UNRELATED=value\n',content)
                self.assertEqual(self.destination.read_bytes(),self.key.read_bytes())

    def test_invalid_endpoints_preserve_previous_url_and_key(self):
        urls=['http://host.invalid/api','https://user:password@host.invalid/api','https://host.invalid/api?token=x','https://host.invalid/api#fragment','https://host.invalid/api\nINJECTED=yes','https://host.invalid:70000/api','https://host.invalid/$VALUE','https://host.invalid/other/path']
        for script in ('install.sh','update.sh'):
            for url in urls:
                with self.subTest(script=script,url=url):
                    self.assertNotEqual(self.configure(script,url).returncode,0)
                    self.assertEqual(self.env.read_text(),self.original)
                    self.assertEqual(self.destination.read_bytes(),b'previous key')

    def test_private_missing_oversized_and_wrong_curve_keys_are_rejected(self):
        oversized=self.root/'oversized.pem';oversized.write_bytes(b'x'*4097)
        wrong_private=self.root/'wrong-private.pem';wrong=self.root/'wrong-public.pem'
        subprocess.run([OPENSSL,'genpkey','-algorithm','EC','-pkeyopt','ec_paramgen_curve:P-384','-out',str(wrong_private)],check=True,capture_output=True)
        subprocess.run([OPENSSL,'pkey','-in',str(wrong_private),'-pubout','-out',str(wrong)],check=True,capture_output=True)
        for script in ('install.sh','update.sh'):
            for key in (self.private,self.root/'missing.pem',oversized,wrong):
                with self.subTest(script=script,key=key.name):
                    self.assertNotEqual(self.configure(script,'https://host.invalid/api',key).returncode,0)
                    self.assertEqual(self.env.read_text(),self.original)
                    self.assertEqual(self.destination.read_bytes(),b'previous key')


if __name__=='__main__':
    unittest.main()
