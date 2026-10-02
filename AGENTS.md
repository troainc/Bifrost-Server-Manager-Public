# Public distribution repository instructions

- Publish customer deployment instructions and versioned deployment artifacts only.
- Do not copy application source, master owner-console code, owner-service code, private Compose overlays, owner credentials, private signing keys, or secret files here.
- Keep the standard customer Controller build free of the Connected installations owner UI and owner-service configuration.
- Never claim a test artifact is production-ready, signed, or independently reviewed without recorded evidence.
- Preserve the Debian/Ubuntu and amd64/arm64 support boundary until additional targets pass real-host acceptance.
- Before adding an installer, verify its source and version pinning, integrity checks, secret permissions, TLS assumptions, idempotency, failure recovery, and preservation of existing data.
- Update README.md, CHANGELOG.md, CONTEXT.md, and LOGS.md for changes.
- Keep VM tests disposable. Never wipe volumes or overwrite an existing installation as a troubleshooting shortcut.
