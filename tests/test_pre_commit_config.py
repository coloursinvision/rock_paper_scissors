import re
from pathlib import Path

CONFIG = Path(__file__).parents[1] / ".pre-commit-config.yaml"


def values_of(key: str) -> list[str]:
    pattern = re.compile(rf"^\s*(?:- )?{key}: (\S+)$")
    values: list[str] = []
    for line in CONFIG.read_text(encoding="utf-8").split("\n"):
        match = pattern.match(line)
        if match is not None:
            values.append(match.group(1))
    return values


def test_every_hook_repository_is_local() -> None:
    assert values_of("repo") == ["local"]


def test_every_hook_runs_without_an_environment_of_its_own() -> None:
    languages = values_of("language")
    assert len(languages) == len(values_of("id"))
    assert set(languages) <= {"unsupported", "unsupported_script"}
