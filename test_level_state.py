import unittest

from breakout.game import Game, GameState


class LevelStateTests(unittest.TestCase):
    def test_every_level_starts_with_countdown_and_stationary_ball(self):
        game = Game()
        for _ in range(2):
            self.assertEqual(game.state, GameState.COUNTDOWN)
            self.assertEqual((game.ball_vx, game.ball_vy), (0, 0))
            game.update(3)
            self.assertTrue(game.launch_ball())
            game.update(1)
            game.start_level()

    def test_countdown_blocks_launch_and_ball_follows_player(self):
        game = Game()
        self.assertFalse(game.launch_ball())
        game.move_player(250)
        position = (game.ball_x, game.ball_y)
        game.update(2)
        self.assertEqual(game.state, GameState.COUNTDOWN)
        self.assertEqual((game.ball_x, game.ball_y), position)
        self.assertEqual(game.ball_x, game.paddle_x)

    def test_countdown_completion_waits_for_explicit_launch(self):
        game = Game()
        game.update(10)
        self.assertEqual(game.state, GameState.BALL_ATTACHED)
        game.move_player(600)
        position = (game.ball_x, game.ball_y)
        game.update(10)
        self.assertEqual((game.ball_x, game.ball_y), position)
        self.assertTrue(game.launch_ball())
        self.assertEqual(game.state, GameState.PLAYING)
        self.assertFalse(game.launch_ball())
        game.update(0.1)
        self.assertNotEqual((game.ball_x, game.ball_y), position)


if __name__ == "__main__":
    unittest.main()
