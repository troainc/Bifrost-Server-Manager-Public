# Context

The owner requested a reset of the public installer repository using AMP's one-command installer as a workflow reference. Installers are original Bifrost code. Private source is kept separately. Distribution uses compiled customer images in GitHub Release assets. The installer installs into the current user's home, requires rootless Docker, and never installs system packages or runs as root. This is a VM installation test, not production acceptance.

Current public release: v0.1.0-installtest.1. Application and installer downloads are available at GitHub Releases; verified on 2026-10-02.

## 2026-10-02 — Automatic non-root prerequisites
install.sh now downloads rootless Docker 29.8.2 and Compose v2.39.4 automatically, starts the user service, and downloads/extracts missing Python, OpenSSL and iptables packages under the user's home using Debian/Ubuntu package sources without APT installation or sudo. It saves the Docker environment for subsequent logins and includes the TROA welcome/support/project message. System UID mapping helpers, assigned subordinate ID ranges, enabled user namespaces, package indexes and an active user systemd login must exist in the VM image; missing requirements are listed precisely. Unattended operation requires user lingering provisioned in that image. This is not a claim of zero host prerequisites or completed clean-VM acceptance.

