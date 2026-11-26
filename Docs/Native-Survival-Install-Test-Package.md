# Stationeers, Valheim and Palworld install test package

Download **bifrost-native-games.55.1.zip** from the [native game testing release](https://github.com/troainc/Bifrost-Server-Manager-Public/releases/tag/v0.1.0-runtime.55). This adds three signed Linux recipes and the matched compiled Host Agent candidate. The runtime is downloaded automatically from the immutable public release; SteamCMD downloads the official game files during installation. No game binaries, credentials or worlds are redistributed.

This is a controlled test add-on, not a replacement for the full signed Bifrost application installer. The existing application Test54 release remains unchanged. Use it with the matched Alpha55 Controller, whose owner deployment includes these signed recipes. Existing Test54 Agents must be upgraded before approving the new adapters.

## Included files

- `blueprints/`: the three signed records, public verification key, signed handoff and exact-artifact review.
- `upgrade-automatic-host-survival55.mjs`: a guarded update for the exact standard Test54 automatic Host and Node 24.22.3. It downloads the checksum-pinned compiled Agent, preserves the old package, accounts, pairing, credentials, setup worker, profiles and worlds, and changes only the Agent unit. Custom or active-job states refuse rather than reset anything.
- `bifrost-linux-host-agent-survival.55.2.zip`: the matched compiled Agent, including `dist/approve-release-catalog.js`.
- `INSTALL.md` and `SHA256SUMS`.

The Agent archive SHA-256 is `1780ecbe51fd3dfb563e0c8893672fd4c108a54f229b8a0ef8f62e1b4da33e46`.

Approved recipe publisher:

```text
ed25519-sha256:0c0369412260010ab125acf2f77a922a59aefbdb06d83d21b817bcf2ece8abfd
```

## Existing standard automatic Host

Run these steps as the existing **bifrost-games** service account, from the privately extracted add-on directory. Do not re-enroll the Host or rerun first-account setup. If entering from a root console, use `runuser -u bifrost-games -- /bin/bash`, change to that account's home, and set `XDG_RUNTIME_DIR=/run/user/$(id -u)` before using its existing user services. Neither game runtime nor Agent should run as root.

First run the read-only diagnosis:

```bash
/opt/bifrost-node-v24.22.3/bin/node ./upgrade-automatic-host-survival55.mjs --diagnose
```

If it verifies the exact current unit, inactive setup worker, published archive and idle state, perform the guarded Agent update:

```bash
/opt/bifrost-node-v24.22.3/bin/node ./upgrade-automatic-host-survival55.mjs
```

The updater restores the prior unit if new-Agent startup fails. A refusal leaves retained state for review; report its stage instead of deleting locks or resetting enrollment. The updater's recovery flag is only for an independently reviewed stopped-Agent state.

Then explicitly approve the additional signed catalog, preserving existing approvals. This stops only the Agent, not the game containers:

```bash
NODE=/opt/bifrost-node-v24.22.3/bin/node
PACKAGE="$HOME/.local/opt/bifrost-host-agent-1780ecbe51fd3dfb563e0c8893672fd4c108a54f229b8a0ef8f62e1b4da33e46"
CONFIG="$HOME/.config/bifrost-host-agent/host-agent.json"
KEY=ed25519-sha256:0c0369412260010ab125acf2f77a922a59aefbdb06d83d21b817bcf2ece8abfd
systemctl --user stop bifrost-host-agent.service || exit 1
if "$NODE" "$PACKAGE/dist/approve-release-catalog.js" "$CONFIG" "$PWD/blueprints" "$KEY"; then
    systemctl --user start bifrost-host-agent.service
else
    systemctl --user start bifrost-host-agent.service
    exit 1
fi
```

The approval command verifies the publisher and handoff hashes, retains existing game IDs and keys, rejects replacements, and keeps a protected previous configuration. It does not install or start a game. For a custom manual Host, use its reviewed matching upgrade procedure and actual configuration path; the standard automatic updater intentionally refuses custom units.

## Install from the GUI

1. Wait for the existing Host to return online and report Agent `0.1.0-alpha.55-survival.2` with all three approved recipes.
2. Open **Game blueprints** or **Game servers → Create instance**. Choose Stationeers, Valheim or Palworld and the compatible Host.
3. Set the instance name, allocation and ports, then review the game's settings before confirming installation. Follow the install job while the runtime and official files download.
4. After readiness, check Settings and test a player connection. Stop/start the new test instance and confirm its world survives. Existing instances remain separate.

| Game | Minimum game RAM / CPU | Default UDP ports | Settings and saved state |
| --- | --- | --- | --- |
| Stationeers | 12 GiB / 4 cores | 27016 game, 27015 update/query | `stationeers/server.json`, `stationeers/saves`, writable terrain defaults |
| Valheim | 4 GiB / 2 cores | 2456 game, 2457 query | `valheim/server.json`, `valheim/saves` |
| Palworld | 16 GiB / 4 cores | 8211 | `pal-saved/Config/LinuxServer/PalWorldSettings.ini`, `pal-saved/SaveGames` |

Valheim's ports must be consecutive. Its blank default password generates and privately retains a server password. Palworld uses the selected port in its actual launch command; REST/RCON stay off by default. Stationeers' terrain-only directory is moved into writable storage; executable/library directories remain read-only. Native profiles use the existing 180-second stop grace period for world loading/saving.

Plan disk space for downloads, game files, writable terrain, runtime cache and backups. The recipes' staging recommendations total about 75 GiB for the three games. Bfsm's last observed 3.7 GB free is insufficient; this package does not resize disks or delete existing data.

## Verification and remaining operator checks

Actual rootless Podman acceptance covered all three official SteamCMD installations, a cold HTTPS runtime import, non-root/read-only/no-capability confinement, managed settings read/save, restart and clean stop. Actual downloaded game layouts, image filesystem layers and a zero HIGH/CRITICAL vulnerability/secret scan bind the signed review. The compiled Host archive was independently checked for dependencies, safe paths, source exclusion and Linux script bytes. The guarded updater passed 23 real-archive/disposable-files checks; only systemd actions were simulated.

Encrypted backup creation passed. **Restore/rollback, remote player joins and longer gameplay remain operator acceptance gates.** Downloaded-software profiles currently have no approved data-tree restore target; this package does not bypass that refusal or claim six-check Forge stable-release approval. No bfsm game installation, disk change, account change, pairing change or Agent update was performed during package preparation.

Private hosted CI did not start because GitHub reported account billing/spending limits. No checks or billing settings were changed; the controlled-testing review uses the existing isolated Linux artifact-verification path.
