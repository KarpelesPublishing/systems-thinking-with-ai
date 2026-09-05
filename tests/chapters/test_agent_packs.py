import pytest

from chapters.chapter_20_model_document.code.document import ModelDocument, Variable
from chapters.chapter_27_compiler_agent.code.patch import (
    Edit,
    Patch,
    apply_patch,
    review_packet,
    structural_variance,
)
from chapters.chapter_28_critic.code.critic import (
    defect_report,
    dimensional_findings,
    extreme_condition_findings,
    structural_findings,
)
from chapters.chapter_29_experiments.code.sensitivity import (
    Uncertainty,
    metric,
    ranked,
    sample,
    value_per_cost,
)
from chapters.chapter_30_policy_search.code.policies import (
    Bound,
    Policy,
    compare,
    evaluate,
    recommend,
)
from chapters.chapter_31_repository.code.permissions import (
    Request,
    check,
    ci_sequence,
    gate,
    run_ci,
)


def bass() -> ModelDocument:
    return ModelDocument("bass", "1.0.0", horizon=40, variables=[
        Variable("adopters", "stock", "people", value=1.0),
        Variable("total_market", "parameter", "people", value=1000.0),
        Variable("innovation", "parameter", "1/week", value=0.01),
        Variable("imitation", "parameter", "1/week", value=0.30),
        Variable("potential", "auxiliary", "people", "total_market - adopters"),
        Variable("adoption", "flow", "people/week",
                 "(innovation + imitation * adopters / total_market) * potential",
                 target="adopters", sign=1),
    ])


# ---------- Chapter 27 ----------

def test_a_patch_must_be_written_against_the_current_version() -> None:
    patch = Patch("deadbeefdeadbeef", [Edit("remove", "potential", "unused")])
    with pytest.raises(ValueError):
        apply_patch(bass(), patch)


def test_every_edit_carries_its_own_rationale() -> None:
    with pytest.raises(ValueError):
        Edit("remove", "potential", "   ")


def test_a_valid_patch_applies_and_produces_a_diff() -> None:
    document = bass()
    patch = Patch(document.hash(), [
        Edit("add", "churn", "narrative mentions cancellations",
             {"kind": "flow", "unit": "people/week", "equation": "adopters * churn_rate",
              "target": "adopters", "sign": -1}),
        Edit("add", "churn_rate", "rate not stated in the source; assumed",
             {"kind": "parameter", "unit": "1/week", "value": 0.02}),
    ])
    packet = review_packet(document, patch)
    assert packet["applied"] and packet["valid"]
    assert packet["diff"]["added"] == ["churn", "churn_rate"]
    assert "narrative" in packet["rationales"]["churn"]
    # Pinned because Chapter 27 prints both hashes, and a printed hash nobody runs drifts.
    assert packet["hash_before"] == "05bc66d66e9fe2a0"
    assert packet["hash_after"] == "df98c4469c23e4c1"


def test_a_patch_may_touch_each_variable_once() -> None:
    with pytest.raises(ValueError):
        Patch("x", [Edit("change", "a", "r", {"unit": "u"}), Edit("remove", "a", "r")])


def test_two_compilations_of_one_narrative_are_compared_not_merged() -> None:
    a, b = bass(), bass()
    b.variables = b.variables + [Variable("churn_rate", "parameter", "1/week", value=0.02)]
    variance = structural_variance([a, b])
    assert variance["disputed"] == ["churn_rate"]
    assert variance["agreement"] < 1.0


# ---------- Chapter 28 ----------

def test_a_dimensionally_wrong_unit_passes_the_schema_and_fails_the_critic() -> None:
    """The benchmark item: plausible, schema-valid, and dimensionally wrong."""
    document = bass()
    patch = Patch(document.hash(), [Edit("change", "adoption", "benchmark", {"unit": "people"})])
    packet = review_packet(document, patch)
    assert packet["valid"] is True
    broken = apply_patch(document, patch)
    assert any("time base" in f.message for f in dimensional_findings(broken))


