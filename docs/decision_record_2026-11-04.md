# Decision record 2026-11-04

Status: accepted on 2026-11-04. It extends the decisions on lock files
and on the CI Python range in the record of 2026-10-26 and supersedes
nothing.

## Lock files per Python version

- Facts checked on 2026-11-04: Python 3.15.0 was released on
  2026-10-09, so the supported range is 3.12 to 3.15. conda-forge has
  Python 3.12.16, 3.13.18, 3.14.10 and 3.15.2, and every locked
  package resolves for each of them on linux-64, osx-64, osx-arm64 and
  win-64.
- environment.yml stays the single list of dependencies of the lean
  environment and pins Python 3.12, the oldest supported version, for
  development; conda-lock.yml is locked from it alone.
- Each newer version has a file in python_versions/ that holds only
  its Python pin and is locked together with environment.yml into the
  lock file next to it. conda-lock 4.0.3 keeps the entry from the later
  input file for a package named in both, so only the Python pin
  differs.
- CI tests 3.12 to 3.15 on Linux and 3.12 and 3.15 on Windows, macOS
  and macOS Intel, as the record of 2026-10-26 requires. It passes the
  version-pinned --format conda-lock-v1, since conda recognizes a lock
  file by name only as conda-lock.yml or conda-lock.yaml.
- The four lock files are regenerated together, from one state of
  conda-forge. The first set was not: platformdirs 4.14.5 reached
  conda-forge between the refresh of conda-lock.yml and the new lock
  files.
- The layout matches the one pandas and xarray use: shared
  dependencies declared once and one entry per Python version, py311
  to py314 in pandas and py312 to py315 in xarray, in a pixi manifest.
  pixi is not used here (record of 2026-10-26); conda-lock gives the
  same structure.
- Python 3.12 left the support window of SPEC 0, which scientific
  Python libraries follow, on 2026-10-01. The project is an
  application, CPython supports 3.12 with security fixes until 2028-10,
  and xarray still tests it, so 3.12 stays.
- Whether the machine-learning libraries have builds for 3.15 (record
  of 2026-10-26, unverified items) is checked when the tuning
  environment is set up.
- To be revisited when Python 3.16 is released, planned for
  2027-10-06, and when CPython ends support for 3.12 in 2028-10.
