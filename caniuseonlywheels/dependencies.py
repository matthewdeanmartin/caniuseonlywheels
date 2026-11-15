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


from caniuseonlywheels import pypi


class CircularDependencyError(Exception):
    """Raised if there are circular dependencies detected."""


def reasons_to_paths(reasons):
    """Calculate the dependency paths to the reasons of the blockers.

    Paths will be in reverse-dependency order (i.e. parent projects are in
    ascending order).

    """
    blockers = set(reasons.keys()) - set(reasons.values())
    paths = set()
    for blocker in blockers:
        path = [blocker]
        parent = reasons[blocker]
        while parent:
            if parent in path:
                raise CircularDependencyError(
                    dict(parent=parent, blocker=blocker, path=path)
                )
            path.append(parent)
            parent = reasons.get(parent)
        paths.add(tuple(path))
    return paths


def dependencies(project_name):
    """Unresolved dependency discovery is no longer supported."""
    from caniuseonlywheels.resolved import InputError

    raise InputError(
        "Use a resolved environment or pinned lock; dependency discovery does not resolve versions"
    )


def blockers(project_names, index_url=pypi.PYPI_INDEX_URL):
    """Reject the historical name-only traversal, which could miss dependencies."""
    from caniuseonlywheels.resolved import InputError

    raise InputError("Use resolved.audit() with a resolved environment or pinned lock")
