# Prepare an existing Linux Host for SE2

Test 54 includes the signed Space Engineers 2 / SE2 Online 0.18.4 blueprint,
the setup GUI and the compiled Linux Host approval helper. The runtime uses
Wine inside rootless Podman. This is a controlled-testing option; installing
Bifrost does not install the private game files or establish game readiness.

## Exact private inputs

Obtain these original files through an authorized private source. Official
replacement downloads may require Steam ownership verification. Bifrost does
not distribute these files, and the public installer cannot download them.

| File | Bytes | SHA-256 |
|---|---:|---|
| `Y51_SE2Online-DedicatedServer-0.18.4-standalone.1-win-x64.zip` | 7406346808 | `912e007e0c06c6bce3054462b5724166870b75c58bf46d1f19c7b8191b31a140` |
| `bifrost-se2online-automatic.oci.tar` | 634207232 | `efa359e0fd3ce24aa9d83e2a3741e0818143f7fa9e25f462eb76a0b61798a98d` |

Verify both complete hashes and sizes before preparation and again after
transfer. A filename, partial checksum or differently exported OCI archive is
insufficient. Keep the signed recipe unchanged; different bytes require a
separately reviewed and signed recipe.

## Preserve and prepare the existing Host

Use the existing game-service account, which can differ from the panel
account. Resolve the running Agent's application, Node executable, configuration
and service from its current service definition. Use the installed Test 54
`dist/configure-se2-provisioning.js` and its matching
`se2online/distribution/` files. Do not replace the Agent with an older private
preparation bundle, re-enroll the Host or recover panel credentials.

Copy the two verified files into a new directory owned by the game-service
account, outside every instance directory. Its mode must be 0700; both files
must be regular, single-link, owned by that account and mode 0600. Do not use
symlinks or hard links. Retain the original private assets separately.

Stop the existing Agent service before approval. Under the same unprivileged
game-service account, run the following template with the actual resolved
paths and installed Node executable:

```sh
node /installed-agent/dist/configure-se2-provisioning.js \
  /existing/host-agent.json /private/se2-assets \
  /installed-agent/se2online/distribution/provisioning-catalog.json \
  /installed-agent/se2online/distribution/provisioning-trust.json
```

The helper preserves the original configuration in a private backup and writes
new versioned policy/catalogue/trust files. It retains existing signed recipes,
publisher keys and profiles, adding the private package root. Retain its
backup and existing enrollment, ledger, keys and bootstrap. Restart the same
Agent service and wait for an authenticated fresh heartbeat. The master should
then offer that Host for SE2. If approval already exists, investigate the exact
existing policy instead of replacing it or repeatedly running the helper.

## Install through the GUI

In the authorized Controller, open **Game blueprints → Space Engineers 2 ·
SE2 Online → Install server**. Select the prepared Host, name the instance,
and configure the Server, World, Water and Advanced panels. The chosen settings
must survive Back/Forward navigation and appear in the review. Reserve at least
8192 MiB and two CPUs; the default game/query ports are UDP 27016/27017.
Query follows game + 1. Review public advertising and optional Discord settings
explicitly; Discord export does not start a worker or send messages.

Read and accept the supplied licence only if authorized, review configuration
and placement, then confirm one intended installation. Follow its exact job
instead of retrying an unresolved submission. Bifrost verifies and extracts the
private package, imports the approved runtime and waits for fresh status from a
loaded, hosted world before committing the instance. Do not manually launch a
container to bypass provisioning.

Test 54 storage estimates are advisory. No storage waiver, timer or forced
instance ID is needed. A real full filesystem still fails and retains
diagnostics. CPU/RAM/port policy, signatures, private-file checks, extraction
bounds, isolation and authorization remain enforced.

Record the job/instance identity, exact recipe/runtime, generated configuration
and ports, fresh readiness, console/logs, graceful stop/start and readiness
again. A running container alone is insufficient. Record a successful client
join separately; player, live Discord, soak and backup/restore acceptance are
separate results. Preserve existing accounts, MFA, pairing and all other fleets.
