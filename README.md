## Can I Use Just Wheels?

Are you worried about supply chain risks? You should be. Any clown can highjack a pypi package
and replace with a malicious package that can run malicious code on:
- install pip/setup.py *
- import
- invocation

Can't do anything about import and invocation, but it is unnecessary to run setup.py, **just always
install wheels**, using the following switches.

```bash
export PIP_ONLY_BINARY=:all:
pipenv install termcolor --skip-lock
# or
pip install termcolor --only-binary=:all:
```

But now you need to find out one by one, what in your requirements.txt doesn't support wheels!

Fortunately, here is a tool, based on the guts of caniusepython3.

## Installation
```bash
pip install caniuseonlywheels  --only-binary=:all:
```

## Usage
```bash
pip freeze>requirements.txt
python -m caniuseonlywheels -r requirements.txt --verbose
```

## Credits
Forked from "caniusepython3", Apache License, Original developer - Brett Cannon.
