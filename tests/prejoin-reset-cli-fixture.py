"""Destructive ONLY inside an explicitly opted-in disposable Docker fixture.

Run with a read-only repository mount and --network none. Uses real dedicated
users, runuser, ownership, Python subprocesses, terminal confirmation and tree
removal. Podman, Docker and systemd responses are simulated, not live daemons.
"""
import json
import os
import pathlib
import pty
import pwd
import select
import subprocess
import time

assert os.getuid() == 0 and pathlib.Path('/.dockerenv').exists()
assert os.environ.get('BIFROST_DISPOSABLE_RESET_FIXTURE') == '1'
source = pathlib.Path(__file__).resolve().parents[1]
helper = source / 'scripts/reset-automatic-instance.py'
game = pathlib.Path('/home/bifrost-games')
panel = pathlib.Path('/home/bifrost')
package = game / '.local/opt' / ('bifrost-host-agent-' + 'a' * 64)
root = panel / '.local/share/bifrost'
config = game / '.config/bifrost-host-agent'
units = game / '.config/systemd/user'
assert not root.exists() and not config.exists(), 'Use a fresh disposable fixture image'


def directory(path, account):
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    record = pwd.getpwnam(account)
    # All created ancestors inside this service home have real service ownership.
    for parent in (path, *path.parents):
        if parent == pathlib.Path('/home'):
            break
        os.chown(parent, record.pw_uid, record.pw_gid)
        parent.chmod(0o700)


def owned_file(path, data, account):
    directory(path.parent, account)
    path.write_text(data)
    record = pwd.getpwnam(account)
    os.chown(path, record.pw_uid, record.pw_gid)
    path.chmod(0o600)


directory(root / 'secrets', 'bifrost')
directory(package, 'bifrost-games')
directory(units, 'bifrost-games')
subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-days', '1', '-subj', '/CN=prejoin-fixture',
    '-keyout', '/tmp/test-key.pem', '-out', '/tmp/test-cert.pem'], check=True, capture_output=True)
certificate = pathlib.Path('/tmp/test-cert.pem').read_text()
owned_file(root / '.env', 'BIFROST_NODE_ROLE=instance\nBIFROST_PUBLIC_URL=https://10.0.0.1:8443\n', 'bifrost')
owned_file(root / 'compose.yaml', 'services: {}\n', 'bifrost')
owned_file(root / 'secrets/local-host-bootstrap.json', json.dumps(dict(enabled=True, token='a' * 64)), 'bifrost')
owned_file(root / 'secrets/panel-cert.pem', certificate, 'bifrost')
owned_file(config / 'local-bootstrap.json', json.dumps(dict(version=1, local='https://10.0.0.1:8443', token='a' * 64,
    certificate=certificate, enableReviewedCatalog=True)), 'bifrost-games')
for setup, name in ((True, 'bifrost-instance-setup.service'), (False, 'bifrost-host-agent.service')):
    prefix = '[Unit]\nDescription=Bifrost ' + ('automatic Instance connection' if setup else 'local game Host Agent') + '\n[Service]\n'
    command = f'ExecStart=/opt/bifrost-node-v24.19.0/bin/node {package}/dist/' + ('automatic-instance-setup.js /home/bifrost-games/.config/bifrost-host-agent/local-bootstrap.json' if setup else 'main.js') + '\n'
    rest = f'WorkingDirectory={package}\n' if setup else 'Environment=BIFROST_HOST_AGENT_CONFIG=/home/bifrost-games/.config/bifrost-host-agent/host-agent.json\n'
    owned_file(units / name, prefix + command + rest + 'Restart=on-failure\nRestartSec=10\nUMask=0077\n' + ('NoNewPrivileges=true\n' if setup else '') + '[Install]\nWantedBy=default.target\n', 'bifrost-games')
for account in ('bifrost', 'bifrost-games'):
    bus = pathlib.Path('/run/user') / str(pwd.getpwnam(account).pw_uid) / 'bus'
    bus.parent.mkdir(parents=True, exist_ok=True)
    bus.touch()

