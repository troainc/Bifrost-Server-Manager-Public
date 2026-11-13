#!/usr/bin/env python3
"""Opt-in, local-only scheduled Controller updates. Never updates Agents or games."""
import argparse
import datetime as dt
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile
import urllib.parse
import urllib.request

REPOSITORY = 'troainc/Bifrost-Server-Manager-Public'
SIGNER = '1dba79e7a3d2608b42a5324089d4db548567999210ffbf3dd96ce5cb63a92e6a'
VERSION = re.compile(r'v(\d+)\.(\d+)\.(\d+)(?:-installtest\.(\d+))?')
ALLOWED_HOSTS = {'api.github.com', 'github.com', 'release-assets.githubusercontent.com', 'objects.githubusercontent.com'}
UNIT = 'bifrost-panel-update'


def version(value, channel):
    match = VERSION.fullmatch(value)
    if not match or (match[4] is not None) != (channel == 'testing'):
        raise ValueError('Release channel or version is unsupported.')
    return tuple(int(match[i]) for i in range(1, 4)) + (int(match[4]) if match[4] else 0,)


def protected(path, directory=False):
    info = path.lstat()
    if path.resolve() != path.absolute() or info.st_uid != os.getuid() or info.st_mode & 0o022:
        raise ValueError('Updater path ownership or containment is unsafe.')
    if directory:
        if not stat.S_ISDIR(info.st_mode): raise ValueError('Expected a protected directory.')
    elif not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError('Expected an unlinked regular file.')
    return path


def approved(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != 'https' or parsed.hostname not in ALLOWED_HOSTS or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError('Unapproved release download destination.')


class Redirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, url):
        approved(url)
        return super().redirect_request(request, response, code, message, headers, url)


def fetch(url, limit):
    approved(url)
    request = urllib.request.Request(url, headers={'User-Agent': 'Bifrost-Local-Updater', 'Accept': 'application/vnd.github+json'})
    with urllib.request.build_opener(Redirect()).open(request, timeout=30) as response:
        data = response.read(limit + 1)
    if not data or len(data) > limit: raise ValueError('Release response exceeds its bound.')
    return data


