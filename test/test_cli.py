# Copyright 2014 Google Inc. All rights reserved.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import io
import logging
import tempfile

import caniuseonlywheels.__main__ as ciu_main
from caniuseonlywheels import projects, pypi
from test import mock, unittest
from test.custom_temp_file import CustomNamedTemporaryFile

EXAMPLE_REQUIREMENTS = """
# From
#  http://www.pip-installer.org/en/latest/reference/pip_install.html#requirement-specifiers
# but without the quotes for shell protection.
Foo.Project \
    >= 1.2
Fizzy [foo, bar]
PickyThing<1.6,>1.9,!=1.9.6,<2.0a0,==2.4c1
Hello
-e git+https://github.com/brettcannon/caniuseonlywheels#egg=caniuseonlywheels
file:../caniuseonlywheels#egg=caniuseonlywheels
# Docs say to specify an #egg argument, but apparently it's optional.
file:../../lib/project
"""

EXAMPLE_EXTRA_REQUIREMENTS = """
testing-stuff
"""

EXAMPLE_METADATA = """Metadata-Version: 1.2
Name: CLVault
Version: 0.5
Summary: Command-Line utility to store and retrieve passwords
Home-page: http://bitbucket.org/tarek/clvault
Author: Tarek Ziade
Author-email: tarek@ziade.org
License: PSF
Keywords: keyring,password,crypt
Requires-Dist: foo; sys.platform == 'okook'
Requires-Dist: bar.baz
Platform: UNKNOWN
"""

EXAMPLE_EXTRA_METADATA = """Metadata-Version: 1.2
Name: ExtraTest
Version: 0.5
Summary: Just for testing
Home-page: nowhere
Author: nobody
License: Apache
Requires-Dist: baz
"""


class CLITests(unittest.TestCase):

    expected_requirements = frozenset(["foo-project", "fizzy", "pickything", "hello"])
    expected_extra_requirements = frozenset(["testing-stuff"])
    expected_metadata = frozenset(["foo", "bar-baz"])
    expected_extra_metadata = frozenset(["baz"])

    def setUp(self):
        log = logging.getLogger("ciu")
        self._prev_log_level = log.getEffectiveLevel()
        logging.getLogger("ciu").setLevel(1000)

    def tearDown(self):
        logging.getLogger("ciu").setLevel(self._prev_log_level)

    def test_requirements(self):
        with CustomNamedTemporaryFile("w") as file:
            file.write(EXAMPLE_REQUIREMENTS)
            file.flush()
            got = projects.projects_from_requirements([file.name])
        self.assertEqual(set(got), self.expected_requirements)

    def test_multiple_requirements_files(self):
        with CustomNamedTemporaryFile("w") as f1:
            f1.write(EXAMPLE_REQUIREMENTS)
            f1.flush()
            with CustomNamedTemporaryFile("w") as f2:
                f2.write(EXAMPLE_EXTRA_REQUIREMENTS)
                f2.flush()
                got = projects.projects_from_requirements([f1.name, f2.name])
        want = self.expected_requirements.union(self.expected_extra_requirements)
        self.assertEqual(set(got), want)

    def test_metadata(self):
        got = projects.projects_from_metadata([EXAMPLE_METADATA])
        self.assertEqual(set(got), self.expected_metadata)

    def test_multiple_metadata(self):
        got = projects.projects_from_metadata(
            [EXAMPLE_METADATA, EXAMPLE_EXTRA_METADATA]
        )
        want = self.expected_metadata.union(self.expected_extra_metadata)
        self.assertEqual(set(got), want)
