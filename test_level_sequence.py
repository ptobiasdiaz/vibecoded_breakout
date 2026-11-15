"""End-to-end level preparation through the public game, input and draw APIs."""

import unittest

try:
    import pygame
except ModuleNotFoundError:
    pygame = None

from breakout.game import Game, GameState
if pygame is not None:
    from breakout.main import draw_countdown, handle_launch_input


class LevelLifecycleTests(unittest.TestCase):
    def test_new_levels_reset_elapsed_time_and_wait_for_launch(self):
        game = Game()
        for level in range(3):
            with self.subTest(level=level + 1):
                self.assertEqual(game.state, GameState.COUNTDOWN)
                self.assertEqual(game.countdown_remaining, 3)
                self.assertEqual(game.filled_countdown_lights, 0)
                for elapsed, filled in ((0.875, 0), (0.125, 1),
                                        (0.875, 1), (0.125, 2),
                                        (0.875, 2)):
                    game.update(elapsed)
                    self.assertEqual(game.filled_countdown_lights, filled)
                    self.assertFalse(game.launch_ball())
                # A frame crossing the deadline must not move or launch the ball.
                game.update(5)
                self.assertEqual(game.state, GameState.BALL_ATTACHED)
                game.move_player(250 + level * 100)
                position = (game.paddle_x, game.paddle_y - 16)
                game.update(10)
                self.assertEqual((game.ball_x, game.ball_y), position)
                self.assertEqual((game.ball_vx, game.ball_vy), (0, 0))
                self.assertTrue(game.launch_ball())
                game.update(0.1)
                self.assertNotEqual((game.ball_x, game.ball_y), position)
                game.start_level()
                self.assertEqual((game.ball_x, game.ball_y), position)
                self.assertEqual((game.ball_vx, game.ball_vy), (0, 0))


@unittest.skipIf(pygame is None, "Pygame is required for input and rendering tests")
class LevelSequenceTests(unittest.TestCase):
    def assert_lights(self, game, filled, visible=True):
        surface = pygame.Surface((800, 600))
        background = (18, 22, 36)
        surface.fill(background)
        draw_countdown(surface, game)
        for index, color in enumerate(game.countdown_colors):
            x = 320 + index * 80
            self.assertEqual(
                surface.get_at((x, 300))[:3],
                color if visible and index < filled else background,
            )
            self.assertEqual(
                surface.get_at((x, 276))[:3],
                (255, 255, 255) if visible else background,
            )

    def assert_attached(self, game):
        self.assertEqual(game.ball_x, game.paddle_x)
        self.assertEqual(
            game.ball_y,
            game.paddle_y - game.PADDLE_HEIGHT / 2 - game.BALL_RADIUS,
        )
        self.assertEqual((game.ball_vx, game.ball_vy), (0, 0))

    def test_complete_sequence_for_each_launch_method_on_each_level(self):
        events = (
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE),
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1),
        )
        for launch_event in events:
            game = Game()
            for level in range(3):
                with self.subTest(input=launch_event, level=level + 1):
                    if level:
                        game.start_level()
                    self.assertEqual(game.state, GameState.COUNTDOWN)
                    self.assertEqual(game.countdown_remaining, 3)
                    self.assertEqual(game.filled_countdown_lights, 0)
                    self.assert_attached(game)
                    self.assert_lights(game, 0)

                    for second in range(3):
                        game.move_player(200 + second * 150)
                        game.update(0.875)
                        self.assertEqual(game.state, GameState.COUNTDOWN)
                        self.assertEqual(game.filled_countdown_lights, second)
                        self.assert_lights(game, second)
                        for event in events:
                            self.assertFalse(handle_launch_input(game, event))
                        self.assert_attached(game)
                        game.update(0.125)
                        self.assertEqual(game.filled_countdown_lights, second + 1)

                    self.assertEqual(game.state, GameState.BALL_ATTACHED)
                    self.assert_lights(game, 0, visible=False)
                    # Blocked inputs must not launch later, even after a long frame.
                    game.update(10)
                    game.move_player(650)
                    self.assertEqual(game.state, GameState.BALL_ATTACHED)
                    self.assert_attached(game)
                    position = (game.ball_x, game.ball_y)
                    self.assertTrue(handle_launch_input(game, launch_event))
                    self.assertEqual(game.state, GameState.PLAYING)
                    game.update(0.1)
                    self.assertNotEqual((game.ball_x, game.ball_y), position)


if __name__ == "__main__":
    unittest.main()
