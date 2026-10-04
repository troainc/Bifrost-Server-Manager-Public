# Changelog

- 2026-10-04: Repair configuration-versus-manifest image identity checking in both standalone scripts. Derive portable configuration locks from the saved archive. Bind accepted OCI manifest IDs to hashed archive metadata and the exact locked configuration; keep rejection of other IDs. Add negative regression cases and an actual testing 6 package/Docker 29 classic/containerd reproduction workflow. Recover a prepared Alpine testing 6 installation through the corrected preserving-data updater rather than another wipe. Published testing 6 attachments remain unchanged; use the current repository bootstrap. Hosted reproduction evidence is pending.

- 2026-10-03: Published v0.1.0-installtest.6 with the current agreements, compiled customer isolation, patched dependency runtime, matched public signing key, three image scan reports and a separate Linux Host Agent ZIP. Final merged hosted bundle and anonymous latest download/checksum verification passed. Real host/game acceptance remains pending.

- 2026-10-03: Clarify separate Linux support boundaries for the automatic Debian/Ubuntu x86_64 Controller installer and the prerequisite-based Linux Host Agent. Record distro/version-specific tests before claiming broader support.

## 2026-10-02
- Rebuilt Linux QuickStart as a single bootstrap script and short interactive wizard.
- Bundled application images in release assets instead of depending on private GHCR visibility.
- Added generated HTTPS for VM setup and image checksum/identity verification.
- Preserved non-root installation and existing data.

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

## 2026-10-03 - Customer testing release preparation

Version v0.1.0-installtest.5 adds a compiled-image bundle builder, defaults to the bundled TROA P-256 verification public key when licensing setup is chosen, and lets the local operator explicitly enable license testing while review details remain pending. Normal template remains BIFROST_LICENSE_TEST_INTAKE=false. Optional analytics, owner administration and private issuer/source are not enabled or distributed. The PostgreSQL image stays on major 17, versioned with the bundle. Updates preserve existing keys, accounts, secrets, review facts and testing setting unless explicitly changed. No Ubuntu/game-host acceptance claimed. Three disposable license-setup test groups and Bash syntax passed; hosted packaging, image scans, public release and actual host tests remain pending.

The patched Debian 12 PostgreSQL image still reported 16 CRITICAL and 102 HIGH findings without available fixes. The new customer testing bundle uses patched Alpine PostgreSQL 17 under its non-root postgres account. This changes libc/locale and runtime ownership; old Debian bundles are therefore refused by the updater before download or file/database mutation. A fresh installation or independently verified backup/restore migration is required. New Alpine installations carry BIFROST_POSTGRES_RUNTIME=alpine17-v1. The existing master database/runtime is unchanged. Clean-host and game acceptance remain deferred.

## 2026-10-03 - Published customer testing download

v0.1.0-installtest.5 was published at 19:02:06Z: https://github.com/troainc/Bifrost-Server-Manager-Public/releases/tag/v0.1.0-installtest.5 . Hosted build run 37146002967 verified compiled issuer/source isolation, three zero HIGH/CRITICAL vulnerability and secret scans, actual bundled fresh database migrations and first-admin setup over verified disposable HTTPS, and a separate Linux Host Agent archive without application source maps. The downloaded build artifact digest and all 11 uploaded release asset digests were checked; anonymous latest installer and SHA256SUMS match. Bundled public issuer key is readable by the non-root Controller.

This is a fresh-install testing download. Home Ubuntu installation, enrollment, game lifecycle, backup/recovery and failure acceptance remain for the owner to perform. Linux Host Agent is unsigned testing only. Earlier Debian database runtimes are refused by the updater before mutation; use a fresh install or separately verified backup/restore migration. No private issuer, private application source, credentials or private signing keys are distributed.

## 2026-10-03 - Disclosure v5 customer integration refresh

Prepare v0.1.0-installtest.6 for the creator's current Controller features and disclosure version 5. Personal user agreement acceptance is separate from administrator installation-license consent. The customer Controller cannot enable owner registry/configuration/recovery APIs, even through environment flags. Customer privacy identity and location belong to the local operator and default blank. The Alpine 17 update compatibility guard and data/key preservation remain unchanged. Hosted packaging, fresh migrations, image scans and licensing flow must pass before publishing; real Ubuntu and game-host acceptance remain pending.
