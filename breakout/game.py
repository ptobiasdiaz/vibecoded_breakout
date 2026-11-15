"""Level lifecycle and ball launch rules, independent of rendering."""

from enum import Enum, auto


class GameState(Enum):
    COUNTDOWN = auto()
    BALL_ATTACHED = auto()
    PLAYING = auto()


class Game:
    COUNTDOWN_SECONDS = 3.0
    BALL_RADIUS = 8
    PADDLE_WIDTH = 100
    PADDLE_HEIGHT = 16

    def __init__(self) -> None:
        self.paddle_x = 400.0
        self.paddle_y = 550.0
        self.start_level()

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
        self.paddle_x = max(self.PADDLE_WIDTH / 2, min(800 - self.PADDLE_WIDTH / 2, x))
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
