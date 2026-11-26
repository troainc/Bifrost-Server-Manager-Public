# Bifrost Forge operator guide

## Add a game
1. Open Settings > Blueprint releases > Build package.
2. Choose New game, then select the closest reviewed template or start with an empty OCI template. For an unknown Steam title/provider, have an engineer review its runtime and adapter first.
3. Enter a stable blueprint ID, display name and recipe version. A recipe version is the Bifrost package revision; the game version/build is separate.
4. Pin the OCI repository digest AND its image configuration ID. Enter the executable inside that runtime, one launch argument per line, ports, resource limits and readiness check. Do not use mutable image tags or shell installers.
5. Upload files. Config defaults can be imported into a safe relative initial-file path. JAR/ZIP/OCI archives are streamed into private staging and SHA-256 verified without executing or extracting them. Bind a verified upload to a vendor-artifact row to fill its size and checksum. Keep its approved vendor HTTPS URL. An upload does not make a private archive publicly downloadable.
6. Review defaults in the editor. Remove credentials and keep per-server passwords/tokens out of distributable defaults. Uploads do not generate a new settings adapter or infer every setting a game supports.
7. Check package. Resolve every schema, runtime, URL, path and resource error. Export the portable package JSON for review or reuse.
8. Create Lab draft. In Validation, record real install, settings, start, stop/start, backup/restore and rollback reports for each exact recipe digest/target.
9. Delivery: explicitly enroll pilot installations and configure their protected feed token/public trust files. A protected master signing key must be configured separately. No private key belongs on a customer Controller.
10. Releases: select the saved draft, check readiness, choose subscribed recipients and publish explicitly. Catalog applied means metadata received; Host approval and actual game installation remain separate.

## Update a game
Choose Update existing and select the exact current template. The builder preserves its runtime, ports, data mounts, readiness, terms and adapter; increments an ordinary recipe patch revision; and opens editable fields. Update the game version/build or authorized artifact URL and bind the newly uploaded file checksum. Keep the blueprint ID so recipients see a revision of the same game. Rerun all affected tests: old evidence never certifies changed recipe content. Existing installed instances are not automatically migrated or restarted.

SE2's current 0.18.4 local-package loader is explicitly pinned by the Agent contract. Uploading a newer runner does not create a compatible loader; a matched provider/contract update is required first.

## What files belong where?
- Blueprint/package JSON: imports the template itself.
- .cfg, .conf, .ini, .json, .properties, .toml, .yaml, .yml, .txt: bounded text defaults, up to 8,192 characters each and 16 files per recipe.
- JAR/ZIP/OCI/TAR/game binaries: private staging and checksum receipt. Vendor artifacts currently support file/ZIP up to 1 GiB; runtime archives use the existing approved public runtime-release policy. Private SE2 game archives stay on authorized Hosts.
- World saves, passwords, bot tokens, Steam login details and signing keys: never include them in a distributable template.

Uploads support files up to 8 GiB, 20 GiB reserved staging total and 128 receipts. Upload progress counts acknowledged bytes; checksum verification is a separate phase. Partial files survive browser closure; discard an unused copy or start a fresh upload. A hashing file can be verified again after a Controller restart. Original files on your computer are untouched.

## Release channels and recovery
Lab is for internal experiments. Pilot is for selected test installations. Stable is for wider tested availability. Recipients must subscribe to the selected channel. Use one game or up to 32 in a release. Withdraw removes a game from new-install choices; it does not stop running servers. Restore an old known-good recipe by copying it into a new higher-sequence release and supplying current reports.

## Current limits
Test orchestration, new executable/settings adapters, signed artwork bundles, scheduled publishing, customer pin policies and long-offline full-snapshot recovery are not automated yet. Releases expire after 90 days; an expired assigned release blocks unsafe catch-up. This guide describes the Alpha 55 candidate. Customer Controllers receive catalogs; publishing controls are master-only.

## Native Linux game templates

Stationeers, Valheim and Palworld Lab candidate templates are now included in deployment/forge-templates. Read [Native Linux game candidates](Native-Linux-Game-Candidates.md) before use. Their reserved runtime URL remains unpublished, and normal matched-build, test, signing and Host approval gates still apply.
