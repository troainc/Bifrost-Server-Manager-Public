# Bifrost Server Manager — operator guide

## What Bifrost does

Bifrost separates the web Controller from the machines that run Space Engineers. The Controller hosts the panel, account and host administration, licensing configuration, and deployment coordination. A Host Agent runs on each enrolled game machine and gives the Controller a managed connection to that machine. A Blueprint describes an installable server layout; host enrollment by itself does not install a game.

This repository currently publishes a customer testing release. Treat operating-system support and deployment behavior as release-specific, and use the current root [README](../README.md) and [release page](https://github.com/troainc/Bifrost-Server-Manager-Public/releases) as the authority.

## Choose a role and prerequisites

- **Controller:** currently the automatic bootstrap targets Debian or Ubuntu on x86_64. It prepares the unprivileged `bifrost` service account and runs the application with rootless containers. Default panel port is 8443. HTTPS uses a generated self-signed certificate in the testing setup.
- **Linux Instance Host:** requires Node.js 24 at `/usr/bin/node`, rootless Podman, and a systemd user manager for the regular game-operator account. The Controller installs the separate Host Agent package and enrolls it with a one-use code.
- Other distributions and host configurations are compatibility candidates until tested against the exact published prerequisites. Do not infer support merely because the app itself runs in containers.

## First Controller install

Run the repository bootstrap as the VM operator and choose **Bifrost Controller** when prompted. The installer asks for the panel address and HTTPS port, checks downloads, generates configuration and credentials, and starts the panel. Create the first administrator in the browser. Use the public README's current bootstrap command because a release asset can contain an older installer than the repository branch.

Before an update, read the release notes and preserve the application data directory. The documented update path backs up configuration and retains the database, credentials, public verification key, and license settings. Use the supported update option; do not remove the install directory or use reinstall as a recovery shortcut. If an update reports an identity mismatch, stop and follow the exact README recovery steps for that version.

## Enroll an instance host

In the Controller, create a one-use host enrollment code. On the game machine, select **Linux Instance Host**, provide the Controller's HTTPS panel URL and the code, and follow the agent installer. The licensing service endpoint is not the Controller URL. Enrollment grants a host connection; review and apply a Blueprint separately to install a game service.

## Routine operations

From `~/.local/share/bifrost`, use the documented Compose commands to inspect service state, read recent logs, stop services, or start them again. In the panel, use the current Controller and host screens to manage administrators, hosts, and deployments. Keep host credentials private, restrict panel access, and record which Blueprint and release were used for each server.

## Acceptance and support boundaries

The repository's CI and installer checks are not proof of a clean production install. Validate a disposable VM first: install the Controller, create the first administrator, enroll a host, deploy a reviewed Blueprint, verify the game service, and test backup and recovery. Record the exact OS, release asset, commands, and logs. The Host Agent testing ZIP may be unsigned; verify its release checksums and follow the release's explicit instructions.
