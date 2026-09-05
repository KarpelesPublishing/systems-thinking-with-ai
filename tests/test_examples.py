"""The example models are readers' models. They must keep validating and running."""

import pytest

from chapters.chapter_20_model_document.code.document import validate
from chapters.chapter_21_compiler.code.compiler import diagnostics
from chapters.chapter_22_runtime.code.runtime import RunSettings, Runtime
from examples.hiring_pipeline import hiring_pipeline
from examples.subscription_growth import subscription_growth
from examples.support_desk import support_desk


@pytest.mark.parametrize("document", [
    hiring_pipeline(), support_desk(), subscription_growth(),
])
def test_every_example_validates_and_compiles_clean(document) -> None:
    assert validate(document) == []
    assert diagnostics(document) == []


def test_the_hiring_pipeline_overshoots_its_target() -> None:
    """A delay inside a balancing loop overshoots. That is the point of the model."""
    result = Runtime(hiring_pipeline(), RunSettings("euler", dt=1.0, horizon=52)).run()
    assert max(result.series["productive"]) > 40.0
    assert result.series["productive"][0] == pytest.approx(20.0)


def test_the_desk_needs_headroom_not_parity() -> None:
    """Effectiveness below one means nominal parity with arrivals is not enough."""
    settings = RunSettings("euler", dt=1.0, horizon=40)
    with pytest.raises(RuntimeError):        # 12 staff is exactly 30/week nominal
        Runtime(support_desk(arrivals=30.0, staff=12.0, past_the_evidence=True), settings).run()
    result = Runtime(support_desk(arrivals=30.0, staff=13.0, past_the_evidence=True),
                     settings).run()
    assert result.series["open_tickets"][-1] == pytest.approx(0.0, abs=1e-6)


def test_growth_erodes_the_quality_it_runs_on() -> None:
    """Chapter 32's shape, assembled from the packs through a document."""
    result = Runtime(subscription_growth(), RunSettings("euler", dt=1.0, horizon=60)).run()
    assert result.series["quality"][0] > result.series["quality"][-1]
    assert result.series["load"][-1] > result.series["load"][0]
