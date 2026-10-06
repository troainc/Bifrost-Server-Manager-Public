#!/usr/bin/env bash
set -Eeuo pipefail
umask 077
VERSION=v0.1.0-installtest.12
# Matched testing release updater; immutable source + digest.
UPDATER_SOURCE_REF=406c597918e56d57be18f3b21035fb6cf1ed175c
UPDATER_SHA256=bdcde7fa4defd3b4ef11c3d6124da9ab1967e938348d8b0aaaf71c5d597e5ce3
INSTALL_DIR="${BIFROST_INSTALL_DIR:-$HOME/.local/share/bifrost}"
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

fail() { printf '\nBifrost: %s\n' "$*" >&2; exit 1; }
fetch() {
  if command -v curl >/dev/null; then curl -fL --progress-bar --retry 3 "$1" -o "$2";
  elif command -v wget >/dev/null; then wget --quiet --show-progress --output-document="$2" "$1";
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
      exec sudo -- env BIFROST_REINSTALL="${BIFROST_REINSTALL:-0}" BIFROST_RESUME="${BIFROST_RESUME:-0}" BIFROST_INSTALL_ROLE="${BIFROST_INSTALL_ROLE:-controller}" bash "$script" --bootstrap
    elif command -v su >/dev/null; then
      local command_line
      printf -v command_line 'exec env BIFROST_REINSTALL=%q BIFROST_RESUME=%q BIFROST_INSTALL_ROLE=%q bash %q --bootstrap' "${BIFROST_REINSTALL:-0}" "${BIFROST_RESUME:-0}" "${BIFROST_INSTALL_ROLE:-controller}" "$script"
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
  ui_banner
  ui_step 'VM PREPARATION' 'One-time administrator setup; the application runs as bifrost.'
  run_task 'Refresh Debian/Ubuntu package sources' apt-get -q update
  run_task 'Install VM prerequisites' env DEBIAN_FRONTEND=noninteractive apt-get -q install -y uidmap kmod dbus-user-session iptables python3 openssl ca-certificates curl tar
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
  exec runuser -u bifrost -- env -i HOME="$account_home" USER=bifrost LOGNAME=bifrost PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin XDG_RUNTIME_DIR="/run/user/$uid" DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$uid/bus" TERM="${TERM:-xterm}" BIFROST_REINSTALL="${BIFROST_REINSTALL:-0}" BIFROST_RESUME="${BIFROST_RESUME:-0}" BIFROST_INSTALL_ROLE="${BIFROST_INSTALL_ROLE:-controller}" bash "$copied"
}

require_host_runtime() {
  command -v python3 >/dev/null || fail 'Python 3 is required to safely unpack the Host Agent package.'
  command -v sha256sum >/dev/null || fail 'sha256sum is required to verify the Host Agent package.'
  [[ -x /usr/bin/node ]] && /usr/bin/node -e 'process.exit(Number(process.versions.node.split(".")[0]) === 24 ? 0 : 1)' || fail 'Instance Host needs Node.js 24 at /usr/bin/node. Prepare it for this account, then rerun.'
  command -v podman >/dev/null || fail 'Instance Host needs rootless Podman available to this account.'
  [[ "$(podman info --format '{{.Host.Security.Rootless}}' 2>/dev/null || true)" == true ]] || fail 'Podman is not running rootless for this account.'
  systemctl --user show-environment >/dev/null 2>&1 || fail 'A systemd user manager is unavailable. Sign in as the regular game-server operator account and retry.'
}

