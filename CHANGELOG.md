# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The inherited `caniusepython3` changelog is preserved in
`CHANGELOG_legacy_caniusepython3.md`. The published 1.0.11 release has no
matching Git tag in this checkout.

## [Unreleased]
### Fixed
- Check every exact version in a resolved environment or flat requirements lock, including transitive dependencies, for a compatible wheel on the running Python.
- Report missing wheels separately from unknown results instead of treating incomplete metadata as success.

## [1.0.11] - 2021-12-06
### Changed
- Last published release before the resolved-set checker repair; detailed release notes are unavailable.

[Unreleased]: https://github.com/matthewdeanmartin/caniuseonlywheels/compare/9c7250fb7f05a8bbff8d6ac1e2987eb92f0b3840...HEAD
[1.0.11]: https://pypi.org/project/caniuseonlywheels/1.0.11/