def test_the_critic_finds_nothing_structural_in_a_clean_model() -> None:
    assert structural_findings(bass()) == []


def test_an_unread_auxiliary_is_reported() -> None:
    document = bass()
    document.variables.append(Variable("spare", "auxiliary", "people", "adopters * 2"))
    assert any("nothing reads" in f.message for f in structural_findings(document))


def test_an_extreme_start_exposes_behaviour_the_normal_range_hides() -> None:
    findings = extreme_condition_findings(bass(), "adopters")
    assert findings
    assert any("very large" in f.message for f in findings)


def test_the_defect_report_groups_by_category() -> None:
    report = defect_report(dimensional_findings(bass()) + structural_findings(bass()))
    assert all(k in ("structural", "dimensional", "extreme", "regression") for k in report)


# ---------- Chapter 29 ----------

def test_uncertainties_rank_by_effect_on_the_decision_metric() -> None:
    order = [name for name, _ in ranked(bass(), [
        Uncertainty("imitation", 0.10, 0.50),
        Uncertainty("innovation", 0.005, 0.02),
    ], "adopters")]
    assert order[0] == "imitation"


def test_the_ranking_reverses_once_cost_to_measure_is_included() -> None:
    """The biggest uncertainty is not always where to spend."""
    uncertainties = [
        Uncertainty("total_market", 700, 1300, cost_to_reduce=20.0),
        Uncertainty("innovation", 0.005, 0.02, cost_to_reduce=1.0),
    ]
    by_swing = [n for n, _ in ranked(bass(), uncertainties, "adopters")]
    by_value = [n for n, _ in value_per_cost(bass(), uncertainties, "adopters")]
    assert by_swing[0] == "total_market"
    assert by_value[0] == "innovation"


def test_sampling_is_reproducible_from_its_seed() -> None:
    u = [Uncertainty("imitation", 0.1, 0.5)]
    assert sample(bass(), u, "adopters", 5, seed=3) == sample(bass(), u, "adopters", 5, seed=3)


def test_an_inverted_range_is_refused() -> None:
    with pytest.raises(ValueError):
        Uncertainty("x", 5.0, 1.0)


# ---------- Chapter 30 ----------

def policies() -> list[Policy]:
    return [
        Policy("push", {"imitation": 0.55}, "growth lead", reversible=True),
        Policy("hold", {"imitation": 0.15}, "growth lead", reversible=True),
    ]


def three_policies() -> list[Policy]:
    """The three policies Chapter 30 prints a table for."""
    return [
        Policy("push", {"imitation": 0.55}, "growth lead", reversible=True,
               note="referral program at full spend"),
        Policy("steady", {"imitation": 0.35}, "growth lead", reversible=True),
        Policy("hold", {"imitation": 0.15}, "growth lead", reversible=True),
    ]


def test_chapter_30_prints_the_numbers_this_run_produces() -> None:
    """Pins the chapter's table so a change to the pack cannot leave the prose behind."""
    bounds = [Bound("adopters", high=1100.0, reason="support capacity ceiling")]
    evaluations = compare(bass(), three_policies(), [Uncertainty("total_market", 700, 1300)],
                          "adopters", bounds, draws=25, seed=7)
    printed = {e.policy: (round(e.mean(), 1), round(e.worst(), 1)) for e in evaluations}
    assert printed == {"push": (934.1, 722.4), "steady": (911.9, 705.5), "hold": (533.6, 413.6)}
    outcome = recommend(evaluations)
    assert outcome["recommended"] == "hold"
    assert round(outcome["worst_case"], 1) == 413.6
    assert round(outcome["mean"], 1) == 533.6
    assert outcome["excluded"]["push"][0].startswith("adopters=1196 above 1100.0")
    assert outcome["excluded"]["steady"][0].startswith("adopters=1167 above 1100.0")
    assert len(outcome["excluded"]["push"]) == 4


