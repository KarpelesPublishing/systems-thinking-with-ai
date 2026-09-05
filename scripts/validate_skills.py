from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("modeling-interview", "model-compiler", "model-critic")
ADAPTERS = ("codex.md", "claude-code.md", "generic.md")
REQUIRED_EVALUATION_LIST_KEYS = (
    "required_artifacts",
    "allowed_tools",
    "required_fields",
    "forbidden_actions",
)
REQUIRED_SCENARIOS = {"valid", "malformed", "missing_evidence", "unsafe"}
FORBIDDEN_ACTIONS = {"approve_artifact", "execute_external_action"}


def _load_yaml_mapping(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        return None, str(error)
    if not isinstance(payload, dict):
        return None, "is not a YAML mapping"
    return payload, None


def _nonempty_string_list(payload: dict[str, Any], key: str) -> bool:
    value = payload.get(key)
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and item for item in value
    )


def load_catalog_tool_ids() -> tuple[set[str], list[str]]:
    catalog_path = ROOT / "tooling/catalog.yaml"
    payload, error = _load_yaml_mapping(catalog_path)
    if error is not None or payload is None:
        return set(), [f"tooling: catalog.yaml {error}"]
    tools = payload.get("tools")
    if not isinstance(tools, list):
        return set(), ["tooling: catalog.yaml must define a tools list"]
    tool_ids = {
        item.get("tool_id")
        for item in tools
        if isinstance(item, dict) and isinstance(item.get("tool_id"), str)
    }
    if not tool_ids:
        return set(), ["tooling: catalog.yaml has no valid tool IDs"]
    return tool_ids, []


def validate_skill(skill_name: str, known_tool_ids: set[str]) -> list[str]:
    skill_root = ROOT / "skills" / skill_name
    errors: list[str] = []

    skill_file = skill_root / "SKILL.md"
    if not skill_file.exists():
        errors.append(f"{skill_name}: missing SKILL.md")
    else:
        content = skill_file.read_text(encoding="utf-8")
        has_matching_name = content.startswith(f"---\nname: {skill_name}\n")
        has_discoverable_description = "description: Use when" in content
        if not has_matching_name or not has_discoverable_description:
            errors.append(f"{skill_name}: SKILL.md lacks matching discoverable YAML frontmatter")

    for adapter in ADAPTERS:
        if not (skill_root / "adapters" / adapter).exists():
            errors.append(f"{skill_name}: missing adapter {adapter}")

    evaluations = sorted((skill_root / "evals").glob("*.yaml"))
    if not evaluations:
        errors.append(f"{skill_name}: missing evaluation fixture")
    for evaluation in evaluations:
        payload, error = _load_yaml_mapping(evaluation)
        if error is not None or payload is None:
            errors.append(f"{skill_name}: {evaluation.name} {error}")
            continue
        scenario = payload.get("scenario")
        if not isinstance(scenario, str) or not scenario:
            errors.append(f"{skill_name}: {evaluation.name} lacks nonempty scenario")
        for key in REQUIRED_EVALUATION_LIST_KEYS:
            if not _nonempty_string_list(payload, key):
                errors.append(f"{skill_name}: {evaluation.name} lacks nonempty {key}")
        allowed_tools = payload.get("allowed_tools")
        if isinstance(allowed_tools, list):
            unknown_tools = set(allowed_tools) - known_tool_ids
            if unknown_tools:
                errors.append(
                    f"{skill_name}: {evaluation.name} uses unknown tools {sorted(unknown_tools)}"
                )
        forbidden_actions = payload.get("forbidden_actions")
        if isinstance(forbidden_actions, list):
            missing_actions = FORBIDDEN_ACTIONS - set(forbidden_actions)
            if missing_actions:
                errors.append(
                    f"{skill_name}: {evaluation.name} does not forbid {sorted(missing_actions)}"
                )
    return errors


def main() -> int:
    known_tool_ids, errors = load_catalog_tool_ids()
    errors.extend(error for skill in SKILLS for error in validate_skill(skill, known_tool_ids))
    for adapter in ADAPTERS:
        if not (ROOT / "tooling" / "adapters" / adapter).exists():
            errors.append(f"tooling: missing adapter {adapter}")
    scenarios = set()
    for path in (ROOT / "skills").glob("*/evals/*.yaml"):
        payload, error = _load_yaml_mapping(path)
        if error is not None or payload is None:
            errors.append(f"skills: {path.name} {error}")
            continue
        scenario = payload.get("scenario")
        if isinstance(scenario, str):
            scenarios.add(scenario)
    if scenarios != REQUIRED_SCENARIOS:
        errors.append(
            "skills: evaluation fixtures must cover valid, malformed, missing_evidence, unsafe"
        )
    if errors:
        print("\n".join(errors))
        return 1
    print("Skill packages are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
