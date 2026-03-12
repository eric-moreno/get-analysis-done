"""Tests for gad.selection module: engine, variables, cutflow, and plots."""

import numpy as np
import awkward as ak
import pytest


# ---------------------------------------------------------------------------
# Task 1 tests: SelectionEngine and VariableStudy
# ---------------------------------------------------------------------------

class TestSelectionEngine:
    """Tests for SelectionEngine cut application and cutflow tracking."""

    def _make_events(self):
        """Create synthetic events for testing."""
        return ak.Array({
            "pt": [10.0, 20.0, 30.0, 40.0, 50.0],
            "eta": [0.1, 0.5, 1.2, 2.5, 3.0],
            "mass": [5.0, 15.0, 25.0, 35.0, 45.0],
        })

    def test_add_cut_registers(self):
        from gad.selection.engine import SelectionEngine
        eng = SelectionEngine("test")
        eng.add_cut("pt_cut", "pt", ">", 20.0)
        assert len(eng._cuts) == 1
        assert eng._cuts[0]["name"] == "pt_cut"

    def test_apply_single_cut(self):
        from gad.selection.engine import SelectionEngine
        eng = SelectionEngine()
        eng.add_cut("pt_cut", "pt", ">", 20.0)
        events = self._make_events()
        result = eng.apply(events)
        assert len(result) == 3  # 30, 40, 50

    def test_apply_multiple_cuts(self):
        from gad.selection.engine import SelectionEngine
        eng = SelectionEngine()
        eng.add_cut("pt_cut", "pt", ">", 15.0)
        eng.add_cut("eta_cut", "eta", "<", 2.0)
        events = self._make_events()
        result = eng.apply(events)
        # pt > 15 -> [20,30,40,50], eta < 2 -> [20(0.5), 30(1.2)]
        assert len(result) == 2

    def test_cutflow_tracking(self):
        from gad.selection.engine import SelectionEngine
        eng = SelectionEngine()
        eng.add_cut("pt_cut", "pt", ">", 20.0)
        events = self._make_events()
        eng.apply(events)
        cf = eng.get_cutflow()
        assert len(cf) == 1
        assert cf[0]["name"] == "pt_cut"
        assert cf[0]["n_before"] == 5
        assert cf[0]["n_after"] == 3
        assert cf[0]["eff_relative"] == pytest.approx(3 / 5)
        assert cf[0]["eff_absolute"] == pytest.approx(3 / 5)

    def test_cutflow_absolute_efficiency(self):
        from gad.selection.engine import SelectionEngine
        eng = SelectionEngine()
        eng.add_cut("pt_cut", "pt", ">", 15.0)
        eng.add_cut("eta_cut", "eta", "<", 2.0)
        events = self._make_events()
        eng.apply(events)
        cf = eng.get_cutflow()
        assert cf[1]["eff_absolute"] == pytest.approx(2 / 5)
        assert cf[1]["eff_relative"] == pytest.approx(2 / 4)

    def test_absolute_flag(self):
        """Test absolute=True takes abs(values) before comparison."""
        from gad.selection.engine import SelectionEngine
        eng = SelectionEngine()
        events = ak.Array({"eta": [-2.5, -0.5, 0.5, 2.5, 3.0]})
        eng.add_cut("eta_abs", "eta", "<", 2.6, absolute=True)
        result = eng.apply(events)
        # abs(eta) < 2.6 -> [-2.5, -0.5, 0.5, 2.5] (3.0 fails)
        assert len(result) == 4

    def test_weighted_yields(self):
        from gad.selection.engine import SelectionEngine
        eng = SelectionEngine()
        eng.add_cut("pt_cut", "pt", ">", 20.0)
        events = self._make_events()
        weights = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        eng.apply(events, weights=weights)
        cf = eng.get_cutflow()
        # Events passing: index 2,3,4 -> weights 3,4,5 = 12.0
        assert cf[0]["weighted_yield"] == pytest.approx(12.0)

    def test_empty_events(self):
        from gad.selection.engine import SelectionEngine
        eng = SelectionEngine()
        eng.add_cut("pt_cut", "pt", ">", 20.0)
        events = ak.Array({"pt": []})
        result = eng.apply(events)
        assert len(result) == 0
        cf = eng.get_cutflow()
        assert cf[0]["n_before"] == 0
        assert cf[0]["n_after"] == 0

    def test_all_operators(self):
        from gad.selection.engine import SelectionEngine
        events = ak.Array({"x": [1.0, 2.0, 3.0, 4.0, 5.0]})
        for op, thresh, expected_len in [
            (">", 3.0, 2), (">=", 3.0, 3), ("<", 3.0, 2),
            ("<=", 3.0, 3), ("==", 3.0, 1), ("!=", 3.0, 4),
        ]:
            eng = SelectionEngine()
            eng.add_cut("test", "x", op, thresh)
            result = eng.apply(events)
            assert len(result) == expected_len, f"Failed for op={op}"

    def test_reset_clears_cutflow_not_cuts(self):
        from gad.selection.engine import SelectionEngine
        eng = SelectionEngine()
        eng.add_cut("pt_cut", "pt", ">", 20.0)
        events = self._make_events()
        eng.apply(events)
        assert len(eng.get_cutflow()) == 1
        eng.reset()
        assert len(eng.get_cutflow()) == 0
        assert len(eng._cuts) == 1  # cuts preserved


