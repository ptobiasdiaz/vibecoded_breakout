"""Level lifecycle and ball launch rules, independent of rendering."""

from enum import Enum, auto


class GameState(Enum):
    COUNTDOWN = auto()
    BALL_ATTACHED = auto()
    PLAYING = auto()


class Game:
    WIDTH = 800
    HEIGHT = 600
    BORDER_WIDTH = 4
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
        self.paddle_x = 400.0
        self.paddle_y = 550.0
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
        self._bounce_off_borders()

    def _bounce_off_borders(self) -> None:
        """Reflect overshoot, including multiple side hits in a single frame."""
        left = self.BORDER_WIDTH + self.BALL_RADIUS
        right = self.WIDTH - left
        span = right - left
        offset = (self.ball_x - left) % (2 * span)
        if offset == 0:
            self.ball_x = left
            self.ball_vx = abs(self.ball_vx)
        elif offset == span:
            self.ball_x = right
            self.ball_vx = -abs(self.ball_vx)
        elif offset < span:
            self.ball_x = left + offset
        else:
            self.ball_x = right - (offset - span)
            self.ball_vx = -self.ball_vx

        top = self.BORDER_WIDTH + self.BALL_RADIUS
        if self.ball_y <= top:
            self.ball_y = top + (top - self.ball_y)
            self.ball_vy = abs(self.ball_vy)
