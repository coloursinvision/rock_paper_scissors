import runpy
from pathlib import Path

import pytest

import check_text
from check_text import Violation, check_file, find_violations, format_violation, is_allowed, main


@pytest.mark.parametrize("char", ["\t", " ", "a", "Z", "0", "~"])
def test_tab_and_printable_ascii_are_allowed(char: str) -> None:
    assert is_allowed(char)


def test_clean_text_has_no_violations() -> None:
    assert find_violations("plain ASCII\twith a tab\nand a second line\n") == []


@pytest.mark.parametrize(
    "char",
    [
        "\u00e9",
        "\u2014",
        "\u00a0",
        "\u200b",
        "\ufeff",
        "\x01",
        "\x7f",
        "\r",
        "\x0b",
        "\x0c",
        "\x85",
        "\u2028",
        "\U000e0041",
    ],
)
def test_forbidden_characters_are_reported(char: str) -> None:
    assert find_violations(f"a{char}b") == [Violation(1, 2, ord(char))]


def test_lines_and_columns_count_from_one_and_every_hit_is_reported() -> None:
    text = "ok\nx\u2014y\u2014\n"
    assert find_violations(text) == [Violation(2, 2, 0x2014), Violation(2, 4, 0x2014)]


def test_format_names_the_character() -> None:
    assert format_violation("a.txt", Violation(2, 3, 0x2014)) == "a.txt:2:3: U+2014 EM DASH"


def test_format_falls_back_for_unnamed_characters() -> None:
    assert format_violation("a.txt", Violation(1, 1, 0x0B)) == "a.txt:1:1: U+000B <unnamed>"


def test_check_file_reports_findings_with_the_path(tmp_path: Path) -> None:
    path = tmp_path / "dash.txt"
    path.write_bytes("ok\n\u2014\n".encode())
    assert check_file(path) == [f"{path}:2:1: U+2014 EM DASH"]


def test_check_file_skips_binary_files(tmp_path: Path) -> None:
    path = tmp_path / "image.bin"
    path.write_bytes(b"\x89PNG\x00\xff")
    assert check_file(path) == []


def test_check_file_reports_invalid_utf8_as_replacement_character(tmp_path: Path) -> None:
    path = tmp_path / "broken.txt"
    path.write_bytes(b"a\xffb\n")
    assert check_file(path) == [f"{path}:1:2: U+FFFD REPLACEMENT CHARACTER"]


def test_check_file_reports_an_unreadable_path(tmp_path: Path) -> None:
    path = tmp_path / "missing.txt"
    messages = check_file(path)
    assert len(messages) == 1
    assert messages[0].startswith(f"{path}: cannot read: ")


def test_main_returns_zero_and_prints_nothing_for_clean_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "clean.txt"
    path.write_bytes(b"plain ASCII\n")
    assert main([str(path)]) == 0
    assert capsys.readouterr().out == ""


def test_main_returns_one_and_prints_each_finding(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "dash.txt"
    path.write_bytes("\u2014\n".encode())
    assert main([str(path)]) == 1
    assert capsys.readouterr().out == f"{path}:1:1: U+2014 EM DASH\n"


def test_main_without_paths_returns_zero() -> None:
    assert main([]) == 0


def test_running_as_a_script_exits_with_main_status(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["check_text.py"])
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(check_text.__file__, run_name="__main__")
    assert excinfo.value.code == 0
