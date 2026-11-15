"""Executable entrypoint and initial screen for Breakout."""

import pygame

from breakout.game import Game, GameState


def handle_launch_input(game: Game, event: pygame.event.Event) -> bool:
    """Consume a fresh launch press; blocked presses are never queued."""
    space_pressed = (
        event.type == pygame.KEYDOWN
        and event.key == pygame.K_SPACE
        and not getattr(event, "repeat", False)
    )
    left_clicked = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
    if space_pressed or left_clicked:
        return game.launch_ball()
    return False


def draw_countdown(screen: pygame.Surface, game: Game) -> None:
    """Draw the three lights only while launch is blocked."""
    if game.state != GameState.COUNTDOWN:
        return
    for index, color in enumerate(game.countdown_colors):
        center = (320 + index * 80, 300)
        if index < game.filled_countdown_lights:
            pygame.draw.circle(screen, color, center, 25)
        pygame.draw.circle(screen, (255, 255, 255), center, 25, width=3)


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
                        handle_launch_input(game, event)
                elif game is not None:
                    handle_launch_input(game, event)

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
                draw_countdown(screen, game)
                if game.state == GameState.BALL_ATTACHED:
                    label = prompt_font.render(
                        "Pulsa ESPACIO o clic izquierdo para lanzar", True, (235, 238, 245)
                    )
                    screen.blit(label, label.get_rect(center=(400, 300)))
            pygame.display.flip()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
