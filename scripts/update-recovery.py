#!/usr/bin/env python3
"""Private, authenticated update checkpoints; recovery creates a NEW database.

Never deletes a database or a volume. Run only as the existing non-root service
account. Encryption keys stay outside checkpoints and must be escrowed separately.
"""
import argparse
import contextlib
import fcntl
import hashlib
import hmac
import json
import os
import pathlib
import re
import secrets
import shutil
import stat
import subprocess
import tarfile
import tempfile
import time

MAGIC = b'BIFREC01'
MANAGED = ('control-plane', 'web', 'https')

@contextlib.contextmanager
def installation_lock(root):
    directory(root)
    path = root/'update.lock'
    inherited = os.environ.get('BIFROST_UPDATE_LOCK_FD')
    fd = int(inherited) if inherited and inherited.isdecimal() else os.open(path, os.O_RDWR|os.O_CREAT|os.O_NOFOLLOW, 0o600)
    try:
        regular(path, True)
        actual, expected = os.fstat(fd), path.stat()
        if (actual.st_dev, actual.st_ino) != (expected.st_dev, expected.st_ino): raise ValueError('Update lock identity changed.')
        fcntl.flock(fd, fcntl.LOCK_EX|fcntl.LOCK_NB)
        yield
    finally:
        if not inherited: os.close(fd)

def current_database(root):
    values=dict(line.split('=',1)for line in regular(root/'.env',True).read_text().splitlines()if'='in line and not line.startswith('#'))
    if any(value not in ('','compose.yaml')for value in (values.get('COMPOSE_FILE',''),os.environ.get('COMPOSE_FILE',''))):raise ValueError('Custom Compose overlays require a separately reviewed recovery procedure.')
    # Resolved Compose is consumed privately; it can contain secret configuration.
    config = json.loads(command(root, ['config','--format','json']))
    services = config.get('services', {})
    name = services.get('control-plane', {}).get('environment', {}).get('DB_NAME')
    migration = services.get('migrate', {}).get('environment', {}).get('DB_NAME')
    if not isinstance(name,str) or not re.fullmatch(r'bifrost(?:_recovery_[a-f0-9]{16})?',name) or name != migration:
        raise ValueError('Controller and migration database identities must match the supported local contract.')
    return name

def select_database(configuration, database):
    pattern = r'(?m)^(\s*DB_NAME:\s*)(?:bifrost(?:_recovery_[a-f0-9]{16})?|\$\{BIFROST_DATABASE_NAME:-bifrost\})\s*$'
    updated, count = re.subn(pattern, lambda match: match.group(1)+database, configuration)
    if count != 2: raise ValueError('Unknown saved Compose database contract; retained databases preserved.')
    return updated

def regular(path, private=False):
    path = pathlib.Path(path)
    if path.resolve() != path.absolute(): raise ValueError('Recovery paths cannot traverse links.')
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_uid != os.getuid():
        raise ValueError('Recovery files must be regular, unlinked and service-owned.')
    if info.st_mode & (0o077 if private else 0o022): raise ValueError('Recovery file permissions are unsafe.')
    return path

@contextlib.contextmanager
def open_regular(path, private=False):
    regular(path,private)
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        info=os.fstat(fd);current=pathlib.Path(path).lstat()
        if not stat.S_ISREG(info.st_mode)or info.st_nlink!=1 or info.st_uid!=os.getuid()or info.st_mode&(0o077 if private else 0o022)or(info.st_dev,info.st_ino)!=(current.st_dev,current.st_ino):raise ValueError('Protected file identity changed.')
        with os.fdopen(fd,'rb',closefd=False)as handle:yield handle
    finally:os.close(fd)

def directory(path):
    path = pathlib.Path(path)
    if path.resolve() != path.absolute(): raise ValueError('Recovery directories cannot traverse links.')
    info = path.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError('Recovery directories must be private and service-owned.')
    return path

def atomic_json(path, value):
    temp = path.with_name(path.name + '.' + secrets.token_hex(8) + '.next')
    with temp.open('x', encoding='utf8') as handle:
        os.chmod(temp, 0o600); json.dump(value, handle, sort_keys=True); handle.flush(); os.fsync(handle.fileno())
    os.replace(temp, path)
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)

