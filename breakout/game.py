"""Level lifecycle and ball launch rules, independent of rendering."""

from enum import Enum, auto


class GameState(Enum):
    COUNTDOWN = auto()
    BALL_ATTACHED = auto()
    PLAYING = auto()


class Game:
    ARENA_WIDTH = 800
    ARENA_HEIGHT = 600
    COUNTDOWN_SECONDS = 3.0
    BALL_RADIUS = 8
    PADDLE_WIDTH = 100
    PADDLE_HEIGHT = 16

    def __init__(
        self,
        first_light_color: tuple[int, int, int] = (255, 70, 70),
        second_light_color: tuple[int, int, int] = (255, 195, 70),
    ) -> None:
        self.countdown_colors = (first_light_color, second_light_color, (0, 255, 0))
        self.paddle_x = self.ARENA_WIDTH / 2
        self.paddle_y = self.ARENA_HEIGHT - 50.0
        self.start_level()

    @property
    def filled_countdown_lights(self) -> int:
        """Fill one light per elapsed second, including green at completion."""
        return min(3, int(self.COUNTDOWN_SECONDS - self.countdown_remaining))

    def start_level(self) -> None:
        """Reset every level to a countdown with an attached, stationary ball."""
        self.state = GameState.COUNTDOWN
        self.countdown_remaining = self.COUNTDOWN_SECONDS
        self.ball_vx = 0.0
        self.ball_vy = 0.0
        self._attach_ball()

    def _attach_ball(self) -> None:
        self.ball_x = self.paddle_x
        self.ball_y = self.paddle_y - self.PADDLE_HEIGHT / 2 - self.BALL_RADIUS

    def move_player(self, x: float) -> None:
        """Move the paddle center horizontally, keeping its full width inside."""
        self.paddle_x = max(
            self.PADDLE_WIDTH / 2,
            min(self.ARENA_WIDTH - self.PADDLE_WIDTH / 2, x),
        )
        if self.state != GameState.PLAYING:
            self._attach_ball()

    def launch_ball(self) -> bool:
        """Authorize launch only once the countdown has finished."""
        if self.state != GameState.BALL_ATTACHED:
            return False
        self.ball_vx = 180.0
        self.ball_vy = -300.0
        self.state = GameState.PLAYING
        return True

    def update(self, dt: float) -> None:
        if dt < 0:
            raise ValueError("Elapsed time must be non-negative")
        if self.state == GameState.COUNTDOWN:
            self.countdown_remaining = max(0.0, self.countdown_remaining - dt)
            if self.countdown_remaining == 0:
                self.state = GameState.BALL_ATTACHED
        if self.state != GameState.PLAYING:
            self._attach_ball()
            return
        self.ball_x += self.ball_vx * dt
        self.ball_y += self.ball_vy * dt
