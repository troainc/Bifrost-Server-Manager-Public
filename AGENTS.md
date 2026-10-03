# Repository instructions

Customer installer and compiled distribution only. Keep private application source, master service, credentials and private signing keys out of this repository. Install and operate as a non-root user with rootless Docker. Preserve installed data. Update README, CHANGELOG, CONTEXT and LOGS with changes.

## 2026-10-03 - Customer testing release preparation

Version v0.1.0-installtest.5 adds a compiled-image bundle builder, defaults to the bundled TROA P-256 verification public key when licensing setup is chosen, and lets the local operator explicitly enable license testing while review details remain pending. Normal template remains BIFROST_LICENSE_TEST_INTAKE=false. Optional analytics, owner administration and private issuer/source are not enabled or distributed. The PostgreSQL image stays on major 17, versioned with the bundle. Updates preserve existing keys, accounts, secrets, review facts and testing setting unless explicitly changed. No Ubuntu/game-host acceptance claimed. Three disposable license-setup test groups and Bash syntax passed; hosted packaging, image scans, public release and actual host tests remain pending.
