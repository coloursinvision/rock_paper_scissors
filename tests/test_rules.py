import itertools

import pytest

from rock_paper_scissors.moves import Move
from rock_paper_scissors.rules import Outcome, judge


@pytest.mark.parametrize(
    ("move", "against", "expected"),
    [
        (Move.ROCK, Move.SCISSORS, Outcome.WIN),
        (Move.PAPER, Move.ROCK, Outcome.WIN),
        (Move.SCISSORS, Move.PAPER, Outcome.WIN),
        (Move.SCISSORS, Move.ROCK, Outcome.LOSE),
        (Move.ROCK, Move.PAPER, Outcome.LOSE),
        (Move.PAPER, Move.SCISSORS, Outcome.LOSE),
    ],
)
def test_judge(move: Move, against: Move, expected: Outcome) -> None:
    assert judge(move, against) is expected


@pytest.mark.parametrize("move", list(Move))
def test_same_move_is_a_draw(move: Move) -> None:
    assert judge(move, move) is Outcome.DRAW


@pytest.mark.parametrize(("a", "b"), list(itertools.product(Move, Move)))
def test_judge_is_symmetric(a: Move, b: Move) -> None:
    assert judge(b, a) is judge(a, b).flipped()
