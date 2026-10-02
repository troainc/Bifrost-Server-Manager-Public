# Bifrost Server Manager Public — Context

This repository is the public distribution boundary, separate from the application source repository.

## Current state

- Public GitHub repository: troainc/Bifrost-Server-Manager-Public.
- Initial README and VM deployment test plan are published.
- No installable Controller deployment bundle or public container images are published yet.
- No VM install, Linux acceptance, signing, or production readiness is claimed.

## Intended package

The first test release should contain a pinned, customer-only Linux Controller installer and Compose configuration that pulls public versioned images. It must not include application source or any master-only service, owner-console code, overlay, or secret. The Host Agent package will be a separate artifact and must remain distinct from the Controller installer.

## Supported test scope

Debian/Ubuntu, amd64/arm64, Docker Compose v2, and disposable test VMs. A real TLS reverse proxy and the vendor-provided public license verification key are required for end-to-end testing. Keep admin setup and license/privacy consent explicit.

## Product boundary

Customer Controllers send required activation/validation heartbeats outbound to the Bifrost licensing service. The product-owner Connected installations console stays in the owner's private deployment. No owner key, signer private key, or customer license secret belongs in this repository.

See Docs/VM-Deployment-Test-Plan.md.
