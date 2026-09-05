"""Name every reference mode once, so a trace can be compared against all six."""

from collections.abc import Callable

from .modes import (
    exponential_decay,
    exponential_growth,
    goal_seeking,
    oscillation,
    overshoot_and_collapse,
    s_shaped_growth,
)


def reference_mode_library() -> dict[str, Callable[..., list[float]]]:
    """Return the six named reference modes used as behavior targets in this book."""
    return {
        "growth": exponential_growth,
        "decay": exponential_decay,
        "goal seeking": goal_seeking,
        "oscillation": oscillation,
        "s-shaped growth": s_shaped_growth,
        "overshoot and collapse": overshoot_and_collapse,
    }
