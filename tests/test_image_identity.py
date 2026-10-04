import hashlib
import importlib.util
import io
import json
import pathlib
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import tarfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("identity", ROOT / "scripts/verify-image-archive.py")
identity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(identity)


class ImageIdentity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.archive = self.root / "images.tar"
        self.lock = self.root / "IMAGE-LOCK.json"
        self.configs = {}
        self.manifests = {}
        self.blobs = {}
        saved, descriptors = [], []
        for name in ["control-plane", "web", "postgres"]:
            tag = f"bifrost/{name}:v0.1.0-installtest.6"
            config = json.dumps({"os": "linux", "architecture": "amd64", "name": name}).encode()
            config_digest = "sha256:" + hashlib.sha256(config).hexdigest()
            config_path = "blobs/sha256/" + config_digest[7:]
            manifest = json.dumps({"config": {"digest": config_digest}}).encode()
            manifest_digest = "sha256:" + hashlib.sha256(manifest).hexdigest()
            self.blobs[config_path] = config
            self.blobs["blobs/sha256/" + manifest_digest[7:]] = manifest
            self.configs[tag] = config_digest
            self.manifests[tag] = manifest_digest
            saved.append({"Config": config_path, "RepoTags": [tag], "Layers": []})
            descriptors.append({"digest": manifest_digest, "annotations": {"io.containerd.image.name": "docker.io/" + tag}})
        self.blobs["manifest.json"] = json.dumps(saved).encode()
        self.blobs["index.json"] = json.dumps({"manifests": descriptors}).encode()
        self.write_archive()
        self.lock.write_text(json.dumps(self.configs))

    def write_archive(self):
        with tarfile.open(self.archive, "w") as archive:
            for name, data in self.blobs.items():
                member = tarfile.TarInfo(name)
                member.size = len(data)
                archive.addfile(member, io.BytesIO(data))

    def verify(self, ids, **fields):
        def inspect(command, **kwargs):
            tag = command[-1]
            return json.dumps([{"Id": ids[tag], "Os": "linux", "Architecture": "amd64", **fields}])
        with patch.object(identity.subprocess, "check_output", side_effect=inspect):
            identity.main([str(self.archive), str(self.lock)])

    def test_classic_configuration_ids_pass(self):
        self.verify(self.configs)

    def test_containerd_manifest_ids_pass_for_the_same_locked_configs(self):
        self.verify(self.manifests)

    def test_wrong_loaded_image_is_rejected(self):
        wrong = {tag: "sha256:" + "f" * 64 for tag in self.configs}
        with self.assertRaisesRegex(ValueError, "Image identity mismatch"):
            self.verify(wrong)

    def test_wrong_platform_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Image identity mismatch"):
            self.verify(self.configs, Architecture="arm64")

    def test_corrupt_manifest_is_rejected(self):
        name = "blobs/sha256/" + next(iter(self.manifests.values()))[7:]
        self.blobs[name] += b" "
        self.write_archive()
        with self.assertRaisesRegex(ValueError, "metadata digest mismatch"):
            self.verify(self.manifests)

    def test_manifest_pointing_to_another_config_is_rejected(self):
        index = json.loads(self.blobs["index.json"])
        manifest = json.dumps({"config": {"digest": "sha256:" + "f" * 64}}).encode()
        digest = "sha256:" + hashlib.sha256(manifest).hexdigest()
        self.blobs["blobs/sha256/" + digest[7:]] = manifest
        index["manifests"][0]["digest"] = digest
        self.blobs["index.json"] = json.dumps(index).encode()
        self.write_archive()
        with self.assertRaisesRegex(ValueError, "manifest/config identity mismatch"):
            self.verify(self.configs)

    def test_wrong_lock_is_rejected(self):
        lock = dict(self.configs)
        lock[next(iter(lock))] = "sha256:" + "f" * 64
        self.lock.write_text(json.dumps(lock))
        with self.assertRaisesRegex(ValueError, "Archive/lock"):
            self.verify(self.configs)

    def test_duplicate_archive_metadata_is_rejected(self):
        with tarfile.open(self.archive, "a") as archive:
            data = self.blobs["manifest.json"]
            member = tarfile.TarInfo("./manifest.json")
            member.size = len(data)
            archive.addfile(member, io.BytesIO(data))
        with self.assertRaisesRegex(ValueError, "Unsafe or duplicate"):
            self.verify(self.configs)

    def test_symlinked_config_is_rejected(self):
        name = "blobs/sha256/" + next(iter(self.configs.values()))[7:]
        with tarfile.open(self.archive, "w") as archive:
            for path, data in self.blobs.items():
                member = tarfile.TarInfo(path)
                if path == name:
                    member.type = tarfile.SYMTYPE
                    member.linkname = "/outside"
                    archive.addfile(member)
                else:
                    member.size = len(data)
                    archive.addfile(member, io.BytesIO(data))
        with self.assertRaisesRegex(ValueError, "Missing or unsafe"):
            self.verify(self.configs)

    def test_classic_archive_without_oci_index_still_checks_config_ids(self):
        del self.blobs["index.json"]
        self.write_archive()
        self.verify(self.configs)
        with self.assertRaisesRegex(ValueError, "Image identity mismatch"):
            self.verify(self.manifests)

    def test_builder_locks_configs_independently_of_engine_ids(self):
        identity.main([str(self.archive), str(self.lock), "--write-lock", *self.configs])
        self.assertEqual(json.loads(self.lock.read_text()), self.configs)

    def test_both_standalone_scripts_embed_the_exact_verifier(self):
        for name in ["install.sh", "update.sh"]:
            script = (ROOT / name).read_text()
            embedded = script.split("<<'IMAGE_IDENTITY_PY'\n", 1)[1].split("\nIMAGE_IDENTITY_PY", 1)[0]
            self.assertEqual(embedded, (ROOT / "scripts/verify-image-archive.py").read_text().rstrip())

    def test_bootstrap_pins_the_corrected_updater_with_a_matching_digest(self):
        script = (ROOT / "install.sh").read_text()
        values = dict(line.split("=", 1) for line in script.splitlines() if line.startswith(("UPDATER_SOURCE_REF=", "UPDATER_SHA256=")))
        updater = subprocess.check_output(["git", "-c", "safe.directory=*", "show", values["UPDATER_SOURCE_REF"] + ":update.sh"], cwd=ROOT)
        self.assertEqual(hashlib.sha256(updater).hexdigest(), values["UPDATER_SHA256"])
        self.assertIn(b"IMAGE_IDENTITY_PY", updater)
        self.assertIn("Pinned updater version differs", script)


if __name__ == "__main__":
    unittest.main()
