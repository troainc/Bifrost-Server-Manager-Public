# Repository guidance

- Keep this public repository limited to customer distribution artifacts. Never add private application source, master owner-panel/service implementation, owner credentials, signing private keys, or private deployment overlays.
- Linux Controller installation and operation must use a regular non-root account and a rootless Docker daemon. Installers must refuse UID 0 and rootful Docker, must not invoke `sudo`, `apt`, privileged `systemctl`, or write outside user-owned paths.
- Preserve existing deployment data. Do not overwrite an installation, delete Docker volumes, or invent an unreviewed upgrade path.
- For repository changes, update `README.md`, `CHANGELOG.md`, `CONTEXT.md`, and `LOGS.md` when their content applies. Validate shell syntax and inspect the final diff before reporting completion.
- Do not claim production readiness or VM acceptance without evidence from a supported Linux VM.