def write_private(path, data):
    # Atomic replacement; the destination is never opened through a link.
    if path.exists() or path.is_symlink(): protected(path)
    fd, temporary = tempfile.mkstemp(prefix='.bifrost-update-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as output:
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def environment(root):
    protected(root, True)
    protected(root / '.env')
    values = dict(line.split('=', 1) for line in (root / '.env').read_text().splitlines() if '=' in line and not line.startswith('#'))
    if values.get('BIFROST_POSTGRES_RUNTIME') != 'alpine17-v1':
        raise ValueError('Cross-runtime database updates require separate migration review.')
    return values


def record(root, event, **fields):
    # Keep one bounded status record; systemd journal retains start/result history.
    entry = {'event': event, 'at': dt.datetime.now(dt.timezone.utc).isoformat(), 'actorUid': os.getuid(), **fields}
    write_private(root / 'automatic-update-status.json', (json.dumps(entry) + '\n').encode())
    print(json.dumps(entry), flush=True)


def check(root, apply=False):
    journal = root / 'update-journal.json'
    if journal.exists():
        if json.loads(protected(journal).read_text()).get('phase') not in ('complete', 'recovered'):
            raise ValueError('An interrupted update requires explicit local recovery before scheduling can continue.')
    policy_path = protected(root / 'automatic-update-policy.json')
    policy = json.loads(policy_path.read_text())
    if set(policy) != {'enabled', 'channel'} or policy['enabled'] is not True or policy['channel'] not in ('stable', 'testing'):
        raise ValueError('Automatic updates are not enabled by the local operator.')
    channel = policy['channel']
    installed = environment(root).get('BIFROST_VERSION', '')
    installed_order = version(installed, channel)
    releases = json.loads(fetch(f'https://api.github.com/repos/{REPOSITORY}/releases?per_page=100', 4 * 1024 * 1024))
    if not isinstance(releases, list): raise ValueError('Invalid release feed.')
    candidates = []
    for release in releases:
        if not isinstance(release, dict) or release.get('draft') or release.get('prerelease') != (channel == 'testing'): continue
        try: order = version(release['tag_name'], channel)
        except (ValueError, KeyError, TypeError): continue
        if order > installed_order: candidates.append((order, release['tag_name']))
    if not candidates:
        record(root, 'current', installed=installed, channel=channel)
        return
    target = max(candidates)[1]
    base = f'https://github.com/{REPOSITORY}/releases/download/{target}'
    with tempfile.TemporaryDirectory(prefix='.bifrost-panel-update-', dir=root) as temporary:
        stage = Path(temporary)
        limits = {'release-signing-public.pem': 4096, 'release-manifest.json': 1024 * 1024,
                  'release-manifest.sig': 64, 'release-manifest.py': 1024 * 1024, 'update.sh': 1024 * 1024}
        for name, limit in limits.items():
            write_private(stage / name, fetch(f'{base}/{name}', limit))
        key, manifest, signature = (stage / name for name in ('release-signing-public.pem', 'release-manifest.json', 'release-manifest.sig'))
        der = subprocess.run(['openssl', 'pkey', '-pubin', '-in', str(key), '-outform', 'DER'], check=True, capture_output=True, timeout=15).stdout
        if len(der) != 44 or not der.startswith(bytes.fromhex('302a300506032b6570032100')) or hashlib.sha256(der).hexdigest() != SIGNER:
            raise ValueError('Untrusted release signer.')
        subprocess.run(['openssl', 'pkeyutl', '-verify', '-pubin', '-inkey', str(key), '-rawin', '-in', str(manifest), '-sigfile', str(signature)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
        statement = json.loads(manifest.read_text())
        # Never execute the downloaded verifier until its bytes are authenticated.
        matches = [item for item in statement['artifacts'] if item.get('name') == 'release-manifest.py']
        verifier_bytes = (stage / 'release-manifest.py').read_bytes()
        if len(matches) != 1 or matches[0]['size'] != len(verifier_bytes) or matches[0]['sha256'] != hashlib.sha256(verifier_bytes).hexdigest():
            raise ValueError('Release verifier does not match its signed identity.')
        spec = importlib.util.spec_from_file_location('authenticated_release', stage / 'release-manifest.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        verified = module.verify(manifest, signature, key, SIGNER, target, {name: stage / name for name in ('release-manifest.py', 'update.sh')})
        script = (stage / 'update.sh').read_text()
        if f'\nVERSION={target}\n' not in script or '\n# BIFROST_UNATTENDED_UPDATE=1\n' not in script:
            raise ValueError('This release has no verified unattended updater; manual update required.')
        bundles = [item for item in verified['artifacts'] if item['name'] == f'bifrost-linux-amd64-{target}.tar.gz']
        if len(bundles) != 1: raise ValueError('Signed Controller bundle is missing.')
        # Bound repeated unattended checkpoints; never prune recovery or game data.
        backups = root / 'update-backups'
        if backups.exists():
            protected(backups, True)
            if len(list(backups.iterdir())) >= 3:
                raise ValueError('Review and escrow retained update checkpoints before another automatic update.')
        if shutil.disk_usage(root).free < 8 * 1024**3 + 3 * bundles[0]['size']:
            raise ValueError('Insufficient free storage for staged update and recovery.')
        record(root, 'ready', installed=installed, target=target, channel=channel, signer=SIGNER)
        if not apply: return
        # Recheck local consent and installed identity immediately before mutation.
        if json.loads(policy_path.read_text()) != policy or environment(root).get('BIFROST_VERSION') != installed:
            raise ValueError('Update policy or installed version changed; update refused.')
        record(root, 'started', installed=installed, target=target, channel=channel, signer=SIGNER)
        clean_env = {key: value for key, value in os.environ.items() if key not in ('BIFROST_RELEASE_DIRECTORY', 'BIFROST_UPDATE_LOCK_FD', 'BASH_ENV', 'ENV')}
        subprocess.run(['/bin/bash', str(stage / 'update.sh'), '--unattended', installed], cwd=root, env=clean_env, check=True, timeout=3600)
        if environment(root).get('BIFROST_VERSION') != target: raise ValueError('Installed version does not match the completed update.')
        record(root, 'completed', installed=installed, target=target, channel=channel, signer=SIGNER)


def configure(root, enabled, channel):
    environment(root)
    units = Path.home() / '.config/systemd/user'
    units.mkdir(parents=True, exist_ok=True)
    protected(units, True)
    driver = protected(root / 'scripts/automatic-panel-updates.py')
    if enabled:
        # Quote systemd arguments, which are not shell expressions.
        def quote(value):
            if any(ord(c) < 32 for c in str(value)): raise ValueError('Unsafe systemd path.')
            return '"' + str(value).replace('\\', '\\\\').replace('"', '\\"').replace('%', '%%').replace('$', '$$') + '"'
        service = f'[Unit]\nDescription=Bifrost signed Controller update\n[Service]\nType=oneshot\nExecStart=/usr/bin/python3 {quote(driver)} run\nTimeoutStartSec=70min\nUMask=0077\nNoNewPrivileges=yes\n'
        timer = '[Unit]\nDescription=Check Bifrost updates daily at 04:00 (server time)\n[Timer]\nOnCalendar=*-*-* 04:00:00\nRandomizedDelaySec=10min\nPersistent=false\n[Install]\nWantedBy=timers.target\n'
        write_private(units / f'{UNIT}.service', service.encode())
        write_private(units / f'{UNIT}.timer', timer.encode())
    # Consent defaults off and belongs to this machine, never the licensing master.
    write_private(root / 'automatic-update-policy.json', (json.dumps({'enabled': enabled, 'channel': channel}) + '\n').encode())
    subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True, timeout=30)
    subprocess.run(['systemctl', '--user', 'enable' if enabled else 'disable', '--now', f'{UNIT}.timer'], check=True, timeout=30)
    record(root, 'enabled' if enabled else 'disabled', channel=channel)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('enable', 'disable', 'check', 'run', 'status'))
    parser.add_argument('--channel', choices=('stable', 'testing'), default='stable')
    args = parser.parse_args()
    if os.getuid() == 0: raise ValueError('Run as the existing non-root bifrost service account.')
    root = Path.home() / '.local/share/bifrost'
    environment(root)
    if args.action == 'status':
        for name in ('automatic-update-policy.json', 'automatic-update-status.json'):
            path = root / name
            if path.exists(): print(protected(path).read_text().strip())
        return
    if args.action in ('enable', 'disable'):
        configure(root, args.action == 'enable', args.channel)
        return
    fd = os.open(root / 'automatic-update.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'r+') as lock:
        protected(root / 'automatic-update.lock')
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try: check(root, apply=args.action == 'run')
        except Exception:
            record(root, 'refused-or-failed', detail='Review the local systemd journal and retained checkpoint; no automatic retry or rollback was forced.')
            raise


if __name__ == '__main__':
    try: main()
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError):
        raise SystemExit('Automatic update refused or failed. Review local status and journal; retained data and checkpoints are not pruned.')
