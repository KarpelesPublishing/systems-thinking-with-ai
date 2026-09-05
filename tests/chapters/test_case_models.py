import pytest

from chapters.chapter_32_service_growth.code.growth import (
    Policy as GrowthPolicy,
)
from chapters.chapter_32_service_growth.code.growth import (
    State as GrowthState,
)
from chapters.chapter_32_service_growth.code.growth import (
    effective_capacity,
    load,
)
from chapters.chapter_32_service_growth.code.growth import (
    run as run_growth,
)
from chapters.chapter_32_service_growth.code.growth import (
    summary as growth_summary,
)
from chapters.chapter_33_technical_debt.code.debt import (
    Policy as DebtPolicy,
)
from chapters.chapter_33_technical_debt.code.debt import (
    available_capacity,
    observable_measures,
)
from chapters.chapter_33_technical_debt.code.debt import (
    run as run_debt,
)
from chapters.chapter_33_technical_debt.code.debt import (
    summary as debt_summary,
)
from chapters.chapter_34_hospital_hybrid.code.hospital import (
    StaffingPolicy,
    equity_gap,
    prohibited_objectives,
)
from chapters.chapter_34_hospital_hybrid.code.hospital import (
    run as run_hospital,
)

STRESSED = {"intake_rate": 0.25, "churn_sensitivity": 1.2}


# ---------- Chapter 32 ----------

def test_slow_hiring_turns_growth_into_collapse() -> None:
    """Peak 185, final 22. The business destroyed the capacity that produced it."""
    policy = GrowthPolicy(**STRESSED, hiring_aggression=0.10)
    result = growth_summary(run_growth(policy, 80), policy)
    assert result["peak_customers"] > 150
    assert result["final_customers"] < result["peak_customers"] / 4


def test_faster_hiring_on_the_same_intake_holds_the_business() -> None:
    """Same growth policy. Only the hiring speed changed."""
    policy = GrowthPolicy(**STRESSED, hiring_aggression=0.25)
    result = growth_summary(run_growth(policy, 80), policy)
    assert result["final_customers"] > 150


def test_throttling_intake_does_not_rescue_it() -> None:
    """The intuitive fix. It cuts inflow while churn continues, and ends lower."""
    loose = GrowthPolicy(**STRESSED, hiring_aggression=0.10, quality_floor=0.0)
    tight = GrowthPolicy(**STRESSED, hiring_aggression=0.10, quality_floor=0.70)
    assert (growth_summary(run_growth(tight, 80), tight)["final_customers"]
            < growth_summary(run_growth(loose, 80), loose)["final_customers"])


def test_capacity_counts_experience_not_heads() -> None:
    green = GrowthState(workforce=10.0, experience=2.0)
    seasoned = GrowthState(workforce=10.0, experience=40.0)
    policy = GrowthPolicy()
    assert effective_capacity(green, policy) < effective_capacity(seasoned, policy)


def test_load_is_undefined_without_capacity() -> None:
    assert load(GrowthState(workforce=0.0, experience=0.0), GrowthPolicy()) == float("inf")


# ---------- Chapter 33 ----------

def test_pushing_hard_wins_the_first_quarter_and_loses_the_year() -> None:
    """100.1 features by period 12 against 87.2, then 230 against 319."""
    hard = DebtPolicy(feature_pressure=1.0, repayment_share=0.0)
    repay = DebtPolicy(feature_pressure=1.0, repayment_share=0.20)
    a, b = debt_summary(run_debt(hard), hard), debt_summary(run_debt(repay), repay)
    assert a["features_by_12"] > b["features_by_12"]
    assert a["features_total"] < b["features_total"]


def test_debt_consumes_the_capacity_that_would_repay_it() -> None:
    hard = DebtPolicy(feature_pressure=1.0, repayment_share=0.0)
    path = run_debt(hard)
    assert available_capacity(path[-1], hard) < available_capacity(path[0], hard)


def test_repayment_leaves_more_capacity_at_the_end() -> None:
    hard = DebtPolicy(repayment_share=0.0)
    repay = DebtPolicy(repayment_share=0.20)
    assert (debt_summary(run_debt(repay), repay)["final_capacity"]
            > debt_summary(run_debt(hard), hard)["final_capacity"])


def test_the_model_says_which_measures_are_proxies() -> None:
    measures = observable_measures()
    assert measures["defects"].startswith("observable")
    assert measures["debt"].startswith("PROXY")


