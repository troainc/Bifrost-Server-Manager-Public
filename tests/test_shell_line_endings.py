import pathlib,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class LinuxScriptBytes(unittest.TestCase):
    def test_standalone_and_packager_scripts_have_linux_line_endings(self):
        for name in ('install.sh','update.sh','scripts/build-release-bundle.sh','scripts/release-bootstrap.sh','.env.example'):
            with self.subTest(name=name):
                data=(ROOT/name).read_bytes()
                self.assertNotIn(b'\r',data,'Linux scripts must execute from their exact packaged bytes, including Windows builds')
