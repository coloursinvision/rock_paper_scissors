import random

import pytest

from rock_paper_scissors.moves import Move
from rock_paper_scissors.players import (
    OPPONENTS,
    CopycatPlayer,
    HumanPlayer,
    Player,
    QuitGameError,
    RandomPlayer,
    Turn,
    make_opponent,
)


def fake_input(*answers):
    """An input() replacement that returns the given answers one by one."""
    queue = list(answers)

    def _input(prompt):
        if not queue:
            raise EOFError
        return queue.pop(0)

    return _input


def test_human_retries_until_valid_move():
    messages = []
    human = HumanPlayer(input_fn=fake_input("banana", "p"), output_fn=messages.append)
    assert human.choose([]) is Move.PAPER
    assert len(messages) == 1 and "not a move" in messages[0]


@pytest.mark.parametrize("word", ["q", "quit", "EXIT"])
def test_human_can_quit(word):
    human = HumanPlayer(input_fn=fake_input(word))
    with pytest.raises(QuitGameError):
        human.choose([])


def test_human_end_of_input_quits():
    human = HumanPlayer(input_fn=fake_input())
    with pytest.raises(QuitGameError):
        human.choose([])


def test_human_parser_is_replaceable():
    # Any callable from text to Move can replace Move.parse.
    human = HumanPlayer(input_fn=fake_input("I'll throw a stone"), parse=lambda _: Move.ROCK)
    assert human.choose([]) is Move.ROCK


def test_random_player_is_reproducible_with_seed():
    a = RandomPlayer(random.Random(42))
    b = RandomPlayer(random.Random(42))
    assert [a.choose([]) for _ in range(20)] == [b.choose([]) for _ in range(20)]


def test_random_player_uses_all_moves():
    bot = RandomPlayer(random.Random(0))
    assert {bot.choose([]) for _ in range(100)} == set(Move)


def test_copycat_repeats_opponents_last_move():
    bot = CopycatPlayer(random.Random(0))
    history = [Turn(mine=Move.ROCK, theirs=Move.PAPER), Turn(mine=Move.ROCK, theirs=Move.SCISSORS)]
    assert bot.choose(history) is Move.SCISSORS


@pytest.mark.parametrize("name", sorted(OPPONENTS))
def test_every_registered_opponent_follows_the_player_protocol(name):
    bot = make_opponent(name, random.Random(0))
    assert isinstance(bot, Player)
    assert bot.choose([]) in set(Move)


def test_unknown_opponent_gives_helpful_error():
    with pytest.raises(ValueError, match="Available"):
        make_opponent("skynet")
