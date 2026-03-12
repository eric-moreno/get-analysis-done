"""RegionDesigner: define control and validation regions by cut inversion."""

import numpy as np
from gad.selection.engine import SelectionEngine


class RegionDesigner:
    """Design control and validation regions via cut inversion.

    Control regions invert one or more signal region cuts to enrich a
    specific background process.  Validation regions sit kinematically
    between the CR and SR by using inverted cuts with tighter thresholds.

    Parameters
    ----------
    sr_cuts : list of dict
        Signal region cut definitions, each with keys: variable, operator,
        threshold, absolute.
    """

    _INV_MAP = {
        ">": "<=",
        ">=": "<",
        "<": ">=",
        "<=": ">",
        "==": "!=",
        "!=": "==",
    }

    def __init__(self, sr_cuts: list):
        self.sr_cuts = sr_cuts

    def define_cr(self, name: str, target_background: str,
                  invert_cuts: list, additional_cuts: list = None) -> dict:
        """Define a control region by inverting specified SR cuts.

        Parameters
        ----------
        name : str
            Region name (e.g. ``'CR_qqbar'``).
        target_background : str
            Background process this CR targets.
        invert_cuts : list of str
            Variable names of SR cuts to invert.
        additional_cuts : list of dict, optional
            Extra cuts specific to this CR.

        Returns
        -------
        dict
            Region definition with name, target_background, cuts, type.
        """
        cr_cuts = []
        for cut in self.sr_cuts:
            if cut["variable"] in invert_cuts:
                inverted = dict(cut)
                inverted["operator"] = self._INV_MAP[cut["operator"]]
                cr_cuts.append(inverted)
            else:
                cr_cuts.append(dict(cut))

        if additional_cuts:
            cr_cuts.extend(additional_cuts)

        return {
            "name": name,
            "target_background": target_background,
            "cuts": cr_cuts,
            "type": "control",
        }

    def define_vr(self, name: str, target_background: str,
                  tighten_cuts: dict = None, additional_cuts: list = None) -> dict:
        """Define a validation region kinematically between CR and SR.

        The VR uses the same inverted operators as the CR (for cuts whose
        variables appear in *tighten_cuts*) but with tighter thresholds that
        move the boundary closer to the SR.

        Parameters
        ----------
        name : str
            Region name (e.g. ``'VR_qqbar'``).
        target_background : str
            Background process this VR validates.
        tighten_cuts : dict, optional
            Mapping of variable name to new (tighter) threshold.  The
            corresponding SR cut operator is inverted.
        additional_cuts : list of dict, optional
            Extra cuts for this VR.

        Returns
        -------
        dict
            Region definition with type ``'validation'``.
        """
        tighten_cuts = tighten_cuts or {}
        vr_cuts = []
        for cut in self.sr_cuts:
            if cut["variable"] in tighten_cuts:
                modified = dict(cut)
                modified["operator"] = self._INV_MAP[cut["operator"]]
                modified["threshold"] = tighten_cuts[cut["variable"]]
                vr_cuts.append(modified)
            else:
                vr_cuts.append(dict(cut))

        if additional_cuts:
            vr_cuts.extend(additional_cuts)

        return {
            "name": name,
            "target_background": target_background,
            "cuts": vr_cuts,
            "type": "validation",
        }

    def get_region_mask(self, region: dict, events) -> np.ndarray:
        """Return a boolean mask for events passing all region cuts.

        Delegates cut application to :class:`gad.selection.engine.SelectionEngine`
        so that cut logic is shared rather than reimplemented.

        Parameters
        ----------
        region : dict
            Region definition (as returned by :meth:`define_cr` / :meth:`define_vr`).
        events : awkward array or similar
            Events to evaluate.

        Returns
        -------
        np.ndarray
            Boolean array of shape ``(len(events),)``.
        """
        n_total = len(events)
        engine = SelectionEngine(name=region.get("name", "region"))
        for cut in region["cuts"]:
            engine.add_cut(
                name=f"{cut['variable']} {cut['operator']} {cut['threshold']}",
                variable=cut["variable"],
                operator=cut["operator"],
                threshold=cut["threshold"],
                absolute=cut.get("absolute", False),
            )
        filtered = engine.apply(events)
        n_pass = len(filtered)

        # Build mask by applying cuts cumulatively via individual masks
        # Re-derive full boolean mask from cuts
        mask = np.ones(n_total, dtype=bool)
        for cut in region["cuts"]:
            values = np.asarray(events[cut["variable"]])
            if cut.get("absolute", False):
                values = np.abs(values)
            op_fn = SelectionEngine._OP_MAP[cut["operator"]]
            mask &= op_fn(values, cut["threshold"])

        return mask
