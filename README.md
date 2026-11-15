## Can I Use Only Wheels?

[Homepage](https://matthewdeanmartin.github.io/caniuseonlywheels/) · [User guide](https://github.com/matthewdeanmartin/caniuseonlywheels/blob/main/docs/usage.md) · [PyPI](https://pypi.org/project/caniuseonlywheels/)

Are you worried about supply chain risks? You should be. Any clown can highjack a pypi package
and replace with a malicious package that can run malicious code on:
- install pip/setup.py *
- import
- invocation

Can't do anything about import and invocation, but it is unnecessary to run setup.py, **always
install wheels**, using the following switches.

```bash
export PIP_ONLY_BINARY=:all:
pipenv install termcolor --skip-lock
# or
pip install termcolor --only-binary=:all:
```

But now you need to find out one by one, what in your requirements.txt doesn't support wheels!

Fortunately, here is a tool, based on the guts of caniusepython3.

**Unreleased repair:** The checkout now audits an already resolved environment or a flat exact-pinned requirements lock. It checks every recorded version, including transitive dependencies, for a wheel compatible with the running Python. Missing wheels and unknown checks fail separately. Published 1.0.11 still has the older name-based checker and can report false success; the behavior below is not released yet.

**Scope:** No dependency resolution, package installs, imports or source builds. Index/metadata errors never count as wheel support. Read the [usage guide](docs/usage.md) and [limitations](docs/limitations.md) for supported inputs and metadata limits.

### So what do I do if the project doesn't have a wheel?
All the options have serious pros and cons. Some options are only available if you have
a direct dependency. If you have a transitive dependency, i.e. you want to install package A,
which in turn installs package B, which doesn't have a wheel. In such a case you must convince
B to publish a wheel or convince A to vendorize/remove the dependency.

* Use piwheels add to /etc/pip.conf.
```
[global]
extra-index-url=https://www.piwheels.org/simple
```
Piwheels.org is now another volunteer organization you will depend on in addtion to pypi.

* Ask the package owner to make a wheel.

* If the package owner published the script that published to pypi, offer a PR to include bdist_wheel
 
* Offer to become a contributor on the github repo if the owner doesn't want to be bothered with the work of doing 
   pull requests

* If you have a direct dependency, fork it and publish `project-name-whl` to pypi. This creates a maintenance
   headache keeping them in sync!

* If you have a direct dependency, vendorize the code. This is also a maintenance pain for keeping in sync with upgrades!

* If the project is abandoned and meets many other criteria, attempt a PEP 541 takeover of the pypi name and 
   then publish a wheel. The pypi.org really can't cope with these requests, it is very burdensome because of the risk of abuse.


## Installation
The published wheel predates the resolved-set repair described here.

```bash
pip install caniuseonlywheels  --only-binary=:all:
```

## Usage
```bash
# Export your existing uv lock, with all transitive pins:
uv export --frozen --no-hashes --no-emit-project --no-dev -o wheels.txt
python -m caniuseonlywheels -r wheels.txt --verbose

# Or inspect the running virtual environment:
.venv/Scripts/python.exe -m caniuseonlywheels --venv .venv
```

## Credits
Forked from "caniusepython3", Apache License, Original developer - Brett Cannon.

## Project Links

- [GitHub](https://github.com/matthewdeanmartin/caniuseonlywheels)
- [PyPI](https://pypi.org/project/caniuseonlywheels/)
- [Bug Tracker](https://github.com/matthewdeanmartin/caniuseonlywheels/issues)
