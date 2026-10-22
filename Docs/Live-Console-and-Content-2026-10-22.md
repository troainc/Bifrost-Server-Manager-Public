# Local Console and content candidate — October 22, 2026

Unpublished local implementation. Published Test 35 installation assets and commands remain immutable. No live installation, master, accounts, worlds or volumes were changed by this work.

The shared customer build now includes continuous bounded live output, explicit Torch command access, stopped-server Workshop world-file edits, and reviewed Torch ZIP installation with manifest/dependency/hash checks, retained originals and rollback. The three optional TROA Workshop mods remain choices; the game downloads Workshop content at its next start. Third-party ZIPs are correctly labeled unsigned. Registry/GUID downloads are not part of this ZIP workflow.

Controller/Agent capability negotiation protects older installations. New commands and content jobs require the upgraded Agent capability; legacy operations retain their contract. Send game console commands is a separate permission, granted to administrator defaults and explicitly delegated to other intended users. Existing stored user/role assignments are preserved. The customer build excludes the private owner registry.

The local Console plugin compiles against Torch 347. It uses a fixed local mailbox and the game command API, with expiry checks and at-most-once handling. It has no Host shell or network listener. It is independent of Gate. Actual Wine/native Torch loading, game commands, Steam downloads, player joining and real-world mod/plugin compatibility still require target acceptance. Rollback restores managed files; keep a full-world backup for runtime game changes.

Local application, native filesystem, protocol, standalone package and public installer tests pass. New immutable signed artifacts, a matched runtime/catalog build and rollout approval are required for delivery. No publication, deployment or paid service is authorized here. Continue using the current published commands until a new release is explicitly approved and verified.
