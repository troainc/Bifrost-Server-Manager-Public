## Publisher catalog packaging (prepared for a future release)

The bundle builder accepts optional arguments 4/5: a reviewed public catalog directory and its independently approved publisher key ID. It verifies the publisher's signed handoff binding the exact catalog/trust bytes, then copies only three public JSON files into the new build tree. Existing installations are never edited by the builder. Controller and Host independently verify each recipe before execution. Testing 9 remains the current download and its reviewed real-game catalog is still pending.

# Customer testing 9: automatic download and create

This release updates the compiled Controller/web and separate Linux Host Agent with signed official-source download recipes and automatic new-instance creation for approved Space Engineers, Palworld and Minecraft targets. Choose the reviewed game/version and enrolled Host, accept required terms, preview placement, then Create. The Host verifies downloads and readiness before registering a separate instance.

A package update alone does not make an unsigned game choice install-ready. Actual reviewed runtime images, signed game recipes/catalogs and independently matching Host policy are required; real vendor-game acceptance remains pending. No synthetic test game is included. Windows public distribution/signing and runtime isolation review are separate and are not included here.

Testing 9 preserves compatible Alpine PostgreSQL 17 installations, keys, accounts, data and the existing provisioning catalog/trust on update. Earlier Debian database runtimes remain refused before mutation. Existing Hosts need their own Agent update; updating the Controller does not silently upgrade Hosts.

# Bifrost Server Manager

## Current testing download

**Testing 10 is in preparation and has not been published.** It will deliver the newly merged download/launcher corrections and verified catalog handoff in matched Controller/Linux Host packages. The signing identity and final package verification are still pending. Continue using the published release below until the new assets are verified.

