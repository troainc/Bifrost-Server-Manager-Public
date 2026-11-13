> Current verified continuation: [Test 41 interface review and rerating](Interface-Production-Review-2026-11-13.md). Historical candidate-only statements below apply to their stated earlier revisions.

# Customer interface — comprehensive audit

> Current continuation: [customer navigation/search revision](Interface-Flow-Redesign-2026-11-13.md). The owner rejected 6.9/10; the newer shared-source candidate is unrendered and untested. Historical category scores below do not apply to it.

The earlier 7.9/10 UI rating is withdrawn. This review records a 4.4/10 shared/source baseline and a conservative **6.9/10 for the last fully checked customer revision**, e79c3d394d180bac43cedc2838e59d19099ad6f2. Newer source corrections are not covered by that score. Published Test 40 is unchanged; this documentation is not a new application release.

## Evidence and limits

The shared application is compiled separately for customer and master. The customer excludes owner/issuer capabilities and private application source. No private implementation or credentials are included here.

All six application workflows passed on the checked revision. The customer interface passed 150 operational layout checks, 276 deep capture/geometry/text combinations, six isolated synthetic workflows and 69 automated WCAG A/AA states with zero reported violations. Capture widths are 1440, 1045, 768 and 390px; all six themes cover defined route subsets. Incomplete accessibility criteria still require manual review. Captured screenshots are not automatically counted as visually reviewed, and these figures do not establish real customer/game acceptance.

Visual review included customer independent/paired and viewer states, inactive license/disclosure update, core fleet/workspace composition, and the separately compiled phone backup records, requested-inventory workspace and General settings. Shared source and master review informed the other shared features. The synthetic event stream is unavailable, so a Connecting/periodic-refresh indicator in an evidence image does not describe production connectivity.

The six isolated workflows cover rejected General saves and validation, schedule timing and authorization, pinned uncertain jobs, default reviewed catalog/creation entry, account-scoped backup drafts and explicit inventory reads. Browser interceptions supplied all simulated writes; no real Controller, Host, game, provider, mail, credential or consent change occurred.

## Category ratings

These are design judgments for the checked revision, not a passing-test percentage.

| Category | Baseline / 10 | Checked revision / 10 | Remaining limit |
| --- | ---: | ---: | --- |
| Information architecture | 4 | 7 | Optional Gate remains a long planning workspace |
| Workflow priority | 4 | 7 | Saved inventories and working tools first; pre-login coverage was incomplete |
| Spacing and responsive composition | 3 | 6.5 | Final audit pagination, branding/email insets and narrow URL corrections need rendered proof |
| Typography and readability | 4 | 7.5 | Readable measured text; technical operations still require care |
| Hierarchy and restraint | 3 | 6.5 | Most nested surfaces removed; residual administration density remains |
| Navigation and orientation | 5 | 6.5 | Stable account/navigation controls; numerous Settings/server/Gate sections remain demanding |
| Forms, validation and feedback | 5 | 7 | Synthetic rejection/authorization paths covered; real authentication/provider states remain manual |
| Status accuracy and trust | 4 | 7.5 | False protection/readiness claims corrected; latest metadata/retention wording is unverified |
| Accessibility and keyboard | 6 | 7 | Automated sampled states pass; incomplete criteria and assistive technology pending |
| Empty, failed, stale and recovery states | 6 | 7 | Populated/failure/uncertain coverage improved; real interruption/recovery still pending |
| Cross-feature consistency | 3 | 6.5 | Shared explicit cascade improves consistency; final feature corrections need proof |
| **Overall design rating** | **4.4 provisional** | **6.9** | Not full production acceptance |

## Improvements prepared

The shared candidate establishes explicit legacy/interface CSS layers, readable typography and consistent controls; puts inventories before setup; uses compact fleet rows and flat backup records; prioritizes reviewed game recipes and working integrations; makes schedules/alerts readable; keeps uncertainty visible despite filters; scopes browser drafts per account; and simplifies settings, profile, documentation and Gate planning. Automatic audit context remains with no user-entered reason prompts. Permissions, confirmations, keys, recovery and customer/owner separation remain.

Latest executable source candidate: 4a2045a91aab419216325aae9473cfdbd92dd29f. Further corrections cover sign-in/MFA/recovery, secondary inventory filters/reset, remaining branding/settings surfaces, audit pagination/summary density, email insets, deployment URL wrapping and precise backup/HTTPS wording. Additional backup/tool disclosure captures are prepared. **These newer changes have not been rendered or tested; no higher final rating is assigned.**

GitHub refused every job in the intervening revision before runner startup because of account payment/spending-limit status. The owner explicitly prohibits anything requiring billing or payment, plus all PC application/test/build/browser/container/WSL workloads. No billing change, payment, paid runner/service or local testing fallback was used. Preservation commits skip CI/CD; skipped checks are not passing evidence. Final verification needs authorized available capacity within those constraints, followed by owner manual acceptance.

## Retained evidence and release boundary

[Evidence index and source provenance](UI-Review-20261113/evidence.json) contains selected synthetic screenshots from the passing revision. They are development fixtures, not a published installer or a real customer installation.

This public branch changes documentation and static review evidence only. No private application/issuer source, installer/updater changes, new release assets, website command changes, installed update, account/MFA/secret/enrollment changes, Host/Agent/game action or automatic-update timer activation. Immutable Test 40 and every older release/data/recovery path remain retained.

No unrestricted production sign-off is claimed. Final automated and rendered verification, actual Debian/Ubuntu/update-interruption/recovery/game/player and assistive-technology acceptance remain outstanding.

Draft customer audit record: [PR27](https://github.com/troainc/Bifrost-Server-Manager-Public/pull/27).
