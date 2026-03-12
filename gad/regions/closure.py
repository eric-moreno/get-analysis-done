"""ClosureTester: VR prediction validation using CR-extrapolated transfer factors."""

import numpy as np

from gad.regions.estimation import EstimationComparator
from gad.regions.validator import RegionValidator


class ClosureTester:
    """Validate VR predictions against observed data using closure tests.

    Closure tests compare CR-extrapolated predictions to VR observed data
    using a pull criterion: |observed - predicted| / total_uncertainty < threshold.
    The default threshold is 2.0 sigma (per BKGD-01).
    """

    def __init__(self, threshold: float = 2.0):
        """Initialize closure tester.

        Parameters
        ----------
        threshold : float
            Maximum allowed pull in sigma units (default 2.0).
        """
        self.threshold = threshold
        self._estimator = EstimationComparator()
        self._validator = RegionValidator()

    def run_closure_test(self, cr_data: float, cr_mc: float, vr_mc: float,
                         vr_observed: float, total_uncertainty: float,
                         name: str = "") -> dict:
        """Run a single closure test for one VR.

        Uses the transfer factor method (CR data / CR MC) to extrapolate
        from CR to VR, then computes the pull against observed data.

        Parameters
        ----------
        cr_data : float
            Observed data yield in the control region.
        cr_mc : float
            MC prediction in the control region.
        vr_mc : float
            MC prediction in the validation region.
        vr_observed : float
            Observed data yield in the validation region.
        total_uncertainty : float
            Total (stat + syst combined) uncertainty on the prediction.
        name : str
            Label for this closure test.

        Returns
        -------
        dict
            Keys: name, predicted, observed, pull, passes, threshold,
            total_uncertainty.
        """
        estimate = self._estimator.transfer_factor_estimate(
            cr_data=cr_data, cr_mc=cr_mc, sr_mc=vr_mc
        )
        predicted = estimate["yield"]

        pull = abs(vr_observed - predicted) / total_uncertainty if total_uncertainty > 0 else 0.0

        return {
            "name": name,
            "predicted": predicted,
            "observed": vr_observed,
            "pull": float(pull),
            "passes": pull < self.threshold,
            "threshold": self.threshold,
            "total_uncertainty": total_uncertainty,
        }

    def run_all_closure_tests(self, vr_configs: list) -> dict:
        """Run closure tests for multiple VRs.

        Parameters
        ----------
        vr_configs : list of dict
            Each dict has keys: cr_data, cr_mc, vr_mc, vr_observed,
            total_uncertainty, and optionally name.

        Returns
        -------
        dict
            Keys: all_pass, results (list), n_pass, n_fail.
        """
        results = []
        for cfg in vr_configs:
            result = self.run_closure_test(
                cr_data=cfg["cr_data"],
                cr_mc=cfg["cr_mc"],
                vr_mc=cfg["vr_mc"],
                vr_observed=cfg["vr_observed"],
                total_uncertainty=cfg["total_uncertainty"],
                name=cfg.get("name", ""),
            )
            results.append(result)

        n_pass = sum(1 for r in results if r["passes"])
        n_fail = len(results) - n_pass

        return {
            "all_pass": n_fail == 0,
            "results": results,
            "n_pass": n_pass,
            "n_fail": n_fail,
        }

    def validate_data_mc(self, distributions: list,
                         threshold: float = 2.0) -> list:
        """Batch data/MC agreement check across multiple distributions.

        Wraps RegionValidator.chi2_ndf and check_agreement for convenience.

        Parameters
        ----------
        distributions : list of dict
            Each dict has keys: name, data_hist, mc_hist, mc_errors (optional).
        threshold : float
            Maximum chi2/ndf for passing (default 2.0).

        Returns
        -------
        list of dict
            Each with keys: name, chi2_ndf, passes, threshold.
        """
        results = []
        for dist in distributions:
            chi2_per_ndf, ndf, chi2 = self._validator.chi2_ndf(
                data_hist=np.asarray(dist["data_hist"]),
                mc_hist=np.asarray(dist["mc_hist"]),
                mc_errors=dist.get("mc_errors"),
            )
            agreement = self._validator.check_agreement(chi2_per_ndf,
                                                        threshold=threshold)
            results.append({
                "name": dist["name"],
                "chi2_ndf": agreement["chi2_ndf"],
                "passes": agreement["passes"],
                "threshold": agreement["threshold"],
            })

        return results
