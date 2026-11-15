"""Level lifecycle and ball launch rules, independent of rendering."""

from dataclasses import dataclass
from enum import Enum, auto


class GameState(Enum):
    COUNTDOWN = auto()
    BALL_ATTACHED = auto()
    PLAYING = auto()
    GAME_OVER = auto()


@dataclass(eq=False)
class Brick:
    x: float
    y: float
    width: float = 70
    height: float = 20
    breakable: bool = True


@dataclass
class Ball:
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0


class Game:
    WIDTH = 800
    HEIGHT = 600
    BORDER_WIDTH = 4
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
        self.paddle_x = 400.0
        self.paddle_y = 550.0
        self.lives = 3
        self.balls: list[Ball] = []
        self.level = 1
        self.bricks: list[Brick] = []
        self._pending_brick_destructions: list[Brick] = []
        self.start_level()

    @property
    def filled_countdown_lights(self) -> int:
        """Fill one light per elapsed second, including green at completion."""
        return min(3, int(self.COUNTDOWN_SECONDS - self.countdown_remaining))

    def start_level(self) -> None:
        """Reset every level to a countdown with an attached, stationary ball."""
        if self.lives == 0:
            return
        self.bricks = self._load_scenario(self.level)
        self._pending_brick_destructions.clear()
        self._reset_ball()

    def _load_scenario(self, level: int) -> list[Brick]:
        """Create fresh entities for the numbered level."""
        rows = 3 + (level - 1) % 3
        return [Brick(85 + column * 80, 60 + row * 30)
                for row in range(rows) for column in range(8)]

    def destroy_brick(self, brick: Brick) -> None:
        """Queue a collision result; stale or repeated events are harmless."""
        if (self.state == GameState.PLAYING and brick.breakable
                and brick in self.bricks
                and brick not in self._pending_brick_destructions):
            self._pending_brick_destructions.append(brick)

    def _resolve_level_completion(self) -> bool:
        for brick in self._pending_brick_destructions:
            if brick in self.bricks:
                self.bricks.remove(brick)
        self._pending_brick_destructions.clear()
        if any(brick.breakable for brick in self.bricks):
            return False
        self.level += 1
        self.start_level()
        return True

    def _reset_ball(self) -> None:
        """Restart the countdown without rebuilding a partially cleared level."""
        self.state = GameState.COUNTDOWN
        self.countdown_remaining = self.COUNTDOWN_SECONDS
        self.balls = [Ball(self.paddle_x, self.paddle_y)]
        self._attach_ball()

    def _attach_ball(self) -> None:
        self.ball_x = self.paddle_x
        self.ball_y = self.paddle_y - self.PADDLE_HEIGHT / 2 - self.BALL_RADIUS

    def move_player(self, x: float) -> None:
        self.paddle_x = max(self.PADDLE_WIDTH / 2, min(800 - self.PADDLE_WIDTH / 2, x))
        if self.state in (GameState.COUNTDOWN, GameState.BALL_ATTACHED):
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
            if self.state != GameState.GAME_OVER:
                self._attach_ball()
            return
        for ball in self.balls:
            ball.x += ball.vx * dt
            ball.y += ball.vy * dt
            self._bounce_off_borders(ball)
        self.balls = [ball for ball in self.balls
                      if ball.y - self.BALL_RADIUS <= self.HEIGHT]
        # Resolve completion once, before charging for the last ball lost.
        if self._resolve_level_completion():
            return
        if not self.balls:
            self.lives -= 1
            if self.lives:
                self._reset_ball()
            else:
                self.state = GameState.GAME_OVER

    def _bounce_off_borders(self, ball: Ball) -> None:
        """Reflect overshoot, including multiple side hits in a single frame."""
        left = self.BORDER_WIDTH + self.BALL_RADIUS
        right = self.WIDTH - left
        span = right - left
        offset = (ball.x - left) % (2 * span)
        if offset == 0:
            ball.x = left
            ball.vx = abs(ball.vx)
        elif offset == span:
            ball.x = right
            ball.vx = -abs(ball.vx)
        elif offset < span:
            ball.x = left + offset
        else:
            ball.x = right - (offset - span)
            ball.vx = -ball.vx

        top = self.BORDER_WIDTH + self.BALL_RADIUS
        if ball.y <= top:
            ball.y = top + (top - ball.y)
            ball.vy = abs(ball.vy)

    @property
    def ball_x(self) -> float:
        """Access the primary ball for existing single-ball callers."""
        return self.balls[0].x

    @ball_x.setter
    def ball_x(self, value: float) -> None:
        self.balls[0].x = value

    @property
    def ball_y(self) -> float:
        """Access the primary ball for existing single-ball callers."""
        return self.balls[0].y

    @ball_y.setter
    def ball_y(self, value: float) -> None:
        self.balls[0].y = value

    @property
    def ball_vx(self) -> float:
        """Access the primary ball for existing single-ball callers."""
        return self.balls[0].vx

    @ball_vx.setter
    def ball_vx(self, value: float) -> None:
        self.balls[0].vx = value

    @property
    def ball_vy(self) -> float:
        """Access the primary ball for existing single-ball callers."""
        return self.balls[0].vy

    @ball_vy.setter
    def ball_vy(self, value: float) -> None:
        self.balls[0].vy = value
