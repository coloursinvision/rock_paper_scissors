# Decision record 2026-10-29

Status: accepted on 2026-10-29. It extends the decision on link scripts
in the record of 2026-10-26 and supersedes nothing.

## Link scripts

- Facts checked on 2026-10-29: conda runs the pre-link, post-link and
  pre-unlink scripts that a package carries and documents no setting to
  turn them off. mamba and micromamba 2.9.0 and later can skip all of
  them with skip_run_link_scripts, for every package at once, with no
  per-package exception.
- The project keeps conda as its only client and does not skip scripts
  globally, since a package that needs its script would then break
  without notice.
- scripts/check_link_scripts.py runs in CI on every platform right
  after the environment is created and fails on a link script from a
  package that is not in its allowlist. The allowlist is empty; an
  entry names the package, the reason, a reference and an expiry.
- On 2026-10-29 the locked environment had no link scripts on any
  platform: 67 packages on linux-64, 59 on osx-64, 59 on osx-arm64 and
  60 on win-64.
- The check finds a script after it has run once, in CI and in the
  environment of the developer who added the package. The limits on
  that risk are conda-forge as the only channel, the lock file with
  integrity hashes, and a review of the recipe of every new dependency.
- To be revisited when conda gains a setting for link scripts, or when
  a client with per-package control fits the project.
