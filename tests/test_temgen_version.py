import unittest
from unittest import TestCase

import semver

from temgen import Temgen


class TestTemgenVersion(TestCase):
    def test__temgen_version__ok(self):
        major = 0
        minor = 5
        patch = 0
        expected_version = semver.Version(major, minor, patch)
        self.assertEqual(Temgen.VERSION.to_tuple()[0:3], expected_version.to_tuple()[0:3])


if __name__ == '__main__':
    unittest.main()
