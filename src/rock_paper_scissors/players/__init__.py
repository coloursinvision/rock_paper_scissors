"""An opponent added to ``OPPONENTS`` becomes available as
``rock_paper_scissors --opponent <key>``."""

from __future__ import annotations

import random
from collections.abc import Callable

from rock_paper_scissors.players.base import Player, QuitGameError, Turn
from rock_paper_scissors.players.copycat import CopycatPlayer
from rock_paper_scissors.players.human import HumanPlayer
from rock_paper_scissors.players.random_bot import RandomPlayer

OpponentFactory = Callable[[random.Random], Player]

OPPONENTS: dict[str, OpponentFactory] = {
    "random": lambda rng: RandomPlayer(rng),
    "copycat": lambda rng: CopycatPlayer(rng),
}


def make_opponent(name: str, rng: random.Random | None = None) -> Player:
    try:
        factory = OPPONENTS[name]
    except KeyError:
        known = ", ".join(sorted(OPPONENTS))
        raise ValueError(f"Unknown opponent {name!r}. Available: {known}.") from None
    return factory(rng or random.Random())


__all__ = [
    "OPPONENTS",
    "CopycatPlayer",
    "HumanPlayer",
    "Player",
    "QuitGameError",
    "RandomPlayer",
    "Turn",
    "make_opponent",
]
