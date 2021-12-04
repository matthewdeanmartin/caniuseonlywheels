from setuptools import setup

import os


# Installed name used for various commands (both script and setuptools).
command_name = os.environ.get('CIU_ALT_NAME') or 'caniusepython3'

with open('README_PyPI.rst') as file:
    long_description = file.read()

with open('dev_requirements.txt') as file:
    tests_require = [dep.strip() for dep in file.readlines()]

setup(name='caniusepython3',
      version='7.3.0',
      description='Determine what projects are blocking you from porting to Python 3',
      long_description=long_description,
      long_description_content_type='text/x-rst',
      author='Brett Cannon',
      author_email='brett@python.org',
      url='https://github.com/brettcannon/caniusepython3',
      packages=['caniusepython3', 'caniusepython3.test'],
      include_package_data=True,
      requires_python='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',
      install_requires=['distlib', 'setuptools', 'packaging',  # Input flexibility
                        'backports.functools_lru_cache',
                        'futures ; python_version=="2.7"',
                        'requests'],  # Functionality
      tests_require=tests_require,  # Testing, external due to Travis
      test_suite='caniusepython3.test',
      classifiers=[
          'Development Status :: 7 - Inactive',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
      ],
      entry_points={
          'console_scripts': [
              '{0} = caniusepython3.__main__:main'.format(command_name),
          ],
          'distutils.commands': [
              '{0} = caniusepython3.command:Command'.format(command_name),
          ],
      },
      zip_safe=True,
)