class TestVariableStudy:
    """Tests for study_variable_separation."""

    def test_known_separation(self):
        """Variables drawn from different distributions should show separation."""
        from gad.selection.variables import study_variable_separation
        rng = np.random.RandomState(42)
        signal = ak.Array({
            "x": rng.normal(5.0, 1.0, 500),
            "y": rng.normal(0.0, 1.0, 500),
        })
        background = ak.Array({
            "x": rng.normal(0.0, 1.0, 500),
            "y": rng.normal(0.0, 1.0, 500),
        })
        results = study_variable_separation(signal, background, ["x", "y"])
        assert len(results) == 2
        # x has separation, y does not
        assert results[0]["variable"] == "x"
        assert results[0]["ks_distance"] > 0.3
        assert results[0]["roc_auc"] >= 0.5

    def test_identical_distributions(self):
        """Identical distributions should have near-zero KS distance."""
        from gad.selection.variables import study_variable_separation
        rng = np.random.RandomState(42)
        vals = rng.normal(0.0, 1.0, 1000)
        signal = ak.Array({"x": vals[:500]})
        background = ak.Array({"x": vals[500:]})
        results = study_variable_separation(signal, background, ["x"])
        assert results[0]["ks_distance"] < 0.15

    def test_perfect_separation(self):
        """Non-overlapping distributions should have ROC AUC near 1."""
        from gad.selection.variables import study_variable_separation
        signal = ak.Array({"x": np.linspace(10.0, 20.0, 200)})
        background = ak.Array({"x": np.linspace(0.0, 5.0, 200)})
        results = study_variable_separation(signal, background, ["x"])
        assert results[0]["roc_auc"] > 0.99

    def test_sorted_descending(self):
        """Results should be sorted by separation_power descending."""
        from gad.selection.variables import study_variable_separation
        rng = np.random.RandomState(42)
        signal = ak.Array({
            "a": rng.normal(10.0, 1.0, 300),
            "b": rng.normal(0.0, 1.0, 300),
            "c": rng.normal(5.0, 1.0, 300),
        })
        background = ak.Array({
            "a": rng.normal(0.0, 1.0, 300),
            "b": rng.normal(0.0, 1.0, 300),
            "c": rng.normal(0.0, 1.0, 300),
        })
        results = study_variable_separation(signal, background, ["a", "b", "c"])
        for i in range(len(results) - 1):
            assert results[i]["separation_power"] >= results[i + 1]["separation_power"]

    def test_result_keys(self):
        """Each result should have all required keys."""
        from gad.selection.variables import study_variable_separation
        signal = ak.Array({"x": [1.0, 2.0, 3.0]})
        background = ak.Array({"x": [4.0, 5.0, 6.0]})
        results = study_variable_separation(signal, background, ["x"])
        required = {"variable", "ks_distance", "ks_pvalue", "roc_auc", "separation_power"}
        assert required.issubset(set(results[0].keys()))

    def test_auc_always_above_half(self):
        """ROC AUC should always be >= 0.5 due to max(auc, 1-auc) correction."""
        from gad.selection.variables import study_variable_separation
        # background has higher values -> naive AUC < 0.5, but correction fixes it
        signal = ak.Array({"x": np.linspace(0.0, 5.0, 200)})
        background = ak.Array({"x": np.linspace(10.0, 20.0, 200)})
        results = study_variable_separation(signal, background, ["x"])
        assert results[0]["roc_auc"] >= 0.5


# ---------------------------------------------------------------------------
# Task 2 tests: CutFlow table, Asimov significance, binned templates, plots
# ---------------------------------------------------------------------------

