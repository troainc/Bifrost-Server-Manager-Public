"""Verify Docker image identity against the checksummed release archive.

Classic Docker reports the config digest as Id; containerd reports the manifest
digest. Accept either only when archive metadata binds it to the locked config.
This file is embedded verbatim in both standalone installer scripts.
"""
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import tarfile


def archive_identities(path):
    with tarfile.open(path, "r:") as archive:
        members = archive.getmembers()
        if len(members) > 10000:
            raise ValueError("Too many image archive entries")
        files = {}
        for member in members:
            name = str(pathlib.PurePosixPath(member.name))
            if name in files or name.startswith("/") or ".." in pathlib.PurePosixPath(name).parts:
                raise ValueError("Unsafe or duplicate image archive entry")
            files[name] = member

        def read_json(name, digest=None):
            member = files.get(name)
            if not member or not member.isfile() or not 0 < member.size <= 1024 * 1024:
                raise ValueError("Missing or unsafe image metadata: " + name)
            data = archive.extractfile(member).read()
            actual = "sha256:" + hashlib.sha256(data).hexdigest()
            if digest is not None and actual != digest:
                raise ValueError("Image metadata digest mismatch: " + name)
            return json.loads(data), actual

        saved, _ = read_json("manifest.json")
        identities = {}
        for image in saved:
            config, digest = read_json(image["Config"])
            if config.get("os") != "linux" or config.get("architecture") != "amd64":
                raise ValueError("Only Linux amd64 release images are supported")
            for tag in image.get("RepoTags") or []:
                if tag in identities:
                    raise ValueError("Ambiguous image tag: " + tag)
                identities[tag] = {"config": digest, "ids": {digest}}

        if "index.json" in files:
            index, _ = read_json("index.json")
            for descriptor in index["manifests"]:
                tag = descriptor.get("annotations", {}).get("io.containerd.image.name", "")
                if tag.startswith("docker.io/"):
                    tag = tag[len("docker.io/"):]
                if tag not in identities:
                    continue
                def manifest_data(item):
                    digest = item["digest"]
                    if not re.fullmatch(r"sha256:[a-f0-9]{64}", digest):
                        raise ValueError("Invalid OCI manifest digest")
                    data, _ = read_json("blobs/sha256/" + digest[7:], digest)
                    return data, digest

                manifest, digest = manifest_data(descriptor)
                if "manifests" in manifest:
                    # BuildKit's containerd store may tag an OCI index containing
                    # one runnable image and its non-runnable provenance record.
                    children = manifest["manifests"]
                    if manifest.get("schemaVersion") != 2 or not isinstance(children, list) or not 1 <= len(children) <= 8:
                        raise ValueError("Invalid or excessive OCI index")
                    runnable, attestations = [], []
                    for child in children:
                        body, child_digest = manifest_data(child)
                        if "manifests" in body:
                            raise ValueError("Nested OCI indexes are unsupported")
                        platform = child.get("platform", {})
                        annotations = child.get("annotations", {})
                        if platform.get("os") == "linux" and platform.get("architecture") == "amd64":
                            if body.get("config", {}).get("digest") != identities[tag]["config"]:
                                raise ValueError("OCI manifest/config identity mismatch: " + tag)
                            runnable.append(child_digest)
                        elif platform == {"architecture": "unknown", "os": "unknown"} and annotations.get("vnd.docker.reference.type") == "attestation-manifest":
                            attestations.append(annotations.get("vnd.docker.reference.digest"))
                        else:
                            raise ValueError("Unsupported OCI index platform")
                    if len(runnable) != 1 or any(reference != runnable[0] for reference in attestations):
                        raise ValueError("Ambiguous or unbound OCI index")
                    identities[tag]["ids"].update([digest, runnable[0]])
                    continue
                if manifest.get("config", {}).get("digest") != identities[tag]["config"]:
                    raise ValueError("OCI manifest/config identity mismatch: " + tag)
                identities[tag]["ids"].add(digest)
        return identities


def main(args):
    archive_path, lock_path = args[:2]
    identities = archive_identities(archive_path)
    if len(args) > 2 and args[2] == "--write-lock":
        tags = args[3:]
        if len(tags) != 3 or len(set(tags)) != 3:
            raise ValueError("Exactly three release image tags are required")
        lock = {tag: identities[tag]["config"] for tag in tags}
        pathlib.Path(lock_path).write_text(json.dumps(lock, indent=2) + "\n")
        return
    lock = json.loads(pathlib.Path(lock_path).read_text())
    if not isinstance(lock, dict) or len(lock) != 3:
        raise ValueError("Exactly three locked release images are required")
    for tag, expected in lock.items():
        if not re.fullmatch(r"bifrost/(control-plane|web|postgres):v[0-9]+\.[0-9]+\.[0-9]+-installtest\.[0-9]+", tag):
            raise ValueError("Unexpected release image tag: " + tag)
        if not isinstance(expected, str) or not re.fullmatch(r"sha256:[a-f0-9]{64}", expected):
            raise ValueError("Invalid locked configuration digest: " + tag)
        identity = identities.get(tag)
        if not identity or identity["config"] != expected:
            raise ValueError("Archive/lock configuration mismatch: " + tag)
        image = json.loads(subprocess.check_output(["docker", "image", "inspect", tag], text=True))[0]
        actual = image["Id"]
        if actual not in identity["ids"] or image.get("Os") != "linux" or image.get("Architecture") != "amd64":
            raise ValueError(f"Image identity mismatch: {tag}; loaded={actual}; allowed={','.join(sorted(identity['ids']))}")
        print(f"Verified {tag}: {actual} (locked config {expected})")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except (ValueError, KeyError, IndexError, OSError, tarfile.TarError, subprocess.CalledProcessError) as error:
        raise SystemExit(str(error))
