import argparse
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, NamedTuple

# A conda package ships link scripts as bin/.<name>-<action>.sh or
# Scripts/.<name>-<action>.bat; records list paths with either separator.
SCRIPT = re.compile(r"(^|[\\/])\.[^\\/]+-(pre-link|post-link|pre-unlink)\.(sh|bat)$")
# Package name -> reason, reference and expiry of the exception.
ALLOWED: dict[str, str] = {}


class Finding(NamedTuple):
    name: str
    version: str
    path: str


def load_records(prefix: Path) -> list[dict[str, Any]]:
    return [
        json.loads(record.read_text(encoding="utf-8"))
        for record in sorted((prefix / "conda-meta").glob("*.json"))
    ]


def find_link_scripts(records: Sequence[Mapping[str, Any]]) -> list[Finding]:
    return [
        Finding(record["name"], record["version"], path)
        for record in records
        for path in record.get("files", [])
        if SCRIPT.search(path) is not None
    ]


def main(argv: Sequence[str] | None = None, allowed: Mapping[str, str] = ALLOWED) -> int:
    parser = argparse.ArgumentParser(
        description="Report conda packages whose link scripts are not on the allowlist."
    )
    parser.add_argument("prefix", type=Path, metavar="PREFIX")
    args = parser.parse_args(argv)
    records = load_records(args.prefix)
    if not records:
        print(f"{args.prefix}: no package records in conda-meta")
        return 1
    findings = find_link_scripts(records)
    failed = False
    for finding in findings:
        if finding.name in allowed:
            verdict = "allowed"
        else:
            verdict = "not allowed"
            failed = True
        print(f"{finding.name} {finding.version}: {finding.path} ({verdict})")
    print(f"{len(records)} packages checked, {len(findings)} link scripts found")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
