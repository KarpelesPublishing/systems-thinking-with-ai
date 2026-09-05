import statistics

import pytest

from chapters.chapter_18_hybrid.code.coupling import (
    AggregateStaffing,
    Interface,
    PatientQueue,
    run_coupled,
)


def test_the_interface_names_what_crosses_and_in_what_unit() -> None:
    face = Interface()
    assert face.unit_of("servers") == "clinicians"
    assert face.unit_of("mean_wait") == "hours"
    with pytest.raises(KeyError):
        face.unit_of("staff_morale")


def test_a_payload_carrying_the_wrong_fields_is_refused() -> None:
    """The boundary is a contract, so an undeclared variable cannot sneak across."""
    face = Interface()
    face.validate({"servers": 10.0}, "to_queue")
    with pytest.raises(ValueError):
        face.validate({"servers": 10.0, "budget": 5.0}, "to_queue")
    with pytest.raises(ValueError):
        face.validate({"mean_wait": 1.0}, "to_aggregate")


def test_the_coupled_run_produces_a_record_for_both_sides() -> None:
    history = run_coupled(periods=40)
    assert set(history) == {"staff", "mean_wait", "queue_length"}
    assert len(history["staff"]) == 40


def test_staffing_responds_to_waiting_reported_by_the_queue() -> None:
    staffing = AggregateStaffing(staff=10.0)
    staffing.step(mean_wait=2.0)
    assert staffing.staff > 10.0
    calm = AggregateStaffing(staff=10.0)
    calm.step(mean_wait=0.1)
    assert calm.staff < 10.0


def test_a_slower_exchange_leaves_the_aggregate_acting_on_stale_information() -> None:
    """Exchange frequency is a modelling decision, not an implementation detail."""
    fast = run_coupled(periods=60, interface=Interface(exchange_every=1), seed=5)
    slow = run_coupled(periods=60, interface=Interface(exchange_every=8), seed=5)
    assert fast["staff"] != slow["staff"]


def test_the_queue_holds_patients_it_cannot_serve() -> None:
    queue = PatientQueue(arrivals_per_period=9.0, service_time=1.0, seed=1)
    observed = queue.step(servers=2, now=0.0)
    assert observed["queue_length"] > 0.0


def test_both_sides_refuse_impossible_settings() -> None:
    with pytest.raises(ValueError):
        AggregateStaffing(adjustment_time=0.0)
    with pytest.raises(ValueError):
        PatientQueue(arrivals_per_period=1.0, service_time=0.0, seed=1)
    with pytest.raises(ValueError):
        PatientQueue(9.0, 1.0, 1).step(servers=0, now=0.0)
    with pytest.raises(ValueError):
        run_coupled(periods=0)


def test_a_constant_wait_converges_to_a_staffing_level() -> None:
    """Chapter 18 tests each side alone, and the aggregate side has to have an equilibrium."""
    for wait, expected in ((0.75, 15.0), (0.5, 10.0), (0.25, 5.0)):
        staffing = AggregateStaffing()
        for _ in range(200):
            staffing.step(wait)
        assert staffing.staff == pytest.approx(expected, abs=1e-6)


def test_the_exchange_frequency_changes_volatility_not_stability() -> None:
    """Pins the chapter's table: both runs oscillate, the slower exchange swings wider."""
    fast = run_coupled(periods=60, interface=Interface(exchange_every=1), seed=5)["staff"]
    slow = run_coupled(periods=60, interface=Interface(exchange_every=8), seed=5)["staff"]
    assert round(statistics.pstdev(fast), 2) == 1.01
    assert round(statistics.pstdev(slow), 2) == 4.75
    assert max(slow) > max(fast) and min(slow) < min(fast)
    # The band the chapter prints for the fast run, and the ratio it names.
    assert (round(min(fast), 1), round(max(fast), 1)) == (7.9, 13.2)
    assert 4.6 < statistics.pstdev(slow) / statistics.pstdev(fast) < 4.8
