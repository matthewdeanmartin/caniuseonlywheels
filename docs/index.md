# Can I Use Only Wheels?

`caniuseonlywheels` checks whether Python projects and their dependencies have published wheels. Give it a requirements file, installed package metadata, or project names. It reports dependency paths that still appear to need source distributions.

Start with the [usage guide](usage.md), then read the [limits of the check](limitations.md) before changing an installation policy.

The checker reads package index metadata. It does not install the projects being analyzed.
