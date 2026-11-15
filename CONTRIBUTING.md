# Code of Conduct
This project follows the [PSF Code of Conduct](https://www.python.org/psf/codeofconduct/).

## Releasing

Add user-facing changes to `CHANGELOG.md` and run
`uv run --frozen --no-build changelogmanager validate --strict`. A push to
`main` creates or refreshes a draft GitHub release; the draft workflow can
also be dispatched manually. Review the draft tagged `vX.Y.Z` and publish it
on GitHub when it is ready.

The published-release workflow checks that the tag points at the current
`main`, then uses keepachangelog-manager to promote `[Unreleased]` and bump
the version in `pyproject.toml` on a release PR. It refreshes `uv.lock`, runs
the package tests and wheel checks, and uploads the wheel to PyPI through the
`pypi` environment. Merge the release PR after the PyPI upload succeeds. The
PyPI trusted publisher must be configured for this repository, the
`.github/workflows/release.yml` workflow, and the `pypi` environment.

