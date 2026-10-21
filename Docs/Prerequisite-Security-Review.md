# Host prerequisite security review

October 21 local review found high-severity advisories in compiled host tools, beyond the previously clean Bifrost runtime image scans. The older Docker 29.8.2 stack had numerous findings. The current official Docker 29.9.2 plus Compose 5.6.1 archives still produced six HIGH/CRITICAL package occurrences across five binaries, covering two distinct x/net advisories (CVE-2026-78669 and CVE-2026-46600). Counts are package occurrences, not six distinct vulnerabilities or proof of reachability. A filesystem source scan returned no analyzed binary results; the root-filesystem compiled-binary scan detected the dependencies. Zero analyzed results must never be called a clean binary scan.

The installer no longer downloads Docker or Compose automatically when missing. It stops with a clear prerequisite message. It does not replace, update, stop or uninstall an existing runtime. A VM administrator must provision an independently reviewed patched rootless Docker/Compose build for the panel account and reviewed rootless Podman/game prerequisites for the game account before acceptance. Presence/version alone is not security approval. A security reviewer must assess the exact installed build, vendor backports, advisory applicability and any explicitly accepted residual risk. No findings are ignored or approved by this task.

Official sources: [Docker static archive index](https://download.docker.com/linux/static/stable/x86_64/), [Docker Engine release notes](https://docs.docker.com/engine/release-notes/29/), [Compose release metadata](https://api.github.com/repos/docker/compose/releases/latest). Frozen archive hashes/scan evidence are retained in the private local audit evidence. These are point-in-time observations, not an instruction to install whichever version is newest later.

On the intended VM, as the existing service account, collect a small read-only inventory:

```sh
python3 scripts/collect-prerequisite-evidence.py > prerequisite-evidence.json
```

The collector reads versions, Docker binary hash and rootless security options only; it does not install tools, change services, enumerate fleet/container data, upload evidence or grant approval. Retain package/vendor identity and the independent vulnerability scan alongside it. Do not include credentials, full Docker configuration or private environment dumps in shared acceptance evidence.

Before beta, the reviewer must explicitly approve the host prerequisite baseline. Until then automatic prerequisite bootstrap remains blocked even though Bifrost's own image scans pass. Private masters also rely on an operator-managed host/Coolify/container stack and need this review; they must never inherit customer fleet authority or share customer game-service accounts.
