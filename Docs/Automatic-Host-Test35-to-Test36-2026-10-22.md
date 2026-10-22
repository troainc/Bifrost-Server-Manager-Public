# Automatic enrolled Host: Test 35 to Test 36 correction

**Stopped tester follow-up:** the initial command below failed at Agent shutdown. The supplied diagnostic confirms the old Agent is now fully stopped with a timeout result; the game processes remain present. Use only the [explicit stopped-service recovery](Automatic-Host-Stopped-Recovery-Test36-2026-10-22.md), which retains data and does not repeat the stop operation. The earlier ordinary command is withdrawn for that state.

The public tester completed the panel update to Test 36. The subsequent Host Agent step stopped before Agent replacement. Its rootless Podman probe hid the underlying error: the game account inherited /home/troa and could not traverse it. The tester diagnostic confirmed HOST_LAYOUT=automatic, PODMAN_EXIT=1 in the inherited directory, then true / PODMAN_EXIT=0 from /home/bifrost-games.

The previous combined update command is withdrawn. The generic manual Agent installer deliberately refuses automatic Hosts, while the pre-join resume path refuses existing enrollment. Those restrictions remain in place. A separate narrow helper now supports the standard, already enrolled and active automatic Test 35 Host, after its panel has successfully updated. It does not reinstall the panel, re-enroll a Host or change Podman privileges.

## Scope and safeguards

Source: scripts/upgrade-automatic-host-testing36.mjs in both repositories. The command-line entry accepts only the fixed bifrost-games account, protected Node 24.19.0 runtime and automatic service layout. It uses the game home as its working directory and requires rootless Podman. Unexpected/custom service templates, writable or linked paths, active setup, active/uncertain jobs, foreign locks or changed credentials cause refusal.

## Published Host-only command

Public source commit: 628b8a4d1921836227878a1d0b492e4ecf16db72. Matching private source correction: 444431b. Both source pushes used [skip ci] [skip cd]. The immutable anonymous helper download was verified byte-for-byte against the tested source: 17804 bytes, SHA-256 f70cc9d63dd69ac2f5432013087db573abb64c8e1c542ebe8ad7efa42ff18b3a. The existing public archive also matched through the production download adapter. After source pushes, the master remains running:healthy on the same p4ejr6vosnflqnflzukfuuey deployment / 2490263a4e7e6a61f22c6f551b6a26414971c07e application source. No master deployment was requested or triggered.

Run only on the existing enrolled automatic Test 35 Host whose panel has already updated to Test 36. Enter the Debian root password at the su prompt. The verified helper runs as bifrost-games from its home. This command does not repeat the panel update and has no wipe, reinstall or re-enrollment action. Outer and inner Bash syntax are checked; actual tester service/heartbeat acceptance remains pending.

The initial ordinary command has been removed here to prevent retrying it against the stopped Agent. Use the explicit recovery guide linked above.
The helper downloads the existing immutable Test 36 Linux Host archive over bounded HTTPS and checks its exact pinned digest. It verifies retained candidate package files against every archive entry before executing the new compiled preflight. It retains the old package and backs up the original Agent unit before an atomic replacement. A private update lock serializes corrections; an idle queue-poll lock gets a short bounded retry window and is never forcibly removed. The ledger lock is held across the Agent service switch, and startup failure restores the original known unit when protected state is unchanged. Changed credentials or unresolved jobs are preserved for operator review.

Only the Agent service is briefly stopped/restarted. No game process/container, world, player data, catalog policy, profile, token, enrollment identity, bootstrap, setup-worker unit, panel configuration, database or volume is written. The old setup worker remains pointed at its retained original package; do not prune that package. Normal game/player changes made concurrently by the running game are outside the helper's writes.

Protected 0755 intermediate directories created by mkdir -p are accepted inside the private 0700 game home; secret/service files and final private directories still require private modes. The helper never changes retained permissions to bypass validation.

## Frozen identities

- Previous Test 35 Linux Host archive SHA-256: 53f28e0dc131ad83a53f13b59c8359175aa0e92b86926660adc7d83b5ef00d4e.
- Target Test 36 Linux Host archive SHA-256: 5aa8e9e80e2cbb89419c88a005bb5c9207f09aa9932e4a43aa96879bcb8793ad (933333 bytes).
- Helper source SHA-256: f70cc9d63dd69ac2f5432013087db573abb64c8e1c542ebe8ad7efa42ff18b3a.
- Test 35 installer fixture SHA-256: 31c4e58c235f5d6103e48f07a86a12aafe299c16679c8d9f8aa777919815a6c1.

The existing signed Test 36 release assets, prior releases and prerequisite baseline remain unchanged. The additional source-only installer cwd corrections are not claimed to modify the published Test 36 installer or Host archive.

## Verification and limits

Both source copies passed 17 focused non-root Linux checks. Fixtures independently reconstruct service bytes from the actual published Test 35 installer, use the real Test 35/36 archives and execute the real compiled Test 36 preflight. Checks cover exact preservation and repeat execution, incompatible/custom/active setup, running jobs, retained/transient locks, failed startup/readiness rollback, concurrent enrollment changes, altered retained packages/preflight refusal before execution, links and writable parents. systemd actions are simulated; no real tester or master service was changed by these tests.

The installer regression suite passed 121 tests total: 118 passed and three root-only cases skipped. The real public Host preflight cwd reproduction, private script cwd reproduction, Bash syntax checks and signed-bootstrap synchronization check passed. The production HTTPS download adapter anonymously fetched and hash-verified the exact public archive through Windows. The local WSL network timed out reaching GitHub; it is not claimed as a successful Linux network-path acceptance. All Linux filesystem/preflight checks use the already verified local published archives.

The complete public Node suite additionally passed all 60 tests with no skips, including the historical preserving updaters and the new correction. Its existing workflow now supplies exact checksum-verified Test 35/36 fixture inputs for the new checks; this delivery uses skip markers and does not trigger paid CI.

Evidence is retained privately under artifacts/rollout36-20261022/automatic-host-upgrade36-tests.log, automatic-host-upgrade36-private-tests.log, automatic-host-installer-regressions.log, automatic-host-full-public-node.log and automatic-host36-publication.json. Source publication and anonymous immutable helper verification completed before issuing the command above. No paid CI, billing change, master deployment, game command or data reset is required.

## Tester acceptance after the command

- Confirm updatedTo v0.1.0-installtest.36 and serviceActive true; keep the original Agent unit/package and panel recovery checkpoint.
- In the Controller, confirm a fresh heartbeat, the same existing Host/instance identities and the new Agent version/capabilities. Heartbeat acceptance is pending even when systemd reports active.
- Confirm the existing game remains available and worlds/settings/accounts are retained.
- Continue the separate live Console, first-party Torch plugin and chosen mod/plugin checks in Test-36-Rollout-2026-10-22.md. Installing a game plugin remains an explicit stopped-game action; this Agent update does not install one.

If the helper reports a refusal, retain its fixed stage/code and report it. Do not reset, re-enroll, remove locks, change permissions or force a custom unit replacement to bypass it.
