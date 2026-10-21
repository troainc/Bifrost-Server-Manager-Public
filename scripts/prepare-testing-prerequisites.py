#!/usr/bin/env python3
"""Prepare the signed maintained Linux baseline for explicitly consenting testers.

Creates missing executable files only. Never upgrades a daemon or starts a service.
Source, notices and raw security evidence remain in the protected download directory.
"""
import argparse
import importlib.util
import os
import pathlib
import platform
import shutil
import stat
import sys
import tempfile
import urllib.parse
import urllib.request
import tarfile

sys.dont_write_bytecode = True
HERE = pathlib.Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('baseline', HERE / 'verify-prerequisite-baseline.py')
BASELINE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASELINE)
ORIGINS = {'github.com', 'release-assets.githubusercontent.com', 'objects.githubusercontent.com'}


def approved(url):
    parsed = urllib.parse.urlsplit(url)
    if (parsed.scheme != 'https' or parsed.hostname not in ORIGINS
            or parsed.username or parsed.password or parsed.port not in (None, 443)):
        raise ValueError('Unapproved prerequisite download origin.')


class Redirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, url):
        approved(url)
        return super().redirect_request(request, response, code, message, headers, url)


def protected_directory(path):
    if not path.is_absolute() or path.resolve() != path:
        raise ValueError('Physical absolute prerequisite directories required.')
    if path.exists():
        info = path.stat()
        if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid()
                or info.st_mode & 0o022):
            raise ValueError('Prerequisite directory must be owned by this account and not group/world writable.')
    else:
        protected_directory(path.parent)
        path.mkdir(mode=0o700)


def fetch(name, target):
    url = ('https://github.com/troainc/Bifrost-Server-Manager-Public/releases/download/'
           + BASELINE.VERSION + '/' + name)
    approved(url)
    limit = 512 * 1024**2 if name in BASELINE.ASSETS else 1024 * 1024
    with urllib.request.build_opener(Redirect()).open(url, timeout=60) as source:
        descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(descriptor, 'wb') as output:
            size = 0
            while True:
                block = source.read(min(1024 * 1024, limit - size + 1))
                if not block:
                    break
                size += len(block)
                if size > limit:
                    raise ValueError('Prerequisite download exceeds its bound.')
                output.write(block)
            if not size:
                raise ValueError('Empty prerequisite download.')


def install_verified(root, home):
    # Verify every payload and every archive entry before creating executable paths.
    BASELINE.verify_baseline(root)
    protected_directory(home)
    destinations = {}
    for name in BASELINE.TOOLS:
        target = (home / '.docker/cli-plugins/docker-compose' if name == 'docker-compose'
                  else home / 'bin' / pathlib.PurePosixPath(name).name)
        if target.exists() or target.is_symlink():
            raise ValueError('Existing prerequisite file retained; automatic replacement refused: ' + str(target))
        destinations[name] = target
    for folder in {target.parent for target in destinations.values()}:
        protected_directory(folder)
    # Exclusive no-follow creation prevents overwrite even if a competing install appears.
    # On interruption retain partial files for review; never erase or retry over them.
    with tarfile.open(root / 'prerequisite-baseline.tar.gz') as archive:
        for member in archive:
            name = member.name.removeprefix('./')
            descriptor = os.open(destinations[name], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o500)
            with os.fdopen(descriptor, 'wb') as output, archive.extractfile(member) as source:
                shutil.copyfileobj(source, output, 1024 * 1024)
                output.flush()
                os.fsync(output.fileno())
    print('Prepared signed Bifrost-maintained testing prerequisites. No daemon or service was changed.')
    print('Preserved source/notices/raw evidence: ' + str(root))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--accept-testing-build', action='store_true')
    arguments = parser.parse_args()
    if not arguments.accept_testing_build:
        raise ValueError('Explicit maintained testing-build consent required.')
    if os.getuid() == 0 or platform.system() != 'Linux' or platform.machine() not in ('x86_64', 'amd64'):
        raise ValueError('Run only as the non-root Linux amd64 Bifrost account.')
    if any(shutil.which(tool) for tool in ('docker', 'dockerd', 'dockerd-rootless-setuptool.sh', 'docker-compose')):
        raise ValueError('Existing runtime detected and retained. Provision or review its missing components separately.')
    home = pathlib.Path.home()
    cache = home / '.local/share/bifrost-prerequisite-testing'
    protected_directory(cache)
    root = pathlib.Path(tempfile.mkdtemp(prefix=BASELINE.VERSION + '-', dir=cache))
    for name in sorted(BASELINE.ASSETS | {'release-manifest.json', 'release-manifest.sig', 'release-signing-public.pem'}):
        print('Downloading signed prerequisite asset: ' + name, flush=True)
        fetch(name, root / name)
    install_verified(root, home)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit('Testing prerequisite preparation refused; retained runtimes/data were not replaced: ' + str(error))
