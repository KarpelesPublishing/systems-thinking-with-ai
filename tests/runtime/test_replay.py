import pytest

from stai.provenance.replay import canonical_hash, create_replay_record


def test_equivalent_payloads_have_identical_hashes() -> None:
    first = create_replay_record(
        model_payload={"model_id": "factory-cycle", "parameters": {"order_rate": 10.0}},
        experiment_payload={"experiment_id": "baseline", "horizon": 24.0},
        result_payload={"rows": [{"time": 0.0, "inventory": 12.0}]},
    )
    second = create_replay_record(
        model_payload={"parameters": {"order_rate": 10.0}, "model_id": "factory-cycle"},
        experiment_payload={"horizon": 24.0, "experiment_id": "baseline"},
        result_payload={"rows": [{"inventory": 12.0, "time": 0.0}]},
    )

    assert first.model_hash == second.model_hash
    assert first.input_hash == second.input_hash
    assert first.result_hash == second.result_hash


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_replay_hash_rejects_nonfinite_payload_values(value: float) -> None:
    with pytest.raises(ValueError, match="canonical"):
        canonical_hash({"value": value})


def test_replay_hash_rejects_non_string_mapping_keys() -> None:
    with pytest.raises(ValueError, match="keys"):
        canonical_hash({1: "value"})
    with pytest.raises(ValueError, match="keys"):
        canonical_hash({"nested": {1: "value"}})


def test_replay_hash_rejects_cyclic_payloads_with_a_canonical_error() -> None:
    cyclic_payload: list[object] = []
    cyclic_payload.append(cyclic_payload)

    with pytest.raises(ValueError, match="cycle"):
        canonical_hash({"cycle": cyclic_payload})
