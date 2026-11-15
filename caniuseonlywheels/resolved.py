"""Inspect an already resolved set; never choose or install package versions."""

import email.parser
import os
from pathlib import Path
import re
import sys
import sysconfig
from dataclasses import dataclass, field

from packaging.markers import default_environment
from packaging.requirements import InvalidRequirement, Requirement
from packaging.specifiers import InvalidSpecifier, SpecifierSet
from packaging.utils import canonicalize_name
from packaging.version import InvalidVersion, Version

from caniuseonlywheels import pypi


class InputError(ValueError):
    """The input is not a supported, resolved dependency set."""


@dataclass
class Pin:
    name: str
    version: str
    extras: set = field(default_factory=set)
    # None means use the exact release's index metadata; [] means no dependencies.
    requirements: object = None
    requires_python: object = None

    @property
    def label(self):
        return "{}=={}".format(self.name, self.version)


@dataclass
class Report:
    checked: int = 0
    blockers: dict = field(default_factory=dict)
    unknown: dict = field(default_factory=dict)

    @property
    def passed(self):
        return self.checked > 0 and not self.blockers and not self.unknown


def _requirement(text):
    try:
        return Requirement(text)
    except InvalidRequirement as exc:
        raise InputError("Invalid requirement {!r}: {}".format(text, exc)) from exc


def _active(requirement, extras=()):
    if requirement.marker is None:
        return True
    try:
        return any(
            requirement.marker.evaluate(dict(default_environment(), extra=extra))
            for extra in {""}.union(extras)
        )
    except (KeyError, ValueError) as exc:
        raise InputError(
            "Cannot evaluate marker in {}: {}".format(requirement, exc)
        ) from exc


def _add(pins, pin):
    previous = pins.get(pin.name)
    if previous is not None:
        if Version(previous.version) != Version(pin.version):
            raise InputError(
                "Conflicting active pins: {} and {}".format(previous.label, pin.label)
            )
        previous.extras.update(pin.extras)
    else:
        pins[pin.name] = pin


def from_requirements(paths):
    """Read flat, exact-pinned requirements exports, evaluating local markers."""
    pins = {}
    for path in paths:
        if Path(path).name == "uv.lock" or Path(path).suffix == ".toml":
            raise InputError(
                "Export the lock first: uv export --frozen --no-hashes --no-emit-project --no-dev -o wheels.txt"
            )
        for number, line in enumerate(
            Path(path).read_text(encoding="utf-8-sig").splitlines(), 1
        ):
            line = re.split(r"\s+#", line, maxsplit=1)[0].strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("-") or line.endswith("\\"):
                raise InputError(
                    "{}:{}: use a flat pinned export without options, includes, hashes or continuations".format(
                        path, number
                    )
                )
            requirement = _requirement(line)
            # Requirement has already validated marker syntax. Remove quoted
            # literals before recognizing variable names on either side of an
            # operator; a quoted value such as os_name == "extra" is harmless.
            marker_variables = re.sub(
                r"\"[^\"]*\"|'[^']*'", "", str(requirement.marker)
            )
            if requirement.marker and re.search(
                r"\b(extra|extras|dependency_groups)\b", marker_variables
            ):
                raise InputError(
                    "Lock-line extra/group markers are ambiguous; export the selected extras/groups or use name[extra]==version"
                )
            if not _active(requirement):
                continue
            specs = list(requirement.specifier)
            if (
                requirement.url
                or len(specs) != 1
                or specs[0].operator != "=="
                or "*" in specs[0].version
            ):
                raise InputError(
                    "{}:{}: expected name==version, got {!r}; resolve/export with your installer first".format(
                        path, number, line
                    )
                )
            try:
                version = str(Version(specs[0].version))
            except InvalidVersion as exc:
                raise InputError("Invalid pinned version in {!r}".format(line)) from exc
            _add(
                pins,
                Pin(
                    canonicalize_name(requirement.name),
                    version,
                    set(requirement.extras),
                ),
            )
    if not pins:
        raise InputError("No active pinned packages for the running interpreter")
    return pins


