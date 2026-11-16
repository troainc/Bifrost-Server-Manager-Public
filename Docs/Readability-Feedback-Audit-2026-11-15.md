# Bifrost master and public instance: harsh UI/UX and release audit

**Live master sign-off is blocked.** After Test49 deployment, the owner-browser path returned502, then loaded the protected temporary-unavailability screen because setup/API requests still returned502. All six application services and server-origin HTTPS checks are healthy. Sanitized Caddy errors show requests dialling the removed web address while its active route points to the current container. A forced graceful reload of the identical configuration did not resolve it. Retained connection/config handling is an inference; the stale-dial/current-route mismatch is directly observed. A brief restart of the shared Coolify proxy is prepared but has **not** been run: owner approval is pending because it can interrupt every TROA site. No security/TLS/data/billing setting was changed. [Documented Caddy reload method](https://caddyserver.com/docs/api#post-load).

Scores below assess the verified compiled UI, not successful owner-browser availability. **Current live master production readiness:5.5/10 while this gateway blocker remains. Public candidate core confidence:8.0/10 pending real target acceptance.** The table's master8.2 production-core judgment is conditional on clearing the gateway and completing owner acceptance; it is not the current deployed sign-off.

November 15, 2026, New York. This assessment covers the actual master and customer application editions, including interaction states. The public repository is distribution tooling; the customer UI is compiled separately from the private application source. Gate remains opt-in experimental. Category scores are critical design judgments, not percentages of proven correctness or a guarantee against regressions.

Test47 missed a basic requirement: licensing and other text could appear directly over detailed artwork. Its positive visual rating was not sufficient evidence. Test48 corrects shared content protection and notification behavior; Test49 completes browser-local AMP feedback and repairs actual multiline entry. This review supersedes earlier visual/readiness claims for the delivered builds. Final release identities and live receipts are in the matching delivery report.

## Category ratings, out of 10

| Category | Master | Public instance | Evidence and remaining weakness |
|---|---:|---:|---|
| Text legibility and surface protection |8.8|8.8|Protected page context, route bodies, license/setup/recovery, pagination and Host disclosure. Worst-case white-art compositing and actual rendered text measured. Exotic browser/OS/font rendering still needs acceptance.|
| Spacing, margins and alignment |8.6|8.6|Shared24px/phone16px insets, one route surface, flat inner forms, full-width320px heading actions. Long administration forms remain dense.|
| Typography and information hierarchy |8.5|8.5|Readable captions, restrained headings and clear action groups. Extensive technical configuration still requires expertise.|
| Frozen TROA/Bifrost brand and art |8.7|8.5|Original detailed desktop/portrait paintings, canonical frozen master helm/favicon, black shell and glacier accents. Artwork taste remains subjective; custom customer brand stays distinct.|
| Navigation and orientation |8.4|8.4|Grouped destinations, active context, responsive section chooser, search and draft-preservation checks. Many-server shortcut disclosure still needs search at scale.|
| Search/control geometry |8.7|8.7|Search input/button align;48 geometry states and24 submitted searches. Long fleet names and small screens covered; huge production fleets are not newly benchmarked.|
| Primary iconography |8.2|8.2|Restrained custom themed glyphs retain visible labels. Secondary vendor/tool icons remain ordinary; the theme is not a reason to obscure recognition.|
| Operational task design |8.5|8.5|Target context, permissions, disruptive confirmation, uncertain state and retained receipts. Multi-operator slow-provider acceptance remains.|
| Toast/action feedback |8.8|8.8|Global mutation results, scoped local/copy/download/refresh feedback, terminal-job handoff, repeated actions and errors. Errors/warnings persist; success/info expire after8seconds. Five-toast cap and generic server messages remain limitations.|
| Loading, empty, offline and failure states |8.5|8.5|Explicit retries, retained last-known graphs and truthful unsupported/offline states. Vendor-specific failures are not exhaustively observed.|
| Live Host/server visuals |8.3|8.3|Host and game-process readings separated, occupancy/freshness and bounded history retained. Actual new readings require a matched reachable Agent and supported game API.|
| Data honesty |8.8|8.8|NULL/stale/offline are not fabricated zeroes; NULL optional telemetry cannot hide a server. System disk is labelled rather than pretending to be world storage.|
| Retained Console |8.6|8.6|History loads on entry; pause/follow affects following, not collection. Reconnect/gaps/unsupported states and manual refresh feedback covered. Retention windows and old Agent capability remain limits.|
| File Explorer |8.5|8.5|Tree/breadcrumb hierarchy, icons, selection, keyboard/pointer destinations, uploads and recoverable conflicts covered. Batch moves are per-item transactions; real OS/touch drag still needs acceptance.|
| Forms and validation |8.5|8.5|Field context retained, typed settings, conflict checks and multiline AMP drafts preserved through typing. Some long forms could use further task decomposition.|
| AMP import/review experience |8.0|8.0|Actual browser-local save/import/export, redaction and assessment failure paths now have toasts; invalid port drafts do not overwrite saved snapshots. This remains an advisory workbench, not a completed automatic AMP cutover product.|
| Game-specific settings breadth |7.2|7.2|Eight typed families. A catalog entry does not create a complete settings/API adapter.|
| Backup/restore and recovery UX |8.5|8.5|Contextual archive, current Host preflight, digest/expiry and explicit authorization; uncertain outcomes retain references. Exact-image encrypted restore proofs pass; power-loss/provider acceptance remains.|
| Scheduling/automation |8.2|8.2|Real authorization/history/conflict tests inherited on identical backend inputs; explicit refresh feedback retained. Real timed game/provider effects remain owner acceptance.|
| Responsive layout |8.5|8.5|320/390/tablet/desktop, long labels, dialogs, alternate themes and small-screen action geometry covered. Physical touch/zoom/keyboard combinations remain manual.|
| Accessibility |8.1|8.1|Measured automated WCAG A/AA states, focus, accessible notifications and reduced-transparency coverage. Automated zero violations is not assistive-technology certification; incomplete criteria remain open.|
| Performance |8.0|8.0|Lazy hidden work, bounded queries/history, separate optimized artwork under512KiB each. Glass GPU cost, maximum fleet size and sustained latency lack a real production profile.|
| Security and authority |8.3|8.4|Signed Host authority, permissions, strict receipts, account-scoped feedback and compiled edition exclusion retained. No new authority change. Scans are clean for three delivered images; this is not an independent penetration test.|
| Accounts/MFA and preservation |8.5|8.5|Existing locking/replay/permission tests retained; actual master checkpoint and protected-field comparison required for deployment. Native Windows target acceptance excluded.|
| Master licensing administration |8.3|N/A|Previously exposed licensing text protected; full action labels and owner-only artifact boundary retained. Large real registry workflows are not newly soaked.|
| Install/update/signature engineering |8.6|8.6|Immutable signed assets, actual Linux Agent, image identities/SBOMs, offline verifiers, encrypted restores and anonymous hashes. Panel update, Agent update and game update remain distinct operations.|
| Release clarity/documentation |8.5|8.5|Fresh/inherited/manual evidence separated; no blanket compatibility claim and no wipe/reinstall commands. Older reports remain historical and must not be read as current acceptance.|
| Maintainability |7.2|7.7|Shared surfaces and notifier reduce drift; large App/Gate components and layered CSS remain significant debt. Narrow public distribution is simpler.|
| Core product design |8.2|8.2|Coherent operational journeys and more honest capability boundaries. Game coverage is uneven and complex recovery concepts remain visible.|
| Universal Steam provisioning coverage |4.5|4.5|471 definitions/455 launch metadata are not471 signed executable runtime/data/port/readiness recipes;16 launches absent and many recipes still incomplete.|
| Production core confidence |8.2|8.0|Verified candidate/release suitable for controlled owner acceptance. Real target/soak evidence is still required for unrestricted production sign-off.|
| Gate experimental product, outside core |5.8|5.8|Opt-in planning and tools retained; unfinished cross-world gameplay/cutover is not relabelled production-ready.|

**UI/UX judgment:8.6/10 for both editions.** This does not average away incomplete game coverage or grant a stable-production sign-off. The readability defect is fixed in a shared structure rather than a one-page color patch.

## Interaction coverage and what it proves

| Journey | Verification | Boundary |
|---|---|---|
| Sign-in, secure setup and recovery |Protected captions/footer/setup, retained drafts and account exit states|Real account/MFA configuration not changed for fixtures|
| Overview and Host telemetry |Individual protected widgets; graph selection/history; offline/stale/NULL data|Actual Fenrir Agent remains unreachable|
| Game server inventory/search |Long labels, geometry, filtering, submitted search, current destination and no hidden NULL servers|No new maximum-fleet production benchmark|
| Settings/license/registry |Whole readable route, disclosures, responsive navigation, repeated save/failure and clipboard|No real license revoke/rotate test on production|
| Console |Retained history on entry, live follow/reconnect, pause/resume/manual refresh/error feedback|Synthetic retained data and tiny fixture Host actions; no real game commands|
| Explorer |Actual tiny-file fixture upload/move/tree/breadcrumb/keyboard/pointer, collisions, stale/retry/offline and phone long paths|Native browser/OS/touch drag remains owner-run|
| Game settings and content |Typed save/conflict, package and permission/capability states|Eight adapters; no universal vendor acceptance|
| AMP local workflows |Real React components in a separate compiled fixture: character-by-character multiline input, repeated save, invalid draft retention, JSON imports/downloads, blocked storage/download, sanitized assessment and errors|Separate helper fixture is distinct from full-app integration, no AMP or Host connection|
| Backup/restore |UI guard journeys plus exact image migrations and two actual encrypted database restores|Compose lifecycle simulation is explicitly separate from real target interruption|
| Automation/integrations |Forms, permission states, explicit refresh and action results|Real email/Discord/provider effects not activated|
| Optional Gate |Default-off entry, tasks/drafts, availability and existing lock/permission boundaries|No gameplay/cutover completion claim|
| Toast lifecycle |Success/error, repeats, keyboard dismissal, modal reachability, account scope and released terminal-job handoff|Burst cap5; durable job history remains the recovery record|

## Evidence ledger

Test48 full broad sweep:96 master/93 customer screen states and6,667/6,259 text runs, against real rendered ancestors plus a deliberately white artwork pixel. Require at least80% protective opacity and4.5:1 text contrast (3:1 for large text). This is stronger than treating an automated accessibility scan over arbitrary image pixels as complete contrast proof. App/CSS/artwork are unchanged in Test49; label that full matrix inherited48, not fresh49.

Fresh final Test49: Linux/web types and builds;2,326 enabled Node cases, zero failures, nine explicit environment gates;149 unique public Python cases across regular/root suites and67 Node;510 TROA units,73-page build/types. Shared Agent tests now select Linux explicitly without loading/building Windows; default ordinary CI retains both platforms. Both compiled editions repeat five affected suites: ten feedback cases,21 game workflows/29 measured accessibility states, eight interfaces,22 core/11 states, and75/73 expanded accessibility states. The actual React AMP helper fixture is recorded separately with its exact case count.

Deliverable verification requires three exact scanned images/SBOMs, development-inclusive lock scan, compiled customer owner/issuer/source exclusion, matched Linux Agent archive, actual migrations/two encrypted DB restores, source binding, offline Ed25519 verifiers and all25 anonymous public asset identities. Master deployment requires a fresh authenticated on-host two-database checkpoint, six healthy services, original mounts,16 secrets, retained managed keys/branding, exact80-row journal, account/security and protected identity comparisons. TROA verification checks all four password-gated no-store commands, exact hash/version, valid/invalid password responses and absence of wipe UI.

Inherited on unchanged backend/Host/contracts: seven real DB route cases and two generic rootless Podman cases from Test46 through48/49. Do not call these fresh49 or vendor-game compatibility. Separate native-game runtime retains35 low/medium advisories; clean application-image scans do not erase those. Failed contrast/geometry/SSR/harness attempts and the first cross-platform scope failure remain retained, never counted as passes.

## Remaining engineering, separate from manual acceptance

1. Complete concrete signed Steam runtime/persistence/architecture/dependency/ports/readiness recipes and missing upstream launch facts. Do not fabricate compatibility or bypass vendor credentials/terms.
2. Deliver/accept the matched Agent on Fenrir when its verified OS/network connection is available. Panel deployment cannot generate readings absent from an old Agent.
3. Expand actual vendor APIs and typed settings beyond the current families. Keep unsupported data explicit.
4. Reduce App/Gate/module size and layered CSS debt incrementally while preserving contracts. Profile glass GPU cost and fleet/request behavior at real scale.

Owner target acceptance remains: Debian/Ubuntu install and in-place update, interruption/rollback, selected games/players/plugins, actual storage/provider failure, OS/touch/zoom/manual assistive technology and sustained soak. No finite deterministic suite proves every outside environment or the absence of every regression. No paid service, billing change, Actions dispatch, Windows application workload, unrelated prune or private-source remote QA export is authorized by this review.
