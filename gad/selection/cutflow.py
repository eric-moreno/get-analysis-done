"""Cut-flow table formatting, Asimov significance, and binned template creation."""

import numpy as np
import pandas as pd


def format_cutflow_table(cutflow):
    """Convert engine cutflow list-of-dicts to a formatted pandas DataFrame.

    Parameters
    ----------
    cutflow : list of dict
        Output from SelectionEngine.get_cutflow(). Each dict has keys:
        name, n_before, n_after, eff_relative, eff_absolute, weighted_yield.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: Cut, N_before, N_after, Eff_rel (%), Eff_abs (%), Yield.
    """
    if not cutflow:
        return pd.DataFrame(columns=["Cut", "N_before", "N_after",
                                     "Eff_rel", "Eff_abs", "Yield"])

    rows = []
    for entry in cutflow:
        rows.append({
            "Cut": entry["name"],
            "N_before": entry["n_before"],
            "N_after": entry["n_after"],
            "Eff_rel": entry["eff_relative"] * 100.0,
            "Eff_abs": entry["eff_absolute"] * 100.0,
            "Yield": entry["weighted_yield"],
        })
    return pd.DataFrame(rows)


def asimov_significance(s, b, sigma_b=0.0):
    """Compute expected significance using the Asimov formula.

    Reference: Cowan et al., EPJC 71 (2011) 1554.

    Parameters
    ----------
    s : float
        Expected signal yield.
    b : float
        Expected background yield.
    sigma_b : float
        Background uncertainty (0 for stat-only).

    Returns
    -------
    float
        Expected significance Z.
    """
    if b <= 0 or s <= 0:
        return 0.0

    if sigma_b > 0:
        # With background uncertainty
        n = s + b
        term1 = n * np.log((n * (b + sigma_b**2)) / (b**2 + n * sigma_b**2))
        term2 = (b**2 / sigma_b**2) * np.log(
            1.0 + (sigma_b**2 * s) / (b * (b + sigma_b**2))
        )
        return float(np.sqrt(2.0 * (term1 - term2)))
    else:
        # Simple Asimov (stat-only)
        return float(np.sqrt(2.0 * ((s + b) * np.log(1.0 + s / b) - s)))


def create_binned_template(values, weights=None, bins=20, range=None,
                           strategy="quantile"):
    """Create a binned histogram template for pyhf consumption.

    Parameters
    ----------
    values : array-like
        Values to bin.
    weights : array-like, optional
        Per-event weights. If None, unit weights are used.
    bins : int
        Number of bins.
    range : tuple of (float, float), optional
        Histogram range. If None, derived from data.
    strategy : str
        Binning strategy: "quantile" (equal statistics) or "uniform".

    Returns
    -------
    dict
        Keys: bin_edges, yields, errors, n_bins, integral.
    """
    values = np.asarray(values, dtype=np.float64)
    if weights is None:
        weights = np.ones(len(values))
    else:
        weights = np.asarray(weights, dtype=np.float64)

    # Filter NaN
    mask = ~np.isnan(values)
    values = values[mask]
    weights = weights[mask]

    if strategy == "quantile":
        # Compute bin edges from quantiles for roughly equal statistics
        quantiles = np.linspace(0, 100, bins + 1)
        bin_edges = np.percentile(values, quantiles)
        # Ensure unique edges (can happen with repeated values)
        bin_edges = np.unique(bin_edges)
        if len(bin_edges) < 2:
            bin_edges = np.array([values.min(), values.max()])
        actual_bins = len(bin_edges) - 1
    else:
        # Uniform binning
        if range is not None:
            lo, hi = range
        else:
            lo, hi = float(values.min()), float(values.max())
            if lo == hi:
                lo -= 0.5
                hi += 0.5
        bin_edges = np.linspace(lo, hi, bins + 1)
        actual_bins = bins

    # Compute histogram
    yields, _ = np.histogram(values, bins=bin_edges, weights=weights)
    # Errors: sqrt of sum of weights squared per bin
    w2, _ = np.histogram(values, bins=bin_edges, weights=weights**2)
    errors = np.sqrt(w2)

    return {
        "bin_edges": bin_edges.tolist(),
        "yields": yields.tolist(),
        "errors": errors.tolist(),
        "n_bins": actual_bins,
        "integral": float(np.sum(yields)),
    }
