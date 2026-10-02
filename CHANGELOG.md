# Changelog

## 2026-10-01 — Linux Controller installer preparation

- Added a release-versioned `install.sh` bootstrap for a one-line Linux install.
- Added a source-free customer Compose bundle with digest-pinned release images, minimal database bootstrap files, protected generated secrets, Docker APT key fingerprint verification, loopback web binding, private-network collision detection, and no-overwrite safeguards.
- Added a private-source customer-image workflow that explicitly compiles the owner panel off and checks customer web assets before image publication.
- Added a public release workflow that requires anonymous GHCR pulls, pins image digests, validates Compose, and publishes the bundle, installer, checksum, and image lock.
- The workflows and files are prepared but no image tag or public deployment release has been published. Linux VM acceptance and a separate Host Agent package remain outstanding.

## 2026-10-01 — Public deployment repository

- Created the public distribution repository and documented the Linux VM deployment-test scope.
- No installable package, public container image, or production release was published in that initial setup.
