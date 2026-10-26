"""Plays the opponent's previous move: the smallest strategy that reads ``history``."""

from __future__ import annotations

import random
from collections.abc import Sequence

from rock_paper_scissors.moves import Move
from rock_paper_scissors.players.base import Turn


class CopycatPlayer:
    def __init__(self, rng: random.Random | None = None, name: str = "copycat") -> None:
        self.name = name
        self._rng = rng or random.Random()

    def choose(self, history: Sequence[Turn]) -> Move:
        if not history:
            return self._rng.choice(list(Move))
        return history[-1].theirs
