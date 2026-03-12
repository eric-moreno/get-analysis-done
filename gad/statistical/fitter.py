"""MLE fitting and expected CLs limit computation via cabinetry.

Wraps cabinetry.fit for maximum likelihood estimation and cabinetry.fit.limit
for expected 95% CL upper limits using the CLs method with Asimov datasets.
"""

import numpy as np
import pyhf

import cabinetry


class Fitter:
    """Statistical fitting and limit computation for pyhf workspaces.

    Parameters
    ----------
    workspace_spec : dict
        Valid pyhf workspace JSON specification (from WorkspaceBuilder.build()).
    """

    def __init__(self, workspace_spec):
        self._spec = workspace_spec
        self._model = None
        self._data = None

    def _get_model_and_data(self, asimov=False):
        """Lazily create model and data from workspace spec.

        Parameters
        ----------
        asimov : bool
            If True, use Asimov dataset instead of observed data.

        Returns
        -------
        tuple
            (model, data) for use with cabinetry.fit functions.
        """
        if asimov:
            # Always regenerate for Asimov to ensure correct POI value
            return cabinetry.model_utils.model_and_data(self._spec, asimov=True)

        if self._model is None:
            self._model, self._data = cabinetry.model_utils.model_and_data(self._spec)
        return self._model, self._data

    def fit(self, asimov=False, goodness_of_fit=False):
        """Run maximum likelihood estimation fit.

        Parameters
        ----------
        asimov : bool
            If True, fit Asimov dataset.
        goodness_of_fit : bool
            If True, compute saturated model goodness-of-fit p-value.

        Returns
        -------
        cabinetry.fit.results_containers.FitResults
            Fit results with bestfit, uncertainty, correlation, labels.
        """
        model, data = self._get_model_and_data(asimov=asimov)

        if goodness_of_fit:
            return cabinetry.fit.fit(
                model, data, goodness_of_fit=True
            )
        return cabinetry.fit.fit(model, data)

    def fit_asimov(self, poi_value=0.0):
        """Fit Asimov data generated at a specified POI value.

        Convenience method for background-only (poi=0) or signal+background
        (poi=1) hypothesis testing.

        Parameters
        ----------
        poi_value : float
            POI value for Asimov data generation. Default 0.0 (background-only).

        Returns
        -------
        cabinetry.fit.results_containers.FitResults
            Fit results.
        """
        model, data = cabinetry.model_utils.model_and_data(self._spec)
        # Generate Asimov data at the specified POI value
        asimov_data = pyhf.infer.calculators.generate_asimov_data(
            poi_value, data, model, None, None, None
        )
        return cabinetry.fit.fit(model, list(asimov_data))

    def expected_limit(self, bracket=None, maxsteps=100):
        """Compute expected 95% CL upper limit using CLs with Asimov dataset.

        Uses cabinetry.fit.limit for the CLs scan.

        Parameters
        ----------
        bracket : tuple of float, optional
            (low, high) POI values bracketing the limit. If None, uses
            (0.1, upper POI bound from model).
        maxsteps : int
            Maximum number of steps for limit finding.

        Returns
        -------
        dict
            Keys:
            - observed_limit: None (Asimov-only, no observed data limit)
            - expected_limit: float (median expected)
            - bands: dict with keys "-2", "-1", "+1", "+2" (sigma bands)
        """
        model, data = self._get_model_and_data(asimov=True)
        kwargs = {"maxsteps": maxsteps}
        if bracket is not None:
            kwargs["bracket"] = bracket
        limit_results = cabinetry.fit.limit(model, data, **kwargs)

        # cabinetry.fit.limit returns LimitResults with:
        # expected_limit: ndarray [−2σ, −1σ, median, +1σ, +2σ]
        # observed_limit: float
        exp = limit_results.expected_limit

        return {
            "observed_limit": None,  # Asimov only
            "expected_limit": float(exp[2]),  # median
            "bands": {
                "-2": float(exp[0]),
                "-1": float(exp[1]),
                "+1": float(exp[3]),
                "+2": float(exp[4]),
            },
        }

    def observed_limit(self, bracket=None, maxsteps=100):
        """Compute observed 95% CL upper limit using CLs with real data.

        Uses cabinetry.fit.limit with the observed data from the workspace
        specification (not Asimov).

        Parameters
        ----------
        bracket : tuple of float, optional
            (low, high) POI values bracketing the limit.
        maxsteps : int
            Maximum number of steps for limit finding.

        Returns
        -------
        dict
            Keys:
            - observed_limit: float (observed 95% CL upper limit)
            - expected_limit: float (median expected)
            - bands: dict with keys "-2", "-1", "+1", "+2" (sigma bands)
        """
        model, data = self._get_model_and_data(asimov=False)
        kwargs = {"maxsteps": maxsteps}
        if bracket is not None:
            kwargs["bracket"] = bracket
        limit_results = cabinetry.fit.limit(model, data, **kwargs)

        exp = limit_results.expected_limit

        return {
            "observed_limit": float(limit_results.observed_limit),
            "expected_limit": float(exp[2]),  # median
            "bands": {
                "-2": float(exp[0]),
                "-1": float(exp[1]),
                "+1": float(exp[3]),
                "+2": float(exp[4]),
            },
        }
