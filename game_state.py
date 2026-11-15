"""Helpers for describing the current game state."""


def describe_game_state(lives: int, score: int) -> str:
    """Return a description of non-negative lives and score."""
    if lives < 0 or score < 0:
        raise ValueError("Lives and score must be non-negative")
    return f"Lives: {lives} | Score: {score}"
