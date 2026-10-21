#!/usr/bin/env python3
"""Keep standalone installers' authenticated bootstrap byte-identical to its source."""
import pathlib,sys,re
root=pathlib.Path(__file__).resolve().parents[1]
template=(root/'scripts/release-bootstrap.sh').read_text(encoding='utf8').rstrip()+'\n'
for name in ('install.sh','update.sh'):
    path=root/name;source=path.read_text(encoding='utf8')
    if '# BEGIN SIGNED_RELEASE_BOOTSTRAP' in source:
        a=source.index('# BEGIN SIGNED_RELEASE_BOOTSTRAP');b=source.index('# END SIGNED_RELEASE_BOOTSTRAP',a)+len('# END SIGNED_RELEASE_BOOTSTRAP')
        actual=source[a:b].rstrip()+'\n'
        if actual==template:continue
        if '--check'in sys.argv:raise SystemExit(name+': signed bootstrap drift')
        source=source[:a]+template.rstrip()+source[b:]
    else:
        if '--check'in sys.argv:raise SystemExit(name+': signed bootstrap missing')
        source,count=re.subn(r'(?m)^VERSION=v[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?\n',lambda match:match.group(0)+template,source,count=1)
        if count!=1:raise SystemExit(name+': exact version declaration missing')
    path.write_text(source,encoding='utf8',newline='\n')
