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

## 2026-10-08 - Testing 17 administrator bootstrap correction

- Read the Debian/Ubuntu OS identifier in a subshell; keep the matched Bifrost release version for the automatic Host package and checksum URLs after panel installation.
- Added executable regression coverage with Debian/Ubuntu version descriptions containing spaces, retained caller variables and unsupported/missing OS identifiers.
- Keep original testing 17 release assets, package digests, catalog/runtime approvals and immutable updater unchanged. Corrected installer source can resume interrupted pre-join Host preparation as root with `--resume-local-host`; no panel wipe or game reset is required.

## Testing 16 candidate

- Master-side reviewed connection requests with explicit administrator Accept/Deny and reasons.
- Distinct pending approval, accepted Host setup, signed connection and heartbeat states.
- Private resumable enrollment requests; explicit self-signed Instance public-certificate trust without TLS bypass.
- Separate status-poll and code-attempt rate buckets; legacy remote clients require a matched update.
- Preserve six signed Java/Torch Wine targets and all earlier immutable releases. Publication pending final verification.

## 2026-10-07 - Testing 15 published; simpler pairing and Torch Wine

Published testing 15 from private application source f6f9c35fefdcd42188c3d4f9c48ab1b3c9613df5 and public packaging source 58e1c5ef2b8de638b2243ded6344877292aee672. All 22 release asset sizes/digests and nine cookie-free latest downloads match; public main installer is byte-identical. Fresh verified loopback HTTPS/database/first-admin setup, 33 installer checks, six signed catalog checks, 15 HTTP authorization/pairing checkpoints, compiled non-root fresh join and handover/recovery passed. Final customer image scans are archive-bound and report zero HIGH/CRITICAL findings or detected secrets; sharp is patched to 0.35.5.

Instance setup shows its actual Node ID and Copy, accepts HTTPS hostname or IP/port and a parent five-digit code, and collapses advanced identity/recovery. The code is encrypted, Controller-bound and expires; no browser persistent storage holds it. A signed Host receipt remains required before Connected. Licensing, node joining, Host enrollment and game creation are separate.

The six-target catalog adds reviewed Torch Wine and preserves all five Java signatures. Public immutable runtime ghcr.io/troainc/bifrost-game-torch-wine@sha256:20149486ed2836668432e4f311fdc22ca92172c428c05f3a2e3e4320a9f891bd was published by free public workflow 37578562603 and pulled anonymously. Official Steam build 24675709 and Torch v1.3.1.347-master reached Game ready under fresh non-root, read-only Wine policy with actual 64 MiB tmp/PID limits. Real customer player, lifecycle, backup/recovery acceptance remains pending. Palworld, Bedrock, vanilla SE and signed Windows distribution remain separate. No private key/source, paid service, billing change or remote VM update is implied. Prior release assets remain immutable.

## Public operator documentation expansion - 2026-10-06

- Added a detailed Controller and Host Agent operator guide under `docs/` and linked it from the README.
- Documented role-specific prerequisites, enrollment, safe update/recovery, routine operations, and the boundary between test evidence and real host/game acceptance.

## 2026-10-06 - Testing 14 published and deployed; Controller connection guide verified

