import unittest

from src.dag_validation import base_value, derived_value


class TestBaseValue(unittest.TestCase):
    def test_base_value(self):
        self.assertEqual(base_value(), 10)

    def test_derived_value(self):
        self.assertEqual(derived_value(), 20)
