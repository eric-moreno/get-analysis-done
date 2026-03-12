"""Tests for gad.regions module: RegionDesigner, RegionValidator, EstimationComparator."""

import numpy as np
import awkward as ak
import pytest


# ---------------------------------------------------------------------------
# Test RegionDesigner
# ---------------------------------------------------------------------------

class TestRegionDesigner:
    """Tests for RegionDesigner CR/VR definition by cut inversion."""

    @pytest.fixture
    def sr_cuts(self):
        return [
            {"variable": "met", "operator": ">", "threshold": 200.0, "absolute": False},
            {"variable": "n_jets", "operator": ">=", "threshold": 4, "absolute": False},
            {"variable": "dphi", "operator": ">", "threshold": 0.4, "absolute": True},
        ]

    @pytest.fixture
    def designer(self, sr_cuts):
        from gad.regions import RegionDesigner
        return RegionDesigner(sr_cuts)

    def test_stores_sr_cuts(self, designer, sr_cuts):
        assert designer.sr_cuts == sr_cuts

    def test_define_cr_inverts_specified_cuts(self, designer):
        cr = designer.define_cr("CR_tt", target_background="ttbar", invert_cuts=["met"])
        # met > 200 should become met <= 200
        met_cut = [c for c in cr["cuts"] if c["variable"] == "met"][0]
        assert met_cut["operator"] == "<="
        assert met_cut["threshold"] == 200.0

    def test_define_cr_preserves_non_inverted_cuts(self, designer):
        cr = designer.define_cr("CR_tt", target_background="ttbar", invert_cuts=["met"])
        njets_cut = [c for c in cr["cuts"] if c["variable"] == "n_jets"][0]
        assert njets_cut["operator"] == ">="
        assert njets_cut["threshold"] == 4

    def test_define_cr_returns_correct_structure(self, designer):
        cr = designer.define_cr("CR_tt", target_background="ttbar", invert_cuts=["met"])
        assert cr["name"] == "CR_tt"
        assert cr["target_background"] == "ttbar"
        assert cr["type"] == "control"
        assert isinstance(cr["cuts"], list)

    def test_define_cr_with_additional_cuts(self, designer):
        extra = [{"variable": "btag", "operator": ">=", "threshold": 2, "absolute": False}]
        cr = designer.define_cr("CR_tt", target_background="ttbar",
                                invert_cuts=["met"], additional_cuts=extra)
        btag_cut = [c for c in cr["cuts"] if c["variable"] == "btag"]
        assert len(btag_cut) == 1
        assert btag_cut[0]["threshold"] == 2

    def test_define_cr_operator_inversions(self, designer):
        """Test all operator inversions."""
        all_ops = [
            {"variable": "a", "operator": ">", "threshold": 1, "absolute": False},
            {"variable": "b", "operator": ">=", "threshold": 2, "absolute": False},
            {"variable": "c", "operator": "<", "threshold": 3, "absolute": False},
            {"variable": "d", "operator": "<=", "threshold": 4, "absolute": False},
            {"variable": "e", "operator": "==", "threshold": 5, "absolute": False},
            {"variable": "f", "operator": "!=", "threshold": 6, "absolute": False},
        ]
        from gad.regions import RegionDesigner
        d = RegionDesigner(all_ops)
        cr = d.define_cr("test", target_background="bkg",
                         invert_cuts=["a", "b", "c", "d", "e", "f"])
        ops = {c["variable"]: c["operator"] for c in cr["cuts"]}
        assert ops == {"a": "<=", "b": "<", "c": ">=", "d": ">", "e": "!=", "f": "=="}

    def test_define_vr_returns_validation_type(self, designer):
        vr = designer.define_vr("VR_tt", target_background="ttbar",
                                tighten_cuts={"met": 150.0})
        assert vr["type"] == "validation"
        assert vr["name"] == "VR_tt"
        assert vr["target_background"] == "ttbar"

    def test_define_vr_tightens_threshold(self, designer):
        """VR should be kinematically between CR and SR."""
        vr = designer.define_vr("VR_tt", target_background="ttbar",
                                tighten_cuts={"met": 150.0})
        met_cut = [c for c in vr["cuts"] if c["variable"] == "met"][0]
        # For met > 200 SR, inverted CR is met <= 200, VR should tighten toward SR
        # VR met threshold should be 150 (between 0 and 200)
        assert met_cut["threshold"] == 150.0

    def test_get_region_mask(self, designer):
        """get_region_mask should return boolean mask for events passing region cuts."""
        cr = designer.define_cr("CR_tt", target_background="ttbar", invert_cuts=["met"])
        # Create synthetic events: met values from 50 to 250
        events = ak.Array({
            "met": np.array([50.0, 100.0, 150.0, 200.0, 250.0]),
            "n_jets": np.array([5, 5, 5, 5, 5]),
            "dphi": np.array([0.5, 0.5, 0.5, 0.5, 0.5]),
        })
        mask = designer.get_region_mask(cr, events)
        # CR inverts met > 200 to met <= 200, keeps n_jets >= 4 and |dphi| > 0.4
        # met <= 200: [50, 100, 150, 200] pass; 250 fails
        # n_jets >= 4: all pass
        # |dphi| > 0.4: all pass
        assert mask.sum() == 4
        assert mask[4] == False  # 250 fails met <= 200

    def test_get_region_mask_empty(self, designer):
        """Mask should be all False if no events pass."""
        cr = designer.define_cr("CR_tt", target_background="ttbar", invert_cuts=["met"])
        events = ak.Array({
            "met": np.array([300.0, 400.0]),
            "n_jets": np.array([5, 5]),
            "dphi": np.array([0.5, 0.5]),
        })
        mask = designer.get_region_mask(cr, events)
        assert mask.sum() == 0


