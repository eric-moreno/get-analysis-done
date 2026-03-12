"""Tests for gad.statistical -- workspace builder, fitter, diagnostics, datacard."""

import json
import os
import tempfile

import numpy as np
import pyhf
import pytest

from gad.statistical.workspace import WorkspaceBuilder
from gad.statistical.fitter import Fitter
from gad.statistical.diagnostics import Diagnostics
from gad.statistical.datacard import DatacardExporter, SensitivityOptimizer


class TestWorkspaceBuilder:
    """Tests for WorkspaceBuilder."""

    def _make_simple_workspace(self):
        """Helper: build a simple 2-channel workspace (SR + CR) with signal + background."""
        wb = WorkspaceBuilder(poi_name="mu")

        # Signal region: 3 bins
        sr_obs = [15.0, 25.0, 10.0]
        wb.add_channel("SR", sr_obs)
        wb.add_sample("SR", "background", [14.0, 24.0, 9.0])
        wb.add_sample("SR", "signal", [1.0, 1.0, 1.0])
        wb.add_signal("SR", "signal")

        # Control region: 3 bins
        cr_obs = [100.0, 200.0, 50.0]
        wb.add_channel("CR", cr_obs)
        wb.add_sample("CR", "background", [100.0, 200.0, 50.0])
        wb.add_sample("CR", "signal", [0.5, 0.5, 0.5])
        wb.add_signal("CR", "signal")

        # Add a normsys modifier to background in SR
        wb.add_modifier("SR", "background", {
            "name": "bkg_norm",
            "type": "normsys",
            "data": {"hi": 1.05, "lo": 0.95},
        })

        return wb

    # -- add_channel / add_sample basic -----------------------------------------

    def test_add_channel_and_sample(self):
        wb = WorkspaceBuilder()
        wb.add_channel("SR", [10.0, 20.0])
        wb.add_sample("SR", "bkg", [10.0, 20.0])
        spec = wb.build()
        assert len(spec["channels"]) == 1
        assert spec["channels"][0]["name"] == "SR"

    def test_add_sample_to_unknown_channel_raises(self):
        wb = WorkspaceBuilder()
        with pytest.raises(KeyError):
            wb.add_sample("missing", "bkg", [10.0])

    # -- add_modifier -----------------------------------------------------------

    def test_add_modifier_normsys(self):
        wb = WorkspaceBuilder()
        wb.add_channel("SR", [10.0])
        wb.add_sample("SR", "bkg", [10.0])
        wb.add_modifier("SR", "bkg", {
            "name": "norm_syst",
            "type": "normsys",
            "data": {"hi": 1.1, "lo": 0.9},
        })
        spec = wb.build()
        sample = spec["channels"][0]["samples"][0]
        mod_names = [m["name"] for m in sample["modifiers"]]
        assert "norm_syst" in mod_names

    # -- add_staterror ----------------------------------------------------------

    def test_add_staterror(self):
        wb = WorkspaceBuilder()
        wb.add_channel("SR", [10.0, 20.0])
        wb.add_sample("SR", "bkg", [10.0, 20.0])
        wb.add_staterror("SR", [1.0, 2.0])
        spec = wb.build()
        sample = spec["channels"][0]["samples"][0]
        staterr_mods = [m for m in sample["modifiers"] if m["type"] == "staterror"]
        assert len(staterr_mods) == 1
        assert staterr_mods[0]["data"] == [1.0, 2.0]

    # -- add_signal -------------------------------------------------------------

    def test_add_signal_adds_normfactor(self):
        wb = WorkspaceBuilder()
        wb.add_channel("SR", [10.0])
        wb.add_sample("SR", "signal", [1.0])
        wb.add_signal("SR", "signal")
        spec = wb.build()
        sample = spec["channels"][0]["samples"][0]
        nf_mods = [m for m in sample["modifiers"] if m["type"] == "normfactor"]
        assert len(nf_mods) == 1
        assert nf_mods[0]["name"] == "mu"

    # -- build validates via pyhf -----------------------------------------------

    def test_build_returns_valid_pyhf_workspace(self):
        wb = self._make_simple_workspace()
        spec = wb.build()
        # Should not raise
        ws = pyhf.Workspace(spec)
        assert ws is not None

    def test_build_has_measurement(self):
        wb = self._make_simple_workspace()
        spec = wb.build()
        assert len(spec["measurements"]) == 1
        assert spec["measurements"][0]["name"] == "analysis"
        assert spec["measurements"][0]["config"]["poi"] == "mu"

    def test_build_has_observations(self):
        wb = self._make_simple_workspace()
        spec = wb.build()
        obs_names = [o["name"] for o in spec["observations"]]
        assert "SR" in obs_names
        assert "CR" in obs_names

    def test_build_empty_workspace_raises(self):
        wb = WorkspaceBuilder()
        with pytest.raises(Exception):
            wb.build()

    # -- validate_asimov --------------------------------------------------------

    def test_validate_asimov_returns_valid(self):
        wb = self._make_simple_workspace()
        spec = wb.build()
        result = wb.validate_asimov(spec)
        assert result["valid"] is True
        assert result["max_pull"] < 0.5

    def test_validate_asimov_has_pulls_dict(self):
        wb = self._make_simple_workspace()
        spec = wb.build()
        result = wb.validate_asimov(spec)
        assert isinstance(result["pulls"], dict)
        assert len(result["pulls"]) > 0

    # -- save / load ------------------------------------------------------------

    def test_save_and_load_roundtrip(self):
        wb = self._make_simple_workspace()
        spec = wb.build()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            wb.save(spec, f.name)
            loaded = WorkspaceBuilder.load(f.name)
        os.unlink(f.name)
        assert loaded == spec

    # -- two channels -----------------------------------------------------------

    def test_two_channel_workspace_valid(self):
        """Full integration: 2-channel workspace with modifier passes pyhf validation."""
        wb = self._make_simple_workspace()
        spec = wb.build()
        ws = pyhf.Workspace(spec)
        model = ws.model()
        assert model.config.channels == ["CR", "SR"]


