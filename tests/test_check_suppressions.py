import io
import runpy

import pytest

import check_suppressions
from check_suppressions import CONFIGURATION_CHANGED, Finding, check_diff, check_line, main

DIFF = (
    "diff --git a/src/x.py b/src/x.py\n"
    "index 1111111..2222222 100644\n"
    "--- a/src/x.py\n"
    "+++ b/src/x.py\n"
    "@@ -10,2 +10,3 @@ def f():\n"
    " a = 1\n"
    "-b = 2\n"
    "+b = 3  # noqa: E501\n"
    "+c = 4\n"
    "diff --git a/pyproject.toml b/pyproject.toml\n"
    "--- a/pyproject.toml\n"
    "+++ b/pyproject.toml\n"
    "@@ -5 +5 @@\n"
    "-fail_under = 100\n"
    "+fail_under = 90\n"
)


@pytest.mark.parametrize(
    ("text", "match"),
    [
        ("x = 1  # noqa: E501", "noqa"),
        ("y = f()  # type: ignore[no-any-return]", "type: ignore"),
        ("y = f()  # type:ignore", "type:ignore"),
        ("if x:  # pragma: no cover", "pragma: no cover"),
    ],
)
def test_a_suppression_is_reported(text: str, match: str) -> None:
    assert check_line("src/x.py", 7, text) == [Finding("src/x.py", 7, f"new suppression: {match}")]


@pytest.mark.parametrize(
    ("text", "match"),
    [
        ("@pytest.mark.skip(reason='slow')", "mark.skip"),
        ("@pytest.mark.skipif(sys.platform == 'win32', reason='x')", "mark.skip"),
        ("@pytest.mark.xfail(strict=True)", "mark.xfail"),
        ("pytest.skip('not here')", ".skip("),
        ("pytest.xfail('known')", ".xfail("),
        ("yaml = pytest.importorskip('yaml')", "importorskip"),
    ],
)
def test_a_skip_is_reported(text: str, match: str) -> None:
    assert check_line("tests/test_x.py", 3, text) == [
        Finding("tests/test_x.py", 3, f"new skip: {match}")
    ]


def test_a_line_with_both_kinds_gives_two_findings() -> None:
    assert check_line("tests/test_x.py", 1, "pytest.skip()  # noqa: B018") == [
        Finding("tests/test_x.py", 1, "new suppression: noqa"),
        Finding("tests/test_x.py", 1, "new skip: .skip("),
    ]


def test_an_ordinary_line_gives_no_findings() -> None:
    assert check_line("src/x.py", 1, "def skip_turn() -> None:") == []


@pytest.mark.parametrize("path", ["", "scripts/check_suppressions.py"])
def test_a_line_without_a_path_or_in_an_excluded_file_is_skipped(path: str) -> None:
    assert check_line(path, 1, "x = 1  # noqa: E501") == []


def test_a_diff_reports_lines_of_the_new_file_and_configuration_changes() -> None:
    assert check_diff(DIFF) == [
        Finding("src/x.py", 11, "new suppression: noqa"),
        Finding("pyproject.toml", 1, CONFIGURATION_CHANGED),
    ]


@pytest.mark.parametrize(
    "path",
    [".pre-commit-config.yaml", ".github/workflows/ci.yml", "pyproject.toml", ".coveragerc"],
)
def test_configuration_files_are_reported(path: str) -> None:
    findings = check_diff(f"+++ b/{path}\n")
    assert findings == [Finding(path, 1, CONFIGURATION_CHANGED)]


def test_a_deleted_file_has_no_path() -> None:
    assert check_diff("--- a/src/x.py\n+++ /dev/null\n@@ -1 +0,0 @@\n-x = 1  # noqa\n") == []


def test_main_prints_annotations_and_always_returns_zero(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr("sys.stdin", io.TextIOWrapper(io.BytesIO(DIFF.encode())))
    assert main([]) == 0
    assert capsys.readouterr().out == (
        "::warning file=src/x.py,line=11::new suppression: noqa\n"
        f"::warning file=pyproject.toml,line=1::{CONFIGURATION_CHANGED}\n"
    )


def test_running_as_a_script_exits_with_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("sys.argv", ["check_suppressions.py"])
    monkeypatch.setattr("sys.stdin", io.TextIOWrapper(io.BytesIO(b"")))
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(check_suppressions.__file__, run_name="__main__")
    assert excinfo.value.code == 0
