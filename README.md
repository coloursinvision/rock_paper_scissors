# rock_paper_scissors

[![CI](https://github.com/coloursinvision/rock_paper_scissors/actions/workflows/ci.yml/badge.svg)](https://github.com/coloursinvision/rock_paper_scissors/actions/workflows/ci.yml)

Rock, Paper, Scissors in Python as a small, tested package. Every player,
human or computer, implements the same one-method interface, so a new
strategy is one new class.

```text
$ printf 'r\np\nq\n' | rock_paper_scissors --opponent copycat --seed 3
Rock, Paper, Scissors: you vs copycat.
Your move (rock/paper/scissors, q to quit): You chose rock, copycat chose rock. It's a draw.
Score: you 0 - 0 copycat (draws: 1)
Your move (rock/paper/scissors, q to quit): You chose paper, copycat chose rock. You win!
Score: you 1 - 0 copycat (draws: 1)
Your move (rock/paper/scissors, q to quit): Game over after 2 round(s). Score: you 1 - 0 copycat (draws: 1)
```

## Quick start

Requires Python 3.12 or later.

```bash
git clone https://github.com/coloursinvision/rock_paper_scissors.git
cd rock_paper_scissors
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

rock_paper_scissors              # play until you type q
rock_paper_scissors --opponent copycat --rounds 5
pytest
```

`python -m rock_paper_scissors` runs the same command.

## How it is organised

```text
src/rock_paper_scissors/
    moves.py              Move enum and the table of which move beats which
    rules.py              judge(move, against) -> Outcome
    game.py               Match: asks both players, judges, keeps history and score
    cli.py                command-line options and all game output
    players/
        base.py           Player protocol and Turn
        human.py          keyboard player with a replaceable parser
        random_bot.py     random opponent, seedable
        copycat.py        opponent that repeats your previous move
```

Rules the structure follows:

- A player has a `name` and `choose(history) -> Move`. `Match` depends on
  nothing else, so it never knows whether it talks to a person or a program.
- `history` holds only finished rounds. No opponent can see the current
  move; `test_players_see_history_from_their_own_side_and_never_the_current_move`
  checks it.
- `rules.py` and `game.py` do no I/O. `HumanPlayer` reads and writes through
  functions passed to it, and `cli.py` formats the output.
- The random generator, the input functions and the parser are passed in,
  which is what makes every part testable without a keyboard.

## Adding an opponent

1. Create `src/rock_paper_scissors/players/<name>.py`:

   ```python
   class MyPlayer:
       def __init__(self, name: str = "my_bot") -> None:
           self.name = name

       def choose(self, history: Sequence[Turn]) -> Move:
           # read history[i].mine and history[i].theirs, return a Move
           raise NotImplementedError
   ```

2. Register it in `OPPONENTS` in `src/rock_paper_scissors/players/__init__.py`.
3. It is then available as `rock_paper_scissors --opponent <name>`, and
   `test_every_registered_opponent_follows_the_player_protocol` covers it.

## License

MIT, see [LICENSE](LICENSE).
