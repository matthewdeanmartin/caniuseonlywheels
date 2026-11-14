#!/usr/bin/env bash
set -euo pipefail

export PYTHONUTF8=1

uv run --frozen --no-build python -X utf8 -m pytest test -q --cov=caniuseonlywheels --cov-report=term-missing
uv build --wheel --no-build --no-build-logs
uv run --frozen --no-build check-wheel-contents dist/*.whl
uv run --frozen --no-build vermin caniuseonlywheels
