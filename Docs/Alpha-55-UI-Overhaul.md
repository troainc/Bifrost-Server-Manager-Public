# Alpha 55 — UI Overhaul

Candidate version: **v0.1.0-alpha.55**. Main prepares the next Alpha build. The existing signed Test 54 release and its installer checksum remain immutable; this commit does not claim a signed Alpha 55 download is available.

## Included in the application candidate

- Refreshed game-server and Host workspaces, game banners, CPU/RAM/player gauges and reported FPS/simulation readings. Missing readings remain unavailable rather than fabricated.
- Cleaner blueprint details, visible SE2 preparation, game artwork management, console/file workflows and upload progress.
- Per-server Discord webhook or bot configuration with encrypted credentials and explicit test delivery. Actual external delivery requires operator credentials.
- Player management, settings coverage improvements, autosaved settings/drafts and toast feedback. Player data and game telemetry still require compatible game adapters.
- Master-only Bifrost Forge: single-game/batch drafts, content-bound test reports, signed channels, recipient delivery, withdrawals and retained recipe pins.
- Forge Build package and Guide: reusable templates, private file staging, verified SHA-256, configuration imports, artifact metadata and Lab draft preparation. Customer editions receive catalogs and have no publishing endpoints.

## Alpha naming and compatibility

New candidates use `alpha.N`; old signed `installtest.N` releases remain accepted. Alpha 55 continues the prerelease build sequence after Test 54. Stable release channels do not opt into Alpha automatically. Signature, artifact hash, source provenance, account/MFA, Host pairing and update-recovery checks remain mandatory.

The package source pins Alpha 55. Continue using the separately published signed release instructions until an Alpha 55 artifact has passed its build, scan, signature and download verification gates. A main-branch push is not a signed release or proof of game installation.

## Operator documentation

- [Forge operator guide](Bifrost-Forge-Operator-Guide.md)
- [Blueprint subscriptions](Blueprint-Subscriptions.md)
- Reusable authoring examples are under `deployment/forge-templates` in the compiled distribution package.

Local focused tests and GUI acceptance cover template preparation, uploads, defaults, draft saves and simulated catalog delivery. They do not certify every game, real Discord delivery, native SE2, or every production deployment. SE2 remains the reviewed 0.18.4 local-package contract. Scheduling, automatic test-Host orchestration, new adapters, signed artwork bundles and very-long-offline snapshot recovery remain future work.

No vendor game archives, private OCI inputs, production credentials or private application source are committed to this public repository.
