"""Nothing here reads input or prints, so any interface can reuse the rules."""

from __future__ import annotations

from enum import StrEnum

from rock_paper_scissors.moves import Move


class Outcome(StrEnum):
    WIN = "win"
    LOSE = "lose"
    DRAW = "draw"

    def flipped(self) -> Outcome:
        """The same result seen from the other player's side."""
        if self is Outcome.WIN:
            return Outcome.LOSE
        if self is Outcome.LOSE:
            return Outcome.WIN
        return Outcome.DRAW


def judge(move: Move, against: Move) -> Outcome:
    """Result for the player who played ``move``."""
    if move is against:
        return Outcome.DRAW
    return Outcome.WIN if move.beats is against else Outcome.LOSE