[Customer testing 9](https://github.com/troainc/Bifrost-Server-Manager-Public/releases/tag/v0.1.0-installtest.9) is published from compiled source fde5104 and installer/environment source 00514eb. It includes the automatic download/create engine, Controller/web/database, matching installer/updater, public license key, image scans/checksums and the updated compiled Linux Host Agent. [Hosted verification](https://github.com/troainc/Bifrost-Server-Manager/actions/runs/37273201450) passed customer/issuer isolation, three zero HIGH/CRITICAL scans and fresh HTTPS migrations/setup. All eleven published asset digests and five anonymous latest downloads match. Reviewed game recipes/runtime images and actual vendor-game acceptance remain pending.

Space Engineers vanilla/Torch, Palworld dedicated/community and Minecraft Java/Paper/Fabric/Forge/NeoForge/Bedrock are available for Host-approved package review. Each needs exact reviewed local software, service/runtime policy and real game testing. Accepted public one-click downloads, automatic Windows service creation and signed Windows distribution remain separate. Updating the Controller does not update an installed Host Agent automatically. The downloaded compiled preparer was checked independently using synthetic SE/Minecraft manifests; this does not run or accept a real game.

## Linux install

The installer asks for the machine's role before installation:

| Role | Purpose |
| --- | --- |
| Controller (`--controller`) | Management panel/API/database; one per fleet |
| Instance Host (`--host`) | Host Agent on a game machine; joins your Controller and can run one or more servers |

A **game instance** is one game server created later in the Controller panel, after Host enrollment and reviewed game-policy approval. For a single game server, use one Controller and one enrolled Host. On one physical machine, install the Controller first, then run `--host` under a prepared non-root game account with Node.js 24, rootless Podman and user systemd. A Host-only install joins an existing Controller; it does not create a separate management panel. The role choice does not determine the number of game instances.

The automatic **Controller installer currently supports Debian and Ubuntu on x86_64**. Its host-preparation step checks the distribution and uses Debian/Ubuntu package tools. Containerized application code does not make that bootstrap script portable to every Linux distribution.

The separate **Linux Host Agent** has no distribution-name restriction, but requires Node.js 24 at `/usr/bin/node`, a working systemd user manager and rootless Podman under the unprivileged account that owns the games. Other Linux distributions are compatibility candidates when those prerequisites exist; record the exact distribution/version during installation, enrollment and game tests before claiming support. Systems without systemd do not meet the current agent requirements. An Ubuntu test is one useful acceptance target, not evidence that every Linux system works.

Run this as your current VM user. The installer requests the administrator password once, creates the unprivileged bifrost account, and continues automatically:

```bash
wget --output-document=install.sh https://raw.githubusercontent.com/troainc/Bifrost-Server-Manager-Public/main/install.sh && bash install.sh
```

The wizard asks for the VM IP/hostname and HTTPS port, downloads the application, checks its checksum, generates configuration and credentials, and starts the panel. Default port: **8443**. Create your administrator in the browser.

Testing 7's repository bootstrap and release installer both include the Controller/Instance Host selector. Its first interactive step asks for the machine role: choose **Bifrost Controller** once; choose **Linux Instance Host** on each game machine. You can also pass `--controller` or `--host`. From the Controller, create a fresh one-use code under **Hosts â†’ Add host**. Host setup verifies and installs the matching Host Agent package and asks for the Controller panel HTTPS URL and code. It requires Node.js 24, rootless Podman, and systemd user services under the regular game operator account. The licensing service URL is different from the Controller URL. Enrolling a host does not install a game; use an approved signed executable Blueprint separately. The catalog starts empty; metadata candidates and drafts do not authorize installation.

The matched testing 7 installer/updater recognize Docker's classic and containerd image identities only when they match the checksummed archive and locked configuration. Earlier testing 6 attachments remain unchanged.

If a compatible Alpine installation stopped after writing configuration with `Image identity mismatch`, preserve it and use `bash install.sh --update` with the current verified bootstrap. The updater preserves the database, administrator, credentials, license URL/public key, testing-intake choice and provisioning catalog/trust. Press Enter at configuration prompts to retain settings. Do not use `--reinstall` or delete the installation to recover this failure. Older Debian PostgreSQL runtimes are refused before mutation and require a separately verified backup/restore migration.

Use Debian/Ubuntu x86_64 with wget or curl. The installer sets up Docker, Compose and missing Python/OpenSSL/iptables tools in your user account. Host preparation installs required system packages with administrator authentication. The Controller and rootless Docker services run as the separate unprivileged bifrost account; administrator preparation does not run the application as root.

The application is delivered as compiled container images inside a GitHub Release asset. No private registry login, private application source, or master licensing service is distributed. The repository-root `install.sh` is the bootstrap; GitHub's `releases/latest/download/install.sh` is a release asset, not a folder in the repository.

This is a VM installation test release. HTTPS uses a generated self-signed certificate. The new testing bundle includes the TROA issuer public verification key. The installer suggests the TROA HTTPS licensing endpoint; you still accept the tracking disclosure in your own panel. You can explicitly choose license testing while your deployment review is pending. Optional analytics stays unavailable until the normal review gate is complete. Privacy review fields are left unset until configured; installation does not invent a legal review.

Files live in `~/.local/share/bifrost`. Existing installations are preserved.

```bash
cd ~/.local/share/bifrost
# Status
docker compose ps
# Logs
docker compose logs --tail 100
# Stop / start
docker compose stop
docker compose up -d
```

## 2026-10-02 â€” Automatic non-root prerequisites
install.sh now downloads rootless Docker 29.8.2 and Compose v2.39.4 automatically, starts the user service, and downloads/extracts missing Python, OpenSSL and iptables packages under the user's home using Debian/Ubuntu package sources without APT installation or sudo. It saves the Docker environment for subsequent logins and includes the TROA welcome/support/project message. System UID mapping helpers, assigned subordinate ID ranges, enabled user namespaces, package indexes and an active user systemd login must exist in the VM image; missing requirements are listed precisely. Unattended operation requires user lingering provisioned in that image. This is not a claim of zero host prerequisites or completed clean-VM acceptance.



## 2026-10-02 â€” Dedicated service account
The explicit --prepare-account mode performs only administrator-owned account preparation: creates bifrost with its own group and initially locked password, checks UID and privileged memberships and sudo policy, protects its home and enables user lingering. It refuses an existing privileged account without altering its groups or grants. Set a login password with passwd bifrost and log in directly as bifrost. Normal installation now requires bifrost and rejects sudo/wheel/docker/lxd/incus-admin membership and discoverable sudo grants. Application installation and services remain non-root; administrator preparation does not install or run the application. Bash syntax checked; real VM account acceptance pending.


## 2026-10-02 â€” Automated VM bootstrap (supersedes manual preparation)
Run the normal one-line installer as the current VM user. It requests administrator authentication using sudo, or su when sudo is unavailable/denied, prepares Debian/Ubuntu system prerequisites and nf_tables, creates/checks the non-privileged bifrost account, enables lingering and starts its user manager, then drops privileges with runuser and continues automatically. New service accounts have locked passwords; no passwd command or manual SSH switch is needed. The legacy --prepare-account option now invokes the same complete bootstrap. Existing installations and privileged account memberships remain fail-closed. Only host preparation is elevated; application setup/runtime remain non-root. Bash syntax passed; clean VM end-to-end acceptance pending.



2026-10-02: Set the administrator bootstrap PATH explicitly to include /usr/sbin and /sbin. Fixes modprobe command not found after successful package preparation when elevation inherits a normal user PATH. Shell syntax passed; VM retry pending.

2026-10-02: Fixed sudo -l exit-status false positive. Account preparation installs an explicit bifrost ALL=(ALL:ALL) !ALL policy validated with visudo, checks listed command permissions for conflicting grants, and retains privileged-group rejection. Existing bifrost account is reused. Shell syntax passed; real VM retry pending.

2026-10-02: Handle null Docker IPAM Config during subnet selection. Added --resume for an interrupted install before .env creation: require existing package/credentials and ownership, retain credentials, skip redownload and credential generation, continue configuration. Completed installations remain protected. Bash syntax passed; VM retry pending.

2026-10-02: v0.1.0-installtest.2 includes current customer onboarding UI. Added update.sh with checksum/image checks, configuration backup, preserved volumes/secrets and optional HTTPS licensing URL/public-key configuration. Compose now mounts the license verification key. License connectivity is pending the real reachable licensing-service endpoint and matching key; localhost:8081 is the master panel, not the remote VM's license server. Backend code is unchanged from the preceding packaged build. Shell/build validation passed; VM update acceptance pending.

2026-10-02: Corrected updater administrator PATH to include /usr/sbin and /sbin before runuser. Checks runuser availability explicitly. Fixes Debian su inheritance causing exec: runuser: not found before any application update. Bash syntax passed; VM retry pending.

2026-10-02: Linux test release v0.1.0-installtest.3 refreshes customer UI and installer/updater. install.sh --update downloads the release updater and verifies its checksum before preserving-data update. Master configuration UI/service settings remain private, excluded from customer builds. Existing VM: download current install.sh and run bash install.sh --update. Fresh VM: bash install.sh. Localhost API and UI restarted.

2026-10-02: Styled installer/updater terminal presentation: TROA banner, readable numbered sections, cyan/gold/green status output, progress-bar downloads, health-based task completion and concise final panel summary. NO_COLOR, non-TTY and dumb terminals use plain text. Package/image/service output is captured in mode-private temporary logs, retained with a diagnostic tail on failure. No fabricated progress percentages; underlying installation/update semantics preserved. Bash syntax passed; live VM presentation acceptance pending.

2026-10-02: Added explicit --reinstall for the requested disposable TROA VM reset. Requires typed WIPE, validates the standard canonical user-home target and ownership/configuration, then removes that Compose stack including volumes and its installation directory before reinstalling. Other locations and symlinked targets refused. This destroys the test panel database/admin/credentials; --update continues to preserve them. No VM wipe was executed remotely.

2026-10-02: Fresh install/reinstall completion URL always ends in /install and opens the existing first-run onboarding route.

2026-10-02: Corrected the installer welcome-banner project URL to therealmsofasgard.com. Bash syntax passed.

2026-10-02: v0.1.0-installtest.4 customer UI includes five-step onboarding and redesigned License & privacy activation/disclosure/status panel with explicit connection and MFA errors. Licensing/consent gates preserved. No master configuration UI is distributed. Existing data preserved with --update; --reinstall requires typed WIPE and resets test data.

## 2026-10-03 â€” Customer licensing setup

- Fresh installs now offer an explicit optional licensing-connection step, with https://bifrost.therealmsofasgard.com/api as the suggested TROA endpoint. Supply the matching issuer public PEM file obtained through a trusted channel; no issuer private key or owner credential is needed or accepted. Skipping leaves management gated until licensing is configured.
- Installer and updater validate the HTTPS root or /api URL and the issuer P-256 public key before replacing license settings. Invalid URLs, private keys, missing/oversized keys and wrong curves preserve the previous license URL/key. Other environment settings, including privacy-review fields, are preserved. This checks key type, not that the operator obtained the correct trusted issuer key.
- Three focused test groups passed across both embedded configuration paths (valid setup, eight invalid endpoints and four invalid-key inputs); both Bash syntax checks passed. Tests used disposable files and generated test keys. Initial Git OpenSSL/Bash execution was blocked by the Windows sandbox runtime; the same isolated checks passed outside it. No installer was run, public release uploaded, customer VM changed or live activation accepted. These changes are local on codex/customer-license-setup-20261003 and require packaging/release verification.

## 2026-10-03 - Hosted installer checks

- Added a read-only pull-request/manual workflow checking install.sh and update.sh syntax and the disposable licensing configuration tests on Ubuntu. It does not install Bifrost, publish packages, access issuer credentials or modify customer machines. Draft PR #1 remains unmerged. Hosted Ubuntu run 37134758662 at 7e5fa0c passed both shell syntax checks and all three licensing configuration test groups across installer/updater paths; this is not a customer installation or live activation test.

The patched Debian 12 PostgreSQL image still reported 16 CRITICAL and 102 HIGH findings without available fixes. The new customer testing bundle uses patched Alpine PostgreSQL 17 under its non-root postgres account. This changes libc/locale and runtime ownership; old Debian bundles are therefore refused by the updater before download or file/database mutation. A fresh installation or independently verified backup/restore migration is required. New Alpine installations carry BIFROST_POSTGRES_RUNTIME=alpine17-v1. The existing master database/runtime is unchanged. Clean-host and game acceptance remain deferred.

## Fleet provisioning testing release 7

Testing 7 is published and verified; earlier release assets remain unchanged. The compiled Agent upgrade path stages a versioned package, validates current profiles/jobs, preserves credentials and game data, and restores the old unit after failed service validation. Use `bash install.sh --host --upgrade` on an enrolled Linux Host after draining/reconciling active jobs. `--re-enroll` additionally requires revoking the old Host, explicit confirmation and a fresh code from the same Controller. Signed generic Linux OCI provisioning and failure tests passed; real games, Windows provisioning and automatic VM creation are separate acceptance or future work.

Customer Compose mounts `config/provisioning-catalog.json` and `config/provisioning-trust.json` read-only. Defaults are empty: descriptive Steam/Blueprint drafts cannot execute. An operator must install reviewed signed definitions/public publisher keys in the Controller and independently approve them on each Host through packaged `dist/configure-provisioning.js`. Publisher private keys stay offline. Never edit a Host config while the Agent is running; stop it, validate the private policy/catalog, preserve the backup key, then restart. No VM provisioning or universal Linux/game support is implied.
