# Public Distribution Context

## Purpose and boundary

`troainc/Bifrost-Server-Manager-Public` is the customer-facing Linux distribution repository. It is distinct from the private application source repository. Keep source code, the Connected installations master panel/service, owner URLs/keys, private Compose overlays, and secret material out of this repository.

The customer web image must be compiled with `VITE_BIFROST_OWNER_PANEL=false`; its release workflow checks the built static assets for owner-registry code. Customer Compose does not configure the master owner service. Customer Controllers retain only outbound license activation/heartbeat configuration.

## Install design

- A single executable `install.sh` is attached to each public deployment-test release. It embeds that fixed release version.
- One-line entry point: `curl --fail --silent --show-error --location https://github.com/troainc/Bifrost-Server-Manager-Public/releases/latest/download/install.sh | sudo bash`.
- The bootstrap reads interactive answers from `/dev/tty`, because standard input supplies the script when it is piped to Bash.
- The bundle contains only the customer Compose file, minimal database bootstrap SQL/shell, and empty reviewed-catalog examples. Image references in the release's `.env.example` are exact GHCR digests.
- Downloaded bundles are checksum-checked and archive paths/types are bounded. The installer preserves existing Docker packages, refuses an existing install directory, never resets volumes, protects generated secrets, binds web to loopback, and selects a non-overlapping private subnet.
- Initial Controller test support is Debian/Ubuntu amd64. Host Agent is separate and is not included until a separate package is published and reviewed.
- A TLS proxy, vendor public license verification key, and organization-reviewed privacy notice inputs are operator prerequisites.

## Current status

Installer and release workflows are prepared in the repository. A matching versioned image tag, public GHCR visibility, published release assets, clean Linux VM install, and Host Agent VM enrollment have not yet been completed. Do not claim production acceptance. See [Linux Controller installation](Docs/Linux-Controller-Install.md) and [VM test plan](Docs/VM-Deployment-Test-Plan.md).
