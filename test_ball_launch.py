import unittest

try:
    import pygame
except ModuleNotFoundError:
    pygame = None

from breakout.game import Game, GameState


@unittest.skipIf(pygame is None, "Pygame is required for input tests")
class BallLaunchTests(unittest.TestCase):
    def launch_events(self):
        return (
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE),
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1),
        )

    def test_each_input_launches_only_after_countdown_and_only_once(self):
        from breakout.main import handle_launch_input

        for event in self.launch_events():
            with self.subTest(event=event):
                game = Game()
                game.update(2.9)
                self.assertFalse(handle_launch_input(game, event))
                game.update(0.2)
                game.move_player(620)
                game.update(1)
                self.assertEqual(game.state, GameState.BALL_ATTACHED)
                self.assertEqual(game.ball_x, game.paddle_x)
                self.assertEqual(game.ball_y, game.paddle_y - 16)
                self.assertEqual((game.ball_vx, game.ball_vy), (0, 0))

                self.assertTrue(handle_launch_input(game, event))
                game.update(0.1)
                position = (game.ball_x, game.ball_y)
                game.move_player(300)
                game.ball_vx = -200
                for extra_event in self.launch_events():
                    self.assertFalse(handle_launch_input(game, extra_event))
                self.assertEqual((game.ball_x, game.ball_y), position)
                self.assertEqual(game.ball_vx, -200)
                game.update(0.1)
                self.assertLess(game.ball_x, position[0])

    def test_other_buttons_and_key_repeat_do_not_launch(self):
        from breakout.main import handle_launch_input

        game = Game()
        game.update(3)
        for event in (
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3),
            pygame.event.Event(pygame.MOUSEBUTTONUP, button=1),
            pygame.event.Event(pygame.KEYUP, key=pygame.K_SPACE),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT),
            pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, repeat=True),
        ):
            self.assertFalse(handle_launch_input(game, event))
        self.assertEqual(game.state, GameState.BALL_ATTACHED)


if __name__ == "__main__":
    unittest.main()
