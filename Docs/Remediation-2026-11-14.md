# Bifrost audit remediation — November 14, 2026

Status: candidate in progress; no new rating or production acceptance earned yet.

The shared master/customer UI is being corrected for application-level modal portals, background/focus isolation, explicit provisioning-draft discard, stable Gate task routing, task-specific Gate composition, schedule editing with stale-plan detection and renewed authorization, file-selection/digest handoff, and a restore workflow in server Backups. Experimental Gate activation remains locked, visibly separate from supported game management. Existing TROA identity and all six themes remain.

Node 24.22.3 image pins and Host runtime archive digest come from official image metadata and Node release checksums. New passwords use scrypt N32768/r8/p3; valid legacy hashes are upgraded only after successful authentication, preserving password/MFA/enrollment data and using compare-and-set protection. No existing installation is mutated by these source edits.

The Controller panel, installation role (Controller, Instance node, Hybrid), separately enrolled Host Agent, and game server are different update/support boundaries. Panel-only updates preserve game data but do not patch the Host runtime or game software. The currently published immutable Host guide uses Test43; the newer runtime is an unpublished candidate until a fully verified signed release is prepared. Do not overwrite old release assets or claim current production is patched by this branch.

Ubuntu testing is explicitly owner-authorized; use disposable containers, no production credentials or Docker socket, monitored storage and automatic cleanup. No paid runners/services. Current checks and evidence are in work/bifrost-remediation-20261114 outside product repos. Failed harness attempts remain evidence. Full candidate verification, rendered review, and honest separate-edition rerating remain required. Real target/game/provider/assistive-technology/soak acceptance stays separate.
