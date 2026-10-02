# Linux Controller deployment test

This guide covers the central Controller on a **disposable Debian/Ubuntu amd64 VM**. The Controller is not a game host. Install a Host Agent on a separate Linux game VM only after the separate Host Agent package is published and verified.

## Release availability

The public repository's `v*` release workflow downloads the same versioned customer images from GHCR, verifies anonymous pulls, resolves both image digests, pins those digests into the bundle, validates the Compose configuration, and publishes a tarball plus an executable `install.sh`, SHA-256 checksum, and image lock file. It fails closed if either image cannot be pulled without authentication.

The private source repository's `v*` workflow builds the Controller and web images from the exact tag, explicitly builds the web image with `VITE_BIFROST_OWNER_PANEL=false`, checks that owner-registry strings are absent from the built web assets, scans for high and critical image vulnerabilities, and publishes versioned images to GHCR. GitHub creates GHCR packages private by default. A repository/org administrator must make both packages public before the public deployment release workflow can pass. Verify anonymous pulls before installing.

Until a matching release exists here and both images are publicly pullable, there is no installable release. Do not substitute `main`, `latest`, a private source checkout, or the QA Compose setup.

## Requirements

- Disposable Debian or Ubuntu VM, amd64, current security updates, outbound HTTPS, DNS name, and at least 4 GB RAM / 20 GB free disk for test use.
- A regular non-root operator account with rootless Docker Engine and Compose v2 already available in that account's Docker context. Bifrost refuses UID 0 and refuses a rootful Docker daemon.
- A separately managed TLS reverse proxy. The Controller's web service binds to `127.0.0.1:8080`; PostgreSQL and the API are not published on host ports.
- The vendor-issued PEM **public** license verification key. Never copy a license signing private key to the VM.
- Organization-approved privacy notice inputs: controller name, contact, jurisdictions, lawful bases, configured processors, data region, review date, and internal review reference. These are deployment data; the installer does not invent or certify them.
- A matching public release tag, its SHA-256 checksum, and publicly pullable GHCR images.

## Install

The one-line install command is:

```bash
curl --fail --silent --show-error --location https://github.com/troainc/Bifrost-Server-Manager-Public/releases/latest/download/install.sh | bash
```

This command will work after the first public deployment-test release is published. The release's script embeds its fixed version, reads interactive answers from the terminal, and downloads the matching digest-pinned bundle. It asks where the vendor-provided public license key PEM is stored. For a controlled rollout, replace `latest` with the exact release tag in the download URL.

The installer supports Debian/Ubuntu amd64 only for this first deployment-test package. Run it as the regular account that will own and operate Bifrost; do not use `sudo` or a root shell. It does not install host packages, configure system Docker, modify system directories, or use a rootful Docker daemon. Required tools and rootless Docker/Compose must already be available to the operator account. Installation defaults to `${XDG_DATA_HOME:-$HOME/.local/share}/bifrost`, or uses `BIFROST_INSTALL_DIR` if set. Files and secrets are created under the current user with private permissions. The installer refuses an existing install path and does not reset volumes.

It downloads the fixed-version release bundle and verifies its SHA-256 checksum before extracting regular files. The bundle's `.env.example` contains the two images pinned by digest. The installer asks for the external HTTPS URL, license service URL, and reviewed privacy values, generates fresh protected secrets, chooses a non-overlapping Docker subnet, validates Compose, and asks before starting containers.

SHA-256 detects accidental transfer changes; it is not a publisher signature. Use GitHub's HTTPS and the tagged, reviewed script. Production deployment additionally needs signed provenance and independent security and recovery review.

## After installation

1. Point the TLS reverse proxy to `http://127.0.0.1:8080`; preserve the original client address and add its trusted-proxy address to `BIFROST_TRUSTED_PROXIES` in `${XDG_DATA_HOME:-$HOME/.local/share}/bifrost/.env` before starting if it is not the local host.
2. Confirm `docker compose ps --all`, `docker compose logs --tail=200`, and `curl --fail http://127.0.0.1:8080/api/health/ready` from the VM.
3. Open the HTTPS URL, create the first administrator, enroll MFA, review the required licensing disclosure, and verify the privacy notice reflects the values entered during setup.
4. Confirm the standard customer UI has no Connected installations owner section. Customer Controllers use only the configured outbound license activation/heartbeat client; the master owner service URL/key are absent from this Compose configuration.
5. Reboot the VM, confirm containers recover and state persists, and record sanitized evidence using [the VM test plan](VM-Deployment-Test-Plan.md).

Run all `docker compose` commands as the same non-root account from the install directory. Keep `${XDG_DATA_HOME:-$HOME/.local/share}/bifrost/.env`, `${XDG_DATA_HOME:-$HOME/.local/share}/bifrost/secrets`, and Docker volumes protected and backed up. Rootless Docker stores its containers and volumes in that user's Docker data directory. Preserve all of them for restart and recovery. Docker restart policies recover containers when the rootless daemon is running; reboot recovery depends on the rootless Docker user service being enabled for the account. The installer does not configure system-wide lingering or require root. The installer does not implement upgrades or rollback yet; do not rerun it over an existing install.

## Not included in this package

- Host Agent enrollment package or game-server lifecycle acceptance.
- Email delivery, master owner-console/service, or source code.
- A TLS proxy, a publisher-signing key, or legal/privacy review for the operator's organization.
- An upgrade/rollback installer or production readiness approval.
