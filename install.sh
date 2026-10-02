#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
VERSION=v0.1.0-installtest.1
INSTALL_DIR="${BIFROST_INSTALL_DIR:-$HOME/.local/share/bifrost}"
fail() { printf '\nBifrost: %s\n' "$*" >&2; exit 1; }
fetch() {
  if command -v curl >/dev/null; then curl -fSL --retry 3 "$1" -o "$2";
  elif command -v wget >/dev/null; then wget --output-document="$2" "$1";
  else fail 'This VM needs wget or curl.'; fi
}
bootstrap_prerequisites() {
  export PATH="$HOME/.local/bin:$HOME/bin:$PATH:/usr/sbin:/sbin"
  local account uid tool file missing=()
  account=$(id -un); uid=$(id -u)
  for tool in newuidmap newgidmap; do command -v "$tool" >/dev/null || missing+=("$tool (host uidmap package)"); done
  for file in /etc/subuid /etc/subgid; do
    awk -F: -v name="$account" -v uid="$uid" '($1==name || $1==uid) && $3>=65536 {found=1} END {exit !found}' "$file" 2>/dev/null || missing+=("$file: at least 65536 subordinate IDs for $account")
  done
  if [[ -r /proc/sys/kernel/unprivileged_userns_clone && $(cat /proc/sys/kernel/unprivileged_userns_clone) != 1 ]]; then missing+=('unprivileged user namespaces enabled in the VM'); fi
  if ((${#missing[@]})); then
    printf '\nThis VM is missing host-level rootless prerequisites:\n' >&2
    printf '  - %s\n' "${missing[@]}" >&2
    fail 'These permissions must be provisioned in the VM image by its administrator. Bifrost cannot create them as a non-root user. Docker and Compose will be installed automatically once these are available.'
  fi
  local runtime="$HOME/.local/share/bifrost-prerequisites" packages=()
  command -v python3 >/dev/null || packages+=(python3)
  command -v openssl >/dev/null || packages+=(openssl)
  command -v iptables >/dev/null || packages+=(iptables)
  if ((${#packages[@]})); then
    command -v apt-get >/dev/null && command -v dpkg-deb >/dev/null || fail 'Automatic user-local prerequisites currently require Debian or Ubuntu.'
    mkdir -p "$runtime/packages" "$runtime/root" "$HOME/.local/bin"
    # Download distribution dependencies without installing system packages or elevating privileges.
    local dependencies=()
    mapfile -t dependencies < <(apt-cache depends --recurse --no-recommends --no-suggests --no-conflicts --no-breaks --no-replaces --no-enhances "${packages[@]}" | sed -n '/^[a-zA-Z0-9][a-zA-Z0-9+.:_-]*$/p' | sort -u)
    ((${#dependencies[@]})) || fail 'No package metadata. The VM image needs populated APT package indexes.'
    (cd "$runtime/packages" && apt-get download "${dependencies[@]}") || fail 'Could not download user-local prerequisites from the VM package sources.'
    for file in "$runtime/packages"/*.deb; do dpkg-deb -x "$file" "$runtime/root"; done
    for tool in python3 openssl; do
      if ! command -v "$tool" >/dev/null; then
        printf '#!/usr/bin/env bash\nexport LD_LIBRARY_PATH=%q\n' "$runtime/root/usr/lib/x86_64-linux-gnu:$runtime/root/lib/x86_64-linux-gnu" > "$HOME/.local/bin/$tool"
        [[ "$tool" != python3 ]] || printf 'export PYTHONHOME=%q\n' "$runtime/root/usr" >> "$HOME/.local/bin/$tool"
        printf 'exec %q "$@"\n' "$runtime/root/usr/bin/$tool" >> "$HOME/.local/bin/$tool"
        chmod 0700 "$HOME/.local/bin/$tool"
      fi
    done
    if ! command -v iptables >/dev/null; then
      for tool in iptables ip6tables; do
        printf '#!/usr/bin/env bash\nexport LD_LIBRARY_PATH=%q\nexec -a %q %q "$@"\n' "$runtime/root/usr/lib/x86_64-linux-gnu:$runtime/root/lib/x86_64-linux-gnu" "$tool-nft" "$runtime/root/usr/sbin/xtables-nft-multi" > "$HOME/.local/bin/$tool"
        chmod 0700 "$HOME/.local/bin/$tool"
      done
    fi
    hash -r
  fi
  python3 --version >/dev/null && openssl version >/dev/null && iptables --version >/dev/null || fail 'User-local prerequisite startup failed.'
  command -v systemctl >/dev/null && systemctl --user show-environment >/dev/null 2>&1 || fail 'Log in directly via SSH or the VM console as your user; a user systemd session is required.'
  export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$uid}"
  [[ -d "$XDG_RUNTIME_DIR" && -w "$XDG_RUNTIME_DIR" ]] || fail 'Your login session has no writable runtime directory. Log out and log in directly.'
  if ! command -v dockerd-rootless-setuptool.sh >/dev/null; then
    local version=29.8.2 stage
    stage=$(mktemp -d)
    fetch "https://download.docker.com/linux/static/stable/x86_64/docker-$version.tgz" "$stage/docker.tgz"
    fetch "https://download.docker.com/linux/static/stable/x86_64/docker-rootless-extras-$version.tgz" "$stage/rootless.tgz"
    mkdir -p "$HOME/bin"
    tar -xzf "$stage/docker.tgz" --strip-components=1 -C "$HOME/bin"
    tar -xzf "$stage/rootless.tgz" --strip-components=1 -C "$HOME/bin"
    rm -f "$stage/docker.tgz" "$stage/rootless.tgz"; rmdir "$stage"
    hash -r
  fi
  export DOCKER_HOST="unix://$XDG_RUNTIME_DIR/docker.sock"
  if ! docker info >/dev/null 2>&1; then
    dockerd-rootless-setuptool.sh install
    systemctl --user start docker
  fi
  for attempt in {1..30}; do docker info >/dev/null 2>&1 && break; sleep 1; done
  docker info --format '{{json .SecurityOptions}}' | grep -qi rootless || fail 'Docker is not running rootless.'
  if ! docker compose version >/dev/null 2>&1; then
    local compose_version=v2.39.4 compose_dir="$HOME/.docker/cli-plugins" stage
    mkdir -p "$compose_dir"; stage=$(mktemp -d)
    fetch "https://github.com/docker/compose/releases/download/$compose_version/docker-compose-linux-x86_64" "$stage/docker-compose-linux-x86_64"
    fetch "https://github.com/docker/compose/releases/download/$compose_version/docker-compose-linux-x86_64.sha256" "$stage/docker-compose-linux-x86_64.sha256"
    (cd "$stage" && sha256sum --check docker-compose-linux-x86_64.sha256) || fail 'Compose checksum failed.'
    install -m 0700 "$stage/docker-compose-linux-x86_64" "$compose_dir/docker-compose"
    rm -f "$stage/docker-compose-linux-x86_64" "$stage/docker-compose-linux-x86_64.sha256"; rmdir "$stage"
  fi
  mkdir -p "$HOME/.config/bifrost"
  printf 'export PATH="$HOME/.local/bin:$HOME/bin:$PATH"\nexport DOCKER_HOST="unix:///run/user/%s/docker.sock"\n' "$uid" > "$HOME/.config/bifrost/environment.sh"
  grep -qF '.config/bifrost/environment.sh' "$HOME/.profile" 2>/dev/null || printf '\n. "$HOME/.config/bifrost/environment.sh"\n' >> "$HOME/.profile"
  printf 'Prerequisites ready: user-local tools, rootless Docker and Compose.\n'
  if [[ $(loginctl show-user "$uid" -p Linger --value 2>/dev/null || true) != yes ]]; then
    printf '\nNote: this VM does not enable user lingering. The panel may stop after logout and will start at your next login. Provision user lingering in the VM image for unattended operation.\n'
  fi
}

prepare_account() {
  [[ $(id -u) -eq 0 ]] || fail 'Account creation requires a VM administrator: run bash install.sh --prepare-account from an administrator root shell.'
  command -v useradd >/dev/null || fail 'The VM image needs the useradd utility.'
  if ! id bifrost >/dev/null 2>&1; then
    useradd --create-home --user-group --shell /bin/bash --comment 'TROA Bifrost Server Manager' bifrost
    printf 'Created bifrost with a locked password and a private primary group.\n'
  fi
  [[ $(id -u bifrost) -ne 0 ]] || fail 'The existing bifrost account has UID 0. Refusing to use it.'
  local group
  for group in $(id -nG bifrost); do
    case "$group" in sudo|wheel|docker|lxd|incus-admin) fail "Existing bifrost account belongs to privileged group $group. Remove that membership before continuing.";; esac
  done
  if command -v sudo >/dev/null; then
    command -v visudo >/dev/null || fail 'sudo is present but visudo is missing; cannot validate the service account policy.'
    [[ -d /etc/sudoers.d ]] || fail 'sudo policy include directory is missing.'
    local policy_tmp policy_listing
    policy_tmp=$(mktemp /etc/sudoers.d/.bifrost-policy.XXXXXX)
    printf 'bifrost ALL=(ALL:ALL) !ALL\n' > "$policy_tmp"
    chmod 0440 "$policy_tmp"
    visudo -cf "$policy_tmp" >/dev/null || { rm -f "$policy_tmp"; fail 'Invalid bifrost sudo denial policy.'; }
    [[ ! -L /etc/sudoers.d/zz-bifrost-deny ]] || { rm -f "$policy_tmp"; fail 'Refusing a symlink at the bifrost sudo policy path.'; }
    mv -f "$policy_tmp" /etc/sudoers.d/zz-bifrost-deny
    visudo -c >/dev/null || fail 'The VM sudo configuration did not validate.'
    policy_listing=$(LC_ALL=C sudo -l -U bifrost 2>&1 || true)
    # sudo -l can succeed for a denied account. Inspect command entries, not its exit code.
    if printf '%s\n' "$policy_listing" | awk '/^[[:space:]]*\(/ {sub(/^[[:space:]]*\([^)]*\)[[:space:]]*/, ""); if ($0 != "!ALL") grant=1} END {exit !grant}'; then
      fail 'Another sudo policy entry grants bifrost commands. Remove that conflicting grant before continuing.'
    fi
  fi
  local account_home
  account_home=$(getent passwd bifrost | cut -d: -f6)
  [[ -d "$account_home" && $(stat -c %u "$account_home") -eq $(id -u bifrost) ]] || fail 'The bifrost home directory is missing or owned by another account.'
  chmod 0700 "$account_home"
  command -v loginctl >/dev/null && loginctl enable-linger bifrost || fail 'Could not enable the bifrost user service at boot.'
  printf '\nAccount ready: bifrost. No sudo/wheel membership or sudo policy grant found.\n'
  printf 'The application runs as bifrost; no password or SSH login is needed for this service account.\n'
}
assert_service_account() {
  [[ $(id -un) == bifrost && $(id -u) -ne 0 ]] || fail 'Run the application installer as bifrost. A VM administrator first runs bash install.sh --prepare-account, then sets its password with passwd bifrost. Log in directly as bifrost.'
  local group
  for group in $(id -nG); do
    case "$group" in sudo|wheel|docker|lxd|incus-admin) fail "bifrost has privileged group membership: $group. Remove it before installing.";; esac
  done
  if command -v sudo >/dev/null; then
    local policy_listing
    policy_listing=$(LC_ALL=C sudo -n -l 2>&1 || true)
    if printf '%s\n' "$policy_listing" | awk '/^[[:space:]]*\(/ {sub(/^[[:space:]]*\([^)]*\)[[:space:]]*/, ""); if ($0 != "!ALL") grant=1} END {exit !grant}'; then
      fail 'bifrost has a sudo policy grant. Remove it before installing.'
    fi
  fi
}

automated_bootstrap() {
  local script
  script=$(readlink -f "${BASH_SOURCE[0]}")
  if [[ $(id -u) -ne 0 ]]; then
    printf '\nAdministrator authentication is needed once to prepare the VM and create bifrost.\n'
    if command -v sudo >/dev/null && sudo -v; then
      exec sudo -- env BIFROST_RESUME="${BIFROST_RESUME:-0}" bash "$script" --bootstrap
    elif command -v su >/dev/null; then
      local command_line
      printf -v command_line 'exec env BIFROST_RESUME=%q bash %q --bootstrap' "${BIFROST_RESUME:-0}" "$script"
      printf 'Enter the VM root password at the following prompt.\n'
      exec su -s /bin/bash -c "$command_line" root
    else
      fail 'This VM provides neither sudo nor su for administrator authentication.'
    fi
  fi
  [[ $(uname -s) == Linux && $(uname -m) == x86_64 ]] || fail 'Linux x86_64 is required.'
  [[ -r /etc/os-release ]] || fail 'Cannot identify the VM operating system.'
  export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
  . /etc/os-release
  case "${ID:-}" in debian|ubuntu) ;; *) fail 'Automatic VM preparation currently supports Debian and Ubuntu.';; esac
  printf '\nPreparing VM prerequisites (the Bifrost application will run only as bifrost).\n'
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y uidmap kmod dbus-user-session iptables python3 openssl ca-certificates curl tar
  modprobe nf_tables
  printf 'nf_tables\n' > /etc/modules-load.d/bifrost-rootless.conf
  prepare_account
  local uid account_home copied
  uid=$(id -u bifrost); account_home=$(getent passwd bifrost | cut -d: -f6)
  # Start the user manager independently of an SSH login; no account password is required.
  systemctl start "user@$uid.service"
  [[ -S "/run/user/$uid/bus" ]] || fail 'The bifrost user session bus did not start.'
  install -d -m 0700 -o bifrost -g "$(id -gn bifrost)" "$account_home/.local" "$account_home/.local/share" "$account_home/.local/share/bifrost-bootstrap"
  copied="$account_home/.local/share/bifrost-bootstrap/install.sh"
  [[ "$script" == "$copied" ]] || install -m 0700 -o bifrost -g "$(id -gn bifrost)" "$script" "$copied"
  printf '\nVM preparation complete. Continuing installation as bifrost (UID %s).\n' "$uid"
  exec runuser -u bifrost -- env -i HOME="$account_home" USER=bifrost LOGNAME=bifrost PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin XDG_RUNTIME_DIR="/run/user/$uid" DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$uid/bus" TERM="${TERM:-xterm}" BIFROST_RESUME="${BIFROST_RESUME:-0}" bash "$copied"
}

[[ "${1:-}" != --help ]] || { echo 'Run bash install.sh. The wizard authenticates the VM administrator once, prepares prerequisites and a non-privileged bifrost account, then installs and runs Bifrost as bifrost.'; exit 0; }
if [[ "${1:-}" == --resume ]]; then export BIFROST_RESUME=1; shift; fi
case "${1:-}" in
  --prepare-account|--bootstrap) [[ $# -eq 1 ]] || fail 'Unexpected arguments.'; automated_bootstrap;;
  '') [[ $# -eq 0 ]] || fail 'Unexpected arguments.'; [[ $(id -un) == bifrost && $(id -u) -ne 0 ]] || automated_bootstrap;;
  *) fail 'Unknown argument.';;
esac
assert_service_account
[[ $(uname -s) == Linux && $(uname -m) == x86_64 ]] || fail 'Linux x86_64 is required.'
[[ "$INSTALL_DIR" == /* && "$INSTALL_DIR" != / && "$INSTALL_DIR" != "$HOME" ]] || fail 'Invalid installation directory.'
if [[ -e "$INSTALL_DIR" ]]; then
  [[ "${BIFROST_RESUME:-0}" == 1 && -d "$INSTALL_DIR" && ! -L "$INSTALL_DIR" && ! -e "$INSTALL_DIR/.env" && -f "$INSTALL_DIR/customer-images.tar" && -f "$INSTALL_DIR/IMAGE-LOCK.json" && -f "$INSTALL_DIR/.env.example" && -d "$INSTALL_DIR/secrets" ]] || fail "Existing installation preserved: $INSTALL_DIR. For an interrupted pre-configuration install only, use bash install.sh --resume."
  [[ $(stat -c %u "$INSTALL_DIR") -eq $(id -u) ]] || fail 'Installation is owned by another account.'
  for name in postgres_owner_password.txt bifrost_app_password.txt rate_limit_pepper.txt mfa_encryption_key.txt agent-job-signing-private.pem agent-job-signing-public.pem panel-key.pem panel-cert.pem; do
    [[ -s "$INSTALL_DIR/secrets/$name" && ! -L "$INSTALL_DIR/secrets/$name" ]] || fail "Cannot resume: missing or unsafe credential $name."
  done
else
  [[ "${BIFROST_RESUME:-0}" != 1 ]] || fail 'No interrupted installation exists to resume.'
fi
[[ -r /dev/tty ]] || fail 'Run from an interactive terminal.'
printf '\nThank you for downloading the TROA Bifrost Server Manager\n\nWe hope you enjoy! Please report any issues in our support Discord: discord.gg/troainc\nLearn more about our projects on therelamsofasgard.com\n\n[1/5] Preparing your account and prerequisites\n'
for tool in sha256sum tar awk sed sort; do command -v "$tool" >/dev/null || fail "Missing base OS tool: $tool"; done
bootstrap_prerequisites
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
scratch=$(mktemp -d)
trap 'rm -rf -- "$scratch"' EXIT
if [[ "${BIFROST_RESUME:-0}" != 1 ]]; then
printf '\n[3/5] Downloading Bifrost\n'
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
else
  printf '\nResuming configuration with existing package and credentials.\n'
fi
network_ids=$(docker network ls -q)
if [[ -n "$network_ids" ]]; then docker network inspect $network_ids > "$scratch/networks.json"; else echo '[]' > "$scratch/networks.json"; fi
python3 - "$INSTALL_DIR" "$address" "$port" "$scratch/networks.json" <<'PY'
import ipaddress,json,pathlib,sys
root=pathlib.Path(sys.argv[1]);used=[]
for network in json.loads(pathlib.Path(sys.argv[4]).read_text()):
    for item in (network.get('IPAM') or {}).get('Config') or []:
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
