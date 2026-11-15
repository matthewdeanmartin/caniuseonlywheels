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

import argparse
import logging
import platform
import sys

from caniuseonlywheels import pypi, resolved

logging.basicConfig(format="[%(levelname)s] %(message)s")


def arguments_from_cli(args):
    parser = argparse.ArgumentParser(
        description="Check every exact version in a resolved set for wheels compatible with the running interpreter."
    )
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument(
        "--requirements",
        "-r",
        nargs="+",
        help="flat exact-pinned requirements lock/export (no hashes or installer options)",
    )
    inputs.add_argument(
        "--venv", help="running interpreter's virtual environment directory"
    )
    # Recognize old flags so migration errors explain why these cannot be checked.
    inputs.add_argument("--projects", "-p", nargs="+", help=argparse.SUPPRESS)
    inputs.add_argument("--metadata", "-m", nargs="+", help=argparse.SUPPRESS)
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="log exact releases as they are checked",
    )
    parser.add_argument(
        "--index",
        "-i",
        default=pypi.PYPI_INDEX_URL,
        help="PyPI-compatible JSON API base URL (not a /simple index)",
    )
    parsed = parser.parse_args(args)
    if parsed.projects or parsed.metadata:
        parser.error(
            "Unresolved project names and root metadata cannot establish a dependency set. Use --venv or --requirements with a fully pinned lock export."
        )
    if parsed.verbose:
        logging.getLogger("ciu").setLevel(logging.INFO)
    return parsed


def print_report(report):
    print(
        "Checked {} pinned distributions for {} {} on {} ({}).".format(
            report.checked,
            platform.python_implementation(),
            platform.python_version(),
            sys.platform,
            platform.machine(),
        )
    )
    for label, reason in sorted(report.blockers.items()):
        print("BLOCKED: {}: {}".format(label, reason))
    for label, reason in sorted(report.unknown.items()):
        print("UNKNOWN: {}: {}".format(label, reason))
    if report.passed:
        print(
            "All recorded distributions have compatible published wheels; recorded dependency requirements are satisfied."
        )
    else:
        print(
            "{} wheel blockers; {} unresolved checks. Wheel-only availability is not established.".format(
                len(report.blockers), len(report.unknown)
            )
        )


def check(projects, index_url=pypi.PYPI_INDEX_URL):
    """Reject the old unresolved-name API instead of reporting false success."""
    raise resolved.InputError(
        "Unresolved project checks were removed; use caniuseonlywheels.check(requirements_paths=[...]) or check(venv=...)"
    )


def main(args=None):
    parsed = arguments_from_cli(args)
    try:
        pins = (
            resolved.from_venv(parsed.venv)
            if parsed.venv
            else resolved.from_requirements(parsed.requirements)
        )
        report = resolved.audit(pins, parsed.index)
    except (resolved.InputError, OSError, UnicodeError) as exc:
        print("UNKNOWN: {}".format(exc), file=sys.stderr)
        raise SystemExit(2)
    print_report(report)
    if report.unknown:
        raise SystemExit(2)
    if report.blockers:
        raise SystemExit(3)


if __name__ == "__main__":  # pragma: no cover
    main()
