import argparse
import re
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple

DOCKERFILE = Path(".devcontainer/Dockerfile")
WORKFLOW = Path(".github/workflows/ci.yml")
DOCKERFILE_VERSION = re.compile(r"ARG MINIFORGE_VERSION=(\S+)")
WORKFLOW_VERSION = re.compile(r"\s*miniforge-version:\s*(\S+)")


class Version(NamedTuple):
    """A Miniforge version and the line that sets it; lines count from 1."""

    path: Path
    line: int
    value: str


def find_versions(path: Path, pattern: re.Pattern[str]) -> list[Version]:
    versions: list[Version] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        match = pattern.fullmatch(line)
        if match is not None:
            versions.append(Version(path, number, match.group(1)))
    return versions


def check(dockerfile: Path, workflow: Path) -> list[str]:
    try:
        found = find_versions(dockerfile, DOCKERFILE_VERSION)
        used = find_versions(workflow, WORKFLOW_VERSION)
    except OSError as error:
        return [f"cannot read: {error}"]
    if len(found) != 1:
        return [f"{dockerfile}: expected one ARG MINIFORGE_VERSION line, found {len(found)}"]
    if not used:
        return [f"{workflow}: no miniforge-version line"]
    expected = found[0]
    return [
        f"{version.path}:{version.line}: miniforge-version {version.value} differs from "
        f"{expected.value} in {expected.path}:{expected.line}"
        for version in used
        if version.value != expected.value
    ]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report a Miniforge version in CI that differs from the dev container."
    )
    parser.add_argument("--dockerfile", type=Path, default=DOCKERFILE)
    parser.add_argument("--workflow", type=Path, default=WORKFLOW)
    args = parser.parse_args(argv)
    errors = check(args.dockerfile, args.workflow)
    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
