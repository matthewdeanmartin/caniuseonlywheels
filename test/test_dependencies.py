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


from caniuseonlywheels import dependencies, pypi
from test import mock, unittest


class GraphResolutionTests(unittest.TestCase):
    def test_circular_dependencies(self):
        reasons = {
            "A": "C",
            "B": "C",
            "C": "A",
        }
        self.assertRaises(
            dependencies.CircularDependencyError, dependencies.reasons_to_paths, reasons
        )

    def test_all_projects_okay(self):
        # A, B, and C are fine on their own.
        self.assertEqual(set(), dependencies.reasons_to_paths({}))

    def test_leaf_okay(self):
        # A -> B where B is okay.
        reasons = {"A": None}
        self.assertEqual(frozenset([("A",)]), dependencies.reasons_to_paths(reasons))

    def test_leaf_bad(self):
        # A -> B -> C where all projects are bad.
        reasons = {"A": None, "B": "A", "C": "B"}
        self.assertEqual(
            frozenset([("C", "B", "A")]), dependencies.reasons_to_paths(reasons)
        )


class RemovedTraversalTests(unittest.TestCase):
    def test_unresolved_names_cannot_pass(self):
        from caniuseonlywheels.resolved import InputError

        with self.assertRaises(InputError):
            dependencies.blockers(["pyftpdlib"])
        with self.assertRaises(InputError):
            dependencies.dependencies("pyftpdlib")
