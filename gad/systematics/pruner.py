"""Systematic uncertainty pruner -- removes negligible systematics.

Prunes systematic variations whose maximum fractional effect on any bin
yield falls below a configurable threshold, reducing workspace complexity
without sacrificing physics sensitivity.
"""

import numpy as np


class SystematicPruner:
    """Prune systematics with negligible effect on bin yields.

    Parameters
    ----------
    threshold : float
        Minimum fractional effect to keep a systematic. Default 0.005 (0.5%).
        A systematic is kept if any bin has |shifted - nominal| / nominal > threshold
        for either the up or down variation.
    """

    def __init__(self, threshold=0.005):
        self.threshold = threshold

    def should_keep(self, nominal_yields, up_yields, down_yields):
        """Determine if a systematic has significant effect.

        Computes maximum fractional effect across all bins for both up and
        down variations. Returns True if max effect exceeds threshold.

        Parameters
        ----------
        nominal_yields : list or array-like
            Nominal bin yields.
        up_yields : list or array-like
            Up-variation bin yields.
        down_yields : list or array-like
            Down-variation bin yields.

        Returns
        -------
        bool
            True if systematic should be kept (significant effect).
        """
        nominal = np.asarray(nominal_yields, dtype=np.float64)
        up = np.asarray(up_yields, dtype=np.float64)
        down = np.asarray(down_yields, dtype=np.float64)

        # Only consider bins where nominal > 0
        valid = nominal > 0

        if not np.any(valid):
            return False

        # Fractional effect per bin
        up_frac = np.abs(up[valid] - nominal[valid]) / nominal[valid]
        down_frac = np.abs(down[valid] - nominal[valid]) / nominal[valid]

        max_effect = max(np.max(up_frac), np.max(down_frac))
        return bool(max_effect > self.threshold)

    def prune_systematics(self, evaluations):
        """Filter a list of systematic evaluations, keeping only significant ones.

        Parameters
        ----------
        evaluations : list of dict
            Each dict must have keys: name, up_yields, down_yields, nominal_yields.

        Returns
        -------
        dict
            Keys:
            - kept: list of evaluation dicts that passed the threshold
            - pruned: list of names that were removed
            - summary: dict with n_total, n_kept, n_pruned, threshold
        """
        kept = []
        pruned = []

        for ev in evaluations:
            if self.should_keep(ev["nominal_yields"], ev["up_yields"], ev["down_yields"]):
                kept.append(ev)
            else:
                pruned.append(ev["name"])

        return {
            "kept": kept,
            "pruned": pruned,
            "summary": {
                "n_total": len(evaluations),
                "n_kept": len(kept),
                "n_pruned": len(pruned),
                "threshold": self.threshold,
            },
        }
