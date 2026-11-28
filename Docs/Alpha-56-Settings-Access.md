# v0.1.0-alpha.56 - Settings & Access Overhaul

Display: **Bifrost Control Plane · v0.1.0-alpha.56 - Settings & Access Overhaul**.

## Included changes

Settings uses one flat workspace, grouped desktop navigation and a mobile section picker. Installation identity and time zone, email delivery, license and privacy have separate views. Existing autosave/toasts and explicit mail-credential saving remain; the main application menu is unchanged.

People & permissions uses a flat directory and searchable matrix with twelve granular file/game-settings grants. Existing files.manage grants remain effective. Editing expands that umbrella into individual grants, so denying one action works. Changes keep generated audit context, MFA/CSRF checks, session revocation and last-admin safeguards.

Each server's Settings → File uploads can restrict approved extensions and file size up to 32 MiB. Policy persists privately on the Host and applies to upload inventory and actual transfers. Revision checks prevent stale overwrites, staged uploads block policy edits, and old Agents do not advertise the settings capability. The Controller and Linux/Windows Agent must be updated together for this feature. Host file roots, read-only mounts and approved types remain authoritative; this does not introduce per-user folder ACLs.

Native-drop compatibility handles missing metadata and non-bubbling events, modern folder handles and bounded FileList fallback. Automated native-style tests are separate from an actual Windows drag in a live browser. Live native-gesture verification remains pending.

## Delivery status

This is a source candidate for main delivery, not a signed downloadable release. Normal builds may run after the authorized push; their outcomes must be checked separately. No customer update or live Host upgrade is part of this source delivery. Public distribution remains compiled artifacts plus installer metadata/documentation; private application source, vendor files and keys remain excluded. Existing signed Test54 assets remain immutable and its in-app installer pin stays unchanged until a new release passes publication gates.

## Version discipline

Every product change must advance the alpha.N version and update its named changelog section. Keep private package versions, Controller/web display identity, Compose/build tags and public installer candidate metadata matched. A build name is display text, not part of the machine-readable SemVer tag. CI rejects private product changes without a version advance and changelog update; distribution checks reject private/public version drift. Historical signed versions must never be relabeled.
