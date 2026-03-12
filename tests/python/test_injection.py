"""Tests for gad.statistical.injection -- SignalInjectionTester."""

import numpy as np
import pyhf
import pytest

from gad.statistical.workspace import WorkspaceBuilder
from gad.statistical.injection import SignalInjectionTester


def _build_test_workspace_spec():
    """Build a simple workspace spec for injection tests."""
    wb = WorkspaceBuilder(poi_name="mu")

    # Signal region: 2 bins (signal large enough for good recovery)
    wb.add_channel("SR", [55.0, 65.0])
    wb.add_sample("SR", "background", [50.0, 60.0])
    wb.add_sample("SR", "signal", [5.0, 5.0])
    wb.add_signal("SR", "signal")

    # Control region: 2 bins
    wb.add_channel("CR", [50.0, 100.0])
    wb.add_sample("CR", "background", [50.0, 100.0])
    wb.add_sample("CR", "signal", [1.0, 1.0])
    wb.add_signal("CR", "signal")

    # A simple normsys
    wb.add_modifier("SR", "background", {
        "name": "bkg_norm",
        "type": "normsys",
        "data": {"hi": 1.05, "lo": 0.95},
    })

    return wb.build()


class TestSignalInjectionTester:
    """Tests for SignalInjectionTester."""

    @pytest.fixture(scope="class")
    def spec(self):
        return _build_test_workspace_spec()

    @pytest.fixture(scope="class")
    def tester(self, spec):
        return SignalInjectionTester(spec)

    # -- test_injection at various mu values ----------------------------------

    def test_injection_at_mu_1_recovers_mu(self, tester):
        result = tester.test_injection(1.0)
        assert abs(result["mu_hat"] - 1.0) < result["sigma_fit"]

    def test_injection_at_mu_05_recovers_mu(self, tester):
        result = tester.test_injection(0.5)
        assert abs(result["mu_hat"] - 0.5) < result["sigma_fit"]

    def test_injection_at_mu_2_recovers_mu(self, tester):
        result = tester.test_injection(2.0)
        assert abs(result["mu_hat"] - 2.0) < result["sigma_fit"]

    # -- run_all returns aggregate result -------------------------------------

    def test_run_all_returns_all_pass_true(self, tester):
        result = tester.run_all()
        assert result["all_pass"] is True

    # -- result structure checks -----------------------------------------------

    def test_result_contains_required_keys(self, tester):
        result = tester.test_injection(1.0)
        for key in ["mu_injected", "mu_hat", "sigma_fit", "pull", "passes"]:
            assert key in result, f"Missing key: {key}"

    def test_pull_is_less_than_1_for_valid_injection(self, tester):
        result = tester.test_injection(1.0)
        assert result["pull"] < 1.0