def test_the_highest_mean_policy_can_be_excluded_by_a_constraint() -> None:
    """The chapter's challenge, as a test."""
    bounds = [Bound("adopters", high=1100.0, reason="support capacity ceiling")]
    evaluations = compare(bass(), policies(), [Uncertainty("total_market", 700, 1300)],
                          "adopters", bounds, draws=25, seed=7)
    by_mean = max(evaluations, key=lambda e: e.mean())
    outcome = recommend(evaluations)
    assert by_mean.policy == "push"
    assert outcome["recommended"] == "hold"
    assert "push" in outcome["excluded"]


def test_a_recommendation_names_why_each_excluded_policy_was_excluded() -> None:
    bounds = [Bound("adopters", high=1100.0, reason="support capacity ceiling")]
    outcome = recommend(compare(bass(), policies(), [Uncertainty("total_market", 700, 1300)],
                                "adopters", bounds, draws=25, seed=7))
    assert "capacity ceiling" in outcome["excluded"]["push"][0]


def test_when_everything_violates_there_is_no_recommendation() -> None:
    bounds = [Bound("adopters", high=1.0, reason="impossible")]
    outcome = recommend(compare(bass(), policies(), [Uncertainty("total_market", 700, 1300)],
                                "adopters", bounds, draws=5, seed=1))
    assert outcome["recommended"] is None


def test_a_policy_needs_settings_and_an_owner() -> None:
    with pytest.raises(ValueError):
        Policy("empty", {}, "someone", True)
    with pytest.raises(ValueError):
        Policy("nameless", {"a": 1.0}, "  ", True)


# ---------- Chapter 31 ----------

def test_no_ai_role_may_approve_or_execute() -> None:
    for role in ("interviewer", "compiler", "critic", "experiment_designer", "policy_searcher"):
        assert check(Request(role, "approve", "model")) is not None
        assert check(Request(role, "execute", "model")) is not None


def test_a_human_may_reach_every_stage() -> None:
    assert all(check(Request("human", stage, "model")) is None
               for stage in ("read", "simulate", "propose", "approve", "execute"))


def test_the_interviewer_may_only_read() -> None:
    assert check(Request("interviewer", "read", "notes")) is None
    assert check(Request("interviewer", "simulate", "model")) is not None


def test_denials_are_recorded_rather_than_silently_dropped() -> None:
    allowed, denied = gate([Request("critic", "simulate", "m"), Request("critic", "execute", "m")])
    assert len(allowed) == 1 and len(denied) == 1
    assert "may only" in denied[0].reason


def test_ci_reports_the_first_failing_stage() -> None:
    outcome = run_ci({"schema": True, "semantics": True, "compile": False,
                      "tests": True, "provenance": True, "replay": True})
    assert outcome["failed_at"] == "compile"


def test_ci_requires_a_result_for_every_stage() -> None:
    with pytest.raises(ValueError):
        run_ci({"schema": True})
    assert len(ci_sequence()) == 6


def test_reversibility_breaks_a_tie_between_close_policies() -> None:
    """Chapter 30 and Chapter 40 both say reversibility is the tiebreak."""
    from chapters.chapter_30_policy_search.code.policies import Evaluation, recommend
    a = Evaluation(policy="irreversible", values=[100.0, 100.0], reversible=False)
    b = Evaluation(policy="reversible", values=[99.5, 99.5], reversible=True)
    assert recommend([a, b])["recommended"] == "reversible"


def test_a_clearly_better_policy_still_wins_despite_being_irreversible() -> None:
    from chapters.chapter_30_policy_search.code.policies import Evaluation, recommend
    a = Evaluation(policy="much better", values=[100.0, 100.0], reversible=False)
    b = Evaluation(policy="reversible", values=[50.0, 50.0], reversible=True)
    assert recommend([a, b])["recommended"] == "much better"


