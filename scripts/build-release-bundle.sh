#!/usr/bin/env bash
set -euo pipefail
umask 077
version=${1:?version}; key=${2:?public verification key}; output=${3:?new output directory}
catalog=${4:-}; publisher=${5:-}
[[ $# -eq 3 || $# -eq 5 ]] || { printf 'Pass both reviewed catalog directory and pinned publisher ID, or neither.\n' >&2; exit 1; }
[[ "$version" =~ ^v[0-9]+\.[0-9]+\.[0-9]+-installtest\.[0-9]+$ ]] || exit 1
[[ ! -e "$output" && -f "$key" && ! -L "$key" ]] || exit 1
grep -qx "VERSION=$version" install.sh
grep -qx "VERSION=$version" update.sh
grep -qx "BIFROST_VERSION=$version" .env.example
grep -qx "BIFROST_CONTROL_PLANE_IMAGE=bifrost/control-plane:$version" .env.example
grep -qx "BIFROST_WEB_IMAGE=bifrost/web:$version" .env.example
[[ $(wc -c < "$key") -le 4096 ]] || exit 1
grep -q '^-----BEGIN PUBLIC KEY-----$' "$key"
! grep -q 'PRIVATE KEY' "$key"
openssl pkey -pubin -in "$key" -outform DER > "$key.der"
python3 - "$key.der" <<'PY'
import pathlib,sys
data=pathlib.Path(sys.argv[1]).read_bytes()
assert len(data)==91 and data.startswith(bytes.fromhex('3059301306072a8648ce3d020106082a8648ce3d03010703420004')), 'Expected issuer P-256 public key'
PY
rm -f "$key.der"
mkdir -p "$output/package"
cp -a deployment/. "$output/package/"
# This is new staging with public templates only. Archive/checkouts created under
# umask 077 can otherwise leave PostgreSQL's non-root init hook unreadable.
for public_config in "$output/package/config/"*; do
  [[ -f "$public_config" && ! -L "$public_config" ]] || exit 1
  chmod 0644 "$public_config"
done
if [[ -n "$catalog" ]]; then
  # These are empty templates in this new staging tree, never an installed policy.
  python3 - "$output/package/config" <<'PY'
import json,pathlib,sys
root=pathlib.Path(sys.argv[1])
for name,empty in [('provisioning-catalog.json',[]),('provisioning-trust.json',{})]:
    p=root/name
    assert p.is_file() and not p.is_symlink() and json.loads(p.read_text())==empty, 'Refusing to replace a nonempty template'
for name in ['provisioning-catalog.json','provisioning-trust.json']:(root/name).unlink()
PY
  python3 scripts/install-reviewed-catalog.py "$catalog" "$publisher" "$output/package/config"
fi
cp .env.example README.md "$output/package/"
cp "$key" "$output/package/config/license-signing-public.pem"
# Public verification material must be readable by the unprivileged container.
chmod 0644 "$output/package/config/license-signing-public.pem"
docker image inspect "bifrost/control-plane:$version" "bifrost/web:$version" "bifrost/postgres:$version" > "$output/images.json"
docker save "bifrost/control-plane:$version" "bifrost/web:$version" "bifrost/postgres:$version" > "$output/package/customer-images.tar"
# A portable lock records the archive config digest, not the engine-specific Id.
python3 scripts/verify-image-archive.py "$output/package/customer-images.tar" "$output/package/IMAGE-LOCK.json" --write-lock \
  "bifrost/control-plane:$version" "bifrost/web:$version" "bifrost/postgres:$version"

tar -czf "$output/bifrost-linux-amd64-$version.tar.gz" -C "$output/package" .
cp install.sh update.sh "$output/"
(cd "$output" && sha256sum "bifrost-linux-amd64-$version.tar.gz" install.sh update.sh > SHA256SUMS)
printf 'Created compiled customer release %s; host/game acceptance remains pending.\n' "$version"
