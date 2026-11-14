# What the result means

The checker asks whether **any release** of a project has **any wheel**. A positive result does not establish that the current version has a wheel for your Python version, operating system, architecture, or ABI.

It reads dependency metadata and follows projects that appear to lack wheels. Failed or missing index responses can be treated as wheel-compatible, so problems may be missed. The tool also has a built-in override list. Review the result against the actual versions and platforms you support.

The checker does not detect malicious code in a wheel or prove that a package is safe. It does not install analyzed projects. To require wheels during a real install, use your installer’s wheel-only option, for example:

```bash
python -m pip install --only-binary :all: -r requirements.txt
```

That installer check is the final test of whether the selected dependency set has compatible published wheels.
