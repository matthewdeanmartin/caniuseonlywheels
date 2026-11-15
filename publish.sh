#!/usr/bin/env bash
set -euo pipefail

# Manual release only. Review the changelog and version preview before running.
uv run --frozen --no-build changelogmanager validate --strict
uv run --frozen --no-build changelogmanager release --bump-versions --pyproject-only --yes
uv lock --no-build
bash ./build.sh
version="$(uv version --short)"
uv publish "dist/caniuseonlywheels-${version}-py3-none-any.whl"
