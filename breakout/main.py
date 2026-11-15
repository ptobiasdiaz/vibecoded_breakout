"""Executable entrypoint and initial screen for Breakout."""

import pygame


def main() -> None:
    """Display the initial screen until a global exit event is received."""
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

        running = True
        while running:
            for event in pygame.event.get():
                # Handle exit globally, before any screen-specific input.
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    running = False
                    break

            if not running:
                break

            screen.fill((18, 22, 36))
            screen.blit(title, title.get_rect(center=(400, 250)))
            screen.blit(prompt, prompt.get_rect(center=(400, 340)))
            pygame.display.flip()
            clock.tick(60)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
