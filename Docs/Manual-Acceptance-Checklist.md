# Customer beta acceptance checklist

This candidate is unpublished and not approved for general beta or stable release. Complete this checklist on disposable, representative VMs and copies of retained data. Never test deletion, corruption, outages or recovery against the only production copy. See [scope](Supported-Release-Scope.md), [installation](Standalone-Installation.md), [recovery](Recovery-and-Key-Rotation.md) and [host prerequisite security](Prerequisite-Security-Review.md).

For each item record tester/reviewer, date, OS, exact signed private/public source revisions, artifact hashes, expected/actual result and sanitized evidence. An unchecked item is unaccepted. A historical prerelease or a passing generic fixture does not qualify this candidate. Recheck changed components after fixes.

## Before installation

- [ ] Independently approve the exact host Docker/Compose, rootless Podman and Node baseline, maintained patch and future update ownership. Verify the separately signed local patched prerequisite candidate as well as the Bifrost application signature. Unchanged vendor archives remain blocked; automatic Docker/Compose download stays paused. Test actual target OS systemd/cgroup CPU/memory/process enforcement. Read-only inventory and local signatures do not approve deployment.
- [ ] Verify every local signed release asset with `bash install.sh --verify-release /absolute/release-directory`. Retain both signed source revisions and signature identity. Missing, altered or linked assets must refuse. Do not use online Test 35 commands before separate publication approval.
- [ ] Confirm isolated panel/game accounts, rootless runtimes, subordinate IDs, private directory permissions, reviewed TLS hostname/trust, host firewall/ports, free disk/RAM and service persistence after logout/reboot. The game account must have no panel socket, sudo or issuer credentials.

## Fresh installation and access

- [ ] Test clean Ubuntu 24.04 and Debian 12 x86_64 separately. Complete Controller, standalone Instance and Hybrid journeys on the combinations actually offered for beta. Record any untested combination as excluded.
- [ ] Finish first administrator, mandatory MFA, recovery-code use and administrator installation-license/legal review in a real browser over verified HTTPS. A second setup attempt must refuse. Sign-out, expiry, reset and lost-MFA support procedures must preserve authorization boundaries.
- [ ] Test viewer/operator/administrator permissions and assigned Host boundaries. Wrong account, wrong origin/CSRF, missing MFA, expired session, disabled user and last-admin removal must refuse without mutation. Confirm customer UI/API/images expose no owner licensing-master functions.
- [ ] Pair a separate Host with explicit local identity/capability approval. Wrong TLS identity, expired/reused receipt, denied/revoked Host and wrong Controller must refuse. Test standalone-to-parent handover, drain/recovery and mixed supported Host versions without transferring authority implicitly.

## Games and operations

- [ ] For EACH game/recipe claimed at beta: record signed recipe/runtime, actual download/create, real remote player join and ports, start/stop/restart, graceful save, configuration/file boundaries, update with retained world, and recovery after reboot. Include Torch/Wine only if actually qualified. Untested games remain excluded; Windows, SE2, native no-Wine SE1 and optional previews are not qualified by this checklist.
- [ ] Restore an encrypted game-world backup into a separate stopped instance using escrowed keys; compare world/configuration, join with a player and measure recovery time. Interrupted restore, bad signature, altered backup, wrong key and insufficient space must refuse or preserve recoverable originals.
- [ ] Interrupt Controller/Host/network during a real lifecycle operation. Verify durable uncertainty, no automatic duplicate execution, bounded output, exact-job visibility, expiry and MFA/proof-bound reconciliation. Confirm revocation and role change stop new work. Never infer a stopped game from a heartbeat failure.
- [ ] Exercise license-service/network outage, clock issues and recovery. Observe the documented grace/expiry policy and verify licensing failure does not stop already running games or grant fleet authority.
- [ ] Test backup/download concurrency, slow storage, disk growth/full conditions and representative operator load against agreed latency/storage budgets. Validate only the supported single application replica.
- [ ] Deliver alerts to an explicitly approved test destination; verify redaction, mention suppression, duplicate handling and disconnected-Host visibility. Record support/on-call owner and retention/backup policy.

## Preserved-state upgrade and recovery

- [ ] On copies of an existing supported installation, upgrade Test 33 to the exact candidate with the matched updater. Compare accounts, roles, MFA, licenses, configuration, worlds, job/audit history, catalog and key fingerprints before/after. No wipe/re-enrollment or silent key replacement is acceptable.
- [ ] Rehearse interrupted update and authenticated checkpoint recovery into a NEW database, preserving the failed original and exact secrets. Check retained managed-key volume mounting and licensing trust overlap. Unsupported old Debian database runtimes must refuse before mutation; use a separately reviewed logical migration, never relabel an old volume.
- [ ] Restore an off-host checkpoint with escrowed keys to a second VM; verify login, least-privilege grants, Host identity, game/world recovery and measured RPO/RTO. Confirm a documented reversal path before accepting upgrades.

## Browser and approvals

- [ ] Use keyboard only, screen reader, 200% zoom, narrow mobile layout and reduced motion. Test setup/MFA, pairing, Fleet search/pagination, job feedback, backup/recovery, permissions and confirmation dialogs; verify focus, labels, errors and reconnect behavior.
- [ ] Approve supported OS/game/version matrix, exclusions, patch/support policy, storage limits, recovery targets and incident contact. Record qualified privacy/data-retention and dependency-license review plus installation-specific consent. Testing intake is not general-intake approval.
- [ ] Independently approve code/security review, signer custody/escrow/rotation and exact-revision hosted CI. Maintainers must activate reviewed branch protection, separate tag creation and immutable update/deletion rules, and a release environment with self-review/admin bypass disabled.
- [ ] Obtain separate explicit authorization for push, deployment and publication. None is granted by local tests, this checklist, or a candidate signature. Stable release additionally requires observed beta operation and incident/recovery evidence.
