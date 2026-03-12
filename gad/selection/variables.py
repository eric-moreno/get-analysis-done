"""Variable separation study: rank discriminating variables by KS distance and ROC AUC."""

import numpy as np
from scipy.stats import ks_2samp
from sklearn.metrics import roc_auc_score


def study_variable_separation(signal_arr, background_arr, variable_names):
    """Compute separation metrics for each variable between signal and background.

    For each variable, computes:
    - KS distance (two-sample Kolmogorov-Smirnov test)
    - KS p-value
    - ROC AUC (single-variable discriminating power, corrected to >= 0.5)
    - separation_power (= KS distance, used as primary ranking metric)

    Parameters
    ----------
    signal_arr : ak.Array or dict-like
        Signal events with fields for each variable.
    background_arr : ak.Array or dict-like
        Background events with fields for each variable.
    variable_names : list of str
        Variable names to study.

    Returns
    -------
    list of dict
        Results sorted by separation_power descending. Each dict has keys:
        variable, ks_distance, ks_pvalue, roc_auc, separation_power.
    """
    results = []
    for var in variable_names:
        sig = np.asarray(signal_arr[var], dtype=np.float64)
        bkg = np.asarray(background_arr[var], dtype=np.float64)

        # Filter NaN values
        sig = sig[~np.isnan(sig)]
        bkg = bkg[~np.isnan(bkg)]

        if len(sig) == 0 or len(bkg) == 0:
            results.append({
                "variable": var,
                "ks_distance": 0.0,
                "ks_pvalue": 1.0,
                "roc_auc": 0.5,
                "separation_power": 0.0,
            })
            continue

        # KS distance
        ks_stat, ks_pval = ks_2samp(sig, bkg)

        # ROC AUC (single-variable discriminating power)
        labels = np.concatenate([np.ones(len(sig)), np.zeros(len(bkg))])
        values = np.concatenate([sig, bkg])
        auc = roc_auc_score(labels, values)
        # Ensure AUC >= 0.5 (flip if anti-correlated)
        auc = max(auc, 1.0 - auc)

        results.append({
            "variable": var,
            "ks_distance": float(ks_stat),
            "ks_pvalue": float(ks_pval),
            "roc_auc": float(auc),
            "separation_power": float(ks_stat),
        })

    return sorted(results, key=lambda x: x["separation_power"], reverse=True)
