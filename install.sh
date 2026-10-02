#!/usr/bin/env bash
set -Eeuo pipefail

DEFAULT_VERSION="SET_BY_PUBLIC_RELEASE_WORKFLOW"
VERSION="${BIFROST_VERSION:-$DEFAULT_VERSION}"
INSTALL_DIR="/opt/bifrost"
LICENSE_PUBLIC_KEY=""
PUBLIC_URL=""
LICENSE_URL=""

fail() { printf 'Bifrost installer: %s\n' "$*" >&2; exit 1; }
log() { printf 'Bifrost installer: %s\n' "$*"; }
usage() {
  cat <<'EOF'
Usage: sudo bash install.sh [--version vX.Y.Z] [--license-public-key FILE]
       [--install-dir DIR]

Installs the source-free Linux Controller bundle from the matching public
GitHub release. Debian/Ubuntu amd64 only for this deployment test. A separate TLS reverse proxy
and the vendor-provided public license verification key are required.
EOF
}

ROLE=controller
if [[ $# -gt 0 && "$1" == controller ]]; then shift; fi
while (($#)); do
  case "$1" in
    --version) [[ $# -ge 2 ]] || fail "--version requires a release tag"; VERSION="$2"; shift 2 ;;
    --license-public-key) [[ $# -ge 2 ]] || fail "--license-public-key requires a file"; LICENSE_PUBLIC_KEY="$2"; shift 2 ;;
    --install-dir) [[ $# -ge 2 ]] || fail "--install-dir requires a path"; INSTALL_DIR="$2"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) fail "Unknown option: $1" ;;
  esac
done

[[ "${EUID:-$(id -u)}" -eq 0 ]] || fail "Run with sudo/root."
[[ -r /dev/tty ]] || fail "Interactive setup needs a terminal. Run this installer from a terminal."
[[ "$VERSION" =~ ^v[0-9]+\.[0-9]+\.[0-9]+([.-][A-Za-z0-9.-]+)?$ ]] || fail "Provide a fixed version tag such as v0.1.0-preview.1; floating tags are not accepted."
if [[ -z "$LICENSE_PUBLIC_KEY" ]]; then
  read -r -p 'Path to the vendor-issued public license verification PEM file: ' LICENSE_PUBLIC_KEY </dev/tty
fi
[[ -f "$LICENSE_PUBLIC_KEY" && -r "$LICENSE_PUBLIC_KEY" ]] || fail "Provide the vendor-issued public license verification key with --license-public-key. Do not use a private key."
grep -q -- 'BEGIN PUBLIC KEY' "$LICENSE_PUBLIC_KEY" || fail "The license key must be a PEM public key."
! grep -q -- 'BEGIN .*PRIVATE KEY' "$LICENSE_PUBLIC_KEY" || fail "A private key was supplied. Provide only the vendor public key."
[[ -r /etc/os-release ]] || fail "Cannot identify Linux distribution."
# shellcheck disable=SC1091
. /etc/os-release
case "${ID:-}" in debian|ubuntu) DISTRO_ID="$ID" ;; *) fail "Only Debian and Ubuntu are supported; detected ${ID:-unknown}." ;; esac
ARCH="$(dpkg --print-architecture 2>/dev/null || true)"
[[ "$ARCH" == amd64 ]] || fail "This initial deployment-test release supports Debian/Ubuntu amd64 only; detected ${ARCH:-unknown}."
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y ca-certificates curl gnupg python3 openssl

if ! command -v docker >/dev/null 2>&1 || ! docker compose version >/dev/null 2>&1; then
  conflicts="$(dpkg-query -W -f='${db:Status-Abbrev} ${binary:Package}\n' docker.io docker-compose docker-compose-v2 docker-doc podman-docker containerd runc 2>/dev/null | awk '$1 ~ /^ii/ {print $2}')"
  [[ -z "$conflicts" ]] || fail "Conflicting container packages are installed ($conflicts). Review them deliberately; this installer will not remove packages or data."
  install -m 0755 -d /etc/apt/keyrings
  key_tmp="$(mktemp /tmp/bifrost-docker-key.XXXXXX)"
  curl --fail --silent --show-error --location "https://download.docker.com/linux/$DISTRO_ID/gpg" -o "$key_tmp"
  fingerprint="$(gpg --show-keys --with-colons "$key_tmp" | awk -F: '$1 == "fpr" {print $10; exit}')"
  expected='060A61C51B558A7F742B77AAC52FEB6B621E9F35'
  [[ "$fingerprint" == "$expected" ]] || { rm -f -- "$key_tmp"; fail "Docker APT signing-key fingerprint verification failed."; }
  docker_key=/etc/apt/keyrings/bifrost-docker.asc
  if [[ -e "$docker_key" ]]; then
    cmp -s "$key_tmp" "$docker_key" || { rm -f -- "$key_tmp"; fail "Existing Docker APT key differs; preserving it for review."; }
    rm -f -- "$key_tmp"
  else
    install -m 0644 "$key_tmp" "$docker_key"
    rm -f -- "$key_tmp"
  fi
  codename="${UBUNTU_CODENAME:-${VERSION_CODENAME:-}}"
  [[ -n "$codename" ]] || fail "Distribution codename is unavailable; Docker repository was not configured."
  docker_repo=/etc/apt/sources.list.d/bifrost-docker.sources
  repo_content="Types: deb\nURIs: https://download.docker.com/linux/$DISTRO_ID\nSuites: $codename\nComponents: stable\nArchitectures: $ARCH\nSigned-By: $docker_key"
  if [[ -e "$docker_repo" ]]; then
    [[ "$(cat "$docker_repo")" == "$(printf '%b' "$repo_content")" ]] || fail "Existing Bifrost Docker repository file differs; preserving it for manual review."
  else
    printf '%b\n' "$repo_content" > "$docker_repo"
    chmod 0644 "$docker_repo"
  fi
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  systemctl enable --now docker
fi
docker compose version >/dev/null 2>&1 || fail "Docker Engine and Compose v2 are required."
[[ ! -e "$INSTALL_DIR" ]] || fail "Install directory already exists: $INSTALL_DIR. Existing installations are preserved; use the documented upgrade procedure."

read -r -p 'Public Controller HTTPS URL (TLS reverse proxy required): ' PUBLIC_URL </dev/tty
[[ "$PUBLIC_URL" =~ ^https://[A-Za-z0-9.-]+(:[0-9]{1,5})?(/[A-Za-z0-9._~/-]*)?$ ]] || fail "Enter a valid HTTPS URL without credentials, query, or fragment."
read -r -p 'Bifrost licensing service HTTPS URL (blank leaves activation unavailable): ' LICENSE_URL </dev/tty
if [[ -n "$LICENSE_URL" ]]; then
  [[ "$LICENSE_URL" =~ ^https://[A-Za-z0-9.-]+(:[0-9]{1,5})?(/[A-Za-z0-9._~/-]*)?$ ]] || fail "Enter a valid HTTPS URL or leave blank."
fi
printf '%s\n' "The public privacy notice must reflect your organization's actual processing and be reviewed before launch."
read -r -p 'Privacy controller / organization name: ' PRIVACY_NAME </dev/tty
read -r -p 'Privacy contact (published email or URL): ' PRIVACY_CONTACT </dev/tty
read -r -p 'Processing jurisdictions (comma-separated): ' PRIVACY_JURISDICTIONS </dev/tty
read -r -p 'Lawful bases (as confirmed by your reviewer): ' PRIVACY_BASES </dev/tty
read -r -p 'Configured data processors (comma-separated): ' PRIVACY_PROCESSORS </dev/tty
read -r -p 'Data region / hosting location: ' PRIVACY_REGION </dev/tty
read -r -p 'Privacy notice review date (YYYY-MM-DD): ' PRIVACY_REVIEW_DATE </dev/tty
read -r -p 'Internal privacy review reference: ' PRIVACY_REVIEW_REF </dev/tty
PRIVACY_VALUE_RE='^[A-Za-z0-9 .,:/@()_+-]+$'
for value in "$PRIVACY_NAME" "$PRIVACY_CONTACT" "$PRIVACY_JURISDICTIONS" "$PRIVACY_BASES" "$PRIVACY_PROCESSORS" "$PRIVACY_REGION" "$PRIVACY_REVIEW_REF"; do
  [[ -n "$value" && "$value" =~ $PRIVACY_VALUE_RE ]] || fail "Privacy setup fields must be non-empty and contain only letters, numbers, spaces, and . , : / @ ( ) _ + - characters."
done
[[ "$PRIVACY_REVIEW_DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] || fail "Enter the reviewed date as YYYY-MM-DD."

TMP="$(mktemp -d /tmp/bifrost-install.XXXXXX)"
trap 'rm -rf -- "$TMP"' EXIT
BASE="https://github.com/troainc/Bifrost-Server-Manager-Public/releases/download/$VERSION"
BUNDLE="bifrost-controller-linux-$VERSION.tar.gz"
curl --fail --silent --show-error --location "$BASE/$BUNDLE" -o "$TMP/$BUNDLE" || fail "Could not download the fixed-version Controller bundle. Confirm that this public release exists."
curl --fail --silent --show-error --location "$BASE/SHA256SUMS" -o "$TMP/SHA256SUMS" || fail "Could not download the release checksum file."
(cd "$TMP" && grep -F "  $BUNDLE" SHA256SUMS | sha256sum --check --status) || fail "Bundle checksum validation failed."

python3 - "$TMP/$BUNDLE" "$TMP/unpacked" <<'PY'
import pathlib, sys, tarfile
archive, destination = sys.argv[1:]
root = pathlib.Path(destination).resolve()
root.mkdir(mode=0o700)
with tarfile.open(archive, "r:gz") as bundle:
    members = bundle.getmembers()
    if not members or len(members) > 1000:
        raise SystemExit("Invalid bundle entry count.")
    for member in members:
        path = pathlib.PurePosixPath(member.name)
        if path.is_absolute() or ".." in path.parts or not (member.isfile() or member.isdir()):
            raise SystemExit("Bundle contains an unsafe path or non-regular entry.")
    bundle.extractall(root)
PY

NETWORK_JSON="$(docker network inspect $(docker network ls -q))" || fail "Could not inspect Docker network ranges; no files were installed."
mapfile -t NETWORK_VALUES < <(python3 -c 'import ipaddress,json,sys
used=[]
for network in json.load(sys.stdin):
  for item in network.get("IPAM",{}).get("Config",[]):
    try: used.append(ipaddress.ip_network(item["Subnet"], strict=False))
    except (KeyError,ValueError): pass
for n in range(256):
  subnet=ipaddress.ip_network(f"10.240.{n}.0/24")
  if not any(subnet.overlaps(existing) for existing in used):
    print(subnet); print(f"10.240.{n}.10"); print(f"127.0.0.1,::1,10.240.{n}.10"); break
else: raise SystemExit("No unused 10.240.x.0/24 Docker range is available")' <<< "$NETWORK_JSON") || fail "No non-overlapping Docker subnet is available. No existing networks were changed."
[[ ${#NETWORK_VALUES[@]} -eq 3 ]] || fail "Could not select a non-overlapping Docker network."

install -d -m 0750 "$INSTALL_DIR"
cp -a "$TMP/unpacked/." "$INSTALL_DIR/"
install -d -m 0700 "$INSTALL_DIR/secrets"
install -m 0600 "$LICENSE_PUBLIC_KEY" "$INSTALL_DIR/secrets/license_signing_public.pem"
install -m 0644 "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
python3 - "$INSTALL_DIR" "$VERSION" "$PUBLIC_URL" "$LICENSE_URL" "${NETWORK_VALUES[0]}" "${NETWORK_VALUES[1]}" "${NETWORK_VALUES[2]}" "$PRIVACY_NAME" "$PRIVACY_CONTACT" "$PRIVACY_JURISDICTIONS" "$PRIVACY_BASES" "$PRIVACY_PROCESSORS" "$PRIVACY_REGION" "$PRIVACY_REVIEW_DATE" "$PRIVACY_REVIEW_REF" <<'PY'
from pathlib import Path
import sys
root = Path(sys.argv[1])
version, public_url, license_url, subnet, web_ip, trusted, privacy_name, privacy_contact, jurisdictions, bases, processors, region, review_date, review_ref = sys.argv[2:]
env = root / ".env"
values = {"BIFROST_VERSION": version, "BIFROST_PUBLIC_URL": public_url, "BIFROST_LICENSE_URL": license_url,
          "BIFROST_PRIVATE_SUBNET": subnet, "BIFROST_WEB_NETWORK_IP": web_ip, "BIFROST_TRUSTED_PROXIES": trusted,
          "BIFROST_PRIVACY_CONTROLLER_NAME": privacy_name, "BIFROST_PRIVACY_CONTACT": privacy_contact,
          "BIFROST_PRIVACY_JURISDICTIONS": jurisdictions, "BIFROST_PRIVACY_LAWFUL_BASES": bases,
          "BIFROST_PRIVACY_PROCESSORS": processors, "BIFROST_PRIVACY_DATA_REGION": region,
          "BIFROST_PRIVACY_REVIEW_APPROVED_AT": review_date, "BIFROST_PRIVACY_REVIEW_REFERENCE": review_ref}
lines = env.read_text().splitlines()
for key, value in values.items():
    lines = [line for line in lines if not line.startswith(key + "=")]
    lines.append(f"{key}={value}")
env.write_text("\n".join(lines) + "\n")
PY
chmod 0600 "$INSTALL_DIR/.env"

for secret in postgres_owner_password bifrost_app_password rate_limit_pepper mfa_encryption_key; do
  openssl rand -base64 48 | tr -d '\n' > "$INSTALL_DIR/secrets/$secret.txt"
  chmod 0600 "$INSTALL_DIR/secrets/$secret.txt"
done
openssl genpkey -algorithm ED25519 -out "$INSTALL_DIR/secrets/agent-job-signing-private.pem"
openssl pkey -in "$INSTALL_DIR/secrets/agent-job-signing-private.pem" -pubout -out "$INSTALL_DIR/secrets/agent-job-signing-public.pem"
chmod 0600 "$INSTALL_DIR/secrets/agent-job-signing-private.pem" "$INSTALL_DIR/secrets/agent-job-signing-public.pem"

cd "$INSTALL_DIR"
docker compose config --quiet
read -r -p 'Start the Bifrost Controller now? [y/N] ' answer </dev/tty
if [[ "$answer" =~ ^[Yy]$ ]]; then
  docker compose pull
  docker compose up -d
  docker compose ps --all
  log "Controller containers started. Keep the generated secrets safe and configure the separate TLS proxy before public access."
  log "First admin setup is completed in the browser. This test deployment does not enroll a game host."
else
  log "Bundle and protected secrets are ready at $INSTALL_DIR; stack not started. Start later with: cd $INSTALL_DIR && sudo docker compose up -d"
fi
