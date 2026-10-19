# Testing

## 1.1.0 - 2026-10-16

Run `python -m pip install -e ".[dev]"`, `ruff format --check .`, `ruff check .`, `pytest`, and `python -m build`. Keep regression fixtures synthetic and source inputs unchanged. `tests/test_feature_wave.py` covers the new behavior, malformed inputs and compatibility defaults. Verify README and CHANGELOG in wheel metadata/documentation and in the source archive before release. Protected cross-platform CI and CodeQL remain required; draft PR preparation does not authorize a merge or release.

## 1.1.1 qualification

Run the full configured Ruff, pytest branch-coverage and package-build checks. Output-safety regressions cover existing/source destinations, symlink destinations, concurrent creators and ordinary I/O failures. Install both the wheel and source distribution separately outside the checkout, verify the entry point and version, and compare packaged documentation with this source. CI must pass on its supported OS/Python matrix before merge.

Closed stdout pipes return exit code 2 with a useful error, without leaving report bytes in an interpreter buffer. Regression checks cover small/large pipes, partial writes and complete Unicode output.
