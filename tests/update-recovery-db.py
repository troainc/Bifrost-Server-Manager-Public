#!/usr/bin/env python3
"""Real dump/restore drill with simulated Compose service control, no installation."""
import importlib.util,json,os,pathlib,subprocess,tempfile,secrets,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
if os.environ.get('BIFROST_RECOVERY_DB_TEST')!='disposable-database-only':raise SystemExit('Disposable database confirmation required.')
CONTAINER='bifrost-release-20261021-pg'
label=subprocess.check_output(['docker','inspect','--format','{{index .Config.Labels "bifrost.audit"}}',CONTAINER],text=True).strip()
if label!='release-remediation-20261021':raise SystemExit('Only the labeled disposable audit container is permitted.')
spec=importlib.util.spec_from_file_location('recovery',ROOT/'scripts/update-recovery.py');recovery=importlib.util.module_from_spec(spec);spec.loader.exec_module(recovery)
def sql(query,database='bifrost'):
    return subprocess.check_output(['docker','exec',CONTAINER,'psql','-U','bifrost_owner','-d',database,'-tAX','-v','ON_ERROR_STOP=1','-c',query],text=True).strip()
table='recovery_sentinel_'+secrets.token_hex(6)
sql(f"CREATE TABLE {table}(value text NOT NULL); INSERT INTO {table} VALUES('baseline-preserved')")
calls=[]
def command(root,args,source=None,destination=None):
    calls.append(args)
    if args[0]=='cp':pathlib.Path(args[2]).mkdir(mode=0o700);return b''
    if args==['config','--format','json']:
        names=re.findall(r'DB_NAME: (bifrost(?:_recovery_[a-f0-9]{16})?)',(root/'compose.yaml').read_text())
        return json.dumps({'services':{name:{'environment':{'DB_NAME':names[0]}} for name in ('control-plane','migrate')}}).encode()
    if args[0]!='exec':return b''
    result=subprocess.run(['docker','exec','-i',CONTAINER,*args[3:]],stdin=source,stdout=destination if destination else subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    return result.stdout
recovery.command=command
with tempfile.TemporaryDirectory(prefix='bifrost-recovery-drill-')as temp:
    root=pathlib.Path(temp);root.chmod(0o700)
    (root/'secrets').mkdir(mode=0o700);(root/'config').mkdir(mode=0o700)
    for name,value in (('.env','BIFROST_VERSION=baseline\n'),('compose.yaml','services:\n  control-plane:\n    environment:\n      DB_NAME: bifrost\n  migrate:\n    environment:\n      DB_NAME: bifrost\n'),('secrets/synthetic-key.txt','synthetic-key-preserved'),('config/example.json','{}')):
        path=root/name;path.write_text(value);path.chmod(0o600)
    identity=recovery.begin(root,'v0.1.0-local.34');state=recovery.journal(root)
    assert state['phase']=='backup-ready'
    assert not list((root/'update-backups'/identity).rglob('database.dump')),'No plaintext database remains after checkpoint'
    state['phase']='failed';recovery.atomic_json(root/'update-journal.json',state)
    sql(f"ALTER TABLE {table} ADD COLUMN failed_migration text; UPDATE {table} SET value='failed-update-state'")
    (root/'.env').write_text('BIFROST_VERSION=failed-candidate\n')
    result=recovery.recover(root,'RECOVER '+identity)
    assert result['originalDatabasePreserved']is True
    assert sql('SELECT value FROM '+table,result['database'])=='baseline-preserved'
    assert sql('SELECT value FROM '+table)=='failed-update-state'
    assert (root/'secrets/synthetic-key.txt').read_text()=='synthetic-key-preserved'
    assert result['database']in(root/'compose.yaml').read_text()
    assert recovery.journal(root)['phase']=='recovered'
    assert (root/'update-backups'/identity/'failed-configuration.enc').is_file()
    # A later update must capture the restored database, not the failed original.
    sql(f"UPDATE {table} SET value='second-checkpoint'",result['database'])
    second=recovery.begin(root,'v0.1.0-local.35')
    assert recovery.journal(root)['database']==result['database']
    sql(f"UPDATE {table} SET value='second-failed-update'",result['database'])
    recovered=recovery.recover(root,'RECOVER '+second)
    assert sql('SELECT value FROM '+table,recovered['database'])=='second-checkpoint'
    assert sql('SELECT value FROM '+table,result['database'])=='second-failed-update'
    assert sql('SELECT value FROM '+table)=='failed-update-state'
print('PASS real PostgreSQL checkpoint, authenticated decrypt, new-database restore, exact key retention and original failed database preservation')
