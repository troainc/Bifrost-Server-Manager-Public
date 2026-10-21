# Recovery and key rotation

All commands below are operator procedures for a future approved maintenance window. October 21 validation uses synthetic local fixtures only. Existing deployed keys, accounts, databases and customer machines are untouched.

## Customer update recovery

The signed updater holds a hard-link/symlink-safe installation lock, stops Controller/web/HTTPS writers, makes a custom PostgreSQL dump, verifies its index and encrypts the dump with exact configuration and keys before applying configuration or migrations. The authenticated envelope uses AES-256-CBC with PBKDF2-SHA256 and an independent encrypt-then-MAC key. Its 64-byte recovery key lives at `secrets/update_recovery.key`, outside the archive. Escrow that exact file separately; a replacement random key cannot recover an earlier checkpoint.

An update journal and encrypted checkpoints are retained under the installation root. A failed update leaves the managed UI services quiesced, preserves the original database/volume and prints the checkpoint path. Review with the checkpoint's retained helper, then use its explicit `recover` action and `--confirmation 'RECOVER <checkpoint-id>'`. Run as the existing non-root service account. Recovery authenticates before decrypting, restores into a **new** database and reconnects the saved configuration to it. It also retains encrypted failed-candidate configuration and keys. Managed application keys are checkpointed and checked before reconnecting saved ciphertext; out-of-band key changes are refused. Custom Compose overlays require a separate reviewed procedure. No database or volume is dropped. A later update snapshots the newly selected database. Retrying an interrupted recovery creates another new database and preserves partial attempts for investigation.

Recovery is a database/configuration checkpoint, not a reverse migration. Preserve original images until recovery acceptance. Host game worlds and Agent ledgers are independently managed and are not erased by a panel update. Existing cross-libc/PostgreSQL runtime migrations remain refused; they need a separately reviewed logical migration.

## Private master recovery

The TROA licensing/owner master has a separate private two-database recovery procedure and protected keys. Customer packages do not contain those services, keys or private maintenance commands.

## MFA and configuration encryption overlap

Controller secrets support `BIFROST_MFA_KEYRING_FILE`; private issuer-owner MFA uses the separate `LICENSE_OWNER_MFA_KEYRING_FILE`. Both are optional protected JSON files; absence retains existing v1/c1 behavior. A ring has `schemaVersion:1`, `activeKeyId`, optional `legacyKeyId`, and up to eight `{id,keyBase64}` entries. IDs are `sha256-` followed by SHA-256 of the exact 32 decoded key bytes. Retain the current key as `legacyKeyId`; add a fresh random key and select it for new writes. Never reuse the Controller key for issuer owners.

Versioned v2/c2 ciphertext binds the key identity and purpose with AES-256-GCM AAD. Existing v1 MFA and c1 configuration values remain readable during overlap. First deploy dual-read support everywhere, escrow the complete ring, then activate the new key during approved maintenance. Rollback code must understand v2/c2 and retain both keys. Old code that knows only v1 cannot read new envelopes.

Offline migration defaults to read-only inventory:

```sh
node apps/control-plane/dist/ops/encryption-rotation.js --role controller --keyring /protected/controller-ring.json
```

Use the matching owner database URL through the protected process environment, not argv/history. Apply additionally requires `--apply --writers-stopped --backup-reference '<exact verified checkpoint>'`. The tool refuses other active database clients, unrecognized encrypted columns, missing keys or corrupt ciphertext. It uses one serializable transaction, decrypts/re-encrypts bounded batches, covers nested pairing/enrollment secrets and appends a maintenance audit record. It prints counts/key IDs only. No key is deleted or automatically retired. The dedicated issuer CLI is excluded from customer images.

Do not remove a retained key until database inventory is empty for it, all stopped/remote versions are upgraded, local state and pending pairing data are inventoried, and retained backups have a tested decrypt/recovery path. Backup retention and escrow can require keeping old keys much longer than live ciphertext. Windows key-file ACL acceptance remains a separate native service check; a POSIX mode check is not Windows ACL validation.

## License signing overlap and compromise

Issuer grants now include a P-256 public-key fingerprint. Keep prior trusted keys in `BIFROST_LICENSE_PREVIOUS_PUBLIC_KEYS_FILE` on the issuer and a reviewed `{schemaVersion:1,keys:[public PEM strings]}` file referenced by `BIFROST_LICENSE_PUBLIC_KEYS_FILE` on customers. Existing primary public-key pinning remains required. Trust is installed by an explicit approved package/configuration change, never learned automatically from discovery or a grant.

Roll over customers to trust old+new keys first; verify overlap, then change the issuer's current private signing key and retain old public verification for existing grants. Retire old public trust only after outstanding grants (up to 14 days), supported offline clients and rollback/backup requirements are accounted for. Compromise response may deliberately revoke old trust and require reactivation; it needs an owner-approved plan. Licensing outage or revocation never authorizes terminating running game processes.

The separate Ed25519 **release** key signs whole-release manifests. Game publisher keys, job keys, licensing keys and encryption keys have different purposes and are not substitutes. The new candidate release key is local-only and has no production custody approval. Whole-release signing authenticates bytes; it does not establish manual acceptance or permission to publish.
