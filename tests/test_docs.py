from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_book_map_links_first_vertical_slice() -> None:
    content = (ROOT / "docs/book-map.md").read_text(encoding="utf-8")

    assert "FM2" in content
    assert "Chapter 2" in content
    assert "modeling-interview" in content
    assert "models/factory-cycle.yaml" in content
    assert "cases/factory-cycle/policy-proposal.yaml" in content


def test_release_policy_keeps_repository_private() -> None:
    content = (ROOT / "docs/release-policy.md").read_text(encoding="utf-8")

    assert "private" in content.lower()
    assert "QR" in content
    assert "versioned release" in content.lower()
