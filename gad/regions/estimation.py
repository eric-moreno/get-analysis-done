"""EstimationComparator: MC-based vs data-driven background estimation comparison."""

import numpy as np


class EstimationComparator:
    """Compare MC-based and data-driven background estimation methods.

    For each major background, evaluate both approaches and recommend the
    one with smaller total uncertainty (per SLCT-08).
    """

    def mc_based_estimate(self, mc_yield: float, mc_stat_err: float,
                          mc_syst_frac: float = 0.0) -> dict:
        """Compute MC-based background estimate.

        Parameters
        ----------
        mc_yield : float
            MC prediction for the background yield.
        mc_stat_err : float
            MC statistical uncertainty.
        mc_syst_frac : float
            Fractional systematic uncertainty (e.g. 0.2 for 20%).

        Returns
        -------
        dict
            Keys: yield, stat_err, syst_err, total_err, method.
        """
        syst_err = mc_yield * mc_syst_frac
        total_err = np.sqrt(mc_stat_err ** 2 + syst_err ** 2)
        return {
            "yield": mc_yield,
            "stat_err": mc_stat_err,
            "syst_err": syst_err,
            "total_err": float(total_err),
            "method": "mc_based",
        }

    def transfer_factor_estimate(self, cr_data: float, cr_mc: float,
                                 sr_mc: float, cr_data_err: float = None,
                                 cr_mc_err: float = None,
                                 sr_mc_err: float = None) -> dict:
        """Compute data-driven estimate using the transfer factor method.

        Transfer factor TF = cr_data / cr_mc.
        Estimated SR yield = TF * sr_mc.

        Parameters
        ----------
        cr_data : float
            Observed data in the control region.
        cr_mc : float
            MC prediction in the control region.
        sr_mc : float
            MC prediction in the signal region.
        cr_data_err, cr_mc_err, sr_mc_err : float, optional
            Errors on each quantity.  Default to sqrt(N) (Poisson).

        Returns
        -------
        dict
            Keys: yield, transfer_factor, stat_err, total_err, method.
        """
        # Default to Poisson errors
        if cr_data_err is None:
            cr_data_err = np.sqrt(max(cr_data, 0.0))
        if cr_mc_err is None:
            cr_mc_err = np.sqrt(max(cr_mc, 0.0))
        if sr_mc_err is None:
            sr_mc_err = np.sqrt(max(sr_mc, 0.0))

        tf = cr_data / cr_mc if cr_mc > 0 else 0.0
        estimated_yield = tf * sr_mc

        # Error propagation: delta_yield / yield = sqrt((delta_TF/TF)^2 + (delta_sr_mc/sr_mc)^2)
        # delta_TF / TF = sqrt((delta_cr_data/cr_data)^2 + (delta_cr_mc/cr_mc)^2)
        if cr_data > 0 and cr_mc > 0 and sr_mc > 0:
            rel_tf = np.sqrt((cr_data_err / cr_data) ** 2 +
                             (cr_mc_err / cr_mc) ** 2)
            rel_sr = sr_mc_err / sr_mc
            rel_total = np.sqrt(rel_tf ** 2 + rel_sr ** 2)
            stat_err = estimated_yield * rel_total
        else:
            stat_err = 0.0

        return {
            "yield": float(estimated_yield),
            "transfer_factor": float(tf),
            "stat_err": float(stat_err),
            "total_err": float(stat_err),
            "method": "transfer_factor",
        }

    def abcd_estimate(self, region_a: float, region_b: float,
                      region_c: float, region_d: float = None) -> dict:
        """Compute ABCD method estimate.

        The SR estimate (region D) = B * C / A.  Region D input is ignored
        (it is what we are predicting).

        Parameters
        ----------
        region_a, region_b, region_c : float
            Observed yields in sideband regions A, B, C.
        region_d : float, optional
            Ignored (predicted by the method).

        Returns
        -------
        dict
            Keys: yield, stat_err, total_err, method.
        """
        estimated_yield = (region_b * region_c / region_a) if region_a > 0 else 0.0

        # Propagate Poisson errors: delta_D/D = sqrt(1/A + 1/B + 1/C)
        if region_a > 0 and region_b > 0 and region_c > 0:
            rel_err = np.sqrt(1.0 / region_a + 1.0 / region_b + 1.0 / region_c)
            stat_err = estimated_yield * rel_err
        else:
            stat_err = 0.0

        return {
            "yield": float(estimated_yield),
            "stat_err": float(stat_err),
            "total_err": float(stat_err),
            "method": "abcd",
        }

    def compare_methods(self, *estimates) -> dict:
        """Compare estimation methods and recommend the best one.

        Parameters
        ----------
        *estimates : dict
            Each must have keys ``method`` and ``total_err``.

        Returns
        -------
        dict
            Keys: estimates, recommended (method name), improvement_percent.
        """
        sorted_est = sorted(estimates, key=lambda e: e["total_err"])
        best = sorted_est[0]
        second = sorted_est[1] if len(sorted_est) > 1 else best

        improvement = (
            (second["total_err"] - best["total_err"]) / second["total_err"] * 100.0
            if second["total_err"] > 0 else 0.0
        )

        return {
            "estimates": list(estimates),
            "recommended": best["method"],
            "improvement_percent": float(improvement),
        }
