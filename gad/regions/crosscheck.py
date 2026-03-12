"""CrossChecker: Independent reproduction of cut-flow and yield estimates."""

import numpy as np

from gad.regions.validator import RegionValidator


class CrossChecker:
    """Cross-check analysis results by independent reproduction.

    Compares cut-flow tables within 1% agreement, yield estimates within
    1-sigma, and provides advisory (non-blocking) auxiliary distribution checks.
    """

    def __init__(self):
        self._validator = RegionValidator()

    def compare_cutflows(self, reference_cutflow, check_cutflow,
                         threshold: float = 0.01) -> dict:
        """Compare two cut-flow tables for agreement.

        Parameters
        ----------
        reference_cutflow : list of dict or DataFrame
            Reference cut-flow. If list-of-dicts, must have 'cut'/'Cut' and
            'yield'/'Yield' keys. If DataFrame, must have 'Cut' and 'Yield'
            columns.
        check_cutflow : list of dict or DataFrame
            Cross-checker cut-flow in the same format.
        threshold : float
            Maximum allowed relative difference (default 0.01 = 1%).

        Returns
        -------
        dict
            Keys: max_diff, per_cut_diffs, passes, threshold.
        """
        ref_entries = self._normalize_cutflow(reference_cutflow)
        check_entries = self._normalize_cutflow(check_cutflow)

        per_cut_diffs = []
        for ref_row, check_row in zip(ref_entries, check_entries):
            ref_yield = ref_row["yield"]
            check_yield = check_row["yield"]
            if ref_yield > 0:
                rel_diff = abs(ref_yield - check_yield) / ref_yield
            else:
                rel_diff = 0.0 if check_yield == 0 else float("inf")

            per_cut_diffs.append({
                "cut": ref_row["cut"],
                "ref_yield": ref_yield,
                "check_yield": check_yield,
                "rel_diff": float(rel_diff),
            })

        max_diff = max(d["rel_diff"] for d in per_cut_diffs) if per_cut_diffs else 0.0

        return {
            "max_diff": float(max_diff),
            "per_cut_diffs": per_cut_diffs,
            "passes": max_diff < threshold,
            "threshold": threshold,
        }

    def compare_yields(self, ref_yield: float, ref_uncertainty: float,
                       check_yield: float, check_uncertainty: float) -> dict:
        """Compare two yield estimates for consistency.

        Computes pull = |ref - check| / sqrt(ref_unc^2 + check_unc^2).

        Parameters
        ----------
        ref_yield, ref_uncertainty : float
            Reference yield and its total uncertainty.
        check_yield, check_uncertainty : float
            Cross-checker yield and its total uncertainty.

        Returns
        -------
        dict
            Keys: pull, passes (pull < 1.0), ref_yield, check_yield.
        """
        combined_unc = np.sqrt(ref_uncertainty ** 2 + check_uncertainty ** 2)
        pull = abs(ref_yield - check_yield) / combined_unc if combined_unc > 0 else 0.0

        return {
            "pull": float(pull),
            "passes": bool(pull < 1.0),
            "ref_yield": ref_yield,
            "check_yield": check_yield,
        }

    def check_auxiliary(self, comparisons: list) -> dict:
        """Run advisory checks on auxiliary distributions.

        These are informational only and never cause hard gate failures
        (per locked decision: auxiliary distribution checks are advisory).

        Parameters
        ----------
        comparisons : list of dict
            Each dict has: name, data_hist, mc_hist, mc_errors (optional).

        Returns
        -------
        dict
            Keys: results (list of {name, chi2_ndf, advisory_warning}),
            advisory_only (always True).
        """
        results = []
        for comp in comparisons:
            chi2_per_ndf, ndf, chi2 = self._validator.chi2_ndf(
                data_hist=np.asarray(comp["data_hist"]),
                mc_hist=np.asarray(comp["mc_hist"]),
                mc_errors=comp.get("mc_errors"),
            )
            agreement = self._validator.check_agreement(chi2_per_ndf)
            results.append({
                "name": comp["name"],
                "chi2_ndf": float(chi2_per_ndf),
                "advisory_warning": not agreement["passes"],
            })

        return {
            "results": results,
            "advisory_only": True,
        }

    @staticmethod
    def _normalize_cutflow(cutflow) -> list:
        """Convert cutflow input to list of {cut, yield} dicts."""
        # Handle pandas DataFrame
        try:
            import pandas as pd
            if isinstance(cutflow, pd.DataFrame):
                rows = []
                for _, row in cutflow.iterrows():
                    cut_name = row.get("Cut", row.get("cut", ""))
                    yield_val = row.get("Yield", row.get("yield", 0.0))
                    rows.append({"cut": cut_name, "yield": float(yield_val)})
                return rows
        except ImportError:
            pass

        # Handle list of dicts
        rows = []
        for entry in cutflow:
            cut_name = entry.get("cut", entry.get("Cut", ""))
            yield_val = entry.get("yield", entry.get("Yield", 0.0))
            rows.append({"cut": cut_name, "yield": float(yield_val)})
        return rows