runtime = '''#!/usr/bin/python3
import json,os,sys,pathlib
name=pathlib.Path(sys.argv[0]).name;args=sys.argv[1:]
if name=='systemctl':
    if 'show' in args:
        if '--value' in args: print('inactive')
        else: print('FragmentPath=/home/bifrost-games/.config/systemd/user/'+args[2]+'\\nDropInPaths=')
elif name=='podman':
    if 'info' in args: print(json.dumps(dict(host=dict(security=dict(rootless=True)))))
    elif 'volume' in args or 'network' in args: print('[]')
elif name=='docker':
    if 'info' in args: print('["rootless"]')
    elif 'compose' in args: print(json.dumps(dict(name='bifrost',services={key:{} for key in ('postgres','migrate','control-plane','web','https')},volumes={key:dict(name='bifrost_'+key) for key in ('postgres_data','branding_data')})))
    elif 'inspect' in args: sys.exit(1)
'''
for name in ('systemctl', 'podman'):
    path = pathlib.Path('/usr/bin') / name
    path.write_text(runtime)
    path.chmod(0o755)
directory(panel / '.local/bin', 'bifrost')
docker = panel / '.local/bin/docker'
docker.write_text(runtime)
docker.chmod(0o755)
unrelated = game / 'keep-unrelated.txt'
owned_file(unrelated, 'preserve', 'bifrost-games')

review = subprocess.run(['/usr/bin/python3', str(helper), '--review-prejoin'], capture_output=True, text=True)
assert review.returncode == 0, review.stdout + review.stderr
assert json.loads(review.stdout)['resetReady'] is True
original_environment = (root / '.env').read_text()
owned_file(root / '.env', original_environment.replace('=instance', '=controller'), 'bifrost')
refused = subprocess.run(['/usr/bin/python3', str(helper), '--apply-prejoin-reset'], capture_output=True, text=True)
assert refused.returncode == 1 and 'Instance panel' in refused.stdout
assert root.exists() and config.exists()
owned_file(root / '.env', original_environment, 'bifrost')
owned_file(root / 'secrets/local-host-bootstrap.json', json.dumps(dict(enabled=True, token='b' * 64)), 'bifrost')
refused = subprocess.run(['/usr/bin/python3', str(helper), '--apply-prejoin-reset'], capture_output=True, text=True)
assert refused.returncode == 1 and 'belongs to another panel' in refused.stdout
assert root.exists() and config.exists()
owned_file(root / 'secrets/local-host-bootstrap.json', json.dumps(dict(enabled=True, token='a' * 64)), 'bifrost')


def apply(confirmation):
    master, slave = pty.openpty()
    process = subprocess.Popen(['/usr/bin/python3', str(helper), '--apply-prejoin-reset'], stdin=slave, stdout=slave, stderr=slave)
    os.close(slave)
    result = b''
    sent = False
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        if select.select([master], [], [], .1)[0]:
            try:
                part = os.read(master, 65536)
            except OSError:
                break
            result += part
            if b'Type WIPE ALL:' in result and not sent:
                os.write(master, confirmation.encode() + b'\n')
                sent = True
        if process.poll() is not None:
            break
    if process.poll() is None:
        process.kill()
    process.wait()
    os.close(master)
    return process.returncode, result.decode()


code, output = apply('CANCEL')
assert code == 1 and 'RESET_REFUSED' in output, output
assert root.exists() and config.exists()
code, output = apply('WIPE ALL')
assert code == 0 and '"resetCompleted": true' in output, output
assert not root.exists() and not config.exists()
assert all(not (units / name).exists() for name in ('bifrost-instance-setup.service', 'bifrost-host-agent.service'))
assert package.exists() and unrelated.read_text() == 'preserve'
print('PASS actual root CLI, dedicated non-root components, matching bootstrap, cancellation, WIPE ALL and real tree removal; runtime replies simulated')
