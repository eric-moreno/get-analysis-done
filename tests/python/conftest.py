"""Shared fixtures for blinding and data module tests."""

import os
import tempfile

import numpy as np
import uproot
import pytest


@pytest.fixture
def mock_state_md(tmp_path):
    """Create a temporary STATE.md with YAML frontmatter containing blinding_status.

    Parameters
    ----------
    blinding_status : str
        Current blinding state value.
    reblind_count : int
        Number of re-blindings performed.
    checklist_complete : bool
        If True, include a fully-complete unblinding checklist in frontmatter.
        Default False (no checklist written).
    """
    def _create(blinding_status="blinded", reblind_count=0, checklist_complete=False):
        state_file = tmp_path / "STATE.md"
        checklist_block = ""
        if checklist_complete:
            checklist_block = (
                "unblinding_checklist:\n"
                "  background_validated: true\n"
                "  systematics_complete: true\n"
                "  stat_model_built: true\n"
                "  cross_checks_pass: true\n"
                "  note_drafted: true\n"
                "  sensitivity_understood: true\n"
                "  blinding_integrity_verified: true\n"
            )
        content = f"""---
gsd_state_version: 1.0
blinding_status: {blinding_status}
reblind_count: {reblind_count}
{checklist_block}---

# Project State

Blinding Status: {blinding_status}
"""
        state_file.write_text(content)
        return str(state_file)
    return _create


@pytest.fixture
def mock_config_yaml(tmp_path):
    """Create a temporary analysis config YAML with signal_region and unblinding settings."""
    def _create(partial_seed=42, allowed_reblind_count=1):
        config_file = tmp_path / "analysis_config.yaml"
        content = f"""signal_region:
  name: SR
  cuts:
    - variable: mll
      operator: ">"
      threshold: 120.0
    - variable: met
      operator: ">"
      threshold: 50.0

control_regions:
  - name: CR_top
    cuts:
      - variable: n_bjets
        operator: ">="
        threshold: 2

unblinding:
  partial_seed: {partial_seed}
  allowed_reblind_count: {allowed_reblind_count}
"""
        config_file.write_text(content)
        return str(config_file)
    return _create


@pytest.fixture
def mock_events():
    """Create a numpy array of 100 mock events."""
    rng = np.random.RandomState(123)
    return rng.random(100)


@pytest.fixture
def mock_sr_plots_dir(tmp_path):
    """Create a temporary plots/signal_region/ directory."""
    sr_dir = tmp_path / "plots" / "signal_region"
    sr_dir.mkdir(parents=True)
    return str(sr_dir)


@pytest.fixture
def mock_root_file(tmp_path):
    """Create a minimal ROOT file with a TTree for testing.

    The tree 't' contains 50 events with branches:
      - x: float64 (event-level)
      - y: float64 (event-level)
      - n: int32 (event-level, acts as event ID)
    """
    path = str(tmp_path / "test_data.root")
    rng = np.random.RandomState(999)
    n_events = 50
    with uproot.recreate(path) as f:
        f["t"] = {
            "x": rng.normal(0, 1, n_events).astype(np.float64),
            "y": rng.exponential(2.0, n_events).astype(np.float64),
            "n": np.arange(n_events, dtype=np.int32),
        }
    return path


@pytest.fixture
def mock_samples_yaml(tmp_path, mock_root_file):
    """Create a samples.yaml config pointing at the mock ROOT file.

    Returns the path to the samples YAML and the analysis config YAML.
    """
    samples_file = tmp_path / "samples.yaml"
    samples_content = f"""samples:
  qqbar:
    paths:
      - {mock_root_file}
    tree_name: t
    cross_section: 1.0
    luminosity: 139.0
    region: control_region
  signal:
    paths:
      - {mock_root_file}
    tree_name: t
    cross_section: 0.5
    luminosity: 139.0
    region: signal_region
"""
    samples_file.write_text(samples_content)

    # Also create an analysis config that references this samples file
    config_file = tmp_path / "analysis_config.yaml"
    config_content = f"""signal_region:
  name: SR
  cuts:
    - variable: mll
      operator: ">"
      threshold: 120.0

control_regions:
  - name: CR_top
    cuts:
      - variable: n_bjets
        operator: ">="
        threshold: 2

unblinding:
  partial_seed: 42
  allowed_reblind_count: 1

samples_config: {str(samples_file)}
"""
    config_file.write_text(config_content)
    return str(samples_file), str(config_file)


