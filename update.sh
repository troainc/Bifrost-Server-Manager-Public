#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
VERSION=v0.1.0-installtest.5
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
python3 - "$scratch/package/IMAGE-LOCK.json" <<'PY'
import json,subprocess,sys
for image,digest in json.load(open(sys.argv[1])).items():
    if subprocess.check_output(['docker','image','inspect',image,'--format','{{.Id}}'],text=True).strip()!=digest:raise SystemExit('Image identity mismatch')
PY
cd "$root"
backup="update-backups/$(date -u +%Y%m%dT%H%M%SZ)";mkdir -p "$backup"
cp -a .env compose.yaml config "$backup/"
# Database volumes, passwords, signing keys and TLS certificate are preserved.
cp "$scratch/package/compose.yaml" compose.yaml
for file in "$scratch/package/config"/*; do
  name=$(basename "$file")
  [[ "$name" != license-signing-public.pem || ! -s config/license-signing-public.pem ]] || continue
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
