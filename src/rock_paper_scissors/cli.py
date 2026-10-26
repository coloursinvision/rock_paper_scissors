from __future__ import annotations

import argparse
import random
from collections.abc import Sequence

from rock_paper_scissors.game import Match, RoundResult, Score
from rock_paper_scissors.players import OPPONENTS, HumanPlayer, QuitGameError, make_opponent
from rock_paper_scissors.rules import Outcome

VERDICT = {
    Outcome.WIN: "You win!",
    Outcome.LOSE: "You lose.",
    Outcome.DRAW: "It's a draw.",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rock_paper_scissors",
        description="Rock, Paper, Scissors in the terminal.",
    )
    parser.add_argument(
        "--opponent",
        choices=sorted(OPPONENTS),
        default="random",
        help="computer opponent to play against (default: random)",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=None,
        metavar="N",
        help="stop after N rounds (default: play until you type q)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="seed for the computer's randomness, for reproducible games",
    )
    return parser


def describe_round(result: RoundResult, you: str, them: str) -> str:
    return (
        f"{you.capitalize()} chose {result.first}, {them} chose {result.second}. "
        + VERDICT[result.outcome]
    )


def describe_score(score: Score, them: str) -> str:
    return f"Score: you {score.wins} - {score.losses} {them} (draws: {score.draws})"


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.rounds is not None and args.rounds < 1:
        build_parser().error("--rounds must be at least 1")

    human = HumanPlayer()
    opponent = make_opponent(args.opponent, random.Random(args.seed))
    match = Match(human, opponent)

    print(f"Rock, Paper, Scissors: {human.name} vs {opponent.name}.")
    try:
        while args.rounds is None or len(match.history) < args.rounds:
            result = match.play_round()
            print(describe_round(result, human.name, opponent.name))
            print(describe_score(match.score, opponent.name))
    except QuitGameError:
        pass
    except KeyboardInterrupt:
        print()

    final = describe_score(match.score, opponent.name)
    print(f"Game over after {match.score.rounds} round(s). {final}")
    return 0
