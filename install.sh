#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
VERSION=v0.1.0-installtest.1
INSTALL_DIR="${BIFROST_INSTALL_DIR:-$HOME/.local/share/bifrost}"
fail() { printf '\nBifrost: %s\n' "$*" >&2; exit 1; }
fetch() {
  if command -v curl >/dev/null; then curl -fSL --retry 3 "$1" -o "$2";
  elif command -v wget >/dev/null; then (cd "$(dirname "$2")" && wget "$1") && test -s "$2";
  else fail 'This VM needs wget or curl.'; fi
}
[[ "${1:-}" != --help ]] || { echo 'Run bash install.sh as a regular Linux user. Requires rootless Docker and Compose v2.'; exit 0; }
[[ $# -eq 0 ]] || fail 'Unknown argument.'
[[ $(id -u) -ne 0 ]] || fail 'Sign in as a regular user. Do not run with sudo or as root.'
[[ $(uname -s) == Linux && $(uname -m) == x86_64 ]] || fail 'Linux x86_64 is required.'
[[ "$INSTALL_DIR" == /* && "$INSTALL_DIR" != / && "$INSTALL_DIR" != "$HOME" ]] || fail 'Invalid installation directory.'
[[ ! -e "$INSTALL_DIR" ]] || fail "Existing installation preserved: $INSTALL_DIR"
[[ -r /dev/tty ]] || fail 'Run from an interactive terminal.'
printf '\nBIFROST SERVER MANAGER — Linux QuickStart\n\n[1/5] Checking your account\n'
for tool in python3 openssl sha256sum tar docker; do command -v "$tool" >/dev/null || fail "Missing $tool. See the README prerequisites."; done
docker compose version >/dev/null || fail 'Docker Compose v2 is required.'
docker info --format '{{json .SecurityOptions}}' 2>/dev/null | grep -qi rootless || fail "Start this user's rootless Docker daemon."
printf '\n[2/5] Panel setup\n'
default_address=$(hostname -I 2>/dev/null | awk '{print $1}')
read -r -p "VM IP or hostname [${default_address:-localhost}]: " address </dev/tty
address=${address:-${default_address:-localhost}}
[[ "$address" =~ ^[A-Za-z0-9][A-Za-z0-9.-]*$ ]] || fail 'Enter a hostname or IPv4 address without a URL or port.'
read -r -p 'HTTPS port [8443]: ' port </dev/tty
port=${port:-8443}
[[ "$port" =~ ^[0-9]{4,5}$ && "$port" -ge 1024 && "$port" -le 65535 ]] || fail 'Choose a port from 1024 to 65535.'
read -r -p "Install at $INSTALL_DIR? [Y/n]: " answer </dev/tty
[[ "$answer" != [Nn]* ]] || exit 0
printf '\n[3/5] Downloading Bifrost\n'
scratch=$(mktemp -d)
trap 'rm -rf -- "$scratch"' EXIT
bundle="bifrost-linux-amd64-$VERSION.tar.gz"
base="https://github.com/troainc/Bifrost-Server-Manager-Public/releases/download/$VERSION"
fetch "$base/$bundle" "$scratch/$bundle" || fail 'Application download failed.'
fetch "$base/SHA256SUMS" "$scratch/SHA256SUMS" || fail 'Checksum download failed.'
(cd "$scratch" && grep -F "  $bundle" SHA256SUMS | sha256sum --check --status) || fail 'Checksum verification failed.'
python3 - "$scratch/$bundle" "$scratch/package" <<'PY'
import pathlib,sys,tarfile
root=pathlib.Path(sys.argv[2]);root.mkdir(mode=0o700)
with tarfile.open(sys.argv[1],'r:gz') as archive:
    entries=archive.getmembers();seen=set();total=0
    if not entries or len(entries)>1000:raise SystemExit('Invalid package.')
    for entry in entries:
        path=pathlib.PurePosixPath(entry.name);key=str(path).casefold();total+=entry.size
        if path.is_absolute() or '..' in path.parts or key in seen or not(entry.isfile() or entry.isdir()) or total>4*1024**3:raise SystemExit('Unsafe package.')
        seen.add(key)
    archive.extractall(root,filter='data')
PY
printf '\n[4/5] Configuring Bifrost\n'
mkdir -p "$(dirname "$INSTALL_DIR")"
mkdir -m 0700 "$INSTALL_DIR"
cp -a "$scratch/package/." "$INSTALL_DIR/"
mkdir -m 0700 "$INSTALL_DIR/secrets"
for name in postgres_owner_password bifrost_app_password rate_limit_pepper; do openssl rand -base64 48 | tr -d '\n' > "$INSTALL_DIR/secrets/$name.txt"; done
openssl rand -base64 32 | tr -d '\n' > "$INSTALL_DIR/secrets/mfa_encryption_key.txt"
openssl genpkey -algorithm ED25519 -out "$INSTALL_DIR/secrets/agent-job-signing-private.pem" 2>/dev/null
openssl pkey -in "$INSTALL_DIR/secrets/agent-job-signing-private.pem" -pubout -out "$INSTALL_DIR/secrets/agent-job-signing-public.pem" 2>/dev/null
san="DNS:$address"
[[ "$address" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]] && san="IP:$address"
openssl req -x509 -newkey rsa:3072 -nodes -days 365 -subj "/CN=$address" -addext "subjectAltName=$san" -keyout "$INSTALL_DIR/secrets/panel-key.pem" -out "$INSTALL_DIR/secrets/panel-cert.pem" >/dev/null 2>&1
# The 0700 parent protects these files on the host; service-specific read-only mounts allow non-root container identities to read them.
chmod 0644 "$INSTALL_DIR"/secrets/*
network_ids=$(docker network ls -q)
if [[ -n "$network_ids" ]]; then docker network inspect $network_ids > "$scratch/networks.json"; else echo '[]' > "$scratch/networks.json"; fi
python3 - "$INSTALL_DIR" "$address" "$port" "$scratch/networks.json" <<'PY'
import ipaddress,json,pathlib,sys
root=pathlib.Path(sys.argv[1]);used=[]
for network in json.loads(pathlib.Path(sys.argv[4]).read_text()):
    for item in network.get('IPAM',{}).get('Config',[]):
        if item.get('Subnet'):used.append(ipaddress.ip_network(item['Subnet'],strict=False))
for index in range(256):
    subnet=ipaddress.ip_network(f'10.240.{index}.0/24')
    if not any(subnet.overlaps(existing) for existing in used):break
else:raise SystemExit('No available Docker subnet.')
values={'BIFROST_PUBLIC_URL':f'https://{sys.argv[2]}:{sys.argv[3]}','BIFROST_HTTPS_PORT':sys.argv[3],'BIFROST_PRIVATE_SUBNET':str(subnet),'BIFROST_WEB_NETWORK_IP':str(subnet.network_address+10),'BIFROST_TRUSTED_PROXIES':f'127.0.0.1,::1,{subnet.network_address+10}'}
env=root/'.env';env.write_text((root/'.env.example').read_text()+'\n'+'\n'.join(f'{k}={v}' for k,v in values.items())+'\n');env.chmod(0o600)
PY
docker load --input "$INSTALL_DIR/customer-images.tar"
python3 - "$INSTALL_DIR/IMAGE-LOCK.json" <<'PY'
import json,subprocess,sys
for name,expected in json.load(open(sys.argv[1])).items():
    actual=subprocess.check_output(['docker','image','inspect',name,'--format','{{.Id}}'],text=True).strip()
    if actual!=expected:raise SystemExit(f'Image identity mismatch: {name}')
PY
rm -f "$INSTALL_DIR/customer-images.tar"
printf '\n[5/5] Starting your panel\n'
cd "$INSTALL_DIR"
docker compose config --quiet
docker compose up -d --wait --wait-timeout 180
printf '\nInstalled. Open https://%s:%s and create your administrator.\nThe VM-test HTTPS certificate is self-signed.\nManage: cd "%s" && docker compose ps\n' "$address" "$port" "$INSTALL_DIR"