class TestCutFlow:
    """Tests for format_cutflow_table."""

    def test_format_cutflow_table_columns(self):
        from gad.selection.cutflow import format_cutflow_table
        cutflow = [
            {"name": "pt > 20", "n_before": 100, "n_after": 80,
             "eff_relative": 0.8, "eff_absolute": 0.8, "weighted_yield": 75.0},
            {"name": "eta < 2.5", "n_before": 80, "n_after": 60,
             "eff_relative": 0.75, "eff_absolute": 0.6, "weighted_yield": 55.0},
        ]
        df = format_cutflow_table(cutflow)
        expected_cols = {"Cut", "N_before", "N_after", "Eff_rel", "Eff_abs", "Yield"}
        assert expected_cols == set(df.columns)
        assert len(df) == 2
        assert df.iloc[0]["Cut"] == "pt > 20"

    def test_format_cutflow_empty(self):
        from gad.selection.cutflow import format_cutflow_table
        df = format_cutflow_table([])
        assert len(df) == 0


class TestAsimovSignificance:
    """Tests for asimov_significance."""

    def test_stat_only(self):
        from gad.selection.cutflow import asimov_significance
        z = asimov_significance(10.0, 100.0)
        assert z == pytest.approx(0.97, abs=0.05)

    def test_zero_signal(self):
        from gad.selection.cutflow import asimov_significance
        assert asimov_significance(0.0, 100.0) == 0.0

    def test_zero_background(self):
        from gad.selection.cutflow import asimov_significance
        assert asimov_significance(10.0, 0.0) == 0.0

    def test_with_syst_less_than_stat_only(self):
        from gad.selection.cutflow import asimov_significance
        z_stat = asimov_significance(10.0, 100.0)
        z_syst = asimov_significance(10.0, 100.0, sigma_b=10.0)
        assert z_syst < z_stat
        assert z_syst > 0.0

    def test_large_signal(self):
        from gad.selection.cutflow import asimov_significance
        z = asimov_significance(100.0, 10.0)
        assert z > 5.0  # very significant


class TestBinnedTemplate:
    """Tests for create_binned_template."""

    def test_uniform_strategy(self):
        from gad.selection.cutflow import create_binned_template
        rng = np.random.RandomState(42)
        values = rng.normal(0, 1, 1000)
        result = create_binned_template(values, weights=None, bins=20,
                                        strategy="uniform")
        assert "bin_edges" in result
        assert "yields" in result
        assert "errors" in result
        assert result["n_bins"] == 20
        assert len(result["bin_edges"]) == 21
        assert len(result["yields"]) == 20
        assert result["integral"] == pytest.approx(1000.0, rel=0.01)

    def test_quantile_strategy(self):
        from gad.selection.cutflow import create_binned_template
        rng = np.random.RandomState(42)
        values = rng.exponential(1.0, 1000)
        result = create_binned_template(values, weights=None, bins=10,
                                        strategy="quantile")
        assert result["n_bins"] == 10
        # Quantile bins should have roughly equal statistics
        yields = result["yields"]
        mean_yield = np.mean(yields)
        for y in yields:
            assert y == pytest.approx(mean_yield, rel=0.3)

    def test_weighted_template(self):
        from gad.selection.cutflow import create_binned_template
        values = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        weights = np.array([2.0, 2.0, 2.0, 2.0, 2.0])
        result = create_binned_template(values, weights=weights, bins=5,
                                        strategy="uniform")
        assert result["integral"] == pytest.approx(10.0)


class TestPlots:
    """Tests for plot_n_minus_1 and plot_variable_comparison."""

    def test_plot_n_minus_1_creates_file(self, tmp_path):
        import matplotlib
        matplotlib.use("Agg")
        from gad.selection.plots import plot_n_minus_1
        from gad.selection.engine import SelectionEngine

        eng = SelectionEngine()
        eng.add_cut("pt_cut", "pt", ">", 15.0)
        eng.add_cut("eta_cut", "eta", "<", 2.0)

        events_dict = {
            "signal": ak.Array({
                "pt": np.random.RandomState(1).uniform(10, 50, 200),
                "eta": np.random.RandomState(2).uniform(0, 3, 200),
            }),
            "background": ak.Array({
                "pt": np.random.RandomState(3).uniform(5, 40, 500),
                "eta": np.random.RandomState(4).uniform(0, 3, 500),
            }),
        }

        out = str(tmp_path / "nm1_test.png")
        plot_n_minus_1(events_dict, eng, cut_index=0, output_path=out)
        import os
        assert os.path.exists(out)
        assert os.path.getsize(out) > 0

    def test_plot_variable_comparison_creates_file(self, tmp_path):
        import matplotlib
        matplotlib.use("Agg")
        from gad.selection.plots import plot_variable_comparison

        rng = np.random.RandomState(42)
        signal = ak.Array({"mass": rng.normal(125, 5, 300)})
        background = ak.Array({"mass": rng.exponential(50, 500)})

        out = str(tmp_path / "var_comp.png")
        plot_variable_comparison(signal, background, "mass", out)
        import os
        assert os.path.exists(out)
        assert os.path.getsize(out) > 0
