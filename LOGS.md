# Work log

## 2026-10-01 — Release asset URL diagnosis

- Confirmed GitHub has no published release, so `/releases/latest/download/install.sh` currently returns 404; the script is only present on the repository branch until a release workflow publishes it as an asset.
- Fixed the bootstrap bundle filename to match the amd64 tarball emitted by the release workflow.
- Added a `wget` path because the reported Debian VM does not have `curl` installed; either downloader must be present in the base image.
- Removed `wget -O` options after the VM's wget rejected them; use plain `wget URL` followed by `bash install.sh` for the bootstrap.
- A tagged private image build and successful public bundle release are still required before the one-line install URL becomes available.

## 2026-10-01 — Require non-root and rootless Docker

- Changed `install.sh` to refuse UID 0, require Docker Compose v2 connected to a rootless daemon, and use a user-owned install directory under XDG data home by default.
- Removed host package installation, APT repository changes, privileged Docker service operations, `/opt/bifrost`, and sudo-based follow-up commands.
- Updated README, CONTEXT, installation guide, and disposable VM plan. Added repository-specific AGENTS.md instructions requiring non-root deployment.
- Static shell syntax and an actual rootless Debian/Ubuntu VM run remain to be verified before claiming deployment acceptance.

## 2026-10-01 — Linux one-line installer preparation

- Added an executable release bootstrap, `install.sh`, configured by the public release workflow to embed a fixed release tag. Interactive prompts read from `/dev/tty` so the requested curl-to-Bash one-line entry point remains interactive.
- Added a customer-only Compose bundle. Release packaging resolves GHCR tags to immutable digests and writes those references to the bundle's environment example.
- The initial APT-based installer was superseded on 2026-10-01 by the rootless non-root flow documented above; no package installation or system-level Docker configuration remains in the installer.
- Installer validates the bundle checksum and archive member type/path, refuses to overwrite an existing install directory, generates mode-0600 secrets, asks for operator-reviewed privacy inputs, and prompts before starting containers.
- Added a source-repo image workflow that sets `VITE_BIFROST_OWNER_PANEL=false`, checks the resulting customer JS assets for owner registry markers, scans high/critical vulnerabilities, and publishes versioned GHCR images.
- Added a public release workflow that tests anonymous GHCR pulls before producing release assets. GitHub's first-published container packages must be changed to public by an authorized package administrator before this gate can pass.
- Verified `install.sh` and database bootstrap shell syntax with Git Bash.
- Local Docker image build could not run because the sandbox denied access to the Docker client configuration. A local web build also could not run because the available pnpm setup could not resolve the web workspace TypeScript compiler. The GitHub release workflows contain their independent build/scanner/Compose checks.
- No tag, GHCR image, release asset, actual Debian/Ubuntu VM install, TLS proxy, first-admin setup, restart recovery, Host Agent enrollment, or production acceptance has been recorded.
