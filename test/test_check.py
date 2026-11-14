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


import tempfile

import caniuseonlywheels as ciu
from caniuseonlywheels import pypi
from test import mock, unittest
from test.custom_temp_file import CustomNamedTemporaryFile

wheelless_project = "stackapi"  # https://pypi.org/project/PuLP/

EXAMPLE_METADATA = """Metadata-Version: 1.2
Name: TestingMetadata
Version: 0.5
Summary: testing
Home-page: http://github.com/brettcannon/caniuseonlywheels
Author: Brett Cannon
Author-email: brett@python.org
License: Apache
Requires-Dist: {}
""".format(
    wheelless_project
)


class CheckTest(unittest.TestCase):

    def setUp(self):
        wheel_support = {"scipy": True, "numpy": True, "ipython": True,
                         wheelless_project: False, "unittest2": True}
        supports = mock.patch(
            "caniuseonlywheels.pypi.supports_wheels",
            side_effect=lambda name: wheel_support.get(name.lower(), True),
        )
        overrides = mock.patch("caniuseonlywheels.pypi.manual_overrides", return_value={})
        self.supports = supports.start()
        overrides.start()
        self.addCleanup(supports.stop)
        self.addCleanup(overrides.stop)

    # When testing input, make sure to use project names that **will** lead to
    # a False answer since unknown projects are skipped.

    def test_success(self):
        self.assertTrue(ciu.check(projects=["scipy", "numpy", "ipython"]))

    def test_failure(self):
        self.assertFalse(ciu.check(projects=[wheelless_project]))

    def test_requirements(self):
        with CustomNamedTemporaryFile("w") as file:
            file.write(wheelless_project + "\n")
            file.flush()
            self.assertFalse(ciu.check(requirements_paths=[file.name]))

    def test_metadata(self):
        self.assertFalse(ciu.check(metadata=[EXAMPLE_METADATA]))

    def test_projects(self):
        # Implicitly done by test_success and test_failure.
        pass

    def test_case_insensitivity(self):
        funky_name = (
            wheelless_project[: len(wheelless_project)].lower()
            + wheelless_project[len(wheelless_project) :].upper()
        )
        self.assertFalse(ciu.check(projects=[funky_name]))

    def test_ignore_missing_projects(self):
        self.assertTrue(ciu.check(projects=["sdfsjdfsdlfk;jasdflkjasdfdfsdf"]))

    def test_manual_overrides(self):
        name = "dummy-xyzzy-12341234123412341234"
        pypi._manual_overrides.cache_clear()
        try:
            with mock.patch("caniuseonlywheels.pypi.manual_overrides", side_effect=pypi._manual_overrides), \
                 mock.patch("caniuseonlywheels.pypi.requests.get", return_value=mock.Mock(status_code=404)), \
                 mock.patch("builtins.print") as output:
                self.assertTrue(ciu.check(projects=[name]))
            output.assert_called_once_with(
                f"You will need to replace {name} with https://pypi.org/project/termcolor-whl/"
            )
        finally:
            pypi._manual_overrides.cache_clear()
        self.supports.assert_not_called()
