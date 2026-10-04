#!/usr/bin/env bash
set -euo pipefail
umask 077
version=${1:?version}; key=${2:?public verification key}; output=${3:?new output directory}
[[ "$version" =~ ^v[0-9]+\.[0-9]+\.[0-9]+-installtest\.[0-9]+$ ]] || exit 1
[[ ! -e "$output" && -f "$key" && ! -L "$key" ]] || exit 1
grep -qx "VERSION=$version" install.sh
grep -qx "VERSION=$version" update.sh
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
