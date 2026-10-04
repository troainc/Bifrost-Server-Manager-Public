# Repository instructions

Customer installer and compiled distribution only. Keep private application source, master service, credentials and private signing keys out of this repository. Install and operate as a non-root user with rootless Docker. Preserve installed data. Update README, CHANGELOG, CONTEXT and LOGS with changes.

## 2026-10-03 - Customer testing release preparation

Version v0.1.0-installtest.5 adds a compiled-image bundle builder, defaults to the bundled TROA P-256 verification public key when licensing setup is chosen, and lets the local operator explicitly enable license testing while review details remain pending. Normal template remains BIFROST_LICENSE_TEST_INTAKE=false. Optional analytics, owner administration and private issuer/source are not enabled or distributed. The PostgreSQL image stays on major 17, versioned with the bundle. Updates preserve existing keys, accounts, secrets, review facts and testing setting unless explicitly changed. No Ubuntu/game-host acceptance claimed. Three disposable license-setup test groups and Bash syntax passed; hosted packaging, image scans, public release and actual host tests remain pending.

The patched Debian 12 PostgreSQL image still reported 16 CRITICAL and 102 HIGH findings without available fixes. The new customer testing bundle uses patched Alpine PostgreSQL 17 under its non-root postgres account. This changes libc/locale and runtime ownership; old Debian bundles are therefore refused by the updater before download or file/database mutation. A fresh installation or independently verified backup/restore migration is required. New Alpine installations carry BIFROST_POSTGRES_RUNTIME=alpine17-v1. The existing master database/runtime is unchanged. Clean-host and game acceptance remain deferred.

## 2026-10-03 - Published customer testing download

v0.1.0-installtest.5 was published at 19:02:06Z: https://github.com/troainc/Bifrost-Server-Manager-Public/releases/tag/v0.1.0-installtest.5 . Hosted build run 37146002967 verified compiled issuer/source isolation, three zero HIGH/CRITICAL vulnerability and secret scans, actual bundled fresh database migrations and first-admin setup over verified disposable HTTPS, and a separate Linux Host Agent archive without application source maps. The downloaded build artifact digest and all 11 uploaded release asset digests were checked; anonymous latest installer and SHA256SUMS match. Bundled public issuer key is readable by the non-root Controller.

This is a fresh-install testing download. Home Ubuntu installation, enrollment, game lifecycle, backup/recovery and failure acceptance remain for the owner to perform. Linux Host Agent is unsigned testing only. Earlier Debian database runtimes are refused by the updater before mutation; use a fresh install or separately verified backup/restore migration. No private issuer, private application source, credentials or private signing keys are distributed.

## 2026-10-03 - Disclosure v5 customer integration refresh

Prepare v0.1.0-installtest.6 for the creator's current Controller features and disclosure version 5. Personal user agreement acceptance is separate from administrator installation-license consent. The customer Controller cannot enable owner registry/configuration/recovery APIs, even through environment flags. Customer privacy identity and location belong to the local operator and default blank. The Alpine 17 update compatibility guard and data/key preservation remain unchanged. Hosted packaging, fresh migrations, image scans and licensing flow must pass before publishing; real Ubuntu and game-host acceptance remain pending.