def _build_test_workspace_spec():
    """Module-level helper to build a small workspace spec for Fitter tests."""
    wb = WorkspaceBuilder(poi_name="mu")

    # Signal region: 2 bins (small for speed, signal large enough for limit scan)
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


class TestFitter:
    """Tests for Fitter."""

    @pytest.fixture(scope="class")
    def spec(self):
        return _build_test_workspace_spec()

    @pytest.fixture(scope="class")
    def fitter(self, spec):
        return Fitter(spec)

    # -- fit --------------------------------------------------------------------

    def test_fit_returns_fit_results(self, fitter):
        result = fitter.fit()
        assert hasattr(result, "bestfit")
        assert hasattr(result, "uncertainty")
        assert hasattr(result, "labels")

    def test_fit_asimov_converges(self, fitter):
        result = fitter.fit(asimov=True)
        assert len(result.bestfit) > 0
        assert all(np.isfinite(result.bestfit))

    def test_fit_asimov_poi_near_zero(self, fitter, spec):
        """Background-only Asimov fit should have POI near 0."""
        result = fitter.fit(asimov=True)
        # Find POI index
        poi_idx = list(result.labels).index("mu")
        assert abs(result.bestfit[poi_idx]) < 1.0  # Should be ~0 for bkg-only Asimov

    # -- fit_asimov convenience -------------------------------------------------

    def test_fit_asimov_convenience(self, fitter):
        result = fitter.fit_asimov(poi_value=0.0)
        assert hasattr(result, "bestfit")

    # -- expected_limit ---------------------------------------------------------

    def test_expected_limit_returns_required_keys(self, fitter):
        result = fitter.expected_limit()
        assert "expected_limit" in result
        assert "bands" in result
        bands = result["bands"]
        for key in ["-2", "-1", "+1", "+2"]:
            assert key in bands

    def test_expected_limit_is_positive(self, fitter):
        result = fitter.expected_limit()
        assert result["expected_limit"] > 0.0

    def test_expected_limit_bands_ordered(self, fitter):
        result = fitter.expected_limit()
        bands = result["bands"]
        # -2sigma < -1sigma < expected < +1sigma < +2sigma
        assert bands["-2"] <= bands["-1"]
        assert bands["-1"] <= result["expected_limit"]
        assert result["expected_limit"] <= bands["+1"]
        assert bands["+1"] <= bands["+2"]

    def test_expected_limit_observed_is_none_for_asimov(self, fitter):
        result = fitter.expected_limit()
        assert result["observed_limit"] is None

    # -- goodness_of_fit --------------------------------------------------------

    def test_fit_with_gof(self, fitter):
        result = fitter.fit(asimov=True, goodness_of_fit=True)
        assert hasattr(result, "bestfit")