Published [controlled testing 14](https://github.com/troainc/Bifrost-Server-Manager-Public/releases/tag/v0.1.0-installtest.14) from private runtime source 577cb6692c8ae7cc8fb4a08b43544f14548fb8aa and public packaging source 225286b0f8fe0e7d4125015a856e8931b636b476. All fifteen uploaded sizes/digests and seven full anonymous latest downloads matched; public main bootstrap matches the release. Prior assets remain immutable and both main histories retain other contributors' commits.

Instance Welcome now uses independent/Controller management cards, separate from its installed role. Step 04 collects the parent panel URL and requires independent public identity confirmation; editing the URL clears trust. The public draft survives license step 05 in the wizard; reloading requires rechecking, and no pairing credential is stored in the browser. Step 06 prepares the private Instance ticket and explicitly directs fresh parent Host code entry in the separate game-service account's setup terminal. Address preview does not enroll a Host, grant fleet ownership, activate licensing or delegate local game authority. Only this authenticated administrator/MFA/CSRF-protected read-only lookup is allowed before agreement; pairing preparation and fleet actions retain their gates.

Full build/typecheck, focused agreement/node/onboarding checks, bounded source-map regression, 33 public installer checks, 14 least-privilege HTTP/database checkpoints, compiled desktop/mobile guide and role-aware panel verification, fresh package migrations/locked Instance setup over verified local HTTPS, final packaged non-root join/handover recovery and signed catalog policy passed. Three final customer image scans reported zero HIGH/CRITICAL findings and no detected secrets, bound through verified archives to configuration locks. Disposable QA database/container volumes were cleaned up. No paid services, signup, billing/spending changes, legal/EULA acceptance or customer machine mutation.

Coolify deployment xmldvazszkk78q8wy3sohkde for 577cb66 succeeded in 1m15s. Fresh signed-in master reads show Controller role, stable Node ID cd76b82e-dd5f-4765-aace-1ee5d5058e1d and footer testing 14. Anonymous licensing and parent identity routes returned 200 JSON without browser credentials. The separate non-root Node.js 24/rootless Podman/user systemd account remains required. This is guide/pairing verification, not inaccessible customer VM or real game/player/lifecycle acceptance. Existing five-target signed Java catalog is retained; new Palworld/Space Engineers/Wine/Bedrock/Windows runtime acceptance, AMP integration, hypervisor provisioning and historical inventory migration remain separate. Earlier candidate records below are superseded.

## 2026-10-06 - Testing 14 onboarding candidate

Fresh Instance setup now separates installed role from independent/parent management cards. Step 04 collects the parent panel URL and public identity confirmation; destination changes clear trust and the public draft survives step 05 within the wizard. No credentials are stored in the browser. Step 06 retains the verified join ticket and terminal entry of a fresh parent Host code after activation. A narrow authenticated administrator/MFA/CSRF-protected identity preview is available before agreement; topology writes and fleet controls stay gated. Matched testing 14 publication and deployment verification are pending. No paid service, real customer Host mutation or game acceptance.

## 2026-10-06 - Testing 13 published; direct Instance joining verified

Published [controlled testing 13](https://github.com/troainc/Bifrost-Server-Manager-Public/releases/tag/v0.1.0-installtest.13) from private runtime source 43ef3e48f4389af80371d70c09e68fdef04dbdc7 and public packaging source e6148a98970e53dd9969df10b7ce9c95de3bad05. All fifteen uploaded sizes/digests and seven full anonymous latest downloads matched; public main bootstrap matches the release installer. Prior release assets remain immutable. Both main branches preserve previous contributor commits.

Fresh Instance onboarding now offers independent management or explicit joining to a verified parent Controller. The installed role is text, and the joining step does not create a local Host code. Its private setup ticket and a parent-generated Host code bind the Instance Node ID to the chosen parent. The matched Linux CLI verifies identity/signature, saves durable recovery state, resumes interrupted completion without a second enrollment, and refuses existing Host/game state. Existing handover remains available and preserves profiles, paths, ledger and backup keys. Licensing does not grant fleet ownership.

Full build/typecheck, 33 public installer checks, five node-policy checks, 13 least-privilege HTTP/database checkpoints, compiled non-root fresh join and handover recovery, independent/parent and role-aware desktop/mobile browser checks, fresh migrations/locked Instance setup over verified local HTTPS, and final packaged catalog policy checks passed. Controller and Host signed catalog bytes match. Three final image scans reported zero HIGH/CRITICAL vulnerabilities and no detected secrets, bound through archive identities to configuration locks. No paid service, signup, billing/spending change or real game EULA acceptance was used.

Coolify deployment bub15bmo7emsxnqmvcskcyo2 for 43ef3e4 succeeded in 1m18s. The freshly reloaded master remains a Controller with stable node cd76b82e-dd5f-4765-aace-1ee5d5058e1d; anonymous licensing discovery and Agent public parent identity work without browser cookies. Current footer links testing 13. Separately prepared Node.js 24/rootless Podman/user systemd under a non-root game account remain required. No inaccessible customer VM was changed. Actual customer/game/player/lifecycle acceptance, Palworld native startup, Space Engineers/Wine, Bedrock runtime publication, Windows handover distribution, AMP integration, hypervisor provisioning and historical inventory migration remain separate. Preparation notes below are historical and superseded by this verified record.

## 2026-10-06 - Direct Instance onboarding and testing 13 preparation

Instance setup now distinguishes independent local management from joining an existing Controller. Installer-fixed role is plain text; step summaries and buttons follow the actual role. The parent URL lookup is administrator-only, TLS verified, bounded and redirect-free, with independent identity confirmation and a verified-paste alternative. Fresh joining requires no prior Hosts, locks local authority and uses a private Instance ticket plus a Host code generated on the parent. The compiled non-root join CLI verifies live parent identity and the exact signed receipt, saves a durable recovery record and completes delegation before Agent startup. Existing Host/game state must use the preserved handover path. Licensing never chooses a parent. Preparing matched testing 13; publication/deployment and real customer/game acceptance are separate. No paid services, private key distribution, game EULA acceptance or customer Host mutation.

## 2026-10-06 - Testing 12 published and deployed; node roles verified

Published [controlled testing 12](https://github.com/troainc/Bifrost-Server-Manager-Public/releases/tag/v0.1.0-installtest.12) from compiled private source b0e1a2d9f9246f7b95c7ab6d2753464fdceddb51 and public packaging source 61795cd9e3bb7a731fd94f7784c876bb3e2ba258. All fifteen uploaded assets matched size/digest readback; seven full cookie-free latest downloads and public main/install.sh matched the release bytes. Testing 10 and 11 remain immutable. Public main now selects explicit Controller, standalone Instance, Hybrid or Host Agent-only roles; existing fleet updates preserve configuration.

Free local workspace build/typecheck, 32 installer checks, five node policy checks, ten least-privilege two-panel HTTP/database checkpoints, compiled non-root interrupted-handover recovery and isolated desktop/mobile browser checks passed. Final packaged fresh migrations, locked Instance setup and verified loopback HTTPS passed. The exact packaged Host verified the five signed Java recipes and preserved prior policy. All three final image scans reported zero HIGH/CRITICAL vulnerabilities and no detected secrets, bound through verified archive identities to image configuration locks. Exact source-map-js 1.2.2 and its bounded regression passed; GitHub alert 3 was recorded fixed at 2026-10-06T04:05:08Z, without dismissal or a paid feature.

Coolify reports successful b0e1a2d deployment (1m06s). A fresh signed-in Hosts read shows Controller role and stable node cd76b82e-dd5f-4765-aace-1ee5d5058e1d. Host pairing, node identity, licensing registration and game creation remain separate. Local Instance/Hybrid game account and runtime preparation are explicit. No customer Host was changed, no EULA accepted, and no real game/player/lifecycle acceptance is claimed. AMP integration, hypervisor provisioning, Windows handover distribution, historical backup/schedule inventory migration, Palworld native startup, Space Engineers/Wine and Bedrock runtime publication remain separate. No paid service, subscription, signup or billing/spending change was used. Earlier candidate notes below are historical and superseded by this record.

## 2026-10-05 - Matched node-role testing 12 candidate

Testing 11 published with fifteen verified assets; seven anonymous latest downloads and public main bootstrap matched. Testing 12 carries the same verified node/pairing implementation and corrects the remaining Hosts guide and fleet card to explain Instance-local and Hybrid-local/remote setup. The private master deployed d062016 successfully and its signed-in Controller identity was verified. Testing 11 remains immutable. New exact-source package/scan/download verification is pending; no customer Host, game, paid service or signing key changed.

## 2026-10-05 - Testing 11 node-role installer candidate

Adds explicit Controller, standalone Instance node and Hybrid panel roles; Host Agent-only installation remains separate. The chosen role and machine hostname are recorded in new panel configuration. Existing updates preserve configuration and do not convert a fleet. The immutable updater pin is 04645cb2f98a4401f2cfd8f1618427631e430df6 with SHA-256 ec2509175a7f1d56a182fbafdb150e52eac5804cff2a89a72f4f0604352d86d6. Matched compiled panel/Host build, scans, HTTPS verification and publication are in progress. Preserve testing 10 assets and the public main bootstrap until testing 11 assets have been verified. No private source/signing keys or paid service is distributed.

## 2026-10-05 - Final testing 10 delivery verified

Public PR #14 merged as 3e2433ee30637f91a3569b7d60c86c9b088aeb7e. Exact head 03f3f4836cce14455b4938c355df6f420b0030b4 passed installer workflow 37380067525 and actual published testing 10 archive workflow 37380067486 in both Docker 29.8.2 classic/containerd stores. Public config archive modes and non-root nginx readability also passed. Cookie-free main/install.sh is byte-identical to the verified release installer (SHA-256 86eb1257c8ceccefb21407a4990ef9232c25aaee57f43ea79d7539c20c525322). All fourteen published asset sizes/digests and five anonymous latest downloads match. This final documentation record does not alter the immutable release or verified executable source. No paid services/signup/billing changes; no remote customer VM or game acceptance is implied. The signed automatic catalog is the five controlled-testing Java 1.21.1 variants described below.

## 2026-10-05 - Published matched testing 10 using free local verification

Testing 10 is published at https://github.com/troainc/Bifrost-Server-Manager-Public/releases/tag/v0.1.0-installtest.10. Private source 4c1a32b7a1010dc81770afcffebe509c821265d6 has the exact same tree as merged private main c30118b5dcea05b0008be3fe264be416547c2e9f; public build source is c5b0bd24e446d8ba259cf32fe30941ef002523e0. Free local Ubuntu WSL Docker Engine passed compiled-only isolation, all three zero HIGH/CRITICAL vulnerability/secret scans, image archive identity/config locks and fresh HTTPS database migrations/first-admin setup. The compiled Linux Host verified the real signed five-target Java catalog as non-root, installed protected policy/backup keys and preserved existing policy. All 14 uploaded asset sizes/digests and five anonymous latest downloads matched. Public source checks 37378786091/37378786180 passed; actual testing 10 classic/containerd acceptance now targets the new immutable archive. Private hosted Actions were blocked before steps by account billing/quota; no paid services/signups/billing changes were used. The dedicated private publisher key is outside Git and distribution. Testing 9 assets and inaccessible customer VMs remain unchanged.

The signed controlled-testing automatic catalog covers Minecraft Java 1.21.1 vanilla/Paper/Fabric/Forge/NeoForge. Real game/player/lifecycle/recovery acceptance, Palworld native readiness, SE Wine/.NET, Bedrock bytes and trusted Windows distribution remain pending. Historical preparation notes below are superseded by this record. Existing installations retain their local catalog/policy on --update; fresh-Host approval and existing-policy migration are distinct.

## 2026-10-05 - Free local release verification and public template permissions

Private hosted Actions are blocked before execution by the account billing/quota state. Edward explicitly prohibited paid services and account changes; verification uses existing Ubuntu WSL with free Docker Engine instead. The local three-image build, scans and compiled isolation checks passed. A restrictive-umask source export also revealed unreadable mode 0600 public database-init/config templates: PostgreSQL could initialize its database, skip the failed hook on restart, and then fail migrations because bifrost_app was missing. The builder now normalizes only public config files in its new staging tree to 0644; customer credentials/installed files are untouched. Fresh empty-volume HTTPS validation must pass before publication. Testing 9 remains unchanged.

## 2026-10-05 - Preparing matched testing 10

Testing 10 is being prepared for the merged automatic-download filename, bounded Steam bootstrap restart, Forge launcher and Torch inventory corrections. The new Controller and compiled Linux Host Agent must receive the same verified publisher catalog. Dedicated publisher identity/signing and the matched customer build/release remain pending; this preparation does not enable games on testing 9. Preserve all existing release assets. Real game start, player connection, lifecycle/recovery, Bedrock/Wine and signed Windows acceptance remain separate. No remote installation has been changed.

## Prepared - reviewed publisher catalog handoff

- A future bundle build can accept a signed public catalog and an independently approved publisher key ID.
- Verify exact-byte handoff signatures/hashes and copy only three public data files.
- Reject wrong publisher, forged signature, altered bytes, private-key material and existing catalog replacement.
- Testing 9 remains immutable; a real reviewed/signed catalog and matched release are still pending.

## 2026-10-05 - Published matched testing 8

[Customer testing 8](https://github.com/troainc/Bifrost-Server-Manager-Public/releases/tag/v0.1.0-installtest.8) is published. Compiled private source 418753acfc9e0618810eaa7bc900f5f0a5640952, public installer/environment source efe2dbe900019bd1fa96217b0dac4dbef028a3e5, final workflow 37262001155. Downloaded artifact SHA-256 59cecfbe436d47485601139873fea9f1b0e3d48126a14f2d92a3ba0c9fe3128e matched GitHub; all eleven uploaded sizes/digests and five anonymous latest downloads matched. Three image scans contained zero HIGH/CRITICAL findings; compiled-only Controller/Agent isolation, deployed public key and fresh HTTPS/database setup passed. The downloaded Agent preparer produced compatible synthetic SE and Minecraft manifests without private repository access. Main CI/security/generic Host operations passed. Runtime approval and actual game/player/lifecycle/recovery acceptance remain pending; signed Windows distribution is not included. Earlier pending notes are historical. Testing 7 assets are unchanged.

## 2026-10-04 - Testing 8 preparation

Preparing a matched Controller/Linux Host Agent download for Space Engineers vanilla/Torch, Palworld and Minecraft Java/Paper/Fabric/Forge/NeoForge/Bedrock Host-approved package review. All nine choices require reviewed local packages and runtime/service policy; vendor downloads, game acceptance and Windows signed distribution remain separate. Testing 7 assets stay immutable. Publish and verify testing 8 assets before merging this bootstrap to main.

## 2026-10-04 - Publish matching testing 7 customer download

- Publish verified compiled Controller/Host packages and matching installer/updater with immutable updater pins, role selection, archive-backed image identity and preserving-data upgrades.
- Include signed generic Linux OCI placement, forward schema repair, bounded operations, Host upgrade/re-enrollment, MFA and mobile-navigation fixes; preserve operator catalog/trust with empty defaults.
- All eleven asset digests and anonymous download bytes verified. Actual game/customer-host acceptance remains separate; older Debian PostgreSQL upgrade guard retained.

# Changelog

## 2026-10-04 — Fix Host installer heredoc terminator

- Closed the Host Agent ZIP extraction Python block with its matching `HOST_ZIP_PY` delimiter. Bash can now parse the complete installer after download.
- No QA or VM execution performed per owner direction.

## 2026-10-04 — Make role choice installer step one

- Presented Controller versus Instance Host selection as step 01 of the interactive installer; Controller setup stages now follow as 02–06.
- Kept role selection inside the installer process; no standalone role-selection page was added.

## 2026-10-04 — Controller and Instance Host installer roles

- Added explicit `--controller` / `--host` selection and an interactive role chooser. Existing noninteractive setup must name a role; administrative bootstrap, reinstall, and resume modes retain their existing behavior.
- Instance Host mode downloads the Host Agent ZIP and checksum for the installer's matching release, verifies the digest, safely unpacks bounded regular files under the user's home, and runs Host enrollment as the regular operator account.
- Host setup requires existing Node.js 24, rootless Podman, and a systemd user manager. It does not create another Controller or install a game server.
- Public release assets are unchanged. Use maintained `main/install.sh` source until a future tagged installer release includes this support.

- 2026-10-04: Repair configuration-versus-manifest image identity checking in both standalone scripts. Derive portable configuration locks from the saved archive. Bind accepted OCI manifest IDs to hashed archive metadata and the exact locked configuration; keep rejection of other IDs. Add negative regression cases and an actual testing 6 package/Docker 29 classic/containerd reproduction workflow. Recover a prepared Alpine testing 6 installation through the corrected preserving-data updater rather than another wipe. Published testing 6 attachments remain unchanged; use the current repository bootstrap. Hosted configuration run 37178051407 passed all 17 regression tests and updater-pin verification; image-store run 37178051391 reproduced the old containerd failure and passed both repaired scripts on classic and containerd.

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

## 2026-10-05 — Automatic creation testing 9 candidate

Prepare a matched immutable testing 9 Controller/web/database and compiled Linux Host Agent from PR #44's verified source. Update installer/environment and pin updater e9ffc7d6af53aeddbcd1cb612bb2181e48f7968f with SHA-256 44a6488824ef221166dd06a48a1c82bc1be3167e8315b37c1cde850c816103ff. Keep testing 8 assets and main bootstrap intact until the new build, scans, hashes and draft assets are verified, then promote this candidate. A newer package does not approve unsigned runtime recipes, certify real vendor games or include public Windows distribution. Hosted release build/publication remains pending at this entry.

## 2026-10-05 — Matched testing 9 published

Published testing 9 from private source fde51044090de7f786d78d6902d9c2ffecba59b5 and public installer/environment source 00514ebd23fae447030a790ec039b86980eb0572; workflow 37273201450 succeeded. The downloaded artifact SHA-256 af05705e877a07db36aabd29626a3049633728c8f8930ca275ab3c9c9cc4aff9 matched GitHub. All eleven uploaded asset sizes/digests and five cookie-free latest downloads match. Three image scans have zero HIGH/CRITICAL findings; compiled-only customer/Agent packaging, fresh HTTPS migrations/setup and deployed public licensing key passed. Updated Host archive includes the automatic installer and generated Java launcher. Public Docker classic/containerd checks now target the actual testing 9 package. Testing 8 assets remain unchanged. Real signed game catalog/runtime preparation and vendor acceptance remain pending; no Windows public distribution or remote customer update is implied.
