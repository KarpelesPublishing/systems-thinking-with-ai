"""Which loop is driving the behavior right now, measured by knockout.

Two loops act on the same stock. Asking which one explains the behavior is not
answerable in the abstract: the answer changes over the run. Knockout measures it
by disabling one loop at a time and recording how much the rate of change moves.
"""

from dataclasses import dataclass

REINFORCING = "word of mouth"
BALANCING = "saturation"


@dataclass(frozen=True)
class Diffusion:
    """Adoption driven by outside influence and by contact with existing adopters."""

    total_market: float = 1000.0
    innovation: float = 0.01
    imitation: float = 0.30

    def __post_init__(self) -> None:
        if self.total_market <= 0:
            raise ValueError("total_market must be positive")
        if not 0.0 <= self.innovation <= 1.0 or not 0.0 <= self.imitation <= 5.0:
            raise ValueError("innovation and imitation must be non-negative and plausible")

    def adoption_rate(
        self,
        adopters: float,
        *,
        contact_from: float | None = None,
        potential_from: float | None = None,
    ) -> float:
        """Adoption this period.

        `contact_from` freezes the adopter pool the imitation term sees, which
        disables the reinforcing loop. `potential_from` freezes the remaining
        market, which disables the balancing loop. Freezing is how a loop is cut
        without changing anything else about the model.
        """
        contact = adopters if contact_from is None else contact_from
        remaining = self.total_market - (adopters if potential_from is None else potential_from)
        remaining = max(0.0, remaining)
        return (self.innovation + self.imitation * contact / self.total_market) * remaining


def run(model: Diffusion, steps: int, initial: float = 1.0, dt: float = 1.0) -> list[float]:
    """The adopter path with both loops live."""
    if steps < 1:
        raise ValueError("steps must be at least 1")
    path = [float(initial)]
    for _ in range(steps):
        path.append(min(model.total_market, path[-1] + dt * model.adoption_rate(path[-1])))
    return path


def contributions(model: Diffusion, path: list[float]) -> dict[str, list[float]]:
    """How much each loop's removal changes the rate, at every point on the path."""
    out: dict[str, list[float]] = {REINFORCING: [], BALANCING: []}
    for adopters in path:
        full = model.adoption_rate(adopters)
        out[REINFORCING].append(abs(full - model.adoption_rate(adopters, contact_from=0.0)))
        out[BALANCING].append(abs(full - model.adoption_rate(adopters, potential_from=0.0)))
    return out


def dominant_loop(model: Diffusion, path: list[float]) -> list[str]:
    """The loop with the larger contribution at each point."""
    c = contributions(model, path)
    return [
        REINFORCING if r >= b else BALANCING
        for r, b in zip(c[REINFORCING], c[BALANCING], strict=True)
    ]


def handover_step(model: Diffusion, path: list[float]) -> int | None:
    """The step where dominance changes hands. None when it never does."""
    labels = dominant_loop(model, path)
    for i in range(1, len(labels)):
        if labels[i] != labels[i - 1]:
            return i
    return None
