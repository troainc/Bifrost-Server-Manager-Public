import importlib.util
import json
import os
import pathlib
import tempfile
import tarfile
import io
import unittest
from unittest import mock

ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('recovery',ROOT/'scripts/update-recovery.py');recovery=importlib.util.module_from_spec(spec);spec.loader.exec_module(recovery)

@unittest.skipUnless(os.name=='posix','POSIX service ownership and OpenSSL required')
class UpdateRecovery(unittest.TestCase):
    def test_checkpoint_copy_supports_old_python_and_refuses_unsafe_entries(self):
        for entry in ['configuration/settings.json','../outside','configuration/link','checkpoint.tar']:
            with self.subTest(entry=entry),tempfile.TemporaryDirectory() as temp:
                root=pathlib.Path(temp);checkpoint=root/'update-backups'/'safe';checkpoint.mkdir(parents=True,mode=0o700)
                archive=checkpoint/'checkpoint.enc'
                with tarfile.open(archive,'w') as tar:
                    data=b'retained';member=tarfile.TarInfo('database.dump');member.size=len(data);tar.addfile(member,io.BytesIO(data))
                    member=tarfile.TarInfo(entry)
                    if entry.endswith('/link'):member.type=tarfile.SYMTYPE;member.linkname='/outside'
                    else:member.size=len(data)
                    tar.addfile(member,None if member.issym() else io.BytesIO(data))
                archive.chmod(0o600);stage=root/'stage';stage.mkdir(mode=0o700)
                with mock.patch.object(recovery,'recovery_key',return_value=b''),mock.patch.object(recovery,'unseal',side_effect=lambda src,dst,key:recovery.shutil.copyfile(src,dst)),mock.patch.object(tarfile.TarFile,'extractall',side_effect=AssertionError('Unfiltered archive extraction must not run')):
                    if entry=='configuration/settings.json':
                        recovery.checkpoint_archive(root,{'id':'safe','archiveSha256':recovery.digest(archive)},stage)
                        self.assertEqual((stage/entry).read_bytes(),b'retained')
                        self.assertEqual((stage/entry).stat().st_mode&0o777,0o600)
                    else:
                        with self.assertRaises((ValueError,FileExistsError)):
                            recovery.checkpoint_archive(root,{'id':'safe','archiveSha256':recovery.digest(archive)},stage)
                self.assertFalse((root/'outside').exists())

    def test_authenticated_envelope_rejects_changed_bytes_wrong_keys_and_missing_escrow(self):
        with tempfile.TemporaryDirectory()as temp:
            root=pathlib.Path(temp);(root/'secrets').mkdir(mode=0o700)
            key=recovery.recovery_key(root,True);plain=root/'data';plain.write_bytes(b'synthetic database and key inventory');plain.chmod(0o600)
            encrypted=root/'checkpoint.enc';recovery.seal(plain,encrypted,key)
            output=root/'restored';recovery.unseal(encrypted,output,key);self.assertEqual(output.read_bytes(),plain.read_bytes())
            output.unlink()
            with self.assertRaises(ValueError):recovery.unseal(encrypted,output,os.urandom(64))
            self.assertFalse(output.exists())
            data=bytearray(encrypted.read_bytes());data[30]^=1;encrypted.write_bytes(data)
            with self.assertRaises(ValueError):recovery.unseal(encrypted,output,key)
            self.assertFalse(output.exists())
            (root/'secrets/update_recovery.key').unlink()
            with self.assertRaises(ValueError):recovery.recovery_key(root)
            self.assertFalse((root/'secrets/update_recovery.key').exists())

    def test_checkpoint_failure_restarts_only_original_services_and_preserves_config(self):
        with tempfile.TemporaryDirectory()as temp:
            root=pathlib.Path(temp);(root/'secrets').mkdir(mode=0o700)
            (root/'.env').write_text('BIFROST_VERSION=previous\n');(root/'.env').chmod(0o600)
            (root/'compose.yaml').write_text('services: {}\n');(root/'compose.yaml').chmod(0o600)
            calls=[]
            def command(path,args,**kwargs):
                calls.append(args)
                if args==['config','--format','json']:return json.dumps({'services':{name:{'environment':{'DB_NAME':'bifrost'}} for name in ('control-plane','migrate')}}).encode()
                if args[0]=='cp':pathlib.Path(args[2]).mkdir(mode=0o700);return b''
                if args[-1]=='SELECT pg_database_size(current_database())':return b'1024\n'
                if 'pg_dump'in args:raise RuntimeError('synthetic storage failure')
                return b''
            with mock.patch.object(recovery,'command',side_effect=command):
                with self.assertRaises(RuntimeError):recovery.begin(root,'v0.1.0-test.34')
            self.assertEqual((root/'.env').read_text(),'BIFROST_VERSION=previous\n')
            self.assertEqual(recovery.journal(root)['phase'],'backup-failed')
            self.assertIn(['up','-d','--no-deps',*recovery.MANAGED],calls)

    def test_changed_journal_and_symlinked_checkpoint_refuse_before_commands(self):
        with tempfile.TemporaryDirectory()as temp:
            root=pathlib.Path(temp);root.chmod(0o700)
            recovery.atomic_json(root/'update-journal.json',{'schemaVersion':1,'id':'../foreign','phase':'failed'})
            with self.assertRaises(ValueError):recovery.journal(root)
            external=root/'external';external.write_bytes(b'unchanged');external.chmod(0o600)
            link=root/'link';link.symlink_to(external)
            with self.assertRaises(ValueError):recovery.regular(link,True)
            self.assertEqual(external.read_bytes(),b'unchanged')

    def test_lock_rejects_hardlinks_and_concurrent_processes(self):
        import subprocess,sys
        with tempfile.TemporaryDirectory()as temp:
            root=pathlib.Path(temp);root.chmod(0o700)
            with recovery.installation_lock(root):
                child=subprocess.run([sys.executable,str(ROOT/'scripts/update-recovery.py'),'review','--root',str(root)],capture_output=True)
                self.assertNotEqual(child.returncode,0)
            external=root/'retained';external.write_bytes(b'preserve');external.chmod(0o600)
            (root/'update.lock').unlink();os.link(external,root/'update.lock')
            with self.assertRaises(ValueError):
                with recovery.installation_lock(root):pass
            self.assertEqual(external.read_bytes(),b'preserve')

    def test_database_selection_is_bounded_and_supports_repeated_recovery(self):
        config='services:\n  migrate:\n    environment:\n      DB_NAME: bifrost\n  control-plane:\n    environment:\n      DB_NAME: ${BIFROST_DATABASE_NAME:-bifrost}\n'
        first='bifrost_recovery_'+'a'*16;second='bifrost_recovery_'+'b'*16
        self.assertEqual(recovery.select_database(recovery.select_database(config,first),second).count(second),2)
        with self.assertRaises(ValueError):recovery.select_database('DB_NAME: unrelated',first)

    def test_crypto_refuses_linked_input_and_existing_output_without_overwrite(self):
        with tempfile.TemporaryDirectory()as temp:
            root=pathlib.Path(temp);source=root/'source';source.write_bytes(b'preserved source');source.chmod(0o600)
            retained=root/'retained';retained.write_bytes(b'preserved output');retained.chmod(0o600)
            with self.assertRaises(FileExistsError):recovery.crypt(source,retained,os.urandom(64))
            self.assertEqual(retained.read_bytes(),b'preserved output')
            alias=root/'alias';alias.symlink_to(source)
            with self.assertRaises(OSError):recovery.crypt(alias,root/'new',os.urandom(64))
            hard=root/'hard';os.link(source,hard)
            with self.assertRaises(ValueError):recovery.crypt(hard,root/'new',os.urandom(64))
            self.assertFalse((root/'new').exists())

    def test_retained_managed_keys_require_the_exact_persistent_candidate_mount(self):
        recovery.require_persistent_managed_keys(pathlib.Path('/unused'),{})
        for volumes,accepted in [([],False),([{'type':'bind','source':'/foreign','target':'/var/lib/bifrost/keys'}],False),([{'type':'volume','source':'controller_key_data','target':'/var/lib/bifrost/keys'}],True)]:
            rendered=json.dumps({'services':{'control-plane':{'volumes':volumes}}}).encode()
            with mock.patch.object(recovery,'command',return_value=rendered):
                if accepted:recovery.require_persistent_managed_keys(pathlib.Path('/unused'),{'retained-key':'digest'})
                else:
                    with self.assertRaises(ValueError):recovery.require_persistent_managed_keys(pathlib.Path('/unused'),{'retained-key':'digest'})