def command(root, args, *, source=None, destination=None):
    result = subprocess.run(['docker', 'compose', '--project-directory', str(root), *args], cwd=root,
        stdin=source, stdout=destination if destination else subprocess.PIPE, stderr=subprocess.PIPE, timeout=1800, check=False)
    if result.returncode: raise RuntimeError('Recovery command failed; services stay quiesced and retained data is preserved. Inspect local Docker diagnostics.')
    return result.stdout

def recovery_key(root, create=False):
    folder = directory(root / 'secrets')
    key = folder / 'update_recovery.key'
    if not key.exists():
        if not create: raise ValueError('Recovery key is missing; restore its exact escrowed value before recovery.')
        fd = os.open(key, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        try: os.write(fd, secrets.token_bytes(64)); os.fsync(fd)
        finally: os.close(fd)
    regular(key, True)
    with open_regular(key,True)as handle:value=handle.read(65)
    if len(value) != 64: raise ValueError('Invalid recovery encryption key.')
    return value

def crypt(source, destination, key, decrypt=False):
    # AES-256-CBC with a separate HMAC-SHA256 encrypt-then-MAC envelope.
    # Passphrase travels through a file descriptor, never argv, environment or logs.
    read_fd, write_fd = os.pipe()
    source_fd=destination_fd=None
    try:
        source_fd=os.open(source,os.O_RDONLY|os.O_NOFOLLOW)
        info=os.fstat(source_fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_uid!=os.getuid() or info.st_mode&0o022:raise ValueError('Unsafe encryption input descriptor.')
        destination_fd=os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        os.write(write_fd, key[:32].hex().encode() + b'\n'); os.close(write_fd); write_fd = -1
        args = ['openssl', 'enc', '-aes-256-cbc', '-pbkdf2', '-iter', '200000', '-md', 'sha256', '-pass', f'fd:{read_fd}']
        if decrypt: args.insert(2, '-d')
        subprocess.run(args, pass_fds=(read_fd,), stdin=source_fd,stdout=destination_fd,check=True, stderr=subprocess.DEVNULL, timeout=1800)
        os.fsync(destination_fd)
    finally:
        os.close(read_fd)
        if write_fd >= 0: os.close(write_fd)
        if source_fd is not None:os.close(source_fd)
        if destination_fd is not None:os.close(destination_fd)

def seal(source, destination, key):
    encrypted = destination.with_suffix('.cipher.next')
    try:
        crypt(source, encrypted, key)
        mac = hmac.new(key[32:], MAGIC, hashlib.sha256)
        with destination.open('xb') as output, open_regular(encrypted,True) as body:
            os.chmod(destination, 0o600); output.write(MAGIC)
            for chunk in iter(lambda: body.read(1024*1024), b''): mac.update(chunk); output.write(chunk)
            output.write(mac.digest()); output.flush(); os.fsync(output.fileno())
    finally:
        encrypted.unlink(missing_ok=True)

def unseal(source, destination, key):
    regular(source, True)
    size = source.stat().st_size
    if size < len(MAGIC) + 64: raise ValueError('Invalid encrypted recovery archive.')
    cipher = destination.with_suffix('.cipher.next')
    try:
        with open_regular(source,True) as body, cipher.open('xb') as out:
            os.chmod(cipher, 0o600)
            if body.read(len(MAGIC)) != MAGIC: raise ValueError('Unsupported recovery archive.')
            mac = hmac.new(key[32:], MAGIC, hashlib.sha256); remaining = size-len(MAGIC)-32
            while remaining:
                chunk = body.read(min(1024*1024, remaining))
                if not chunk: raise ValueError('Truncated recovery archive.')
                remaining -= len(chunk); mac.update(chunk); out.write(chunk)
            if not hmac.compare_digest(mac.digest(), body.read(32)): raise ValueError('Recovery archive authentication failed; nothing was decrypted.')
        crypt(cipher, destination, key, True)
    finally:
        cipher.unlink(missing_ok=True)

def copy_private(source, destination):
    if source.is_dir():
        if source.resolve() != source.absolute() or source.is_symlink(): raise ValueError('Unsafe checkpoint directory.')
        destination.mkdir(mode=0o700)
        for child in source.iterdir():
            if child.name != 'update_recovery.key': copy_private(child, destination / child.name)
    else:
        regular(source)
        with open_regular(source) as old, destination.open('xb') as new:
            os.chmod(destination, 0o600); shutil.copyfileobj(old, new)

def journal(root):
    path = root / 'update-journal.json'
    if not path.exists(): return None
    regular(path, True)
    value = json.loads(path.read_text())
    if value.get('schemaVersion') != 1 or not re.fullmatch(r'[0-9]{8}T[0-9]{6}Z-[a-f0-9]{12}', value.get('id', '')):
        raise ValueError('Invalid update journal; preserve it for review.')
    return value

def begin(root, version):
    directory(root); directory(root/'secrets')
    current = journal(root)
    if current and current['phase'] not in ('complete', 'recovered', 'backup-failed'):
        raise ValueError('An interrupted update requires explicit review/recovery before another update.')
    if not re.fullmatch(r'v[0-9]+\.[0-9]+\.[0-9]+(?:-[A-Za-z0-9.-]+)?', version): raise ValueError('Invalid candidate version.')
    key = recovery_key(root, True)
    database = current_database(root)
    size = int(command(root,['exec','-T','postgres','psql','--username=bifrost_owner','--dbname='+database,'--tuples-only','--no-align','--command','SELECT pg_database_size(current_database())']).strip())
    if size < 1 or size > 100*1024**3 or shutil.disk_usage(root).free < size*3+256*1024**2:
        raise ValueError('Insufficient checkpoint space or database exceeds the supported checkpoint limit.')
    backups = root/'update-backups'; backups.mkdir(mode=0o700, exist_ok=True); directory(backups)
    identity = time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-'+secrets.token_hex(6)
    checkpoint = backups/identity; checkpoint.mkdir(mode=0o700)
    state = {'schemaVersion':1,'id':identity,'candidate':version,'database':database,'phase':'quiescing','createdAt':time.time()}
    atomic_json(root/'update-journal.json', state)
    try:
        command(root, ['stop','--timeout','60',*MANAGED])
        with tempfile.TemporaryDirectory(prefix='checkpoint-',dir=checkpoint) as temp:
            stage=pathlib.Path(temp); os.chmod(stage,0o700)
            for name in ('.env','compose.yaml','config','secrets','IMAGE-LOCK.json'):
                if (root/name).exists(): copy_private(root/name,stage/name)
            command(root,['cp','control-plane:/var/lib/bifrost/keys',str(stage/'managed-keys')])
            require_persistent_managed_keys(root,key_inventory(stage/'managed-keys'))
            dump=stage/'database.dump'
            with dump.open('xb') as out:
                os.chmod(dump,0o600)
                command(root,['exec','-T','postgres','pg_dump','--username=bifrost_owner','--dbname='+database,'--format=custom'],destination=out)
            with dump.open('rb') as data: command(root,['exec','-T','postgres','pg_restore','--list'],source=data)
            archive=stage/'checkpoint.tar'
            with tarfile.open(archive,'w') as tar:
                for item in stage.iterdir():
                    if item != archive: tar.add(item,arcname=item.name,recursive=True)
            # Drop only this private staging copy after its complete tar exists.
            # This avoids retaining dump+tar+cipher+envelope simultaneously.
            discard_staged_inputs(stage,archive)
            if shutil.disk_usage(checkpoint).free<archive.stat().st_size*2+64*1024**2:raise ValueError('Insufficient space for authenticated checkpoint encryption.')
            seal(archive,checkpoint/'checkpoint.enc',key)
            state['archiveSha256']=digest(checkpoint/'checkpoint.enc')
        shutil.copyfile(__file__,checkpoint/'update-recovery.py');os.chmod(checkpoint/'update-recovery.py',0o700)
        state['phase']='backup-ready'; atomic_json(checkpoint/'checkpoint.json',state);atomic_json(root/'update-journal.json',state)
        return identity
    except Exception:
        state['phase']='backup-failed';atomic_json(root/'update-journal.json',state)
        # No installation config/schema changed yet. Restore the old service availability.
        command(root,['up','-d','--no-deps',*MANAGED])
        raise

def require_persistent_managed_keys(root,inventory):
    if not inventory:return
    rendered=json.loads(command(root,['config','--format','json']))
    mounts=rendered.get('services',{}).get('control-plane',{}).get('volumes',[])
    if not any(isinstance(mount,dict)and mount.get('target')=='/var/lib/bifrost/keys'and mount.get('type')=='volume'and mount.get('source')=='controller_key_data'for mount in mounts):
        raise ValueError('Retained managed keys require explicit migration into the candidate controller_key_data volume before update. Preserve the old container and exact keys; no configuration or schema was changed.')


def digest(path):
    result=hashlib.sha256()
    with open_regular(path) as data:
        for chunk in iter(lambda:data.read(1024*1024),b''):result.update(chunk)
    return result.hexdigest()

def discard_staged_inputs(stage,archive):
    for path in stage.iterdir():
        if path==archive:continue
        if path.is_symlink():raise ValueError('Linked staging copy refused.')
        if path.is_dir():shutil.rmtree(path)
        else:path.unlink()

def checkpoint_archive(root,state,stage):
    checkpoint=directory(directory(root/'update-backups')/state['id'])
    archive=regular(checkpoint/'checkpoint.enc',True)
    if digest(archive)!=state['archiveSha256']:raise ValueError('Checkpoint digest changed.')
    tarpath=stage/'checkpoint.tar';unseal(archive,tarpath,recovery_key(root))
    with tarfile.open(tarpath) as tar:
        total=0; seen=set()
        for member in tar:
            name=pathlib.PurePosixPath(member.name);total+=member.size
            if name.is_absolute() or '..'in name.parts or member.name.rstrip('/')!=str(name) or member.name in seen or len(seen)>=20000 or not(member.isfile()or member.isdir()) or total>100*1024**3:raise ValueError('Unsafe recovery checkpoint.')
            seen.add(member.name)
        tar.extractall(stage,filter='data')
    regular(stage/'database.dump',True)

def key_inventory(folder):
    if not folder.is_dir()or folder.is_symlink():raise ValueError('Managed key inventory is unavailable.')
    result={}
    for path in folder.rglob('*'):
        if path.is_symlink():raise ValueError('Linked managed key refused.')
        if path.is_file():
            if len(result)>=1000 or path.stat().st_size>65536:raise ValueError('Managed key inventory exceeds its bound.')
            result[str(path.relative_to(folder))]=digest(regular(path))
    return result

def recover(root,confirmation):
    directory(root);state=journal(root)
    if not state or state['phase'] not in ('backup-ready','applying','failed','recovering'):raise ValueError('No recoverable interrupted update.')
    if confirmation!='RECOVER '+state['id']:raise ValueError('Exact checkpoint recovery confirmation required.')
    checkpoint=directory(root/'update-backups'/state['id'])
    with tempfile.TemporaryDirectory(prefix='recover-',dir=checkpoint) as temp:
        stage=pathlib.Path(temp);os.chmod(stage,0o700);checkpoint_archive(root,state,stage)
        command(root,['stop','--timeout','60',*MANAGED])
        # The updater never changes managed key material. Verify it still matches
        # the checkpoint before reconnecting saved ciphertext; never overwrite a
        # later out-of-band key change or claim it was restored automatically.
        command(root,['cp','control-plane:/var/lib/bifrost/keys',str(stage/'current-managed-keys')])
        if key_inventory(stage/'managed-keys')!=key_inventory(stage/'current-managed-keys'):raise ValueError('Managed encryption keys changed outside this update. Restore the exact escrowed key inventory before recovery.')
        # Original database and volume remain intact, including failed migration state.
        database='bifrost_recovery_'+secrets.token_hex(8)
        state['phase']='recovering';state.setdefault('recoveryAttempts',[]).append(database);state['recoveryDatabase']=database;atomic_json(root/'update-journal.json',state)
        command(root,['exec','-T','postgres','createdb','--username=bifrost_owner',database])
        with (stage/'database.dump').open('rb') as data:
            command(root,['exec','-T','postgres','pg_restore','--username=bifrost_owner','--exit-on-error','--dbname='+database],source=data)
        command(root,['exec','-T','postgres','psql','--username=bifrost_owner','--dbname=postgres','--set=ON_ERROR_STOP=1','--command',f'REVOKE ALL ON DATABASE {database} FROM PUBLIC; GRANT CONNECT ON DATABASE {database} TO bifrost_app'])
        # Keep candidate configuration and keys too, authenticated/encrypted.
        if not (checkpoint/'failed-configuration.enc').exists():
            failed=stage/'failed-configuration';failed.mkdir(mode=0o700)
            for name in ('.env','compose.yaml','IMAGE-LOCK.json','config','secrets'):
                if (root/name).exists():copy_private(root/name,failed/name)
            failed_tar=stage/'failed-configuration.tar'
            with tarfile.open(failed_tar,'w')as tar:tar.add(failed,arcname='failed-configuration')
            seal(failed_tar,checkpoint/'failed-configuration.enc',recovery_key(root))
        configuration=select_database((stage/'compose.yaml').read_text(),database)
        # Recover private config via atomic replacements after verifying each original.
        for name in ('.env','compose.yaml','IMAGE-LOCK.json'):
            if not(stage/name).exists():continue
            regular(root/name)
            data=configuration.encode()if name=='compose.yaml'else(stage/name).read_bytes()
            if name=='.env':
                lines=[line for line in data.decode().splitlines() if line.partition('=')[0]!='BIFROST_DATABASE_NAME']
                data=('\n'.join(lines+['BIFROST_DATABASE_NAME='+database])+'\n').encode()
            pending=root/(name+'.recovery-next')
            with pending.open('xb')as out:os.chmod(pending,0o600);out.write(data);out.flush();os.fsync(out.fileno())
            os.replace(pending,root/name)
        # Data/keys/config were not changed by the updater except public templates.
        # Restore public config and exact original keys; preserve extra new files.
        for folder in ('config','secrets'):
            for old in (stage/folder).rglob('*'):
                if old.is_dir():continue
                relative=old.relative_to(stage/folder);dest=root/folder/relative
                if dest.exists():regular(dest)
                else:dest.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
                pending=dest.with_name(dest.name+'.recovery-next')
                copy_private(old,pending);os.replace(pending,dest)
                if folder=='config':dest.chmod(0o644)
        command(root,['config','--quiet'])
        command(root,['up','-d','--no-deps','--wait','--wait-timeout','180',*MANAGED])
        state['phase']='recovered';state['recoveredAt']=time.time();atomic_json(root/'update-journal.json',state)
    return {'phase':'recovered','database':database,'originalDatabasePreserved':True}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('action',choices=['begin','applying','complete','failed','review','recover']);parser.add_argument('--root',type=pathlib.Path,required=True);parser.add_argument('--version');parser.add_argument('--confirmation')
    args=parser.parse_args();root=args.root.absolute();directory(root)
    if os.getuid()==0:raise ValueError('Run as the existing non-root Bifrost service account.')
    with installation_lock(root): run_action(args,root)

def run_action(args,root):
    if args.action=='begin':print(begin(root,args.version or ''));return
    state=journal(root)
    if not state:raise ValueError('No update journal.')
    if args.action=='review':print(json.dumps(state,sort_keys=True));return
    if args.action=='recover':print(json.dumps(recover(root,args.confirmation)));return
    allowed={'applying':('backup-ready',),'complete':('applying',),'failed':('backup-ready','applying')}
    if state['phase']not in allowed[args.action]:raise ValueError('Invalid update phase transition.')
    if args.action=='failed':command(root,['stop','--timeout','60',*MANAGED])
    state['phase']=args.action;atomic_json(root/'update-journal.json',state)
    print(state['id'])

if __name__=='__main__':
    try:main()
    except (ValueError,OSError,RuntimeError,subprocess.SubprocessError,tarfile.TarError):
        raise SystemExit('Bifrost recovery refused or failed. Retain the journal/checkpoint and inspect local diagnostics; no database or volume was deleted.')
