# Work log

## 2026-10-02
Replaced the release-dependent placeholder bootstrap with a short Linux wizard. Packaging and download verification are in progress; record final results after release publication.

Packaged runtime proof: isolated PostgreSQL, migrations, Controller, web and HTTPS services passed Compose health checks. HTTPS readiness returned connected and setup status requires an administrator. Rootless Linux VM acceptance is still pending.

Published v0.1.0-installtest.1 with application archive, install.sh, SHA256SUMS and image identity lock. Both latest-release download endpoints returned HTTP 200. Downloaded installer SHA-256 matches local source; Bash syntax and help entry point passed. Public history preserved while old release workflow and outdated docs were removed.
