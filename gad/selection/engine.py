"""SelectionEngine: apply sequential cuts to awkward arrays with efficiency tracking."""

import numpy as np
import awkward as ak


class SelectionEngine:
    """Apply sequential cuts and track efficiency at each stage.

    Each cut is defined by a variable name, comparison operator, and threshold.
    The engine applies cuts in order and records a cutflow table with per-cut
    absolute and relative efficiency plus weighted yield.

    Parameters
    ----------
    name : str
        Name for this selection (e.g., "preselection", "signal_region").
    """

    _OP_MAP = {
        ">": np.greater,
        ">=": np.greater_equal,
        "<": np.less,
        "<=": np.less_equal,
        "==": np.equal,
        "!=": np.not_equal,
    }

    def __init__(self, name: str = "selection"):
        self.name = name
        self._cuts = []
        self._cutflow = []

    def add_cut(self, name: str, variable: str, operator: str, threshold: float,
                absolute: bool = False):
        """Register a cut to be applied.

        Parameters
        ----------
        name : str
            Human-readable cut name (e.g., "pt > 20 GeV").
        variable : str
            Branch/field name in the event array.
        operator : str
            One of ">", ">=", "<", "<=", "==", "!=".
        threshold : float
            Cut threshold value.
        absolute : bool
            If True, take abs(values) before applying the comparison.
        """
        if operator not in self._OP_MAP:
            raise ValueError(f"Unknown operator '{operator}'. "
                             f"Supported: {list(self._OP_MAP.keys())}")
        self._cuts.append({
            "name": name,
            "variable": variable,
            "operator": operator,
            "threshold": threshold,
            "absolute": absolute,
        })

    def apply(self, events: ak.Array, weights=None):
        """Apply all registered cuts sequentially.

        Parameters
        ----------
        events : ak.Array
            Input event array with fields matching cut variable names.
        weights : array-like, optional
            Per-event weights. If None, unit weights are used.

        Returns
        -------
        ak.Array
            Filtered events passing all cuts.
        """
        self._cutflow = []
        n_initial = len(events)
        remaining = events
        w = np.asarray(weights) if weights is not None else np.ones(n_initial)

        for cut in self._cuts:
            n_before = len(remaining)
            values = remaining[cut["variable"]]
            if cut["absolute"]:
                values = np.abs(values)

            op_fn = self._OP_MAP[cut["operator"]]
            mask = op_fn(values, cut["threshold"])
            remaining = remaining[mask]
            w = w[mask]

            n_after = len(remaining)
            self._cutflow.append({
                "name": cut["name"],
                "n_before": n_before,
                "n_after": n_after,
                "eff_relative": n_after / n_before if n_before > 0 else 0.0,
                "eff_absolute": n_after / n_initial if n_initial > 0 else 0.0,
                "weighted_yield": float(np.sum(w)),
            })

        return remaining

    def get_cutflow(self):
        """Return the cutflow as a list of dicts.

        Each entry has keys: name, n_before, n_after, eff_relative,
        eff_absolute, weighted_yield.
        """
        return self._cutflow

    def reset(self):
        """Clear cutflow data (preserves cut definitions)."""
        self._cutflow = []
