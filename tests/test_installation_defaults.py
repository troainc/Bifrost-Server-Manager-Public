"""Execute installer settings/early refusals without modifying an installation."""
import os
import pathlib
import shlex
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = (ROOT / 'install.sh').read_text()

class InstallationDefaults(unittest.TestCase):
    def shell(self, fragment):
        return subprocess.run(['bash', '-c', 'set -euo pipefail\n' + fragment], capture_output=True, text=True, timeout=10)

    def test_standard_port_without_terminal_prompt(self):
        fragment = SCRIPT.split('\nport=8443\n', 1)[1].split('scratch=$(mktemp -d)', 1)[0]
        result = self.shell('BIFROST_INSTALL_ADVANCED=0; INSTALL_DIR=/synthetic/retained\nread(){ echo UNEXPECTED_PROMPT >&2; exit 99; }; fail(){ exit 98; }\nport=8443\n' + fragment + '\ntest "$port" = 8443')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('UNEXPECTED_PROMPT', result.stderr)
        self.assertIn('/synthetic/retained', result.stdout)

    def test_standard_license_connection_without_automatic_consent(self):
        fragment = SCRIPT.split('\nconfigure_license=y\n', 1)[1].split('  python3 - "$INSTALL_DIR" "$license_url" "$key_file"', 1)[0]
        result = self.shell('BIFROST_INSTALL_ADVANCED=0; INSTALL_DIR=/synthetic/retained; configure_license=y\nread(){ echo UNEXPECTED_PROMPT >&2; exit 99; }\n' + fragment + '\nprintf "%s|%s\\n" "$license_url" "$key_file"\nfi')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'https://bifrost.therealmsofasgard.com/api|/synthetic/retained/config/license-signing-public.pem')
        self.assertTrue("read -r -p 'Enable license testing before completing your local review?" in SCRIPT, 'Explicit testing authorization must remain separate')

    def test_legacy_wipe_refuses_at_entry_before_bootstrap_or_download(self):
        for arguments, env_value in [(['--reinstall'], '0'), (['--instance', '--reinstall'], '0'), (['--bootstrap'], '1'), (['--host'], '1'), (['--update'], '1')]:
            result = subprocess.run(['bash', str(ROOT / 'install.sh'), *arguments], env={**os.environ, 'BIFROST_REINSTALL': env_value}, capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('Legacy --reinstall is disabled', result.stderr)
            self.assertNotIn('Download', result.stdout)

    def test_su_command_preserves_advanced_and_space_containing_paths(self):
        line = next(line.strip() for line in SCRIPT.splitlines() if line.lstrip().startswith("printf -v command_line 'exec env BIFROST_INSTALL_ADVANCED="))
        result = self.shell('BIFROST_INSTALL_ADVANCED=1; BIFROST_RELEASE_DIRECTORY="/synthetic/assets with spaces"; BIFROST_INSTALL_ROLE=instance; script="/synthetic/install with spaces.sh"\n' + line + '\nprintf "%s" "$command_line"')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(shlex.split(result.stdout), ['exec', 'env', 'BIFROST_INSTALL_ADVANCED=1', 'BIFROST_RELEASE_DIRECTORY=/synthetic/assets with spaces', 'BIFROST_REINSTALL=0', 'BIFROST_RESUME=0', 'BIFROST_INSTALL_ROLE=instance', 'bash', '/synthetic/install with spaces.sh', '--bootstrap'])

    def test_final_ready_message_follows_host_preparation(self):
        body = SCRIPT.split('automated_bootstrap() {', 1)[1].split('\nrequire_host_runtime() {', 1)[0]
        self.assertLess(body.index('prepare_automatic_instance_host'), body.index('INSTALLATION READY FOR BROWSER SETUP'))

if __name__ == '__main__':
    unittest.main()
