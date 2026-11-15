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


import packaging.utils

from caniuseonlywheels import pypi
from test import mock, unittest


class NameTests(unittest.TestCase):
    def test_simple(self):
        want = "simple-name_with.everything-separator_known"
        got = pypi.just_name(want)
        self.assertEqual(got, want)

    def test_requirements(self):
        want = "project.name"
        got = pypi.just_name(want + ">=2.0.1")
        self.assertEqual(got, want)

    def test_bad_requirements(self):
        # From the OpenStack requirements file:
        # https://raw2.github.com/openstack/requirements/master/global-requirements.txt
        want = "warlock"
        got = pypi.just_name(want + ">1.01<2")
        self.assertEqual(got, want)

    def test_metadata(self):
        want = "foo"
        got = pypi.just_name("foo; sys.platform == 'okook'")
        self.assertEqual(got, want)


class OverridesTests(unittest.TestCase):
    def setUp(self):
        pypi._manual_overrides.cache_clear()
        request = mock.patch(
            "caniuseonlywheels.pypi.requests.get",
            return_value=mock.Mock(status_code=404),
        )
        request.start()
        self.addCleanup(request.stop)
        self.addCleanup(pypi._manual_overrides.cache_clear)

    def test_canonicalization(self):
        for name in pypi.manual_overrides():
            self.assertEqual(name, packaging.utils.canonicalize_name(name))

    def test_success(self):
        overrides = pypi.manual_overrides()
        self.assertTrue(len(overrides) >= 1)
        self.assertIn("dummy-xyzzy-12341234123412341234", overrides)
        self.assertEqual(
            overrides["dummy-xyzzy-12341234123412341234"],
            "https://pypi.org/project/termcolor-whl/",
        )
