"""Experiment context loader.

Loads experiment-specific configuration from a multi-file YAML directory
structure at ``experiments/{name}/``.  Each experiment directory contains
required files (detector description, object definitions) and optional
files (MC generators, performance, references).

This module is experiment-agnostic -- adding a new experiment requires
only creating a new directory with the appropriate YAML files, not
changing any Python code.
"""

from pathlib import Path

import yaml


class ExperimentContext:
    """Loads experiment context from ``experiments/{name}/`` directory.

    The directory must contain at least ``detector.yaml`` and
    ``objects.yaml``.  Optional files (``mc_generators.yaml``,
    ``performance.yaml``, ``references.yaml``) are loaded when present
    and default to empty dicts when absent.

    Parameters
    ----------
    experiment_name : str
        Name of the experiment (must match directory name).
    experiments_dir : str
        Path to the parent ``experiments/`` directory.

    Attributes
    ----------
    detector : dict
        Detector description (subsystems, collider info, run periods).
    objects : dict
        Object definitions with selection cuts and metadata.
    mc_generators : dict
        Monte Carlo generator information (empty if file absent).
    performance : dict
        Detector performance metrics (empty if file absent).
    references : dict
        Key papers and references (empty if file absent).

    Raises
    ------
    FileNotFoundError
        If the experiment directory or a required file does not exist.
    """

    REQUIRED_FILES = ["detector.yaml", "objects.yaml"]
    OPTIONAL_FILES = ["mc_generators.yaml", "performance.yaml", "references.yaml"]

    def __init__(self, experiment_name: str, experiments_dir: str = "experiments"):
        self._base = Path(experiments_dir) / experiment_name
        if not self._base.exists():
            raise FileNotFoundError(
                f"Experiment '{experiment_name}' not found at {self._base}"
            )
        self._load()

    def _load(self):
        """Load all required and optional YAML files."""
        for fname in self.REQUIRED_FILES:
            path = self._base / fname
            if not path.exists():
                raise FileNotFoundError(f"Required file missing: {path}")

        self.detector = self._load_yaml("detector.yaml")
        self.objects = self._load_yaml("objects.yaml")
        self.mc_generators = self._load_yaml("mc_generators.yaml") or {}
        self.performance = self._load_yaml("performance.yaml") or {}
        self.references = self._load_yaml("references.yaml") or {}

    def _load_yaml(self, filename: str) -> dict:
        """Read and parse a single YAML file.

        Parameters
        ----------
        filename : str
            Name of the YAML file relative to the experiment directory.

        Returns
        -------
        dict or None
            Parsed YAML content, or None if the file does not exist.
        """
        path = self._base / filename
        if not path.exists():
            return None
        with open(path) as f:
            return yaml.safe_load(f) or {}

    def get_object_definition(self, obj_name: str, overrides: dict = None) -> dict:
        """Get an object definition with optional per-analysis overrides.

        Parameters
        ----------
        obj_name : str
            Name of the object (e.g. ``"good_track"``).
        overrides : dict, optional
            Mapping of object name to override fields.  Only overrides
            matching ``obj_name`` are applied.

        Returns
        -------
        dict
            The object definition, with overrides merged if provided.
            Returns an empty dict if the object is not defined.
        """
        defn = dict(self.objects.get(obj_name, {}))
        if overrides and obj_name in overrides:
            defn.update(overrides[obj_name])
        return defn
