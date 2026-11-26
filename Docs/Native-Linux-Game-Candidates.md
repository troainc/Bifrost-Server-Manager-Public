# Native Linux game candidates: Stationeers, Valheim and Palworld

Three additional native Linux dedicated-server packages have been prepared and tested under rootless Podman. These are **Lab candidates**, not an announcement of a published automatic-install catalog or a replacement signed release.

| Game | Steam server app | Initial resources | Default UDP ports |
| --- | --- | --- | --- |
| Stationeers | 600760 | 12 GiB / 4 CPU | 27016 game; 27015 update/query |
| Valheim | 896660 | 4 GiB / 2 CPU | 2456 game; 2457 query |
| Palworld | 2394010 | 16 GiB / 4 CPU | 8211 game |

The portable authoring documents are in deployment/forge-templates. They include native runtime identity, download policy, game-specific settings and persistent-data layout. The reserved runtime HTTPS asset in these candidate documents has not been published. Importing a template does not activate it.

## What was verified

All three official Steam packages installed using the Bifrost SteamCMD wrapper under actual rootless Podman 4.9.3 on Ubuntu 24.04. Each game started, used its configured ports, saved its world and reopened the same persistent files after stop/start. Palworld's live local API confirmed the configured server name, daytime speed and experience multiplier. Stationeers loaded its selected Mars world and retained its saved station. Test servers were stopped afterward.

Twenty-nine focused automated checks passed, covering native launch validation, settings/persistence, signed catalog/install requests, Forge authorization/release gates and GUI component rendering. Component rendering is not an end-to-end authenticated GUI installation or remote player-connection test.

## Configuration and updates

- Valheim requires consecutive game/query ports. An empty password default generates a privately persisted password on first start. Applying an enabled world key adds it; disabling a previously saved key requires an explicit preset reset or the game controls.
- Stationeers keeps its working directory, saved stations and writable terrain assets outside executable/library files. The signed package declares these paths; owners do not enter launch commands.
- Palworld passes the reserved port to the actual listener as well as its listing metadata. Save data remains under the persistent Pal/Saved mount. RCON/REST are disabled in distribution defaults; credentials and structured platform options remain protected from the scalar editor.

A matched Controller and Host Agent build is required before using these settings adapters. The existing Agent 54 does not gain new adapters through a catalog-only update. A publisher must complete the remaining backup/restore, rollback and target acceptance reports, publish the immutable runtime, then sign and distribute the reviewed catalog through Forge. Existing customer data, accounts, pairing and immutable signed releases are unchanged. No game files, private application source or signing keys are included here.
