"""Exercise the real Host preflight function with a cwd-sensitive Podman stub."""
import os
import pathlib
import subprocess
import tempfile
import unittest

SCRIPT = (pathlib.Path(__file__).resolve().parents[1] / 'install.sh').read_text()
BODY = SCRIPT.split('require_host_runtime() {\n', 1)[1].split('\n}\n', 1)[0]


class HostWorkingDirectory(unittest.TestCase):
    @unittest.skipUnless(os.name == 'posix', 'Bash ownership/runtime behavior requires Linux')
    def test_inherited_admin_directory_is_replaced_before_podman_probe(self):
        with tempfile.TemporaryDirectory() as value:
            root = pathlib.Path(value)
            home = root / 'game-home'
            inherited = root / 'admin-home'
            tools = root / 'tools'
            for directory in (home, inherited, tools):
                directory.mkdir(mode=0o700)
            for name, content in {
                'node': '#!/bin/bash\nexit 0\n',
                'systemctl': '#!/bin/bash\nexit 0\n',
                'podman': '#!/bin/bash\n[[ "$PWD" == "$HOME" ]] || exit 23\nprintf "true\\n"\n',
            }.items():
                path = tools / name
                path.write_text(content)
                path.chmod(0o700)
            environment = dict(os.environ, HOME=str(home), BIFROST_NODE_BIN=str(tools / 'node'), PATH=str(tools) + ':' + os.environ['PATH'])
            prefix = 'fail(){ echo "$*" >&2; exit 1; }; require_host_runtime(){\n'
            suffix = '\n}; require_host_runtime\n'
            result = subprocess.run(['/bin/bash', '-c', prefix + BODY + suffix], cwd=inherited, env=environment, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            old_body = BODY.replace('  cd -- "$HOME" || fail \'Cannot enter the game account home directory.\'\n', '')
            old = subprocess.run(['/bin/bash', '-c', prefix + old_body + suffix], cwd=inherited, env=environment, capture_output=True, text=True)
            self.assertNotEqual(old.returncode, 0, 'The fixture must reproduce the old inherited-directory failure')


if __name__ == '__main__':
    unittest.main()
