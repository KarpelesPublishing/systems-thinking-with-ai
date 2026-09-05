"""A workforce as tenure bands, with experience travelling alongside the people.

A headcount is a stock. Experience is a second stock that moves when people move,
which is what makes it a coflow. Modelling the first without the second produces a
workforce whose members are interchangeable, and they are not.
"""

from dataclasses import dataclass

from .validate_number import validate_number


@dataclass(frozen=True)
class Band:
    """One tenure band: how many people, and how much experience they hold between them."""

    people: float
    experience: float  # person-years, held by this band in total

    def __post_init__(self) -> None:
        validate_number(self.people, "people")
        validate_number(self.experience, "experience")
        if self.people < 0 or self.experience < 0:
            raise ValueError("a band cannot hold negative people or negative experience")

    def average(self) -> float:
        """Years per person in this band."""
        return self.experience / self.people if self.people > 0 else 0.0


def advance(
    bands: list[Band],
    hires: float,
    maturation: list[float],
    attrition: list[float],
    dt: float = 1.0,
) -> list[Band]:
    """Move people and their experience one step along the chain.

    `maturation[i]` is the fraction of band i moving up per period. `attrition[i]`
    is the fraction leaving. Experience travels at the band's own average, so people
    who leave take their experience with them and cannot leave it behind.
    """
    n = len(bands)
    if len(maturation) != n or len(attrition) != n:
        raise ValueError("one maturation and one attrition rate per band")
    if dt <= 0:
        raise ValueError("dt must be positive")
    for rate in list(maturation) + list(attrition):
        if not 0.0 <= rate <= 1.0:
            raise ValueError("rates are fractions per period, between 0 and 1")
    validate_number(hires, "hires")
    if hires < 0:
        raise ValueError("hires must be non-negative")

    people_out = [dt * maturation[i] * b.people for i, b in enumerate(bands)]
    people_lost = [dt * attrition[i] * b.people for i, b in enumerate(bands)]
    exp_out = [people_out[i] * bands[i].average() for i in range(n)]
    exp_lost = [people_lost[i] * bands[i].average() for i in range(n)]

    updated = []
    for i, band in enumerate(bands):
        people_in = hires if i == 0 else people_out[i - 1]
        exp_in = 0.0 if i == 0 else exp_out[i - 1]
        moving_out = people_out[i] if i < n - 1 else 0.0
        exp_moving_out = exp_out[i] if i < n - 1 else 0.0
        people = band.people + people_in - moving_out - people_lost[i]
        experience = (
            band.experience + exp_in + dt * band.people - exp_moving_out - exp_lost[i]
        )
        updated.append(Band(max(0.0, people), max(0.0, experience)))
    return updated


def headcount(bands: list[Band]) -> float:
    """People across every band, which conservation must preserve."""
    return sum(b.people for b in bands)


def total_experience(bands: list[Band]) -> float:
    """Person-years across every band, the coflow's total."""
    return sum(b.experience for b in bands)


def average_experience(bands: list[Band]) -> float:
    """Experience per person, the ratio that moves without jumping."""
    people = headcount(bands)
    return total_experience(bands) / people if people > 0 else 0.0


def effective_capacity(bands: list[Band], ramp_years: float = 2.0) -> float:
    """Capacity counted in experience-weighted people, not in heads.

    A person contributes in proportion to their experience up to `ramp_years`,
    and fully after that. This is the quantity a headcount-only model reports as
    equal to headcount.
    """
    if ramp_years <= 0:
        raise ValueError("ramp_years must be positive")
    return sum(b.people * min(1.0, b.average() / ramp_years) for b in bands)