# ---------- Chapter 34 ----------

def test_shortest_first_improves_the_average_and_abandons_the_complex_group() -> None:
    """The equity failure, as a test: gap 1.05 becomes 6.29."""
    fifo = run_hospital(StaffingPolicy(priority="fifo"))
    greedy = run_hospital(StaffingPolicy(priority="shortest_first"))
    assert greedy["mean_by_group"]["routine"] < fifo["mean_by_group"]["routine"]
    assert greedy["mean_by_group"]["complex"] > fifo["mean_by_group"]["complex"] * 3
    assert equity_gap(greedy) > equity_gap(fifo) * 3


def test_the_greedy_policy_leaves_patients_unserved() -> None:
    assert run_hospital(StaffingPolicy(priority="shortest_first"))["queue_left"] > 0
    assert run_hospital(StaffingPolicy(priority="fifo"))["queue_left"] == 0


def test_outcomes_are_reported_per_group_not_only_in_total() -> None:
    outcome = run_hospital(StaffingPolicy())
    assert set(outcome["mean_by_group"]) == {"routine", "complex"}
    assert set(outcome["p90_by_group"]) == {"routine", "complex"}


def test_the_model_names_the_objectives_it_must_not_be_optimized_against() -> None:
    prohibited = prohibited_objectives()
    assert any("mean wait alone" in p for p in prohibited)
    assert any("subgroup constraint" in p for p in prohibited)


def test_group_shares_must_sum_to_one() -> None:
    from chapters.chapter_34_hospital_hybrid.code.hospital import Group
    with pytest.raises(ValueError):
        run_hospital(StaffingPolicy(), groups=(Group("a", 0.5, 1.0), Group("b", 0.2, 1.0)))


def test_the_run_is_reproducible_from_its_seed() -> None:
    assert (run_hospital(StaffingPolicy(), seed=3)["mean_by_group"]
            == run_hospital(StaffingPolicy(), seed=3)["mean_by_group"])


def test_chapter_33_prints_the_numbers_this_run_produces() -> None:
    """Pins the opening table and the repayment sweep the prose describes."""
    hard, repay = DebtPolicy(repayment_share=0.0), DebtPolicy(repayment_share=0.20)
    path_hard, path_repay = run_debt(hard, 60), run_debt(repay, 60)
    assert round(path_hard[12].features_done, 1) == 100.1
    assert round(path_repay[12].features_done, 1) == 87.2
    assert round(path_hard[-1].features_done, 1) == 230.1
    assert round(path_repay[-1].features_done, 1) == 319.0
    assert round(available_capacity(path_hard[-1], hard), 2) == 6.31
    assert round(available_capacity(path_repay[-1], repay), 2) == 8.11
    # The crossover the chapter names, and the flat band of the sweep.
    assert path_hard[24].features_done > path_repay[24].features_done
    assert path_repay[26].features_done > path_hard[26].features_done
    sweep = {s: run_debt(DebtPolicy(repayment_share=s), 60)[-1].features_done
             for s in (0.10, 0.25, 0.35, 0.40)}
    best = max(sweep.values())
    assert all(v >= 0.9 * best for s, v in sweep.items() if s >= 0.25)
    assert sweep[0.10] < 0.8 * best


def test_chapter_32_collapses_by_damped_oscillation_not_a_straight_line() -> None:
    """The chapter now describes repeated rallies of shrinking amplitude, so pin them."""
    path = run_growth(GrowthPolicy(intake_rate=0.25, churn_sensitivity=1.2,
                                   hiring_aggression=0.10), 80)
    customers = [state.customers for state in path]
    turns = [i for i in range(1, len(customers) - 1)
             if (customers[i] - customers[i - 1]) * (customers[i + 1] - customers[i]) < 0]
    peaks = [round(customers[i], 1) for i in turns if customers[i] > customers[i - 1]]
    troughs = [round(customers[i], 1) for i in turns if customers[i] < customers[i - 1]]
    assert peaks[:5] == [185.5, 145.7, 119.4, 100.5, 83.2]
    assert troughs[:5] == [92.2, 79.9, 66.8, 54.2, 44.8]
    # Both envelopes close monotonically, which is what makes each rally smaller.
    assert peaks[:5] == sorted(peaks[:5], reverse=True)
    assert troughs[:5] == sorted(troughs[:5], reverse=True)
    assert round(customers[-1], 1) == 22.3
