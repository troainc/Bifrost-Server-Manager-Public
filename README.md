# Bifrost Server Manager

## Linux install

Run this as your current VM user. The installer requests the administrator password once, creates the unprivileged bifrost account, and continues automatically:

```bash
wget --output-document=install.sh https://github.com/troainc/Bifrost-Server-Manager-Public/releases/latest/download/install.sh && bash install.sh
```

The wizard asks for the VM IP/hostname and HTTPS port, downloads the application, checks its checksum, generates configuration and credentials, and starts the panel. Default port: **8443**. Create your administrator in the browser.

Use Debian/Ubuntu x86_64 with wget or curl. The installer sets up Docker, Compose and missing Python/OpenSSL/iptables tools in your user account. The VM image must provide uidmap helpers, subordinate UID/GID ranges, enabled user namespaces and an active user systemd session. Bifrost refuses root and never invokes sudo.

The application is delivered as compiled container images inside a GitHub Release asset. No private registry login, private application source, or master licensing service is distributed. The repository-root `install.sh` is the bootstrap; GitHub's `releases/latest/download/install.sh` is a release asset, not a folder in the repository.

This is a VM installation test release. HTTPS uses a generated self-signed certificate. Licensing activation still requires your license service and public verification key, configured separately. Privacy review fields are left unset until configured; installation does not invent a legal review.

Files live in `~/.local/share/bifrost`. Existing installations are preserved.

```bash
cd ~/.local/share/bifrost
# Status
docker compose ps
# Logs
docker compose logs --tail 100
# Stop / start
docker compose stop
docker compose up -d
```

The installer follows the single-command shell wizard pattern described by [CubeCoders AMP](https://cubecoders.com/AMP/Install); it contains original Bifrost code.

## 2026-10-02 — Automatic non-root prerequisites
install.sh now downloads rootless Docker 29.8.2 and Compose v2.39.4 automatically, starts the user service, and downloads/extracts missing Python, OpenSSL and iptables packages under the user's home using Debian/Ubuntu package sources without APT installation or sudo. It saves the Docker environment for subsequent logins and includes the TROA welcome/support/project message. System UID mapping helpers, assigned subordinate ID ranges, enabled user namespaces, package indexes and an active user systemd login must exist in the VM image; missing requirements are listed precisely. Unattended operation requires user lingering provisioned in that image. This is not a claim of zero host prerequisites or completed clean-VM acceptance.



## 2026-10-02 — Dedicated service account
The explicit --prepare-account mode performs only administrator-owned account preparation: creates bifrost with its own group and initially locked password, checks UID and privileged memberships and sudo policy, protects its home and enables user lingering. It refuses an existing privileged account without altering its groups or grants. Set a login password with passwd bifrost and log in directly as bifrost. Normal installation now requires bifrost and rejects sudo/wheel/docker/lxd/incus-admin membership and discoverable sudo grants. Application installation and services remain non-root; administrator preparation does not install or run the application. Bash syntax checked; real VM account acceptance pending.


## 2026-10-02 — Automated VM bootstrap (supersedes manual preparation)
Run the normal one-line installer as the current VM user. It requests administrator authentication using sudo, or su when sudo is unavailable/denied, prepares Debian/Ubuntu system prerequisites and nf_tables, creates/checks the non-privileged bifrost account, enables lingering and starts its user manager, then drops privileges with runuser and continues automatically. New service accounts have locked passwords; no passwd command or manual SSH switch is needed. The legacy --prepare-account option now invokes the same complete bootstrap. Existing installations and privileged account memberships remain fail-closed. Only host preparation is elevated; application setup/runtime remain non-root. Bash syntax passed; clean VM end-to-end acceptance pending.



2026-10-02: Set the administrator bootstrap PATH explicitly to include /usr/sbin and /sbin. Fixes modprobe command not found after successful package preparation when elevation inherits a normal user PATH. Shell syntax passed; VM retry pending.
