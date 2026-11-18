# Contributing

Issues are welcome: report a bug, a wrong result or an idea for an
opponent in the
[issue tracker](https://github.com/coloursinvision/rock_paper_scissors/issues).
Pull requests are limited to collaborators, since the project has a
single maintainer.

Report a security problem privately, as [SECURITY.md](SECURITY.md)
describes, never in an issue.

## Writing an issue

- the command you ran, for example
  `rock_paper_scissors --opponent copycat --seed 3`;
- what you expected and what happened instead;
- your operating system and the output of `python --version` and
  `conda --version`.

## Rules for collaborators

- Set up the environment and run the checks as the [README](README.md)
  describes; every check passes before a change is pushed.
- Every file, commit message and pull request is written in English,
  in ASCII.
- A commit subject is an imperative sentence of at most 72 characters,
  with no type prefix; the body says why.
- Commits are signed; `main` accepts only signed commits and a linear
  history.
- Branch names are lowercase words joined by hyphens.
