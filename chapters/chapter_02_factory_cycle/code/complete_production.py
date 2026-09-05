from .validate_number import validate_number


def complete_production(work_in_process: float, production_delay: float) -> float:
    """Calculate completed production from work in process and production delay."""
    validate_number(work_in_process, "work_in_process")
    validate_number(production_delay, "production_delay")
    if work_in_process < 0:
        raise ValueError("work_in_process must be non-negative")
    if production_delay <= 0:
        raise ValueError("production_delay must be positive")
    return work_in_process / production_delay
