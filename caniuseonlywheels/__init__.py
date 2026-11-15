# Copyright 2014 Google Inc. All rights reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Calculate whether the specified package(s) and their dependencies support Wheels."""

import multiprocessing

from caniuseonlywheels import pypi

try:
    CPU_COUNT = max(2, multiprocessing.cpu_count())
except NotImplementedError:  # pragma: no cover
    CPU_COUNT = 2


def check(
    requirements_paths=(),
    metadata=(),
    projects=(),
    venv=None,
    index_url=pypi.PYPI_INDEX_URL,
):
    """Check a resolved environment or exact-pinned requirements export.

    Return False for wheel blockers or unknown index/dependency checks.
    Raise InputError for unsupported/unresolved input. No packages are installed.
    """
    from caniuseonlywheels import resolved

    if metadata or projects or bool(requirements_paths) == bool(venv):
        raise resolved.InputError(
            "Supply either venv or requirements_paths with a fully pinned lock export; unresolved projects/metadata are unsupported"
        )
    pins = (
        resolved.from_venv(venv)
        if venv
        else resolved.from_requirements(requirements_paths)
    )
    return resolved.audit(pins, index_url).passed
