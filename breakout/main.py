"""Executable entrypoint and initial screen for Breakout."""

import pygame

from breakout.game import Game, GameState


def handle_paddle_input(game: Game, event: pygame.event.Event) -> None:
    """Mouse positions are relative to the window containing the game area."""
    if event.type == pygame.MOUSEMOTION:
        game.move_player(event.pos[0])


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


def draw_borders(screen: pygame.Surface, game: Game) -> None:
    """Draw solid walls along the top and sides, leaving the bottom open."""
    white = (255, 255, 255)
    width = game.BORDER_WIDTH
    pygame.draw.rect(screen, white, (0, 0, game.WIDTH, width))
    pygame.draw.rect(screen, white, (0, 0, width, game.HEIGHT))
    pygame.draw.rect(screen, white, (game.WIDTH - width, 0, width, game.HEIGHT))


def main() -> None:
    """Display the initial screen and run the level launch lifecycle."""
    try:
        pygame.init()
        screen = pygame.display.set_mode((Game.WIDTH, Game.HEIGHT))
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
                    handle_paddle_input(game, event)
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
                draw_borders(screen, game)
                pygame.draw.rect(screen, (235, 238, 245), (
                    game.paddle_x - game.PADDLE_WIDTH / 2,
                    game.paddle_y - game.PADDLE_HEIGHT / 2,
                    game.PADDLE_WIDTH, game.PADDLE_HEIGHT,
                ))
                for ball in game.balls:
                    pygame.draw.circle(screen, (255, 195, 70),
                                       (round(ball.x), round(ball.y)),
                                       game.BALL_RADIUS)
                if game.state == GameState.GAME_OVER:
                    label = prompt_font.render(
                        "Partida terminada", True, (235, 238, 245)
                    )
                    screen.blit(label, label.get_rect(center=(400, 300)))
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
