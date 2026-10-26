import pytest

from rock_paper_scissors.moves import Move


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("rock", Move.ROCK),
        ("Paper", Move.PAPER),
        ("  SCISSORS ", Move.SCISSORS),
        ("r", Move.ROCK),
        ("p", Move.PAPER),
        ("s", Move.SCISSORS),
    ],
)
def test_parse_accepts_names_and_shortcuts(text, expected):
    assert Move.parse(text) is expected


@pytest.mark.parametrize("text", ["", "rok", "lizard", "x"])
def test_parse_rejects_unknown_text(text):
    with pytest.raises(ValueError, match="not a move"):
        Move.parse(text)


def test_every_move_beats_exactly_one_other_move():
    assert {m.beats for m in Move} == set(Move)
    for move in Move:
        assert move.beats is not move
        assert move.beaten_by.beats is move
