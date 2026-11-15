# Customer instance remediation and harsh audit — November 14, 2026

Final: compiled-customer checks, selected rendered review and cleanup complete; production delivery and owner target acceptance remain pending. This supersedes historical 8.0 design judgments for the new candidate. The November 13 independent baseline was 4.5 overall; the new candidate judgment is 7.0. These are design/engineering judgments, not certification.

This repository contains installer/distribution tooling. The customer UI and Controller are separately compiled from shared application source. Private application/issuer source, owner registry and signing secrets are excluded from customer distribution. Current source changes are local and unpublished. Existing immutable Test43 and all prior downloads remain unchanged; no installed Controller/Host/game or update timer was changed.

## Main customer ratings

| Category | Baseline → candidate /10 |
|---|---:|
| UI execution | 5.0 → 7.8 |
| User experience | 4.0 → 7.0 |
| Visual design | 5.5 → 7.7 |
| Product design | 4.0 → 6.5 |
| Performance | 6.5 → 6.8 |
| Security | 6.5 → 8.0 |
| Full production readiness | 4.0 → 6.0 |
| Overall product judgment | 4.5 → 7.0 |

## Detailed customer ratings

| Category | Customer /10 | Remaining deduction |
|---|---:|---|
| Spacing, alignment and density | 7.5 | Consistent dialog insets, scroll regions and flat Gate/file sections. Some legacy workspace density persists. |
| Typography and readability | 7.5 | Provisioning/action dialogs now use the application typeface; technical instructions remain text-heavy. |
| Brand and theme presentation | 7.5 | Canonical TROA helm/favicon and ecosystem shell retained, not redrawn. Deep workflows were not individually reviewed in every palette. |
| Component consistency | 7.0 | Shared modal boundary and flatter sections; historical form/disclosure implementations remain heterogeneous. |
| Navigation and information architecture | 7.0 | Explicit Gate task selection owns the URL. Experimental planning moved away from normal operations. Broad terminology still needs operator familiarity. |
| Dialogs and focus/background boundaries | 8.2 | Portals above chrome, inert background, shared scroll lock and restored background state; real assistive-tech acceptance still pending. |
| Responsive interaction | 7.5 | Actual Torch review and modal hit targets verified at 1440, 1045 and 390 pixels. Physical devices/zoom/browser matrix remain open. |
| Accessibility confidence | 7.3 | Existing A/AA matrix plus actual Torch and file states checked; automated passes do not resolve incomplete criteria or certify WCAG. |
| First-run and role clarity | 5.5 | Controller/Instance/Hybrid/Host distinctions are preserved and update scopes clearer; still too much system vocabulary for a new operator. |
| Server creation and placement | 7.5 | Above-chrome review, explicit draft discard, guarded Gate exit, collapsed optional planning and preserved uncertain jobs. Real game creation still unaccepted. |
| Everyday fleet/server operations | 7.0 | Existing freshness and action safeguards preserved; large inventories and sustained live console not freshly proven. |
| Job feedback and interruption recovery | 7.5 | Uncertain creation remains visible and links to Activity; read/upload selection state is safer. Actual interrupted targets remain manual acceptance. |
| File and content workflows | 7.0 | Selected path and verified digest flow into replacement; stale digest/file/authorization clear together. Advanced digest and policy concepts remain visible. |
| Backup and recovery experience | 6.5 | Server Backups leads to verified restore on the same server page; read-only plan and actual restore are distinguished. Real destination/restore acceptance remains. |
| Scheduling and automation | 7.5 | Existing plans editable with duration units, renewed authorization and stale-plan rejection. No actual timed/provider action was enabled. |
| Gate world-management product | 5.5 | Stable task routing and less visual clutter; central live activation/travel/recovery execution still unavailable. Reclassification is not feature completion. |
| People, permissions and account security UX | 7.5 | Permission notice no longer overlaps scroll content; real DB MFA recovery safeguards pass. No real account/role was modified. |
| Master licensing/installation administration | N/A | Excluded from customer builds. |
| Install/update/distribution experience | 6.5 | Runtime admission now enforces the actual patched floor, signed/preservation tooling retained. No new signed candidate bundle or target upgrade was performed. |
| Documentation and release clarity | 7.5 | Host guide matches existing immutable Test43 and explains independent update scopes. New runtime remains explicitly unpublished. |
| Maintainability and change safety | 6.0 | Actual schedule routes extracted for DB tests; large App/Gate components and layered CSS remain meaningful debt. |
| Regression and acceptance confidence | 7.0 | New assertions target previously missed branch, layering, draft and state failures. Finite fixtures still cannot establish every real-target behavior. |

## Implemented candidate corrections

Dialogs use application-level portals above the shell, with inert background/focus and scroll boundaries. Provisioning requires an explicit keep/discard decision, including the previously unguarded Open Gate exit. Actual Torch-only optional planning is collapsed; decorative steps and a cramped phone badge are removed, and service checkboxes use aligned flat rows. TROA identity provenance, existing themes and confirmation/security boundaries are retained.

