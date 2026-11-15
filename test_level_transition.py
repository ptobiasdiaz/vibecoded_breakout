import unittest

from breakout.game import Ball, Brick, Game, GameState


class LevelTransitionTests(unittest.TestCase):
    def playing_game(self):
        game = Game()
        game.update(3)
        game.launch_ball()
        return game

    def test_remaining_brick_prevents_advance(self):
        game = self.playing_game()
        first, remaining = Brick(100, 100), Brick(200, 100)
        game.bricks = [first, remaining]
        game.destroy_brick(first)
        game.update(0)
        self.assertEqual(game.level, 1)
        self.assertEqual(game.bricks, [remaining])
        self.assertEqual(game.state, GameState.PLAYING)

    def test_last_brick_loads_next_scenario_once_and_preserves_lives(self):
        game = self.playing_game()
        game.lives = 2
        old_ball = game.balls[0]
        old_bricks = list(game.bricks)
        for brick in old_bricks:
            game.destroy_brick(brick)
            game.destroy_brick(brick)
        game.update(0)
        self.assertEqual(game.level, 2)
        self.assertEqual(game.lives, 2)
        self.assertEqual(game.state, GameState.COUNTDOWN)
        self.assertEqual(game.countdown_remaining, 3)
        self.assertEqual(len(game.bricks), 32)
        self.assertTrue(all(brick not in game.bricks for brick in old_bricks))
        self.assertIsNot(game.balls[0], old_ball)
        self.assertEqual((game.ball_vx, game.ball_vy), (0, 0))
        self.assertEqual(game._pending_brick_destructions, [])
        game.update(3)
        game.launch_ball()
        for brick in old_bricks:
            game.destroy_brick(brick)
        game.update(0)
        self.assertEqual(game.level, 2)
        self.assertEqual(len(game.bricks), 32)

    def test_completion_wins_over_simultaneous_last_ball_loss(self):
        for lives in (1, 2, 3):
            with self.subTest(lives=lives):
                game = self.playing_game()
                game.lives = lives
                game.balls = [Ball(300, 609), Ball(500, 610)]
                for brick in game.bricks:
                    game.destroy_brick(brick)
                game.update(10)
                self.assertEqual(game.level, 2)
                self.assertEqual(game.lives, lives)
                self.assertEqual(game.state, GameState.COUNTDOWN)
                self.assertEqual(game.countdown_remaining, 3)
                self.assertEqual(len(game.balls), 1)
                game.update(0)
                self.assertEqual(game.level, 2)

    def test_ball_loss_keeps_partially_destroyed_scenario(self):
        game = self.playing_game()
        first = game.bricks[0]
        remaining = game.bricks[1:]
        game.destroy_brick(first)
        game.balls = [Ball(400, 609)]
        game.update(0)
        self.assertEqual(game.lives, 2)
        self.assertEqual(game.level, 1)
        self.assertEqual(game.bricks, remaining)
        self.assertEqual(game._pending_brick_destructions, [])

    def test_unbreakable_bricks_do_not_block_completion(self):
        game = self.playing_game()
        target, wall = Brick(100, 100), Brick(200, 100, breakable=False)
        game.bricks = [target, wall]
        game.destroy_brick(wall)
        game.update(0)
        self.assertEqual(game.level, 1)
        game.destroy_brick(target)
        game.update(0)
        self.assertEqual(game.level, 2)
        self.assertNotIn(wall, game.bricks)

    def test_multiple_level_completions(self):
        game = self.playing_game()
        for expected in (2, 3, 4):
            for brick in game.bricks:
                game.destroy_brick(brick)
            game.update(0)
            self.assertEqual(game.level, expected)
            self.assertEqual(game.lives, 3)
            game.update(3)
            game.launch_ball()

    def test_game_over_cannot_advance(self):
        game = self.playing_game()
        game.lives = 1
        game.balls = []
        game.update(0)
        for brick in game.bricks:
            game.destroy_brick(brick)
        game.update(10)
        self.assertEqual(game.level, 1)
        self.assertEqual(game.state, GameState.GAME_OVER)