class TestDiagnostics:
    """Tests for Diagnostics class."""

    @pytest.fixture(scope="class")
    def spec(self):
        return _build_test_workspace_spec()

    @pytest.fixture(scope="class")
    def diag(self, spec, tmp_path_factory):
        output_dir = str(tmp_path_factory.mktemp("diag_figures"))
        return Diagnostics(spec, output_dir=output_dir)

    @pytest.fixture(scope="class")
    def fit_results(self, diag):
        """Get fit results once for reuse."""
        import cabinetry
        model, data = cabinetry.model_utils.model_and_data(diag._spec)
        return cabinetry.fit.fit(model, data)

    # -- pull_plot ---------------------------------------------------------------

    def test_pull_plot_returns_path(self, diag, fit_results):
        path = diag.pull_plot(fit_results)
        assert path is not None
        assert os.path.exists(path)

    def test_pull_plot_is_pdf(self, diag, fit_results):
        path = diag.pull_plot(fit_results)
        assert path.endswith(".pdf")

    # -- ranking_plot ------------------------------------------------------------

    def test_ranking_plot_returns_results_and_path(self, diag, fit_results):
        ranking_results, path = diag.ranking_plot(fit_results=fit_results)
        assert path is not None
        assert os.path.exists(path)
        assert hasattr(ranking_results, "labels")

    # -- correlation_matrix ------------------------------------------------------

    def test_correlation_matrix_returns_path(self, diag, fit_results):
        path = diag.correlation_matrix(fit_results)
        assert path is not None
        assert os.path.exists(path)

    def test_correlation_matrix_is_pdf(self, diag, fit_results):
        path = diag.correlation_matrix(fit_results)
        assert path.endswith(".pdf")

    # -- likelihood_scan ---------------------------------------------------------

    def test_likelihood_scan_returns_results_and_path(self, diag):
        scan_results, path = diag.likelihood_scan("bkg_norm")
        assert path is not None
        assert os.path.exists(path)
        assert hasattr(scan_results, "name")
        assert scan_results.name == "bkg_norm"

    # -- gof_test ----------------------------------------------------------------

    def test_gof_test_returns_dict(self, diag):
        result = diag.gof_test()
        assert "gof_stat" in result
        assert "p_value" in result
        assert result["saturated"] is True

    # -- run_all_diagnostics ----------------------------------------------------

    def test_run_all_returns_summary(self, diag):
        result = diag.run_all_diagnostics()
        assert "fit_results" in result
        assert "ranking_results" in result
        assert "constraint_analysis" in result
        assert "gof" in result
        assert "figure_paths" in result
        assert isinstance(result["figure_paths"], dict)


class TestConstraintAnalysis:
    """Tests for constraint analysis method."""

    @pytest.fixture(scope="class")
    def spec(self):
        return _build_test_workspace_spec()

    @pytest.fixture(scope="class")
    def diag(self, spec, tmp_path_factory):
        output_dir = str(tmp_path_factory.mktemp("constraint_figures"))
        return Diagnostics(spec, output_dir=output_dir)

    @pytest.fixture(scope="class")
    def fit_and_ranking(self, diag):
        """Get fit results and ranking results."""
        import cabinetry
        model, data = cabinetry.model_utils.model_and_data(diag._spec)
        fit_results = cabinetry.fit.fit(model, data)
        ranking_results = cabinetry.fit.ranking(model, data, fit_results=fit_results)
        return fit_results, ranking_results

    def test_constraint_analysis_returns_list(self, diag, fit_and_ranking):
        fit_results, ranking_results = fit_and_ranking
        result = diag.constraint_analysis(fit_results, ranking_results, top_n=5)
        assert isinstance(result, list)

    def test_constraint_analysis_entry_has_required_keys(self, diag, fit_and_ranking):
        fit_results, ranking_results = fit_and_ranking
        result = diag.constraint_analysis(fit_results, ranking_results, top_n=5)
        if len(result) > 0:
            entry = result[0]
            for key in ["name", "pre_fit_unc", "post_fit_unc", "constraint_factor", "impact_on_mu"]:
                assert key in entry

    def test_constraint_analysis_sorted_by_impact(self, diag, fit_and_ranking):
        fit_results, ranking_results = fit_and_ranking
        result = diag.constraint_analysis(fit_results, ranking_results, top_n=5)
        if len(result) > 1:
            impacts = [abs(e["impact_on_mu"]) for e in result]
            assert impacts == sorted(impacts, reverse=True)

    def test_constraint_factor_is_ratio(self, diag, fit_and_ranking):
        fit_results, ranking_results = fit_and_ranking
        result = diag.constraint_analysis(fit_results, ranking_results, top_n=5)
        for entry in result:
            expected = entry["post_fit_unc"] / entry["pre_fit_unc"]
            assert abs(entry["constraint_factor"] - expected) < 1e-6


