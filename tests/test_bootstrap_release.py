"""OS detection must not change the release used by administrator Host setup."""
import pathlib
import re
import shlex
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (ROOT / 'install.sh').read_text()
RELEASE = re.search(r'^VERSION=(\S+)$', SCRIPT, re.M).group(1)


class BootstrapRelease(unittest.TestCase):
    def run_detection_and_downloads(self, os_release):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = pathlib.Path(temporary) / 'os-release'
            fixture.write_text(os_release)
            start = SCRIPT.index('  [[ -r /etc/os-release ]]')
            end = SCRIPT.index("  printf '\\nPreparing VM prerequisites", start)
            detection = SCRIPT[start:end].replace('/etc/os-release', shlex.quote(str(fixture)))
            downloads = '\n'.join(line for line in SCRIPT.splitlines()
                                  if line.strip().startswith('fetch ')
                                  and 'releases/download/$VERSION/' in line
                                  and '"$stage/' in line
                                  and ('host.zip"' in line or 'SHA256SUMS"' in line))
            self.assertEqual(len(downloads.splitlines()), 2)
            harness = (f'set -Eeuo pipefail\nVERSION={shlex.quote(RELEASE)}\n'
                       'ID=retained-id\nVERSION_ID=retained-version-id\nstage=/unused\n'
                       'fail(){ printf "%s\\n" "$*" >&2; exit 2; }\n'
                       'ui_banner(){ :; }\nui_step(){ :; }\n'
                       'detect_os(){\n' + detection + '}\n'
                       'fetch(){ printf "%s\\n" "$1"; }\n'
                       'detect_os\n' + downloads + '\n'
                       'printf "retained:%s:%s:%s\\n" "$VERSION" "$ID" "$VERSION_ID"\n')
            return subprocess.run(['bash', '-c', harness], text=True, capture_output=True)

    def test_debian_and_ubuntu_versions_cannot_replace_release_urls(self):
        for distro, version in [('debian', '12 (bookworm)'), ('ubuntu', '24.04.3 LTS (Noble Numbat)')]:
            with self.subTest(distro=distro):
                result = self.run_detection_and_downloads(
                    f'ID={distro}\nVERSION="{version}"\nVERSION_ID="different-os-version"\n')
                self.assertEqual(result.returncode, 0, result.stderr)
                base = f'https://github.com/troainc/Bifrost-Server-Manager-Public/releases/download/{RELEASE}'
                self.assertEqual(result.stdout.splitlines(), [
                    base + '/bifrost-linux-host-agent.zip', base + '/SHA256SUMS',
                    f'retained:{RELEASE}:retained-id:retained-version-id'])

    def test_unsupported_or_missing_os_id_fails_before_download(self):
        for fixture in ['ID=fedora\nVERSION="41 (Server Edition)"\n', 'VERSION="unknown"\nID=\n']:
            result = self.run_detection_and_downloads(fixture)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, '')
            self.assertIn('supports Debian and Ubuntu', result.stderr)


if __name__ == '__main__':
    unittest.main()
