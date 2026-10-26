"""Any object with a ``name`` and ``choose(history)`` can play; the game loop needs nothing else."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from rock_paper_scissors.moves import Move


@dataclass(frozen=True, slots=True)
class Turn:
    """One finished round, seen from the side of the player being asked."""

    mine: Move
    theirs: Move


@runtime_checkable
class Player(Protocol):
    name: str

    def choose(self, history: Sequence[Turn]) -> Move:
        """Pick a move for the next round.

        ``history`` holds only finished rounds, oldest first, so a player can
        learn from the past but never sees the opponent's current move.
        """
        ...


class QuitGameError(Exception):
    """Raised by a player who wants to stop the match."""
