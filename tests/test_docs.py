from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_book_map_links_first_vertical_slice() -> None:
    content = (ROOT / "docs/book-map.md").read_text(encoding="utf-8")

    assert "FM2" in content
    assert "Chapter 2" in content
    assert "modeling-interview" in content
    assert "models/factory-cycle.yaml" in content
    assert "cases/factory-cycle/policy-proposal.yaml" in content


def test_release_policy_records_public_authorization_and_pins_book_destination() -> None:
    content = (ROOT / "docs/release-policy.md").read_text(encoding="utf-8")

    assert "publisher authorized public repository access" in content.lower()
    assert "QR" in content
    assert "edition tag" in content.lower()
    assert "do not delete or move" in content.lower()
    assert "does not grant an open-source" in content.lower()
