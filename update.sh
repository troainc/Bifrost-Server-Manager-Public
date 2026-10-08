#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
VERSION=v0.1.0-installtest.19
# Terminal presentation: readable without color, animation, or a wide terminal.
UI_RESET='' UI_BLUE='' UI_GREEN='' UI_GOLD='' UI_DIM='' UI_BOLD=''
if [[ -t 1 && -z "${NO_COLOR:-}" && "${TERM:-dumb}" != dumb ]]; then
  UI_RESET=$'\033[0m'; UI_BLUE=$'\033[38;5;81m'; UI_GREEN=$'\033[38;5;114m'
  UI_GOLD=$'\033[38;5;221m'; UI_DIM=$'\033[2m'; UI_BOLD=$'\033[1m'
fi
ui_rule(){ printf '%s%s%s\n' "$UI_DIM" '------------------------------------------------------------' "$UI_RESET"; }
ui_banner(){
  printf '\n'; ui_rule
  printf '  %s%sT R O A   /   B I F R O S T%s\n' "$UI_BLUE" "$UI_BOLD" "$UI_RESET"
  printf '  SERVER MANAGER  %s|  Linux %s%s\n' "$UI_DIM" "$VERSION" "$UI_RESET"
  printf '  %sServers bridge worlds.%s\n' "$UI_DIM" "$UI_RESET"
  ui_rule
}
ui_step(){ printf '\n%s%s  %s%s\n' "$UI_GOLD" "$UI_BOLD" "$1" "$UI_RESET"; [[ -z "${2:-}" ]] || printf '  %s%s%s\n' "$UI_DIM" "$2" "$UI_RESET"; ui_rule; }
ui_ok(){ printf '  %s[OK]%s %s\n' "$UI_GREEN" "$UI_RESET" "$*"; }
run_task(){
  local label="$1" log status; shift
  log=$(mktemp /tmp/bifrost-task.XXXXXX)
  printf '  %s[WORK]%s %s\n' "$UI_BLUE" "$UI_RESET" "$label"
  if "$@" >"$log" 2>&1; then
    rm -f "$log"; ui_ok "$label"
  else
    status=$?; printf '\n  %s[FAILED]%s %s\n' "$UI_GOLD" "$UI_RESET" "$label" >&2
    tail -n 25 "$log" >&2
    printf '\n  Full diagnostic log: %s\n' "$log" >&2
    return "$status"
  fi
}

fail(){ printf '\nBifrost update: %s\n' "$*" >&2; exit 1; }
script=$(readlink -f "${BASH_SOURCE[0]}")
if [[ $(id -un) != bifrost ]]; then
  if [[ $(id -u) != 0 ]]; then
    printf 'Administrator authentication is needed to switch to bifrost.\n'
    if command -v sudo >/dev/null && sudo -v; then exec sudo bash "$script"; fi
    printf -v line 'exec bash %q' "$script"; exec su -s /bin/bash -c "$line" root
  fi
  export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
  cd / || fail 'Cannot select a safe update working directory.'
  command -v runuser >/dev/null || fail 'The VM is missing runuser (util-linux package).'
  uid=$(id -u bifrost); home=$(getent passwd bifrost | cut -d: -f6)
  [[ "$uid" != 0 ]] || fail 'bifrost must be non-root.'
  install -d -m 0700 -o bifrost -g "$(id -gn bifrost)" "$home/.local/share/bifrost-bootstrap"
  copied="$home/.local/share/bifrost-bootstrap/update.sh"
  [[ "$script" == "$copied" ]] || install -m 0700 -o bifrost -g "$(id -gn bifrost)" "$script" "$copied"
  exec runuser -u bifrost -- env -i HOME="$home" USER=bifrost LOGNAME=bifrost PATH="$home/.local/bin:$home/bin:/usr/bin:/bin:/usr/sbin:/sbin" XDG_RUNTIME_DIR="/run/user/$uid" DOCKER_HOST="unix:///run/user/$uid/docker.sock" bash "$copied"
fi
[[ $(id -u) != 0 ]] || fail 'Root runtime prohibited.'
export PATH="$HOME/.local/bin:$HOME/bin:$PATH:/usr/sbin:/sbin"
export DOCKER_HOST="unix:///run/user/$(id -u)/docker.sock"
ui_banner
ui_step 'UPDATE YOUR COMMAND CENTER' 'Your database, administrator and credentials will be preserved.'
root="$HOME/.local/share/bifrost"
[[ -f "$root/.env" && -d "$root/secrets" ]] || fail 'No configured installation exists.'
# Changing libc/locale implementations is not a safe in-place database update.
# Refuse older Debian bundles before downloading or modifying any installation data.
python3 - "$root/.env" <<'DATABASE_RUNTIME_PY'
import pathlib,sys
values=dict(line.split('=',1) for line in pathlib.Path(sys.argv[1]).read_text().splitlines() if '=' in line and not line.startswith('#'))
if values.get('BIFROST_POSTGRES_RUNTIME')!='alpine17-v1':
    raise SystemExit('This testing release requires a fresh installation or a separately verified database backup/restore migration. Existing Debian PostgreSQL data is unchanged; automatic cross-runtime update is refused.')
