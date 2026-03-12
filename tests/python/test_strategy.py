"""Tests for analysis strategy template and renderer.

Covers:
- Template file existence and section completeness
- Placeholder marker presence
- StrategyRenderer rendering and validation
- Error handling for empty physics prompt
"""

import os
import pytest


# ── Template file tests ──────────────────────────────────────────────


TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "templates", "ANALYSIS_STRATEGY_TEMPLATE.md"
)

REQUIRED_SECTIONS = [
    "Executive Summary",
    "Signal Process",
    "Backgrounds",
    "Dataset and Luminosity",
    "Object Definitions",
    "Blinding Protocol",
    "Event Selection Strategy",
    "Categorization Plan",
    "Background Estimation",
    "Systematic Uncertainties",
    "Statistical Approach",
    "Target Sensitivity",
    "Quality Gate Criteria",
]


class TestTemplateFile:
    """Tests for the ANALYSIS_STRATEGY_TEMPLATE.md file."""

    def test_template_exists(self):
        assert os.path.exists(TEMPLATE_PATH), (
            f"Template not found at {TEMPLATE_PATH}"
        )

    def test_template_has_all_13_sections(self):
        with open(TEMPLATE_PATH) as f:
            content = f.read()
        for section in REQUIRED_SECTIONS:
            assert f"## {section}" in content or f"# {section}" in content, (
                f"Missing section header: {section}"
            )

    def test_template_has_placeholder_markers(self):
        with open(TEMPLATE_PATH) as f:
            content = f.read()
        required_placeholders = [
            "{{experiment_name}}",
            "{{signal_process}}",
            "{{sqrt_s}}",
        ]
        for placeholder in required_placeholders:
            assert placeholder in content, (
                f"Missing placeholder: {placeholder}"
            )

    def test_template_has_lead_analyst_markers(self):
        with open(TEMPLATE_PATH) as f:
            content = f.read()
        assert "LEAD_ANALYST" in content, (
            "Template must contain LEAD_ANALYST comment markers"
        )


# ── StrategyRenderer tests ──────────────────────────────────────────


class TestStrategyRenderer:
    """Tests for the StrategyRenderer class."""

    @pytest.fixture
    def renderer(self):
        from gad.strategy.renderer import StrategyRenderer
        return StrategyRenderer(template_path=TEMPLATE_PATH)

    @pytest.fixture
    def mock_ctx(self, mock_experiment_dir):
        """Create a mock ExperimentContext from the fixture."""
        from gad.config.experiment import ExperimentContext
        exp_dir = mock_experiment_dir("test_exp")
        return ExperimentContext("test_exp", experiments_dir=exp_dir)

    def test_render_produces_filled_document(self, renderer, mock_ctx):
        result = renderer.render(
            physics_prompt="Search for Higgs boson in ZZ channel",
            experiment_context=mock_ctx,
        )
        assert isinstance(result, str)
        assert len(result) > 100
        # Experiment name should be filled in
        assert "test_exp" in result

    def test_render_fills_experiment_fields(self, renderer, mock_ctx):
        result = renderer.render(
            physics_prompt="Search for Higgs boson",
            experiment_context=mock_ctx,
        )
        # Detector collider should appear
        assert "TestCollider" in result
        # Object names should appear
        assert "good_track" in result or "good_jet" in result

    def test_rendered_contains_all_13_sections(self, renderer, mock_ctx):
        result = renderer.render(
            physics_prompt="Search for new physics",
            experiment_context=mock_ctx,
        )
        for section in REQUIRED_SECTIONS:
            assert f"## {section}" in result or f"# {section}" in result, (
                f"Rendered doc missing section: {section}"
            )

    def test_rendered_has_quality_gate_criteria(self, renderer, mock_ctx):
        result = renderer.render(
            physics_prompt="Search for new physics",
            experiment_context=mock_ctx,
        )
        # Must have gate transitions from 0->1 through 6->7
        for gate_from in range(7):
            gate_to = gate_from + 1
            assert (
                f"{gate_from}" in result and f"{gate_to}" in result
            ), f"Quality gate {gate_from}->{gate_to} not found"

    def test_validate_rendered_returns_empty_for_valid(self, renderer, mock_ctx):
        rendered = renderer.render(
            physics_prompt="Search for new physics",
            experiment_context=mock_ctx,
        )
        missing = renderer.validate_rendered(rendered)
        assert missing == [], f"Unexpected missing sections: {missing}"

    def test_validate_rendered_detects_missing_sections(self, renderer):
        incomplete = "## Executive Summary\nSome content\n"
        missing = renderer.validate_rendered(incomplete)
        assert len(missing) > 0
        assert "Signal Process" in missing

    def test_render_raises_on_empty_prompt(self, renderer, mock_ctx):
        with pytest.raises(ValueError, match="physics_prompt"):
            renderer.render(physics_prompt="", experiment_context=mock_ctx)

    def test_render_raises_on_none_prompt(self, renderer, mock_ctx):
        with pytest.raises(ValueError, match="physics_prompt"):
            renderer.render(physics_prompt=None, experiment_context=mock_ctx)

    def test_render_without_experiment_context(self, renderer):
        """Renderer should work without experiment context (placeholders stay)."""
        result = renderer.render(
            physics_prompt="Search for new physics",
        )
        assert isinstance(result, str)
        # All 13 sections should still be present
        for section in REQUIRED_SECTIONS:
            assert f"## {section}" in result or f"# {section}" in result

    def test_required_sections_class_attribute(self):
        from gad.strategy.renderer import StrategyRenderer
        assert hasattr(StrategyRenderer, "REQUIRED_SECTIONS")
        assert len(StrategyRenderer.REQUIRED_SECTIONS) == 13