@pytest.fixture
def mock_experiment_dir(tmp_path):
    """Create a temporary experiments/{name}/ directory with YAML files.

    Returns a factory function that accepts experiment name and optional
    file contents to override defaults.
    """
    import yaml

    default_detector = {
        "experiment": "test_exp",
        "collider": "TestCollider",
        "full_name": "Test Experiment",
        "sqrt_s_range": [10.0, 200.0],
        "subsystems": {
            "tracker": {"name": "TRK", "type": "silicon"},
        },
    }

    default_objects = {
        "good_track": {
            "description": "Test good track",
            "cuts": [
                {"variable": "pt", "operator": ">", "threshold": 0.5, "unit": "GeV"},
                {"variable": "eta", "operator": "<", "threshold": 2.5, "absolute": True},
            ],
            "metadata": {"expected_efficiency": 0.95},
        },
        "good_jet": {
            "description": "Test good jet",
            "cuts": [
                {"variable": "pt", "operator": ">", "threshold": 20.0, "unit": "GeV"},
            ],
            "metadata": {"expected_efficiency": 0.90},
        },
    }

    default_mc_generators = {
        "generators": {
            "pythia": {"name": "PYTHIA", "version": "8.3", "use": "signal and background"},
        },
    }

    default_performance = {
        "tracking": {
            "momentum_resolution": "sigma(1/pt) = 1e-3 (GeV/c)^-1",
            "reference": "Test NIM paper",
        },
    }

    default_references = {
        "key_papers": {
            "detector_paper": {
                "title": "Test detector paper",
                "journal": "Test Journal 1 (2020)",
            },
        },
    }

    def _create(name="test_exp", *, files=None, skip_files=None):
        """Create experiment directory.

        Parameters
        ----------
        name : str
            Experiment name (subdirectory name).
        files : dict, optional
            Mapping of filename -> content dict to override defaults.
        skip_files : list, optional
            List of filenames to omit from the directory.
        """
        exp_dir = tmp_path / "experiments" / name
        exp_dir.mkdir(parents=True, exist_ok=True)

        all_files = {
            "detector.yaml": default_detector,
            "objects.yaml": default_objects,
            "mc_generators.yaml": default_mc_generators,
            "performance.yaml": default_performance,
            "references.yaml": default_references,
        }

        if files:
            all_files.update(files)

        skip = set(skip_files or [])
        for fname, content in all_files.items():
            if fname not in skip:
                (exp_dir / fname).write_text(yaml.dump(content, default_flow_style=False))

        return str(tmp_path / "experiments")

    return _create


@pytest.fixture
def mock_aleph_experiment(tmp_path):
    """Create a realistic ALEPH-like experiment directory."""
    import yaml

    exp_dir = tmp_path / "experiments" / "aleph"
    exp_dir.mkdir(parents=True)

    detector = {
        "experiment": "aleph",
        "collider": "LEP",
        "full_name": "Apparatus for LEP Physics",
        "sqrt_s_range": [88.0, 209.0],
        "run_periods": [
            {"name": "LEP1", "years": [1989, 1995], "sqrt_s": [88.0, 95.0]},
            {"name": "LEP2", "years": [1995, 2000], "sqrt_s": [130.0, 209.0]},
        ],
        "subsystems": {
            "vertex_detector": {"name": "VDET", "type": "silicon_microstrip", "layers": 2},
            "tracking_chamber": {"name": "TPC", "type": "time_projection_chamber"},
            "ecal": {"name": "ECAL", "type": "lead_proportional_wire_chamber"},
            "hcal": {"name": "HCAL", "type": "iron_streamer_tube"},
            "magnet": {"type": "superconducting_solenoid", "field_tesla": 1.5},
        },
    }

    objects = {
        "good_track": {
            "description": "ALEPH good charged track",
            "reference": "ALEPH EPJC 14 (2000), Section 3.1",
            "cuts": [
                {"variable": "charge", "operator": "!=", "threshold": 0},
                {"variable": "ntpc", "operator": ">=", "threshold": 4},
                {"variable": "cos_theta", "operator": "<", "threshold": 0.94, "absolute": True},
                {"variable": "pt", "operator": ">", "threshold": 0.2, "unit": "GeV"},
                {"variable": "d0", "operator": "<", "threshold": 2.0, "absolute": True, "unit": "cm"},
                {"variable": "z0", "operator": "<", "threshold": 20.0, "absolute": True, "unit": "cm"},
            ],
            "metadata": {"expected_efficiency": 0.99, "note": "Applied per-particle before counting N_ch"},
        },
        "good_neutral": {
            "description": "ALEPH good neutral particle",
            "reference": "ALEPH EPJC 14 (2000), Section 3.1",
            "cuts": [
                {"variable": "charge", "operator": "==", "threshold": 0},
                {"variable": "cos_theta", "operator": "<", "threshold": 0.98, "absolute": True},
                {"variable": "pmag", "operator": ">", "threshold": 0.4, "unit": "GeV"},
            ],
        },
    }

    mc_generators = {
        "generators": {
            "pythia": {"name": "PYTHIA", "version": "6.1", "use": "qq and 4-fermion backgrounds"},
            "herwig": {"name": "HERWIG", "version": "6.2", "use": "Fragmentation systematic"},
            "kk2f": {"name": "KK2f", "version": "4.19", "use": "Z/gamma* production"},
        },
    }

    performance = {
        "tracking": {
            "momentum_resolution": "sigma(1/pt) = 6e-4 (GeV/c)^-1",
            "reference": "ALEPH NIM A360 (1995) 481-506",
        },
        "b_tagging": {
            "method": "lifetime-based impact parameter",
            "working_points": {
                "loose": {"efficiency": 0.80, "mistag_rate": 0.10},
                "medium": {"efficiency": 0.65, "mistag_rate": 0.02},
                "tight": {"efficiency": 0.50, "mistag_rate": 0.005},
            },
        },
    }

    references = {
        "key_papers": {
            "detector_nim": {
                "title": "ALEPH: A detector for electron-positron annihilations at LEP",
                "journal": "Nucl. Instrum. Meth. A294 (1990) 121-178",
            },
            "performance_nim": {
                "title": "Performance of the ALEPH detector at LEP",
                "journal": "Nucl. Instrum. Meth. A360 (1995) 481-506",
            },
        },
    }

    for fname, content in [
        ("detector.yaml", detector),
        ("objects.yaml", objects),
        ("mc_generators.yaml", mc_generators),
        ("performance.yaml", performance),
        ("references.yaml", references),
    ]:
        (exp_dir / fname).write_text(yaml.dump(content, default_flow_style=False))

    return str(tmp_path / "experiments")
