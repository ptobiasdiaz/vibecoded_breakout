"""Executable entrypoint and initial screen for Breakout."""

import math

import pygame

from breakout.game import Game, GameState


def main() -> None:
    """Display the initial screen and run the level launch lifecycle."""
    try:
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Breakout")
        clock = pygame.time.Clock()
        title_font = pygame.font.Font(None, 88)
        prompt_font = pygame.font.Font(None, 32)
        title = title_font.render("BREAKOUT", True, (255, 195, 70))
        prompt = prompt_font.render(
            "Pulsa ESPACIO para comenzar", True, (235, 238, 245)
        )

        game = None
        running = True
        while running:
            dt = clock.tick(60) / 1000.0
            for event in pygame.event.get():
                # Handle exit globally, before any screen-specific input.
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if game is None:
                        game = Game()
                    else:
                        game.launch_ball()

            if not running:
                break

            screen.fill((18, 22, 36))
            if game is None:
                screen.blit(title, title.get_rect(center=(400, 250)))
                screen.blit(prompt, prompt.get_rect(center=(400, 340)))
            else:
                keys = pygame.key.get_pressed()
                direction = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
                game.move_player(game.paddle_x + direction * 400 * dt)
                game.update(dt)
                pygame.draw.rect(screen, (235, 238, 245), (
                    game.paddle_x - game.PADDLE_WIDTH / 2,
                    game.paddle_y - game.PADDLE_HEIGHT / 2,
                    game.PADDLE_WIDTH, game.PADDLE_HEIGHT,
                ))
                pygame.draw.circle(screen, (255, 195, 70),
                                   (round(game.ball_x), round(game.ball_y)),
                                   game.BALL_RADIUS)
                if game.state != GameState.PLAYING:
                    message = (str(math.ceil(game.countdown_remaining))
                               if game.state == GameState.COUNTDOWN
                               else "Pulsa ESPACIO para lanzar")
                    label = prompt_font.render(message, True, (235, 238, 245))
                    screen.blit(label, label.get_rect(center=(400, 300)))
            pygame.display.flip()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
