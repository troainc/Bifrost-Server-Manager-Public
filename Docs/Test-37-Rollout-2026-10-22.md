# Test 37 public testing release - October 22, 2026

The owner authorized the new immutable public package and the website's Debian/Ubuntu installation and panel update commands. [Test 37](https://github.com/troainc/Bifrost-Server-Manager-Public/releases/tag/v0.1.0-installtest.37) is published as a testing prerelease. All 28 application assets were anonymously downloaded over verified HTTPS and matched exact local SHA-256 digests/sizes, including the full 225,456,987-byte customer archive. Previous releases and the separately signed prerequisite baseline remain unchanged. No customer machine, Host Agent or game server was updated by publication.

Frozen application/Host source: `13726049cc3cc63022a45246e36c1f580740f4b5`. Public packaging source: `8c374782f086fdfaeda76cd875a1f8eee22a7bdb`. Installer SHA-256: `83d7eda77a4b1cfa4cefcdf6bdd53dce09d77fa993e43e1ed5cd2022bb08363f`. Linux Host archive SHA-256: `44665936ebe25fad218af9718037b968fc308da8ad2c5dc404eceeb97cbd66b7`. Existing Ed25519 signer identity is retained; both real installer and updater verify all 26 signed payloads and exact source/image identities.

## Changes

The Controller acknowledges authorized live console deliveries with JSON, so already installed Test 36 Agents do not enter retry backoff after successful delivery. New Linux Agent clients accept successful 204 responses as well; Windows source has the same correction but this release does not distribute a new Windows binary. Host installation uses the account's accessible home directory before rootless Podman preflight. Fresh image layers include patched Alpine packages; the current scanner initially identified musl 1.2.6-r2, and a full uncached rebuild with the available update resolved the finding. All three final images pass current HIGH/CRITICAL/UNKNOWN vulnerability and secret gates, with complete SBOMs. No advisory suppression was added.

Existing approved game runtimes/recipes and the first-party Torch Console bridge are retained unchanged. No game content or runtime is installed automatically. Real Torch/Wine plugin loading, commands, mods and player connectivity remain target acceptance work.

## Validation

- Customer Controller/web/PostgreSQL and the versioned standalone Linux Host compile from frozen source. Actual compiled customer image inspection confirms private source/owner/issuer capabilities are excluded; four dependency-security checks pass.
- Public regression suite: 66 Node and 118 Python pass; three root-only Python cases pass separately inside the explicit disposable fixture. No final failures.
- Twelve focused transport, heartbeat, release-control and signature-negative tests pass. The sandbox initially refused localhost TCP; the authorized local-network rerun passes all twelve. The unchanged application implementation retains its earlier 298-pass/13-explicit-skip evidence; this is carried-forward evidence, not a new full-suite run.
- The exact packaged Compose passes verified TLS, initial setup status, anonymous access denial, fresh migrations twice, append-only grants and protected keyring activation/restart.
- Test 36-to-37 migrations run twice on a populated disposable database and retain every synthetic account/password/MFA/recovery field and migration-journal row exactly.
- The exact new Controller passes real HTTP console security/ownership/nonce/revocation tests with the actual shipped Test 36 HTTP client. Both routing matrices pass: 34 master and 25 customer checks using the new customer web image and synthetic upstreams only.
- Website: six gate/command unit tests, typecheck and optimized production build pass. Required shared-cookie settings and dummy build-only Supabase public configuration are used locally; no shared database is written. Sixteen actual generated shell success/checksum/download/operation-failure scenarios pass, plus wrapper/inner syntax and the retained reset syntax. Both OS update selections and copy feedback are browser-verified locally. Clipboard feedback is verified; independent system clipboard readback is not claimed.

## Safe updating and remaining acceptance

The website's installation and update commands are separate, use Debian `su` or Ubuntu `sudo`, and verify the pinned installer checksum before the signed release bootstrap. The update command invokes only `--update`: an existing panel updates in place with an encrypted checkpoint, retaining accounts, MFA, keys, settings and databases. It leaves enrolled Host Agents and games running. Test 36 Hosts already support the corrected Controller console. The old combined panel/manual-Host sequence remains withdrawn; do not use wipe/reinstall for an update. Older incompatible database runtimes refuse safely and need a separately reviewed migration. The command asks separately about testing consent and keeps existing license settings when Enter is pressed.

Manual acceptance remains: a fresh Debian/Ubuntu install, the existing target panel update, retained-account/MFA/Host checks, actual Torch/plugin/mod/player behavior, and independent security/prerequisite/privacy/licensing/key-custody approval. This is not a stable/beta approval or a claim that every target scenario has been tested. No paid services or billing changes.

## Website delivery verified

The [live main-site testing section](https://therealmsofasgard.com/gaming-hub/bifrost-server-manager#testing-installation) visibly shows Test37 and the install/update entry point. Frozen site source `1712f428d5d0f37426f73da7bd6b49169c9b9f51` deployed successfully at `2026-10-22T20:45:10.000000Z`. The unchanged existing password gate returns exact matching Test37 version/installer checksum for both Debian/Ubuntu installation commands and both separate panel-only update commands, with no-store. Browser verification confirms the visible live release/entry point; local production browser checks cover both OS update selections/copy feedback. No real installation/update/reset was executed. Existing website authentication, shared data, artwork, tester password and unrelated routes are retained.
