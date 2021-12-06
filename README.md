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

### So what do I do if the project doesn't have a wheel?
All the options have serious pros and cons. Some options are only available if you have
a direct dependency. If you have a transitive dependency, i.e. you want to install package A,
which in turn installs package B, which doesn't have a wheel. In such a case you must convince
B to publish a wheel or convince A to vendorize/remove the dependency.

1. Use piwheels add to /etc/pip.conf.
```
[global]
extra-index-url=https://www.piwheels.org/simple
```
Piwheels.org is now another volunteer organization you will depend on in addtion to pypi.
2. Ask them to make a wheel. 
3. If they published the script that published to pypi, offer a PR to include bdist_wheel
4. Offer to become a contributor on the github repo if the owner doesn't want to be bothered with the work of doing 
   pull requests
5. If you have a direct dependency, fork it and publish `project-name-whl` to pypi. This creates a maintenance
   headache keeping them in sync!
6. If you have a direct dependency, vendorize the code. This is also a maintenance pain for keeping in sync with upgrades!
7. If the project is abandoned and meets many other criteria, attempt a PEP 541 takeover of the pypi name and 
   then publish a wheel. The pypi org really can't cope with these requests.


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