install_instance_host() {
  [[ $(id -u) -ne 0 ]] || fail 'Run Instance Host setup as the regular account that will own its game services; do not use sudo.'
  require_host_runtime
  local stage package checksum_file digest
  mkdir -p -m 0700 "$HOME/.local/share"
  stage=$(mktemp -d "$HOME/.local/share/bifrost-host-setup.XXXXXX")
  package="$stage/package"
  checksum_file="$stage/bifrost-linux-host-agent.zip.sha256"
  ui_banner
  ui_step 'INSTANCE HOST   Connect this game machine' 'This installs the outbound Host Agent under your current account.'
  fetch "https://github.com/troainc/Bifrost-Server-Manager-Public/releases/download/$VERSION/bifrost-linux-host-agent.zip" "$stage/bifrost-linux-host-agent.zip" || fail 'Could not download the Host Agent package for this release.'
  fetch "https://github.com/troainc/Bifrost-Server-Manager-Public/releases/download/$VERSION/bifrost-linux-host-agent.zip.sha256" "$checksum_file" || fail 'Could not download the Host Agent checksum.'
  (cd "$stage" && sha256sum --check bifrost-linux-host-agent.zip.sha256) || fail 'Host Agent package checksum failed.'
  mkdir -m 0700 "$package"
  python3 - "$stage/bifrost-linux-host-agent.zip" "$package" <<'HOST_ZIP_PY'
import os,pathlib,stat,sys,zipfile
archive,destination=sys.argv[1:]
root=pathlib.Path(destination).resolve(strict=True);seen=set();total=0
with zipfile.ZipFile(archive) as source:
    entries=source.infolist()
    if not entries or len(entries)>10000:raise SystemExit('Invalid Host Agent package entry count.')
    for entry in entries:
        name=entry.filename;path=pathlib.PurePosixPath(name);mode=entry.external_attr>>16;kind=stat.S_IFMT(mode)
        if not name or name.startswith('/') or '\\' in name or ':' in name or any(part in ('','.','..') for part in name.rstrip('/').split('/')):raise SystemExit('Unsafe Host Agent package path.')
        if name.casefold() in seen:raise SystemExit('Duplicate Host Agent package path.')
        seen.add(name.casefold())
        if kind not in (0,stat.S_IFREG,stat.S_IFDIR):raise SystemExit('Host Agent package contains a link or special file.')
        total+=entry.file_size
        if entry.file_size>512*1024*1024 or total>1024*1024*1024:raise SystemExit('Host Agent package exceeds its extraction limit.')
    for entry in entries:
        target=root.joinpath(*pathlib.PurePosixPath(entry.filename).parts)
        if os.path.commonpath((str(root),str(target.resolve(strict=False))))!=str(root):raise SystemExit('Host Agent package path escapes its staging directory.')
        if entry.is_dir():target.mkdir(mode=0o700,parents=True,exist_ok=True);continue
        target.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
        fd=os.open(target,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0),0o600)
        with os.fdopen(fd,'wb') as out,source.open(entry) as inp:
            while True:
                chunk=inp.read(1024*1024)
                if not chunk:break
                out.write(chunk)
HOST_ZIP_PY
  [[ -f "$package/install-agent.sh" && -f "$package/dist/enroll.js" ]] || fail 'The downloaded Host Agent package is incomplete.'
  digest=$(sha256sum "$stage/bifrost-linux-host-agent.zip" | awk '{print $1}')
  printf '%s\n' "$digest" > "$package/.bifrost-package-sha256"
  chmod 0600 "$package/.bifrost-package-sha256"
  printf '\nCreate a fresh one-use code in the Controller under Hosts → Add host. The Host Agent will ask for the Controller panel HTTPS URL and that code.\n'
  bash "$package/install-agent.sh" "$package" "${HOST_FLAGS[@]}"
  rm -rf -- "$stage"
  ui_ok 'Instance Host enrolled and its user service is enabled.'
  printf '  Enrollment connects this machine to the fleet; install a reviewed game Blueprint separately.\n'
}

