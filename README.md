## 2026-10-08 - Testing 19 workflow candidate

The tester's newer Host 816f7f1b-0520-4251-835b-884e798cb50a now reports heartbeats. Its Torch instance 755552ce-a981-41c6-9227-62821bd9ddd6 remains uncertain under job a3e07272-7cea-4287-91ca-5114a5d4927c. The older never-reporting Host is a separate stale enrollment, not a reason to repeat onboarding. Authenticated master and Bifrost-only Coolify inspection verify testing 18 deployment; Controller request logs establish the job identity but do not establish its failure cause. No production Host credential, job, reservation or game was changed.

This candidate keeps named provisioning jobs visible in Activity and Recent installations before an Agent profile is reported, shows permission-scoped diagnostics and stable references, and adds specific expired/heartbeat/catalog/resource/port/recovery preview refusals. The review displays expiry, offers an explicit new preview and resets confirmation after rejection. Host and game display names are audited Controller metadata; game aliases survive empty/replacement heartbeats without changing hostname, UUID, profile, paths or credentials. Revoke accepts online or database-stale Hosts and uses an explicit identity/reason/confirmation form. Uncertain jobs and reservations remain preserved.

The matched Agent reports bounded installation phase/code diagnostics without forwarding child stderr, URLs, paths or credentials. Legacy receipts remain accepted only under the existing exact identity/digest/version and execution-evidence checks. Unverified outcomes remain uncertain. The public read-only diagnose-provisioning.mjs helper inspects the existing bifrost-games configuration, ledger, retained manifest and fixed runtime/installer container names; it does not print tokens, environment or commands and cannot reset, retry or delete.

Full build/typecheck, five Controller contract tests, public diagnostic redaction checks and 28 Node 24/least-privilege PostgreSQL HTTP/database checkpoints passed. Isolated compiled UI browser checks verify names, stale revocation validation, visible uncertain jobs, expired-preview refresh, specific recovery refusal and reset confirmation; desktop and 390-pixel layouts fit their viewports. These synthetic UI diagnostics are not the tester's actual failure. A compiled non-root receipt regression and matched package/image/HTTPS verification remain pending at this entry, as do release publication, current production rollout and actual Torch/vendor/VM acceptance. No reinstall, pre-join recovery, blind retry, paid service or billing change.

## 2026-10-08 - Testing 18 published; approved automatic Host recovery verified

