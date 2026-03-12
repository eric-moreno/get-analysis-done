"""Analysis configuration loader.

Reads a YAML analysis config file and exposes signal region definition,
unblinding settings (partial seed, allowed reblind count), control
region definitions, and experiment context fields (experiment name,
samples config, object overrides, centre-of-mass energy).
"""

from pathlib import Path

import yaml


class AnalysisConfig:
    """Loads and exposes analysis configuration from a YAML file.

    Parameters
    ----------
    config_path : str
        Path to the analysis config YAML file.

    Attributes
    ----------
    signal_region : dict
        Signal region definition with name and cuts.
    control_regions : list
        Control region definitions.
    partial_seed : int
        Fixed seed for 10% partial unblinding random sampling.
    allowed_reblind_count : int
        Maximum number of times re-blinding is permitted.
    experiment : str or None
        Experiment name for ExperimentContext lookup (e.g. ``"aleph"``).
    samples_config : dict or None
        Raw samples configuration (structured YAML or raw path mode).
    object_overrides : dict
        Per-analysis object definition overrides.
    sqrt_s : float or None
        Centre-of-mass energy in GeV.
    """

    def __init__(self, config_path: str):
        self._config_path = Path(config_path)
        self._load()

    def _load(self):
        """Parse the YAML config file."""
        with open(self._config_path) as f:
            data = yaml.safe_load(f) or {}

        self.signal_region = data.get("signal_region", {})
        self.control_regions = data.get("control_regions", [])

        unblinding = data.get("unblinding", {})
        self.partial_seed = unblinding.get("partial_seed", 42)
        self.allowed_reblind_count = unblinding.get("allowed_reblind_count", 1)

        # Experiment context fields (all optional for backward compatibility)
        self.experiment = data.get("experiment", None)
        self.samples_config = data.get("samples", None)
        self.object_overrides = data.get("object_overrides", {})
        self.sqrt_s = data.get("sqrt_s", None)
