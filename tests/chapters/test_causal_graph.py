import pytest

from chapters.chapter_08_causal_graph.code.graph import (
    Link,
    audit,
    find_loops,
    links_without_time_semantics,
    loop_polarity,
    unsupported_links,
)

FACTORY = [
    Link("backlog", "production", 1, "observed", True),
    Link("production", "backlog", -1, "observed", True),
    Link("production", "inventory", 1, "observed", True),
    Link("inventory", "production", -1, "inferred", True),
]


def test_a_two_link_correction_loop_is_balancing() -> None:
    assert loop_polarity(["backlog", "production"], FACTORY) == "balancing"


def test_a_loop_with_no_negative_links_is_reinforcing() -> None:
    growth = [
        Link("adopters", "word of mouth", 1, "inferred", False),
        Link("word of mouth", "adopters", 1, "inferred", True),
    ]
    assert loop_polarity(["adopters", "word of mouth"], growth) == "reinforcing"


def test_two_negatives_make_a_loop_reinforcing_again() -> None:
    """Polarity counts negatives, so intuition about 'two bad things' fails here.

    Overtime and morale, not price and demand: price to demand is negative but
    demand to price is positive, so that pair is one negative and balances.
    """
    pair = [
        Link("overtime", "morale", -1, "inferred", False),
        Link("morale", "overtime", -1, "inferred", True),
    ]
    assert loop_polarity(["overtime", "morale"], pair) == "reinforcing"


def test_the_price_demand_pair_is_balancing_not_reinforcing() -> None:
    """The example the chapter used to get wrong, kept as a guard."""
    pair = [
        Link("price", "demand", -1, "inferred", False),
        Link("demand", "price", 1, "inferred", True),
    ]
    assert loop_polarity(["price", "demand"], pair) == "balancing"


def test_every_loop_is_found_once_rather_than_once_per_rotation() -> None:
    loops = find_loops(FACTORY)
    assert len(loops) == 2
    assert sorted(sorted(loop) for loop in loops) == [
        ["backlog", "production"],
        ["inventory", "production"],
    ]


def test_links_resting_on_assumption_are_reported() -> None:
    links = FACTORY + [Link("inventory", "shipments", 1, "assumed", False)]
    assert [link.target for link in unsupported_links(links)] == ["shipments"]


def test_links_with_no_recorded_time_semantics_are_reported() -> None:
    links = FACTORY + [Link("inventory", "shipments", 1, "observed")]
    flagged = links_without_time_semantics(links)
    assert len(flagged) == 1
    assert flagged[0].delayed is None


def test_the_audit_summarizes_what_the_diagram_rests_on() -> None:
    links = FACTORY + [
        Link("inventory", "shipments", 1, "assumed"),
        Link("shipments", "inventory", -1, "proposed"),
    ]
    summary = audit(links)
    assert summary["links"] == 6
    assert summary["loops"] == 3
    assert summary["unsupported"] == 2
    assert summary["no_time_semantics"] == 2


def test_impossible_links_are_rejected() -> None:
    with pytest.raises(ValueError):
        Link("a", "b", 0, "observed")
    with pytest.raises(ValueError):
        Link("a", "b", 1, "obvious")
    with pytest.raises(ValueError):
        Link("a", "a", 1, "observed")


def test_polarity_of_a_loop_with_a_missing_link_is_an_error_not_a_guess() -> None:
    with pytest.raises(ValueError):
        loop_polarity(["backlog", "inventory"], FACTORY)