Published [testing 18](https://github.com/troainc/Bifrost-Server-Manager-Public/releases/tag/v0.1.0-installtest.18) from private compiled source 4c16d8f65ec9bbf87cbcd1481b5116e93665be1f and public packaging source 9ff6857c780b645769c217e7e6ee80018f4d812f. All 25 uploaded asset sizes/digests and twelve cookie-free release downloads matched; the immutable public installer matches the release. Installer SHA256 is 1d57696892fb0a38a37b00b2783fccf286cc3f41359a57c17a97cf9cf397b2e1. Updater source remains pinned to 8d013df35f94e9ea8997aa025313fc97f2e2592a, SHA256 fece4382431c35556ed6751f7fed8b16cdb1471dbdfd9c0907da790d6f70463f. Earlier assets and contributor histories are preserved.

The redacted tester diagnostic confirmed an approved request with no automatic setup ticket and no Host config/token/receipt/ledger. Fresh requests now retain their encrypted ticket regardless of bootstrap preparation timing. Private-capability POST recovery reuses the same still-approved fresh request under authority/row locks, preserving the master's issued Host credential; concurrent recovery returns one saved ticket. GET remains read-only. Existing Host files, paired nodes and unresolved jobs refuse recovery.

Full build/typecheck, 42 normal installer checks, three separately executed disposable-root bootstrap checks, three non-root managed-service upgrade checks, 25 exact packaged HTTP/database checkpoints, compiled non-root signed join/handover/TLS/recovery and authenticated first-heartbeat fixtures, six signed catalog checks and fresh verified loopback HTTPS setup passed. All three final image scans have zero HIGH/CRITICAL findings or detected secrets and are bound through archive identities to the shipped image locks. Unchanged Torch runtime evidence is explicitly reused from testing 15 and unchanged responsive UI evidence from testing 17; this release does not claim fresh visual browser acceptance.

For this prepared pre-join VM, use the matched installer's --update followed by root --resume-local-host --upgrade. The update preserves panel data/accounts/keys/TLS/bootstrap; the explicit Host mode validates both fixed service templates, backs up their bytes and changes only the matched package paths before restarting setup. bifrost and bifrost-games remain separate non-root service accounts. No wipe, parent re-enrollment, game/EULA acceptance, paid service or billing change is needed. Actual inaccessible tester VM/systemd/heartbeat/game acceptance remains pending. Master production rollout was not verified during this recovery release; source/release verification alone is not deployment evidence. These documentation commits do not change the compiled release identity.

## 2026-10-08 - Approved automatic Host ticket recovery candidate

The tester's redacted diagnostic confirms local HTTPS 200, approved request, correctly protected bootstrap, no saved setup ticket and no Host configuration/token/receipt/ledger. Testing 17 persisted the encrypted automatic ticket only if VM Host preparation was already enabled at browser submission. Fresh joins now retain that ticket regardless of preparation timing; same-request retries preserve it. The worker uses an explicit private-capability POST to recover a missing ticket for the same still-approved, incomplete fresh request. Recovery is locked, audited and idempotent, preserves the parent approval, Host credential and machine identity, and refuses paired nodes, existing local Hosts or unresolved jobs. GET diagnostics remain read-only. Existing Host files/receipts are not overwritten, and the worker refuses ticket recovery when a Host configuration exists.

Preparing matched testing 18 with the earlier release-version, administrator PATH and neutral-working-directory fixes. Its explicit root --resume-local-host --upgrade mode updates only prepared pre-join managed service package paths after validating both fixed templates and preserving prior unit bytes; it refuses existing Host enrollment/job state. The panel updater preserves database, administrator, keys, TLS and bootstrap capability. No panel wipe, parent re-enrollment, credential rotation or service-account privilege grant. Local build/typecheck, isolated HTTP/database and non-root signed join/first-heartbeat regressions are the evidence; release packaging/publication and inaccessible tester VM acceptance remain separate pending steps. Six reviewed Java/Torch Wine recipes and vendor terms gates are unchanged. No paid services or billing changes.

## 2026-10-08 - Read-only automatic Host diagnostics

The tester's Instance reports approval received but automatic setup needs attention; the journal contains only the deliberately generic worker error. Added scripts/diagnose-local-host.mjs to inspect private bootstrap/config/receipt/ledger presence and ownership, then GET the exact local HTTPS setup endpoint with its existing capability and pinned public certificate. It prints only HTTP status, allowlisted stage and ticket/parent-identity presence; no credential, ticket, receipt contents, raw response/error text, POST, credential claim, file write or service action. Root pipes reviewed source to Node running as bifrost-games from /, preserving service-account/private-home boundaries. Two disposable Node tests verify missing-ticket classification and secret/remote-payload redaction; the existing check workflow includes them. This diagnostic does not alter the installed testing 17 runtime or prior release assets. Actual tester diagnosis/recovery is pending; a missing approved join ticket is a hypothesis until the diagnostic output confirms it.

## 2026-10-08 - Private administrator working-directory recovery

The tester reached matched Host downloads, then rootless Podman refused its inherited /home/troa working directory. Root preparation now selects / before switching to either non-root panel or game accounts; all target paths are absolute. No home-directory permission expansion, root game runtime, panel wipe or service-account privilege change is needed. A network-disabled disposable container with a real non-root account reproduced EACCES from a mode-0700 administrator home, then passed using the actual corrected preparation prefix; the home remained 0700. All 39 normal installer checks and shell syntax pass, with three separate disposable-root configuration checks skipped in this run. Reviewed remaining runuser calls: their absolute paths, fixed service environments and automatic worker WorkingDirectory remain intact. Existing exact-byte package/bootstrap/unit retry guards preserve the already prepared files. Resume interrupted pre-join Host preparation as the VM administrator; real tester heartbeat/game acceptance is pending. Existing testing 17 assets remain immutable.

## 2026-10-08 - Non-login administrator recovery PATH correction

The tester authenticated as root through non-login su, but inherited a PATH without /usr/sbin; Host recovery stopped at visudo before downloading the Agent. Local read-only reproduction confirms visudo is hidden by /usr/bin:/bin and resolves at /usr/sbin/visudo with the administrator PATH. Automatic Host preparation now normalizes trusted administrator command directories for both fresh and resumed setup, and checks for visudo before writing game-account sudo policy. The existing release-version correction is retained. All 39 normal installer regressions pass; three disposable-root-only tests remain skipped in this run. Existing root/non-root boundaries, installed panel data, Host credentials, games, catalog and immutable release assets remain unchanged. The bifrost panel and bifrost-games Agent are non-root service accounts; only one-time OS preparation runs as the VM administrator. Resume interrupted pre-join preparation instead of reinstalling the healthy panel. Actual tester Host/game acceptance is pending.

## Testing 17 administrator bootstrap correction - 2026-10-08

The corrected main-branch installer isolates `/etc/os-release` parsing so Debian/Ubuntu's `VERSION` cannot replace the Bifrost release tag used by automatic Host downloads. It still downloads the exact existing testing 17 packages; published release assets and the verified updater remain unchanged. Use the corrected main/immutable-source installer for fresh installation, rather than the original testing 17 release's `install.sh` asset.

If testing 17 reported the panel ready, installed local game Host prerequisites, then stopped with `curl: (3) URL rejected: Malformed input to a URL function`, preserve the installed panel. As the VM administrator, run the corrected installer with `--resume-local-host` only. This completes interrupted pre-join Host preparation without reinstalling the panel, changing its administrator/license or deleting games. The command refuses existing Host credentials, join receipts and job state; those require recovery instead of fresh preparation. Finish browser Controller joining and master acceptance, then wait for the Agent heartbeat. Real tester VM and game acceptance remain separate.

## Fresh testing 17 Instance flow

On Debian/Ubuntu amd64, fresh `bash install.sh --instance` also prepares the isolated `bifrost-games` account, rootless Podman, pinned Node 24 and automatic Host service. Choose the intended Controller HTTPS hostname or IPv4/port and enter its code in browser setup. Its administrator accepts the request under Hosts. Bifrost completes the signed join and starts the Agent automatically; wait for its heartbeat, then create the game in the parent panel. Game terms are still explicit at creation. The reviewed catalog includes five Minecraft Java variants and Space Engineers Torch Wine; other targets remain gated.

Existing Host credentials, receipts and game/job state are preserved and refuse fresh preparation. Do not wipe a Host to retry joining. `sudo bash install.sh --resume-local-host` can resume only interrupted pre-join preparation on the same fresh Instance and requires exact matching files. The normal updater preserves existing configuration and does not retroactively provision this bootstrap. Independent local/Hybrid and manual Agent-only installs retain their explicit setup. Actual clean VM/systemd/game acceptance remains pending despite disposable compiled and installer checks.

## Testing 16 candidate: reviewed Controller connections

Enter the chosen Controller address and five-digit code in the Instance setup screen, then choose **Send connection request**. On the master, an administrator opens **Hosts → Connection requests**, compares the displayed Node ID and chooses **Accept** or **Deny** with a reason. Approval does not install a game or start the Agent. After acceptance, complete the one-time Host setup under the separately prepared non-root game account using the displayed Instance URL and private setup ticket. A recent valid heartbeat establishes that the Host is online.

For a self-signed Instance panel, the Host terminal asks for its public certificate PEM and independently confirmed SHA-256 fingerprint. Browser certificate acceptance alone is insufficient. Never supply the panel private key or disable TLS verification. Interrupted setup resumes the same private request or saved receipt. Denied/expired requests without issued credentials can renew; already-issued credentials need reconciliation. Existing game files/profiles stay on the Host.

Testing 16 publication is pending verification. The six signed Java/Torch Wine targets are retained without changing runtime approval. Controller and Linux Host packages must match; older remote clients cannot bypass acceptance. No paid services or new game/player acceptance is implied.

## Testing 15: simpler Controller connection

Instance setup displays this machine's Node ID and collects the chosen Controller's HTTPS hostname or IP/port. Check that destination with its administrator, activate the installation's separate free license, then enter the Controller's five-digit Hosts → Add host code. It is encrypted and expires after five minutes. Complete the one-time Host setup under the prepared non-root game account using the displayed command and private setup ticket. The Agent verifies the parent and saves its signed receipt before the machine appears connected. An expired code is requested again in the terminal. Existing Host transfers use the separate advanced handover flow.

Hosts keeps machine status and connection controls visible and collapses setup guidance, network discovery and advanced identity/role settings. Testing 15 is published with reviewed Torch Wine and the existing five signed Minecraft Java targets. The six-target catalog and matching Controller/Host package are verified; customer player and lifecycle acceptance remain separate.
## Previous Instance onboarding in testing 14

Choose **Run independently** to manage local games or **Connect to a Controller**
to use a parent fleet panel. The installed Instance role is displayed separately.
After administrator/MFA setup, **step 04** asks for the parent's HTTPS panel URL
(without `/api`), fetches its public identity and requires independent confirmation
of its Node ID and key fingerprint. Editing the address clears confirmation.
The verified destination stays in this wizard while you activate the separate
Instance license in step 05. Reloading requires checking the destination again;
no pairing credential is saved in browser storage.

In **step 06**, confirm this Instance Node ID and provide a reason, then prepare
its private join ticket. Under the separately prepared non-root game-service
account, run `bash install.sh --host --join-instance`. The terminal asks for the
Instance URL, private ticket and a fresh five-digit code generated on the parent
Controller → Hosts → Add host. Generate the code when ready, rather than before
license onboarding, because it expires quickly. The compiled Agent verifies the
live parent and signed receipt before starting. Interrupted joins reuse saved
private recovery state; existing enrolled Hosts use the separate handover flow.
Checking an address does not delegate control, enroll a Host or activate a license.
Testing 14 publication, all fifteen asset sizes/digests and seven anonymous latest downloads are verified. Prior release assets remain immutable.

## Installation roles in testing 12

Choose `--controller`, `--instance` or `--hybrid` when installing a panel. `--host` installs only the game Host Agent and joins the explicitly selected Controller. A Bifrost node, its free-license installation and each game server have separate identities. A standalone Instance enrolls its own local Host; Hybrid can enroll local and remote Hosts. The game-service account, Node.js 24 and rootless Podman still require separate preparation.

Standalone-to-Controller handover requires verified parent identity, administrator confirmation, completed jobs and a stopped Agent. The matched `dist/pair-controller.js` retains profiles/data/backup keys, saves a signed receipt for recovery and disables local game authority. Historical backup/schedule inventory stays local pending migration. Optional private-LAN Bifrost discovery is disabled by default, bounded and never automatically establishes trust. AMP import, hypervisor VM creation and Windows handover distribution remain separate.

Examples, after downloading and verifying the release installer:

```bash
bash install.sh --controller
bash install.sh --instance
bash install.sh --hybrid
```

To wipe a disposable test panel, use the selected role with `--reinstall`, review its displayed absolute path and type its required confirmation. This deletes that panel's stored data; it does not wipe a separately installed Host Agent or its games. Preserve game data before choosing any reset.

Testing 12 retains the reviewed five-target Java catalog from testing 10. Role changes do not approve a new vendor runtime. Existing installations update separately from their Host Agents and retain local catalogs/keys/policies. Publication and real game acceptance are recorded separately below.

## Publisher catalog packaging

Testing 10 includes the verified publisher-signed public catalog for Minecraft Java 1.21.1 vanilla/Paper/Fabric/Forge/NeoForge. Controller and Linux Host packages receive the same signed bytes and pinned public publisher identity. The Host asks its operator to approve private storage, bind address and resource limits. Each Create still requires the game-specific terms/EULA. Customers do not create publisher recipes or signing keys.

Palworld and Space Engineers download/create engine fixes are included, but their automatic signed launch runtimes remain pending. Bedrock and trusted Windows distribution also remain separate. A signed controlled-testing catalog does not prove real game startup, player access, lifecycle or recovery acceptance.

# Bifrost Server Manager

## Current testing download

[Customer testing 15](https://github.com/troainc/Bifrost-Server-Manager-Public/releases/tag/v0.1.0-installtest.15) is published with matched compiled panel images and Linux Host Agent, simplified Controller connection and Hosts pages, six signed Linux recipes, checksums, scans and verification receipts. All 22 uploaded asset sizes/digests and nine anonymous downloads match. Fresh migrations and locked-role setup passed over verified local HTTPS; 33 installer checks, 15 authorization/pairing HTTP checkpoints and compiled non-root join/handover recovery passed. Three final customer image scans and the Torch dependency-runtime scan reported zero HIGH/CRITICAL findings and detected secrets. No paid services or signup were used.

Space Engineers **Torch on Linux Wine**, rather than vanilla, reached `Game ready` in a fresh non-root, read-only sandbox. The immutable public runtime was pulled without registry credentials. Five Minecraft Java 1.21.1 recipes (vanilla, Paper, Fabric, Forge and NeoForge) retain their exact previous signatures. Real customer player connectivity, save/stop/restart, backup/restore and failure recovery remain to be tested. Palworld, Bedrock, vanilla SE and signed Windows distribution have separate pending requirements.

Compatible Alpine PostgreSQL 17 updates preserve accounts, secrets, data and existing local provisioning catalog/trust/policy. Updating the panel does not silently update a Host Agent or replace its approved game policy. Fresh Hosts can explicitly approve the included six-target catalog; existing Hosts need their separate update and policy migration review. See [Torch controlled-test guide](docs/Torch-Wine-Controlled-Testing.md).

## Linux install

The installer asks for the machine's role before installation:

| Role | Purpose |
| --- | --- |
| Controller (`--controller`) | Management panel/API/database; one per fleet |
| Standalone Instance (`--instance`) | Local panel; manages its own enrolled local Host until explicitly handed to a Controller |
| Hybrid (`--hybrid`) | Controller with a separate local Host, plus optional remote Hosts |
| Host Agent only (`--host`) | No panel; joins the selected Controller and can run one or more games |

A **game instance** is one game server created later in your panel, after Host enrollment and reviewed game-policy approval. For one machine, choose Instance for local-only use or Hybrid for local plus remote management, then separately prepare a non-root game account and install its local Host using that panel's Node ID. Host-only installation joins an existing Controller and creates no panel. Role choice does not determine the number of game servers.

The automatic **Controller installer currently supports Debian and Ubuntu on x86_64**. Its host-preparation step checks the distribution and uses Debian/Ubuntu package tools. Containerized application code does not make that bootstrap script portable to every Linux distribution.

The separate **Linux Host Agent** has no distribution-name restriction, but requires Node.js 24 at `/usr/bin/node`, a working systemd user manager and rootless Podman under the unprivileged account that owns the games. Other Linux distributions are compatibility candidates when those prerequisites exist; record the exact distribution/version during installation, enrollment and game tests before claiming support. Systems without systemd do not meet the current agent requirements. An Ubuntu test is one useful acceptance target, not evidence that every Linux system works.

Run this as your current VM user. The installer requests the administrator password once, creates the unprivileged bifrost account, and continues automatically:

```bash
wget --output-document=install.sh https://raw.githubusercontent.com/troainc/Bifrost-Server-Manager-Public/main/install.sh && bash install.sh
```

The wizard asks for the VM IP/hostname and HTTPS port, downloads the application, checks its checksum, generates configuration and credentials, and starts the panel. Default port: **8443**. Create your administrator in the browser.

The testing 15 bootstrap and release installer support all four role choices. From **Hosts -> Add host**, create a fresh one-use machine pairing code. Host setup verifies its matching package and asks for the Controller panel HTTPS URL and code. Local Instance/Hybrid setup also supplies that panel's Node ID, as shown in its guide. The licensing URL is different; enrollment connects a machine and does not install a game. Choose a reviewed signed Blueprint afterward.

The installer/updater recognizes Docker classic/containerd image identities only when they match the checksummed archive and locked configuration. Earlier release attachments remain unchanged.

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


## Documentation

Use the [documentation index](docs/README.md) and [operator guide](docs/USER_GUIDE.md) for role selection, installation, enrollment, updates, and day-to-day operations. Check the release notes for the current testing-build boundaries.
