import argparse
import unicodedata
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple


class Violation(NamedTuple):
    """A forbidden character; line and column count from 1."""

    line: int
    column: int
    codepoint: int


def is_allowed(char: str) -> bool:
    codepoint = ord(char)
    return codepoint == 0x09 or 0x20 <= codepoint <= 0x7E


def find_violations(text: str) -> list[Violation]:
    violations: list[Violation] = []
    # Split on LF only: str.splitlines() also breaks at VT, FF, NEL and the
    # Unicode line separators, which this check must report, not skip.
    for line_number, line in enumerate(text.split("\n"), start=1):
        for column, char in enumerate(line, start=1):
            if not is_allowed(char):
                violations.append(Violation(line_number, column, ord(char)))
    return violations


def format_violation(path: str, violation: Violation) -> str:
    char = chr(violation.codepoint)
    name = unicodedata.name(char, "<unnamed>")
    return f"{path}:{violation.line}:{violation.column}: U+{violation.codepoint:04X} {name}"


def check_file(path: Path) -> list[str]:
    try:
        data = path.read_bytes()
    except OSError as error:
        return [f"{path}: cannot read: {error}"]
    # A NUL byte marks a binary file, the same test git uses.
    if b"\0" in data:
        return []
    text = data.decode("utf-8", errors="replace")
    return [format_violation(str(path), violation) for violation in find_violations(text)]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report characters outside tab, line feed and printable ASCII."
    )
    parser.add_argument("paths", nargs="*", type=Path, metavar="PATH")
    args = parser.parse_args(argv)
    failed = False
    for path in args.paths:
        for message in check_file(path):
            print(message)
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