DATABASE_RUNTIME_PY
docker info --format '{{json .SecurityOptions}}' | grep -qi rootless || fail 'Rootless Docker is required.'
scratch=$(mktemp -d);trap 'rm -rf -- "$scratch"' EXIT
base="https://github.com/troainc/Bifrost-Server-Manager-Public/releases/download/$VERSION"
bundle="bifrost-linux-amd64-$VERSION.tar.gz"
curl -fL --progress-bar --retry 3 "$base/$bundle" -o "$scratch/$bundle"
curl -fL --progress-bar --retry 3 "$base/SHA256SUMS" -o "$scratch/SHA256SUMS"
(cd "$scratch" && grep -F "  $bundle" SHA256SUMS | sha256sum --check --status) || fail 'Package checksum failed.'
python3 - "$scratch/$bundle" "$scratch/package" <<'PY'
import pathlib,sys,tarfile
root=pathlib.Path(sys.argv[2]);root.mkdir(mode=0o700)
with tarfile.open(sys.argv[1]) as archive:
    entries=archive.getmembers();seen=set();total=0
    if not entries or len(entries)>1000:raise SystemExit('Invalid package')
    for entry in entries:
        path=pathlib.PurePosixPath(entry.name);total+=entry.size;key=str(path).casefold()
        if path.is_absolute() or '..' in path.parts or key in seen or not(entry.isfile() or entry.isdir()) or total>4*1024**3:raise SystemExit('Unsafe package')
        seen.add(key)
    archive.extractall(root,filter='data')
PY

printf '\nThis is a testing release. Qualified deployment review is still pending.\n'
read -r -p 'Enable license testing before completing your local review? [y/N, Enter keeps setting]: ' test_intake </dev/tty
case "$test_intake" in
  [Yy]|[Nn])
    test_value=false; [[ "$test_intake" != [Yy] ]] || test_value=true
    python3 - "$root/.env" "$test_value" <<'TEST_INTAKE_PY'
import pathlib,sys
p=pathlib.Path(sys.argv[1]);lines=[line for line in p.read_text().splitlines() if line.partition('=')[0]!='BIFROST_LICENSE_TEST_INTAKE']
p.write_text('\n'.join(lines+[f'BIFROST_LICENSE_TEST_INTAKE={sys.argv[2]}'])+'\n');p.chmod(0o600)
TEST_INTAKE_PY
    ;;
  '') ;;
  *) fail 'Answer y or n for testing intake.';;
esac
run_task 'Load verified update images' docker load --input "$scratch/package/customer-images.tar"
python3 - "$scratch/package/customer-images.tar" "$scratch/package/IMAGE-LOCK.json" <<'IMAGE_IDENTITY_PY'
"""Verify Docker image identity against the checksummed release archive.

Classic Docker reports the config digest as Id; containerd reports the manifest
digest. Accept either only when archive metadata binds it to the locked config.
This file is embedded verbatim in both standalone installer scripts.
"""
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import tarfile


