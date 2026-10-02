# Disposable Linux VM deployment test plan

**Status: installer and release workflow prepared; no versioned release or Linux VM acceptance recorded.**

## Release gate

Before installing, verify that this repository has a matching deployment-test release containing:

- `install.sh`, the source-free Controller tarball, `SHA256SUMS`, and `IMAGE-LOCK.txt`.
- The release version and the two exact GHCR image digests.
- A public anonymous pull for both images.
- A supported target: Debian/Ubuntu amd64 for this first test build.

The private source repository publishes images from a version tag after its image build, owner-panel exclusion check, and high/critical vulnerability scan. GitHub initially creates packages private. An authorized administrator must set both `bifrost-control-plane` and `bifrost-web` packages to public. The public deployment release refuses to proceed while unauthenticated pulls fail.

SHA-256 detects accidental transfer changes but is not a publisher signature. Do not install a moving source branch, private source checkout, local QA build, or unversioned image tag.

## Test topology

1. **Controller VM:** disposable Debian/Ubuntu amd64, outbound HTTPS, and rootless Docker Engine/Compose v2 available to a dedicated non-root account. Use a dedicated VM and test hostname.
2. **Instance Host VM:** separate disposable Linux machine. The Host Agent package is a separate artifact and must be published before this part of the test can run.
3. Configure a separate TLS reverse proxy to reach the Controller's loopback web port. Use test-only credentials and license data.

Record distro/version, architecture, kernel, Docker/Compose versions, VM provider, release tag, image digests, date, operator, and sanitized outcomes.

## One-line install

After a public release is available, run this from a terminal:

```bash
curl --fail --silent --show-error --location https://github.com/troainc/Bifrost-Server-Manager-Public/releases/latest/download/install.sh | bash
```

Run the command from the dedicated non-root account that will own and operate Bifrost; never use `sudo`. Use a fixed tagged release URL instead of `latest` for controlled testing. Rootless Docker and required utilities must be available to that account before install. Keep the vendor-issued license verification **public** key available on the VM. The installer asks for its path, external HTTPS URL, license-service URL, and operator-reviewed privacy values.

## Controller test cases

- Confirm the fixed version and bundle checksum before install.
- Install on a clean VM as a non-root account; verify root execution is refused, rootful Docker is refused, created files belong to the operator, secret modes are 0600, and the listener is bound only to loopback.
- Confirm PostgreSQL has no host-published port and web/API/database use the expected network boundaries.
- Configure TLS reverse proxy, complete first-admin setup, enroll MFA, and confirm the privacy notice reflects the operator's input.
- Confirm the customer UI contains no Connected installations owner section and customer Compose contains no owner service URL/key.
- Test license activation only with the supplied public verification key and configured HTTPS licensing service.
- Confirm rootless Docker is enabled for the operator account; reboot and verify containers start and database state remains intact without logging in as root.
- Review bounded logs and verify no secrets appear.
- In a disposable copy only, simulate a startup failure and document recovery without deleting volumes.
- Record each case pass/fail and sanitized evidence. Remove only the disposable VM after review.

## Host test cases

When a separate public Host Agent package becomes available:

- Verify its checksum and exact version.
- Enroll with a fresh one-time code over HTTPS.
- Confirm the operator-owned service identity, no Docker-socket access, and user-level service.
- Reboot and check reconnect/heartbeat and revocation handling.
- Treat host connectivity separately from game provider/runtime lifecycle acceptance.

## Recovery and limits

The first Controller installer deliberately refuses an existing installation. It does not implement an upgrade/rollback workflow; preserve the complete `${XDG_DATA_HOME:-$HOME/.local/share}/bifrost` configuration, secrets, and rootless Docker volumes owned by the operator account. Do not use production data during deployment testing.

Capture sanitized commands and results only. Never attach secrets, one-time codes, private keys, raw environment files, or unsanitized logs. A passing VM rehearsal is not independent security review, publisher signature, production readiness, or game-host lifecycle acceptance.
