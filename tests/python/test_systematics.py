"""Tests for gad.systematics -- evaluator and pruner."""

import numpy as np
import pytest

from gad.systematics.evaluator import SystematicEvaluator
from gad.systematics.pruner import SystematicPruner


class TestSystematicEvaluator:
    """Tests for SystematicEvaluator."""

    def setup_method(self):
        self.evaluator = SystematicEvaluator()

    # -- evaluate_weight_variation -------------------------------------------

    def test_weight_variation_returns_correct_keys(self):
        nominal = {"bin_edges": [0, 1, 2], "yields": [10.0, 20.0], "errors": [1.0, 2.0]}
        values = np.array([0.5, 0.5, 1.5, 1.5, 1.5])
        up_w = np.array([2.0, 2.0, 2.0, 2.0, 2.0])
        down_w = np.array([0.5, 0.5, 0.5, 0.5, 0.5])
        result = self.evaluator.evaluate_weight_variation(
            nominal, up_w, down_w, values, nominal["bin_edges"]
        )
        assert "up_yields" in result
        assert "down_yields" in result
        assert "nominal_yields" in result
        assert result["type"] == "histosys"

    def test_weight_variation_rehistograms_with_weights(self):
        nominal = {"bin_edges": [0, 1, 2], "yields": [2.0, 3.0], "errors": [1.0, 1.0]}
        values = np.array([0.5, 0.5, 1.5, 1.5, 1.5])
        up_w = np.array([3.0, 3.0, 3.0, 3.0, 3.0])
        down_w = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
        result = self.evaluator.evaluate_weight_variation(
            nominal, up_w, down_w, values, nominal["bin_edges"]
        )
        # up: bin0 = 3+3=6, bin1 = 3+3+3=9
        np.testing.assert_allclose(result["up_yields"], [6.0, 9.0])
        # down: bin0 = 1+1=2, bin1 = 1+1+1=3
        np.testing.assert_allclose(result["down_yields"], [2.0, 3.0])

    def test_weight_variation_clips_negative_yields(self):
        nominal = {"bin_edges": [0, 1, 2], "yields": [1.0, 1.0], "errors": [1.0, 1.0]}
        values = np.array([0.5, 1.5])
        up_w = np.array([-5.0, 2.0])
        down_w = np.array([1.0, -3.0])
        result = self.evaluator.evaluate_weight_variation(
            nominal, up_w, down_w, values, nominal["bin_edges"]
        )
        assert result["up_yields"][0] == pytest.approx(1e-6)
        assert result["down_yields"][1] == pytest.approx(1e-6)

    # -- evaluate_shape_variation --------------------------------------------

    def test_shape_variation_extracts_yields(self):
        nominal = {"bin_edges": [0, 1, 2], "yields": [10.0, 20.0], "errors": [1.0, 2.0]}
        up_tmpl = {"bin_edges": [0, 1, 2], "yields": [12.0, 22.0], "errors": [1.1, 2.1]}
        down_tmpl = {"bin_edges": [0, 1, 2], "yields": [8.0, 18.0], "errors": [0.9, 1.9]}
        result = self.evaluator.evaluate_shape_variation(nominal, up_tmpl, down_tmpl)
        np.testing.assert_allclose(result["up_yields"], [12.0, 22.0])
        np.testing.assert_allclose(result["down_yields"], [8.0, 18.0])
        np.testing.assert_allclose(result["nominal_yields"], [10.0, 20.0])
        assert result["type"] == "histosys"

    def test_shape_variation_clips_negatives(self):
        nominal = {"bin_edges": [0, 1], "yields": [5.0], "errors": [1.0]}
        up_tmpl = {"bin_edges": [0, 1], "yields": [-1.0], "errors": [1.0]}
        down_tmpl = {"bin_edges": [0, 1], "yields": [3.0], "errors": [1.0]}
        result = self.evaluator.evaluate_shape_variation(nominal, up_tmpl, down_tmpl)
        assert result["up_yields"][0] == pytest.approx(1e-6)

    # -- evaluate_normalization ----------------------------------------------

    def test_normalization_returns_normsys(self):
        result = self.evaluator.evaluate_normalization(100.0, 1.05, 0.95)
        assert result["type"] == "normsys"
        assert result["hi"] == pytest.approx(1.05)
        assert result["lo"] == pytest.approx(0.95)

    # -- make_modifier -------------------------------------------------------

    def test_make_modifier_histosys(self):
        eval_result = {
            "type": "histosys",
            "up_yields": [12.0, 22.0],
            "down_yields": [8.0, 18.0],
        }
        mod = self.evaluator.make_modifier("JES", eval_result)
        assert mod["name"] == "JES"
        assert mod["type"] == "histosys"
        assert mod["data"]["hi_data"] == [12.0, 22.0]
        assert mod["data"]["lo_data"] == [8.0, 18.0]

    def test_make_modifier_normsys(self):
        eval_result = {"type": "normsys", "hi": 1.05, "lo": 0.95}
        mod = self.evaluator.make_modifier("lumi", eval_result)
        assert mod["name"] == "lumi"
        assert mod["type"] == "normsys"
        assert mod["data"]["hi"] == 1.05
        assert mod["data"]["lo"] == 0.95

    # -- build_modifier_name -------------------------------------------------

    def test_modifier_name_correlated(self):
        name = self.evaluator.build_modifier_name("JES", process="qqbar", correlated=True)
        assert name == "JES"

    def test_modifier_name_uncorrelated(self):
        name = self.evaluator.build_modifier_name("ISR", process="qqbar", correlated=False)
        assert name == "ISR_qqbar"

    def test_modifier_name_correlated_default(self):
        name = self.evaluator.build_modifier_name("JER")
        assert name == "JER"


