# Changelog

## 2026-10-02
- Rebuilt Linux QuickStart as a single bootstrap script and short interactive wizard.
- Bundled application images in release assets instead of depending on private GHCR visibility.
- Added generated HTTPS for VM setup and image checksum/identity verification.
- Preserved non-root installation and existing data.

## 2026-10-02 — Automatic non-root prerequisites
install.sh now downloads rootless Docker 29.8.2 and Compose v2.39.4 automatically, starts the user service, and downloads/extracts missing Python, OpenSSL and iptables packages under the user's home using Debian/Ubuntu package sources without APT installation or sudo. It saves the Docker environment for subsequent logins and includes the TROA welcome/support/project message. System UID mapping helpers, assigned subordinate ID ranges, enabled user namespaces, package indexes and an active user systemd login must exist in the VM image; missing requirements are listed precisely. Unattended operation requires user lingering provisioned in that image. This is not a claim of zero host prerequisites or completed clean-VM acceptance.

