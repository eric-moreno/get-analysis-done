"""Overtraining detection and systematic robustness validation for BDTs.

Provides KS-test-based overtraining check and systematic shift robustness
evaluation. Designed for HEP BDT validation workflows.
"""
import numpy as np
from scipy.stats import ks_2samp


def check_overtraining(model, X_train, X_test, y_train, y_test,
                       threshold=0.05):
    """KS test on BDT score distributions for train vs test.

    Compares BDT output score distributions between training and test
    sets separately for signal (label=1) and background (label=0).
    Overtraining is flagged when the KS p-value falls below threshold.

    Parameters
    ----------
    model : XGBClassifier
        Trained XGBoost model with predict_proba method.
    X_train, X_test : array-like
        Training and test feature arrays.
    y_train, y_test : array-like
        Training and test labels (0 or 1).
    threshold : float
        KS p-value threshold below which overtraining is flagged
        (default 0.05).

    Returns
    -------
    dict
        Keys: signal, background (each with ks_statistic, ks_pvalue,
        passes), and overall_passes (True if both pass).
    """
    train_scores = model.predict_proba(X_train)[:, 1]
    test_scores = model.predict_proba(X_test)[:, 1]

    results = {}
    for label, label_name in [(1, "signal"), (0, "background")]:
        train_sel = train_scores[y_train == label]
        test_sel = test_scores[y_test == label]
        ks_stat, ks_pval = ks_2samp(train_sel, test_sel)
        results[label_name] = {
            "ks_statistic": float(ks_stat),
            "ks_pvalue": float(ks_pval),
            "passes": ks_pval >= threshold,
        }

    results["overall_passes"] = all(
        r["passes"] for r in results.values() if isinstance(r, dict)
    )
    return results


def check_systematic_robustness(model, X_nominal, X_shifted_dict,
                                feature_names):
    """Compare BDT scores on nominal vs systematically shifted samples.

    For each systematic variation, predicts BDT scores on shifted features
    and compares to nominal scores. A variation is considered stable if
    the maximum absolute BDT score shift is below 0.1.

    Parameters
    ----------
    model : XGBClassifier
        Trained XGBoost model with predict_proba method.
    X_nominal : array-like
        Nominal feature array.
    X_shifted_dict : dict
        Mapping of systematic name to shifted feature array
        (same shape as X_nominal).
    feature_names : list of str
        Feature names (for documentation; not used in computation).

    Returns
    -------
    dict
        Keyed by systematic name, each with max_shift, mean_shift,
        and stable (bool).
    """
    nominal_scores = model.predict_proba(X_nominal)[:, 1]
    results = {}

    for syst_name, X_shifted in X_shifted_dict.items():
        shifted_scores = model.predict_proba(X_shifted)[:, 1]
        diffs = np.abs(shifted_scores - nominal_scores)
        max_shift = float(np.max(diffs))
        mean_shift = float(np.mean(diffs))
        results[syst_name] = {
            "max_shift": max_shift,
            "mean_shift": mean_shift,
            "stable": max_shift < 0.1,
        }

    return results
