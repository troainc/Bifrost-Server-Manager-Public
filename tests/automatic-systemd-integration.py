#!/usr/bin/env python3
"""Real user-systemd/locking test with a disposable publisher and signed Bash fixture.

Never executes Docker or modifies a real installation. Production trust has no test
override: only this non-shipped fixture driver injects its disposable publisher.
"""
import datetime as dt
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import time

assert os.environ.get('GITHUB_ACTIONS') == 'true'
assert os.environ.get('RUNNER_ENVIRONMENT') == 'github-hosted'
assert os.getuid() != 0 and Path.home() == Path('/home/bifrost')
SOURCE = Path(__file__).resolve().parents[1]
root = Path.home() / '.local/share/bifrost'
assert not root.exists(), 'Refuse an existing installation'
root.mkdir(parents=True, mode=0o700)
stage = root / '.fixture-publisher'
stage.mkdir(mode=0o700)
scripts = root / 'scripts'
scripts.mkdir(mode=0o700)
installed, target = 'v0.1.0-installtest.38', 'v0.1.0-installtest.39'


def private(path, value):
    path.write_bytes(value.encode() if isinstance(value, str) else value)
    path.chmod(0o600)


def reset_version():
    private(root / '.env', f'BIFROST_VERSION={installed}\nBIFROST_POSTGRES_RUNTIME=alpine17-v1\nBIFROST_LICENSE_URL=https://fixture.invalid/api\n')


def run(args, check=True):
    return subprocess.run(args, check=check, text=True, capture_output=True, timeout=40)


def wait(check):
    deadline = time.monotonic() + 25
    while time.monotonic() < deadline:
        if check(): return
        time.sleep(.1)
    raise AssertionError('Disposable service did not reach the expected state')


reset_version()
run(['openssl', 'genpkey', '-algorithm', 'ed25519', '-out', str(stage / 'private.pem')])
run(['openssl', 'pkey', '-in', str(stage / 'private.pem'), '-pubout', '-out', str(stage / 'release-signing-public.pem')])
der = subprocess.check_output(['openssl', 'pkey', '-pubin', '-in', str(stage / 'release-signing-public.pem'), '-outform', 'DER'])
signer = hashlib.sha256(der).hexdigest()
script = f'''#!/bin/bash
set -Eeuo pipefail
VERSION={target}
# BIFROST_UNATTENDED_UPDATE=1
[[ $1 == --unattended && $2 == {installed} ]]
[[ $(id -un) == bifrost && $(id -u) != 0 ]]
[[ -z ${{BASH_ENV+x}} && -z ${{ENV+x}} && -z ${{BIFROST_RELEASE_DIRECTORY+x}} && -z ${{BIFROST_UPDATE_LOCK_FD+x}} ]]
root="$HOME/.local/share/bifrost"
[[ $PWD == "$root" ]]
exec 9>"$root/update.lock"
flock -n 9 || exit 73
touch "$root/.fixture-publisher/ready"
while [[ -f "$root/.fixture-publisher/hold" ]]; do sleep .1; done
python3 - "$root" "$VERSION" <<'FIXTURE_APPLY'
from pathlib import Path
import json,os,sys
root=Path(sys.argv[1]);env=root/'.env'
env.write_text(env.read_text().replace('BIFROST_VERSION={installed}', 'BIFROST_VERSION='+sys.argv[2]))
with (root/'.fixture-publisher/applies.jsonl').open('a') as output:
 output.write(json.dumps({{'uid':os.getuid(),'noNewPrivileges':'NoNewPrivs:\\t1' in Path('/proc/self/status').read_text()}})+'\\n')
FIXTURE_APPLY
'''
private(stage / 'update.sh', script)
private(stage / 'release-manifest.py', (SOURCE / 'scripts/release-manifest.py').read_bytes())
def artifact(name, value): return {'name': name, 'size': len(value), 'sha256': hashlib.sha256(value).hexdigest()}
now = dt.datetime.now(dt.timezone.utc)
statement = {'schemaVersion': 1, 'version': target, 'signerSha256': signer, 'privateSourceSha': 'a' * 40, 'publicSourceSha': 'b' * 40,
             'createdAt': now.isoformat(), 'expiresAt': (now + dt.timedelta(days=1)).isoformat(),
             'artifacts': [artifact('update.sh', script.encode()), artifact('release-manifest.py', (stage / 'release-manifest.py').read_bytes()), artifact(f'bifrost-linux-amd64-{target}.tar.gz', b'fixture only')]}
