import argparse
import re
import sys
from collections.abc import Sequence
from typing import NamedTuple

SUPPRESSION = re.compile(
    r"eslint-disable|ts-ignore|ts-expect-error|noqa|type: ?ignore|nolint"
    r"|#\[(allow|expect)\(|pragma: no cover|SuppressWarnings"
)
SKIP = re.compile(
    r"\.only\(|\.skip\(|\bxit\(|\bxdescribe\(|mark\.skip|mark\.xfail|\.xfail\("
    r"|importorskip|t\.Skip\(|@Ignore|@Disabled"
)
CONFIGURATION = re.compile(
    r"coverage|ruff|mypy|(^|/)pyproject\.toml$|^\.pre-commit-config\.yaml$|^\.github/workflows/"
)
CONFIGURATION_CHANGED = "configuration changed: check thresholds, excludes and ignores"
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")
# These files hold the patterns above as data, so every change to them would match.
EXCLUDED = frozenset({"scripts/check_suppressions.py", "tests/test_check_suppressions.py"})


class Finding(NamedTuple):
    """A change a reviewer should read; line counts from 1 in the new file."""

    path: str
    line: int
    message: str


def check_line(path: str, number: int, text: str) -> list[Finding]:
    if not path or path in EXCLUDED:
        return []
    findings: list[Finding] = []
    for kind, pattern in (("suppression", SUPPRESSION), ("skip", SKIP)):
        match = pattern.search(text)
        if match is not None:
            findings.append(Finding(path, number, f"new {kind}: {match.group(0)}"))
    return findings


def check_diff(diff: str) -> list[Finding]:
    findings: list[Finding] = []
    path = ""
    number = 0
    for line in diff.split("\n"):
        if line.startswith("+++ "):
            path = line.removeprefix("+++ b/") if line.startswith("+++ b/") else ""
            if path and path not in EXCLUDED and CONFIGURATION.search(path):
                findings.append(Finding(path, 1, CONFIGURATION_CHANGED))
            continue
        hunk = HUNK.match(line)
        if hunk is not None:
            number = int(hunk.group(1))
        elif line.startswith("+"):
            findings.extend(check_line(path, number, line[1:]))
            number += 1
        elif line.startswith(" "):
            number += 1
    return findings


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Warn about suppressions, skips and configuration changes in a diff."
    )
    parser.parse_args(argv)
    diff = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    for finding in check_diff(diff):
        print(f"::warning file={finding.path},line={finding.line}::{finding.message}")
    # The check only warns: a reviewer reads each finding, so the step never fails.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
