"""N-1 plots and variable distribution comparison plots."""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _apply_cuts_except(events, cuts, skip_index):
    """Apply all cuts except the one at skip_index, return filtered events."""
    op_map = {
        ">": np.greater, ">=": np.greater_equal,
        "<": np.less, "<=": np.less_equal,
        "==": np.equal, "!=": np.not_equal,
    }
    remaining = events
    for i, c in enumerate(cuts):
        if i == skip_index:
            continue
        values = remaining[c["variable"]]
        if c.get("absolute"):
            values = np.abs(values)
        mask = op_map[c["operator"]](values, c["threshold"])
        remaining = remaining[mask]
    return remaining


def plot_n_minus_1(events_dict, selection_engine, cut_index, output_path,
                   bins=50):
    """Generate an N-1 plot for a specific cut.

    Applies all cuts EXCEPT the one at cut_index, then plots the distribution
    of the variable for that cut across all processes.

    Parameters
    ----------
    events_dict : dict
        Mapping of process name to ak.Array of events.
    selection_engine : SelectionEngine
        Engine with registered cuts.
    cut_index : int
        Index of the cut to exclude (the variable being studied).
    output_path : str
        Path to save the PNG output.
    bins : int
        Number of histogram bins.
    """
    # Try to use mplhep for HEP-style plots
    try:
        import mplhep as hep
        hep.style.use("ATLAS")
    except (ImportError, Exception):
        pass

    cut = selection_engine._cuts[cut_index]
    var_name = cut["variable"]

    fig, ax = plt.subplots(figsize=(8, 6))

    for process_name, evts in events_dict.items():
        remaining = _apply_cuts_except(evts, selection_engine._cuts, cut_index)
        plot_vals = np.asarray(remaining[var_name])
        if cut.get("absolute"):
            plot_vals = np.abs(plot_vals)

        ax.hist(plot_vals, bins=bins, label=process_name,
                histtype="step", linewidth=2, density=True)

    # Draw cut line
    ax.axvline(cut["threshold"], color="red", linestyle="--",
               label=f"Cut: {cut['operator']} {cut['threshold']}")
    ax.set_xlabel(var_name)
    ax.set_ylabel("Normalized events")
    ax.set_title(f"N-1: {cut['name']}")
    ax.legend()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_variable_comparison(signal_arr, background_arr, variable_name,
                             output_path, bins=50):
    """Plot signal vs background distribution for a single variable.

    Signal shown as unfilled line, background as filled histogram.
    Both normalized to unit area for shape comparison.

    Parameters
    ----------
    signal_arr : ak.Array
        Signal events.
    background_arr : ak.Array
        Background events.
    variable_name : str
        Variable to plot.
    output_path : str
        Path to save the PNG output.
    bins : int
        Number of histogram bins.
    """
    try:
        import mplhep as hep
        hep.style.use("ATLAS")
    except (ImportError, Exception):
        pass

    sig_vals = np.asarray(signal_arr[variable_name])
    bkg_vals = np.asarray(background_arr[variable_name])

    fig, ax = plt.subplots(figsize=(8, 6))

    # Background as filled histogram
    ax.hist(bkg_vals, bins=bins, label="Background", alpha=0.5,
            density=True, color="blue")
    # Signal as unfilled line
    ax.hist(sig_vals, bins=bins, label="Signal", histtype="step",
            linewidth=2, density=True, color="red")

    ax.set_xlabel(variable_name)
    ax.set_ylabel("Normalized to unit area")
    ax.set_title(f"Signal vs Background: {variable_name}")
    ax.legend()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
