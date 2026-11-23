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

Fresh Linux regression: 2,412 passes, zero failures, 11 explicit environment
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
