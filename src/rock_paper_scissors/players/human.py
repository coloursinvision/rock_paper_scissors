"""Input, output and parsing are passed in, so tests can script the input and
the parser can be replaced, for example by one that reads free text."""

from __future__ import annotations

from collections.abc import Callable, Sequence

from rock_paper_scissors.moves import Move
from rock_paper_scissors.players.base import QuitGameError, Turn

QUIT_WORDS = frozenset({"q", "quit", "exit"})


class HumanPlayer:
    def __init__(
        self,
        name: str = "you",
        *,
        input_fn: Callable[[str], str] | None = None,
        output_fn: Callable[[str], None] | None = None,
        parse: Callable[[str], Move] = Move.parse,
    ) -> None:
        self.name = name
        # Resolved here rather than as default arguments, so the built-ins are
        # looked up when the player is created (and can be patched in tests).
        self._input = input_fn or input
        self._output = output_fn or print
        self._parse = parse

    def choose(self, history: Sequence[Turn]) -> Move:
        while True:
            try:
                text = self._input("Your move (rock/paper/scissors, q to quit): ")
            except EOFError:  # Ctrl+D, or the end of piped input
                raise QuitGameError from None
            if text.strip().lower() in QUIT_WORDS:
                raise QuitGameError
            try:
                return self._parse(text)
            except ValueError as error:
                self._output(str(error))
