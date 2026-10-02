# Disposable Linux VM deployment test plan

**Status: preparation only. No downloadable public deployment bundle or container images are available yet.**

## Test topology

Use two disposable VMs for the first end-to-end pass:

1. **Controller VM:** Debian or Ubuntu, amd64/arm64, systemd, outbound HTTPS, Docker Engine and Compose v2.
2. **Instance Host VM:** Debian or Ubuntu, amd64/arm64, systemd, outbound HTTPS, rootless Podman and Node.js 24 installed by the separate Host Agent package.

Keep these machines isolated from production accounts, game data, and production secrets. Record distro/version, architecture, kernel, Docker/Compose versions, and package source.

## Before a test release is available

Do not copy the private application source checkout or master Compose overlays to the VM. Wait for a tagged release in this repository that lists:

- Controller bundle version and immutable image tags.
- SHA-256 files for the bundle and each image digest.
- Supported OS/architecture.
- License public-key provisioning instructions.
- TLS reverse-proxy requirements.
- Upgrade and rollback notes.

SHA-256 detects transfer corruption but does not authenticate the publisher. Production use additionally requires signed provenance, independent review, recovery evidence, and owner acceptance.

## Controller test cases

For a published deployment-test version:

- Verify the release version and checksums before installation.
- Install on a clean disposable VM and confirm generated secret files are mode 0600 and the data volume persists.
- Confirm the web listener is bound to loopback and PostgreSQL is not exposed publicly.
- Configure a TLS reverse proxy and complete first-administrator setup.
- Confirm the standard build has no Connected installations owner section or owner-service configuration.
- Confirm the required license disclosure appears and activation works only with the owner-provided public verification key and configured HTTPS license URL.
- Restart the VM and verify the service and database recover with state intact.
- Review bounded service logs and confirm secrets are not printed.
- Simulate a failed startup using a disposable copy, verify recovery instructions, then restore the successful test state.
- Remove only the disposable VM and its test data after recording evidence.

## Host test cases

After Controller acceptance, use the separate Host Agent package:

- Verify package integrity before installing.
- Enroll through a fresh one-time code over HTTPS.
- Confirm the bifrost-host account is locked, has no Docker socket access, and runs the user-level service.
- Reboot and verify reconnect/heartbeat without inbound management ports.
- Verify revocation prevents further authenticated work.
- Do not treat provider cards as game lifecycle acceptance. A supported game profile requires its own signed-profile, lifecycle, update, backup/restore, and failure-recovery evidence.

## Evidence record

For each run, capture test date, operator, VM provider, distro/version, architecture, exact release tag and image digests, sanitized commands and results, failures, recovery steps, and a final pass/fail per case. Never attach secrets, one-time codes, private keys, raw environment files, or unsanitized logs.

This test plan does not establish production readiness or a security certification.
