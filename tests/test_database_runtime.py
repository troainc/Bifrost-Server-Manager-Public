import pathlib, subprocess, sys, tempfile, unittest
SCRIPT = (pathlib.Path(__file__).resolve().parents[1] / 'update.sh').read_text()
CHECK = SCRIPT.split("<<'DATABASE_RUNTIME_PY'\n",1)[1].split('\nDATABASE_RUNTIME_PY',1)[0]
class RuntimeUpdate(unittest.TestCase):
    def test_older_or_unknown_database_runtime_is_refused_without_modification(self):
        with tempfile.TemporaryDirectory() as directory:
            env=pathlib.Path(directory)/'.env'
            for content in ['BIFROST_VERSION=v0.1.0-installtest.4\n','BIFROST_POSTGRES_RUNTIME=unknown\n','BIFROST_POSTGRES_RUNTIME=alpine17-v1\n']:
                env.write_text(content)
                result=subprocess.run([sys.executable,'-c',CHECK,str(env)],capture_output=True,text=True)
                self.assertEqual(result.returncode,0 if 'alpine17-v1' in content else 1)
                self.assertEqual(env.read_text(),content)
                if result.returncode: self.assertIn('data is unchanged',result.stderr)
