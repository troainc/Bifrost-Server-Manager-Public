#!/usr/bin/env python3
"""Explicit full reset of a standard automatic Instance; run before install.sh.

Root only coordinates the two dedicated users. Workloads and tree deletion run
as their non-root owners. No system reset/prune, arbitrary path or force remove.
"""
import hashlib
import json
import os
import pathlib
import pwd
import re
import shutil
import stat
import subprocess
import sys

UUID = r"[a-f0-9]{8}-(?:[a-f0-9]{4}-){3}[a-f0-9]{12}"
SERVICES = {"postgres", "migrate", "control-plane", "web", "https"}
UNITS = ("bifrost-instance-setup.service", "bifrost-host-agent.service")
NODE = "/opt/bifrost-node-v24.19.0/bin/node"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def run(args, *, cwd="/", timeout=120, allow_failure=False):
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True, timeout=timeout)
    require(allow_failure or result.returncode == 0, "Command failed: " + pathlib.Path(args[0]).name + " " + args[1])
    return result


def json_run(args, **kwargs):
    output = run(args, **kwargs).stdout
    require(len(output) <= 8 * 1024 * 1024, "Runtime inspection too large")
    return json.loads(output)


def safe_directory(path, uid):
    require(path.is_absolute() and path.resolve() == path, "Directory resolves outside its canonical path")
    info = path.lstat()
    require(stat.S_ISDIR(info.st_mode) and not path.is_symlink() and info.st_uid == uid and not info.st_mode & 0o022,
            "Directory is not protected and owner managed")


def private_file(path, uid, maximum=4 * 1024 * 1024):
    safe_directory(path.parent, uid)
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), "rb") as source:
        info = os.fstat(source.fileno())
        require(stat.S_ISREG(info.st_mode) and info.st_uid == uid and info.st_nlink == 1 and
                not info.st_mode & 0o022 and info.st_size <= maximum, "Unsafe managed input")
        return source.read(maximum + 1)


def optional_tree(path, uid):
    require(path.parent.resolve() == path.parent and not path.is_symlink(), "Unsafe reset target")
    if path.exists():
        safe_directory(path, uid)
    return str(path)


def check_game_unit(data, package, setup):
    prefix = "[Unit]\nDescription=Bifrost " + ("automatic Instance connection" if setup else "local game Host Agent") + "\n[Service]\n"
    command = f"ExecStart={NODE} {package}/dist/" + ("automatic-instance-setup.js /home/bifrost-games/.config/bifrost-host-agent/local-bootstrap.json" if setup else "main.js") + "\n"
    rest = (f"WorkingDirectory={package}\n" if setup else "Environment=BIFROST_HOST_AGENT_CONFIG=/home/bifrost-games/.config/bifrost-host-agent/host-agent.json\n")
    expected = prefix + command + rest + "Restart=on-failure\nRestartSec=10\nUMask=0077\n" + ("NoNewPrivileges=true\n" if setup else "") + "[Install]\nWantedBy=default.target\n"
    require(data.decode() == expected, "Custom Host service; preserve it")


