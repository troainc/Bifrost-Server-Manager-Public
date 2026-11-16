# Supported candidate scope and acceptance

Updated November 16, 2026. The production target is the **core server manager**. The owner explicitly keeps Gate as an opt-in experimental preview; unfinished cross-world gameplay is excluded from the core production promise. This is a scope decision, not completion of Gate gameplay.

The delivered controlled-testing build is immutable Test50;see [delivery and scope](Test-50-Delivery-2026-11-16.md). All28 assets,both offline verifiers,master deployment and four live TROA commands are verified. The catalogue has22 signed targets,not471 executable recipes. Owner target/manual/player/soak acceptance and broader requested engineering remain. Existing Host policy approval is preserved;editing this repository does not update an installed Controller,Agent or game. Older releases remain immutable;Gate stays opt-in experimental.

Current candidate evidence and category ratings: [Production core verification](Production-Core-2026-11-14.md). That candidate report does not promote the published commands.

## Two separate products

| Deployment | Included responsibility | Excluded authority |
|---|---|---|
| Private TROA master | Product owner accounts/MFA, installation registry, signed licensing, revocation, privacy policy and optional local ASN enrichment | Licensing identity does not grant control of customer fleets, Hosts or worlds |
| Public customer Controller, Instance or Hybrid | Customer accounts/MFA, explicit Host approval, signed jobs, reviewed local game policies, files and encrypted backups | Issuer service, owner accounts, license signing secrets and owner administration are removed from customer artifacts |

The separate Linux Host Agent is compiled customer code. No new native Windows distribution is included in this candidate. Windows source/contract checks do not establish Windows service or packaging acceptance.

## Initial operating envelope

- One Controller application replica and one PostgreSQL primary per installation. PostgreSQL coordinates jobs and authority; WebSocket hints stay process-local. Fallback reads continue at 15 seconds disconnected and 60 seconds connected.
- Initial beta planning ceiling: 10 enrolled Linux Hosts, 50 total game instances, 10 simultaneous interactive operators. This is a conservative operating restriction, not a certified maximum. The automated fleet benchmark records its actual smaller synthetic workload and excludes TLS, authentication, game CPU, vendor downloads and backup throughput.
- Keep PostgreSQL, runtime storage and encrypted backup storage on monitored persistent disks. Alert at 20% free; stop new installations and updates when required space/margins cannot be verified. Do not use game minimum storage as a platform sizing estimate.
- A page contains at most 25 Hosts by default (50 explicitly). Search is server-side, bounded to 20 matches with truncation. Activity includes 50 recent and 100 unfinished jobs with an explicit overflow warning; in-progress detail views track exact job IDs independently.
- Uncertain mutations block new disruptive work. Administrators can reconcile lifecycle uncertainty only using a fresh stable Host status plus fresh TOTP. File/package/restore recovery requires a rollback receipt bound to the exact interrupted job. Older receipts and ambiguous retained state require local operator investigation. Never delete locks/ledgers to force a retry.

Expand the envelope only after repeatable measurements at the proposed load, outage/reconnect tests, queue/drain observations and storage-growth/backup-throughput measurements. Multiple replicas remain outside this candidate's operating promise.

## Game and optional capability boundaries

| Capability | Candidate position | Acceptance required |
|---|---|---|
| Signed reviewed Linux x64 OCI recipes | Distribution supports the exact committed publisher catalog and immutable runtime/package identities | Exact game/version install, lifecycle, update, backup/restore and player join on target Ubuntu/Debian; acceptance does not transfer across runtime revisions |
| Space Engineers 1 / Torch on Linux | Existing reviewed Wine runtime only, where the signed recipe permits it | Real Steam entitlement/download, Torch load, selected ports and player join; no claim of a native no-Wine server |
| Reviewed Java/Bedrock recipes | Only recipes actually present in the signed handoff | Each exact vendor/runtime recipe needs its own target and player acceptance; synthetic package tests establish validation, not working games |
| Windows SCM and native Host | Source/contract work retained, excluded from this Linux release promise | New matched Windows package, dedicated service account/ACLs, recovery and real runtime acceptance |
| Space Engineers 2 and no-Wine SE1 | Roadmap, unavailable | Supported vendor interfaces and implementation before any support claim |
| Gate world coordination, map publishing and bridges | Experimental planning, hidden by default. Each account explicitly opts in through Profile or Settings → Experimental features, in that browser only. Disabling the preview retains saved plans. Activation, live travel and isolated Gate recovery execution remain locked/unavailable. | Separate bridge/game/network integration, rollback and operator acceptance; excluded from core readiness and no gameplay support promise |
| Extension registry and remote storage providers | Policy and configuration boundaries exist; no installed/connected claim follows from a catalog entry | Signed compatible package and explicit local approval; real destination/auth/recovery testing for each provider |
| AMP migration | Retired | `/api/migrations/*` stays unavailable; historical data/contracts are retained |

## Release gates

Core candidate gates include clean dependency audit, build/typecheck, customer/owner exclusion, regression and concurrency tests, database migration/grant checks, data-preserving update/master recovery, overlapping key trust, signed release verification, artifact scans and source-bound evidence. Failed gates stop promotion.

Separate human/external gates remain: independently reviewed code and security findings, approved signer custody/escrow, actual branch/ruleset/environment activation, successful exact-revision verification on authorized isolated capacity (free bounded Ubuntu workers are allowed; paid CI is not required), qualified privacy/legal review before general customer intake, target OS/game/player and accessibility acceptance, production secret/backup configuration, off-host restore and an agreed support/on-call owner. None is marked approved by local source changes.

Stable release additionally requires beta observation, recorded incidents/recovery, accepted performance/storage budgets, a supported-version/lifecycle policy and complete exact-target acceptance. A testing label must remain until those requirements are met.

## Core operator journeys

- First administrator: select the machine role, optionally name the installation, create the administrator, configure MFA/recovery, accept the agreements and activate the free license, then connect the explicitly selected Host. Going back before account creation preserves draft fields. The installer-selected role remains authoritative.
- Daily operation: select a Host/server, review freshness and capability, authorize the specific consequence, follow its exact job in Activity. Uncertain results are not success and must not be blindly resubmitted.
- File replacement: choose the server file, read its current digest, choose a replacement allowed by the Host policy, and renew authorization. Changing the selected file clears stale digest, file, preview and confirmation state.
- Backup restore: select an archive belonging to that server with a valid retained local copy and a verification receipt less than 24 hours old. Check the online Host's recovery state, then authorize replacement within one minute. The Controller independently rechecks permissions, archive binding and integrity. A queued restore keeps its job reference; uncertainty requires investigation before retry.
- Updates: panel update preserves configuration, accounts, MFA, keys and database, using the authenticated recovery checkpoint. Optional scheduled panel updates remain explicit opt-in. Host Agent, Host Node runtime and vendor games have separate update procedures; no timer is enabled by these source changes.

The candidate acceptance report must distinguish compiled fixture UI, real isolated database/container tests, exact signed delivery and the owner's manual production-target checks. Zero automated accessibility findings are not assistive-technology certification. Synthetic OCI execution is not vendor-game or player acceptance.
