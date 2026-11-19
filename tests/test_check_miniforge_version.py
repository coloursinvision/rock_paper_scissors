import runpy
from pathlib import Path

import pytest

import check_miniforge_version
from check_miniforge_version import (
    DOCKERFILE_VERSION,
    WORKFLOW_VERSION,
    Version,
    check,
    find_versions,
    main,
)

DOCKERFILE = "FROM base\n\nARG MINIFORGE_VERSION=26.9.4-2\nARG MINIFORGE_SHA256=abc\n"
WORKFLOW = (
    "jobs:\n"
    "  test:\n"
    "    steps:\n"
    "      - uses: conda-incubator/setup-miniconda@abc\n"
    "        with:\n"
    "          miniforge-version: 26.9.4-2\n"
    "  hygiene:\n"
    "    steps:\n"
    "      - uses: conda-incubator/setup-miniconda@abc\n"
    "        with:\n"
    "          miniforge-version: 26.9.4-2\n"
)


def write(tmp_path: Path, dockerfile: str, workflow: str) -> tuple[Path, Path]:
    dockerfile_path = tmp_path / "Dockerfile"
    workflow_path = tmp_path / "ci.yml"
    dockerfile_path.write_text(dockerfile, encoding="utf-8")
    workflow_path.write_text(workflow, encoding="utf-8")
    return dockerfile_path, workflow_path


def test_find_versions_returns_each_matching_line_with_its_number(tmp_path: Path) -> None:
    dockerfile, workflow = write(tmp_path, DOCKERFILE, WORKFLOW)
    assert find_versions(dockerfile, DOCKERFILE_VERSION) == [Version(dockerfile, 3, "26.9.4-2")]
    assert find_versions(workflow, WORKFLOW_VERSION) == [
        Version(workflow, 6, "26.9.4-2"),
        Version(workflow, 11, "26.9.4-2"),
    ]


def test_the_same_version_everywhere_gives_no_errors(tmp_path: Path) -> None:
    assert check(*write(tmp_path, DOCKERFILE, WORKFLOW)) == []


def test_a_different_version_in_the_workflow_is_reported(tmp_path: Path) -> None:
    dockerfile, workflow = write(tmp_path, DOCKERFILE, WORKFLOW.replace("26.9.4-2", "26.9.4-1", 1))
    assert check(dockerfile, workflow) == [
        f"{workflow}:6: miniforge-version 26.9.4-1 differs from 26.9.4-2 in {dockerfile}:3"
    ]


@pytest.mark.parametrize("text", ["FROM base\n", DOCKERFILE + "ARG MINIFORGE_VERSION=26.9.4-1\n"])
def test_a_dockerfile_without_exactly_one_version_is_reported(tmp_path: Path, text: str) -> None:
    dockerfile, workflow = write(tmp_path, text, WORKFLOW)
    count = text.count("ARG MINIFORGE_VERSION=")
    assert check(dockerfile, workflow) == [
        f"{dockerfile}: expected one ARG MINIFORGE_VERSION line, found {count}"
    ]


def test_a_workflow_without_a_version_is_reported(tmp_path: Path) -> None:
    dockerfile, workflow = write(tmp_path, DOCKERFILE, "jobs: {}\n")
    assert check(dockerfile, workflow) == [f"{workflow}: no miniforge-version line"]


def test_a_missing_file_is_reported(tmp_path: Path) -> None:
    errors = check(tmp_path / "Dockerfile", tmp_path / "ci.yml")
    assert len(errors) == 1
    assert errors[0].startswith("cannot read: ")


def test_main_prints_each_error_and_returns_one(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    dockerfile, workflow = write(tmp_path, DOCKERFILE, WORKFLOW.replace("26.9.4-2", "26.9.4-1"))
    assert main(["--dockerfile", str(dockerfile), "--workflow", str(workflow)]) == 1
    assert capsys.readouterr().out == (
        f"{workflow}:6: miniforge-version 26.9.4-1 differs from 26.9.4-2 in {dockerfile}:3\n"
        f"{workflow}:11: miniforge-version 26.9.4-1 differs from 26.9.4-2 in {dockerfile}:3\n"
    )


def test_running_as_a_script_exits_with_zero_for_one_version(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    dockerfile, workflow = write(tmp_path, DOCKERFILE, WORKFLOW)
    args = ["--dockerfile", str(dockerfile), "--workflow", str(workflow)]
    monkeypatch.setattr("sys.argv", ["check_miniforge_version.py", *args])
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(check_miniforge_version.__file__, run_name="__main__")
    assert excinfo.value.code == 0
