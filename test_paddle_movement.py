"""Horizontal paddle controls and arena boundaries (t2)."""

import unittest
from unittest.mock import patch

from breakout.game import Game

try:
    import pygame
except ModuleNotFoundError:
    pygame = None


class PaddleBoundsTests(unittest.TestCase):
    def test_paddle_stays_inside_at_fixed_height_in_every_state(self):
        game = Game()
        height = game.paddle_y
        for phase in range(3):
            for target, expected in ((-500, 50), (320, 320), (1500, 750)):
                game.move_player(target)
                self.assertEqual(game.paddle_x, expected)
                self.assertEqual(game.paddle_y, height)
                self.assertGreaterEqual(game.paddle_x - game.PADDLE_WIDTH / 2, 0)
                self.assertLessEqual(
                    game.paddle_x + game.PADDLE_WIDTH / 2, game.ARENA_WIDTH
                )
            if phase == 0:
                game.update(3)
            elif phase == 1:
                game.launch_ball()


@unittest.skipIf(pygame is None, "Pygame is required for input tests")
class PaddleInputTests(unittest.TestCase):
    def test_mouse_uses_local_x_and_ignores_y(self):
        from breakout.main import handle_paddle_input

        game = Game()
        for x, y, expected in ((230, 0, 230), (230, 590, 230),
                               (-20, 300, 50), (900, 300, 750)):
            handle_paddle_input(game, pygame.event.Event(
                pygame.MOUSEMOTION, pos=(x, y), rel=(0, 0), buttons=(0, 0, 0)
            ))
            self.assertEqual(game.paddle_x, expected)
            self.assertEqual(game.paddle_y, 550)
            self.assertEqual(game.ball_x, expected)

    def test_held_arrow_keys_move_horizontally_in_game_loop(self):
        from breakout.main import main

        for left, right, expected in ((1, 0, 300), (0, 1, 500), (1, 1, 400)):
            with self.subTest(left=left, right=right):
                game = Game()
                with patch('breakout.main.pygame') as pg, \
                     patch('breakout.main.Game', return_value=game):
                    pg.time.Clock.return_value.tick.return_value = 250
                    pg.event.get.side_effect = [
                        [type('Event', (), {'type': pg.KEYDOWN, 'key': pg.K_SPACE})()],
                        [type('Event', (), {'type': pg.QUIT})()],
                    ]
                    pg.key.get_pressed.return_value = {
                        pg.K_LEFT: left, pg.K_RIGHT: right,
                    }
                    main()
                self.assertEqual(game.paddle_x, expected)
                self.assertEqual(game.paddle_y, 550)


if __name__ == '__main__':
    unittest.main()
