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


import datetime
import json
import logging
import multiprocessing
import pkgutil
import re
from functools import lru_cache

import packaging.utils
import requests

try:
    CPU_COUNT = max(2, multiprocessing.cpu_count())
except NotImplementedError:  # pragma: no cover
    CPU_COUNT = 2

PROJECT_NAME = re.compile(r"[\w.-]+")
PYPI_INDEX_URL = "https://pypi.org/pypi"


def just_name(supposed_name):
    """Strip off any versioning or restrictions metadata from a project name."""
    return PROJECT_NAME.match(supposed_name).group(0).lower()


def manual_overrides():
    """Read the overrides file.

    Read the overrides from cache, if available. Otherwise, an attempt is made
    to read the file as it currently stands on GitHub, and then only if that
    fails is the included file used. The result is cached for one day.
    """
    return _manual_overrides(datetime.date.today())


@lru_cache(maxsize=1)
def _manual_overrides(_cache_date=None):
    """Read the overrides file.

    An attempt is made to read the file as it currently stands on GitHub, and
    then only if that fails is the included file used.
    """
    log = logging.getLogger("ciu")
    request = requests.get(
        "https://raw.githubusercontent.com/"
        "matthewdeanmartin/caniuseonlywheels/"
        "master/caniuseonlywheels/overrides.json"
    )
    if request.status_code == 200:
        log.info("Overrides loaded from GitHub and cached")
        overrides = request.json()
    else:
        log.info("Overrides loaded from included package data and cached")
        raw_bytes = pkgutil.get_data(__name__, "overrides.json")
        overrides = json.loads(raw_bytes.decode("utf-8"))
    return {
        packaging.utils.canonicalize_name(name): replacement
        for name, replacement in overrides.items()
    }


class MetadataError(ValueError):
    """The index did not provide usable exact-release metadata."""


def release_metadata(project_name, version, index_url=PYPI_INDEX_URL):
    """Fetch one exact release. HTTP and metadata failures are never success."""
    from urllib.parse import quote
    from packaging.version import InvalidVersion, Version

    url = "{}/{}/{}/json".format(
        index_url.rstrip("/"),
        quote(project_name, safe=""),
        quote(str(version), safe=""),
    )
    logging.getLogger("ciu").info("Checking %s==%s", project_name, version)
    try:
        response = requests.get(url, timeout=(5, 30))
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise MetadataError("Could not read {}: {}".format(url, exc)) from exc
    try:
        info = data["info"]
        if packaging.utils.canonicalize_name(
            info["name"]
        ) != packaging.utils.canonicalize_name(project_name) or Version(
            info["version"]
        ) != Version(
            str(version)
        ):
            raise MetadataError(
                "Index returned a different project or version for {}=={}".format(
                    project_name, version
                )
            )
        if "requires_dist" not in info or not isinstance(data["urls"], list):
            raise MetadataError(
                "Index response lacks release files or dependency metadata"
            )
    except (KeyError, TypeError, AttributeError, InvalidVersion) as exc:
        raise MetadataError(
            "Malformed exact-release metadata for {}=={}".format(project_name, version)
        ) from exc
    return data


def release_supports_wheels(release, project_name, version):
    """Match exact-release files to the running Python's interpreter/ABI/platform."""
    from packaging.tags import sys_tags
    from packaging.specifiers import SpecifierSet
    from packaging.markers import default_environment
    from packaging.version import Version

    compatible = set(sys_tags())
    found = False
    for file_info in release["urls"]:
        try:
            filename = file_info["filename"]
            if not isinstance(filename, str):
                raise MetadataError("Invalid release filename")
            if not filename.endswith(".whl"):
                continue
            name, wheel_version, _, tags = packaging.utils.parse_wheel_filename(
                filename
            )
            if name != packaging.utils.canonicalize_name(
                project_name
            ) or wheel_version != Version(str(version)):
                raise MetadataError(
                    "Wheel filename does not match the exact release: {}".format(
                        filename
                    )
                )
            if not isinstance(file_info.get("yanked"), bool):
                raise MetadataError(
                    "Missing or invalid wheel yanked status: {}".format(filename)
                )
            if file_info["yanked"] or not compatible.intersection(tags):
                continue
            file_python = file_info.get("requires_python")
            release_python = release["info"].get("requires_python")
            if any(
                value is not None and not isinstance(value, str)
                for value in (file_python, release_python)
            ):
                raise MetadataError("Invalid Requires-Python metadata")
            requires_python = file_python or release_python
            if requires_python and not SpecifierSet(requires_python).contains(
                default_environment()["python_full_version"], prereleases=True
            ):
                continue
            found = True
        except (KeyError, TypeError, ValueError) as exc:
            raise MetadataError("Malformed wheel metadata: {}".format(exc)) from exc
    return found


def supports_wheels(project_name, version=None, index_url=PYPI_INDEX_URL):
    """Check an exact release; this does not check its dependencies."""
    if version is None:
        raise MetadataError(
            "An exact version is required; use a resolved environment or pinned lock"
        )
    return release_supports_wheels(
        release_metadata(project_name, version, index_url), project_name, version
    )