def from_venv(path):
    """Read distribution metadata in the running venv without importing packages."""
    root = Path(path).resolve()
    if root != Path(sys.prefix).resolve() or not (root / "pyvenv.cfg").is_file():
        raise InputError(
            "--venv must name the running interpreter's virtual environment; invoke its Python so wheel tags match"
        )
    config = (root / "pyvenv.cfg").read_text(encoding="utf-8")
    if re.search(r"(?im)^include-system-site-packages\s*=\s*true\s*$", config):
        raise InputError(
            "Virtual environments with system site-packages are unsupported; export a pinned lock instead"
        )
    paths = {Path(sysconfig.get_path(key)).resolve() for key in ("purelib", "platlib")}
    pins = {}
    for site in sorted(paths):
        if os.path.commonpath((str(root), str(site))) != str(root):
            raise InputError(
                "Site-packages is outside the virtual environment: {}".format(site)
            )
        for entry in sorted(site.iterdir()):
            if entry.name.endswith((".egg-info", ".egg-link", ".egg")):
                raise InputError(
                    "Legacy installed metadata is unsupported: {}".format(entry)
                )
            if not entry.name.endswith(".dist-info"):
                continue
            if (entry / "direct_url.json").exists():
                raise InputError(
                    "Local, editable, VCS and direct-URL installs cannot be matched to an index release: {}".format(
                        entry.name
                    )
                )
            metadata_path = entry / "METADATA"
            if not metadata_path.is_file():
                raise InputError("Missing installed metadata: {}".format(metadata_path))
            metadata = email.parser.Parser().parsestr(
                metadata_path.read_text(encoding="utf-8")
            )
            if not metadata.get("Name") or not metadata.get("Version"):
                raise InputError(
                    "Installed metadata lacks Name or Version: {}".format(metadata_path)
                )
            name = canonicalize_name(metadata["Name"])
            try:
                version = str(Version(metadata["Version"]))
            except InvalidVersion as exc:
                raise InputError(
                    "Invalid installed version: {}".format(metadata_path)
                ) from exc
            if name in pins:
                raise InputError("Duplicate installed distribution: {}".format(name))
            pins[name] = Pin(
                name,
                version,
                requirements=metadata.get_all("Requires-Dist", []),
                requires_python=metadata.get("Requires-Python"),
            )
    if not pins:
        raise InputError("No installed distributions found in the virtual environment")
    return pins


def _check_python(specifier):
    if specifier is None or specifier == "":
        return True
    if not isinstance(specifier, str):
        raise InputError("Requires-Python must be a string")
    try:
        return SpecifierSet(specifier).contains(
            default_environment()["python_full_version"], prereleases=True
        )
    except InvalidSpecifier as exc:
        raise InputError("Invalid Requires-Python: {!r}".format(specifier)) from exc


def audit(pins, index_url=pypi.PYPI_INDEX_URL):
    """Check files and validate recorded dependencies, without solving for versions."""
    if not pins:
        raise InputError("A nonempty resolved set is required")
    report = Report(checked=len(pins))
    requirements = {}
    active_extras = {name: set(pin.extras) for name, pin in pins.items()}
    for name, pin in sorted(pins.items()):
        try:
            release = pypi.release_metadata(name, pin.version, index_url)
            if not pypi.release_supports_wheels(release, name, pin.version):
                report.blockers[pin.label] = (
                    "no non-yanked compatible wheel for the running interpreter"
                )
            raw = (
                pin.requirements
                if pin.requirements is not None
                else release["info"]["requires_dist"]
            )
            if raw is None:
                raw = []
            if not isinstance(raw, list) or any(
                not isinstance(item, str) for item in raw
            ):
                raise InputError(
                    "Requires-Dist must be a list of requirement strings or null"
                )
            requirements[name] = [_requirement(item) for item in raw]
            python_requirement = (
                pin.requires_python
                if pin.requirements is not None
                else release["info"].get("requires_python")
            )
            if not _check_python(python_requirement):
                report.unknown[pin.label] = (
                    "resolved version does not support the running Python (Requires-Python {})".format(
                        python_requirement
                    )
                )
        except (pypi.MetadataError, InputError) as exc:
            report.unknown[pin.label] = str(exc)

    # Extras only activate requirements already recorded in metadata. No versions
    # are selected and no packages are added; cycles end when extras stabilize.
    changed = True
    while changed:
        changed = False
        for name, dependencies in requirements.items():
            for requirement in dependencies:
                try:
                    if not _active(requirement, active_extras[name]):
                        continue
                    dependency = canonicalize_name(requirement.name)
                    pin = pins.get(dependency)
                    if requirement.url:
                        raise InputError(
                            "unsupported direct-URL dependency {}".format(requirement)
                        )
                    if pin is None:
                        raise InputError(
                            "resolved set is incomplete: missing {} required by {}".format(
                                requirement, pins[name].label
                            )
                        )
                    if not requirement.specifier.contains(
                        pin.version, prereleases=True
                    ):
                        raise InputError(
                            "resolved set is inconsistent: {} requires {}, but has {}".format(
                                pins[name].label, requirement, pin.label
                            )
                        )
                    additional = set(requirement.extras) - active_extras[dependency]
                    if additional:
                        active_extras[dependency].update(additional)
                        changed = True
                except InputError as exc:
                    report.unknown["{} -> {}".format(pins[name].label, requirement)] = (
                        str(exc)
                    )
    return report
