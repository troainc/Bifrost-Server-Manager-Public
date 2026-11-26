# Native Linux game install test package

Stationeers, Valheim and Palworld have a published controlled-test add-on with three master-signed blueprints, a matched compiled Host Agent and a guarded standard Test54 update tool. Follow the [installation guide](Native-Survival-Install-Test-Package.md) and download [bifrost-native-games.55.1.zip](https://github.com/troainc/Bifrost-Server-Manager-Public/releases/download/v0.1.0-runtime.55/bifrost-native-games.55.1.zip).

The runtime downloads automatically through verified HTTPS. Official game files download separately through SteamCMD. No game files, private signing keys, credentials or worlds are redistributed. The existing full signed application release stays unchanged.

Signed public catalog data is in `deployment/survival-catalog/`; reusable preparation templates are in `deployment/forge-templates/`. Existing Host approvals and publisher keys are retained by the explicit catalog import helper. The matched Alpha55 Controller is required for the new adapters; a catalog alone cannot upgrade an older Agent or Controller.

Actual rootless Podman game installation, managed settings read/save, restart and graceful stop passed for all three. The review binds the exact runtime/archive, downloaded layouts, process confinement and clean HIGH/CRITICAL/secret scan. The guarded updater passed 23 checks using real old/new archive bytes and disposable files, with systemd simulated. Operator restore/rollback, remote-player and longer-gameplay acceptance remains open. No bfsm upgrade or gameplay test was performed during package preparation.

Future game revisions remain subject to the master Forge's exact-digest review and signing gates. These controlled-test signatures do not claim six-check stable Forge promotion.
