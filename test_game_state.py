import unittest

from game_state import describe_game_state


class DescribeGameStateTests(unittest.TestCase):
    def test_normal_state(self):
        self.assertEqual(describe_game_state(3, 1200), "Lives: 3 | Score: 1200")

    def test_zero_lives_and_score(self):
        self.assertEqual(describe_game_state(0, 0), "Lives: 0 | Score: 0")

    def test_negative_lives(self):
        with self.assertRaises(ValueError):
            describe_game_state(-1, 1200)

    def test_negative_score(self):
        with self.assertRaises(ValueError):
            describe_game_state(3, -1)


if __name__ == "__main__":
    unittest.main()
