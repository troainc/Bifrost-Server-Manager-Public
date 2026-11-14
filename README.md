> Test42 canonical TROA identity and shared Data/MH shell: [review and category ratings](Docs/Interface-Ecosystem-Review-2026-11-13.md), [exact automated evidence and delivery status](Docs/Test-42-Delivery-2026-11-13.md). Master/customer8.0/8.0 is a scoped design judgment; real-target manual acceptance remains open. No paid services or PC tests/builds. Historical records follow.

> [Historical Test 39 delivery and acceptance status](Docs/Test-39-Delivery-2026-11-13.md).

## 2026-11-13 — Signed Test 39 published and anonymously verified

Owner authorized the matched public testing release and website install/update instructions. PR 25 merged into main as 69b3f1e58622a037dea1cb10eac0ce121be23546. Immutable signed v0.1.0-installtest.39 (release 444484964) is published; all 25 assets anonymously downloaded over HTTPS match exact signed size/SHA-256. Frozen application source is 5d10c56212dcd00ef01d6be7464fd8018242b738, packaging source 5813fc986226135d7e5629c82f7ee9c2c30767c2. Installer SHA-256: 64c6b79b37cac1c55ff87036184a607e8f7958e1c54ba2864d8a5bcab83a28c1. Both exact offline bootstrap verifiers pass before publication. Prior releases stay immutable. Publication does not apply an update to any existing server.

The owner will test the public server manually. No existing customer installation, timer, Agent or game was changed; no stable promotion is implied. Full target updater/interruption/recovery, actual game/player/runtime, screen-reader and long-soak acceptance remain pending. All tests/builds run on hosted runners, with no PC runtime/WSL workload; the existing offline key signed only a small manifest and never left its original location. Large assets stayed off the PC. See Docs/Test-39-Delivery-2026-11-13.md. The prior scored audit records pre-publication history; this new owner-authorized delivery supersedes that hold.

> November 12 source candidate: [opt-in scheduled panel updates](Docs/Automatic-Panel-Updates.md). Testing runs remotely; this is not a published release or enabled setting. Existing Test 38 assets remain immutable.

> Signed Test 38 Node security testing assets and gated main-site commands are published and verified. Real installation and game acceptance remain open; see [release evidence and remaining checks](Docs/Test-38-Node-Security-2026-10-23.md).

> Test 37 public package and main-site Debian/Ubuntu install/update commands are live and verified. [Delivery evidence and manual acceptance](Docs/Test-37-Rollout-2026-10-22.md). Panel updates preserve data and leave enrolled Hosts/games running; no real customer update was performed.

> Test 36 testing delivery is verified. See [release evidence, in-place update command and remaining testing checklist](Docs/Test-36-Rollout-2026-10-22.md). Existing data and prior releases are retained. Host updates and stopped-game Console plugin installation are separate; general release and real-game acceptance remain pending.
> Local October 22 candidate: continuous Console, separately delegated Torch commands and stopped-server mod/plugin ZIP installation are implemented and tested locally. [Scope, evidence and target acceptance](Docs/Live-Console-and-Content-2026-10-22.md). Published installation assets remain unchanged.

> Local October 22 follow-up is unpublished. The modified working-tree installer must not replace the signed Test 35 asset. See [local validation and remaining checks](Docs/UI-UX-Remediation-2026-10-22.md).

## 2026-10-21 - Test 35 delivery verified

Test 35 UI fixes are deployed on the master and published as a new signed customer testing prerelease. Master account/security rows, mounted data, secrets, keys and branding match its retained checkpoint; all six services are healthy. All 33 application/prerequisite downloads match anonymous HTTPS hashes. Rebuilt private tests passed 262 with nine explicit skips; public 43 Node checks and exact-source hosted installer/image-store checks passed. Exact candidate and deployed image scans passed. Private hosted runners remain blocked by GitHub billing/spending limits. Human acceptance and general release approval remain outstanding. Frozen artifact sources and full preservation/verification evidence: Docs/Test-35-Rollout-2026-10-21.md. Documentation-only delivery uses [skip cd] to avoid an unnecessary restart.