# ---------------------------------------------------------------------------
# Test RegionValidator
# ---------------------------------------------------------------------------

class TestRegionValidator:
    """Tests for RegionValidator purity and data/MC agreement."""

    @pytest.fixture
    def validator(self):
        from gad.regions import RegionValidator
        return RegionValidator()

    def test_compute_purity_known(self, validator):
        """Purity = N_target / N_total with known composition."""
        events_dict = {
            "ttbar": np.array([1, 2, 3, 4, 5]),
            "wjets": np.array([10, 20]),
        }
        # region_mask_fn returns True for all events
        mask_fn = lambda evts: np.ones(len(evts), dtype=bool)
        purity = validator.compute_purity(events_dict, mask_fn, "ttbar")
        assert purity == pytest.approx(5.0 / 7.0, rel=1e-6)

    def test_compute_purity_empty_region(self, validator):
        events_dict = {
            "ttbar": np.array([1, 2, 3]),
            "wjets": np.array([10, 20]),
        }
        mask_fn = lambda evts: np.zeros(len(evts), dtype=bool)
        purity = validator.compute_purity(events_dict, mask_fn, "ttbar")
        assert purity == 0.0

    def test_check_purity_passes(self, validator):
        result = validator.check_purity(0.7, threshold=0.5)
        assert result["passes"] is True
        assert result["purity"] == 0.7
        assert result["threshold"] == 0.5

    def test_check_purity_fails(self, validator):
        result = validator.check_purity(0.3, threshold=0.5)
        assert result["passes"] is False

    def test_chi2_ndf_perfect_agreement(self, validator):
        data = np.array([100.0, 200.0, 150.0])
        mc = np.array([100.0, 200.0, 150.0])
        chi2_per_ndf, ndf, chi2 = validator.chi2_ndf(data, mc)
        assert chi2_per_ndf == pytest.approx(0.0, abs=1e-10)

    def test_chi2_ndf_known_values(self, validator):
        data = np.array([100.0, 200.0, 150.0])
        mc = np.array([110.0, 190.0, 160.0])
        chi2_per_ndf, ndf, chi2 = validator.chi2_ndf(data, mc)
        assert ndf > 0
        assert chi2 > 0
        assert chi2_per_ndf == pytest.approx(chi2 / ndf, rel=1e-6)

    def test_chi2_ndf_skips_low_stats_bins(self, validator):
        """Bins with data+mc < 5 should be skipped."""
        data = np.array([1.0, 100.0, 200.0])
        mc = np.array([1.0, 110.0, 190.0])
        chi2_per_ndf, ndf, chi2 = validator.chi2_ndf(data, mc)
        # First bin: 1+1=2 < 5, skipped. Only 2 bins used.
        assert ndf == 2

    def test_check_agreement_passes(self, validator):
        result = validator.check_agreement(1.5, threshold=2.0)
        assert result["passes"] is True
        assert result["chi2_ndf"] == 1.5

    def test_check_agreement_fails(self, validator):
        result = validator.check_agreement(3.0, threshold=2.0)
        assert result["passes"] is False