def game_review(home, uid):
    root = home / ".local/share/bifrost-instances"
    config_dir, state_dir = home / ".config/bifrost-host-agent", home / ".local/state/bifrost-host-agent"
    config_path = config_dir / "host-agent.json"
    config_bytes = private_file(config_path, uid)
    config = json.loads(config_bytes)
    require(config.get("provisioning", {}).get("root") == str(root), "Nonstandard game data root; preserve it")
    require(config.get("tokenFile") == str(state_dir / "host.token") and config.get("ledgerFile") == str(state_dir / "job-ledger.json"), "Nonstandard Host state paths")
    require(config.get("backupRoot") in (None, str(state_dir / "managed-backups")) and
            config.get("backupEncryptionKeyFile") in (None, str(state_dir / "managed-backups/encryption.key")) and
            not config.get("backupDestinations") and not config.get("backupRcloneConfigFile"),
            "Separate backup configuration needs its own reset review")
    safe_directory(root, uid)
    ledger = json.loads(private_file(state_dir / "job-ledger.json", uid))
    require(isinstance(ledger, dict) and all(re.fullmatch(UUID, key) and value == "complete" for key, value in ledger.items()), "Host has unfinished or invalid work")
    require(not os.path.lexists(state_dir / "job-ledger.json.lock"), "Host ledger busy; retry after current operation")
    fingerprint = hashlib.sha256(config_bytes).hexdigest()
    unit_paths = []
    for unit in UNITS:
        path = home / ".config/systemd/user" / unit
        data = private_file(path, uid, 8192)
        paths = set(re.findall(rb"/home/bifrost-games/\.local/opt/bifrost-host-agent-[a-f0-9]{64}", data))
        require(len(paths) == 1, "Unrecognized Host service package")
        package = paths.pop().decode()
        safe_directory(pathlib.Path(package), uid)
        check_game_unit(data, package, unit == UNITS[0])
        properties = run(["/usr/bin/systemctl", "--user", "show", unit, "--property=FragmentPath,DropInPaths"]).stdout
        properties = dict(line.split("=", 1) for line in properties.splitlines() if "=" in line)
        require(properties.get("FragmentPath") == str(path) and properties.get("DropInPaths") == "", "Custom effective Host service")
        fingerprint = hashlib.sha256((fingerprint + hashlib.sha256(data).hexdigest()).encode()).hexdigest()
        unit_paths.append(str(path))
    require(json_run(["/usr/bin/podman", "info", "--format", "json"])["host"]["security"]["rootless"] is True, "Game runtime must be rootless")
    ids = run(["/usr/bin/podman", "ps", "--all", "--quiet", "--no-trunc"]).stdout.split()
    require(len(ids) <= 256 and all(re.fullmatch(r"[a-f0-9]{64}", value) for value in ids), "Invalid container inventory")
    containers = json_run(["/usr/bin/podman", "container", "inspect", *ids]) if ids else []
    images = set()
    for container in containers:
        identity = container.get("Config", {}).get("Labels", {}).get("io.bifrost.instance-id", "")
        require(re.fullmatch(UUID, identity), "Foreign container on game account; preserve all workloads")
        name = container.get("Name", "").lstrip("/")
        require(name in (f"bifrost-{identity}", f"bifrost-install-{identity}") or
                re.fullmatch(f"bifrost-port-backup-{identity}-{UUID}", name), "Unrecognized Bifrost container name")
        for mount in container.get("Mounts", []):
            if mount.get("Type") == "bind":
                source = pathlib.Path(mount.get("Source", ""))
                require(source.is_absolute() and source.resolve() == source and source.is_relative_to(root / identity), "Container mount outside its instance")
            else:
                require(mount.get("Type") == "tmpfs", "Unreviewed persistent container volume")
        require(container["Id"] in ids, "Container identity changed")
        images.add(container["Image"])
    networks = []
    for entry in json_run(["/usr/bin/podman", "network", "ls", "--format", "json"]):
        name = entry["name"]
        if name == "podman":
            continue
        inspected = json_run(["/usr/bin/podman", "network", "inspect", name])[0]
        identity = inspected.get("labels", {}).get("io.bifrost.instance-id", "")
        require(re.fullmatch(UUID, identity) and name == f"bifrost-{identity}", "Foreign game network")
        require(all(value in ids for value in (inspected.get("containers") or {})), "Network has a foreign attachment")
        networks.append({"name": name, "id": inspected["id"]})
    trees = [optional_tree(path, uid) for path in (root, config_dir, state_dir)]
    return dict(component="game", fingerprint=fingerprint, containers=ids, images=sorted(images), networks=networks, trees=trees, units=unit_paths)


def panel_review(home, uid):
    root = home / ".local/share/bifrost"
    safe_directory(root, uid)
    environment = private_file(root / ".env", uid, 65536)
    values = dict(line.split("=", 1) for line in environment.decode().splitlines() if "=" in line and not line.startswith("#"))
    require(values.get("BIFROST_NODE_ROLE") == "instance", "Full automatic reset requires an Instance panel")
    compose_bytes = private_file(root / "compose.yaml", uid, 65536)
    require(any("rootless" in value.lower() for value in json_run(["docker", "info", "--format", "{{json .SecurityOptions}}"])), "Panel runtime must be rootless")
    model = json_run(["docker", "compose", "config", "--format", "json"], cwd=str(root))
    project = model.get("name")
    require(project == "bifrost" and set(model.get("services", {})) == SERVICES, "Unrecognized panel Compose project")
    require(set(model.get("volumes", {})) == {"postgres_data", "branding_data"}, "Unrecognized panel volumes")
    require(not any(value.get("external") for value in model["volumes"].values()), "External panel volume")
    ids = run(["docker", "ps", "--all", "--quiet", "--no-trunc", "--filter", "label=com.docker.compose.project=bifrost"]).stdout.split()
    require(len(ids) <= 16 and all(re.fullmatch(r"[a-f0-9]{64}", value) for value in ids), "Invalid panel inventory")
    containers = json_run(["docker", "container", "inspect", *ids]) if ids else []
    images = set()
    for item in containers:
        labels = item["Config"].get("Labels") or {}
        require(labels.get("com.docker.compose.service") in SERVICES and labels.get("com.docker.compose.project.working_dir") == str(root), "Foreign panel-project container")
        images.add(item["Image"])
    volumes = []
    for key, value in model["volumes"].items():
        name = value.get("name")
        require(name == f"bifrost_{key}", "Unexpected panel volume name")
        found = run(["docker", "volume", "inspect", name], allow_failure=True)
        if found.returncode:
            continue
        volume = json.loads(found.stdout)[0]
        labels = volume.get("Labels") or {}
        require(labels.get("com.docker.compose.project") == project and labels.get("com.docker.compose.volume") == key, "Foreign panel volume")
        attached = run(["docker", "ps", "--all", "--quiet", "--no-trunc", "--filter", f"volume={name}"]).stdout.split()
        require(all(identity in ids for identity in attached), "Panel volume shared with another workload")
        volumes.append(name)
    networks = []
    for key, value in model.get("networks", {}).items():
        require(not value.get("external"), "External panel network")
        name = value.get("name")
        require(name == f"bifrost_{key}", "Unexpected panel network name")
        found = run(["docker", "network", "inspect", name], allow_failure=True)
        if found.returncode:
            continue
        network = json.loads(found.stdout)[0]
        require(network.get("Labels", {}).get("com.docker.compose.project") == project and all(identity in ids for identity in (network.get("Containers") or {})), "Panel network shared with another workload")
        networks.append({"name": name, "id": network["Id"]})
    return dict(component="panel", fingerprint=hashlib.sha256(environment + compose_bytes).hexdigest(), containers=ids,
                images=sorted(images), networks=networks, volumes=volumes, trees=[optional_tree(root, uid)])


