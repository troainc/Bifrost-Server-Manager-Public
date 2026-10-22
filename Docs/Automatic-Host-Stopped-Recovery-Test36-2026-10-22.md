# Test 36 Host: recover after the confirmed shutdown timeout

The tester's existing panel is already Test 36. The initial Host-only updater reached Agent shutdown but did not replace its service file. The supplied diagnostic reports a failed timeout with MainPID=0, ExecMainCode=1, ExecMainStatus=0, empty ControlGroup and Job, and TasksCurrent=[not set]. The process-name list still includes Torch.Server.exe and Wine; player/game health is not established by that list.

The initial updater and systemd both used 90-second stop windows. The new source gives the stop subprocess 120 seconds and independently observes completion rather than treating only the command's exit result as authoritative. The exact remaining-child reason for the original systemd timeout has not been established from the supplied status fields.

The explicit --resume-stopped mode accepts only the exact enrolled Test 35 automatic unit with a fully stopped, empty service and no pending systemd job. It verifies the retained Test 36 candidate archive/files, protected state and compiled job preflight before switching the Agent unit. It holds the update and idle-ledger locks, rechecks quiescence before replacement and never repeats the old stop operation for this recovery. An unexpectedly running/changing/uncertain state is refused. Startup failure restores the original unit and leaves an originally stopped Agent stopped. Successful repeat execution verifies the already updated running Agent.

No panel update, database operation, reset, re-enrollment, credential/permission change, setup-worker replacement, game stop/start or container replacement is performed. Old packages/unit backup and every config/token/profile/world remain retained. The existing signed Test 36 assets are unchanged.

## Verification

- Both private and public focused suites: 23/23 passed with real published installer templates/archives and compiled preflight, disposable non-root files and simulated updater service actions.
- New cases cover the exact reported state, fixed-field status queries, staged-candidate recovery without repeated stop, default refusal without explicit recovery, residual/pending-process refusal, stop-call failure with independent shutdown proof and rollback to the original stopped state.
- A real local transient systemd fixture independently reproduced Result=timeout, MainPID=0, ExecMainCode=1, ExecMainStatus=0, empty ControlGroup/Job and TasksCurrent=[not set]. The new guard accepted this fully quiescent state. Only the unique bifrost-qa36-stop fixture was started/stopped/reset; it was cleaned up. No production/tester service was accessed by this fixture.
- Private/public cwd regressions and Bash syntax remain passing. The complete public suite passed all 66 tests with no skips. The previous installer suite result remains 118 passed with three explicit root-only skips; installer source did not change in this follow-up.

Evidence remains in private artifacts/rollout36-20261022/automatic-host-upgrade36-stop-tests.log, automatic-host-upgrade36-stop-private-tests.log, automatic-host-stop-full-public-node.log and automatic-host36-real-systemd-timeout.json. The observed real-systemd stop command itself returned success even though the unit Result was timeout; the helper now checks state in both success/failure branches.

The earlier helper at public source 628b8a4 / SHA-256 f70cc9d63dd69ac2f5432013087db573abb64c8e1c542ebe8ad7efa42ff18b3a remains immutable but its ordinary command is withdrawn for this stopped tester state. Actual recovery, new Agent heartbeat and game/player acceptance remain pending until the tester runs the new checksum-pinned command.

## Published stopped-service recovery command

Public immutable source: 1a2a24f0f1b81c50bdf0e2f57cfe7f428e9cefd3; matching private source: 5e435b4c7b78bceef61d4ffeee35d1a0a40e2b7a. Anonymous verification confirmed the complete 20574-byte helper matches the tested source, SHA-256 720b0436d684773693d39ceb08aa8a35bed0e8d4026baa90f151040bd8e7dccc. Source pushes used [skip ci] [skip cd]; master read-only verification still shows running:healthy on unchanged deployment p4ejr6vosnflqnflzukfuuey and application source 2490263a4e7e6a61f22c6f551b6a26414971c07e. No master deployment, asset overwrite or paid CI.

Run on the same tester VM with the confirmed fully stopped old automatic Host and already updated panel. The helper rechecks the actual state and refuses a changed or unsafe one. Enter the Debian root password. This mode does not repeat shutdown of the old Agent; it switches the validated unit and starts the new Agent. Keep the old package/unit backup and panel checkpoint. Actual tester execution, heartbeat and game/player acceptance remain pending.

```bash
su -s /bin/bash -c 'set -euo pipefail; export PATH=/usr/sbin:/usr/bin:/sbin:/bin; cd /home/bifrost-games; game_uid=$(id -u bifrost-games); stage=$(mktemp -d /tmp/bifrost-host36-recover.XXXXXX); chmod 0755 "$stage"; curl --proto "=https" --proto-redir "=https" --connect-timeout 15 --max-time 180 --max-filesize 65536 -fL --retry 3 https://raw.githubusercontent.com/troainc/Bifrost-Server-Manager-Public/1a2a24f0f1b81c50bdf0e2f57cfe7f428e9cefd3/scripts/upgrade-automatic-host-testing36.mjs -o "$stage/update-host.mjs"; printf "%s\n" "720b0436d684773693d39ceb08aa8a35bed0e8d4026baa90f151040bd8e7dccc  $stage/update-host.mjs" | sha256sum -c -; chmod 0644 "$stage/update-host.mjs"; runuser -u bifrost-games -- env -i HOME=/home/bifrost-games USER=bifrost-games LOGNAME=bifrost-games PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin XDG_RUNTIME_DIR="/run/user/$game_uid" DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$game_uid/bus" /opt/bifrost-node-v24.19.0/bin/node "$stage/update-host.mjs" --resume-stopped' root
```