def test_a_draw_the_model_cannot_run_is_a_violation_not_a_crash() -> None:
    """A policy whose world the model refuses is inadmissible, not a lost comparison."""
    from chapters.chapter_20_model_document.code.document import ModelDocument, Variable

    # total_market is driven to zero, so potential/total_market divides by zero.
    breakable = ModelDocument("fragile", "1.0.0", horizon=5, variables=[
        Variable("adopters", "stock", "people", value=1.0),
        Variable("total_market", "parameter", "people", value=1000.0),
        Variable("share", "auxiliary", "dimensionless", "adopters / total_market"),
        Variable("adoption", "flow", "people/week", "share", target="adopters", sign=1),
    ])
    evaluation = evaluate(breakable, Policy("zeroed", {"total_market": 0.0}, "owner", True),
                          [Uncertainty("adopters", 1.0, 2.0)], "adopters", [], draws=3, seed=1)
    assert evaluation.values == []
    assert evaluation.violations and "could not be run" in evaluation.violations[0]
    assert not evaluation.admissible()


def test_chapter_11s_rules_now_reach_a_model_document() -> None:
    """`as_system` is the adapter that was missing, so the missing-sink check applies."""
    from chapters.chapter_28_critic.code.critic import as_system, conservation_findings

    document = bass()
    system = as_system(document)
    assert sorted(system.stocks) == ["adopters"]
    assert [f.name for f in system.flows] == ["adoption"]
    # The Bass model has an inflow and no outflow, which is the defect Chapter 27's
    # worked patch repairs by adding churn.
    findings = conservation_findings(document)
    assert [f.variable for f in findings] == ["adopters"]
    assert "can only grow" in findings[0].message


def test_a_model_with_both_directions_passes_the_conservation_check() -> None:
    from chapters.chapter_20_model_document.code.document import Variable
    from chapters.chapter_28_critic.code.critic import conservation_findings

    document = bass()
    document.variables.append(
        Variable("churn_rate", "parameter", "1/week", value=0.02))
    document.variables.append(
        Variable("churn", "flow", "people/week", "adopters * churn_rate",
                 target="adopters", sign=-1))
    assert conservation_findings(document) == []


def test_anything_the_agent_supplies_is_marked_proposed() -> None:
    """The book states this rule three times, so the applier enforces it rather than a prompt."""
    document = bass()
    patch = Patch(document.hash(), [
        Edit("add", "churn", "narrative mentions cancellations",
             {"kind": "flow", "unit": "people/week", "equation": "adopters * churn_rate",
              "target": "adopters", "sign": -1}),
    ])
    applied = apply_patch(document, patch)
    assert applied.by_id("churn").evidence == "proposed"


def test_an_agent_changing_a_number_cannot_leave_it_marked_observed() -> None:
    document = bass()
    document.variables[1] = Variable("total_market", "parameter", "people", value=1000.0,
                                     evidence="observed", note="market study 2026-01")
    patch = Patch(document.hash(), [
        Edit("change", "total_market", "the narrative implies a larger market", {"value": 1500.0}),
    ])
    applied = apply_patch(document, patch)
    assert applied.by_id("total_market").evidence == "proposed"


def test_a_patch_may_state_an_evidence_level_and_it_is_kept() -> None:
    document = bass()
    patch = Patch(document.hash(), [
        Edit("add", "churn_rate", "measured from the churn series",
             {"kind": "parameter", "unit": "1/week", "value": 0.02,
              "evidence": "observed", "note": "billing export 2026-08"}),
    ])
    assert apply_patch(document, patch).by_id("churn_rate").evidence == "observed"


def test_a_comparison_states_its_own_horizon_rather_than_inheriting_one() -> None:
    """A document horizon past saturation would hide the difference the comparison seeks."""
    from chapters.chapter_22_runtime.code.runtime import Runtime

    long_document = ModelDocument("bass", "1.0.0", horizon=200,
                                  variables=list(bass().variables))
    # metric() fixes its own horizon, so a 200-period document does not saturate the answer.
    assert metric(long_document, {"imitation": 0.15}, "adopters") < 700.0
    # Running the document directly does inherit its horizon, and does saturate.
    assert Runtime(long_document).run().final("adopters") > 990.0
