# What the result means

The unreleased resolved-set checker tests **each recorded exact version** against
published release files using the running Python's interpreter, ABI and platform
tags, plus `Requires-Python`. Wheels from other versions, incompatible tags,
yanked files and suggestions to replace a package do not count. HTTP failures,
missing releases, malformed metadata and incomplete resolved sets produce unknown
results with a nonzero exit code.

This is a read-only audit of an existing resolution, not a dependency resolver.
It never chooses versions, installs analyzed packages, imports them, or builds
source distributions. A source-only package is a blocker even when it is pure
Python. A matching published wheel must exist at the configured JSON index;
locally built wheels and other indexes are not searched.

For a requirements export, dependency validation uses the exact release's
`Requires-Dist` index metadata. That metadata can be absent, inaccurate, or differ
between release artifacts; this check does not download and inspect every wheel.
For a virtual environment it uses installed metadata. Every recorded pin is
checked, but installed metadata cannot reconstruct the extras originally
requested, so it cannot detect every absent optional dependency. Explicit extras
in pinned requirements and dependencies activate their recorded requirements.
Markers are evaluated on the running interpreter, not on a simulated platform.

A success result establishes wheel availability for the **recorded set and
metadata**. It does not guarantee that an installer will reproduce that set,
that a file is downloadable, that hashes match, or that the package works. The
tool does not detect malicious code or make wheels safe to import or execute.

Use your installer's wheel-only option for the real install:

```bash
python -m pip install --only-binary :all: -r wheels.txt
```

The published 1.0.11 release predates this repair. Its name-based traversal can
miss source-only dependencies, accept historical/incompatible wheels, and report
success after metadata errors. Do not use that release's success result as an
installation gate.
