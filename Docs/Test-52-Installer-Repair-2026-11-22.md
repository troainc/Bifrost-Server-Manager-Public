# Test 52: automatic Host checksum repair

Test 51 could start its panel successfully, verify its Host archive signature,
then stop with `sha256sum: standard input: no properly formatted checksum lines
found`. Its release checksum inventory contained Windows CRLF line endings.
The automatic Host path's anchored text filter failed to select that record.
The earlier generic checksum test accepted CRLF and did not exercise this path.

Test 52 uses an exact byte reader for this check. It accepts LF/CRLF, requires
one exact Host filename/hash record, rejects duplicates/malformed/wrong digests,
and retains the preceding signed-release verification. Release generation now
writes canonical LF bytes with a tested shared helper and refuses to rewrite
an already signed inventory. Prior Test 51 assets remain immutable.

An interrupted Test 51 Instance can run the separately pinned compatibility
installer with `--resume-local-host`. This resumes its unprivileged local Host
preparation and preserves the already healthy panel. Do not wipe or rerun a
fresh panel install to repair this failure. Existing enrolled Hosts require
their explicit upgrade/recovery path.

For the healthy Test 51 panel that stopped at this checksum error, run this
as the Debian administrator. The compatibility source remains pinned to Test 51
and verifies its original immutable signed Host package. Enter the root password
when `su` asks; this command does not reinstall the panel.

```sh
su -s /bin/bash -c '
set -eu
export PATH=/usr/sbin:/usr/bin:/sbin:/bin
stage=$(mktemp -d /tmp/bifrost-host-repair.XXXXXX)
chmod 0755 "$stage"
curl --proto "=https" --proto-redir "=https" -fL --retry 3 \
  https://raw.githubusercontent.com/troainc/Bifrost-Server-Manager-Public/9717e24be40eda17120d0a3de9fd13fa966edb25/install.sh \
  -o "$stage/install.sh"
printf "%s\n" "23bb46dae8dea7426ca901f2db49151011d8cefe038e97380f785c3227917f21  $stage/install.sh" | sha256sum -c -
bash "$stage/install.sh" --resume-local-host
' root
```

Fresh Debian/Ubuntu installs should use the matched Test 52 commands from
the main Bifrost page. The recovery above intentionally retains the existing
Test 51 panel. Successful local signature/checksum/extraction tests do not
establish completion of the owner's real Host setup.

Application behavior and SE2's private-asset requirements remain as documented
for Test 51. The unchanged compiled Controller/database are reused under matched
Test 52 image tags; the web installer/version pins and Host package version
metadata are updated. Their continuity and focused fresh installer checks are
recorded separately from Test 51's inherited application/game acceptance.

## Publication and live readback

Test 52 release454450348 is published with 25 anonymously downloaded assets;
all hashes, offline signatures and actual signed Host-stage checks pass.
Public PR39 merged as 33c1078; private PR105/master163fa31 native deployment
n99ofg3j6uyp3xz2269micz5 and Main PR143/master6b3091b deployment
eaq19l763ra5t3f4ponbq0d4 finished. All four live Debian/Ubuntu install/update
commands pin the exact Test 52 installer digest, with password/no-store checks.
The public page renders Test 52. Six private-master services are healthy and
both master/site environment fingerprints and persistent mounts are preserved.
No reset or install was executed on the owner's target by this repair session.
Fresh checks and unchanged/inherited application evidence are distinguished in
release-evidence.json. These closure notes do not replace immutable signed assets.
