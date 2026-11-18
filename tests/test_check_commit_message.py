import runpy
from pathlib import Path

import pytest

import check_commit_message
from check_commit_message import (
    SCISSORS,
    Finding,
    check_file,
    check_message,
    check_subject,
    main,
    message_lines,
)


def test_comments_and_everything_after_the_scissors_line_are_dropped() -> None:
    text = f"Add x\n# comment\n\nWhy.\n{SCISSORS}\ndiff \u00e9\n"
    assert message_lines(text) == [(1, "Add x"), (3, ""), (4, "Why.")]


def test_a_carriage_return_before_a_line_feed_is_dropped() -> None:
    assert message_lines("Add x\r\n\r\nWhy.\r\n") == [(1, "Add x"), (2, ""), (3, "Why."), (4, "")]


def test_a_good_subject_has_no_findings() -> None:
    assert check_subject(1, "Add a check of commit messages") == []


def test_a_subject_of_72_characters_passes_and_73_fails() -> None:
    assert check_subject(1, "A" * 72) == []
    assert check_subject(1, "A" * 73) == [Finding(1, "subject is 73 characters, at most 72")]


@pytest.mark.parametrize("subject", ["Feat: add x", "Fix(ci)!: add x", "Docs(readme): add x"])
def test_a_type_prefix_is_reported(subject: str) -> None:
    assert check_subject(1, subject) == [Finding(1, "subject starts with a type prefix")]


def test_a_lowercase_start_is_reported() -> None:
    findings = check_subject(1, "add x")
    assert findings == [Finding(1, "subject does not start with a capital letter")]


def test_a_final_period_is_reported() -> None:
    assert check_subject(1, "Add x.") == [Finding(1, "subject ends with a period")]


def test_a_message_with_subject_and_body_has_no_findings() -> None:
    assert check_message("Add x\n\nThe body says why.\n") == []


def test_blank_lines_before_the_subject_are_skipped() -> None:
    assert check_message("\n  \nAdd x\n") == []


def test_reported_line_numbers_count_lines_of_the_file() -> None:
    findings = check_message("\n\nadd x\n")
    assert findings == [Finding(3, "subject does not start with a capital letter")]


@pytest.mark.parametrize("text", ["", "\n\n", "# only a comment\n"])
def test_a_message_without_text_has_an_empty_subject(text: str) -> None:
    assert check_message(text) == [Finding(1, "empty subject")]


def test_a_missing_blank_line_after_the_subject_is_reported() -> None:
    assert check_message("Add x\nWhy.\n") == [Finding(2, "no blank line after the subject")]


def test_characters_outside_ascii_are_reported_with_line_and_column() -> None:
    findings = check_message("Add x\n\nCaf\u00e9 \u2014 done\na\x0bb\n")
    assert findings == [
        Finding(3, "column 4: U+00E9 LATIN SMALL LETTER E WITH ACUTE"),
        Finding(3, "column 6: U+2014 EM DASH"),
        Finding(4, "column 2: U+000B <unnamed>"),
    ]


@pytest.mark.parametrize(
    ("line", "banned"),
    [
        ("Co-authored-by: Claude <x@example.com>", "Co-authored-by: Claude"),
        ("Generated with a tool", "Generated with"),
        ("Assisted by a tool", "Assisted by"),
        ("Written by an assistant", "Written by an assistant"),
        ("Claude-Session: abc", "Claude-Session:"),
        ("See https://claude.ai/code/abc", "claude.ai/code"),
        ("As an AI, I add x", "As an AI"),
        ("Here is the updated version", "Here is the updated version"),
        ("I have prepared the following", "I have prepared the following"),
        ("Let me add x", "Let me"),
        ("I will now add x", "I will now"),
        ("<|im_start|>user", "<|im_start|>"),
        ("[INST] add x [/INST]", "[INST]"),
        ("<<SYS>> add x", "<<SYS>>"),
        ("Finish step 10 of the plan", "step 10"),
    ],
)
def test_banned_text_is_reported(line: str, banned: str) -> None:
    assert check_message(f"Add x\n\n{line}\n") == [Finding(3, f"banned text: {banned!r}")]


@pytest.mark.parametrize(
    "line",
    ["Let methods return", "Add a CI step", "Co-authored-by: Ann Smith <a@example.com>"],
)
def test_ordinary_text_is_not_banned(line: str) -> None:
    assert check_message(f"Add x\n\n{line}\n") == []


def test_check_file_reports_findings_with_the_path(tmp_path: Path) -> None:
    path = tmp_path / "COMMIT_EDITMSG"
    path.write_bytes(b"Add x.\n")
    assert check_file(path) == [f"{path}:1: subject ends with a period"]


def test_check_file_reports_invalid_utf8_as_replacement_character(tmp_path: Path) -> None:
    path = tmp_path / "COMMIT_EDITMSG"
    path.write_bytes(b"Add x\xff\n")
    assert check_file(path) == [f"{path}:1: column 6: U+FFFD REPLACEMENT CHARACTER"]


def test_check_file_keeps_a_lone_carriage_return(tmp_path: Path) -> None:
    path = tmp_path / "COMMIT_EDITMSG"
    path.write_bytes(b"Add\rx\n")
    assert check_file(path) == [f"{path}:1: column 4: U+000D <unnamed>"]


def test_check_file_reports_an_unreadable_path(tmp_path: Path) -> None:
    path = tmp_path / "missing"
    messages = check_file(path)
    assert len(messages) == 1
    assert messages[0].startswith(f"{path}: cannot read: ")


def test_main_returns_zero_and_prints_nothing_for_a_good_message(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "COMMIT_EDITMSG"
    path.write_bytes(b"Add x\n\nWhy.\n")
    assert main([str(path)]) == 0
    assert capsys.readouterr().out == ""


def test_main_returns_one_and_prints_each_finding(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "COMMIT_EDITMSG"
    path.write_bytes(b"add x.\n")
    assert main([str(path)]) == 1
    assert capsys.readouterr().out == (
        f"{path}:1: subject does not start with a capital letter\n"
        f"{path}:1: subject ends with a period\n"
    )


def test_main_without_paths_returns_zero() -> None:
    assert main([]) == 0


def test_running_as_a_script_exits_with_main_status(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["check_commit_message.py"])
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(check_commit_message.__file__, run_name="__main__")
    assert excinfo.value.code == 0
