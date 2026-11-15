# Can I Use Only Wheels?

`caniuseonlywheels` audits an already resolved Python environment or a flat,
exact-pinned requirements export. It checks every recorded distribution,
including transitive dependencies, for a published wheel compatible with the
running interpreter. Missing wheels and unresolved checks are reported separately.

**This resolved-set repair is unreleased.** The published 1.0.11 release still
contains the older name-based checker; see the [limitations](limitations.md).

Start with the [usage guide](usage.md). The checker only reads installed metadata
and package index metadata. It does not resolve versions, install or import the
projects being analyzed, or build source distributions.
