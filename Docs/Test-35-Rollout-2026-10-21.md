# Test 35 UI rollout - 2026-10-21

Owner-authorized installation-testing delivery of the shared UI audit fixes. Keep existing master users, MFA, sessions, permissions, licensing, keys, branding, configuration, database volumes and earlier releases. No schema changes, global Docker upgrade or account resets are included. Test 34 and v0.0.0-prerequisites.1 remain immutable.

Preparation: verify the frozen source, both UI editions and public installer; build and scan actual artifacts; perform isolated packaged checks; retain an on-host checkpoint and rollback images before master deployment. Publish a new signed Test 35 prerelease and update the website installer version/hash together after anonymous verification. Record exact commit, package, deployment and preservation results below only when verified. Human testing, independent release gates and stable/beta approval remain outstanding.

The source-level UI assessment is 7.5/10 for master and 8/10 for customer. Builds and synthetic browser checks are not manual production acceptance. See the private UI-Audit-2026-10-21.md and existing manual acceptance checklist for remaining checks.

## Verified results

- Frozen private implementation: `3fe6278f16f1d724b6d8c16d0915973d5f574f35`; public packaging: `4c1486e087857849a95299d10e0a187fb6523a49`. Both primary branches were updated. Later documentation commits do not change these artifact identities.
- [Test 35](https://github.com/troainc/Bifrost-Server-Manager-Public/releases/tag/v0.1.0-installtest.35) was published as a prerelease on 2026-10-21 at 23:28:45 UTC. Existing releases and the separate prerequisite baseline are unchanged. All 25 application and eight prerequisite files were downloaded anonymously and matched their hashes.
- The Ed25519-signed application manifest covers 23 payloads. Both installer and updater verified its actual signature and all payload hashes. Installer SHA-256: `31c4e58c235f5d6103e48f07a86a12aafe299c16679c8d9f8aa777919815a6c1`.
- Customer Controller, web and PostgreSQL images were rebuilt and scanned; the owner web candidate was separately built/scanned. No HIGH/CRITICAL/UNKNOWN vulnerability or secret findings were reported by the pinned scanner. Customer images omit owner registry capabilities. Existing compiled Linux Host bytes are retained from their recorded source `5314704a8ee3ee059598666bcc38a80d23d9a84a`; backend/schema/Host/lockfile source did not change in this UI delivery.
- Typecheck and workspace build passed. Rebuilt private Node tests: 262 passed, nine explicit platform/runtime skips, zero failures. Public checks: 43 Node tests passed; Python checks executed 101 of 104 tests with three root-only skips locally. Exact-source public hosted installer/root fixtures and classic/containerd image-identity workflows passed (39693978148 and 39693977960).
- Isolated acceptance used the actual packaged customer images with HTTPS, first administrator setup, anonymous access denial, all 79 fresh-install migrations applied twice, append-only runtime grants and persisted keyring restart. Synthetic data and retained fixture volumes are separate from production.
- Exact-source private hosted jobs executed zero steps because GitHub account payments/spending limits blocked runners. Local checks and deployed-image scans are separate evidence; hosted private CI is not claimed to have passed. No billing settings were changed.

## Manual acceptance and approval

Test 35 is installation testing, not general beta/stable approval. On the deployed master, hard refresh and check wheel/keyboard sidebar access, Profile & security/MFA, mobile Gate navigation, dialogs, tables, file/history controls and the owner registry. On a separate supported server, use the website's matching Debian/Ubuntu command and check installation, first administrator/MFA/legal/license setup, Host heartbeat, game creation/start/stop, player connection and backup/recovery with representative data. Native Windows service, assistive technology/touch hardware, target OS resource limits and independent security/source-license/privacy/key-custody approval remain human gates. Existing manual checklists remain applicable.

## Separate owner master

The owner master was deployed and its account/security records, mounted data, secrets, managed keys and branding verified against its retained on-host checkpoint. Private production receipts remain private. This customer package contains compiled customer artifacts, not private issuer source or credentials.
