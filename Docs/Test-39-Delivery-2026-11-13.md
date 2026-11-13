# Test 39 delivery — November 13, 2026

## 2026-11-13 — Website handoff verified

The live TROA Server Manager page now provides Test 39 Debian/Ubuntu fresh-install and panel-only in-place update commands behind its existing tester gate. The reset payload, wipe controls/hints and stale action-reason guidance are removed. Full hosted website units/build/typecheck and live command readback passed. The owner performs the actual public-server acceptance; no installation/update or game operation was applied here.

## 2026-11-13 — Signed Test 39 published and anonymously verified

Owner authorized the matched public testing release and website install/update instructions. PR 25 merged into main as 69b3f1e58622a037dea1cb10eac0ce121be23546. Immutable signed v0.1.0-installtest.39 (release 444484964) is published; all 25 assets anonymously downloaded over HTTPS match exact signed size/SHA-256. Frozen application source is 5d10c56212dcd00ef01d6be7464fd8018242b738, packaging source 5813fc986226135d7e5629c82f7ee9c2c30767c2. Installer SHA-256: 64c6b79b37cac1c55ff87036184a607e8f7958e1c54ba2864d8a5bcab83a28c1. Both exact offline bootstrap verifiers pass before publication. Prior releases stay immutable. Publication does not apply an update to any existing server.

The owner will test the public server manually. No existing customer installation, timer, Agent or game was changed; no stable promotion is implied. Full target updater/interruption/recovery, actual game/player/runtime, screen-reader and long-soak acceptance remain pending. All tests/builds run on hosted runners, with no PC runtime/WSL workload; the existing offline key signed only a small manifest and never left its original location. Large assets stayed off the PC. See Docs/Test-39-Delivery-2026-11-13.md. The prior scored audit records pre-publication history; this new owner-authorized delivery supersedes that hold.

[Signed Test 39 release](https://github.com/troainc/Bifrost-Server-Manager-Public/releases/tag/v0.1.0-installtest.39). The release manifest binds exact artifact/source identities and retains outstanding manual acceptance. Optional automatic updates remain disabled until explicitly opted in locally. Follow the [automatic-update runbook](Automatic-Panel-Updates.md); a panel update does not upgrade Agents or games.
