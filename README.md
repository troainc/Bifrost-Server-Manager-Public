# Bifrost Server Manager Public

Public Linux deployment files and deployment-test artifacts for Bifrost Server Manager.

This repository is separate from the private application source. It contains only the customer Controller Compose bundle, bootstrap installer, deployment documentation, and release workflows. It does not contain application source, the master Connected installations UI/service, owner configuration, credentials, or private signing keys.

## One-line Linux install

After a deployment-test release is published, install the latest published release on a **disposable Debian/Ubuntu amd64 VM** with:

```bash
curl --fail --silent --show-error --location https://github.com/troainc/Bifrost-Server-Manager-Public/releases/latest/download/install.sh | sudo bash
```

The script reads prompts from the terminal, asks for the vendor-issued license verification **public** PEM path, the HTTPS panel and licensing URLs, and organization-reviewed privacy notice values. It installs Docker Engine and Compose v2 from Docker's signed APT repository if they are missing, verifies Docker's signing-key fingerprint, downloads the fixed-version bundle, checks its SHA-256, chooses a non-overlapping Docker network, protects generated secrets, and asks before starting the containers.

For change-controlled deployment, replace `latest` with an exact release tag in the URL. The installer refuses an existing install directory and does not delete volumes or existing container packages.

**There is not a published deployment-test release yet.** The one-line command will become usable after the private source image workflow publishes both versioned customer images, an administrator makes both GHCR packages public, and this repository's matching release workflow verifies anonymous image pulls and publishes the bundle. The workflow pins image digests in the released Compose bundle. Do not run an unpublished version or substitute `main` / `latest` images.

## Deployment-test scope

- Controller VM: Debian or Ubuntu, amd64, systemd, outbound HTTPS, Docker Engine and Compose v2.
- Instance Host VM: separate machine and a separate Host Agent package. That package is not part of this initial Controller bundle.
- TLS reverse proxy: separately configured, with the Bifrost web listener bound to loopback at `127.0.0.1:8080`.
- License activation: vendor service URL plus its matching public verification key. No signer private key belongs on the VM.
- Privacy notice: supply the organization's actual contact, processing jurisdictions, lawful bases, processors, data region, and completed review record. The installer does not provide legal review or make a compliance claim.

See [Linux Controller installation](Docs/Linux-Controller-Install.md) and the [disposable VM test plan](Docs/VM-Deployment-Test-Plan.md).

SHA-256 checks detect transfer corruption but are not publisher signatures. These deployment-test artifacts do not establish production readiness, security certification, independent review, or supported game lifecycle operation.
