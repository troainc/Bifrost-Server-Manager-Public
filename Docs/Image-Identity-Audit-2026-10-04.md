# Testing 6 image identity audit and repair

The installer successfully configures licensing and imports the images, then
compares `docker image inspect --format '{{.Id}}'` to IMAGE-LOCK.json. The lock
contains configuration digests produced by the packaging runner's classic image
store. The installer provisions Docker 29.8.2; its fresh containerd store reports
the OCI manifest digest as Id. These are different hashes of different metadata
for the same image. A direct equality check deterministically rejects it.

Private main bc5bf0e and public main 6c8c09f were refreshed before the audit.
The actual published customer testing 6 package was downloaded and checked
against its published SHA-256, then imported into isolated Docker 29.8.2 daemons.
No application containers, game processes, master deployment or customer VM
were modified during this audit.

| Image | Locked configuration digest | containerd image Id / archive manifest digest |
| --- | --- | --- |
| Controller | d93e716d4d8c8f380d040d77b4fece6bb28f763080e548461c63cc4331e8a661 | 09066a5b17edc277e8ce7b8b7b2e34752f3cc16bdf07af0b09cd40498cf5759e |
| Web | 5008ef0105059d2762e1ef537a60f903bc61525b3838f8e74dc87001823f6d11 | 2d4df712dbb894d71236c06e0f5396afc2c0a4187c0d0bf6a1b84bef60c6f4d3 |
| PostgreSQL | 4895b4d21c25a96e05e6e9220eb5f6dcb3ec37129129e282171c3234119f25df | 243d375794342aa4c09e0d86cfb8c5d8d7a96fce60e4ece41e33e9d5ea9a132a |

Hosted [reproduction run 37177955493](https://github.com/troainc/Bifrost-Server-Manager-Public/actions/runs/37177955493)
loaded the exact release: containerd produced all three mismatches above and the
repaired helper, embedded installer and embedded updater accepted all three.
The classic store passed with the expected configuration Ids. Final repeat
[image-store run 37178051391](https://github.com/troainc/Bifrost-Server-Manager-Public/actions/runs/37178051391)
passed both stores and both embedded scripts.
[Configuration run 37178051407](https://github.com/troainc/Bifrost-Server-Manager-Public/actions/runs/37178051407)
passed all 17 regression tests, Bash syntax and the actual pinned public updater
download/hash check.

The repair verifies configuration bytes from the archive against the locked
configuration digest. A manifest Id is accepted only when the archive's tag
descriptor identifies it, its bytes hash to that digest, and its config reference
equals the locked configuration. The loaded platform must be Linux amd64.
Other IDs, corrupt metadata, wrong locks/platforms, duplicate archive paths and
linked configuration metadata are rejected. The builder now derives locks from
saved configuration bytes, independently of the build daemon's storage backend.

The original release attachments are retained. The README directs users to the
current repository bootstrap. Its `--update` downloads the corrected updater at
immutable revision d6d5201b43e7d64388848e39c76ce9844ce00384 and verifies SHA-256
4fc6543061de24b805df1032a223d0be8f14a060558bffb38ed4f955a3b0fa75 before execution.
For an installation that reached testing 6 configuration, this preserves the
existing credentials/license settings and completes deployment using the same
verified application bundle. Older Debian database installations remain blocked;
the repair does not perform a cross-runtime migration.

The customer's direct image-ID output was not provided. The cause above is a
real reproduced installer defect under the runtime it provisions, not a claim
that a post-repair run on that particular VM has already succeeded.