def archive_identities(path):
    with tarfile.open(path, "r:") as archive:
        members = archive.getmembers()
        if len(members) > 10000:
            raise ValueError("Too many image archive entries")
        files = {}
        for member in members:
            name = str(pathlib.PurePosixPath(member.name))
            if name in files or name.startswith("/") or ".." in pathlib.PurePosixPath(name).parts:
                raise ValueError("Unsafe or duplicate image archive entry")
            files[name] = member

        def read_json(name, digest=None):
            member = files.get(name)
            if not member or not member.isfile() or not 0 < member.size <= 1024 * 1024:
                raise ValueError("Missing or unsafe image metadata: " + name)
            data = archive.extractfile(member).read()
            actual = "sha256:" + hashlib.sha256(data).hexdigest()
            if digest is not None and actual != digest:
                raise ValueError("Image metadata digest mismatch: " + name)
            return json.loads(data), actual

        saved, _ = read_json("manifest.json")
        identities = {}
        for image in saved:
            config, digest = read_json(image["Config"])
            if config.get("os") != "linux" or config.get("architecture") != "amd64":
                raise ValueError("Only Linux amd64 release images are supported")
            for tag in image.get("RepoTags") or []:
                if tag in identities:
                    raise ValueError("Ambiguous image tag: " + tag)
                identities[tag] = {"config": digest, "ids": {digest}}

        if "index.json" in files:
            index, _ = read_json("index.json")
            for descriptor in index["manifests"]:
                tag = descriptor.get("annotations", {}).get("io.containerd.image.name", "")
                if tag.startswith("docker.io/"):
                    tag = tag[len("docker.io/"):]
                if tag not in identities:
                    continue
                def manifest_data(item):
                    digest = item["digest"]
                    if not re.fullmatch(r"sha256:[a-f0-9]{64}", digest):
                        raise ValueError("Invalid OCI manifest digest")
                    data, _ = read_json("blobs/sha256/" + digest[7:], digest)
                    return data, digest

                manifest, digest = manifest_data(descriptor)
                if "manifests" in manifest:
                    # BuildKit's containerd store may tag an OCI index containing
                    # one runnable image and its non-runnable provenance record.
                    children = manifest["manifests"]
                    if manifest.get("schemaVersion") != 2 or not isinstance(children, list) or not 1 <= len(children) <= 8:
                        raise ValueError("Invalid or excessive OCI index")
                    runnable, attestations = [], []
                    for child in children:
                        body, child_digest = manifest_data(child)
                        if "manifests" in body:
                            raise ValueError("Nested OCI indexes are unsupported")
                        platform = child.get("platform", {})
                        annotations = child.get("annotations", {})
                        if platform.get("os") == "linux" and platform.get("architecture") == "amd64":
                            if body.get("config", {}).get("digest") != identities[tag]["config"]:
                                raise ValueError("OCI manifest/config identity mismatch: " + tag)
                            runnable.append(child_digest)
                        elif platform == {"architecture": "unknown", "os": "unknown"} and annotations.get("vnd.docker.reference.type") == "attestation-manifest":
                            attestations.append(annotations.get("vnd.docker.reference.digest"))
                        else:
                            raise ValueError("Unsupported OCI index platform")
                    if len(runnable) != 1 or any(reference != runnable[0] for reference in attestations):
                        raise ValueError("Ambiguous or unbound OCI index")
                    identities[tag]["ids"].update([digest, runnable[0]])
                    continue
                if manifest.get("config", {}).get("digest") != identities[tag]["config"]:
                    raise ValueError("OCI manifest/config identity mismatch: " + tag)
                identities[tag]["ids"].add(digest)
        return identities


def main(args):
    archive_path, lock_path = args[:2]
    identities = archive_identities(archive_path)
    if len(args) > 2 and args[2] == "--write-lock":
        tags = args[3:]
        if len(tags) != 3 or len(set(tags)) != 3:
            raise ValueError("Exactly three release image tags are required")
        lock = {tag: identities[tag]["config"] for tag in tags}
        pathlib.Path(lock_path).write_text(json.dumps(lock, indent=2) + "\n")
        return
    lock = json.loads(pathlib.Path(lock_path).read_text())
    if not isinstance(lock, dict) or len(lock) != 3:
        raise ValueError("Exactly three locked release images are required")
    for tag, expected in lock.items():
        if not re.fullmatch(r"bifrost/(control-plane|web|postgres):v[0-9]+\.[0-9]+\.[0-9]+-installtest\.[0-9]+", tag):
            raise ValueError("Unexpected release image tag: " + tag)
        if not isinstance(expected, str) or not re.fullmatch(r"sha256:[a-f0-9]{64}", expected):
            raise ValueError("Invalid locked configuration digest: " + tag)
        identity = identities.get(tag)
        if not identity or identity["config"] != expected:
            raise ValueError("Archive/lock configuration mismatch: " + tag)
        image = json.loads(subprocess.check_output(["docker", "image", "inspect", tag], text=True))[0]
        actual = image["Id"]
        if actual not in identity["ids"] or image.get("Os") != "linux" or image.get("Architecture") != "amd64":
            raise ValueError(f"Image identity mismatch: {tag}; loaded={actual}; allowed={','.join(sorted(identity['ids']))}")
        print(f"Verified {tag}: {actual} (locked config {expected})")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except (ValueError, KeyError, IndexError, OSError, tarfile.TarError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))
