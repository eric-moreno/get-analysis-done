"""Blinding integrity checks for pre-unblinding validation.

Verifies that no signal region data has leaked into plots, wave outputs,
or git history before the analysis is unblinded.
"""

import os
import re
import subprocess
from pathlib import Path


class BlindingIntegrityChecker:
    """Check blinding integrity across file system and git history.

    Parameters
    ----------
    analysis_dir : str or Path
        Root directory of the analysis.
    sr_plots_dir : str or Path, optional
        Directory where signal region plots would be stored.
        Default: "plots/signal_region" relative to analysis_dir.
    """

    def __init__(self, analysis_dir, sr_plots_dir=None):
        self._analysis_dir = Path(analysis_dir)
        if sr_plots_dir is not None:
            self._sr_plots_dir = Path(sr_plots_dir)
        else:
            self._sr_plots_dir = self._analysis_dir / "plots" / "signal_region"

    def check_sr_plots_empty(self):
        """Check that the signal region plots directory is empty or missing.

        Returns
        -------
        dict
            Keys: check, passes, detail.
        """
        if not self._sr_plots_dir.exists():
            return {
                "check": "sr_plots_empty",
                "passes": True,
                "detail": "SR plots directory does not exist",
            }

        files = list(self._sr_plots_dir.iterdir())
        passes = len(files) == 0

        return {
            "check": "sr_plots_empty",
            "passes": passes,
            "detail": (
                "SR plots directory is empty"
                if passes
                else f"SR plots directory contains {len(files)} file(s): "
                + ", ".join(f.name for f in files[:5])
            ),
        }

    def check_no_sr_yields_in_outputs(self, wave_dirs=None):
        """Scan wave output files for signal region yield values.

        Parameters
        ----------
        wave_dirs : list of str, optional
            Directories to scan. If None, returns pass (nothing to scan).

        Returns
        -------
        dict
            Keys: check, passes, violations.
        """
        if wave_dirs is None:
            return {
                "check": "no_sr_yields_in_outputs",
                "passes": True,
                "violations": [],
            }

        pattern = re.compile(
            r"observed.*signal.region.*\d+\.\d+", re.IGNORECASE
        )
        extensions = {".md", ".json", ".yaml", ".yml", ".txt"}
        violations = []

        for wave_dir in wave_dirs:
            for root, _dirs, filenames in os.walk(wave_dir):
                for fname in filenames:
                    fpath = Path(root) / fname
                    if fpath.suffix.lower() not in extensions:
                        continue
                    try:
                        content = fpath.read_text(errors="ignore")
                        if pattern.search(content):
                            violations.append(str(fpath))
                    except OSError:
                        continue

        return {
            "check": "no_sr_yields_in_outputs",
            "passes": len(violations) == 0,
            "violations": violations,
        }

    def check_git_history(self):
        """Check git history for commits containing signal region observed data.

        Returns
        -------
        dict
            Keys: check, passes, commits.
        """
        try:
            result = subprocess.run(
                [
                    "git", "log", "--all", "--diff-filter=A",
                    "-S", "signal_region_observed",
                    "--format=%H %s",
                ],
                cwd=str(self._analysis_dir),
                capture_output=True,
                text=True,
                timeout=30,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return {
                "check": "git_no_sr_data",
                "passes": False,
                "commits": [],
                "detail": "Failed to run git log",
            }

        commits = [
            line.strip()
            for line in result.stdout.strip().split("\n")
            if line.strip()
        ]

        return {
            "check": "git_no_sr_data",
            "passes": len(commits) == 0,
            "commits": commits,
        }

    def run_all(self, wave_dirs=None):
        """Run all integrity checks.

        Parameters
        ----------
        wave_dirs : list of str, optional
            Directories to scan for SR yield leaks.

        Returns
        -------
        dict
            Keys: checks (list), all_pass (bool).
        """
        checks = [
            self.check_sr_plots_empty(),
            self.check_no_sr_yields_in_outputs(wave_dirs=wave_dirs),
            self.check_git_history(),
        ]
        return {
            "checks": checks,
            "all_pass": all(c["passes"] for c in checks),
        }