Gate tasks keep their selected destination/URL instead of changing during scrolling; visible task sections and prerequisites replace one giant scrolling page. Experimental planning is separate from normal operations. Live activation, cross-world gameplay and isolated recovery execution remain unavailable, with locks preserved. This is a product limitation, not a feature declared complete by relabeling it.

Existing schedules can be edited using human duration units and renewed authorization. Server routes enforce current permissions, capabilities and a locked revision comparison; stale competing edits cannot silently overwrite the winning plan. Prior job/requester evidence is retained.

Selecting a file carries its relative path into replacement. A verified read fills the current digest; changing selection clears stale digest, chosen file and visible file input, preview/progress and authorization. File-only guidance and paging fit the task. Server Backups connects to the same server's verified restore flow; a read-only plan is explicitly separate from an executed restore. Existing integrity/rollback safeguards remain.

The candidate Host installer pins official Node 24.22.3 and its archive checksum; the actual admission predicate rejects 24.22.0/1/2. Controller images use digest-pinned Node 24.22.3. New password hashes use scrypt N32768/r8/p3; valid older hashes remain usable and upgrade after successful authentication/MFA, with concurrent-account-change protection. No password reset or identity/MFA/enrollment mutation is performed by preparing these source changes.

The Host guide now references the existing immutable Test43 rather than Test38 and explains the separate Controller, Host Agent, Host runtime and game update boundaries. A newer patched signed bundle is still required before customers can receive the candidate. Do not mix mutable repo scripts into an older signed release or claim a panel update patches every Host/game.

## Verification and limits

- Workspace types/build pass; customer UI compiled separately. The final focused browser suite has 27 interactions, including actual Torch recipe states at 1440/1045/390, geometry, draft exits, uncertain jobs, schedules, read-only permissions and stale file replacement.
- Customer navigation/search/draft matrix: 118 cases; interface workflows: eight; cold sign-in and actual periodic authenticated-session-expiry journeys. Browser operation responses are synthetic and never reach a real Controller, Host or external provider.
- Customer accessibility: 73 existing A/AA states plus six actual-Torch/file states; zero automated violations required. Incomplete rules and screen-reader/device/browser acceptance remain manual.
- Shared application Node suite: 339 pass, five environment-gated skips out of 344. Three real PostgreSQL cases and two actual rootless generic provisioning cases pass separately, with component-input continuity recorded. These do not establish vendor-game execution.
- Public installer: 146 non-root Python plus three isolated-root cases =149 unique passes; 67 Node cases pass; Bash/bootstrap consistency and checksummed historical Host upgrade fixtures pass.
- Production npm advisories: zero. Actual customer Controller image: Node 24.22.3, four dependency/security smokes, compiled/source/issuer isolation and fresh LOW-through-CRITICAL vulnerability/secret scan with zero findings. Image inputs are unchanged from the scanned build. This is not a penetration test or a fresh scan of every database/web/Windows artifact.
- Selected desktop/phone expanded/error/read-only captures are visually reviewed. The final visual process caught defects that automated accessibility did not. Not every capture or deep workflow/theme combination is individually human-reviewed.

Backend/installer suites passed on the frozen application logic before subsequent Torch presentation/browser-assertion corrections. Final types/build and both compiled browser suites validate those presentation changes; source-input comparisons preserve the distinction between fresh and inherited evidence. Final evidence is retained in the owner's workspace, with failed and superseded attempts preserved.

Gate's visible scroll burden is much smaller, but substantial editor state remains mounted. Large frontend components and approximately 0.6 MB raw CSS remain maintainability/performance debt. Loopback fixture resource bytes are not wire transfer sizes or production latency. No new production load/soak result is claimed.

## Release boundary

This candidate can advance to controlled owner acceptance. It does not yet earn an unrestricted stable-production recommendation. A new matched signed build, downloaded hash verification and actual installed runtime/update readback remain delivery gates. On chosen Debian/Ubuntu targets, acceptance must cover fresh setup, in-place updates, independent Host runtime, pairing/reconnect, opt-in update timer/opt-out, interruption/recovery and preserved accounts/keys/world data. Real game/player/lifecycle, mod/plugin, digest-conflict/upload, destination/restore, scheduled/provider failures, assistive technology and sustained load remain separate acceptance.

No paid service, billing change or workflow dispatch was used. Ubuntu testing is explicitly authorized and uses bounded disposable resources without production credentials or Docker socket. Owned workers, fixture containers, test images, builder/cache volume and temporary workspaces are removed as work progresses; unrelated resources and virtual-disk files are not globally pruned or compacted. No real account, game, notification, provider publication or timer was changed.

Final customer artifact: 31 JavaScript chunks, 1,281,986 raw JS bytes, 366,958 gzip bytes across all JS chunks, 613,695 raw CSS bytes; zero checked private owner UI/API markers. These are total artifact sizes, not initial network transfer. Final owned Ubuntu container/workspace/cache inventories are empty; no unrelated resource was pruned.
