import json
import runpy
from pathlib import Path
from typing import Any

import pytest

import check_link_scripts
from check_link_scripts import SCRIPT, Finding, find_link_scripts, load_records, main


def write_prefix(prefix: Path, *records: dict[str, Any]) -> None:
    meta = prefix / "conda-meta"
    meta.mkdir()
    for record in records:
        path = meta / f"{record['name']}-{record['version']}.json"
        path.write_text(json.dumps(record), encoding="utf-8")


@pytest.mark.parametrize(
    "path",
    [
        "bin/.foo-pre-link.sh",
        "bin/.foo-post-link.sh",
        "bin/.foo-pre-unlink.sh",
        "Scripts/.foo-post-link.bat",
        "Scripts\\.foo-pre-unlink.bat",
    ],
)
def test_link_script_paths_match(path: str) -> None:
    assert SCRIPT.search(path) is not None


@pytest.mark.parametrize(
    "path",
    [
        "bin/foo-post-link.sh",
        "bin/.foo-post-link.py",
        "bin/.foo-post-unlink.sh",
        "lib/.foo-post-link.sh.bak",
        "bin/python3.12",
    ],
)
def test_other_paths_do_not_match(path: str) -> None:
    assert SCRIPT.search(path) is None


def test_find_link_scripts_reports_each_script_with_its_package() -> None:
    records: list[dict[str, Any]] = [
        {"name": "a", "version": "1", "files": ["bin/a", "bin/.a-post-link.sh"]},
        {"name": "b", "version": "2"},
    ]
    assert find_link_scripts(records) == [Finding("a", "1", "bin/.a-post-link.sh")]


def test_load_records_reads_every_record_in_name_order(tmp_path: Path) -> None:
    write_prefix(tmp_path, {"name": "zlib", "version": "1"}, {"name": "abc", "version": "2"})
    assert [record["name"] for record in load_records(tmp_path)] == ["abc", "zlib"]


def test_main_passes_a_clean_environment(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    write_prefix(tmp_path, {"name": "a", "version": "1", "files": ["bin/a"]})
    assert main([str(tmp_path)]) == 0
    assert capsys.readouterr().out == "1 packages checked, 0 link scripts found\n"


def test_main_fails_on_a_script_outside_the_allowlist(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    write_prefix(tmp_path, {"name": "a", "version": "1", "files": ["bin/.a-post-link.sh"]})
    assert main([str(tmp_path)], allowed={}) == 1
    assert capsys.readouterr().out == (
        "a 1: bin/.a-post-link.sh (not allowed)\n1 packages checked, 1 link scripts found\n"
    )


def test_main_passes_a_script_on_the_allowlist(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    write_prefix(tmp_path, {"name": "a", "version": "1", "files": ["bin/.a-post-link.sh"]})
    assert main([str(tmp_path)], allowed={"a": "reason, reference, expiry"}) == 0
    assert capsys.readouterr().out == (
        "a 1: bin/.a-post-link.sh (allowed)\n1 packages checked, 1 link scripts found\n"
    )


def test_main_fails_without_package_records(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert main([str(tmp_path)]) == 1
    assert capsys.readouterr().out == f"{tmp_path}: no package records in conda-meta\n"


def test_running_as_a_script_exits_with_main_status(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    write_prefix(tmp_path, {"name": "a", "version": "1"})
    monkeypatch.setattr("sys.argv", ["check_link_scripts.py", str(tmp_path)])
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(check_link_scripts.__file__, run_name="__main__")
    assert excinfo.value.code == 0
