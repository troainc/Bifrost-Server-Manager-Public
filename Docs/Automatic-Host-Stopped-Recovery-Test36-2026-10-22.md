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
