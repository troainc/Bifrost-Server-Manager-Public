# Test 53: browser onboarding and preserved Host recovery

Instance setup now has four essential stages: choose management, secure the
administrator, activate the free license, and connect the game Host. Joining a
fleet collects the Controller address and its fresh five-digit code together
after activation. The administrator confirms the destination and requests access;
the chosen Controller administrator approves it. Prepared Debian/Ubuntu Hosts
finish connection automatically and wait for their authenticated first heartbeat.
Manual Host instructions remain available for installations without preparation.

Licensing never chooses a parent or grants TROA control of a customer's fleet.
An independent installation stays independent. Customers may run their own
Controller/Hybrid and invite their own machines. Controller identity, MFA,
license, CSRF, signed receipt and administrator approval protections remain.

## Retained Host state

The setup page reads saved state before enabling connection. It distinguishes a
fresh join, a resumable request, an existing Host requiring reviewed handover,
unresolved work, and a narrowly recoverable empty revoked local Host. Existing
connection destinations cannot be silently changed. Conflict messages explain
the actual blocked condition instead of combining unrelated causes.

A revoked Host record is not an empty database. Recovery is offered only for the
one revoked local-bootstrap Host belonging to this Instance, with no game,
provisioning or job records. It requires explicit exact-Host administrator consent
and a prepared local worker. After parent approval, the worker independently
checks the old enrollment identity, empty profile/job state and game/backup
storage. It stops the old Agent and archives its private configuration, token,
backup key and enrollment state with a resumable journal. It never deletes the
revoked record, reactivates its credential, wipes a database, moves game data or
replaces another Controller's Host. Backup-key metadata is preserved; actual game
or backup files refuse this empty-Host path and require reviewed handover.

## Verification and limits

Fresh Linux regression: 2,413 passes, zero failures, 11 explicit environment
gates. Real migrated PostgreSQL HTTP acceptance: 37 checkpoints, including explicit
revoked-Host consent, preserved history, game-data refusal and destination-bound
resume. Nine filesystem cases cover archival, keys, symlinks, identity mismatch,
job/backup refusal and interrupted rename recovery. The actual compiled Agent
verifies the parent's signed receipt and sends an authenticated heartbeat after
empty revoked-Host recovery in a disposable Linux integration fixture.

Five compiled-customer Chromium scenarios cover fresh connection, explicit
recovery, existing-Host refusal, saved-request resume and independent management.
Desktop and 390px mobile checks pass with no page errors or external requests.
These are software/fixture checks, not new game/player or real-device acceptance.
All existing SE2 private-asset requirements and other acceptance limits remain.
Upgrading panel software does not automatically authorize a Host or change its
Controller. Preserve account credentials and use supported account recovery if
password or MFA access has been lost; a pairing code cannot recover an account.


## Published delivery

Test 53 release 454943378 is published with 25 signed assets. Every asset was downloaded anonymously and compared byte-for-byte; downloaded Ed25519 signature, complete hashes, exact Host checksum/non-root extraction and tamper refusal pass. The exact shipped customer web bytes pass five desktop/mobile scenarios; the exact shipped Host archive completes signed recovery and an authenticated heartbeat in the disposable integration fixture. Controller/web image scans are fresh and clean; unchanged database scan evidence is inherited.

The public repository, private master and main website were updated. The live Bifrost page serves four matched Debian/Ubuntu install/update commands with installer SHA-256 33ed4da3aac459e46f33cbad480482296d3749bb084a238ccd8aa9d2ee94d4ea. The tester gate and no-store responses remain intact.

The owner's existing Debian test Instance was updated without wiping and explicitly connected to the selected master. The master shows its paired Host Online on Test 53 with repeated authenticated heartbeats. Its original account/password/MFA/recovery/session/legal/secret/settings and revoked history were verified preserved; old private enrollment contents were archived. Account recovery was declined and not performed. No game was installed or data wiped. This owner-target acceptance does not certify all games or remove SE2 private-asset preparation requirements.

Additional verification: 161 public Python cases (158 pass, three root cases separately passed), 67 Node cases, six website gate/command tests and typecheck. Linux regression has 2,413 passes, zero failures and 11 explicit environment gates; real PostgreSQL acceptance has 37 checkpoints. No Ubuntu/WSL, paid service, Actions dispatch or new notification was used. Documentation-only closure does not rewrite signed assets.
