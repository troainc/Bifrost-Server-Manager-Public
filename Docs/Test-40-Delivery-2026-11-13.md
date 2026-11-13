# Test 40 delivery — November 13, 2026

[Test 40](https://github.com/troainc/Bifrost-Server-Manager-Public/releases/tag/v0.1.0-installtest.40) is published as the owner-authorized controlled testing prerelease. Publication does not apply an update to an existing installation. Previous releases remain unchanged; this is not stable/general-production promotion.

Public PR 26 merged into `main` as `e8561996c04ba03d11cf642f1f827e1926b0076b`. Frozen public tooling is `514950478f257475eb2635b60976e80431d2185f`, matched application `96dafbca874da495bf9f51aaa48e14735afe97f3`. Both are retained in merged history. The private owner/issuer source and credentials remain excluded from customer artifacts.

All exact-source hosted application gates pass: CI, operations, security, dependency review, both-edition UI and compiled customer distribution/isolation/recovery. Public [installer/systemd checks](https://github.com/troainc/Bifrost-Server-Manager-Public/actions/runs/43482580047) and [Docker-store identity checks](https://github.com/troainc/Bifrost-Server-Manager-Public/actions/runs/43482580223) pass. Customer UI passes 150 screen/theme/viewport checks and 68 accessibility states with zero automated A/AA violations; incomplete criteria remain manual. [Customer design rerating](Operator-UI-Audit-2026-11-13.md) is 7.9/10, a design judgment rather than target acceptance.

Release `444602042` was published at **18:42:35 UTC**. All **25 public assets** anonymously downloaded over HTTPS match exact signed sizes/SHA-256. Both installer/updater offline verifiers passed before publication. The signed manifest includes exact source identities, SBOMs, image identity/security evidence and explicit outstanding manual acceptance.

| Artifact | SHA-256 |
| --- | --- |
| Installer | `1c0c40ae1d1061d3b16195b3b7f53b1b02aedd320ce2f2f1fc849aae12fb5b36` |
| Updater | `f72ba423a698d15761dc8d07fa8ae7170321d2b0b72a43256ebd3d5e756fd5fa` |
| Linux bundle, 222,537,416 bytes | `2ed94b457263910ac14b5caa47970ffd359503810032c3244f6bed5e0b849e71` |
| Manifest, 4,044 bytes | `4f4b4d9b4db888500de6889c7673fa6e9b3e58f8f34240ef4ec5e25827865f78` |
| Signature, 64 bytes | `b14c8922a87ea11c5d4afdf8eecef20655af7fd95c517ebc8cc4c4563af09aba` |

The release signer SPKI is unchanged: `1dba79e7a3d2608b42a5324089d4db548567999210ffbf3dd96ce5cb63a92e6a`. The existing offline private key never left its location. No tests/builds/previews/containers/WSL workload ran on the owner's PC; only the small manifest was signed there, and large assets stayed off local disk.

The [TROA tester page](https://therealmsofasgard.com/gaming-hub/bifrost-server-manager#testing-installation) now serves Test 40 Debian `su` and Ubuntu `sudo` fresh-install commands plus separate panel-only updates. Website PR 130 merged/deployed; all 488 hosted units/build/types pass. Live readback at **18:46:38 UTC** verified the exact published installer hash, all four commands, valid/invalid password handling and no-store. Reset payload/wipe controls are absent. No installer/updater was executed by that verification.

The owner will manually test the customer instance. Real OS/game/player, complete updater interruption/recovery, assistive-technology and long-soak acceptance remain open. No existing customer, Host Agent, game, timer or enrollment was changed during this delivery. Scheduled updates remain opt-in/off by default. Use the in-place update path for an existing supported panel and retain its recovery material.
