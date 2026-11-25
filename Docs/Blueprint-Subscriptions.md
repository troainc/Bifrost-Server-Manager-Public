# Signed blueprint subscriptions

Alpha 55 adds an optional receiving worker to compiled customer Controllers. Publishing is available only on the authorized master, through its separate publishing permission and protected signing boundary.

An operator explicitly creates a subscriber on that master and provisions its one-time feed credential and approved **public** publisher trust ring on the receiving Controller. Do not put the master private signing key, license keys or Host pairing credentials in subscription configuration.

Set these receiving Controller values only after the files exist:

```
BIFROST_FORGE_MASTER_URL=https://your-master.example
BIFROST_FORGE_RECIPIENT_ID=<assigned recipient UUID>
BIFROST_FORGE_TOKEN_FILE=/var/lib/bifrost/keys/forge/feed-token
BIFROST_FORGE_TRUST_FILE=/var/lib/bifrost/keys/forge/public-trust.json
BIFROST_FORGE_CHANNELS=stable
```

The compiled Compose template passes these optional variables through. Its existing private Controller key volume can hold the two protected files. They must be real service-owned files with mode 0600 or stricter on Linux; do not replace the surrounding volume or existing keys. The token is the purpose-specific Forge credential. The trust file maps approved Ed25519 key IDs to their public PEM values. Windows uses the protected ProgramData/Bifrost ACL policy.

Receiving is disabled when the required settings are blank. HTTPS, signatures, recipient scope, subscribed channels, expiry and increasing sequence numbers are checked before activation. The worker polls every 30 seconds. Lost acknowledgements are retried without installing a game again. An invalid release preserves the previously active catalog.

Catalog applied means that metadata was received. It does not approve Host policies, accept vendor terms, download private game files, install or restart a server. A compatible Host and provider remain required. Previously created install jobs keep their exact recipe digests. Withdrawals stop offering affected blueprints for new installation; they do not stop running servers.

Release validity is 90 days. An expired assigned release blocks unsafe catch-up; full-snapshot recovery for longer offline intervals is not yet implemented. Keep existing subscription keys during deliberate publisher rotation until retained releases have a reviewed recovery path.
