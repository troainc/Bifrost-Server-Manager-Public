# Scheduled panel updates — production candidate, November 12, 2026

## Existing installations

The supported Alpine PostgreSQL panel layout already supports a signed in-place update. It preserves accounts, MFA, configuration, credentials, database volumes and Host enrollment. A Controller update restarts panel services; it does not update or restart enrolled Agents or game processes. Earlier Debian PostgreSQL layouts still require separately reviewed backup/restore migration. Source-managed TROA master deployments use their deployment platform.

## New candidate

`automatic-panel-updates.py` adds an optional local systemd user timer. It is disabled until the local service account explicitly enables it. It checks once daily at 04:00 server time with up to ten minutes of jitter; missed windows are skipped. Stable is the default channel. Installation-testing users must explicitly select testing. Switching a testing installation to stable requires a manual reviewed transition; scheduling cannot downgrade or change channels.

The helper selects only a newer matching-channel release from the fixed public repository. It authenticates the pinned Ed25519 publisher, signed version-bound and expiring manifest, verifier bytes and exact updater bytes before execution. It refuses releases without signed unattended-update support, insufficient disk space, three retained checkpoints, interrupted recovery, changed policy/version, unsafe paths, or competing updates. Download staging is temporary and removed. Recovery checkpoints, existing image versions, databases and game data are never pruned. Review/escrow retained checkpoints through the recovery runbook before scheduling further updates.

The updater retains licensing and disclosure settings in unattended mode. The signed existing recovery helper takes an encrypted checkpoint before applying changes. Failed or interrupted apply requires explicit recovery review; scheduling does not force rollback, remove a lock, replay an uncertain operation, or re-enroll a Host. Status is a bounded local JSON record and history is retained in the systemd journal. No inbound port, Controller Docker socket, master-initiated execution, credentials or arbitrary command interface is added.

## Use after a new signed release containing this helper is published and accepted

Run as the existing non-root `bifrost` service account. The helper is included at the fixed installation path in fresh bundles and installed by the matching in-place updater.

```sh
python3 "$HOME/.local/share/bifrost/scripts/automatic-panel-updates.py" enable --channel stable
python3 "$HOME/.local/share/bifrost/scripts/automatic-panel-updates.py" status
python3 "$HOME/.local/share/bifrost/scripts/automatic-panel-updates.py" check
python3 "$HOME/.local/share/bifrost/scripts/automatic-panel-updates.py" disable
```

Testing installations use `enable --channel testing` after explicitly choosing to accept future signed testing releases. `check` verifies a plan without applying it. `run` uses the saved local policy and applies at most one newer release. Disabling prevents future scheduled starts; it does not kill an update already applying. Inspect `journalctl --user -u bifrost-panel-update.service` for outcomes and the retained recovery journal before retrying after interruption. The administrator controls checkpoint escrow and disk maintenance.

This source candidate does not modify Test 38 assets, install/enable any timer, update a remote machine, publish a new release or add automatic Host/game updates. Test 38's immutable updater lacks the new unattended marker and is refused by the helper. A new matched signed release is required.

## Validation

No checks execute on the owner's PC. Hosted Python tests use temporary signed fixtures to exercise channel/consent, exact-version apply, substitution, signature/signer/expiry refusal, downgrade, interruption, storage/checkpoint bounds, destinations and cleanup. Existing installer, recovery and image-store suites remain required. Real systemd timer execution, concurrent manual update, lost network/power, preserved accounts/MFA/keys/Host/game state and operator recovery acceptance must pass on the designated server before production approval.
