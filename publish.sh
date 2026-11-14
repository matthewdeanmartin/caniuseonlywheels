#!/usr/bin/env bash
set -euo pipefail

# Manual release only. Review the version and changelog before running.
uv version --bump patch --no-sync
uv lock --no-build
bash ./build.sh
version="$(uv version --short)"
uv publish "dist/caniuseonlywheels-${version}-py3-none-any.whl"
