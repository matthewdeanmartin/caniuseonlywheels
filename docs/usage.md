# Usage

Install the tool from a published wheel:

```bash
python -m pip install --only-binary :all: caniuseonlywheels
```

Check one or more projects:

```bash
python -m caniuseonlywheels --projects requests packaging
```

Check packages listed in a requirements file:

```bash
python -m caniuseonlywheels --requirements requirements.txt
```

Other inputs include `--metadata` for package metadata files. Use `--index` to select the package index URL, `--exclude` to skip a project, and `--verbose` for additional logging. Run `python -m caniuseonlywheels --help` for the full option list.

The CLI exits with code `3` when it finds blockers. Its output is advisory: [read the limitations](limitations.md) before using it to enforce an installation policy.