# ---------------------------------------------------------------------------
# Test EstimationComparator
# ---------------------------------------------------------------------------

class TestEstimationComparator:
    """Tests for EstimationComparator MC-based vs data-driven methods."""

    @pytest.fixture
    def comparator(self):
        from gad.regions import EstimationComparator
        return EstimationComparator()

    def test_mc_based_estimate(self, comparator):
        result = comparator.mc_based_estimate(mc_yield=100.0, mc_stat_err=10.0,
                                              mc_syst_frac=0.2)
        assert result["yield"] == 100.0
        assert result["stat_err"] == 10.0
        assert result["syst_err"] == pytest.approx(20.0)
        expected_total = np.sqrt(10.0**2 + 20.0**2)
        assert result["total_err"] == pytest.approx(expected_total)
        assert result["method"] == "mc_based"

    def test_mc_based_estimate_no_syst(self, comparator):
        result = comparator.mc_based_estimate(mc_yield=100.0, mc_stat_err=10.0)
        assert result["syst_err"] == 0.0
        assert result["total_err"] == pytest.approx(10.0)

    def test_transfer_factor_estimate(self, comparator):
        # CR data=200, CR MC=100, SR MC=50 => TF=2.0, estimated yield=100
        result = comparator.transfer_factor_estimate(cr_data=200.0, cr_mc=100.0,
                                                     sr_mc=50.0)
        assert result["transfer_factor"] == pytest.approx(2.0)
        assert result["yield"] == pytest.approx(100.0)
        assert result["method"] == "transfer_factor"
        assert result["total_err"] > 0

    def test_transfer_factor_error_propagation(self, comparator):
        result = comparator.transfer_factor_estimate(
            cr_data=200.0, cr_mc=100.0, sr_mc=50.0,
            cr_data_err=14.14, cr_mc_err=10.0, sr_mc_err=7.07)
        assert result["stat_err"] > 0
        assert result["total_err"] > 0

    def test_abcd_estimate(self, comparator):
        # D = B * C / A
        result = comparator.abcd_estimate(region_a=100.0, region_b=200.0,
                                          region_c=150.0, region_d=None)
        assert result["yield"] == pytest.approx(300.0)  # 200*150/100
        assert result["method"] == "abcd"
        assert result["total_err"] > 0

    def test_compare_methods_recommends_lower_uncertainty(self, comparator):
        est1 = {"method": "mc_based", "yield": 100.0, "total_err": 25.0}
        est2 = {"method": "transfer_factor", "yield": 95.0, "total_err": 15.0}
        result = comparator.compare_methods(est1, est2)
        assert result["recommended"] == "transfer_factor"
        assert "improvement_percent" in result
        assert result["improvement_percent"] > 0

    def test_compare_methods_includes_estimates(self, comparator):
        est1 = {"method": "mc_based", "yield": 100.0, "total_err": 25.0}
        est2 = {"method": "transfer_factor", "yield": 95.0, "total_err": 15.0}
        result = comparator.compare_methods(est1, est2)
        assert len(result["estimates"]) == 2


# ---------------------------------------------------------------------------
# Test ClosureTester
# ---------------------------------------------------------------------------