class TestDatacardExporter:
    """Tests for DatacardExporter and SensitivityOptimizer."""

    @pytest.fixture(scope="class")
    def spec(self):
        return _build_test_workspace_spec()

    @pytest.fixture(scope="class")
    def exporter(self):
        return DatacardExporter()

    @pytest.fixture(scope="class")
    def export_result(self, exporter, spec, tmp_path_factory):
        output_dir = str(tmp_path_factory.mktemp("datacard_output"))
        return exporter.export(spec, output_dir)

    # -- export creates files ---------------------------------------------------

    def test_export_creates_datacard_file(self, export_result):
        assert os.path.exists(export_result["datacard_path"])

    def test_export_creates_shapes_file(self, export_result):
        assert os.path.exists(export_result["shapes_path"])

    def test_export_returns_counts(self, export_result):
        assert export_result["n_channels"] > 0
        assert export_result["n_processes"] > 0

    # -- datacard format --------------------------------------------------------

    def test_datacard_has_imax_header(self, export_result):
        with open(export_result["datacard_path"]) as f:
            content = f.read()
        assert "imax" in content

    def test_datacard_has_jmax_header(self, export_result):
        with open(export_result["datacard_path"]) as f:
            content = f.read()
        assert "jmax" in content

    def test_datacard_has_kmax_header(self, export_result):
        with open(export_result["datacard_path"]) as f:
            content = f.read()
        assert "kmax" in content

    def test_datacard_has_shapes_line(self, export_result):
        with open(export_result["datacard_path"]) as f:
            content = f.read()
        assert "shapes" in content
        assert "shapes.root" in content

    def test_datacard_has_observation_line(self, export_result):
        with open(export_result["datacard_path"]) as f:
            content = f.read()
        assert "observation" in content

    def test_datacard_signal_at_process_index_zero(self, export_result):
        """Signal process should have process index 0."""
        with open(export_result["datacard_path"]) as f:
            lines = f.readlines()
        # Find the process index line (second 'process' line)
        process_lines = [l for l in lines if l.strip().startswith("process")]
        assert len(process_lines) >= 2
        # The numeric process line should contain 0 for signal
        idx_line = process_lines[1].strip()
        values = idx_line.split()[1:]  # skip "process" label
        assert "0" in values

    def test_datacard_has_lnN_for_normsys(self, export_result):
        with open(export_result["datacard_path"]) as f:
            content = f.read()
        assert "lnN" in content

    def test_datacard_has_autoMCStats(self, export_result):
        with open(export_result["datacard_path"]) as f:
            content = f.read()
        assert "autoMCStats" in content

    # -- shapes.root contents ---------------------------------------------------

    def test_shapes_root_readable(self, export_result):
        import uproot
        f = uproot.open(export_result["shapes_path"])
        assert len(f.keys()) > 0
        f.close()

    def test_shapes_root_has_channel_process_histograms(self, export_result):
        import uproot
        f = uproot.open(export_result["shapes_path"])
        keys = [k.split(";")[0] for k in f.keys()]
        # Should have at least one channel/process histogram
        assert any("/" in k for k in keys)
        f.close()

    # -- SensitivityOptimizer ---------------------------------------------------

    def test_sensitivity_comparison_returns_dataframe(self, spec):
        optimizer = SensitivityOptimizer()
        configs = {"baseline": spec, "alternative": spec}
        result = optimizer.compare_configurations(configs)
        import pandas as pd
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    def test_sensitivity_comparison_has_required_columns(self, spec):
        optimizer = SensitivityOptimizer()
        configs = {"baseline": spec}
        result = optimizer.compare_configurations(configs)
        for col in ["config", "expected_limit", "band_m2", "band_m1", "band_p1", "band_p2", "best"]:
            assert col in result.columns

    def test_sensitivity_comparison_marks_best(self, spec):
        optimizer = SensitivityOptimizer()
        configs = {"baseline": spec, "same": spec}
        result = optimizer.compare_configurations(configs)
        assert result["best"].sum() >= 1  # At least one marked best


class TestFitterObserved:
    """Tests for Fitter.observed_limit() using real (observed) data."""

    @pytest.fixture(scope="class")
    def spec(self):
        return _build_test_workspace_spec()

    @pytest.fixture(scope="class")
    def fitter(self, spec):
        return Fitter(spec)

    def test_observed_limit_returns_required_keys(self, fitter):
        result = fitter.observed_limit()
        assert "observed_limit" in result
        assert "expected_limit" in result
        assert "bands" in result
        bands = result["bands"]
        for key in ["-2", "-1", "+1", "+2"]:
            assert key in bands

    def test_observed_limit_is_positive(self, fitter):
        result = fitter.observed_limit()
        assert result["observed_limit"] > 0.0

    def test_observed_limit_bands_ordered(self, fitter):
        result = fitter.observed_limit()
        bands = result["bands"]
        assert bands["-2"] <= bands["-1"]
        assert bands["-1"] <= result["expected_limit"]
        assert result["expected_limit"] <= bands["+1"]
        assert bands["+1"] <= bands["+2"]

    def test_observed_limit_uses_real_data(self, fitter):
        result = fitter.observed_limit()
        assert result["observed_limit"] is not None
