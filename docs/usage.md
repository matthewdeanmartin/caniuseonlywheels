# Usage

These instructions describe the **unreleased resolved-set repair**. The published
1.0.11 release still uses the older project-name check.

Run the checker on the Python interpreter and platform you intend to install on.
It checks that interpreter's implementation, ABI and platform tags; there is no
cross-platform target flag.

## A resolved requirements export

Use your existing resolver to export an already resolved lock. For example, from
a project with an up-to-date `uv.lock`:

```bash
uv export --frozen --no-hashes --no-emit-project --no-dev -o wheels.txt
python -m caniuseonlywheels --requirements wheels.txt --verbose
```

Select any desired extras/groups with your exporter's options. The checker does
not resolve dependencies or read universal `uv.lock` files directly. It accepts a
flat requirements export containing exact `name==version` pins, optional extras
(`name[extra]==version`), environment markers, blank lines and comments. It rejects
active conflicting pins, ranges, URLs, local/editable/VCS sources, hashes, nested
files and installer options. An ordinary requirements file containing only your
direct dependencies is insufficient: missing recorded dependencies produce an
unknown result, even when the parent has a wheel.

A healthy existing environment can also supply a pinned snapshot:

```bash
python -m pip freeze --all > wheels.txt
python -m caniuseonlywheels -r wheels.txt
```

Review that snapshot for unsupported direct/local/editable sources. No package is
installed, imported, or built by the check. Every active pin is checked, including
transitive dependencies and source-only pure-Python packages.

## The running virtual environment

```bash
# Windows Git Bash, using the environment's Python:
.venv/Scripts/python.exe -m caniuseonlywheels --venv .venv
# POSIX:
.venv/bin/python -m caniuseonlywheels --venv .venv
```

The checker must already be available to that interpreter. `--venv` only accepts
the **running interpreter's environment** so its wheel tags cannot silently be
borrowed from another Python. It reads installed `.dist-info/METADATA` files and
checks every installed distribution, including development tools. It rejects
system-site-package environments, legacy egg metadata and direct-URL/editable
installs. Use a resolved registry-only lock export for projects whose environment
contains an editable application.

Installed metadata does not record which extras were originally requested.
Already installed extra packages are checked; missing optional packages cannot be
inferred from that history. A lock with explicit `package[extra]==version` pins
can communicate extra selections.

## Results and exit codes

- `0`: every recorded active pin has a non-yanked compatible published wheel and
  its recorded active dependency requirements are satisfied by the supplied set.
- `3`: at least one exact version lacks a compatible non-yanked wheel.
- `2`: input, index, metadata or dependency-set checks are unresolved. This takes
  precedence over `3` when both unknowns and wheel blockers occur.

`--index` accepts a PyPI-compatible JSON API base URL (default:
`https://pypi.org/pypi`), not a `/simple` index. Each request has bounded connection
and read timeouts. `--verbose` prints the exact releases being queried.

The old `--projects`, `--metadata`, and setup.py checks cannot establish a resolved
set and now reject the input with migration guidance. `--exclude` is unsupported:
removing required pins could disguise an incomplete result. Historical package
replacement suggestions are not treated as wheels for the original dependency.

The Python API is `caniuseonlywheels.check(requirements_paths=["wheels.txt"])` or
`caniuseonlywheels.check(venv=".venv")`. It returns `False` for blockers or unknown
checks and raises `resolved.InputError` for unsupported input. Use
`resolved.audit()` with `resolved.from_requirements()` or `resolved.from_venv()`
when you need the separate blocker and unknown details.

Read the [limitations](limitations.md) before enforcing an installation policy.
