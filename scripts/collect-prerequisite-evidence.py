#!/usr/bin/env python3
"""Read-only local prerequisite inventory. Never installs, restarts or approves tools."""
import hashlib,json,pathlib,shutil,subprocess

def probe(argv):
    try:
        result=subprocess.run(argv,capture_output=True,text=True,timeout=12,check=False)
        return {'available':result.returncode==0,'value':result.stdout.strip()[:4096]if result.returncode==0 else None}
    except (OSError,subprocess.SubprocessError):return {'available':False,'value':None}

def collect():
    executable=shutil.which('docker');binary=None
    if executable:
        try:
            path=pathlib.Path(executable).resolve(strict=True);digest=hashlib.sha256()
            with path.open('rb')as source:
                for block in iter(lambda:source.read(1024*1024),b''):digest.update(block)
            binary={'path':str(path),'sha256':digest.hexdigest()}
        except OSError:pass
    return {'schemaVersion':1,'readOnly':True,'securityApproval':False,'vulnerabilityReviewRequired':True,'dockerBinary':binary,'dockerClient':probe(['docker','--version']),'dockerServer':probe(['docker','version','--format','{{.Server.Version}}']),'compose':probe(['docker','compose','version','--short']),'securityOptions':probe(['docker','info','--format','{{json .SecurityOptions}}']),'note':'Versions and hashes are evidence, not a vulnerability clearance. Review the exact approved prerequisite build independently; no credentials, full environment, containers or fleet inventory are collected.'}

if __name__=='__main__':print(json.dumps(collect(),indent=2))
