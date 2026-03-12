"""Variable inventory scanner for ROOT file branch cataloging.

Scans all branches in a ROOT TTree and reports:
  - name, typename, num_entries, is_jagged
  - min, max, mean, fill_fraction (fraction of non-zero values)

Used by the data explorer agent to produce Wave 1 variable reports.
"""

import numpy as np
import uproot


def scan_variable_inventory(file_path: str, tree_name: str = "t",
                            max_events: int = 10000) -> list:
    """Scan all branches in a ROOT file and return metadata with statistics.

    Parameters
    ----------
    file_path : str
        Path to the ROOT file.
    tree_name : str
        Name of the TTree. Defaults to ``"t"``.
    max_events : int
        Maximum number of events to read for computing statistics.
        Limits memory usage on large files.

    Returns
    -------
    list of dict
        Each dict has keys: name, typename, num_entries, is_jagged,
        min, max, mean, fill_fraction.
    """
    f = uproot.open(file_path)
    tree = f[tree_name]
    result = []

    for key in tree.keys():
        branch = tree[key]
        typename = branch.typename
        is_jagged = "[]" in typename
        num_entries = branch.num_entries

        # Load a subset for statistics
        entry_stop = min(max_events, num_entries) if max_events else None
        arr = branch.array(entry_stop=entry_stop, library="ak")

        # Flatten jagged arrays before computing statistics
        if is_jagged:
            import awkward as ak
            flat = np.asarray(ak.flatten(arr))
        else:
            flat = np.asarray(arr)

        # Compute statistics on the flat numpy array
        if len(flat) > 0:
            stat_min = float(np.nanmin(flat))
            stat_max = float(np.nanmax(flat))
            stat_mean = float(np.nanmean(flat))
            fill_fraction = float(np.count_nonzero(flat) / len(flat))
        else:
            stat_min = None
            stat_max = None
            stat_mean = None
            fill_fraction = 0.0

        result.append({
            "name": key,
            "typename": typename,
            "num_entries": num_entries,
            "is_jagged": is_jagged,
            "min": stat_min,
            "max": stat_max,
            "mean": stat_mean,
            "fill_fraction": fill_fraction,
        })

    return result


class VariableInventory:
    """Wrapper around scan_variable_inventory with output formatting.

    Parameters
    ----------
    file_path : str
        Path to the ROOT file to scan.
    tree_name : str
        Name of the TTree.
    max_events : int
        Maximum events for statistics computation.
    """

    def __init__(self, file_path: str, tree_name: str = "t",
                 max_events: int = 10000):
        self._file_path = file_path
        self._data = scan_variable_inventory(file_path, tree_name, max_events)

    def to_json(self) -> list:
        """Return the inventory as a list of dicts (JSON-serializable)."""
        return self._data

    def to_markdown(self) -> str:
        """Return the inventory as a formatted markdown table."""
        lines = []
        lines.append("| Name | Type | Entries | Jagged | Min | Max | Mean | Fill% |")
        lines.append("|------|------|---------|--------|-----|-----|------|-------|")
        for entry in self._data:
            jagged_str = "Yes" if entry["is_jagged"] else "No"
            min_str = f"{entry['min']:.4g}" if entry["min"] is not None else "N/A"
            max_str = f"{entry['max']:.4g}" if entry["max"] is not None else "N/A"
            mean_str = f"{entry['mean']:.4g}" if entry["mean"] is not None else "N/A"
            fill_str = f"{entry['fill_fraction'] * 100:.1f}%"
            lines.append(
                f"| {entry['name']} | {entry['typename']} | {entry['num_entries']} "
                f"| {jagged_str} | {min_str} | {max_str} | {mean_str} | {fill_str} |"
            )
        return "\n".join(lines)
