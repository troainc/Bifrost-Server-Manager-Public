# Bifrost Server Manager

## Current testing download

[Customer testing 6](https://github.com/troainc/Bifrost-Server-Manager-Public/releases/tag/v0.1.0-installtest.6) is being verified for disclosure version 5 and the current Controller features. It includes the compiled Controller, bundled public verification key, image scan/checksum evidence and a separate compiled Linux Host Agent ZIP. The previous testing bundle passed disposable Compose verification; this refreshed bundle requires its own hosted checks before publication. real installation, host enrollment and game/backup/recovery acceptance remain pending. The Host Agent ZIP is an unsigned testing build: extract it and follow INSTALL.md on your own game machine.

## Linux install

The automatic **Controller installer currently supports Debian and Ubuntu on x86_64**. Its host-preparation step checks the distribution and uses Debian/Ubuntu package tools. Containerized application code does not make that bootstrap script portable to every Linux distribution.

The separate **Linux Host Agent** has no distribution-name restriction, but requires Node.js 24 at `/usr/bin/node`, a working systemd user manager and rootless Podman under the unprivileged account that owns the games. Other Linux distributions are compatibility candidates when those prerequisites exist; record the exact distribution/version during installation, enrollment and game tests before claiming support. Systems without systemd do not meet the current agent requirements. An Ubuntu test is one useful acceptance target, not evidence that every Linux system works.

Run this as your current VM user. The installer requests the administrator password once, creates the unprivileged bifrost account, and continues automatically:

```bash
wget --output-document=install.sh https://github.com/troainc/Bifrost-Server-Manager-Public/releases/latest/download/install.sh && bash install.sh
```

The wizard asks for the VM IP/hostname and HTTPS port, downloads the application, checks its checksum, generates configuration and credentials, and starts the panel. Default port: **8443**. Create your administrator in the browser.

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

The installer follows the single-command shell wizard pattern described by [CubeCoders AMP](https://cubecoders.com/AMP/Install); it contains original Bifrost code.

## 2026-10-02 — Automatic non-root prerequisites
install.sh now downloads rootless Docker 29.8.2 and Compose v2.39.4 automatically, starts the user service, and downloads/extracts missing Python, OpenSSL and iptables packages under the user's home using Debian/Ubuntu package sources without APT installation or sudo. It saves the Docker environment for subsequent logins and includes the TROA welcome/support/project message. System UID mapping helpers, assigned subordinate ID ranges, enabled user namespaces, package indexes and an active user systemd login must exist in the VM image; missing requirements are listed precisely. Unattended operation requires user lingering provisioned in that image. This is not a claim of zero host prerequisites or completed clean-VM acceptance.



## 2026-10-02 — Dedicated service account
The explicit --prepare-account mode performs only administrator-owned account preparation: creates bifrost with its own group and initially locked password, checks UID and privileged memberships and sudo policy, protects its home and enables user lingering. It refuses an existing privileged account without altering its groups or grants. Set a login password with passwd bifrost and log in directly as bifrost. Normal installation now requires bifrost and rejects sudo/wheel/docker/lxd/incus-admin membership and discoverable sudo grants. Application installation and services remain non-root; administrator preparation does not install or run the application. Bash syntax checked; real VM account acceptance pending.


## 2026-10-02 — Automated VM bootstrap (supersedes manual preparation)
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

## 2026-10-03 — Customer licensing setup

- Fresh installs now offer an explicit optional licensing-connection step, with https://bifrost.therealmsofasgard.com/api as the suggested TROA endpoint. Supply the matching issuer public PEM file obtained through a trusted channel; no issuer private key or owner credential is needed or accepted. Skipping leaves management gated until licensing is configured.
- Installer and updater validate the HTTPS root or /api URL and the issuer P-256 public key before replacing license settings. Invalid URLs, private keys, missing/oversized keys and wrong curves preserve the previous license URL/key. Other environment settings, including privacy-review fields, are preserved. This checks key type, not that the operator obtained the correct trusted issuer key.
- Three focused test groups passed across both embedded configuration paths (valid setup, eight invalid endpoints and four invalid-key inputs); both Bash syntax checks passed. Tests used disposable files and generated test keys. Initial Git OpenSSL/Bash execution was blocked by the Windows sandbox runtime; the same isolated checks passed outside it. No installer was run, public release uploaded, customer VM changed or live activation accepted. These changes are local on codex/customer-license-setup-20261003 and require packaging/release verification.

## 2026-10-03 - Hosted installer checks

- Added a read-only pull-request/manual workflow checking install.sh and update.sh syntax and the disposable licensing configuration tests on Ubuntu. It does not install Bifrost, publish packages, access issuer credentials or modify customer machines. Draft PR #1 remains unmerged. Hosted Ubuntu run 37134758662 at 7e5fa0c passed both shell syntax checks and all three licensing configuration test groups across installer/updater paths; this is not a customer installation or live activation test.

The patched Debian 12 PostgreSQL image still reported 16 CRITICAL and 102 HIGH findings without available fixes. The new customer testing bundle uses patched Alpine PostgreSQL 17 under its non-root postgres account. This changes libc/locale and runtime ownership; old Debian bundles are therefore refused by the updater before download or file/database mutation. A fresh installation or independently verified backup/restore migration is required. New Alpine installations carry BIFROST_POSTGRES_RUNTIME=alpine17-v1. The existing master database/runtime is unchanged. Clean-host and game acceptance remain deferred.
