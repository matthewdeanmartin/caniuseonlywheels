# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.4.0] - 2016-06-20
### Changed
- Normalize all names to their canonical representations
- Make stale overrides less scary

## [3.3.0] - 2015-09-15
### Added
- Add Python 3.5 support
- Add functools32 to overrides

### Removed
- Drop Python 2.6 support

### Fixed
- Newlines can be part of the beginning of a file
- Don't use no-position format args

## [3.2.0] - 2015-05-29
### Fixed
- Fixed the case of valid pypi projects but there's a distlib error
- Prevent MemoryError crash when a package specifies circular dependencies
- Fix failing CLI test on UTF-8 terminals
- xlwt now supports Python 3.3+

## [3.1.0] - 2015-03-20
### Added
- Add logging to aid in understanding how caniusepython3 works under the hood
- Display the party popper emoji as a bit of flair when there are no blockers

### Fixed
- Don't barf if requirement has no url attribute
- Handle the url attribute on requirements objects from pip

### Changed
- Drop checkers that have moved upstream

## [3.0.0] - 2015-01-16
### Changed
- Work around a bug in distlib
- Use containers in Travis

## [2.2.0] - 2014-10-31
### Changed
- Move testing to unittest2

## [2.1.2] - 2014-06-05
### Fixed
- Avoid infinite recursions
- Override jinja as jinja2 supports Python 3

## [2.1.1] - 2014-05-16
### Changed
- Normalize direct dependencies

## [2.1.0] - 2014-03-28
### Changed
- Output the overrides when run in verbose mode
- Fix logging message formatting

### Removed
- Remove stale overrides for paramiko and python-keystoneclient

## [2.0.3] - 2014-03-21
### Fixed
- Fix `just_name` import path after 2.0 package restructure
- Fix `setuptools` command to correctly collect `extras_require` dependencies
- Switch from `logging.warn` to `logging.warning` to silence deprecation notice

### Changed
- Expand test coverage for `command.py` and `dependency.py` modules

## [2.0.2] - 2014-03-14
### Changed
- Unicode everywhere
- Try and make Python 2.6 happy

## [2.0.1] - 2014-03-14
### Fixed
- Fix syntax error in Python 3.3+

## [2.0.0] - 2014-03-18
### Added
- Introduce the check() function
- Allow for explicit manual overrides
- Make it easier to use icanhazpython3 as a name

### Changed
- Unify handling of multiple arguments
- Make CLI arguments accept 1+ arguments instead of using a comma-separated list

## [1.2.1] - 2014-03-18
### Added
- Allow multiple requirements files to be specified
- Set logging config in __init__ so all code gets the benefit

### Changed
- Override cmd2 and uwsgi as Python 3 compatible packages
- Clean up overrides.json and update documentation

[3.4.0]: https://github.com/matthewdeanmartin/caniuseonlywheels/compare/3.3.0...3.4.0
[3.3.0]: https://github.com/matthewdeanmartin/caniuseonlywheels/compare/3.2.0...3.3.0
[3.2.0]: https://github.com/matthewdeanmartin/caniuseonlywheels/compare/3.1.0...3.2.0
[3.1.0]: https://github.com/matthewdeanmartin/caniuseonlywheels/compare/3.0.0...3.1.0
[3.0.0]: https://github.com/matthewdeanmartin/caniuseonlywheels/compare/2.2.0...3.0.0
[2.2.0]: https://github.com/matthewdeanmartin/caniuseonlywheels/compare/2.1.2...2.2.0
[2.1.2]: https://github.com/matthewdeanmartin/caniuseonlywheels/compare/2.1.1...2.1.2
[2.1.1]: https://github.com/matthewdeanmartin/caniuseonlywheels/compare/2.1.0...2.1.1
[2.1.0]: https://github.com/matthewdeanmartin/caniuseonlywheels/compare/2.0.3...2.1.0
[2.0.3]: https://github.com/matthewdeanmartin/caniuseonlywheels/compare/2.0.2...2.0.3
[2.0.2]: https://github.com/matthewdeanmartin/caniuseonlywheels/compare/2.0.1...2.0.2
[2.0.1]: https://github.com/matthewdeanmartin/caniuseonlywheels/compare/2.0.0...2.0.1
[2.0.0]: https://github.com/matthewdeanmartin/caniuseonlywheels/compare/1.2.1...2.0.0
[1.2.1]: https://github.com/matthewdeanmartin/caniuseonlywheels/compare/1.2.0...1.2.1