private(stage / 'release-manifest.json', json.dumps(statement))
run(['openssl', 'pkeyutl', '-sign', '-inkey', str(stage / 'private.pem'), '-rawin', '-in', str(stage / 'release-manifest.json'), '-out', str(stage / 'release-manifest.sig')])
driver = scripts / 'automatic-panel-updates.py'
private(driver, f'''import importlib.util,json,os
from pathlib import Path
spec=importlib.util.spec_from_file_location('production_helper',{str(SOURCE / 'scripts/automatic-panel-updates.py')!r})
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.SIGNER={signer!r}
stage=Path({str(stage)!r})
def fixture_fetch(url,limit):
 if url==f'https://api.github.com/repos/{{module.REPOSITORY}}/releases?per_page=100':
  data=json.dumps([{{'tag_name':{target!r},'draft':False,'prerelease':True}}]).encode()
 else:
  prefix=f'https://github.com/{{module.REPOSITORY}}/releases/download/{target}/'
  assert url.startswith(prefix)
  name=url[len(prefix):];assert '/' not in name and name in ('release-signing-public.pem','release-manifest.json','release-manifest.sig','release-manifest.py','update.sh')
  data=(stage/name).read_bytes()
 assert len(data)<=limit
 return data
module.fetch=fixture_fetch
os.environ.update({{'BASH_ENV':'/fixture/forbidden','ENV':'/fixture/forbidden','BIFROST_RELEASE_DIRECTORY':'/fixture/forbidden','BIFROST_UPDATE_LOCK_FD':'999'}})
if __name__=='__main__': module.main()
''')
spec = importlib.util.spec_from_file_location('production_helper', SOURCE / 'scripts/automatic-panel-updates.py')
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)
unit = 'bifrost-panel-update'
ctl = ['systemctl', '--user']
results = []
try:
    helper.configure(root, True, 'testing')
    assert run(ctl + ['is-enabled', unit + '.timer']).stdout.strip() == 'enabled'
    assert run(ctl + ['is-active', unit + '.timer']).stdout.strip() == 'active'
    timer = (Path.home() / '.config/systemd/user' / (unit + '.timer')).read_text()
    assert 'Persistent=false' in timer and '04:00:00' in timer and 'RandomizedDelaySec=10min' in timer
    assert not (stage / 'applies.jsonl').exists(), 'Enabling a timer must not apply immediately'
    private(stage / 'hold', '')
    run(ctl + ['start', '--no-block', unit + '.service'])
    wait(lambda: (stage / 'ready').exists())
    contender = run(['/usr/bin/python3', str(driver), 'run'], check=False)
    assert contender.returncode != 0, 'A second helper must not enter an active apply'
    helper.configure(root, False, 'testing')
    assert run(ctl + ['show', unit + '.service', '--property=ActiveState', '--value']).stdout.strip() == 'activating', 'Disabling the timer must not kill an applying service'
    (stage / 'hold').unlink()
    wait(lambda: run(ctl + ['show', unit + '.service', '--property=ActiveState', '--value']).stdout.strip() == 'inactive')
    applies = [json.loads(line) for line in (stage / 'applies.jsonl').read_text().splitlines()]
    assert len(applies) == 1 and applies[0] == {'uid': os.getuid(), 'noNewPrivileges': True}
    assert target in (root / '.env').read_text()
    assert 'https://fixture.invalid/api' in (root / '.env').read_text()
    assert not json.loads((root / 'automatic-update-policy.json').read_text())['enabled']
    assert json.loads((root / 'automatic-update-status.json').read_text())['event'] == 'completed'
    results.append('Real non-root systemd service authenticated and executed one signed Bash fixture; concurrent helper refused; disable preserved the in-flight apply; environment sanitized; NoNewPrivileges enforced')
    reset_version()
    helper.configure(root, True, 'testing')
    private(root / 'update-journal.json', json.dumps({'phase': 'failed'}))
    assert run(ctl + ['start', unit + '.service'], check=False).returncode != 0
    assert json.loads((root / 'automatic-update-status.json').read_text())['code'] == 'recovery-required'
    (root / 'update-journal.json').unlink()
    with (root / 'update.lock').open('r+') as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert run(ctl + ['start', unit + '.service'], check=False).returncode != 0
    assert json.loads((root / 'automatic-update-status.json').read_text())['code'] == 'update-apply-failed'
    assert len((stage / 'applies.jsonl').read_text().splitlines()) == 1
    assert installed in (root / '.env').read_text()
    assert not list(root.glob('.bifrost-panel-update-*')), 'Temporary download staging must be removed'
    results.append('Interrupted recovery refused before execution; a held installation lock refused Bash apply; no mutation, replay, or staging leak')
finally:
    helper.configure(root, False, 'testing')
    assert run(ctl + ['is-active', unit + '.timer'], check=False).returncode != 0
    journal = run(['journalctl', '--user', '-u', unit + '.service', '--no-pager', '-o', 'cat']).stdout
    output = Path(os.environ['BIFROST_SYSTEMD_OUTPUT'])
    output.write_text(json.dumps({'results': results, 'passed': len(results) == 2, 'uid': os.getuid(), 'scope': 'Real systemd with a disposable publisher and signed Bash fixture; full Docker updater and power-loss acceptance remain separate'}, indent=2) + '\n')
    output.chmod(0o644)
    assert 'completed' in journal and 'recovery-required' in journal
for result in results: print('PASS ' + result)
