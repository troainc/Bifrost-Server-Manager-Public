# Public distribution production-readiness audit — November 13, 2026

## Verdict and scoring

**Engineering readiness: 8/10 as a release candidate, conditional on the matched application checks. Operational acceptance is pending.** Scores are strict judgments from source and hosted evidence, not probabilities, a security certification, or a promise that every game works. Supported released functions are assessed separately from gated/optional features. A published catalog name does not establish an installable or accepted game.

| Category | Rating / 10 | Evidence and remaining limit |
|---|---:|---|
| Customer/owner separation | 9 | Compiled customer artifacts exclude private issuer/owner modules and authority. Licensing does not grant customer execution authority. |
| Authentication, permissions and auditing | 9 | Shared application retains MFA, CSRF, signed jobs, exact confirmations, actor/action/target/outcome history and append-only grants. Users do not enter action reasons. |
| Dependency/image security | 8 | Matched runtime and dependency gates block configured severities; pinned source and image identities are verified. Low-severity findings and independent penetration testing are not represented as absent. |
| Operational UI/UX | 8 | Flat sections/rows, clearer setup/settings separation, readable text, touch controls and keyboard focus replace decorative/nested designs. |
| Automated accessibility | 8 | Shared application runs measured WCAG A/AA/contrast checks against both build editions. Incomplete checks and real screen-reader acceptance remain explicit limits. |
| In-place installation/update | 8 | Supported Alpine PostgreSQL panels update without reinstalling, resetting users or re-enrolling Hosts. Earlier Debian layouts are refused pending a reviewed migration. Actual full target updater acceptance remains required. |
| Automatic updates | 8 | Local opt-in, pinned publisher/manifest/verifier/updater, compatible-family selection, single-flight locks, storage/checkpoint/recovery bounds and bounded diagnostics. Real systemd behavior passes with a controlled signed Bash fixture; full Docker cutover/power loss remains manual. |
| Recovery and retained data | 8 | Real PostgreSQL encrypted checkpoints and two new-database restores preserve synthetic account/MFA/Host/settings/journal state. Recovery-key escrow and target restore timing remain operator acceptance. |
| Packaging and provenance | 9 | Matched frozen sources, checksums, SBOMs, image identity and compiled Host isolation are verified. Test 39 remains unsigned/unpublished until a separately approved release. |
| Fleet performance | 7 | Bounded read/query policies and hosted sustained fleet profiles improve the baseline. They do not certify game execution capacity, target hardware, long-duration soak or Internet/TLS performance. |
| Runtime/game compatibility | 7 | Hosted Linux/rootless and Windows service/provisioning fixtures pass. Every actual game/runtime/plugin/mod/platform combination still requires target acceptance and remains gated accordingly. |
| Operator diagnostics and consent | 8 | Actionable secret-free failure codes, retained journal/checkpoints, explicit version-family review and reliable opt-out. Diagnostics do not silently repair or replay uncertain work. |
| Real production acceptance | 6 | Source/fixture readiness is stronger; the owner's server, game/player, complete automatic apply, interruption and recovery checks are still pending. |

## Additional corrections from this audit

- Release discovery follows at most five 100-release pages. A full bounded history is refused with `release-discovery-limit`, instead of incorrectly claiming the installation is current. Malformed later pages also refuse before downloading or applying assets.
- Routine automatic-update consent no longer authorizes a stable major-version change, or a 0.x minor-version change. Those transitions require manual review. An available compatible-family update is still selected when a newer family also exists.
- Systemd directories are created privately under any caller umask, validating existing parents instead of changing their permissions. A group-writable Ubuntu umask previously made newly created directories fail the ownership/containment check. Existing unsafe parents still fail closed.
- Disabling scheduling can revoke consent even if the installed driver file is missing. It disables future timer starts without killing an already applying service.
- The shared interface's measured audit corrects button/metadata contrast and names fleet-filter/history controls, beyond the prior visual-only review.

## Exact public source and hosted evidence

Frozen executable/tooling source: `5813fc986226135d7e5629c82f7ee9c2c30767c2`. Later documentation-only finalization does not change those tested bytes.

- [Installer/configuration and real systemd](https://github.com/troainc/Bifrost-Server-Manager-Public/actions/runs/43458488311): 148 Python cases, 145 passing and three root-only cases passing in the separate ownership job; 66 Node cases passing; focused signature/recovery checks also pass.
- The real non-root systemd job enables the local timer without applying immediately, authenticates and executes exactly one controlled signed Bash fixture, proves environment sanitization and NoNewPrivileges, rejects a concurrent helper and held installation lock, refuses an interrupted recovery journal, removes temporary staging, and disables future starts while allowing in-flight completion. Its disposable publisher is injected only in non-shipped test code. Production has no test trust override.
- [Docker-store compatibility](https://github.com/troainc/Bifrost-Server-Manager-Public/actions/runs/43458488331): classic/containerd identity checks pass using the immutable Test 33 compatibility fixture. This is not evidence that Test 39 has been published or applied.
- Shared interface, exact compiled package, private-module exclusion, security, sustained fleet profiles and real database checkpoint/restore evidence are recorded in the matched application's review report and release provenance. Do not substitute a package from another source revision.

All tests/builds/browsers/containers for this audit run on GitHub-hosted runners. No test or runtime workload runs on the owner's PC.

## Remaining acceptance and deployment boundary

Test 38 stays immutable. Test 39 is an unpublished candidate, not a current stable production release. No existing installation, timer, Agent or game was changed by this audit. The owner will test the selected server manually after the candidate is ready. Merge, release signing/publication and deployments are separate approval steps.

Before production acceptance, validate the actual OS/database layout, retained identities/MFA/keys/worlds, full signed panel update, real timer/apply and manual-update concurrency, lost network/power and explicit recovery, and exact game/player/plugin/mod behavior. Record the supported workload and backup/recovery objectives on the selected hardware. A panel-only update does not upgrade Agents or games.

The [automatic-update runbook](Automatic-Panel-Updates.md) documents local opt-in/disable, recovery, storage/checkpoint limits, release channels, bounded release discovery and compatibility-family review. The new `version-family-review-required` diagnostic is a manual upgrade gate, not a fault to bypass.
