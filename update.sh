#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
VERSION=v0.1.0-installtest.3
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
  [[ -f "$key_file" ]] || fail 'Public key file not found.'
  openssl pkey -pubin -in "$key_file" -noout >/dev/null || fail 'Not a valid public key.'
  python3 - "$license_url" .env <<'PY'
import pathlib,sys,urllib.parse
url=urllib.parse.urlsplit(sys.argv[1])
if url.scheme!='https' or not url.hostname or url.username or url.password or url.query or url.fragment or any(c.isspace() for c in sys.argv[1]):raise SystemExit('Use an absolute HTTPS licensing-service URL')
p=pathlib.Path(sys.argv[2]);lines=[l for l in p.read_text().splitlines() if not l.startswith('BIFROST_LICENSE_URL=')];p.write_text('\n'.join(lines+[f'BIFROST_LICENSE_URL={sys.argv[1]}'])+'\n')
PY
  cp "$key_file" config/license-signing-public.pem
fi
chmod 0644 config/license-signing-public.pem
docker compose config --quiet
run_task 'Apply update and check service health' docker compose up -d --wait --wait-timeout 180 --force-recreate migrate control-plane web https
ui_step 'UPDATE COMPLETE' 'Refresh your browser to see the latest panel.'
printf '\nUpdated to %s. Your database, administrator and credentials were preserved.\nConfiguration backup: %s/%s\nLicense activation requires a reachable HTTPS licensing service and its matching public key.\n' "$VERSION" "$root" "$backup"
