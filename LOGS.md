# Work log

## 2026-10-02
Replaced the release-dependent placeholder bootstrap with a short Linux wizard. Packaging and download verification are in progress; record final results after release publication.

Packaged runtime proof: isolated PostgreSQL, migrations, Controller, web and HTTPS services passed Compose health checks. HTTPS readiness returned connected and setup status requires an administrator. Rootless Linux VM acceptance is still pending.

Published v0.1.0-installtest.1 with application archive, install.sh, SHA256SUMS and image identity lock. Both latest-release download endpoints returned HTTP 200. Downloaded installer SHA-256 matches local source; Bash syntax and help entry point passed. Public history preserved while old release workflow and outdated docs were removed.

## 2026-10-02 — Automatic non-root prerequisites
install.sh now downloads rootless Docker 29.8.2 and Compose v2.39.4 automatically, starts the user service, and downloads/extracts missing Python, OpenSSL and iptables packages under the user's home using Debian/Ubuntu package sources without APT installation or sudo. It saves the Docker environment for subsequent logins and includes the TROA welcome/support/project message. System UID mapping helpers, assigned subordinate ID ranges, enabled user namespaces, package indexes and an active user systemd login must exist in the VM image; missing requirements are listed precisely. Unattended operation requires user lingering provisioned in that image. This is not a claim of zero host prerequisites or completed clean-VM acceptance.

