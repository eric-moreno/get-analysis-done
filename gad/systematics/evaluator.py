"""Systematic uncertainty evaluator producing up/down template pairs.

Generates shifted histogram templates for each systematic source,
suitable for constructing pyhf histosys and normsys modifiers.
"""

import numpy as np


# Floor for clipping negative yields (avoids pyhf fit failures)
_YIELD_FLOOR = 1e-6


class SystematicEvaluator:
    """Evaluate systematic uncertainties as shifted histogram templates.

    All methods are stateless -- the class groups related operations logically.
    """

    @staticmethod
    def _clip_yields(yields):
        """Clip negative yields to floor value."""
        return [max(y, _YIELD_FLOOR) for y in yields]

    def evaluate_weight_variation(self, nominal_template, up_weights, down_weights,
                                  values, bin_edges):
        """Evaluate a weight-based systematic variation.

        Re-histograms the same events with shifted per-event weights.

        Parameters
        ----------
        nominal_template : dict
            Nominal template with keys: bin_edges, yields, errors.
        up_weights : array-like
            Per-event weights for the up variation.
        down_weights : array-like
            Per-event weights for the down variation.
        values : array-like
            Observable values (same events as nominal).
        bin_edges : array-like
            Bin edges to use for histogramming.

        Returns
        -------
        dict
            Keys: up_yields, down_yields, nominal_yields, type.
        """
        values = np.asarray(values, dtype=np.float64)
        up_weights = np.asarray(up_weights, dtype=np.float64)
        down_weights = np.asarray(down_weights, dtype=np.float64)
        bin_edges = np.asarray(bin_edges, dtype=np.float64)

        up_yields, _ = np.histogram(values, bins=bin_edges, weights=up_weights)
        down_yields, _ = np.histogram(values, bins=bin_edges, weights=down_weights)

        return {
            "up_yields": self._clip_yields(up_yields.tolist()),
            "down_yields": self._clip_yields(down_yields.tolist()),
            "nominal_yields": list(nominal_template["yields"]),
            "type": "histosys",
        }

    def evaluate_shape_variation(self, nominal_template, up_template, down_template):
        """Evaluate a shape-based systematic variation.

        Extracts yields from pre-computed shifted templates (e.g., from
        re-running selection with shifted inputs).

        Parameters
        ----------
        nominal_template : dict
            Nominal template with yields key.
        up_template : dict
            Up-variation template with yields key.
        down_template : dict
            Down-variation template with yields key.

        Returns
        -------
        dict
            Keys: up_yields, down_yields, nominal_yields, type.
        """
        return {
            "up_yields": self._clip_yields(list(up_template["yields"])),
            "down_yields": self._clip_yields(list(down_template["yields"])),
            "nominal_yields": list(nominal_template["yields"]),
            "type": "histosys",
        }

    def evaluate_normalization(self, nominal_yield, up_scale, down_scale):
        """Evaluate a normalization (rate-only) systematic.

        Parameters
        ----------
        nominal_yield : float
            Total nominal yield (used for reference, not in output).
        up_scale : float
            Multiplicative scale factor for up variation (e.g. 1.05).
        down_scale : float
            Multiplicative scale factor for down variation (e.g. 0.95).

        Returns
        -------
        dict
            Keys: type, hi, lo.
        """
        return {
            "type": "normsys",
            "hi": float(up_scale),
            "lo": float(down_scale),
        }

    def make_modifier(self, name, evaluation_result):
        """Create a pyhf-compatible modifier dict from an evaluation result.

        Parameters
        ----------
        name : str
            Modifier name (use build_modifier_name for correlation-aware naming).
        evaluation_result : dict
            Output from evaluate_weight_variation, evaluate_shape_variation,
            or evaluate_normalization.

        Returns
        -------
        dict
            pyhf modifier specification.
        """
        mod_type = evaluation_result["type"]
        if mod_type == "histosys":
            return {
                "name": name,
                "type": "histosys",
                "data": {
                    "hi_data": list(evaluation_result["up_yields"]),
                    "lo_data": list(evaluation_result["down_yields"]),
                },
            }
        elif mod_type == "normsys":
            return {
                "name": name,
                "type": "normsys",
                "data": {
                    "hi": evaluation_result["hi"],
                    "lo": evaluation_result["lo"],
                },
            }
        else:
            raise ValueError(f"Unknown modifier type: {mod_type}")

    @staticmethod
    def build_modifier_name(source, process=None, correlated=True):
        """Build modifier name following correlation conventions.

        Experimental systematics (correlated=True) share the same name across
        all processes/channels for 100% correlation. Theory systematics
        (correlated=False) get process-specific names for uncorrelated treatment.

        Parameters
        ----------
        source : str
            Systematic source name (e.g. "JES", "ISR").
        process : str, optional
            Process name (e.g. "qqbar"). Required if correlated=False.
        correlated : bool
            If True, return source name only. If False, return source_process.

        Returns
        -------
        str
            Modifier name.
        """
        if correlated:
            return source
        return f"{source}_{process}"
