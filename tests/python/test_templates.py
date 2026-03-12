"""Tests verifying all Wave 1 report templates have required sections."""

import os
import pytest

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "templates")


def _read_template(name):
    """Read a template file and return its content."""
    path = os.path.join(TEMPLATES_DIR, name)
    assert os.path.exists(path), f"Template {name} not found at {path}"
    with open(path) as f:
        return f.read()


class TestTheoryScout:
    """Verify WAVE1_THEORY_SCOUT.md has all required sections."""

    def setup_method(self):
        self.content = _read_template("WAVE1_THEORY_SCOUT.md")

    def test_template_exists(self):
        path = os.path.join(TEMPLATES_DIR, "WAVE1_THEORY_SCOUT.md")
        assert os.path.exists(path)

    def test_has_literature_review(self):
        assert "## Literature Review" in self.content

    def test_has_signal_cross_sections(self):
        assert "## Signal Cross-Sections" in self.content

    def test_has_existing_limits(self):
        assert "## Existing Limits" in self.content

    def test_has_matrix_element_feasibility(self):
        assert "## Matrix-Element Discriminant Feasibility" in self.content

    def test_has_recommendations(self):
        assert "## Recommendations" in self.content


class TestDataExplorer:
    """Verify WAVE1_DATA_EXPLORER.md has all required sections."""

    def setup_method(self):
        self.content = _read_template("WAVE1_DATA_EXPLORER.md")

    def test_template_exists(self):
        path = os.path.join(TEMPLATES_DIR, "WAVE1_DATA_EXPLORER.md")
        assert os.path.exists(path)

    def test_has_sample_inventory(self):
        assert "## Sample Inventory" in self.content

    def test_has_luminosity_cross_check(self):
        assert "## Luminosity Cross-Check" in self.content

    def test_has_data_quality_report(self):
        assert "## Data Quality Report" in self.content

    def test_has_variable_catalog(self):
        assert "## Variable Catalog" in self.content

    def test_has_warnings_and_blockers(self):
        assert "## Warnings and Blockers" in self.content


class TestDetectorSpecialist:
    """Verify WAVE1_DETECTOR_SPECIALIST.md has all required sections."""

    def setup_method(self):
        self.content = _read_template("WAVE1_DETECTOR_SPECIALIST.md")

    def test_template_exists(self):
        path = os.path.join(TEMPLATES_DIR, "WAVE1_DETECTOR_SPECIALIST.md")
        assert os.path.exists(path)

    def test_has_object_definitions(self):
        assert "## Object Definitions" in self.content

    def test_has_performance_validation(self):
        assert "## Performance Validation" in self.content

    def test_has_scale_factors(self):
        assert "## Scale Factors" in self.content

    def test_has_data_mc_comparisons(self):
        assert "## Data/MC Comparisons" in self.content

    def test_has_recommendations(self):
        assert "## Recommendations" in self.content


class TestWave1Summary:
    """Verify WAVE1_SUMMARY.md has all required sections."""

    def setup_method(self):
        self.content = _read_template("WAVE1_SUMMARY.md")

    def test_template_exists(self):
        path = os.path.join(TEMPLATES_DIR, "WAVE1_SUMMARY.md")
        assert os.path.exists(path)

    def test_has_executive_summary(self):
        assert "## Executive Summary" in self.content

    def test_has_finalized_object_definitions(self):
        assert "## Finalized Object Definitions" in self.content

    def test_has_finalized_mc_sample_list(self):
        assert "## Finalized MC Sample List" in self.content

    def test_has_cross_check_notes(self):
        assert "## Cross-Check Notes" in self.content

    def test_has_data_quality_summary(self):
        assert "## Data Quality Summary" in self.content

    def test_has_theory_context(self):
        assert "## Theory Context" in self.content

    def test_has_wave2_recommendations(self):
        assert "## Wave 2 Recommendations" in self.content

    def test_has_gate_evaluation(self):
        assert "## Gate 1->2 Evaluation" in self.content
