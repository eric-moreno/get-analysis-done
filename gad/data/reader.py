"""DataReader: thin uproot wrapper with blinding enforcement.

All agent data access should go through DataReader so that blinding
is enforced transparently. Agents call ``reader.load_sample('qqbar',
branches=[...])`` and get back arrays with blinding auto-enforced.

Two input modes:
  - **Raw path mode:** Quick exploration without a config file.
    Use ``DataReader.from_path(path)`` or ``DataReader().load_path(path)``.
  - **Config mode:** Production usage with YAML config listing samples.
    Use ``DataReader(config_path=..., state_path=...)``.
"""

import glob as globmod
from pathlib import Path

import uproot
import yaml

from ..blinding.module import BlindingManager


class DataReader:
    """Thin wrapper around uproot with blinding enforcement.

    Parameters
    ----------
    config_path : str, optional
        Path to analysis config YAML. If provided along with state_path,
        enables sample-based loading with blinding enforcement.
    state_path : str, optional
        Path to STATE.md for BlindingManager. Required for blinding checks.
    """

    def __init__(self, config_path: str = None, state_path: str = None):
        self._config = None
        self._blinding = None
        self._samples = {}
        self._raw_path = None

        if config_path is not None:
            self._load_config(config_path)
        if config_path is not None and state_path is not None:
            self._blinding = BlindingManager(state_path, config_path)

    def _load_config(self, config_path: str):
        """Load the analysis config and associated samples config."""
        with open(config_path) as f:
            self._config = yaml.safe_load(f) or {}

        # Load samples from either inline or referenced file
        samples_config_path = self._config.get("samples_config")
        if samples_config_path:
            with open(samples_config_path) as f:
                samples_data = yaml.safe_load(f) or {}
            self._samples = samples_data.get("samples", {})
        elif "samples" in self._config:
            self._samples = self._config["samples"]

    @classmethod
    def from_path(cls, path: str, state_path: str = None):
        """Create a reader in raw-path mode (no config file).

        Parameters
        ----------
        path : str
            Path to a ROOT file for direct access.
        state_path : str, optional
            Path to STATE.md (unused in raw-path mode but stored).

        Returns
        -------
        DataReader
        """
        reader = cls()
        reader._raw_path = path
        return reader

    def load_path(self, path: str, tree_name: str = None, branches=None,
                  library: str = "ak", entry_stop: int = None):
        """Read a ROOT file directly (raw exploration mode, no blinding).

        Parameters
        ----------
        path : str
            Path to a ROOT file.
        tree_name : str, optional
            Name of the TTree. Defaults to ``"t"`` (ALEPH convention).
        branches : list of str, optional
            Branch names to load. If None, loads all branches.
        library : str
            Output library: ``"ak"`` (awkward) or ``"pd"`` (pandas).
        entry_stop : int, optional
            Maximum number of entries to read.

        Returns
        -------
        awkward.Array or pandas.DataFrame
        """
        if tree_name is None:
            tree_name = "t"

        f = uproot.open(path)
        tree = f[tree_name]
        kwargs = {"library": library}
        if branches is not None:
            kwargs["expressions"] = branches
        if entry_stop is not None:
            kwargs["entry_stop"] = entry_stop

        return tree.arrays(**kwargs)

    def load_sample(self, sample_name: str, branches=None,
                    library: str = "ak", entry_stop: int = None):
        """Load a named sample from config with blinding enforcement.

        Parameters
        ----------
        sample_name : str
            Sample name as defined in the samples config.
        branches : list of str, optional
            Branch names to load.
        library : str
            Output library: ``"ak"`` (default) or ``"pd"``.
        entry_stop : int, optional
            Maximum number of entries to read.

        Returns
        -------
        awkward.Array or pandas.DataFrame

        Raises
        ------
        KeyError
            If sample_name is not found in the config.
        BlindingViolationError
            If blinding policy denies access to the sample's region.
        """
        sample_info = self._resolve_sample(sample_name)
        region = self._determine_region(sample_info)

        # Check blinding BEFORE loading data to avoid unnecessary I/O
        if self._blinding is not None and region == "signal_region":
            # check_access with events=None will raise if access denied
            self._blinding.check_access(region, events=None)

        file_paths = self._resolve_files(sample_info)
        tree_name = sample_info.get("tree_name", "t")

        sources = {p: tree_name for p in file_paths}
        kwargs = {"library": library}
        if branches is not None:
            kwargs["expressions"] = branches
        if entry_stop is not None:
            kwargs["entry_stop"] = entry_stop

        events = uproot.concatenate(sources, **kwargs)

        # For partial unblinding, apply sampling after loading
        if (self._blinding is not None and region == "signal_region"
                and library == "ak"):
            import awkward as ak
            import numpy as np
            # check_access returns filtered events for PARTIAL_10PCT
            # Convert length to numpy for the blinding manager
            np_proxy = np.ones(len(events))
            filtered = self._blinding.check_access(region, events=np_proxy)
            if filtered is not None and len(filtered) < len(events):
                # Build boolean mask from the blinding manager's sampling
                rng = np.random.RandomState(self._blinding._config.partial_seed)
                mask = rng.random(len(events)) < 0.1
                events = events[mask]

        return events

    def scan_branches(self, path: str, tree_name: str = None):
        """Return branch metadata without loading event data.

        Parameters
        ----------
        path : str
            Path to a ROOT file.
        tree_name : str, optional
            Name of the TTree. Defaults to ``"t"``.

        Returns
        -------
        list of dict
            Each dict has keys: name, typename, num_entries, is_jagged.
        """
        if tree_name is None:
            tree_name = "t"

        f = uproot.open(path)
        tree = f[tree_name]
        result = []
        for key in tree.keys():
            branch = tree[key]
            typename = branch.typename
            result.append({
                "name": key,
                "typename": typename,
                "num_entries": branch.num_entries,
                "is_jagged": "[]" in typename,
            })
        return result

    def _resolve_sample(self, sample_name: str) -> dict:
        """Look up a sample in the loaded config.

        Raises KeyError if not found.
        """
        if sample_name not in self._samples:
            raise KeyError(
                f"Sample '{sample_name}' not found in config. "
                f"Available samples: {list(self._samples.keys())}"
            )
        return self._samples[sample_name]

    def _resolve_files(self, sample_info: dict) -> list:
        """Resolve file paths from sample info (handles glob, list, single)."""
        paths_raw = sample_info.get("paths", [])
        if isinstance(paths_raw, str):
            paths_raw = [paths_raw]

        resolved = []
        for p in paths_raw:
            if "*" in p or "?" in p:
                resolved.extend(sorted(globmod.glob(p)))
            else:
                resolved.append(p)
        return resolved

    def _determine_region(self, sample_info: dict) -> str:
        """Return the region tag for a sample (signal_region or control_region)."""
        return sample_info.get("region", "control_region")


def create_reader(input_path: str, state_path: str = None) -> DataReader:
    """Auto-detect input mode and create appropriate DataReader.

    If input_path ends with ``.yaml`` or ``.yml``, treats it as a config file.
    Otherwise, treats it as a raw ROOT file path.

    Parameters
    ----------
    input_path : str
        Path to either a YAML config file or a ROOT file.
    state_path : str, optional
        Path to STATE.md for blinding enforcement.

    Returns
    -------
    DataReader
    """
    p = Path(input_path)
    if p.suffix in (".yaml", ".yml"):
        return DataReader(config_path=input_path, state_path=state_path)
    else:
        return DataReader.from_path(input_path, state_path=state_path)
