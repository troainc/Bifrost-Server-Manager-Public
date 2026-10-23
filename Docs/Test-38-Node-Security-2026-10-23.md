# Test 38 Node security candidate — October 23, 2026

Test 38 is in preparation. The current published testing release remains Test 37. Do not use the Test 38 source installer until the matching immutable signed Controller/web/Host release assets are published and verified.

The new installer pins the official Node 24.22.1 Linux x64 archive with SHA-256 `6c172a9ab6718f7b801fb5a7bd486af2ee5e32758086a04b84fcce2aa77095e6` for fresh automatic Hosts. Manual Host installation also requires Node 24.22.1 or later in 24.x. The Controller package uses a digest-pinned Node 24.22.1 runtime; the PostgreSQL image retains Test 37's exact image configuration. The panel-only `--update` command remains separate from enrolled Host Agent and game updates.

Current local evidence: the official archive checksum and runtime identity verify; isolated customer Controller/web builds and owner-exclusion checks pass; the new Linux Host archive builds and passes offline inspection/simulation; public shell, bootstrap, Python and Node regressions pass with hash-verified historical fixtures. The final signed package, image scans, disposable preserved-state update, publication/download verification and real target acceptance remain open. No customer or master installation has been changed.
