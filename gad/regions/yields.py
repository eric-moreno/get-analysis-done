"""YieldTable: Background yield aggregation per process and region."""

import numpy as np

try:
    import pandas as pd
except ImportError:
    pd = None


class YieldTable:
    """Aggregate background yields per process and region.

    Produces formatted yield tables with stat and syst uncertainties,
    and computes total background with error propagation in quadrature.
    """

    def __init__(self):
        self._processes = {}  # name -> {region_yields, is_signal}

    def add_process(self, name: str, region_yields: dict,
                    is_signal: bool = False):
        """Register a process with per-region yields.

        Parameters
        ----------
        name : str
            Process name (e.g. 'ttbar', 'wjets').
        region_yields : dict
            Mapping of region_name -> {yield, stat_err, syst_err}.
        is_signal : bool
            If True, exclude from total background computation.
        """
        self._processes[name] = {
            "region_yields": region_yields,
            "is_signal": is_signal,
        }

    def build(self):
        """Build formatted yield table as a DataFrame.

        Returns
        -------
        pd.DataFrame
            Rows = processes, columns = regions.
            Cell values formatted as 'yield +/- stat +/- syst'.
        """
        if pd is None:
            raise ImportError("pandas is required for YieldTable.build()")

        all_regions = set()
        for proc_info in self._processes.values():
            all_regions.update(proc_info["region_yields"].keys())
        regions = sorted(all_regions)

        rows = {}
        for proc_name, proc_info in self._processes.items():
            row = {}
            for region in regions:
                entry = proc_info["region_yields"].get(region)
                if entry is not None:
                    row[region] = (
                        f"{entry['yield']:.1f} +/- {entry['stat_err']:.1f} "
                        f"+/- {entry['syst_err']:.1f}"
                    )
                else:
                    row[region] = "-"
            rows[proc_name] = row

        df = pd.DataFrame.from_dict(rows, orient="index")
        df = df[regions]  # ensure column order
        return df

    def total_background(self) -> dict:
        """Compute total background per region with error propagation.

        Signal processes (is_signal=True) are excluded.
        Errors are propagated in quadrature.

        Returns
        -------
        dict
            Mapping of region_name -> {yield, stat_err, syst_err}.
        """
        region_totals = {}

        for proc_name, proc_info in self._processes.items():
            if proc_info["is_signal"]:
                continue
            for region, entry in proc_info["region_yields"].items():
                if region not in region_totals:
                    region_totals[region] = {
                        "yield": 0.0,
                        "stat_err_sq": 0.0,
                        "syst_err_sq": 0.0,
                    }
                region_totals[region]["yield"] += entry["yield"]
                region_totals[region]["stat_err_sq"] += entry["stat_err"] ** 2
                region_totals[region]["syst_err_sq"] += entry["syst_err"] ** 2

        result = {}
        for region, totals in region_totals.items():
            result[region] = {
                "yield": totals["yield"],
                "stat_err": float(np.sqrt(totals["stat_err_sq"])),
                "syst_err": float(np.sqrt(totals["syst_err_sq"])),
            }

        return result

    def to_dict(self) -> dict:
        """Return machine-readable nested structure.

        Returns
        -------
        dict
            Mapping of process_name -> region_name -> {yield, stat_err, syst_err}.
        """
        result = {}
        for proc_name, proc_info in self._processes.items():
            result[proc_name] = {}
            for region, entry in proc_info["region_yields"].items():
                result[proc_name][region] = {
                    "yield": entry["yield"],
                    "stat_err": entry["stat_err"],
                    "syst_err": entry["syst_err"],
                }
        return result