class TestClosureTest:
    """Tests for ClosureTester VR prediction validation."""

    @pytest.fixture
    def tester(self):
        from gad.regions import ClosureTester
        return ClosureTester(threshold=2.0)

    def test_run_closure_test_passes_within_threshold(self, tester):
        """Closure test passes when pull < 2.0 sigma."""
        # CR data=200, CR MC=100, VR MC=50 => TF=2.0, predicted=100
        # observed=105, total_uncertainty=10 => pull=|105-100|/10 = 0.5
        result = tester.run_closure_test(
            cr_data=200.0, cr_mc=100.0, vr_mc=50.0,
            vr_observed=105.0, total_uncertainty=10.0, name="VR_tt"
        )
        assert result["name"] == "VR_tt"
        assert result["predicted"] == pytest.approx(100.0)
        assert result["observed"] == 105.0
        assert result["pull"] == pytest.approx(0.5)
        assert result["passes"] is True
        assert result["threshold"] == 2.0
        assert result["total_uncertainty"] == 10.0

    def test_run_closure_test_fails_beyond_threshold(self, tester):
        """Closure test fails when pull > 2.0 sigma."""
        # predicted=100, observed=130, uncertainty=10 => pull=3.0
        result = tester.run_closure_test(
            cr_data=200.0, cr_mc=100.0, vr_mc=50.0,
            vr_observed=130.0, total_uncertainty=10.0
        )
        assert result["pull"] == pytest.approx(3.0)
        assert result["passes"] is False

    def test_run_closure_test_uses_transfer_factor(self, tester):
        """Prediction must come from CR-extrapolated transfer factor, not pure MC."""
        # CR data=300, CR MC=100, VR MC=40 => TF=3.0, predicted=120 (not 40)
        result = tester.run_closure_test(
            cr_data=300.0, cr_mc=100.0, vr_mc=40.0,
            vr_observed=120.0, total_uncertainty=10.0
        )
        assert result["predicted"] == pytest.approx(120.0)
        assert result["pull"] == pytest.approx(0.0, abs=1e-10)
        assert result["passes"] is True

    def test_run_all_closure_tests_all_pass(self, tester):
        """Batch closure test with all passing."""
        configs = [
            {"cr_data": 200.0, "cr_mc": 100.0, "vr_mc": 50.0,
             "vr_observed": 105.0, "total_uncertainty": 10.0, "name": "VR1"},
            {"cr_data": 300.0, "cr_mc": 100.0, "vr_mc": 40.0,
             "vr_observed": 125.0, "total_uncertainty": 10.0, "name": "VR2"},
        ]
        result = tester.run_all_closure_tests(configs)
        assert result["all_pass"] is True
        assert result["n_pass"] == 2
        assert result["n_fail"] == 0
        assert len(result["results"]) == 2

    def test_run_all_closure_tests_some_fail(self, tester):
        """Batch closure test with some failures."""
        configs = [
            {"cr_data": 200.0, "cr_mc": 100.0, "vr_mc": 50.0,
             "vr_observed": 105.0, "total_uncertainty": 10.0, "name": "VR1"},
            {"cr_data": 200.0, "cr_mc": 100.0, "vr_mc": 50.0,
             "vr_observed": 130.0, "total_uncertainty": 10.0, "name": "VR2"},
        ]
        result = tester.run_all_closure_tests(configs)
        assert result["all_pass"] is False
        assert result["n_pass"] == 1
        assert result["n_fail"] == 1

    def test_validate_data_mc_good_agreement(self, tester):
        """Data/MC validation passes with chi2/ndf < 2.0."""
        distributions = [
            {
                "name": "met",
                "data_hist": np.array([100.0, 200.0, 150.0]),
                "mc_hist": np.array([100.0, 200.0, 150.0]),
                "mc_errors": None,
            }
        ]
        results = tester.validate_data_mc(distributions)
        assert len(results) == 1
        assert results[0]["name"] == "met"
        assert results[0]["passes"] is True
        assert results[0]["chi2_ndf"] == pytest.approx(0.0, abs=1e-10)

    def test_validate_data_mc_poor_agreement(self, tester):
        """Data/MC validation fails with large disagreement."""
        distributions = [
            {
                "name": "met",
                "data_hist": np.array([100.0, 200.0, 150.0]),
                "mc_hist": np.array([50.0, 300.0, 80.0]),
                "mc_errors": None,
            }
        ]
        results = tester.validate_data_mc(distributions)
        assert results[0]["passes"] is False
        assert results[0]["chi2_ndf"] > 2.0

    def test_validate_data_mc_custom_threshold(self, tester):
        """Custom chi2/ndf threshold."""
        distributions = [
            {
                "name": "pt",
                "data_hist": np.array([100.0, 200.0, 150.0]),
                "mc_hist": np.array([105.0, 195.0, 155.0]),
                "mc_errors": None,
            }
        ]
        results = tester.validate_data_mc(distributions, threshold=0.01)
        # Small disagreement but very tight threshold
        assert results[0]["threshold"] == 0.01


