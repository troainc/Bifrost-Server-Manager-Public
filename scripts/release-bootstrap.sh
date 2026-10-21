# BEGIN SIGNED_RELEASE_BOOTSTRAP
# Local candidate identity. Private signing material is never part of this repository.
readonly RELEASE_SIGNER_SPKI_SHA256=1dba79e7a3d2608b42a5324089d4db548567999210ffbf3dd96ce5cb63a92e6a
fetch_release_asset(){
  local asset="$1" destination="$2"
  python3 - "$VERSION" "$asset" "$destination" "${BIFROST_RELEASE_DIRECTORY:-}" <<'RELEASE_ASSET_PY'
import os,pathlib,re,stat,sys,urllib.request,urllib.parse
version,name,destination,offline=sys.argv[1:]
if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,159}',name)or'..'in name:raise SystemExit('Unsafe release asset name.')
limit=1024*1024 if name in ('release-signing-public.pem','release-manifest.json','release-manifest.sig','release-manifest.py','SHA256SUMS')else 4*1024**3

def approved(url):
    value=urllib.parse.urlsplit(url)
    if value.scheme!='https'or value.hostname not in ('github.com','release-assets.githubusercontent.com','objects.githubusercontent.com')or value.username or value.password or value.port not in (None,443):raise ValueError('Unapproved release origin.')
class Redirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,request,response,code,message,headers,url):
        approved(url);return super().redirect_request(request,response,code,message,headers,url)
source=None
try:
    if offline:
        root=pathlib.Path(offline)
        if not root.is_absolute()or root.resolve()!=root or not root.is_dir():raise ValueError('Local release directory must be absolute, physical and readable.')
        # Traverse from a held directory descriptor; no followed source links.
        directory=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW,dir_fd=directory)
        finally:os.close(directory)
        info=os.fstat(fd)
        if not stat.S_ISREG(info.st_mode)or info.st_nlink!=1 or not 0<info.st_size<=limit:
            os.close(fd);raise ValueError('Local release asset must be a bounded unlinked regular file.')
        source=os.fdopen(fd,'rb')
    else:
        url=f'https://github.com/troainc/Bifrost-Server-Manager-Public/releases/download/{version}/{name}';approved(url)
        source=urllib.request.build_opener(Redirect()).open(url,timeout=30)
    output=os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(output,'wb')as target:
        total=0
        while True:
            block=source.read(min(1024*1024,limit-total+1))
            if not block:break
            total+=len(block)
            if total>limit:raise ValueError('Release asset exceeds its bound.')
            target.write(block)
        if not total:raise ValueError('Release asset is empty.')
except (OSError,ValueError)as error:
    raise SystemExit('Release asset unavailable or unsafe; no alternate source was used: '+str(error))
finally:
    if source is not None:source.close()
RELEASE_ASSET_PY
}
verify_signed_release(){
  local target="$1" local_name="$2" asset_name="${3:-$2}" name
  for name in release-signing-public.pem release-manifest.json release-manifest.sig release-manifest.py; do
    fetch_release_asset "$name" "$target/$name" || fail 'Signed release metadata is unavailable.'
  done
  local actual_signer
  actual_signer=$(openssl pkey -pubin -in "$target/release-signing-public.pem" -outform DER | openssl dgst -sha256 -r | cut -d ' ' -f 1)
  [[ "$actual_signer" == "$RELEASE_SIGNER_SPKI_SHA256" ]] || fail 'Release signing identity does not match the pinned publisher.'
  openssl pkeyutl -verify -pubin -inkey "$target/release-signing-public.pem" -rawin -in "$target/release-manifest.json" -sigfile "$target/release-manifest.sig" >/dev/null 2>&1 || fail 'Release statement signature is invalid.'
  # Authenticate the verifier itself before executing any downloaded Python.
  python3 - "$target" <<'SIGNED_VERIFIER_PY'
import hashlib,json,pathlib,sys
root=pathlib.Path(sys.argv[1]);manifest=json.loads((root/'release-manifest.json').read_text())
records=[item for item in manifest['artifacts']if item['name']=='release-manifest.py']
if len(records)!=1:raise SystemExit('Signed verifier record missing or duplicated.')
path=root/'release-manifest.py';data=path.read_bytes()
if len(data)!=records[0]['size']or hashlib.sha256(data).hexdigest()!=records[0]['sha256']:raise SystemExit('Signed verifier bytes do not match.')
SIGNED_VERIFIER_PY
  [[ $? -eq 0 ]] || fail 'Release verifier integrity failed.'
  python3 "$target/release-manifest.py" --manifest "$target/release-manifest.json" --signature "$target/release-manifest.sig" --public-key "$target/release-signing-public.pem" --expected-signer "$RELEASE_SIGNER_SPKI_SHA256" --version "$VERSION" --asset "$asset_name=$target/$local_name" || fail 'Signed release verification failed.'
}
verify_local_release(){
  [[ $# -eq 1 && -n "$1" ]] || fail 'Pass one absolute local release directory.'
  command -v python3 >/dev/null && command -v openssl >/dev/null || fail 'Verification requires Python 3 and OpenSSL.'
  local stage status=0
  stage=$(mktemp -d)
  (
    export BIFROST_RELEASE_DIRECTORY="$1"
    fetch_release_asset install.sh "$stage/install.sh" || exit 1
    verify_signed_release "$stage" install.sh
    python3 -B - "$stage" "$BIFROST_RELEASE_DIRECTORY" "$RELEASE_SIGNER_SPKI_SHA256" "$VERSION" <<'VERIFY_LOCAL_RELEASE_PY'
import importlib.util,json,pathlib,sys
stage,assets=map(pathlib.Path,sys.argv[1:3])
spec=importlib.util.spec_from_file_location('verified_release',stage/'release-manifest.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
statement=json.loads((stage/'release-manifest.json').read_text())
result=module.verify(stage/'release-manifest.json',stage/'release-manifest.sig',stage/'release-signing-public.pem',sys.argv[3],sys.argv[4],{item['name']:assets/item['name']for item in statement['artifacts']})
print('PASS all signed local artifact hashes; private source '+result['privateSourceSha']+'; public source '+result['publicSourceSha'])
print('Verification only: no account, service, database, installation or publication was changed.')
VERIFY_LOCAL_RELEASE_PY
  ) || status=$?
  # Only fixed-name public metadata copied into this function's own mktemp tree.
  rm -f -- "$stage/install.sh" "$stage/release-signing-public.pem" "$stage/release-manifest.json" "$stage/release-manifest.sig" "$stage/release-manifest.py"
  rmdir -- "$stage"
  return "$status"
}
# END SIGNED_RELEASE_BOOTSTRAP
