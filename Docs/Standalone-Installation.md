# Linux installation and first game server — Test 28

The public administrator bootstrap is for Debian/Ubuntu x86_64 with systemd. The panel runs as `bifrost` in rootless Docker; games run as the separate `bifrost-games` account in rootless Podman. Administrator authentication prepares OS prerequisites once; neither application nor Agent runs as root. Use the release-pinned, checksum-verified Debian or Ubuntu command on the [testing installation page](https://therealmsofasgard.com/gaming-hub/bifrost-server-manager#testing-installation).

## Independent standalone machine

1. Install with `--instance`. Keep the terminal open through **Local Host prepared**. Default panel HTTPS is `https://YOUR-HOST:8443/install`. Verify the server's generated public certificate before trusting it in a browser.
2. Select **Run independently**. Create the first administrator, configure MFA and save recovery codes. Review the platform terms/disclosure, then activate the free license. In an installation-test build, separately authorize the disclosed testing check-ins when requested; analytics remains optional and off.
3. At **Connect your hosts**, approve the isolated local Host and the bundled signed game catalog, then select **Set up local Host**. No pairing code, external master membership or copied Host command is needed for this prepared standalone path.
4. Wait for **Local Host online · reviewed catalog approved**. This requires the real Agent's authenticated heartbeat; an enrollment request alone is not readiness. If you entered the panel early, the same completion step remains under **Hosts → Local Host setup guide**. On an Instance, **Add host** also opens this automatic setup/status; manual pairing is offered only when no automatic Host was prepared.
5. Open **Blueprints → Ready to install → Choose a host and install**, or **Game servers → Create instance**. Choose a reviewed recipe, online compatible Host, resources and game ports. Review that game's terms, preview placement, provide a meaningful creation reason of at least 8 characters, confirm and create it. Draft/candidate definitions cannot be accepted into an executable catalog from the browser.
6. Follow the installation job until readiness, then test the player connection. An online panel/Host or startup marker alone does not prove a player can join.

## Capacity and player access

Torch requires 6 GiB game RAM, 3 CPU reservations and 20 GiB free game-data storage plus a 0.5 GiB margin. Panel/runtime resources are additional. The fresh Host defaults reserve about 80% of machine memory/CPUs; a small VM may have insufficient Host policy capacity. Check the creation screen's effective limits and free-space report. These are safety requirements, not claimed current disk usage. Thin-provisioning the virtual disk does not increase the guest filesystem automatically.

Game ports are operator choices. Torch defaults remain UDP 27016 (game) and 8766 (Steam); 2750 is one site's selection, not a global requirement. The selected Torch game port is used internally and on the Host. Players connect to the Host's LAN IP and chosen game port. Allow additional disk for runtime image cache and extraction, beyond the game storage floor. Remote players need its public address and a matching router/firewall forward; panel HTTPS does not transport game UDP. Keep the Agent/database private.

## Connecting to a separate Controller

Choose **Connect to a Controller** only if a fleet administrator supplies that panel's HTTPS address. Verify its Node ID/signing identity, activate this Instance's own license, then use a fresh one-time code from that Controller's **Hosts → Add host**. The parent administrator approves the connection request. The prepared worker completes the signed join and starts its Agent after approval. Create games in the parent panel after the heartbeat. The TROA licensing-service URL is not the fleet pairing address.

## Manual / remote Host-only installation

Use `--host` as a dedicated non-root game-service account with a protected Node.js 24 executable, rootless Podman, subordinate IDs and a working user systemd bus. It installs no panel. The downloadable x86_64 catalog has no arm64 game recipes; do not infer game support from generic Agent architecture support.

Use the matched checksum-pinned Host command shown by this release's panel. `curl` is available from administrator bootstrap. A custom protected runtime can be selected with `BIFROST_NODE_BIN=/absolute/path/to/node`; it must be Node 24. Do not run the Agent as root, share the panel Docker account/socket, or grant the game account sudo.

Account/path preflight runs before connection prompts. Enter the exact panel HTTPS origin (including its port). Certificate trust and Controller identity are checked before the five-digit Host code is requested; this is separate from six-digit MFA. For a self-signed Controller, securely obtain its **public** certificate PEM, provide its path at the CLI prompt, and compare its SHA-256 fingerprint independently on the panel server. Do not supply a private key or disable TLS verification. Enrollment and the ongoing Agent retain that certificate trust. System-trusted HTTPS can leave the certificate prompt blank. The prompt needs a readable local file path (for example `/home/game/panel-cert.pem`), never the panel URL. The standard panel public certificate is `/home/bifrost/.local/share/bifrost/secrets/panel-cert.pem`; its directory is private, so the panel administrator must provide only this public PEM copy to the game-service account using their authenticated administration channel. Compare `openssl x509 -in PATH-TO-PUBLIC-PEM -noout -fingerprint -sha256` on the panel and game machine. Never copy `panel-key.pem`. A filename alone does not establish trust; the independently verified fingerprint must match, and the HTTPS address must match the certificate hostname/IP.

Explicitly approve the bundled signed catalog in the terminal to enable game creation; skipping it leaves an enrolled monitoring-only Host. Existing policy and game profiles are preserved instead of replaced. A Controller/Hybrid remote request also needs that Controller administrator's acceptance. Codes expire after ten minutes and are one use; a saved pending request/receipt must be resumed rather than discarded.

## Diagnose / recover without wiping

The prepared local services run as `bifrost-games`. A VM administrator can inspect them without granting that account sudo:

```bash
su -s /bin/bash -c 'cd /; games_uid=$(/usr/bin/id -u bifrost-games); /usr/sbin/runuser -u bifrost-games -- /usr/bin/env HOME=/home/bifrost-games XDG_RUNTIME_DIR=/run/user/$games_uid DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$games_uid/bus /usr/bin/systemctl --user --no-pager status bifrost-instance-setup.service bifrost-host-agent.service' root
```

On Ubuntu, an administrator may use `sudo` for this OS/account invocation; that does not run the Agent itself as root. Use the same account environment with `journalctl --user -u bifrost-instance-setup.service -u bifrost-host-agent.service --no-pager -n 60` for diagnostics. Preserve secrets, receipts, ledgers and worlds. Never post credentials or full config files.

Ubuntu 24.04 namespace restrictions are handled by a path-specific profile for `/home/bifrost/bin/rootlesskit`. Global AppArmor/sysctl protection remains enabled. A differing existing profile is preserved for administrator review. The bootstrap diagnoses unavailable rootless/user-systemd prerequisites instead of disabling protections.

Use the matched updater for panel updates. Existing Host policy is not silently changed; enrolled Host upgrades need their supported preserved-state path. `--resume-local-host --upgrade` is only for prepared **unenrolled** automatic services. A full wipe is a separate destructive operation with review and `WIPE ALL`; ordinary reinstall is not a clean Host/database reset. See the public reset guide for incomplete versus enrolled setup. Bifrost does not provision hypervisor VMs; Windows public installation remains preview.

## Verification scope

Test 28 verification is recorded with the release's source provenance and acceptance evidence. Runtime checks and synthetic fixtures are distinguished from clean distro installation and real vendor/player acceptance. Earlier release assets remain immutable.