if [[ "${1:-}" == --update ]]; then
  [[ $# -eq 1 ]] || fail 'Unexpected arguments.'
  update_stage=$(mktemp -d)
  fetch "https://raw.githubusercontent.com/troainc/Bifrost-Server-Manager-Public/$UPDATER_SOURCE_REF/update.sh" "$update_stage/update.sh"
  (cd "$update_stage" && printf '%s  update.sh\n' "$UPDATER_SHA256" | sha256sum --check --status) || fail 'Updater checksum failed.'
  grep -qx "VERSION=$VERSION" "$update_stage/update.sh" || fail 'Pinned updater version differs from the requested release.'
  bash "$update_stage/update.sh"
  rm -f "$update_stage/update.sh"; rmdir "$update_stage"
  exit 0
fi
[[ "${1:-}" != --help ]] || { echo 'Run bash install.sh to choose Controller, standalone Instance node, or Hybrid. Pass --controller, --instance, or --hybrid; --host installs only an Agent for an existing Controller. Existing Hosts can use --host --upgrade; revoked Hosts can use --host --upgrade --re-enroll.'; exit 0; }
HOST_FLAGS=()
if [[ "${1:-}" == --host ]]; then
  BIFROST_INSTALL_ROLE=host
  shift
  while [[ $# -gt 0 ]]; do
    case "$1" in --upgrade|--re-enroll) HOST_FLAGS+=("$1"); shift;; *) fail 'Host accepts only --upgrade and --re-enroll.';; esac
  done
elif [[ "${1:-}" == --controller || "${1:-}" == --instance || "${1:-}" == --hybrid ]]; then
  BIFROST_INSTALL_ROLE="${1#--}"
  shift
  case "${1:-}" in --reinstall) export BIFROST_REINSTALL=1; shift;; --resume) export BIFROST_RESUME=1; shift;; esac
  [[ $# -eq 0 ]] || fail 'A node role accepts only an optional --reinstall or --resume.'
elif [[ "${1:-}" == --reinstall || "${1:-}" == --resume || "${1:-}" == --prepare-account || "${1:-}" == --bootstrap ]]; then
  BIFROST_INSTALL_ROLE="${BIFROST_INSTALL_ROLE:-controller}"
elif [[ -z "${BIFROST_INSTALL_ROLE:-}" ]]; then
  [[ -r /dev/tty ]] || fail 'Choose --controller, --instance, --hybrid or --host when running without a terminal.'
  ui_banner
  ui_step '01 / 06   Choose this machine’s role' 'Controller manages a fleet. Instance manages this machine. Hybrid does both.'
  printf "\n  1) Controller — central fleet panel; separate game Hosts\n  2) Standalone Instance node — local panel and local game Host; can pair later\n  3) Hybrid — fleet Controller plus a local game Host\n  4) Host Agent only — join an existing Controller; no new panel\n\n"
  printf '  A game instance is one server created later in the Controller panel.\n'
  printf '  For one game server, you still need a Controller and an enrolled Host.\n'
  printf '  Instance and Hybrid panels require a separately prepared local Host Agent account.\n  Complete panel setup and licensing, then enroll that local Agent before creating games.\n\n'
  read -r -p 'Select 1, 2, 3 or 4: ' install_choice </dev/tty
  case "$install_choice" in 1) BIFROST_INSTALL_ROLE=controller;; 2) BIFROST_INSTALL_ROLE=instance;; 3) BIFROST_INSTALL_ROLE=hybrid;; 4) BIFROST_INSTALL_ROLE=host;; *) fail 'Choose a displayed node role or Host Agent only.';; esac