# ---------------------------------------------------------------------------
# Test CrossChecker
# ---------------------------------------------------------------------------

class TestCrossChecker:
    """Tests for CrossChecker independent reproduction and auxiliary checks."""

    @pytest.fixture
    def checker(self):
        from gad.regions import CrossChecker
        return CrossChecker()

    def test_compare_cutflows_passes_within_threshold(self, checker):
        """Cut-flow comparison passes when max relative diff < 1%."""
        ref = [{"cut": "presel", "yield": 1000.0}, {"cut": "met>200", "yield": 500.0}]
        check = [{"cut": "presel", "yield": 1002.0}, {"cut": "met>200", "yield": 499.0}]
        result = checker.compare_cutflows(ref, check)
        assert result["passes"] is True
        assert result["max_diff"] < 0.01
        assert result["threshold"] == 0.01
        assert len(result["per_cut_diffs"]) == 2

    def test_compare_cutflows_fails_beyond_threshold(self, checker):
        """Cut-flow comparison fails when max relative diff > 1%."""
        ref = [{"cut": "presel", "yield": 1000.0}, {"cut": "met>200", "yield": 500.0}]
        check = [{"cut": "presel", "yield": 1000.0}, {"cut": "met>200", "yield": 450.0}]
        result = checker.compare_cutflows(ref, check)
        assert result["passes"] is False
        assert result["max_diff"] > 0.01

    def test_compare_cutflows_per_cut_details(self, checker):
        """Each per_cut_diff has cut name, ref/check yields, rel_diff."""
        ref = [{"cut": "presel", "yield": 1000.0}]
        check = [{"cut": "presel", "yield": 1005.0}]
        result = checker.compare_cutflows(ref, check)
        entry = result["per_cut_diffs"][0]
        assert entry["cut"] == "presel"
        assert entry["ref_yield"] == 1000.0
        assert entry["check_yield"] == 1005.0
        assert entry["rel_diff"] == pytest.approx(0.005, rel=1e-3)

    def test_compare_cutflows_accepts_dataframes(self, checker):
        """Should accept pandas DataFrames as input."""
        import pandas as pd
        ref_df = pd.DataFrame({"Cut": ["presel", "met"], "Yield": [1000.0, 500.0]})
        check_df = pd.DataFrame({"Cut": ["presel", "met"], "Yield": [1002.0, 499.0]})
        result = checker.compare_cutflows(ref_df, check_df)
        assert result["passes"] is True
        assert len(result["per_cut_diffs"]) == 2

    def test_compare_yields_passes_within_1sigma(self, checker):
        """Yield comparison passes when pull < 1.0."""
        result = checker.compare_yields(
            ref_yield=100.0, ref_uncertainty=10.0,
            check_yield=105.0, check_uncertainty=10.0
        )
        # pull = |100-105| / sqrt(100+100) = 5/14.14 ~ 0.354
        assert result["passes"] is True
        assert result["pull"] < 1.0
        assert result["ref_yield"] == 100.0
        assert result["check_yield"] == 105.0

    def test_compare_yields_fails_beyond_1sigma(self, checker):
        """Yield comparison fails when pull > 1.0."""
        result = checker.compare_yields(
            ref_yield=100.0, ref_uncertainty=5.0,
            check_yield=120.0, check_uncertainty=5.0
        )
        # pull = |100-120| / sqrt(25+25) = 20/7.07 ~ 2.83
        assert result["passes"] is False
        assert result["pull"] > 1.0

    def test_check_auxiliary_returns_advisory(self, checker):
        """Auxiliary checks are advisory only, never hard-fail."""
        comparisons = [
            {
                "name": "dphi",
                "data_hist": np.array([100.0, 200.0, 150.0]),
                "mc_hist": np.array([50.0, 300.0, 80.0]),
                "mc_errors": None,
            }
        ]
        result = checker.check_auxiliary(comparisons)
        assert result["advisory_only"] is True
        assert len(result["results"]) == 1
        assert "advisory_warning" in result["results"][0]
        assert result["results"][0]["name"] == "dphi"

    def test_check_auxiliary_good_agreement_no_warning(self, checker):
        """No advisory warning when agreement is good."""
        comparisons = [
            {
                "name": "met",
                "data_hist": np.array([100.0, 200.0, 150.0]),
                "mc_hist": np.array([100.0, 200.0, 150.0]),
                "mc_errors": None,
            }
        ]
        result = checker.check_auxiliary(comparisons)
        assert result["advisory_only"] is True
        assert result["results"][0]["advisory_warning"] is False


