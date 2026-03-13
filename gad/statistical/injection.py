"""Signal injection tests for pre-unblinding validation.

Injects signal at known mu values into Asimov data and verifies the fit
recovers mu_hat within 1*sigma_fit, validating the statistical machinery.
"""

import cabinetry
import pyhf


class SignalInjectionTester:
    """Test signal recovery by injecting at known mu values.

    Parameters
    ----------
    workspace_spec : dict
        Valid pyhf workspace JSON specification.
    """

    def __init__(self, workspace_spec):
        self._spec = workspace_spec

    def test_injection(self, mu_injected):
        """Inject signal at mu_injected and fit to recover mu_hat.

        Parameters
        ----------
        mu_injected : float
            Signal strength to inject.

        Returns
        -------
        dict
            Keys: mu_injected, mu_hat, sigma_fit, pull, passes.
        """
        model, data = cabinetry.model_utils.model_and_data(self._spec)

        # Generate Asimov data at the injected mu value
        asimov_data = pyhf.infer.calculators.generate_asimov_data(
            mu_injected, data, model, None, None, None
        )

        # Fit the pseudo-data
        fit_results = cabinetry.fit.fit(model, list(asimov_data))

        # Extract mu_hat and sigma_fit
        poi_idx = list(fit_results.labels).index(model.config.poi_name)
        mu_hat = float(fit_results.bestfit[poi_idx])
        sigma_fit = float(fit_results.uncertainty[poi_idx])

        # Compute pull (handle sigma_fit=0)
        if sigma_fit == 0.0:
            pull = float("inf")
        else:
            pull = abs(mu_hat - mu_injected) / sigma_fit

        passes = pull < 1.0

        return {
            "mu_injected": mu_injected,
            "mu_hat": mu_hat,
            "sigma_fit": sigma_fit,
            "pull": pull,
            "passes": passes,
        }

    def run_all(self, mu_values=(0.5, 1.0, 2.0)):
        """Run injection tests at multiple mu values.

        Parameters
        ----------
        mu_values : tuple of float
            Signal strengths to test.

        Returns
        -------
        dict
            Keys: tests (list of result dicts), all_pass (bool),
            recovery_rate (float between 0.0 and 1.0).
        """
        tests = [self.test_injection(mu) for mu in mu_values]
        passing = sum(1 for t in tests if t["passes"])
        return {
            "tests": tests,
            "all_pass": all(t["passes"] for t in tests),
            "recovery_rate": passing / len(tests) if tests else 0.0,
        }
