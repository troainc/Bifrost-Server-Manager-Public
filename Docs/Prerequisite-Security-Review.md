# Host prerequisite security baseline

## Authorized installation testing

The owner authorized publication for controlled installation testing on October 21. Test 35 offers the separately signed maintained baseline only after the installing operator types `USE TEST PREREQUISITES`. This supersedes the local-only restriction in the historical assessment below; it does not grant general beta/stable or independent security approval. Existing runtimes are never replaced. An incomplete existing Docker installation needs separate administrator review. Fresh preparation verifies all five signed payloads and the exact twelve tools, retains sources/notices/raw evidence, and writes new account-owned executable files before the normal rootless service setup. The signature-authenticated preparer refuses foreign origins, invalid/tampered statements, linked/writable directories and existing executable paths. No global Docker daemon is upgraded.

Independent security/source-license review, maintained patch ownership and fresh OS/systemd/resource-limit acceptance remain open. Use a disposable test VM and complete the manual acceptance checklist. A declined prompt does not download or install the baseline.

The October 21 local remediation provides a separately signed **patched prerequisite candidate**, version `v0.0.0-prerequisites.1`, for both the private master and customer distribution. It is a Bifrost-maintained security build from pinned upstream sources, not an unchanged Docker vendor release. The installed daemon, services, configurations and all retained data remain unchanged. No deployment or publication is authorized.

The original official Docker 29.9.2/Compose 5.6.1 archives remain unsuitable for automatic bootstrap: they contain the x/net advisory occurrences found in the initial audit. Missing Docker/Compose downloads therefore remain paused. The local candidate fixes those dependencies and additional eBPF/user-parser findings, retains runc seccomp/libpathrs, and backports the registry maintainer's manifest-digest verification fix. A test reproduces forged-header substitution before the backport and rejects it afterward. Independent review of this maintained build and its future update ownership is required before deployment.

Candidate components: Docker daemon 29.9.2, containerd 2.4.2, runc 1.5.2 and Compose 5.6.1, identified with `bifrost-security.1`; patched tools use Go 1.27.3, x/net 0.60.0 and eBPF 0.22.0; runc additionally uses the fixed user parser 0.4.1, seccomp 2.6.1 and libpathrs 0.2.6. Unchanged CLI/proxy/init/rootless helpers retain exact official archive bytes.

Raw vulnerability reports are preserved. Module metadata still reports the backported registry issue and an unmaintained OpenPGP subpackage warning. These are not blanket-ignored: the registry fix has an exact source hash and before/after regression; actual compiled package inventories and compiler graphs omit the deprecated OpenPGP import paths. New findings, changed binaries, incomplete or stale evidence and missing runtime results fail the local assessment. A zero-subject binary scan is never accepted. Human security approval remains separate from this mechanical evidence.

Verify a supplied local prerequisite candidate without installing it:

```sh
python3 scripts/verify-prerequisite-baseline.py /absolute/prerequisite-candidate
```

This verifies the pinned Ed25519 identity, separate prerequisite version, source revisions, all five signed payload hashes and the exact twelve-tool archive inventory. It changes no services, accounts or installation and cannot grant production approval. The main Bifrost application release has its own signature and must also be verified. Never substitute this prerequisite manifest for an application release manifest.

On the intended VM, as the existing service account, collect a small read-only inventory:

```sh
python3 scripts/collect-prerequisite-evidence.py > prerequisite-evidence.json
```

The collector reads versions, Docker binary hash and rootless security options only; it does not install tools, change services, enumerate fleet/container data, upload evidence or grant approval. Retain package/vendor identity and the independent vulnerability scan alongside it. Do not include credentials, full Docker configuration or private environment dumps in shared acceptance evidence.

Before rollout, independently review the exact OS packages/backports, rootless systemd/cgroup delegation, actual CPU/memory/process enforcement, TLS/firewall and persistent service accounts. WSL fixture startup/recovery does not qualify a fresh Debian/Ubuntu installation, production quotas, player connections or game-world restoration. Approve signer custody, licensing/source-notice obligations, this backport and patch ownership. Private master host/Coolify software needs the same approval and never gains customer fleet authority from licensing.

Primary references: [Go x/net HTTP/2 advisory](https://pkg.go.dev/vuln/GO-2026-6611), [DNS advisory](https://pkg.go.dev/vuln/GO-2026-5942), [deprecated OpenPGP package scope](https://vuln.go.dev/ID/GO-2026-5932.json), [registry maintainer advisory and fix](https://github.com/distribution/distribution/security/advisories/GHSA-685w-q87j-wqw3), [Docker vendor release notes](https://docs.docker.com/engine/release-notes/29/). Pin/hash and full local test evidence are retained with the candidate. These are point-in-time results, not approval to install whichever version is newest later.
