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
- Work on a topic branch. `main` accepts a commit only after the
  required check `checks`, which waits for every CI job, has passed on
  it: push the branch, wait for `checks`, then run
  `git merge --ff-only <branch>` on `main` and push.
- Branch names are lowercase words joined by hyphens.
- In the development container, commit and push on the host; the
  README explains why.

## Dependency updates

Dependabot reports updates of the pinned GitHub Actions and of the base
image in `.devcontainer/Dockerfile` once a week. Its pull requests are
not merged: each of their commits ends in a sign-off trailer that the
commit message check rejects, so their checks fail. Make the same
change in a commit of your own on a topic branch; Dependabot then
closes its pull request.

Dependabot waits 7 days after a release of an action, but it knows
publication dates only for Docker Hub, so it proposes a new base image
from `mcr.microsoft.com` at once. Take a new image only when it is at
least 7 days old:

```bash
docker buildx imagetools inspect --format '{{ (index .Image "linux/amd64").Created }}' mcr.microsoft.com/devcontainers/base:<tag>
```

The Miniforge version is set in three places: `ARG MINIFORGE_VERSION`
in `.devcontainer/Dockerfile`, next to the SHA-256 of the installer from
the release, and `miniforge-version` twice in
`.github/workflows/ci.yml`. A pre-commit hook fails when they differ.

## Updating the lock files

The four lock files are regenerated together, from one state of
conda-forge, and only from builds at least 7 days old:

```bash
export CONDA_SOLVER=classic CONDA_FLAGS="--exclude-newer 7d"
conda lock lock --no-mamba --file environment.yml \
    -p linux-64 -p osx-64 -p osx-arm64 -p win-64 --lockfile conda-lock.yml
for version in 3_13 3_14 3_15; do
    conda lock lock --no-mamba --file environment.yml \
        --file "python_versions/python_$version.yml" \
        -p linux-64 -p osx-64 -p osx-arm64 -p win-64 \
        --lockfile "python_versions/python_$version.conda-lock.yml"
done
unset CONDA_SOLVER CONDA_FLAGS
```

Only conda's classic solver supports `--exclude-newer`, so conda-lock
runs conda instead of mamba. conda-forge records no upload dates, so the
age counts from build dates. A security fix may skip the wait: run the
same commands with `--update <package>` added and without the two
variables, and give the reason in the commit message.
