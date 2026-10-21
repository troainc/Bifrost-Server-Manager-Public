# Bifrost Server Manager — customer distribution

Bifrost manages customer Controllers, explicitly approved Hosts and game instances through signed jobs and reviewed local policies. The private TROA licensing/owner master is a separate deployment and is excluded from these packages.

## Current status

`v0.1.0-installtest.34` is a local unpublished candidate. Its source adds whole-release signature verification and encrypted database/configuration/key checkpoints with recovery into a new database. Existing production/customer data and earlier release assets remain preserved. No candidate install command is advertised until publication and independent approval are complete.

The historical published prerelease is [Test 33](https://github.com/troainc/Bifrost-Server-Manager-Public/releases/tag/v0.1.0-installtest.33). Its earlier acceptance and signature limitations remain historical; it is not evidence for this candidate. [Earlier delivery records](Docs/History/README-before-release-readiness-2026-10-21.md) are retained.

Read [supported scope and acceptance](Docs/Supported-Release-Scope.md), [update recovery and key rotation](Docs/Recovery-and-Key-Rotation.md), and [standalone installation](Docs/Standalone-Installation.md). The initial beta promise is Linux x64, one Controller replica, reviewed exact game recipes and explicit operator ownership. Native Windows packages, SE2, no-Wine SE1 and optional Gate/bridge integrations are outside this candidate's beta support promise pending their own acceptance.

## Artifact and update policy

Installer/updater code pins the candidate release signer and verifies a signed version/source/artifact manifest before executing a downloaded updater or loading customer packages. Customer code never downloads a private signing key. Initial bootstrap instructions must pin the exact installer checksum through an independently reviewed channel. Offline signatures authenticate bytes; they do not approve publication, manual acceptance or privacy policy.

Updates require the existing non-root service account and retained keys, stop platform writers, verify an encrypted PostgreSQL checkpoint, and journal configuration/schema changes. Recovery authenticates the checkpoint, creates a new database, restores exact configuration and keys, and preserves the original failed database. Escrow the separate recovery key and retain old images. Normal update/recovery never resets worlds, removes databases or runs a volume wipe.

## Verification and release

Run shell syntax/bootstrap synchronization, Python installer/signature/recovery regressions and Node diagnostic tests before packaging. The private build pipeline compiles matched public-only Controller/web/Host artifacts, verifies owner exclusion and exact image identity, records dependency/SBOM and scan evidence, and signs only source-bound local candidates with passing automated gates. Exact target OS/game/player, accessibility, production configuration/key escrow, qualified privacy review and external repository/CI approvals remain explicit requirements before rollout.

Use [AGENTS.md](AGENTS.md), [CONTEXT.md](CONTEXT.md) and [LOGS.md](LOGS.md) for current local work. Do not replace earlier release assets or describe source/fixture checks as customer machine acceptance.
