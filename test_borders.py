import unittest

from breakout.game import Game, GameState

try:
    import pygame
except ModuleNotFoundError:
    pygame = None


class BorderTests(unittest.TestCase):
    def game_at(self, x, y, vx, vy):
        game = Game()
        game.state = GameState.PLAYING
        game.ball_x, game.ball_y = x, y
        game.ball_vx, game.ball_vy = vx, vy
        return game

    def test_side_overshoot_and_direction(self):
        for x, vx, expected_x, expected_vx in (
            (20, -100, 104, 100), (780, 100, 696, -100),
            (400, 2000, 728, -2000), (400, -2000, 72, 2000),
        ):
            with self.subTest(vx=vx):
                game = self.game_at(x, 200, vx, 0)
                game.update(1)
                self.assertEqual((game.ball_x, game.ball_vx), (expected_x, expected_vx))

    def test_corner_reflects_both_axes_and_moves_away(self):
        game = self.game_at(20, 20, -100, -100)
        game.update(0.1)
        self.assertEqual((game.ball_x, game.ball_y), (14, 14))
        self.assertEqual((game.ball_vx, game.ball_vy), (100, 100))
        game.update(0.1)
        self.assertEqual((game.ball_x, game.ball_y), (24, 24))

    def test_exact_contact_points_inward(self):
        game = self.game_at(20, 20, -80, -80)
        game.update(0.1)
        self.assertEqual((game.ball_x, game.ball_y), (12, 12))
        self.assertEqual((game.ball_vx, game.ball_vy), (80, 80))

    def test_bottom_is_open(self):
        game = self.game_at(400, 590, 0, 300)
        game.update(0.05)
        self.assertEqual(game.ball_y, 605)
        self.assertEqual(game.ball_vy, 300)
        self.assertEqual(game.state, GameState.PLAYING)

    @unittest.skipIf(pygame is None, "Pygame is required for rendering tests")
    def test_three_white_borders_and_open_bottom(self):
        from breakout.main import draw_borders

        game = Game()
        screen = pygame.Surface((game.WIDTH, game.HEIGHT))
        screen.fill((18, 22, 36))
        draw_borders(screen, game)
        for point in ((400, 0), (0, 300), (799, 300)):
            self.assertEqual(tuple(screen.get_at(point))[:3], (255, 255, 255))
        self.assertEqual(tuple(screen.get_at((400, 599)))[:3], (18, 22, 36))


if __name__ == '__main__':
    unittest.main()
