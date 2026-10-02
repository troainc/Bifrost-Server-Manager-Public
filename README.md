# Bifrost Server Manager

## Linux install

Run this as your regular Linux user:

```bash
wget --output-document=install.sh https://github.com/troainc/Bifrost-Server-Manager-Public/releases/latest/download/install.sh && bash install.sh
```

The wizard asks for the VM IP/hostname and HTTPS port, downloads the application, checks its checksum, generates configuration and credentials, and starts the panel. Default port: **8443**. Create your administrator in the browser.

Use a Debian/Ubuntu x86_64 VM with **rootless Docker Engine and Compose v2**, Python 3.12+, OpenSSL, and wget or curl available. Bifrost refuses root and never invokes sudo. Rootless Docker must already be provisioned for your account.

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
