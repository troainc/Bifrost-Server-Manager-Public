## 2026-10-21 - Test 35 delivery verified

Test 35 UI fixes are deployed on the master and published as a new signed customer testing prerelease. Master account/security rows, mounted data, secrets, keys and branding match its retained checkpoint; all six services are healthy. All 33 application/prerequisite downloads match anonymous HTTPS hashes. Rebuilt private tests passed 262 with nine explicit skips; public 43 Node checks and exact-source hosted installer/image-store checks passed. Exact candidate and deployed image scans passed. Private hosted runners remain blocked by GitHub billing/spending limits. Human acceptance and general release approval remain outstanding. Frozen artifact sources and full preservation/verification evidence: Docs/Test-35-Rollout-2026-10-21.md. Documentation-only delivery uses [skip cd] to avoid an unnecessary restart.

## 2026-10-21 - Test 35 UI fixes prepared for authorized testing delivery

Test 35 includes shared scrolling, navigation, responsive registry/field labels, modal focus and inventory-feedback fixes. It preserves existing data, accounts, cryptographic identities and installed runtimes. Prior release assets remain immutable. Publication and deployment evidence, and the remaining human checks, are recorded in Docs/Test-35-Rollout-2026-10-21.md; do not infer successful delivery from this preparation entry.

# Bifrost Server Manager — customer distribution

Bifrost manages customer Controllers, explicitly approved Hosts and game instances through signed jobs and reviewed local policies. The private TROA licensing/owner master is a separate deployment and is excluded from these packages.

## Current status

`v0.1.0-installtest.34` is published for owner-authorized controlled installation testing. Fresh setup offers the separately signed maintained prerequisite baseline only after explicit tester consent; independent review and real target-server acceptance remain pending. Its source adds whole-release signature verification and encrypted database/configuration/key checkpoints with recovery into a new database. Existing production/customer data and earlier release assets remain preserved. No candidate install command is advertised until publication and independent approval are complete.

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
