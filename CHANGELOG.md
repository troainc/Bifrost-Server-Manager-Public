# Changelog

## 2026-10-01 — Rootless non-root installation

- Reworked the Linux bootstrap to refuse root and rootful Docker, use a regular account's rootless Docker Engine, and store the Controller under that account's data directory.
- Removed APT/Docker system installation and all privileged commands from the installer. Host prerequisites must already be available to the operator account.
- Updated the one-line install command, deployment guide, and VM test plan to use the non-root account. Added rootless reboot recovery expectations.
- Linux VM acceptance is still required; the installer has not yet been validated against a real rootless Docker host.

## 2026-10-01 — Correct release bundle asset name

- Matched the installer's downloaded tarball name to the amd64 asset produced by the release workflow.
- Clarified that the `/releases/latest/download/install.sh` URL is unavailable until a deployment-test release is successfully published.
- Added `wget` as an alternative to `curl` for retrieving the installer and release bundle.
- Changed the `wget` instructions to plain file download because the deployment VM's wget rejects output options.

## 2026-10-01 — Linux Controller installer preparation

- Added a release-versioned `install.sh` bootstrap for a one-line Linux install.
- Added a source-free customer Compose bundle with digest-pinned release images, minimal database bootstrap files, protected generated secrets, loopback web binding, private-network collision detection, and no-overwrite safeguards. (The original APT-based bootstrap was replaced by the non-root/rootless installer listed above.)
- Added a private-source customer-image workflow that explicitly compiles the owner panel off and checks customer web assets before image publication.
- Added a public release workflow that requires anonymous GHCR pulls, pins image digests, validates Compose, and publishes the bundle, installer, checksum, and image lock.
- The workflows and files are prepared but no image tag or public deployment release has been published. Linux VM acceptance and a separate Host Agent package remain outstanding.

## 2026-10-01 — Public deployment repository

- Created the public distribution repository and documented the Linux VM deployment-test scope.
- No installable package, public container image, or production release was published in that initial setup.