IMAGE_IDENTITY_PY
cd "$root"
backup="update-backups/$(date -u +%Y%m%dT%H%M%SZ)";mkdir -p "$backup"
cp -a .env compose.yaml config "$backup/"
# Database volumes, passwords, signing keys and TLS certificate are preserved.
if [[ ! -e secrets/local-host-bootstrap.json ]]; then printf '{"enabled":false}\n' > secrets/local-host-bootstrap.json; chmod 0644 secrets/local-host-bootstrap.json; fi
[[ ! -L secrets/local-host-bootstrap.json ]] || fail 'Unsafe local Host bootstrap secret.'
cp "$scratch/package/compose.yaml" compose.yaml
for file in "$scratch/package/config"/*; do
  name=$(basename "$file")
  [[ "$name" != license-signing-public.pem || ! -s config/license-signing-public.pem ]] || continue
  # Local executable Blueprint approvals are preserved across releases.
  [[ "$name" != provisioning-catalog.json && "$name" != provisioning-trust.json || ! -e "config/$name" ]] || continue
  cp "$file" "config/$name"
done
cp "$scratch/package/IMAGE-LOCK.json" IMAGE-LOCK.json
python3 - .env "$VERSION" <<'PY'
import pathlib,sys
p=pathlib.Path(sys.argv[1]);lines=p.read_text().splitlines();version=sys.argv[2]
updates={'BIFROST_VERSION':version,'BIFROST_CONTROL_PLANE_IMAGE':f'bifrost/control-plane:{version}','BIFROST_WEB_IMAGE':f'bifrost/web:{version}'}
lines=[line for line in lines if line.partition('=')[0] not in updates]
p.write_text('\n'.join(lines+[f'{k}={v}' for k,v in updates.items()])+'\n')
PY
read -r -p 'Master license HTTPS URL (Enter keeps existing configuration): ' license_url </dev/tty
if [[ -n "$license_url" ]]; then
  read -r -p 'Public verification PEM file path (on this VM, readable by bifrost): ' key_file </dev/tty
  python3 - "$root" "$license_url" "$key_file" <<'LICENSE_SETUP_PY'
import pathlib,re,subprocess,sys,urllib.parse
root=pathlib.Path(sys.argv[1]); raw=sys.argv[2]; key=pathlib.Path(sys.argv[3])
url=urllib.parse.urlsplit(raw)
try: port=url.port
except ValueError: raise SystemExit('Invalid license service port.')
if (url.scheme!='https' or not url.hostname or url.username is not None or url.password is not None
    or url.query or url.fragment or url.path.rstrip('/') not in ('','/api')
    or any(c.isspace() or ord(c)<32 or c in "'\"\\$`#" for c in raw)
    or not re.fullmatch(r'[A-Za-z0-9.:-]+',url.hostname)
    or port is not None and not 1<=port<=65535):
    raise SystemExit('Use an HTTPS license service root or /api URL without credentials or extra parameters.')
if not key.is_file() or key.is_symlink() or not 0<key.stat().st_size<=4096:
    raise SystemExit('Use a regular matching public verification PEM file (maximum 4096 bytes).')
data=key.read_bytes()
if not re.fullmatch(rb'\s*-----BEGIN PUBLIC KEY-----\s+[A-Za-z0-9+/=\r\n]+-----END PUBLIC KEY-----\s*',data):
    raise SystemExit('Only a public key is accepted; never supply an issuer private key.')
check=subprocess.run(['openssl','pkey','-pubin','-outform','DER'],input=data,capture_output=True)
prefix=bytes.fromhex('3059301306072a8648ce3d020106082a8648ce3d03010703420004')
if check.returncode or len(check.stdout)!=91 or not check.stdout.startswith(prefix):
    raise SystemExit('The Bifrost license issuer requires its matching P-256 public key.')
env=root/'.env'; config=root/'config'; destination=config/'license-signing-public.pem'
if env.is_symlink() or config.is_symlink() or destination.is_symlink() or not env.is_file() or not config.is_dir():
    raise SystemExit('Unsafe or missing installation configuration.')
lines=[line for line in env.read_text().splitlines() if line.partition('=')[0]!='BIFROST_LICENSE_URL']
destination.write_bytes(data);destination.chmod(0o644)
env.write_text('\n'.join(lines+[f'BIFROST_LICENSE_URL={raw.rstrip("/")}'])+'\n');env.chmod(0o600)
print('License connection configured. Activation still requires the privacy readiness gate and in-panel disclosure acceptance.')
LICENSE_SETUP_PY
fi
chmod 0644 config/license-signing-public.pem
docker compose config --quiet
run_task 'Apply update and check service health' docker compose up -d --wait --wait-timeout 180 --force-recreate migrate control-plane web https
ui_step 'UPDATE COMPLETE' 'Refresh your browser to see the latest panel.'
printf '\nUpdated to %s. Your database, administrator and credentials were preserved.\nConfiguration backup: %s/%s\nLicense activation requires a reachable HTTPS licensing service and its matching public key.\n' "$VERSION" "$root" "$backup"
