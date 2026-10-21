#!/usr/bin/env python3
"""Read-only verification of the separately signed local prerequisite candidate."""
import argparse
import importlib.util
import json
import pathlib
import sys
import tarfile

sys.dont_write_bytecode = True

VERSION = 'v0.0.0-prerequisites.1'
SIGNER = '1dba79e7a3d2608b42a5324089d4db548567999210ffbf3dd96ce5cb63a92e6a'
TOOLS = {
    'docker/containerd', 'docker/containerd-shim-runc-v2', 'docker/ctr',
    'docker/docker', 'docker/docker-init', 'docker/docker-proxy', 'docker/dockerd',
    'docker/runc', 'docker-compose', 'docker-rootless-extras/rootlesskit',
    'docker-rootless-extras/dockerd-rootless.sh',
    'docker-rootless-extras/dockerd-rootless-setuptool.sh',
}
ASSETS = {'prerequisite-baseline.tar.gz', 'prerequisite-sources.tar.gz',
          'security-evidence.tar.gz', 'security-assessment.json', 'source-provenance.json'}


def verify_baseline(root, expected_signer=SIGNER):
    if not root.is_absolute() or root.resolve() != root or not root.is_dir():
        raise ValueError('Use an absolute physical candidate directory.')
    verifier_path = pathlib.Path(__file__).parent / 'release-manifest.py'
    spec = importlib.util.spec_from_file_location('local_release_verifier', verifier_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    statement = module.verify(root / 'release-manifest.json', root / 'release-manifest.sig',
                              root / 'release-signing-public.pem', expected_signer, VERSION,
                              {name: root / name for name in ASSETS})
    if {item['name'] for item in statement['artifacts']} != ASSETS:
        raise ValueError('Unexpected prerequisite artifact inventory.')
    for name in ASSETS:
        if (root / name).stat().st_size > 512 * 1024**2:
            raise ValueError('Oversized prerequisite artifact.')
    assessment = json.loads((root / 'security-assessment.json').read_text())
    if (assessment.get('schemaVersion') != 1 or type(assessment.get('unresolvedFindings')) is not int or assessment.get('unresolvedFindings') != 0
            or assessment.get('productionApproved') is not False
            or assessment.get('manualAcceptanceComplete') is not False):
        raise ValueError('Missing local security evidence or false production approval.')
    with tarfile.open(root / 'prerequisite-baseline.tar.gz') as archive:
        inventory = set()
        total = 0
        for item in archive:
            name = item.name.removeprefix('./')
            if (name not in TOOLS or name in inventory or not item.isfile()
                    or item.mode != 0o500 or not 0 < item.size <= 256 * 1024**2):
                raise ValueError('Unsafe or unexpected prerequisite archive member.')
            inventory.add(name)
            total += item.size
            with archive.extractfile(item) as source:
                header = source.read(20)
            if name.endswith('.sh'):
                if not header.startswith(b'#!'):
                    raise ValueError('Expected reviewed shell helper.')
            elif len(header) < 20 or header[:6] != b'\x7fELF\x02\x01' or header[18:20] != b'\x3e\x00':
                raise ValueError('Expected Linux amd64 executable.')
        if inventory != TOOLS or total > 1024**3:
            raise ValueError('Incomplete or oversized prerequisite tool inventory.')
    return statement


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=pathlib.Path)
    arguments = parser.parse_args()
    verify_baseline(arguments.directory)
    print('PASS signed prerequisite candidate and exact tool archive. Verification only: no tools installed, services changed or production approval granted.')
