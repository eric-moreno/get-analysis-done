"""RegionValidator: purity checks and data/MC agreement for control/validation regions."""

import numpy as np


class RegionValidator:
    """Validate control and validation regions.

    Provides purity computation (target background fraction) and
    chi-squared/ndf data/MC agreement tests.
    """

    def compute_purity(self, events_dict: dict, region_mask_fn,
                       target_process: str) -> float:
        """Compute purity = N_target / N_total in a region.

        Parameters
        ----------
        events_dict : dict
            Mapping of process name to event arrays (or any sequence with
            ``len``).
        region_mask_fn : callable
            Function accepting an event array and returning a boolean mask.
        target_process : str
            Name of the target background process.

        Returns
        -------
        float
            Purity value in [0, 1].  Returns 0.0 if no events pass.
        """
        n_target = 0
        n_total = 0
        for process, evts in events_dict.items():
            mask = region_mask_fn(evts)
            n_in_region = int(np.sum(mask))
            n_total += n_in_region
            if process == target_process:
                n_target = n_in_region
        return n_target / n_total if n_total > 0 else 0.0

    def check_purity(self, purity: float, threshold: float = 0.5) -> dict:
        """Check whether purity meets the threshold.

        Parameters
        ----------
        purity : float
            Computed purity value.
        threshold : float
            Minimum acceptable purity (default 0.5, per SLCT-07).

        Returns
        -------
        dict
            Keys: purity, threshold, passes.
        """
        return {
            "purity": purity,
            "threshold": threshold,
            "passes": purity >= threshold,
        }

    def chi2_ndf(self, data_hist: np.ndarray, mc_hist: np.ndarray,
                 mc_errors: np.ndarray = None) -> tuple:
        """Compute chi-squared/ndf for data vs MC histogram comparison.

        Uses combined Poisson (data) and MC statistical errors.  Bins with
        ``data + mc < 5`` are skipped as having insufficient statistics.

        Parameters
        ----------
        data_hist : array-like
            Observed data bin counts.
        mc_hist : array-like
            Expected MC bin counts.
        mc_errors : array-like, optional
            MC statistical errors per bin.  Defaults to ``sqrt(mc)`` (Poisson).

        Returns
        -------
        tuple of (chi2_per_ndf, ndf, chi2)
        """
        data_hist = np.asarray(data_hist, dtype=float)
        mc_hist = np.asarray(mc_hist, dtype=float)

        if mc_errors is None:
            mc_errors = np.sqrt(np.maximum(mc_hist, 0.0))

        mc_errors = np.asarray(mc_errors, dtype=float)

        # Skip low-statistics bins
        sufficient = (data_hist + mc_hist) >= 5
        d = data_hist[sufficient]
        m = mc_hist[sufficient]
        me = mc_errors[sufficient]

        ndf = len(d)
        if ndf == 0:
            return (0.0, 0, 0.0)

        # Combined error: Poisson on data + MC stat error
        sigma2 = d + me ** 2  # var(data) = data (Poisson), var(mc) = me^2
        # Protect against zero variance
        sigma2 = np.maximum(sigma2, 1e-10)

        chi2 = float(np.sum((d - m) ** 2 / sigma2))
        chi2_per_ndf = chi2 / ndf

        return (chi2_per_ndf, ndf, chi2)

    def check_agreement(self, chi2_ndf_value: float,
                        threshold: float = 2.0) -> dict:
        """Check whether data/MC agreement meets the threshold.

        Parameters
        ----------
        chi2_ndf_value : float
            Computed chi2/ndf value.
        threshold : float
            Maximum acceptable chi2/ndf (default 2.0, per user decision).

        Returns
        -------
        dict
            Keys: chi2_ndf, threshold, passes.
        """
        return {
            "chi2_ndf": chi2_ndf_value,
            "threshold": threshold,
            "passes": chi2_ndf_value < threshold,
        }
