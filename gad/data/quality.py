"""Data quality scan for ROOT file validation.

Checks file integrity, event counts, branch consistency, NaN/inf statistics,
and duplicate event detection. Produces structured reports with warnings
(proceed) vs blockers (halt) classification.
"""

import os
from collections import Counter
from pathlib import Path

import numpy as np
import uproot


class DataQualityScan:
    """Comprehensive data quality scanner for ROOT files.

    Usage::

        scan = DataQualityScan()
        report = scan.run(file_paths, tree_name="t", event_id_branch="n")
        yaml_dict = scan.to_yaml()
        markdown_str = scan.to_markdown()
    """

    def __init__(self):
        self._report = None

    def run(self, file_paths: list, tree_name: str = "t",
            event_id_branch: str = None, max_events: int = 10000) -> dict:
        """Run all quality checks on the given files.

        Parameters
        ----------
        file_paths : list of str
            Paths to ROOT files to check.
        tree_name : str
            Name of the TTree in each file.
        event_id_branch : str, optional
            Branch name containing unique event IDs for duplicate detection.
            If None, uses hash-based duplicate detection on first 5 numeric branches.
        max_events : int
            Maximum events to sample for NaN/inf and duplicate checks.

        Returns
        -------
        dict
            Structured report with sections: file_integrity, event_counts,
            branch_consistency, nan_inf, duplicates, warnings, blockers.
        """
        warnings = []
        blockers = []

        # 1. File integrity
        file_integrity = self._check_file_integrity(file_paths)
        for fi in file_integrity:
            if not fi["ok"]:
                blockers.append(f"File not found or unreadable: {fi['path']}")

        # Filter to only valid files for remaining checks
        valid_paths = [fi["path"] for fi in file_integrity if fi["ok"]]

        # 2. Event counts
        event_counts = self._check_event_counts(valid_paths, tree_name)

        # 3. Branch consistency
        branch_consistency = self._check_branch_consistency(valid_paths, tree_name)
        if not branch_consistency["consistent"] and len(valid_paths) > 1:
            warnings.append(
                f"Branch names inconsistent across files: "
                f"extra={branch_consistency.get('extra', [])}, "
                f"missing={branch_consistency.get('missing', [])}"
            )

        # 4. NaN/inf statistics
        nan_inf = self._check_nan_inf(valid_paths, tree_name, max_events)
        for entry in nan_inf:
            if entry["nan_count"] > 0 or entry["inf_count"] > 0:
                warnings.append(
                    f"Branch '{entry['branch']}' in {entry['file']}: "
                    f"{entry['nan_count']} NaN, {entry['inf_count']} inf"
                )

        # 5. Duplicate events
        duplicates = self._check_duplicates(
            valid_paths, tree_name, event_id_branch, max_events
        )
        if duplicates["count"] > 0:
            warnings.append(
                f"Found {duplicates['count']} duplicate events "
                f"({duplicates['fraction']:.2%}) via {duplicates['method']}"
            )

        self._report = {
            "file_integrity": file_integrity,
            "event_counts": event_counts,
            "branch_consistency": branch_consistency,
            "nan_inf": nan_inf,
            "duplicates": duplicates,
            "warnings": warnings,
            "blockers": blockers,
        }
        return self._report

    def to_yaml(self) -> dict:
        """Return the report as a dict for machine consumption."""
        if self._report is None:
            raise RuntimeError("Must call run() before to_yaml()")
        return dict(self._report)

    def to_markdown(self) -> str:
        """Return the report as a formatted markdown string."""
        if self._report is None:
            raise RuntimeError("Must call run() before to_markdown()")

        lines = []
        r = self._report

        lines.append("## Data Quality Report")
        lines.append("")

        # File Integrity
        lines.append("### File Integrity")
        lines.append("")
        for fi in r["file_integrity"]:
            status = "OK" if fi["ok"] else "MISSING"
            lines.append(f"- [{status}] {fi['path']}")
        lines.append("")

        # Event Counts
        lines.append("### Event Counts")
        lines.append("")
        lines.append(f"- Total events: {r['event_counts'].get('total', 0)}")
        for path, count in r["event_counts"].get("per_file", {}).items():
            lines.append(f"  - {Path(path).name}: {count}")
        lines.append("")

        # Branch Consistency
        lines.append("### Branch Consistency")
        lines.append("")
        bc = r["branch_consistency"]
        lines.append(f"- Consistent: {bc['consistent']}")
        if not bc["consistent"]:
            lines.append(f"- Common branches: {bc.get('common', [])}")
            lines.append(f"- Extra branches: {bc.get('extra', [])}")
            lines.append(f"- Missing branches: {bc.get('missing', [])}")
        lines.append("")

        # NaN/Inf
        lines.append("### NaN/Inf Statistics")
        lines.append("")
        for entry in r["nan_inf"]:
            if entry["nan_count"] > 0 or entry["inf_count"] > 0:
                lines.append(
                    f"- {entry['branch']} ({Path(entry['file']).name}): "
                    f"{entry['nan_count']} NaN, {entry['inf_count']} inf"
                )
        if not any(e["nan_count"] > 0 or e["inf_count"] > 0 for e in r["nan_inf"]):
            lines.append("- No NaN/inf values detected")
        lines.append("")

        # Duplicates
        lines.append("### Duplicate Events")
        lines.append("")
        d = r["duplicates"]
        lines.append(f"- Method: {d['method']}")
        lines.append(f"- Duplicates found: {d['count']} ({d['fraction']:.2%})")
        lines.append("")

        # Warnings / Blockers
        if r["warnings"]:
            lines.append("### Warnings")
            lines.append("")
            for w in r["warnings"]:
                lines.append(f"- {w}")
            lines.append("")

        if r["blockers"]:
            lines.append("### Blockers")
            lines.append("")
            for b in r["blockers"]:
                lines.append(f"- **{b}**")
            lines.append("")

        return "\n".join(lines)

    # -- Internal check methods --

    def _check_file_integrity(self, file_paths: list) -> list:
        """Check that each file exists and is readable."""
        result = []
        for path in file_paths:
            ok = os.path.isfile(path)
            if ok:
                try:
                    f = uproot.open(path)
                    f.close()
                except Exception:
                    ok = False
            result.append({"path": path, "ok": ok})
        return result

    def _check_event_counts(self, file_paths: list, tree_name: str) -> dict:
        """Count events per file and total."""
        per_file = {}
        total = 0
        for path in file_paths:
            try:
                f = uproot.open(path)
                tree = f[tree_name]
                count = tree.num_entries
                per_file[path] = count
                total += count
            except Exception:
                per_file[path] = 0
        return {"total": total, "per_file": per_file}

    def _check_branch_consistency(self, file_paths: list, tree_name: str) -> dict:
        """Check that all files have the same branch names."""
        if len(file_paths) == 0:
            return {"consistent": True, "common": [], "extra": [], "missing": []}

        branch_sets = []
        for path in file_paths:
            try:
                f = uproot.open(path)
                tree = f[tree_name]
                branch_sets.append(set(tree.keys()))
            except Exception:
                branch_sets.append(set())

        if len(branch_sets) <= 1:
            common = list(branch_sets[0]) if branch_sets else []
            return {"consistent": True, "common": common, "extra": [], "missing": []}

        # Use first file as reference
        reference = branch_sets[0]
        all_branches = set()
        for bs in branch_sets:
            all_branches |= bs

        common = set(reference)
        for bs in branch_sets[1:]:
            common &= bs

        extra = list(all_branches - reference)
        missing = list(reference - common)
        consistent = all(bs == reference for bs in branch_sets)

        return {
            "consistent": consistent,
            "common": sorted(common),
            "extra": sorted(extra),
            "missing": sorted(missing),
        }

    def _check_nan_inf(self, file_paths: list, tree_name: str,
                       max_events: int) -> list:
        """Check for NaN and inf values in numeric branches."""
        result = []
        for path in file_paths:
            try:
                f = uproot.open(path)
                tree = f[tree_name]
                for key in tree.keys():
                    typename = tree[key].typename
                    # Only check numeric types (float/double)
                    if not any(t in typename.lower() for t in
                               ("float", "double", "float32", "float64")):
                        continue
                    entry_stop = min(max_events, tree[key].num_entries)
                    arr = tree[key].array(entry_stop=entry_stop, library="np")
                    nan_count = int(np.sum(np.isnan(arr)))
                    inf_count = int(np.sum(np.isinf(arr)))
                    result.append({
                        "file": path,
                        "branch": key,
                        "nan_count": nan_count,
                        "inf_count": inf_count,
                        "checked_events": entry_stop,
                    })
            except Exception:
                pass
        return result

    def _check_duplicates(self, file_paths: list, tree_name: str,
                          event_id_branch: str, max_events: int) -> dict:
        """Check for duplicate events across all files."""
        if not file_paths:
            return {"count": 0, "fraction": 0.0, "method": "none", "details": []}

        if event_id_branch:
            return self._check_duplicates_by_id(
                file_paths, tree_name, event_id_branch, max_events
            )
        else:
            return self._check_duplicates_by_hash(
                file_paths, tree_name, max_events
            )

    def _check_duplicates_by_id(self, file_paths, tree_name, id_branch,
                                max_events):
        """Check for duplicate event IDs."""
        all_ids = []
        for path in file_paths:
            try:
                f = uproot.open(path)
                tree = f[tree_name]
                entry_stop = min(max_events, tree.num_entries)
                ids = tree[id_branch].array(entry_stop=entry_stop, library="np")
                all_ids.extend(ids.tolist())
            except Exception:
                pass

        total = len(all_ids)
        if total == 0:
            return {"count": 0, "fraction": 0.0, "method": "event_id", "details": []}

        counter = Counter(all_ids)
        dup_count = sum(c - 1 for c in counter.values() if c > 1)
        details = [{"id": k, "count": v} for k, v in counter.items() if v > 1]

        return {
            "count": dup_count,
            "fraction": dup_count / total if total > 0 else 0.0,
            "method": "event_id",
            "details": details,
        }

    def _check_duplicates_by_hash(self, file_paths, tree_name, max_events):
        """Check for duplicates by hashing first 5 numeric branches."""
        import hashlib

        hashes = []
        for path in file_paths:
            try:
                f = uproot.open(path)
                tree = f[tree_name]
                # Pick first 5 numeric branches
                numeric_keys = []
                for key in tree.keys():
                    typename = tree[key].typename
                    if any(t in typename.lower() for t in
                           ("float", "double", "int", "uint")):
                        numeric_keys.append(key)
                    if len(numeric_keys) >= 5:
                        break

                if not numeric_keys:
                    continue

                entry_stop = min(max_events, tree.num_entries)
                arrays = {k: tree[k].array(entry_stop=entry_stop, library="np")
                          for k in numeric_keys}
                n = entry_stop
                for i in range(n):
                    row_bytes = b""
                    for k in numeric_keys:
                        row_bytes += arrays[k][i].tobytes()
                    hashes.append(hashlib.md5(row_bytes).hexdigest())
            except Exception:
                pass

        total = len(hashes)
        if total == 0:
            return {"count": 0, "fraction": 0.0, "method": "hash", "details": []}

        counter = Counter(hashes)
        dup_count = sum(c - 1 for c in counter.values() if c > 1)

        return {
            "count": dup_count,
            "fraction": dup_count / total if total > 0 else 0.0,
            "method": "hash",
            "details": [],
        }
