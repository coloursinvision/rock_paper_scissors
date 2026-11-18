import argparse
import re
import sys
import unicodedata
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple

import check_text

MAX_SUBJECT_LENGTH = 72
SCISSORS = "# ------------------------ >8 ------------------------"
TYPE_PREFIX = re.compile(r"^[A-Za-z]+(\([^)]*\))?!?: ")
TOOL_TRAILER = (
    r"^(co-authored-by|generated-by|assisted-by|made-with|signed-off-by):"
    r".*(claude|gpt|copilot|gemini|codex|cursor|aider|anthropic|openai|devin|windsurf|jules|bot)"
)
BANNED_PATTERNS = (
    # Trailers and phrases that credit a tool.
    TOOL_TRAILER,
    r"generated with",
    r"assisted by",
    r"written by an? (ai|assistant|model)",
    # Session trailers and links.
    r"^[a-z-]*session[a-z-]*:",
    r"claude\.ai/code",
    # Narration of the drafting.
    r"\bas an ai\b",
    r"here is the updated version",
    r"i have prepared the following",
    r"\blet me\b",
    r"\bi will now\b",
    # Chat-template tokens.
    r"<\|?(im_start|im_end|endoftext|bos|eos|pad)\|?>",
    r"\[/?inst\]",
    r"<<sys>>",
    # Numbered items of a private plan of work.
    r"\b(step|phase|stage) [0-9]+\b",
)
BANNED = [re.compile(pattern, re.IGNORECASE) for pattern in BANNED_PATTERNS]


class Finding(NamedTuple):
    """A rule the message breaks; line counts from 1 in the message file."""

    line: int
    message: str


def message_lines(text: str) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    for number, raw_line in enumerate(text.split("\n"), start=1):
        # An editor on Windows may save CRLF; the carriage return is not part of the text.
        line = raw_line.removesuffix("\r")
        if line == SCISSORS:
            break
        if not line.startswith("#"):
            lines.append((number, line))
    return lines


def check_subject(number: int, subject: str) -> list[Finding]:
    findings: list[Finding] = []
    if len(subject) > MAX_SUBJECT_LENGTH:
        message = f"subject is {len(subject)} characters, at most {MAX_SUBJECT_LENGTH}"
        findings.append(Finding(number, message))
    if TYPE_PREFIX.match(subject) is not None:
        findings.append(Finding(number, "subject starts with a type prefix"))
    if not subject[:1].isupper():
        findings.append(Finding(number, "subject does not start with a capital letter"))
    if subject.endswith("."):
        findings.append(Finding(number, "subject ends with a period"))
    return findings


def check_message(text: str) -> list[Finding]:
    lines = message_lines(text)
    # git drops blank lines before the subject, so the first line with text is the subject.
    while lines and not lines[0][1].strip():
        del lines[0]
    if not lines:
        return [Finding(1, "empty subject")]
    subject_line, subject = lines[0]
    findings = check_subject(subject_line, subject)
    if len(lines) > 1 and lines[1][1].strip():
        findings.append(Finding(lines[1][0], "no blank line after the subject"))
    for number, line in lines:
        for violation in check_text.find_violations(line):
            name = unicodedata.name(chr(violation.codepoint), "<unnamed>")
            message = f"column {violation.column}: U+{violation.codepoint:04X} {name}"
            findings.append(Finding(number, message))
        for pattern in BANNED:
            match = pattern.search(line)
            if match is not None:
                findings.append(Finding(number, f"banned text: {match.group(0)!r}"))
    return findings


def check_file(path: Path) -> list[str]:
    try:
        data = path.read_bytes()
    except OSError as error:
        return [f"{path}: cannot read: {error}"]
    text = data.decode("utf-8", errors="replace")
    return [f"{path}:{finding.line}: {finding.message}" for finding in check_message(text)]


def check_log(text: str) -> list[str]:
    # git log --format='%H%x00%B%x00' writes "<sha>\0<message>\0" and a line feed per commit.
    fields = text.split("\0")
    commits = [(fields[i].strip(), fields[i + 1]) for i in range(0, len(fields) - 1, 2)]
    if not commits:
        return ["no commits on standard input"]
    return [
        f"{sha}:{finding.line}: {finding.message}"
        for sha, message in commits
        for finding in check_message(message)
    ]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Report commit message lines that break the project rules."
    )
    parser.add_argument("paths", nargs="*", type=Path, metavar="PATH")
    parser.add_argument(
        "--log",
        action="store_true",
        help="read the output of git log --format='%%H%%x00%%B%%x00' from standard input",
    )
    args = parser.parse_args(argv)
    failed = False
    for path in args.paths:
        for message in check_file(path):
            print(message)
            failed = True
    if args.log:
        for message in check_log(sys.stdin.buffer.read().decode("utf-8", errors="replace")):
            print(message)
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
