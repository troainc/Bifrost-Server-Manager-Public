#!/usr/bin/env bash
set -Eeuo pipefail

DEFAULT_VERSION="SET_BY_PUBLIC_RELEASE_WORKFLOW"
VERSION="${BIFROST_VERSION:-$DEFAULT_VERSION}"
INSTALL_DIR="${BIFROST_INSTALL_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/bifrost}"
LICENSE_PUBLIC_KEY=""
PUBLIC_URL=""
LICENSE_URL=""

fail() { printf 'Bifrost installer: %s\n' "$*" >&2; exit 1; }
log() { printf 'Bifrost installer: %s\n' "$*"; }
usage() {
  cat <<'EOF'
Usage: bash install.sh [--version vX.Y.Z] [--license-public-key FILE]
       [--install-dir DIR]

Installs the source-free Linux Controller bundle from the matching public
GitHub release as the current non-root user. Requires Debian/Ubuntu amd64,
rootless Docker Engine with Compose v2, a separate TLS reverse proxy, and the
vendor-provided public license verification key. This installer never uses sudo.
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

[[ "${EUID:-$(id -u)}" -ne 0 ]] || fail "Do not run as root or with sudo. Sign in as the regular account that will own and run Bifrost, then run bash install.sh."
[[ -n "${HOME:-}" && "$HOME" != "/root" ]] || fail "A regular user home directory is required."
[[ "$INSTALL_DIR" == /* ]] || fail "Install directory must be an absolute path."
[[ -r /dev/tty ]] || fail "Interactive setup needs a terminal. Run this installer from a terminal."
for tool in curl python3 openssl awk grep sha256sum; do
  command -v "$tool" >/dev/null 2>&1 || fail "A required command is missing. Have curl, python3, openssl, awk, grep, and sha256sum provisioned before installation; this installer will not use root access to install packages."
done
command -v docker >/dev/null 2>&1 || fail "Rootless Docker Engine is required for this account. Have it provisioned before installation; this installer will not install system packages or use a root-owned Docker daemon."
docker compose version >/dev/null 2>&1 || fail "Docker Compose v2 is required for this account."
docker info >/dev/null 2>&1 || fail "Docker is not available to this user. Configure and start rootless Docker for this account."
security_options="$(docker info --format '{{json .SecurityOptions}}' 2>/dev/null || true)"
grep -qi 'rootless' <<< "$security_options" || fail "This account is connected to a rootful Docker daemon. Configure rootless Docker for this account; Bifrost requires a rootless daemon."
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
BUNDLE="bifrost-controller-linux-amd64-$VERSION.tar.gz"
curl --fail --silent --show-error --location --max-filesize 104857600 "$BASE/$BUNDLE" -o "$TMP/$BUNDLE" || fail "Could not download the fixed-version Controller bundle (maximum size 100 MiB). Confirm that this public release exists."
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
    seen = set()
    total = 0
    for member in members:
        path = pathlib.PurePosixPath(member.name)
        normalized = str(path).casefold()
        total += member.size
        if (path.is_absolute() or ".." in path.parts or normalized in seen
                or not (member.isfile() or member.isdir()) or member.size > 16 * 1024 * 1024
                or total > 64 * 1024 * 1024):
            raise SystemExit("Bundle contains an unsafe path or non-regular entry.")
        seen.add(normalized)
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

mkdir -m 0700 -p "$(dirname "$INSTALL_DIR")"
mkdir -m 0700 "$INSTALL_DIR"
chmod 0700 "$INSTALL_DIR"
cp -a "$TMP/unpacked/." "$INSTALL_DIR/"
mkdir -m 0700 "$INSTALL_DIR/secrets"
cp "$LICENSE_PUBLIC_KEY" "$INSTALL_DIR/secrets/license_signing_public.pem"
chmod 0600 "$INSTALL_DIR/secrets/license_signing_public.pem"
cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
chmod 0600 "$INSTALL_DIR/.env"
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
  log "Bundle and protected secrets are ready at $INSTALL_DIR; stack not started. Start later with: cd $INSTALL_DIR && docker compose up -d"
fi
