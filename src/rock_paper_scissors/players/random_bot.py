"""The generator is passed in, so tests and ``--seed`` give reproducible games."""

from __future__ import annotations

import random
from collections.abc import Sequence

from rock_paper_scissors.moves import Move
from rock_paper_scissors.players.base import Turn


class RandomPlayer:
    def __init__(self, rng: random.Random | None = None, name: str = "computer") -> None:
        self.name = name
        self._rng = rng or random.Random()

    def choose(self, history: Sequence[Turn]) -> Move:
        return self._rng.choice(list(Move))
