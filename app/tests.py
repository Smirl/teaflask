"""Package level tests."""

import unittest
from . import api_1_0, auth, main, decorators, email, exceptions, models


class MainTestCase(unittest.TestCase):

    """Main tests for the whole app."""

    def test_add(self):
        """Assert that we can add."""
        self.assertEqual(2, 1 + 1)
