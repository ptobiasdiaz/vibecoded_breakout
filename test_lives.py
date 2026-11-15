import unittest

from breakout.game import Ball, Game, GameState


class LivesTests(unittest.TestCase):
    def playing_game(self):
        game = Game()
        game.update(3)
        game.launch_ball()
        return game

    def test_new_games_have_three_lives(self):
        game = self.playing_game()
        game.ball_y = 609
        game.update(0)
        self.assertEqual(game.lives, 2)
        self.assertEqual(Game().lives, 3)
        game.start_level()
        self.assertEqual(game.lives, 2)

    def test_ball_must_be_completely_below_bottom(self):
        game = self.playing_game()
        game.ball_y = game.HEIGHT + game.BALL_RADIUS
        game.update(0)
        self.assertEqual(game.lives, 3)
        game.ball_y += 0.01
        game.update(0)
        self.assertEqual(game.lives, 2)

    def test_losing_one_ball_preserves_other_ball_and_life(self):
        game = self.playing_game()
        survivor = Ball(400, 300, 0, 10)
        game.balls = [Ball(400, 608, 0, 20), survivor]
        game.update(0.1)
        self.assertEqual(game.balls, [survivor])
        self.assertEqual(survivor.y, 301)
        self.assertEqual(game.lives, 3)
        self.assertEqual(game.state, GameState.PLAYING)

    def test_simultaneous_losses_cost_one_life_and_restart_countdown(self):
        game = self.playing_game()
        game.balls = [Ball(300, 609), Ball(500, 610)]
        game.update(10)
        self.assertEqual(game.lives, 2)
        self.assertEqual(len(game.balls), 1)
        self.assertEqual(game.state, GameState.COUNTDOWN)
        self.assertEqual(game.filled_countdown_lights, 0)
        self.assertEqual(game.countdown_remaining, 3)
        self.assertEqual((game.ball_vx, game.ball_vy), (0, 0))
        game.move_player(200)
        self.assertEqual(game.ball_x, 200)
        for second in range(3):
            self.assertFalse(game.launch_ball())
            game.update(1)
            self.assertEqual(game.filled_countdown_lights, second + 1)
        self.assertTrue(game.launch_ball())

    def test_three_losses_end_game_without_another_ball(self):
        game = Game()
        for remaining in (2, 1, 0):
            game.update(3)
            self.assertTrue(game.launch_ball())
            game.balls = [Ball(400, 609), Ball(500, 610)]
            game.update(0)
            self.assertEqual(game.lives, remaining)
        self.assertEqual(game.state, GameState.GAME_OVER)
        self.assertEqual(game.balls, [])
        for _ in range(3):
            game.update(100)
            game.move_player(300)
            game.start_level()
            self.assertFalse(game.launch_ball())
        self.assertEqual(game.lives, 0)
        self.assertEqual(game.balls, [])
        self.assertEqual(game.state, GameState.GAME_OVER)
