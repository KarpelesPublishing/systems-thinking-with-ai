from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_evaluation_fixtures_cover_required_safety_scenarios() -> None:
    scenarios = set()
    for fixture in (ROOT / "skills").glob("*/evals/*.yaml"):
        payload = yaml.safe_load(fixture.read_text(encoding="utf-8"))
        scenarios.add(payload["scenario"])
        assert payload["required_artifacts"]
        assert payload["allowed_tools"]
        assert "execute_external_action" in payload["forbidden_actions"]

    assert scenarios == {"valid", "malformed", "missing_evidence", "unsafe"}