fi
case "$BIFROST_INSTALL_ROLE" in host) install_instance_host; exit 0;; controller|instance|hybrid) ;; *) fail 'Installation role is missing; choose Controller, Instance, Hybrid or Host Agent.';; esac
if [[ "${1:-}" == --reinstall ]]; then export BIFROST_REINSTALL=1; shift; fi
if [[ "${1:-}" == --resume ]]; then export BIFROST_RESUME=1; shift; fi
case "${1:-}" in
  --prepare-account|--bootstrap) [[ $# -eq 1 ]] || fail 'Unexpected arguments.'; automated_bootstrap;;
  '') [[ $# -eq 0 ]] || fail 'Unexpected arguments.'; [[ $(id -un) == bifrost && $(id -u) -ne 0 ]] || automated_bootstrap;;
  *) fail 'Unknown argument.';;
esac
assert_service_account
[[ $(uname -s) == Linux && $(uname -m) == x86_64 ]] || fail 'Linux x86_64 is required.'
[[ "$INSTALL_DIR" == /* && "$INSTALL_DIR" != / && "$INSTALL_DIR" != "$HOME" ]] || fail 'Invalid installation directory.'
if [[ "${BIFROST_REINSTALL:-0}" == 1 ]]; then
  expected="$(readlink -f "$HOME")/.local/share/bifrost"
  actual=$(readlink -m "$INSTALL_DIR")
  [[ "$INSTALL_DIR" == "$HOME/.local/share/bifrost" && "$actual" == "$expected" && ! -L "$INSTALL_DIR" ]] || fail 'Reinstall only supports the standard bifrost home installation; refusing an alternate or symlinked path.'
  [[ -r /dev/tty ]] || fail 'Reinstall requires an interactive terminal.'
  ui_banner
  ui_step 'RESET TEST INSTALLATION' 'This permanently deletes this panel database, administrator, credentials and local configuration.'
  printf '  Target: %s\n' "$actual"
  read -r -p 'Type WIPE to confirm a clean reinstall: ' confirmation </dev/tty
  [[ "$confirmation" == WIPE ]] || fail 'Reinstall cancelled; data preserved.'
  if [[ -d "$actual" ]]; then
    [[ $(stat -c %u "$actual") -eq $(id -u) && -f "$actual/compose.yaml" && -f "$actual/.env" ]] || fail 'Refusing to wipe a directory that is not an owned, configured Bifrost installation.'
    export PATH="$HOME/.local/bin:$HOME/bin:$PATH:/usr/sbin:/sbin"
    export DOCKER_HOST="unix:///run/user/$(id -u)/docker.sock"
    docker info --format '{{json .SecurityOptions}}' | grep -qi rootless || fail 'Rootless Docker is required to remove this installation.'
    (cd "$actual" && run_task 'Remove test containers and database volumes' docker compose down --volumes)
    rm -rf -- "$actual"
    ui_ok 'Old test installation removed. Beginning a fresh install.'
  fi
fi
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
ui_banner
printf '\nThank you for downloading the TROA Bifrost Server Manager\n\nWe hope you enjoy! Please report any issues in our support Discord:\n  discord.gg/troainc\nLearn more about our projects:\n  therealmsofasgard.com\n'
ui_step '02 / 06   Prepare your account' 'Checking your tools and rootless Docker.'
for tool in sha256sum tar awk sed sort; do command -v "$tool" >/dev/null || fail "Missing base OS tool: $tool"; done
bootstrap_prerequisites
ui_step '03 / 06   Make it yours' 'Choose the address and port for your new panel.'
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
ui_step '04 / 06   Download your command center' 'Downloading the release, then verifying its checksum.'
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
ui_step '05 / 06   Secure your installation' 'Creating private credentials and HTTPS configuration.'
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
python3 - "$INSTALL_DIR" "$address" "$port" "$scratch/networks.json" "$BIFROST_INSTALL_ROLE" <<'PY'
import ipaddress,json,pathlib,sys,socket
root=pathlib.Path(sys.argv[1]);used=[]
for network in json.loads(pathlib.Path(sys.argv[4]).read_text()):
    for item in (network.get('IPAM') or {}).get('Config') or []:
        if item.get('Subnet'):used.append(ipaddress.ip_network(item['Subnet'],strict=False))
for index in range(256):
    subnet=ipaddress.ip_network(f'10.240.{index}.0/24')
    if not any(subnet.overlaps(existing) for existing in used):break
else:raise SystemExit('No available Docker subnet.')
values={'BIFROST_NODE_ROLE':sys.argv[5],'BIFROST_NODE_HOSTNAME':socket.gethostname(),'BIFROST_PUBLIC_URL':f'https://{sys.argv[2]}:{sys.argv[3]}','BIFROST_HTTPS_PORT':sys.argv[3],'BIFROST_PRIVATE_SUBNET':str(subnet),'BIFROST_WEB_NETWORK_IP':str(subnet.network_address+10),'BIFROST_TRUSTED_PROXIES':f'127.0.0.1,::1,{subnet.network_address+10}'}
env=root/'.env';env.write_text((root/'.env.example').read_text()+'\n'+'\n'.join(f'{k}={v}' for k,v in values.items())+'\n');env.chmod(0o600)
PY
printf '\nLicensing uses your installation identifier and check-ins; optional analytics stays off.\n'
read -r -p 'Configure the TROA license service now? [Y/n]: ' configure_license </dev/tty
if [[ "$configure_license" != [Nn] ]]; then
  read -r -p 'Master license HTTPS URL [https://bifrost.therealmsofasgard.com/api]: ' license_url </dev/tty
  license_url=${license_url:-https://bifrost.therealmsofasgard.com/api}
  read -r -p 'Matching public verification PEM path (Enter uses bundled TROA key): ' key_file </dev/tty
  key_file=${key_file:-$INSTALL_DIR/config/license-signing-public.pem}
  python3 - "$INSTALL_DIR" "$license_url" "$key_file" <<'LICENSE_SETUP_PY'
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
else
  printf 'License configuration skipped. You can configure it later with the updater; game management remains gated.\n'
fi

printf '\nThis is a testing release. Qualified deployment review is still pending.\n'
read -r -p 'Enable license testing before completing your local review? [y/N, Enter keeps setting]: ' test_intake </dev/tty
case "$test_intake" in
  [Yy]|[Nn])
    test_value=false; [[ "$test_intake" != [Yy] ]] || test_value=true
    python3 - "$INSTALL_DIR/.env" "$test_value" <<'TEST_INTAKE_PY'
import pathlib,sys
p=pathlib.Path(sys.argv[1]);lines=[line for line in p.read_text().splitlines() if line.partition('=')[0]!='BIFROST_LICENSE_TEST_INTAKE']
p.write_text('\n'.join(lines+[f'BIFROST_LICENSE_TEST_INTAKE={sys.argv[2]}'])+'\n');p.chmod(0o600)
TEST_INTAKE_PY
    ;;
  '') ;;
  *) fail 'Answer y or n for testing intake.';;
esac
run_task 'Load verified application images' docker load --input "$INSTALL_DIR/customer-images.tar"
python3 - "$INSTALL_DIR/customer-images.tar" "$INSTALL_DIR/IMAGE-LOCK.json" <<'IMAGE_IDENTITY_PY'
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
rm -f "$INSTALL_DIR/customer-images.tar"
ui_step '06 / 06   Bring your panel online' 'Waiting for the database, API and web services to be healthy.'
cd "$INSTALL_DIR"
docker compose config --quiet
run_task 'Start and check all panel services' docker compose up -d --wait --wait-timeout 180
ui_step 'YOUR BIFROST PANEL IS READY' 'Open the panel to confirm its node role and begin onboarding.'
printf '\n  Node role: %s\n' "$BIFROST_INSTALL_ROLE"
if [[ "$BIFROST_INSTALL_ROLE" == instance || "$BIFROST_INSTALL_ROLE" == hybrid ]]; then
  printf '  Next: prepare a separate non-root game-service account with Node.js 24 and rootless Podman.\n  After panel setup and license activation, use Hosts → Add host to pair that local Agent.\n  Run bash install.sh --host as the prepared game account, using this panel URL.\n  Standalone Instance nodes later use an explicit ownership handover to a parent Controller.\n'
fi
printf '\n  Panel     https://%s:%s/install\n  Account   bifrost (non-root)\n  Files     %s\n\n  Your test HTTPS certificate is self-signed.\n  Your browser will ask you to confirm it.\n\n  Support   discord.gg/troainc\n\n' "$address" "$port" "$INSTALL_DIR"
ui_rule
