import unittest

try:
    import pygame
except ModuleNotFoundError:
    pygame = None

from breakout.game import Game, GameState


class CountdownTests(unittest.TestCase):
    def test_lights_fill_at_each_second_and_reset_for_each_level(self):
        game = Game(first_light_color=(120, 30, 40), second_light_color=(50, 60, 170))
        self.assertEqual(game.countdown_colors,
                         ((120, 30, 40), (50, 60, 170), (0, 255, 0)))
        for _ in range(2):
            self.assertEqual(game.filled_countdown_lights, 0)
            for second in range(1, 4):
                game.update(0.75)
                self.assertEqual(game.filled_countdown_lights, second - 1)
                self.assertFalse(game.launch_ball())
                game.update(0.25)
                self.assertEqual(game.filled_countdown_lights, second)
            self.assertEqual(game.state, GameState.BALL_ATTACHED)
            self.assertEqual(game.ball_x, game.paddle_x)
            self.assertEqual((game.ball_vx, game.ball_vy), (0, 0))
            self.assertTrue(game.launch_ball())
            game.start_level()

    @unittest.skipIf(pygame is None, "Pygame is required for rendering tests")
    def test_render_empty_outlines_sequential_fills_and_disappearance(self):
        from breakout.main import draw_countdown

        game = Game()
        surface = pygame.Surface((800, 600))
        background = (18, 22, 36)
        for elapsed in range(4):
            surface.fill(background)
            draw_countdown(surface, game)
            for index in range(3):
                center_x = 320 + index * 80
                visible = elapsed < 3
                expected = (game.countdown_colors[index]
                            if visible and index < elapsed else background)
                self.assertEqual(surface.get_at((center_x, 300))[:3], expected)
                self.assertEqual(surface.get_at((center_x, 276))[:3],
                                 (255, 255, 255) if visible else background)
            game.update(1)


if __name__ == "__main__":
    unittest.main()
