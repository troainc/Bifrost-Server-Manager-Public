"""Exercise the real recovery entry with a restricted non-login su PATH."""
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (ROOT / 'install.sh').read_text()


class HostResume(unittest.TestCase):
    def run_resume(self, uid):
        start = SCRIPT.index('prepare_automatic_instance_host() {')
        end = SCRIPT.index('  local game=', start)
        # Execute the actual root check and PATH normalization, then stop
        # before account, policy, file, network or systemd mutations.
        prepare = SCRIPT[start:end] + '  printf "prepared:%s:%s\\n" "$PATH" "$PWD"\n}\n'
        start = SCRIPT.index('if [[ "${1:-}" == --resume-local-host ]]; then')
        end = SCRIPT.index('HOST_FLAGS=()', start)
        recovery = SCRIPT[start:end]
        harness = ('set -Eeuo pipefail\nPATH=/usr/bin:/bin\n'
                   f'id(){{ printf "%s\\n" {uid}; }}\n'
                   'uname(){ case "$1" in -s) echo Linux;; -m) echo x86_64;; esac; }\n'
                   'fail(){ printf "%s\\n" "$*" >&2; exit 2; }\n' + prepare + recovery)
        with tempfile.TemporaryDirectory() as private_home:
            pathlib.Path(private_home).chmod(0o700)
            return subprocess.run(['bash', '-c', harness, 'fixture', '--resume-local-host'],
                                  text=True, capture_output=True, cwd=private_home)

    def test_root_resume_restores_administrator_tools_path(self):
        result = self.run_resume(0)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(),
                         'prepared:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/')

    def test_unprivileged_resume_still_refuses_before_preparation(self):
        result = self.run_resume(1000)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')
        self.assertIn('as the VM administrator', result.stderr)


if __name__ == '__main__':
    unittest.main()
