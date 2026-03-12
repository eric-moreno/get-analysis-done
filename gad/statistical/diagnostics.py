"""Fit diagnostics: NP pulls, ranking, correlation matrix, GoF, likelihood scan, constraint analysis.

Wraps cabinetry visualization and fit utilities to produce publication-ready
diagnostic plots (PDF format with mplhep experiment styling) and constraint
analysis summaries for the top dominant nuisance parameters.
"""

import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import cabinetry


class Diagnostics:
    """Fit diagnostic suite for pyhf workspaces.

    Produces NP pull plots, ranking plots, correlation matrices,
    likelihood scans, goodness-of-fit tests, and in-situ constraint
    analysis for the most impactful nuisance parameters.

    Parameters
    ----------
    workspace_spec : dict
        Valid pyhf workspace JSON specification.
    output_dir : str
        Directory for saving diagnostic figures.
    experiment_style : str
        mplhep experiment style name (e.g., "ATLAS", "CMS").
    """

    def __init__(self, workspace_spec, output_dir="figures", experiment_style="ATLAS"):
        self._spec = workspace_spec
        self._output_dir = output_dir
        self._experiment_style = experiment_style

        # Ensure output directory exists
        Path(self._output_dir).mkdir(parents=True, exist_ok=True)

        # Set mplhep experiment style with graceful fallback
        try:
            import mplhep
            style = getattr(mplhep.style, experiment_style, None)
            if style is not None:
                plt.style.use(style)
        except (ImportError, AttributeError):
            pass

    def _get_model_and_data(self, asimov=False):
        """Get pyhf model and data from workspace spec.

        Parameters
        ----------
        asimov : bool
            If True, use Asimov dataset.

        Returns
        -------
        tuple
            (model, data)
        """
        return cabinetry.model_utils.model_and_data(self._spec, asimov=asimov)

    def pull_plot(self, fit_results):
        """Generate nuisance parameter pull plot as PDF.

        Parameters
        ----------
        fit_results : cabinetry.fit.results_containers.FitResults
            Results from a maximum likelihood fit.

        Returns
        -------
        str
            Path to the saved pull plot PDF.
        """
        cabinetry.visualize.pulls(
            fit_results,
            figure_folder=self._output_dir,
            close_figure=True,
            save_figure=True,
        )
        return str(Path(self._output_dir) / "pulls.pdf")

    def ranking_plot(self, fit_results=None):
        """Generate nuisance parameter ranking plot as PDF.

        Computes ranking (impact on POI) and visualizes results.

        Parameters
        ----------
        fit_results : cabinetry.fit.results_containers.FitResults, optional
            Pre-computed fit results. If None, runs a fit first.

        Returns
        -------
        tuple
            (ranking_results, figure_path) where ranking_results is a
            cabinetry RankingResults and figure_path is the PDF path.
        """
        model, data = self._get_model_and_data()
        ranking_results = cabinetry.fit.ranking(
            model, data, fit_results=fit_results,
        )
        cabinetry.visualize.ranking(
            ranking_results,
            figure_folder=self._output_dir,
            close_figure=True,
            save_figure=True,
        )
        return ranking_results, str(Path(self._output_dir) / "ranking.pdf")

    def correlation_matrix(self, fit_results):
        """Generate parameter correlation matrix plot as PDF.

        Parameters
        ----------
        fit_results : cabinetry.fit.results_containers.FitResults
            Results from a maximum likelihood fit.

        Returns
        -------
        str
            Path to the saved correlation matrix PDF.
        """
        cabinetry.visualize.correlation_matrix(
            fit_results,
            figure_folder=self._output_dir,
            pruning_threshold=0.1,
            close_figure=True,
            save_figure=True,
        )
        return str(Path(self._output_dir) / "correlation_matrix.pdf")

    def likelihood_scan(self, par_name, par_range=None, n_steps=21):
        """Run likelihood scan for a parameter and save plot as PDF.

        Parameters
        ----------
        par_name : str
            Name of the parameter to scan.
        par_range : tuple of float, optional
            (low, high) scan range. If None, cabinetry auto-determines.
        n_steps : int
            Number of scan steps.

        Returns
        -------
        tuple
            (scan_results, figure_path) where scan_results is a
            cabinetry ScanResults and figure_path is the PDF path.
        """
        model, data = self._get_model_and_data()
        scan_results = cabinetry.fit.scan(
            model, data, par_name,
            par_range=par_range,
            n_steps=n_steps,
        )
        cabinetry.visualize.scan(
            scan_results,
            figure_folder=self._output_dir,
            close_figure=True,
            save_figure=True,
        )
        return scan_results, str(Path(self._output_dir) / f"scan_{par_name}.pdf")

    def gof_test(self):
        """Run saturated model goodness-of-fit test.

        Returns
        -------
        dict
            Keys: gof_stat (float), p_value (float), saturated (bool).
        """
        model, data = self._get_model_and_data()
        fit_results = cabinetry.fit.fit(model, data, goodness_of_fit=True)

        return {
            "gof_stat": float(fit_results.best_twice_nll),
            "p_value": float(fit_results.goodness_of_fit),
            "saturated": True,
        }

    def constraint_analysis(self, fit_results, ranking_results, top_n=5):
        """Analyze constraints on the most impactful nuisance parameters.

        For the top_n highest-impact NPs from ranking, compares pre-fit
        vs post-fit uncertainty and computes the constraint factor.

        Parameters
        ----------
        fit_results : cabinetry.fit.results_containers.FitResults
            Fit results with bestfit and uncertainty arrays.
        ranking_results : cabinetry.fit.results_containers.RankingResults
            Ranking results with impact information.
        top_n : int
            Number of top NPs to include.

        Returns
        -------
        list of dict
            Sorted by descending absolute impact on mu. Each dict has:
            name, pre_fit_unc, post_fit_unc, constraint_factor, impact_on_mu.
        """
        # Compute impact on mu for each NP from ranking
        # Impact = max(|postfit_up|, |postfit_down|)
        impacts = []
        for i, label in enumerate(ranking_results.labels):
            impact = max(
                abs(float(ranking_results.postfit_up[i])),
                abs(float(ranking_results.postfit_down[i])),
            )
            impacts.append((label, impact))

        # Sort by impact descending, take top_n
        impacts.sort(key=lambda x: x[1], reverse=True)
        top_nps = impacts[:top_n]

        # Build constraint analysis for each top NP
        # Map fit_results labels to indices
        fit_label_idx = {label: i for i, label in enumerate(fit_results.labels)}

        results = []
        for np_name, impact_on_mu in top_nps:
            if np_name not in fit_label_idx:
                continue

            idx = fit_label_idx[np_name]
            post_fit_unc = float(fit_results.uncertainty[idx])

            # Pre-fit uncertainty: 1.0 for normalized NPs (standard convention)
            pre_fit_unc = 1.0

            constraint_factor = post_fit_unc / pre_fit_unc

            results.append({
                "name": np_name,
                "pre_fit_unc": pre_fit_unc,
                "post_fit_unc": post_fit_unc,
                "constraint_factor": constraint_factor,
                "impact_on_mu": impact_on_mu,
            })

        return results

    def run_all_diagnostics(self):
        """Run full diagnostic suite: fit, pulls, ranking, correlation, GoF, constraints.

        Returns
        -------
        dict
            Keys: fit_results, ranking_results, constraint_analysis, gof,
            figure_paths (dict of name -> path).
        """
        model, data = self._get_model_and_data()
        fit_results = cabinetry.fit.fit(model, data)

        # Pull plot
        pull_path = self.pull_plot(fit_results)

        # Ranking plot
        ranking_results, ranking_path = self.ranking_plot(fit_results=fit_results)

        # Correlation matrix
        corr_path = self.correlation_matrix(fit_results)

        # GoF
        gof = self.gof_test()

        # Constraint analysis
        constraints = self.constraint_analysis(fit_results, ranking_results, top_n=5)

        figure_paths = {
            "pulls": pull_path,
            "ranking": ranking_path,
            "correlation_matrix": corr_path,
        }

        return {
            "fit_results": fit_results,
            "ranking_results": ranking_results,
            "constraint_analysis": constraints,
            "gof": gof,
            "figure_paths": figure_paths,
        }
