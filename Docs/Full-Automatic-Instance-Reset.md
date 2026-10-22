# Full reset before a fresh automatic Instance installation

## Stale certificate recovery for an empty local Host

Normal automatic reset still refuses mismatched certificates. If the protected
pre-enrollment Host bootstrap retains an old certificate but the current local
Instance uses exactly the same HTTPS origin, use the explicit read-only
`--review-stale-prejoin` mode. It accepts only the strict empty pre-enrollment
Host plus a panel bootstrap exactly `{"enabled":false}`, and different valid
public certificates. Any enrollment config/token/receipt, work ledger/lock,
game data/runtime, custom units, wrong origin, enabled panel capability,
Controller/Hybrid role or foreign/shared resources still refuses.

`--apply-stale-prejoin-reset` repeats all checks and asks for **WIPE STALE LOCAL
HOST**, then **WIPE ALL**. Both plans are checked again before either cleanup;
the empty Host is checked after worker shutdown. This explicitly destroys only
the reviewed local installation. It does not prove old certificate ownership,
trust that certificate, contact a remote panel, or repair enrollment in place.
The main site's reset command selects this recovery only after its separate
read-only review succeeds; it cannot confirm either phrase for the owner.
Other refused states stop without reinstalling. Use only on the disposable
public test Instance intended to be wiped, never the master or shared host.

## Automatic review, including a disabled pre-enrollment bootstrap

Use the current checksum-pinned helper with `--review-auto` and
`--apply-auto-reset`. Automatic review selects the existing strict enrolled
path when `host-agent.json` exists (including a linked path, which refuses),
otherwise it requires the strict empty pre-enrollment Host review. A prepared
Host with a panel bootstrap exactly `{"enabled":false}` is accepted only when
the protected game bootstrap has the SAME HTTPS origin and public certificate
as that Instance panel. No capability is enabled or regenerated.

Before any deletion, both accounts must have standard homes, the expected
service templates and protected paths. No enrollment token/receipt/config,
ledger/lock, unknown configuration, game files, game containers, game volumes
or foreign game networks may exist on the pre-enrollment path. Rootless runtime
checks and canonical path/link/ownership protections remain mandatory. Known
panel volumes may include the standard `controller_key_data` volume only with
its exact Controller mount; foreign, external and shared volumes still refuse.

Review is read-only. Apply repeats review, requires an interactive terminal and
exact `WIPE ALL`, rechecks BOTH component plans before beginning cleanup, stops
the managed workers and rechecks the empty Host state after shutdown. Changed
state refuses. Unrelated files, OS accounts, compiled Host packages, other
workloads, the private master and router settings are outside the reset scope.
The matched Test 35 installer runs only if apply exits successfully.

The main-site Debian wipe command includes `su`, verifies the immutable helper
and Test 35 installer hashes before execution, and remains separate from fresh
installation behind the existing tester password gate. No inline helper patch
or forced cleanup is needed. Earlier release assets remain immutable.

The root CLI regression fixture covers enabled and disabled bootstraps,
origin/token/role mismatch, cancellation, exact confirmation, real service-user
subprocesses and filesystem removal while retaining unrelated markers. Runtime
responses are simulated inside network-disabled disposable Debian containers;
this does not claim the owner's actual server was reset.

The legacy `--reinstall` path is disabled in the unpublished October 22 follow-up. Do not use it as a reset or update workflow. The historical published Test 35 command only resets a panel and refuses an automatically enrolled Host; use this separately reviewed strict reset helper for an explicitly authorized complete disposable-Instance reset.

The separate `scripts/reset-automatic-instance.py` supports a standard Debian/Ubuntu automatic Instance with the dedicated `/home/bifrost` panel and `/home/bifrost-games` Host. Run the checksum-verified helper as the VM administrator with `--review` to inspect the bounded reset scope, or `--apply-reset` to repeat the review and request the exact `WIPE ALL` terminal confirmation before any reset action. Run the matched, verified `install.sh --instance` only after `resetCompleted:true`.

For an Instance stopped during browser setup or licensing before local Host enrollment, use `--review-prejoin` and `--apply-prejoin-reset` instead. This separate mode verifies the installer-provided bootstrap against the panel origin, public certificate and private capability without printing the capability. Both fixed user-service templates must match, the game runtime must be rootless and empty, and no enrollment receipt, Host configuration, token, ledger, unknown configuration or game data may exist. It stops and verifies both managed services, then repeats the complete review before removing the prepared Host configuration and panel. If enrollment starts during shutdown, it refuses and preserves remaining files. It still requires `WIPE ALL`. It supports a standard automatic Instance, not a Controller, Hybrid or custom installation.

The original reset asset in test26 remains immutable. Incomplete-setup reset commands must download a checksum-pinned newer public source revision of the helper, then use the test26 release installer. A panel-only wipe would leave the old local bootstrap capability and services referencing a replaced panel, so it is not the clean automatic Instance test.

The full reset permanently removes the local panel database, administrator, licensing configuration, credentials, automatic Host enrollment, game worlds and managed local backups. It leaves Linux accounts, prerequisite tools, old compiled Agent packages, unrelated workloads and router rules in place. The parent Controller's old registration is not silently deleted or reused: the new Instance follows normal pairing/approval with a new identity. Revoke the old registration in the parent panel when the replacement has been accepted.

Root coordinates dedicated non-root component owners. Game and panel runtime operations and data removal execute as their respective service accounts. The review refuses custom homes/roots/units/drop-ins, a busy or unfinished ledger, foreign game containers/networks, shared panel volumes/networks and linked reset targets. It locks the ledger, gracefully stops games before the Agent, verifies shutdown, removes reviewed containers without force and deletes only canonical managed trees using Linux fd-based no-follow removal. A changed review refuses cleanup. Cached images are removed only by reviewed identity without force; shared images may remain. No Podman/Docker system reset or blanket prune is used.

An interrupted destructive reset can leave completed portions removed. The helper reports refusal and preserves remaining state; inspect before continuing. This helper is for an explicit full reset, not an update or preserving recovery. The disposable tests simulate runtime replies and exercise real filesystem boundaries as a non-root Linux user. Actual customer reinstall, new download and player acceptance require their own run.

`tests/prejoin-reset-cli-fixture.py` additionally exercises the real root coordinator, dedicated users, `runuser`, terminal cancellation/confirmation and filesystem deletion inside an explicitly opted-in disposable Docker container with a read-only repository mount and no network. Docker, Podman and systemd replies are simulated; that fixture does not establish real daemon shutdown or customer acceptance.

Game ports are selected when creating the new game. The distributed defaults remain game UDP27016 and Steam UDP8766; a site may choose game2750 and forward that same port to its Host. The signed Torch storage minimum is20GiB plus the normal free-space margin and queued reservations. Router configuration is site-specific and is not changed by the installer or reset.
