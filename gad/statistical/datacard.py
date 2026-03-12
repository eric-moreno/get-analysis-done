"""CMS Combine datacard exporter and sensitivity optimization helper.

Exports pyhf workspace specifications to CMS HiggsAnalysis-CombinedLimit
compatible text datacards and ROOT shape files. Also provides sensitivity
comparison across alternative fit configurations.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import uproot

from gad.statistical.fitter import Fitter


class DatacardExporter:
    """Export pyhf workspace to CMS Combine datacard format.

    Produces a text datacard (datacard.txt) and ROOT shape file (shapes.root)
    compatible with the CMS HiggsAnalysis-CombinedLimit tool.
    """

    def export(self, workspace_spec, output_dir):
        """Export workspace to CMS Combine format.

        Parameters
        ----------
        workspace_spec : dict
            Valid pyhf workspace JSON specification.
        output_dir : str
            Directory for output files.

        Returns
        -------
        dict
            Keys: datacard_path, shapes_path, n_channels, n_processes, n_systematics.
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        channels = workspace_spec["channels"]
        observations = {o["name"]: o["data"] for o in workspace_spec["observations"]}
        measurement = workspace_spec["measurements"][0]
        poi_name = measurement["config"]["poi"]

        # Identify signal and background processes
        # Signal: has normfactor modifier with POI name
        signal_names = set()
        all_process_names = []
        process_per_channel = {}

        for ch in channels:
            ch_name = ch["name"]
            process_per_channel[ch_name] = []
            for sample in ch["samples"]:
                if sample["name"] not in all_process_names:
                    all_process_names.append(sample["name"])
                process_per_channel[ch_name].append(sample["name"])
                for mod in sample["modifiers"]:
                    if mod["type"] == "normfactor" and mod["name"] == poi_name:
                        signal_names.add(sample["name"])

        # Order: signals first (index 0, -1, ...), then backgrounds (1, 2, ...)
        signals = [p for p in all_process_names if p in signal_names]
        backgrounds = [p for p in all_process_names if p not in signal_names]
        ordered_processes = signals + backgrounds

        # Assign process indices: signal gets 0 (and negative for additional signals),
        # backgrounds get 1, 2, 3, ...
        process_indices = {}
        for i, name in enumerate(signals):
            process_indices[name] = -i  # 0, -1, -2, ...
        for i, name in enumerate(backgrounds):
            process_indices[name] = i + 1

        # Collect systematics
        systematics = {}  # name -> {type, affects: {(ch, proc): data}}
        has_staterror = False

        for ch in channels:
            ch_name = ch["name"]
            for sample in ch["samples"]:
                proc_name = sample["name"]
                for mod in sample["modifiers"]:
                    mod_type = mod["type"]
                    mod_name = mod["name"]

                    if mod_type == "normfactor":
                        continue  # POI, not a systematic
                    if mod_type == "staterror":
                        has_staterror = True
                        continue  # Handled via autoMCStats

                    if mod_name not in systematics:
                        systematics[mod_name] = {
                            "type": mod_type,
                            "affects": {},
                        }
                    systematics[mod_name]["affects"][(ch_name, proc_name)] = mod["data"]

        n_channels = len(channels)
        n_backgrounds = len(backgrounds)
        n_systematics = len(systematics)

        # -- Write shapes.root ---------------------------------------------------
        shapes_path = output_dir / "shapes.root"
        self._write_shapes_root(
            shapes_path, channels, observations, systematics, ordered_processes,
        )

        # -- Write datacard.txt --------------------------------------------------
        datacard_path = output_dir / "datacard.txt"
        self._write_datacard_txt(
            datacard_path, channels, observations, ordered_processes,
            process_indices, signals, backgrounds, systematics, has_staterror,
        )

        return {
            "datacard_path": str(datacard_path),
            "shapes_path": str(shapes_path),
            "n_channels": n_channels,
            "n_processes": len(ordered_processes),
            "n_systematics": n_systematics,
        }

    def _write_shapes_root(self, path, channels, observations, systematics, ordered_processes):
        """Write ROOT shape file with TH1-compatible histograms.

        Parameters
        ----------
        path : Path
            Output ROOT file path.
        channels : list of dict
            Channel definitions from workspace spec.
        observations : dict
            Channel name -> observed data.
        systematics : dict
            Systematic name -> {type, affects}.
        ordered_processes : list of str
            Ordered process names.
        """
        with uproot.recreate(str(path)) as f:
            for ch in channels:
                ch_name = ch["name"]
                sample_map = {s["name"]: s for s in ch["samples"]}

                for proc_name in ordered_processes:
                    if proc_name not in sample_map:
                        continue
                    sample = sample_map[proc_name]
                    data = np.array(sample["data"], dtype=np.float64)
                    n_bins = len(data)
                    # Uniform binning from 0 to n_bins
                    edges = np.arange(n_bins + 1, dtype=np.float64)

                    # Write nominal histogram
                    hist_name = f"{ch_name}/{proc_name}"
                    f[hist_name] = (data, edges)

                    # Write shifted histograms for shape systematics
                    for syst_name, syst_info in systematics.items():
                        key = (ch_name, proc_name)
                        if key not in syst_info["affects"]:
                            continue
                        if syst_info["type"] == "histosys":
                            syst_data = syst_info["affects"][key]
                            hi_data = np.array(syst_data["hi_data"], dtype=np.float64)
                            lo_data = np.array(syst_data["lo_data"], dtype=np.float64)
                            f[f"{ch_name}/{proc_name}_{syst_name}Up"] = (hi_data, edges)
                            f[f"{ch_name}/{proc_name}_{syst_name}Down"] = (lo_data, edges)

                # Write observed data histogram
                obs_data = np.array(observations[ch_name], dtype=np.float64)
                obs_edges = np.arange(len(obs_data) + 1, dtype=np.float64)
                f[f"{ch_name}/data_obs"] = (obs_data, obs_edges)

    def _write_datacard_txt(self, path, channels, observations, ordered_processes,
                            process_indices, signals, backgrounds, systematics,
                            has_staterror):
        """Write CMS Combine text datacard.

        Parameters
        ----------
        path : Path
            Output datacard file path.
        channels : list of dict
            Channel definitions.
        observations : dict
            Channel name -> observed data.
        ordered_processes : list of str
            Ordered process names (signals first).
        process_indices : dict
            Process name -> CMS Combine index.
        signals : list of str
            Signal process names.
        backgrounds : list of str
            Background process names.
        systematics : dict
            Systematic definitions.
        has_staterror : bool
            Whether staterror modifiers are present.
        """
        ch_names = [ch["name"] for ch in channels]
        sample_map = {}
        for ch in channels:
            sample_map[ch["name"]] = {s["name"]: s for s in ch["samples"]}

        lines = []

        # Header
        lines.append(f"imax {len(ch_names)}")
        lines.append(f"jmax {len(backgrounds)}")
        lines.append(f"kmax {len(systematics)}")
        lines.append("-" * 60)

        # Shapes line
        lines.append("shapes * * shapes.root $CHANNEL/$PROCESS $CHANNEL/$PROCESS_$SYSTEMATIC")
        lines.append("-" * 60)

        # Observation line
        obs_parts = ["observation"]
        for ch_name in ch_names:
            obs_data = observations[ch_name]
            obs_parts.append(f"{sum(obs_data):.1f}")
        lines.append("bin         " + "  ".join(ch_names))
        lines.append("  ".join(obs_parts))
        lines.append("-" * 60)

        # Rate table: bin / process name / process index / rate
        bin_row = ["bin"]
        proc_name_row = ["process"]
        proc_idx_row = ["process"]
        rate_row = ["rate"]

        for ch_name in ch_names:
            for proc_name in ordered_processes:
                if proc_name not in sample_map[ch_name]:
                    continue
                sample = sample_map[ch_name][proc_name]
                bin_row.append(ch_name)
                proc_name_row.append(proc_name)
                proc_idx_row.append(str(process_indices[proc_name]))
                rate_row.append(f"{sum(sample['data']):.4f}")

        lines.append("  ".join(bin_row))
        lines.append("  ".join(proc_name_row))
        lines.append("  ".join(proc_idx_row))
        lines.append("  ".join(rate_row))
        lines.append("-" * 60)

        # Systematic lines
        for syst_name, syst_info in sorted(systematics.items()):
            syst_type = syst_info["type"]

            if syst_type == "normsys":
                combine_type = "lnN"
            elif syst_type == "histosys":
                combine_type = "shape"
            else:
                combine_type = "lnN"  # fallback

            parts = [syst_name, combine_type]
            for ch_name in ch_names:
                for proc_name in ordered_processes:
                    if proc_name not in sample_map[ch_name]:
                        continue
                    key = (ch_name, proc_name)
                    if key in syst_info["affects"]:
                        data = syst_info["affects"][key]
                        if syst_type == "normsys":
                            parts.append(f"{data['hi']:.4f}/{data['lo']:.4f}")
                        elif syst_type == "histosys":
                            parts.append("1.0")
                        else:
                            parts.append("1.0")
                    else:
                        parts.append("-")
            lines.append("  ".join(parts))

        # autoMCStats line (always include for MC statistical uncertainties)
        lines.append("* autoMCStats 0")

        with open(str(path), "w") as f:
            f.write("\n".join(lines) + "\n")


class SensitivityOptimizer:
    """Compare expected limits across alternative workspace configurations.

    Supports SYST-08: lead analyst reviews expected limits under alternative
    configurations (baseline, coarser binning, aggressive pruning).
    """

    def compare_configurations(self, configs):
        """Compare expected limits for multiple workspace configurations.

        Parameters
        ----------
        configs : dict
            Mapping of config_name -> workspace_spec.

        Returns
        -------
        pandas.DataFrame
            Columns: config, expected_limit, band_m2, band_m1, band_p1,
            band_p2, best (bool).
        """
        rows = []
        for name, spec in configs.items():
            fitter = Fitter(spec)
            limit_result = fitter.expected_limit()
            rows.append({
                "config": name,
                "expected_limit": limit_result["expected_limit"],
                "band_m2": limit_result["bands"]["-2"],
                "band_m1": limit_result["bands"]["-1"],
                "band_p1": limit_result["bands"]["+1"],
                "band_p2": limit_result["bands"]["+2"],
            })

        df = pd.DataFrame(rows)

        # Mark the best configuration (lowest expected limit = most sensitive)
        if len(df) > 0:
            best_idx = df["expected_limit"].idxmin()
            df["best"] = False
            df.loc[best_idx, "best"] = True

        return df
