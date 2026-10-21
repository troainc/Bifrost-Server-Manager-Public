# BEGIN SIGNED_RELEASE_BOOTSTRAP
# Local candidate identity. Private signing material is never part of this repository.
readonly RELEASE_SIGNER_SPKI_SHA256=1dba79e7a3d2608b42a5324089d4db548567999210ffbf3dd96ce5cb63a92e6a
verify_signed_release(){
  local target="$1" local_name="$2" asset_name="${3:-$2}" metadata_base
  metadata_base="https://github.com/troainc/Bifrost-Server-Manager-Public/releases/download/$VERSION"
  python3 - "$metadata_base" "$target" <<'SIGNED_RELEASE_DOWNLOAD_PY'
import os,pathlib,sys,urllib.request,urllib.parse
base,target=sys.argv[1],pathlib.Path(sys.argv[2])
def approved(url):
    value=urllib.parse.urlsplit(url)
    if value.scheme!='https' or value.hostname not in ('github.com','release-assets.githubusercontent.com','objects.githubusercontent.com') or value.username or value.password or value.port not in (None,443):raise ValueError('Unapproved metadata origin.')
class Redirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,request,response,code,message,headers,url):
        approved(url);return super().redirect_request(request,response,code,message,headers,url)
opener=urllib.request.build_opener(Redirect())
for name in ('release-signing-public.pem','release-manifest.json','release-manifest.sig','release-manifest.py'):
    url=base+'/'+name;approved(url)
    with opener.open(url,timeout=30) as response:
        data=response.read(1024*1024+1)
    if len(data)>1024*1024:raise ValueError('Oversized release metadata.')
    descriptor=os.open(target/name,os.O_WRONLY|os.O_CREAT|os.O_TRUNC|os.O_NOFOLLOW,0o600)
    with os.fdopen(descriptor,'wb')as output:output.write(data)
SIGNED_RELEASE_DOWNLOAD_PY
  [[ $? -eq 0 ]] || fail 'Signed release metadata download failed.'
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
# END SIGNED_RELEASE_BOOTSTRAP
