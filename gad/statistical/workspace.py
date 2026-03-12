"""pyhf HistFactory workspace construction from templates and systematic modifiers.

Builds a valid pyhf workspace JSON spec with channels, samples, observations,
and measurements. Supports histosys, normsys, staterror, normfactor, and lumi
modifier types. Validates workspace against pyhf schema and optionally runs
background-only Asimov fit for NP pull validation.
"""

import json
from copy import deepcopy

import pyhf


class WorkspaceBuilder:
    """Build pyhf HistFactory workspace specifications.

    Assembles channels (regions), samples (processes), observations (data),
    modifiers (systematics), and measurements into a valid pyhf workspace.

    Parameters
    ----------
    poi_name : str
        Name of the parameter of interest (default: "mu").
    """

    def __init__(self, poi_name="mu"):
        self._poi_name = poi_name
        self._channels = {}   # name -> list of sample dicts
        self._observations = {}  # name -> list of floats

    def add_channel(self, name, observed):
        """Register a channel (region) with observed data.

        Parameters
        ----------
        name : str
            Channel name (e.g., "SR", "CR_top").
        observed : list of float
            Observed data bin counts. Use Asimov expectation for blinded SR.
        """
        self._channels[name] = []
        self._observations[name] = [float(v) for v in observed]

    def add_sample(self, channel_name, sample_name, data, modifiers=None):
        """Add a sample (process) to a channel.

        Parameters
        ----------
        channel_name : str
            Must be a previously registered channel.
        sample_name : str
            Sample name (e.g., "background", "signal").
        data : list of float
            Per-bin yields from template["yields"].
        modifiers : list of dict, optional
            List of pyhf modifier dicts to attach.

        Raises
        ------
        KeyError
            If channel_name has not been registered.
        """
        if channel_name not in self._channels:
            raise KeyError(f"Channel '{channel_name}' not registered. Call add_channel first.")
        sample = {
            "name": sample_name,
            "data": [float(v) for v in data],
            "modifiers": list(modifiers) if modifiers else [],
        }
        self._channels[channel_name].append(sample)

    def add_modifier(self, channel_name, sample_name, modifier):
        """Add a modifier to a specific sample in a channel.

        Parameters
        ----------
        channel_name : str
            Channel name.
        sample_name : str
            Sample name within the channel.
        modifier : dict
            pyhf modifier dict with keys: name, type, data.
            Supported types: histosys, normsys, staterror, normfactor, lumi.

        Raises
        ------
        KeyError
            If channel or sample not found.
        """
        for sample in self._channels[channel_name]:
            if sample["name"] == sample_name:
                sample["modifiers"].append(deepcopy(modifier))
                return
        raise KeyError(f"Sample '{sample_name}' not found in channel '{channel_name}'.")

    def add_staterror(self, channel_name, errors):
        """Add staterror modifier to all samples in a channel (Barlow-Beeston lite).

        One nuisance parameter per bin, shared across all samples in the channel.

        Parameters
        ----------
        channel_name : str
            Channel name.
        errors : list of float
            Per-bin absolute statistical uncertainties.
        """
        modifier = {
            "name": f"staterror_{channel_name}",
            "type": "staterror",
            "data": [float(e) for e in errors],
        }
        for sample in self._channels[channel_name]:
            sample["modifiers"].append(deepcopy(modifier))

    def add_signal(self, channel_name, sample_name):
        """Add normfactor modifier for the POI to a signal sample.

        Parameters
        ----------
        channel_name : str
            Channel name.
        sample_name : str
            Signal sample name.
        """
        self.add_modifier(channel_name, sample_name, {
            "name": self._poi_name,
            "type": "normfactor",
            "data": None,
        })

    def build(self):
        """Construct and validate the full pyhf workspace specification.

        Returns
        -------
        dict
            Valid pyhf workspace JSON spec.

        Raises
        ------
        pyhf.exceptions.InvalidSpecification
            If the workspace is malformed.
        RuntimeError
            If no channels have been added.
        """
        if not self._channels:
            raise RuntimeError("No channels added. Add at least one channel with samples.")

        channels = []
        observations = []

        for ch_name in sorted(self._channels.keys()):
            samples = self._channels[ch_name]
            channels.append({
                "name": ch_name,
                "samples": deepcopy(samples),
            })
            observations.append({
                "name": ch_name,
                "data": list(self._observations[ch_name]),
            })

        spec = {
            "channels": channels,
            "observations": observations,
            "measurements": [
                {
                    "name": "analysis",
                    "config": {
                        "poi": self._poi_name,
                        "parameters": [],
                    },
                }
            ],
            "version": "1.0.0",
        }

        # Validate against pyhf schema
        pyhf.Workspace(spec)

        return spec

    def validate_asimov(self, spec=None):
        """Run background-only Asimov fit and check NP pulls.

        Parameters
        ----------
        spec : dict, optional
            Workspace spec. If None, builds from current state.

        Returns
        -------
        dict
            Keys: valid (bool), pulls (dict name->pull), max_pull (float),
            fit_results (cabinetry FitResults).
        """
        import cabinetry

        if spec is None:
            spec = self.build()

        model, data = cabinetry.model_utils.model_and_data(spec, asimov=True)
        fit_results = cabinetry.fit.fit(model, data)

        # Extract NP pulls (bestfit - nominal) / uncertainty
        # For pyhf, nominal values are typically 0 for normsys and 1 for normfactor
        labels = fit_results.labels
        bestfit = fit_results.bestfit
        uncertainty = fit_results.uncertainty

        pulls = {}
        max_pull = 0.0
        for i, label in enumerate(labels):
            # Skip POI
            if label == self._poi_name:
                continue
            pull = float(bestfit[i])  # For constrained NPs, bestfit ~= pull from 0
            pulls[label] = pull
            if abs(pull) > max_pull:
                max_pull = abs(pull)

        return {
            "valid": max_pull < 0.5,
            "pulls": pulls,
            "max_pull": max_pull,
            "fit_results": fit_results,
        }

    @staticmethod
    def save(spec, path):
        """Save workspace spec to JSON file.

        Parameters
        ----------
        spec : dict
            Workspace spec.
        path : str
            Output file path.
        """
        with open(path, "w") as f:
            json.dump(spec, f, indent=2)

    @classmethod
    def load(cls, path):
        """Load workspace spec from JSON file.

        Parameters
        ----------
        path : str
            Path to JSON file.

        Returns
        -------
        dict
            Workspace spec.
        """
        with open(path) as f:
            return json.load(f)