# ---------------------------------------------------------------------------
# Test YieldTable
# ---------------------------------------------------------------------------

class TestYieldTable:
    """Tests for YieldTable background yield aggregation."""

    @pytest.fixture
    def table(self):
        from gad.regions import YieldTable
        return YieldTable()

    def test_add_process_and_build(self, table):
        """Build yield table with one process."""
        table.add_process("ttbar", {
            "SR": {"yield": 50.0, "stat_err": 5.0, "syst_err": 10.0},
            "CR": {"yield": 200.0, "stat_err": 14.0, "syst_err": 20.0},
        })
        df = table.build()
        assert "SR" in df.columns
        assert "CR" in df.columns
        assert "ttbar" in df.index

    def test_build_formats_cells(self, table):
        """Cells should be formatted as 'yield +/- stat +/- syst'."""
        table.add_process("ttbar", {
            "SR": {"yield": 50.0, "stat_err": 5.0, "syst_err": 10.0},
        })
        df = table.build()
        cell = df.loc["ttbar", "SR"]
        assert "+/-" in cell or "+-" in cell

    def test_total_background_single_process(self, table):
        """Total background with one process equals that process."""
        table.add_process("ttbar", {
            "SR": {"yield": 50.0, "stat_err": 5.0, "syst_err": 10.0},
        })
        totals = table.total_background()
        assert totals["SR"]["yield"] == pytest.approx(50.0)
        assert totals["SR"]["stat_err"] == pytest.approx(5.0)
        assert totals["SR"]["syst_err"] == pytest.approx(10.0)

    def test_total_background_multiple_processes(self, table):
        """Total background sums yields and propagates errors in quadrature."""
        table.add_process("ttbar", {
            "SR": {"yield": 50.0, "stat_err": 5.0, "syst_err": 10.0},
        })
        table.add_process("wjets", {
            "SR": {"yield": 30.0, "stat_err": 4.0, "syst_err": 6.0},
        })
        totals = table.total_background()
        assert totals["SR"]["yield"] == pytest.approx(80.0)
        assert totals["SR"]["stat_err"] == pytest.approx(np.sqrt(25 + 16))
        assert totals["SR"]["syst_err"] == pytest.approx(np.sqrt(100 + 36))

    def test_total_background_excludes_signal(self, table):
        """Signal processes should not be included in total background."""
        table.add_process("ttbar", {
            "SR": {"yield": 50.0, "stat_err": 5.0, "syst_err": 10.0},
        })
        table.add_process("signal", {
            "SR": {"yield": 10.0, "stat_err": 3.0, "syst_err": 2.0},
        }, is_signal=True)
        totals = table.total_background()
        assert totals["SR"]["yield"] == pytest.approx(50.0)

    def test_to_dict(self, table):
        """to_dict returns machine-readable nested structure."""
        table.add_process("ttbar", {
            "SR": {"yield": 50.0, "stat_err": 5.0, "syst_err": 10.0},
        })
        d = table.to_dict()
        assert "ttbar" in d
        assert "SR" in d["ttbar"]
        assert d["ttbar"]["SR"]["yield"] == 50.0

    def test_multiple_regions(self, table):
        """Yield table with multiple regions and processes."""
        table.add_process("ttbar", {
            "SR": {"yield": 50.0, "stat_err": 5.0, "syst_err": 10.0},
            "CR": {"yield": 200.0, "stat_err": 14.0, "syst_err": 20.0},
        })
        table.add_process("wjets", {
            "SR": {"yield": 30.0, "stat_err": 4.0, "syst_err": 6.0},
            "CR": {"yield": 100.0, "stat_err": 10.0, "syst_err": 15.0},
        })
        df = table.build()
        assert df.shape == (2, 2)
        totals = table.total_background()
        assert "SR" in totals
        assert "CR" in totals
