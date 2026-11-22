#!/usr/bin/env python3
"""Write canonical LF-only checksums in an unsigned local release staging directory."""
import hashlib,pathlib,re,stat,sys

def write_checksums(directory):
 root=pathlib.Path(directory).absolute()
 if root.resolve()!=root or not root.is_dir():raise ValueError('Use a physical staging directory.')
 if any((root/name).exists()for name in ['release-manifest.json','release-manifest.sig']):raise ValueError('Do not rewrite a signed release inventory.')
 lines=[]
 for p in sorted(root.iterdir()):
  info=p.lstat()
  if p.name=='SHA256SUMS':
   if not stat.S_ISREG(info.st_mode)or info.st_nlink!=1:raise ValueError('Unsafe existing checksum inventory.')
   continue
  if stat.S_ISDIR(info.st_mode):continue
  if not stat.S_ISREG(info.st_mode)or info.st_nlink!=1 or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,159}',p.name)or'..'in p.name:raise ValueError('Unsafe public release asset.')
  digest=hashlib.sha256()
  with p.open('rb')as source:
   for data in iter(lambda:source.read(1048576),b''):digest.update(data)
  lines.append(digest.hexdigest()+'  '+p.name+'\n')
 if not lines:raise ValueError('No release assets.')
 (root/'SHA256SUMS').write_bytes(''.join(lines).encode('ascii'))
 return len(lines)

if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Usage: write-release-checksums.py UNSIGNED-STAGING-DIRECTORY')
 print('Wrote canonical LF checksums for '+str(write_checksums(sys.argv[1]))+' public assets.')