def delete_tree(path, uid):
    target = pathlib.Path(path)
    if target.exists():
        safe_directory(target, uid)
        # Python's Linux fd-based rmtree does not follow directory symlinks.
        require(shutil.rmtree.avoids_symlink_attacks, "Safe filesystem removal unavailable")
        shutil.rmtree(target)


def game_apply(home, uid, expected):
    current = game_review(home, uid)
    require(current == expected, "Game reset review changed; no cleanup performed")
    state = home / ".local/state/bifrost-host-agent"
    lock_path = state / "job-ledger.json.lock"
    lock = os.open(lock_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    original_inode = os.fstat(lock).st_ino
    with os.fdopen(lock, "w") as owner:
        json.dump(dict(owner="explicit-full-reset", pid=os.getpid()), owner)
        owner.flush()
        os.fsync(owner.fileno())
    completed = False
    try:
        for identity in current["containers"]:
            status = json_run(["/usr/bin/podman", "container", "inspect", identity])[0]["State"]
            if status.get("Running"):
                run(["/usr/bin/podman", "stop", "--time", "60", identity], timeout=95)
            stopped = json_run(["/usr/bin/podman", "container", "inspect", identity])[0]["State"]
            require(stopped.get("Running") is False and stopped.get("Paused") is False and stopped.get("Pid") == 0, "Game did not stop")
        run(["/usr/bin/systemctl", "--user", "disable", "--now", *UNITS], timeout=150)
        for unit in UNITS:
            status = run(["/usr/bin/systemctl", "--user", "show", unit, "--property=ActiveState", "--value"]).stdout.strip()
            require(status == "inactive", "Host service did not stop")
        require(set(run(["/usr/bin/podman", "ps", "--all", "--quiet", "--no-trunc"]).stdout.split()) == set(current["containers"]), "Game inventory changed during shutdown")
        for identity in current["containers"]:
            run(["/usr/bin/podman", "rm", identity])
        for network in current["networks"]:
            actual = json_run(["/usr/bin/podman", "network", "inspect", network["name"]])[0]
            require(actual["id"] == network["id"] and not actual.get("containers"), "Game network still attached")
            run(["/usr/bin/podman", "network", "rm", network["name"]])
        for image in current["images"]:
            # No --force: runtime refuses shared or otherwise retained images.
            run(["/usr/bin/podman", "image", "rm", image], allow_failure=True)
        for unit in current["units"]:
            private_file(pathlib.Path(unit), uid, 8192)
            pathlib.Path(unit).unlink()
        run(["/usr/bin/systemctl", "--user", "daemon-reload"])
        run(["/usr/bin/systemctl", "--user", "unset-environment", "BIFROST_STORAGE_TEST_INSTANCE_ID",
             "BIFROST_STORAGE_TEST_BLUEPRINT_DIGEST", "BIFROST_STORAGE_TEST_EXPIRES_AT"])
        require(lock_path.lstat().st_ino == original_inode, "Ledger lock ownership changed")
        for tree in current["trees"]:
            delete_tree(tree, uid)
        completed = True
    finally:
        if not completed and lock_path.exists() and lock_path.lstat().st_ino == original_inode:
            lock_path.unlink()


def panel_apply(home, uid, expected):
    current = panel_review(home, uid)
    require(current == expected, "Panel reset review changed; no cleanup performed")
    if current["containers"]:
        run(["docker", "stop", "--time", "60", *current["containers"]], timeout=150)
        run(["docker", "rm", *current["containers"]])
    for volume in current["volumes"]:
        run(["docker", "volume", "rm", volume])
    for network in current["networks"]:
        actual = json_run(["docker", "network", "inspect", network["id"]])[0]
        require(actual["Name"] == network["name"] and not actual.get("Containers"), "Panel network still attached")
        run(["docker", "network", "rm", network["id"]])
    for image in current["images"]:
        run(["docker", "image", "rm", image], allow_failure=True)
    delete_tree(current["trees"][0], uid)


def account_environment(account):
    record = pwd.getpwnam(account)
    home = pathlib.Path(record.pw_dir)
    require(record.pw_uid > 0 and home == pathlib.Path("/home") / account, "Nonstandard service account")
    safe_directory(home, record.pw_uid)
    return record, dict(HOME=str(home), USER=account, LOGNAME=account,
                       PATH=f"{home}/.local/bin:{home}/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                       XDG_RUNTIME_DIR=f"/run/user/{record.pw_uid}",
                       DBUS_SESSION_BUS_ADDRESS=f"unix:path=/run/user/{record.pw_uid}/bus",
                       DOCKER_HOST=f"unix:///run/user/{record.pw_uid}/docker.sock")


def child(account, mode, plan=None):
    _, environment = account_environment(account)
    args = ["/usr/sbin/runuser", "-u", account, "--", "/usr/bin/env", "-i"]
    args += [f"{key}={value}" for key, value in environment.items()]
    args += ["/usr/bin/python3", str(pathlib.Path(__file__).resolve()), mode]
    result = subprocess.run(args, input=json.dumps(plan) if plan else "", text=True, capture_output=True, cwd="/", timeout=600)
    require(result.returncode == 0, f"{account} reset {mode} failed; preserve remaining state and inspect the bounded error: " + result.stdout.strip()[:300])
    return json.loads(result.stdout)


def main():
    require(sys.platform == "linux", "Linux is required")
    if len(sys.argv) == 2 and sys.argv[1] in ("--component-review", "--component-apply"):
        account = pwd.getpwuid(os.getuid()).pw_name
        require(os.getuid() > 0 and account in ("bifrost", "bifrost-games"), "Use dedicated non-root component owner")
        record, _ = account_environment(account)
        home = pathlib.Path(record.pw_dir)
        review = game_review if account == "bifrost-games" else panel_review
        if sys.argv[1] == "--component-review":
            return review(home, record.pw_uid)
        plan = json.load(sys.stdin)
        (game_apply if account == "bifrost-games" else panel_apply)(home, record.pw_uid, plan)
        return dict(componentReset=True, component=plan["component"])
    require(os.getuid() == 0 and len(sys.argv) == 2 and sys.argv[1] in ("--review", "--apply-reset"),
            "Run as VM administrator: --review or --apply-reset")
    for account in ("bifrost", "bifrost-games"):
        record, _ = account_environment(account)
        require(pathlib.Path(f"/run/user/{record.pw_uid}/bus").exists(), "Dedicated user manager is unavailable")
    game, panel = child("bifrost-games", "--component-review"), child("bifrost", "--component-review")
    summary = dict(readOnly=True, resetReady=True, gameContainers=len(game["containers"]), panelContainers=len(panel["containers"]),
                   scope="panel database, panel credentials, automatic Host enrollment and all local Bifrost test worlds")
    if sys.argv[1] == "--review":
        return summary
    require(sys.stdin.isatty(), "Full reset requires an interactive terminal")
    print(json.dumps(summary), flush=True)
    print("Permanently remove the standard Instance panel and all its Bifrost games/enrollment. Linux accounts and router settings remain. Type WIPE ALL:", flush=True)
    require(input().strip() == "WIPE ALL", "Full reset cancelled; existing data preserved")
    child("bifrost-games", "--component-apply", game)
    child("bifrost", "--component-apply", panel)
    return dict(resetCompleted=True, panelRemoved=True, automaticHostRemoved=True, testWorldsRemoved=True,
                nextStep="Run the verified matched install.sh --instance as the administrator")


if __name__ == "__main__":
    try:
        print(json.dumps(main()), flush=True)
    except (RuntimeError, OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        # No child stderr, tokens, private config or runtime inspection is disclosed.
        text = str(error) if isinstance(error, RuntimeError) else type(error).__name__
        print(json.dumps(dict(resetCompleted=False, code="RESET_REFUSED", reason=text[:500])), flush=True)
        sys.exit(1)