class TestSystematicPruner:
    """Tests for SystematicPruner."""

    def setup_method(self):
        self.pruner = SystematicPruner(threshold=0.005)

    # -- should_keep ---------------------------------------------------------

    def test_should_keep_large_effect(self):
        """Systematic with 10% effect should be kept."""
        nominal = [100.0, 200.0]
        up = [110.0, 220.0]  # 10% effect
        down = [90.0, 180.0]
        assert self.pruner.should_keep(nominal, up, down) is True

    def test_should_keep_small_effect(self):
        """Systematic with 0.1% effect should be pruned."""
        nominal = [100.0, 200.0]
        up = [100.1, 200.2]  # 0.1% effect
        down = [99.9, 199.8]
        assert self.pruner.should_keep(nominal, up, down) is False

    def test_should_keep_checks_both_directions(self):
        """Keep if only down variation exceeds threshold."""
        nominal = [100.0, 200.0]
        up = [100.0, 200.0]  # no effect
        down = [90.0, 200.0]  # 10% effect in bin 0
        assert self.pruner.should_keep(nominal, up, down) is True

    def test_should_keep_skips_zero_nominal(self):
        """Skip bins where nominal <= 0 to avoid division by zero."""
        nominal = [0.0, 100.0]
        up = [5.0, 100.1]  # bin 0 nominal is 0, bin 1 has 0.1%
        down = [0.0, 99.9]
        assert self.pruner.should_keep(nominal, up, down) is False

    def test_should_keep_at_threshold_boundary(self):
        """Exactly at threshold (0.5%) should NOT be kept (strict >)."""
        nominal = [100.0]
        up = [100.5]  # exactly 0.5%
        down = [99.5]
        assert self.pruner.should_keep(nominal, up, down) is False

    def test_should_keep_above_threshold(self):
        """Just above threshold should be kept."""
        nominal = [100.0]
        up = [100.6]  # 0.6% > 0.5%
        down = [99.5]
        assert self.pruner.should_keep(nominal, up, down) is True

    # -- prune_systematics ---------------------------------------------------

    def test_prune_systematics_filters_correctly(self):
        evaluations = [
            {"name": "JES", "up_yields": [110.0], "down_yields": [90.0],
             "nominal_yields": [100.0]},
            {"name": "tiny", "up_yields": [100.01], "down_yields": [99.99],
             "nominal_yields": [100.0]},
            {"name": "JER", "up_yields": [105.0], "down_yields": [95.0],
             "nominal_yields": [100.0]},
        ]
        result = self.pruner.prune_systematics(evaluations)
        kept_names = [e["name"] for e in result["kept"]]
        assert "JES" in kept_names
        assert "JER" in kept_names
        assert "tiny" not in kept_names
        assert "tiny" in result["pruned"]

    def test_prune_systematics_summary(self):
        evaluations = [
            {"name": "JES", "up_yields": [110.0], "down_yields": [90.0],
             "nominal_yields": [100.0]},
            {"name": "tiny", "up_yields": [100.01], "down_yields": [99.99],
             "nominal_yields": [100.0]},
        ]
        result = self.pruner.prune_systematics(evaluations)
        assert result["summary"]["n_total"] == 2
        assert result["summary"]["n_kept"] == 1
        assert result["summary"]["n_pruned"] == 1
        assert result["summary"]["threshold"] == 0.005

    def test_prune_systematics_empty_list(self):
        result = self.pruner.prune_systematics([])
        assert result["kept"] == []
        assert result["pruned"] == []
        assert result["summary"]["n_total"] == 0

    def test_custom_threshold(self):
        """Pruner with 10% threshold should prune 5% effect."""
        pruner = SystematicPruner(threshold=0.10)
        nominal = [100.0]
        up = [105.0]  # 5% < 10% threshold
        down = [95.0]
        assert pruner.should_keep(nominal, up, down) is False
