"""Tests for PostUnblindingClassifier.

Tests cover:
- Category A/B/C classification
- Persistence of problems to STATE.md frontmatter
- Invalid category rejection
- Retrieval of all problems
"""

import yaml
import pytest

from gad.statistical.classifier import PostUnblindingClassifier


@pytest.fixture
def state_md(tmp_path):
    """Create a temporary STATE.md for classifier tests."""
    def _create(problems=None):
        state_file = tmp_path / "STATE.md"
        fm = {
            "gsd_state_version": 1.0,
            "blinding_status": "unblinded",
            "reblind_count": 0,
        }
        if problems is not None:
            fm["post_unblinding_problems"] = problems
        fm_text = yaml.dump(fm, default_flow_style=False).strip()
        content = f"---\n{fm_text}\n---\n\n# Project State\n"
        state_file.write_text(content)
        return str(state_file)
    return _create


class TestPostUnblindingClassifier:
    """Tests for PostUnblindingClassifier."""

    def test_classify_category_a(self, state_md):
        """classify returns problem with category='A'."""
        clf = PostUnblindingClassifier(state_md())
        result = clf.classify("Large deviation in SR", "A")
        assert result["category"] == "A"
        assert result["description"] == "Large deviation in SR"

    def test_classify_category_b(self, state_md):
        """classify returns problem with category='B'."""
        clf = PostUnblindingClassifier(state_md())
        result = clf.classify("Moderate deviation", "B")
        assert result["category"] == "B"

    def test_classify_category_c(self, state_md):
        """classify returns problem with category='C'."""
        clf = PostUnblindingClassifier(state_md())
        result = clf.classify("Minor issue in fit", "C")
        assert result["category"] == "C"

    def test_classify_persists_to_state(self, state_md):
        """After classify(), STATE.md frontmatter contains post_unblinding_problems list."""
        path = state_md()
        clf = PostUnblindingClassifier(path)
        clf.classify("Test problem", "A", resolution="Investigate")

        content = open(path).read()
        end_idx = content.index("---", 3)
        fm = yaml.safe_load(content[3:end_idx])
        assert "post_unblinding_problems" in fm
        assert len(fm["post_unblinding_problems"]) == 1
        assert fm["post_unblinding_problems"][0]["category"] == "A"
        assert fm["post_unblinding_problems"][0]["resolution"] == "Investigate"

    def test_classify_invalid_category_raises(self, state_md):
        """Category not in A/B/C raises ValueError."""
        clf = PostUnblindingClassifier(state_md())
        with pytest.raises(ValueError, match="Invalid category"):
            clf.classify("Bad category", "D")

    def test_get_problems_returns_all(self, state_md):
        """After multiple classifications, get_problems() returns all."""
        path = state_md()
        clf = PostUnblindingClassifier(path)
        clf.classify("Problem 1", "A")
        clf.classify("Problem 2", "B")
        clf.classify("Problem 3", "C")

        problems = clf.get_problems()
        assert len(problems) == 3
        categories = [p["category"] for p in problems]
        assert "A" in categories
        assert "B" in categories
        assert "C" in categories
