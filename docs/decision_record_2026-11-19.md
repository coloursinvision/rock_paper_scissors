# Decision record 2026-11-19

Status: accepted on 2026-11-19. It extends the decisions on lock files
in the records of 2026-10-26 and 2026-11-04 and supersedes nothing.

## Minimum release age of locked packages

- Facts checked on 2026-11-19: conda 26.9 and later can leave out
  packages newer than a cutoff with --exclude-newer, but on conda 26.10
  only the classic solver supports it, not the default rattler solver.
  conda-lock 4.0.3 solves through mamba 2.9.0 by default, which has no
  such option.
- With --no-mamba, CONDA_SOLVER=classic and CONDA_FLAGS set to
  "--exclude-newer 7d", conda-lock passes the cutoff to conda. A lock of
  environment.yml for the four platforms then differed from one without
  the cutoff in 45 entries, each held back to a build older than 7 days.
- The four lock files are refreshed this way, together; the commands
  are in CONTRIBUTING.md.
- conda-forge records no upload dates, so the age counts from build
  dates, which conda's documentation does not call a reliable cooldown.
  The lock file does not record the cutoff.
- A security fix may skip the wait: the package is updated alone with
  --update, and the commit message gives the reason.
- To be revisited when conda-lock or the default solver supports the
  cutoff.

## Development container

- .devcontainer/ holds a Dockerfile and devcontainer.json; .dockerignore
  lets only conda-lock.yml and scripts/check_link_scripts.py into the
  build.
- The base image is mcr.microsoft.com/devcontainers/base
  3.0.12-ubuntu26.04, pinned by the digest of its multi-platform index.
  Ubuntu 26.04 is the release the ubuntu-latest runners move to. Release
  3.0.13 was 6 days old on the day, so the older one was taken, in line
  with the 7-day rule above.
- Miniforge is installed from the release installer in the same version
  as CI and checked against a SHA-256 written in the Dockerfile; the
  release's asset digest and its .sha256 file give the same value. The
  image condaforge/miniforge3 was not used: it pins Ubuntu by a date tag
  and does not check its installer.
- The environment is created from conda-lock.yml without a solve, and
  check_link_scripts.py runs on it right after: 68 packages, no link
  scripts. The package caches are removed in the same layers, which
  takes the image from 2.88 to 2.38 GB.
- The image is built for linux/amd64, the platform CI tests and the lock
  files cover; on Apple Silicon it runs under emulation. The platform is
  set in devcontainer.json, since BuildKit warns about a constant
  platform in FROM. To be revisited with the machine-learning
  environment.
- updateContentCommand installs the package in editable mode, since
  that needs the mounted folder.
- With a local folder, commits and pushes are made on the host. The
  repository's .git/config is visible in the container, but the signing
  key it names is a path on the host, and pre-commit install in the
  container would write hooks that point to the container's
  interpreter. A codespace has its own clone, where both work.
- The base image has no system Python. The Python Environments extension
  1.44.0 then offers to install uv and Python, and no setting turns that
  off; the README asks to decline it. A system Python from apt would
  avoid the prompt but add a second interpreter beside conda.
- The extension takes the interpreter set in devcontainer.json only
  when no setting names an environment manager for the workspace;
  otherwise it takes that manager's default, the base environment.
  Whether a fresh codespace takes the right one is checked before the
  first workshop.
- No CI job builds the image. It is built and opened by hand before each
  workshop, since a container that nothing builds breaks unnoticed;
  pandas removed its own on 2025-11-07 after reports that it no longer
  worked.

## Miniforge version

- The Miniforge version is set by hand in three places: the Dockerfile
  and the two setup steps in ci.yml. scripts/check_miniforge_version.py
  fails when they differ; it runs as a pre-commit hook when either file
  changes and in the hygiene job on every push.

## Dependency updates

- Dependabot checks the pinned actions and the base image once a week,
  with a cooldown of 7 days, and groups the actions into one pull
  request.
- Its pull requests are not merged. Each of its commits ends in
  "Signed-off-by: dependabot[bot] <support@github.com>", a trailer that
  the commit message check rejects, and CI checks every commit on main,
  so one merged commit would fail every later run. The update is made
  again in a signed commit from a topic branch, and Dependabot closes
  its pull request.
- Dependabot reads publication dates only from Docker Hub
  (docker/lib/dependabot/docker/update_checker.rb on 2026-11-19), so it
  skips the cooldown for the image from mcr.microsoft.com: on
  2026-11-19 it proposed 3.0.13 at 6 days old. The age of a new image
  is checked by hand before it is taken.
- The dependency graph and Dependabot alerts are on since 2026-11-19.
  The graph lists only the two pinned actions, since it does not read
  the conda files. Dependabot security updates are off, since every
  update is made by hand.
