# Work log

## 2026-10-01 — Linux one-line installer preparation

- Added an executable release bootstrap, `install.sh`, configured by the public release workflow to embed a fixed release tag. Interactive prompts read from `/dev/tty` so the requested curl-to-Bash one-line entry point remains interactive.
- Added a customer-only Compose bundle. Release packaging resolves GHCR tags to immutable digests and writes those references to the bundle's environment example.
- Added Docker APT installation with upstream signing-key fingerprint verification, package-conflict preservation, private Docker subnet collision checking, loopback web port, and private database/API networks.
- Installer validates the bundle checksum and archive member type/path, refuses to overwrite an existing install directory, generates mode-0600 secrets, asks for operator-reviewed privacy inputs, and prompts before starting containers.
- Added a source-repo image workflow that sets `VITE_BIFROST_OWNER_PANEL=false`, checks the resulting customer JS assets for owner registry markers, scans high/critical vulnerabilities, and publishes versioned GHCR images.
- Added a public release workflow that tests anonymous GHCR pulls before producing release assets. GitHub's first-published container packages must be changed to public by an authorized package administrator before this gate can pass.
- Verified `install.sh` and database bootstrap shell syntax with Git Bash.
- Local Docker image build could not run because the sandbox denied access to the Docker client configuration. A local web build also could not run because the available pnpm setup could not resolve the web workspace TypeScript compiler. The GitHub release workflows contain their independent build/scanner/Compose checks.
- No tag, GHCR image, release asset, actual Debian/Ubuntu VM install, TLS proxy, first-admin setup, restart recovery, Host Agent enrollment, or production acceptance has been recorded.
