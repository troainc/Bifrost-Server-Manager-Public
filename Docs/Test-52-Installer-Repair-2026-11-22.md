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

Application behavior and SE2's private-asset requirements remain as documented
for Test 51. The unchanged compiled Controller/database are reused under matched
Test 52 image tags; the web installer/version pins and Host package version
metadata are updated. Their continuity and focused fresh installer checks are
recorded separately from Test 51's inherited application/game acceptance.
