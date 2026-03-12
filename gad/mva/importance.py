"""Feature importance extraction, categorization evaluation, and shape-vs-counting comparison.

Provides utilities for analysing trained BDT models: extracting feature
importance rankings, evaluating whether event categorization improves
sensitivity, and comparing shape-based vs counting-based analysis strategies.
"""
import math


def _asimov_significance(s, b, sigma_b=0.0):
    """Compute expected Asimov significance.

    Parameters
    ----------
    s : float
        Expected signal yield.
    b : float
        Expected background yield.
    sigma_b : float
        Background uncertainty (default 0, stat-only).

    Returns
    -------
    float
        Expected significance Z. Returns 0.0 if s <= 0 or b <= 0.

    Notes
    -----
    Uses the Asimov approximation:
    - If sigma_b == 0: Z = sqrt(2 * ((s+b)*ln(1+s/b) - s))
    - If sigma_b > 0: full formula with background uncertainty term.

    TODO: Consolidate with gad.selection.cutflow.asimov_significance
    when that module is available.
    """
    if s <= 0 or b <= 0:
        return 0.0

    if sigma_b <= 0:
        # Simple case without systematic uncertainty
        term = (s + b) * math.log(1.0 + s / b) - s
        return math.sqrt(2.0 * term) if term > 0 else 0.0

    # Full formula with background uncertainty
    sigma_b2 = sigma_b ** 2
    term1 = (s + b) * math.log((s + b) * (b + sigma_b2) / (b**2 + (s + b) * sigma_b2))
    term2 = (b**2 / sigma_b2) * math.log(1.0 + sigma_b2 * s / (b * (b + sigma_b2)))
    val = 2.0 * (term1 - term2)
    return math.sqrt(val) if val > 0 else 0.0


def get_feature_importance(model, feature_names, importance_type="gain"):
    """Extract and rank feature importances from a trained XGBoost model.

    Parameters
    ----------
    model : XGBClassifier
        Trained XGBoost model.
    feature_names : list of str
        Feature names corresponding to training columns.
    importance_type : str
        Importance type passed to get_score (default "gain").

    Returns
    -------
    list of dict
        Sorted by importance descending. Each dict has:
        feature, importance, importance_fraction.
    """
    booster = model.get_booster()
    scores = booster.get_score(importance_type=importance_type)

    # Build full list (features not in scores have zero importance)
    results = []
    for name in feature_names:
        results.append({
            "feature": name,
            "importance": scores.get(name, 0.0),
        })

    total = sum(r["importance"] for r in results)
    for r in results:
        r["importance_fraction"] = r["importance"] / total if total > 0 else 0.0

    results.sort(key=lambda x: x["importance"], reverse=True)
    return results


def evaluate_categorization(yields_inclusive, yields_categorized):
    """Compare inclusive vs categorized expected significance.

    Parameters
    ----------
    yields_inclusive : dict
        {"signal": float, "background": float} for inclusive selection.
    yields_categorized : list of dict
        List of {"signal": float, "background": float} per category.

    Returns
    -------
    dict
        inclusive_significance, categorized_significance,
        improvement_percent, recommendation ("categorized" if > 5% gain,
        else "inclusive"), per_category_significances.
    """
    z_inclusive = _asimov_significance(
        yields_inclusive["signal"], yields_inclusive["background"])

    per_cat_z = []
    for cat in yields_categorized:
        z_cat = _asimov_significance(cat["signal"], cat["background"])
        per_cat_z.append(z_cat)

    # Combined significance: quadrature sum
    z_combined = math.sqrt(sum(z**2 for z in per_cat_z))

    if z_inclusive > 0:
        improvement = (z_combined - z_inclusive) / z_inclusive * 100.0
    else:
        improvement = 0.0 if z_combined == 0 else float("inf")

    recommendation = "categorized" if improvement > 5.0 else "inclusive"

    return {
        "inclusive_significance": z_inclusive,
        "categorized_significance": z_combined,
        "improvement_percent": improvement,
        "recommendation": recommendation,
        "per_category_significances": per_cat_z,
    }


def compare_shape_vs_counting(shape_significance, counting_significance):
    """Compare shape-based vs counting-based analysis sensitivity.

    Parameters
    ----------
    shape_significance : float
        Expected significance from shape (binned template) analysis.
    counting_significance : float
        Expected significance from counting (cut-and-count) analysis.

    Returns
    -------
    dict
        shape_Z, counting_Z, improvement_percent, recommendation
        ("shape" if shape > counting by > 10%, "counting" if counting
        > shape by > 10%, "either" otherwise), and warning about
        stat-only nature of the comparison.
    """
    if counting_significance > 0:
        improvement = (shape_significance - counting_significance) / counting_significance * 100.0
    elif shape_significance > 0:
        improvement = float("inf")
    else:
        improvement = 0.0

    if improvement > 10.0:
        recommendation = "shape"
    elif improvement < -10.0:
        recommendation = "counting"
    else:
        recommendation = "either"

    return {
        "shape_Z": shape_significance,
        "counting_Z": counting_significance,
        "improvement_percent": improvement,
        "recommendation": recommendation,
        "warning": (
            "This is a stat-only comparison. Systematics evaluated in "
            "Phase 4 may change the relative sensitivity of shape vs "
            "counting approaches."
        ),
    }
