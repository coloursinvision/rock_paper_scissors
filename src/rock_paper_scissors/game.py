from __future__ import annotations

from dataclasses import dataclass

from rock_paper_scissors.moves import Move
from rock_paper_scissors.players.base import Player, Turn
from rock_paper_scissors.rules import Outcome, judge


@dataclass(frozen=True, slots=True)
class RoundResult:
    first: Move
    second: Move
    outcome: Outcome  # from the first player's perspective


@dataclass(frozen=True, slots=True)
class Score:
    wins: int = 0
    losses: int = 0
    draws: int = 0

    @property
    def rounds(self) -> int:
        return self.wins + self.losses + self.draws


class Match:
    def __init__(self, first: Player, second: Player) -> None:
        self.first = first
        self.second = second
        self.history: list[RoundResult] = []

    def play_round(self) -> RoundResult:
        # Both players see only finished rounds, so the second player
        # can never react to the first player's current move.
        first_move = self.first.choose(self._turns(as_first=True))
        second_move = self.second.choose(self._turns(as_first=False))
        result = RoundResult(first_move, second_move, judge(first_move, second_move))
        self.history.append(result)
        return result

    @property
    def score(self) -> Score:
        """Score from the first player's perspective."""
        outcomes = [r.outcome for r in self.history]
        return Score(
            wins=outcomes.count(Outcome.WIN),
            losses=outcomes.count(Outcome.LOSE),
            draws=outcomes.count(Outcome.DRAW),
        )

    def _turns(self, *, as_first: bool) -> list[Turn]:
        if as_first:
            return [Turn(mine=r.first, theirs=r.second) for r in self.history]
        return [Turn(mine=r.second, theirs=r.first) for r in self.history]
