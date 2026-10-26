from rock_paper_scissors.cli import main
from rock_paper_scissors.game import Match, Score
from rock_paper_scissors.moves import Move
from rock_paper_scissors.rules import Outcome


class Scripted:
    """A test player that plays a fixed list of moves and records what it was shown."""

    def __init__(self, *moves, name="scripted"):
        self.name = name
        self._moves = list(moves)
        self.seen_histories = []

    def choose(self, history):
        self.seen_histories.append(list(history))
        return self._moves.pop(0)


def test_play_round_judges_and_records_history():
    match = Match(Scripted(Move.ROCK), Scripted(Move.SCISSORS))
    result = match.play_round()
    assert (result.first, result.second, result.outcome) == (Move.ROCK, Move.SCISSORS, Outcome.WIN)
    assert match.history == [result]


def test_score_counts_from_first_players_perspective():
    match = Match(
        Scripted(Move.ROCK, Move.ROCK, Move.ROCK),
        Scripted(Move.SCISSORS, Move.PAPER, Move.ROCK),
    )
    for _ in range(3):
        match.play_round()
    assert match.score == Score(wins=1, losses=1, draws=1)
    assert match.score.rounds == 3


def test_players_see_history_from_their_own_side_and_never_the_current_move():
    first = Scripted(Move.ROCK, Move.PAPER)
    second = Scripted(Move.SCISSORS, Move.SCISSORS)
    match = Match(first, second)
    match.play_round()
    match.play_round()

    assert first.seen_histories[0] == [] and second.seen_histories[0] == []
    # In round 2 each side sees round 1, with "mine" being its own move.
    assert (first.seen_histories[1][0].mine, first.seen_histories[1][0].theirs) == (
        Move.ROCK,
        Move.SCISSORS,
    )
    assert (second.seen_histories[1][0].mine, second.seen_histories[1][0].theirs) == (
        Move.SCISSORS,
        Move.ROCK,
    )


def test_cli_plays_a_full_game(monkeypatch, capsys):
    answers = iter(["r", "p", "q"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    assert main(["--seed", "1"]) == 0
    out = capsys.readouterr().out
    assert "You chose rock" in out
    assert "Game over after 2 round(s)" in out


def test_cli_stops_after_requested_rounds(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _prompt: "s")
    assert main(["--rounds", "3", "--opponent", "copycat", "--seed", "7"]) == 0
    assert "Game over after 3 round(s)" in capsys.readouterr().out
