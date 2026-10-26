"""An Enum turns a typo such as ``"rok"`` into an error instead of a lost round."""

from __future__ import annotations

from enum import StrEnum


class Move(StrEnum):
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"

    @property
    def beats(self) -> Move:
        return _BEATS[self]

    @property
    def beaten_by(self) -> Move:
        return _BEATEN_BY[self]

    @classmethod
    def parse(cls, text: str) -> Move:
        """Accept a full name or a one-letter shortcut, in any case.

        Raises:
            ValueError: if the text is not a recognised move.
        """
        key = text.strip().lower()
        if key in _ALIASES:
            return _ALIASES[key]
        valid = ", ".join(m.value for m in cls)
        raise ValueError(f"{text!r} is not a move. Choose one of: {valid} (or r/p/s).")


_BEATS: dict[Move, Move] = {
    Move.ROCK: Move.SCISSORS,
    Move.PAPER: Move.ROCK,
    Move.SCISSORS: Move.PAPER,
}
_BEATEN_BY: dict[Move, Move] = {loser: winner for winner, loser in _BEATS.items()}
_ALIASES: dict[str, Move] = {m.value: m for m in Move} | {m.value[0]: m for m in Move}