## 2026-10-21 - Test 35 UI fixes prepared for authorized testing delivery

Test 35 includes shared scrolling, navigation, responsive registry/field labels, modal focus and inventory-feedback fixes. It preserves existing data, accounts, cryptographic identities and installed runtimes. Prior release assets remain immutable. Publication and deployment evidence, and the remaining human checks, are recorded in Docs/Test-35-Rollout-2026-10-21.md; do not infer successful delivery from this preparation entry.

# Bifrost Server Manager — customer distribution

Bifrost manages customer Controllers, explicitly approved Hosts and game instances through signed jobs and reviewed local policies. The private TROA licensing/owner master is a separate deployment and is excluded from these packages.

## Current status

[Test 40](https://github.com/troainc/Bifrost-Server-Manager-Public/releases/tag/v0.1.0-installtest.40) is the current owner-authorized controlled testing prerelease. It includes the operator UI redesign, signed in-place panel updates and retained encrypted recovery safeguards. [Exact delivery/download verification and manual acceptance](Docs/Test-40-Delivery-2026-11-13.md) remain separate. Use the verified Debian/Ubuntu fresh-install or panel-only update instructions on the [TROA tester page](https://therealmsofasgard.com/gaming-hub/bifrost-server-manager#testing-installation). Existing data and prior release assets are preserved; real target/game/player and full update/recovery acceptance remain open.

The historical published prerelease is [Test 33](https://github.com/troainc/Bifrost-Server-Manager-Public/releases/tag/v0.1.0-installtest.33). Its earlier acceptance and signature limitations remain historical; it is not evidence for this candidate. [Earlier delivery records](Docs/History/README-before-release-readiness-2026-10-21.md) are retained.

Read [supported scope and acceptance](Docs/Supported-Release-Scope.md), [update recovery and key rotation](Docs/Recovery-and-Key-Rotation.md), and [standalone installation](Docs/Standalone-Installation.md). The initial beta promise is Linux x64, one Controller replica, reviewed exact game recipes and explicit operator ownership. Native Windows packages, SE2, no-Wine SE1 and optional Gate/bridge integrations are outside this candidate's beta support promise pending their own acceptance.

## Artifact and update policy

Installer/updater code pins the candidate release signer and verifies a signed version/source/artifact manifest before executing a downloaded updater or loading customer packages. Customer code never downloads a private signing key. Initial bootstrap instructions must pin the exact installer checksum through an independently reviewed channel. Offline signatures authenticate bytes; they do not approve publication, manual acceptance or privacy policy.

Updates require the existing non-root service account and retained keys, stop platform writers, verify an encrypted PostgreSQL checkpoint, and journal configuration/schema changes. Recovery authenticates the checkpoint, creates a new database, restores exact configuration and keys, and preserves the original failed database. Escrow the separate recovery key and retain old images. Normal update/recovery never resets worlds, removes databases or runs a volume wipe.

## Verification and release

Run shell syntax/bootstrap synchronization, Python installer/signature/recovery regressions and Node diagnostic tests before packaging. The private build pipeline compiles matched public-only Controller/web/Host artifacts, verifies owner exclusion and exact image identity, records dependency/SBOM and scan evidence, and signs only source-bound local candidates with passing automated gates. Exact target OS/game/player, accessibility, production configuration/key escrow, qualified privacy review and external repository/CI approvals remain explicit requirements before rollout.

Use [AGENTS.md](AGENTS.md), [CONTEXT.md](CONTEXT.md) and [LOGS.md](LOGS.md) for current local work. Do not replace earlier release assets or describe source/fixture checks as customer machine acceptance.

Host prerequisite approval is an open release gate. Missing Docker/Compose are no longer downloaded automatically; see [prerequisite security review](Docs/Prerequisite-Security-Review.md). Existing host runtimes/data are preserved.

Use the [manual acceptance checklist](Docs/Manual-Acceptance-Checklist.md) to record the exact candidate's OS, upgrade, game/player, recovery, accessibility and approval evidence. It is also included in the compiled bundle alongside the read-only prerequisite inventory script.
