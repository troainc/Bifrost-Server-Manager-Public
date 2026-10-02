# Bifrost Server Manager Public

Public distribution and deployment-testing home for Bifrost Server Manager.

This repository is intentionally separate from the application source repository. It is for customer-facing install instructions and versioned deployment artifacts. It must not contain the master licensing console, owner-service configuration, owner keys, source checkout, credentials, or private deployment overlays.

## Deployment status

The repository has been created, but it does not yet contain a downloadable Controller release or public container images. Do not use it to install a VM until a versioned deployment-test release is published here.

The first deployment-test package will provide:

- A version-pinned Linux Controller deployment bundle and installer.
- Public customer container images built from the standard Controller configuration.
- SHA-256 checksums for transfer-integrity checks.
- Debian/Ubuntu VM test steps for clean install, first admin setup, restart, logs, and recovery.

Checksum files are not publisher signatures. A deployment-test release is not production approval.

## Planned VM test targets

Use disposable Debian or Ubuntu VMs on amd64 or arm64. Test the Controller on one VM and enroll a separate Instance Host VM. Do not use a production fleet or real game data for the first run.

The current source installer is not yet distributed from this repository. Do not copy the private/master Compose overlays or owner-service keys into this repo.

## Security boundary

The public/customer deployment must keep the master Connected installations console and owner-service credentials out of its UI, API configuration, Compose files, and release bundle. Customer Controllers use only the public licensing verification key and the outbound license activation/heartbeat client.

## Test tracking

See [VM deployment test plan](Docs/VM-Deployment-Test-Plan.md). Release assets will be listed in GitHub Releases after their build and review gates are in place.
