# Bifrost Server Manager Public

Public Linux deployment files and deployment-test artifacts for Bifrost Server Manager.

This repository is separate from the private application source. It contains only the customer Controller Compose bundle, bootstrap installer, deployment documentation, and release workflows. It does not contain application source, the master Connected installations UI/service, owner configuration, credentials, or private signing keys.

## One-line Linux install

After a deployment-test release is published, install the latest published release on a **disposable Debian/Ubuntu amd64 VM** with:

```bash
curl --fail --silent --show-error --location https://github.com/troainc/Bifrost-Server-Manager-Public/releases/latest/download/install.sh | bash
```

Run the command as the regular Linux account that will own and operate Bifrost. Never prefix it with `sudo` and do not run it from a root shell. The installer refuses UID 0 and refuses a rootful Docker daemon. It requires rootless Docker Engine and Compose v2, plus `curl`, `python3`, `openssl`, `awk`, `grep`, and `sha256sum` already available to that account; it does not use `apt`, install host packages, or modify system files.

The installer stores the deployment under `${XDG_DATA_HOME:-$HOME/.local/share}/bifrost` (or `BIFROST_INSTALL_DIR`), owned by your account with private configuration and secrets. It asks for the vendor-issued license verification **public** PEM path, HTTPS panel and licensing URLs, and organization-reviewed privacy notice values. Then it downloads the fixed-version bundle, checks its SHA-256, chooses a non-overlapping Docker network, generates secrets, validates Compose, and asks before starting containers as your user. Have a system administrator provision rootless Docker and required host packages before installation; no root access is needed to install or operate Bifrost itself.

For change-controlled deployment, replace `latest` with an exact release tag in the URL. The installer refuses an existing install directory and does not delete volumes or existing container packages.

**There is not a published deployment-test release yet.** The one-line command will become usable after the private source image workflow publishes both versioned customer images, an administrator makes both GHCR packages public, and this repository's matching release workflow verifies anonymous image pulls and publishes the bundle. The workflow pins image digests in the released Compose bundle. Do not run an unpublished version or substitute `main` / `latest` images.

## Deployment-test scope

- Controller VM: Debian or Ubuntu, amd64, outbound HTTPS, and rootless Docker Engine with Compose v2 available to the non-root operator account.
- Instance Host VM: separate machine and a separate Host Agent package. That package is not part of this initial Controller bundle.
- TLS reverse proxy: separately configured, with the Bifrost web listener bound to loopback at `127.0.0.1:8080`.
- License activation: vendor service URL plus its matching public verification key. No signer private key belongs on the VM.
- Privacy notice: supply the organization's actual contact, processing jurisdictions, lawful bases, processors, data region, and completed review record. The installer does not provide legal review or make a compliance claim.

See [Linux Controller installation](Docs/Linux-Controller-Install.md) and the [disposable VM test plan](Docs/VM-Deployment-Test-Plan.md).

SHA-256 checks detect transfer corruption but are not publisher signatures. These deployment-test artifacts do not establish production readiness, security certification, independent review, or supported game lifecycle operation.
