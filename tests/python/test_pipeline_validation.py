"""Pipeline component validation tests.

Verify that all pipeline pieces (manifests, gates, agents, templates, modules)
are correctly wired together. These tests check structural correctness of the
project -- they do NOT run the actual analysis pipeline.
"""

import importlib
from pathlib import Path

import pytest
import yaml

# Project root: get-analysis-done/
ROOT = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# Wave manifest validation
# ---------------------------------------------------------------------------

WAVE_IDS = list(range(8))


@pytest.mark.parametrize("wave_id", WAVE_IDS)
def test_wave_manifest_valid(wave_id: int) -> None:
    """Each wave manifest (0-7) parses as valid YAML with required fields."""
    manifest_path = ROOT / "wave-manifests" / f"wave-{wave_id}.yaml"
    assert manifest_path.exists(), f"wave-{wave_id}.yaml not found"

    with open(manifest_path) as f:
        data = yaml.safe_load(f)

    assert isinstance(data, dict), f"wave-{wave_id}.yaml did not parse as dict"
    assert "wave" in data, f"wave-{wave_id}.yaml missing 'wave' key"
    assert "load_artifacts" in data, f"wave-{wave_id}.yaml missing 'load_artifacts' key"
    assert "agents" in data, f"wave-{wave_id}.yaml missing 'agents' key"
    assert data["wave"] == wave_id, f"wave-{wave_id}.yaml 'wave' field is {data['wave']}, expected {wave_id}"


def test_all_wave_manifests_valid() -> None:
    """All 8 wave manifests (0-7) parse as valid YAML with required fields."""
    manifests_dir = ROOT / "wave-manifests"
    assert manifests_dir.is_dir(), "wave-manifests/ directory not found"

    for wave_id in WAVE_IDS:
        path = manifests_dir / f"wave-{wave_id}.yaml"
        assert path.exists(), f"wave-{wave_id}.yaml missing"
        with open(path) as f:
            data = yaml.safe_load(f)
        for key in ("wave", "load_artifacts", "agents"):
            assert key in data, f"wave-{wave_id}.yaml missing '{key}'"


# ---------------------------------------------------------------------------
# Gate template validation
# ---------------------------------------------------------------------------

GATE_PAIRS = [(i, i + 1) for i in range(7)]


@pytest.mark.parametrize("src,dst", GATE_PAIRS)
def test_gate_template_valid(src: int, dst: int) -> None:
    """Each gate template parses as valid YAML with required fields."""
    gate_path = ROOT / "gate-templates" / f"gate-{src}-to-{dst}.yaml"
    assert gate_path.exists(), f"gate-{src}-to-{dst}.yaml not found"

    with open(gate_path) as f:
        data = yaml.safe_load(f)

    assert isinstance(data, dict), f"gate-{src}-to-{dst}.yaml did not parse as dict"
    assert "gate" in data, f"gate-{src}-to-{dst}.yaml missing 'gate' key"
    assert "criteria" in data, f"gate-{src}-to-{dst}.yaml missing 'criteria' key"
    assert "on_failure" in data, f"gate-{src}-to-{dst}.yaml missing 'on_failure' key"


def test_all_gate_templates_valid() -> None:
    """All 7 gate templates parse as valid YAML with required fields."""
    gates_dir = ROOT / "gate-templates"
    assert gates_dir.is_dir(), "gate-templates/ directory not found"

    for src, dst in GATE_PAIRS:
        path = gates_dir / f"gate-{src}-to-{dst}.yaml"
        assert path.exists(), f"gate-{src}-to-{dst}.yaml missing"
        with open(path) as f:
            data = yaml.safe_load(f)
        for key in ("gate", "criteria", "on_failure"):
            assert key in data, f"gate-{src}-to-{dst}.yaml missing '{key}'"


# ---------------------------------------------------------------------------
# Agent definitions
# ---------------------------------------------------------------------------

AGENT_NAMES = [
    "gad-background-estimator",
    "gad-cross-checker",
    "gad-data-explorer",
    "gad-detector-specialist",
    "gad-lead-analyst",
    "gad-ml-specialist",
    "gad-note-writer",
    "gad-signal-lead",
    "gad-systematics-fitter",
    "gad-systematic-source-evaluator",
    "gad-theory-scout",
]


def test_all_agent_definitions_exist() -> None:
    """All 11 agent .md files exist in agents/ and contain a role section."""
    agents_dir = ROOT / "agents"
    assert agents_dir.is_dir(), "agents/ directory not found"

    for name in AGENT_NAMES:
        path = agents_dir / f"{name}.md"
        assert path.exists(), f"{name}.md not found in agents/"
        content = path.read_text()
        assert "role" in content.lower() or "<role>" in content, (
            f"{name}.md does not contain a 'role' or '<role>' section"
        )


# ---------------------------------------------------------------------------
# Note section templates
# ---------------------------------------------------------------------------

NOTE_SECTIONS = [
    "section_01_introduction.tex",
    "section_02_data_mc.tex",
    "section_03_objects.tex",
    "section_04_selection.tex",
    "section_05_background.tex",
    "section_06_systematics.tex",
    "section_07_statistical.tex",
    "section_08_expected.tex",
    "section_09_observed.tex",
    "appendix_a_blinding.tex",
]

MIN_SECTION_BYTES = 100


def test_all_note_section_templates_exist() -> None:
    """All 9 sections + appendix exist in templates/ANALYSIS_NOTE_SECTIONS/ with non-trivial content."""
    sections_dir = ROOT / "templates" / "ANALYSIS_NOTE_SECTIONS"
    assert sections_dir.is_dir(), "templates/ANALYSIS_NOTE_SECTIONS/ not found"

    for filename in NOTE_SECTIONS:
        path = sections_dir / filename
        assert path.exists(), f"{filename} not found"
        size = path.stat().st_size
        assert size > MIN_SECTION_BYTES, (
            f"{filename} is only {size} bytes (minimum {MIN_SECTION_BYTES})"
        )


# ---------------------------------------------------------------------------
# Wave 7 specific checks
# ---------------------------------------------------------------------------

def test_wave7_manifest_references_valid_artifacts() -> None:
    """All load_artifacts paths in wave-7.yaml are plausible artifact paths."""
    wave7_path = ROOT / "wave-manifests" / "wave-7.yaml"
    with open(wave7_path) as f:
        data = yaml.safe_load(f)

    artifacts = data.get("load_artifacts", [])
    assert len(artifacts) > 0, "wave-7.yaml has no load_artifacts"

    for entry in artifacts:
        assert "path" in entry, f"Artifact entry missing 'path': {entry}"
        assert "reason" in entry, f"Artifact entry missing 'reason': {entry}"
        # Path should be a relative string with a meaningful name
        p = entry["path"]
        assert isinstance(p, str) and len(p) > 3, f"Artifact path too short: {p}"


def test_note_writer_has_wave7_instructions() -> None:
    """gad-note-writer.md contains a 'Wave 7' section."""
    nw_path = ROOT / "agents" / "gad-note-writer.md"
    content = nw_path.read_text()
    assert "Wave 7" in content, "gad-note-writer.md missing 'Wave 7' section"


def test_cross_checker_has_citation_verification() -> None:
    """gad-cross-checker.md contains 'INSPIRE' and 'citation'."""
    cc_path = ROOT / "agents" / "gad-cross-checker.md"
    content = cc_path.read_text()
    assert "INSPIRE" in content, "gad-cross-checker.md missing 'INSPIRE'"
    assert "citation" in content.lower(), "gad-cross-checker.md missing 'citation'"


def test_main_tex_has_bibliography() -> None:
    """main.tex has uncommented bibliographystyle and bibliography lines."""
    main_path = ROOT / "templates" / "ANALYSIS_NOTE_SECTIONS" / "main.tex"
    content = main_path.read_text()
    lines = content.splitlines()

    found_style = False
    found_bib = False
    for line in lines:
        stripped = line.strip()
        # Must be uncommented (not starting with %)
        if stripped.startswith("\\bibliographystyle") and not stripped.startswith("%"):
            found_style = True
        if stripped.startswith("\\bibliography") and not stripped.startswith("%") and "style" not in stripped:
            found_bib = True

    assert found_style, "main.tex missing uncommented \\bibliographystyle"
    assert found_bib, "main.tex missing uncommented \\bibliography"


# ---------------------------------------------------------------------------
# Documentation module importability
# ---------------------------------------------------------------------------

def test_documentation_module_importable() -> None:
    """gad.documentation module and all submodules import without error."""
    mod = importlib.import_module("gad.documentation")
    assert mod is not None

    for submod_name in ("citations", "plots", "compiler", "verification"):
        submod = importlib.import_module(f"gad.documentation.{submod_name}")
        assert submod is not None


# ---------------------------------------------------------------------------
# ALEPH experiment context
# ---------------------------------------------------------------------------

ALEPH_REQUIRED_FILES = [
    "detector.yaml",
    "objects.yaml",
    "mc_generators.yaml",
    "performance.yaml",
    "references.yaml",
]


def test_aleph_experiment_context_complete() -> None:
    """experiments/aleph/ has all 5 required YAML files."""
    aleph_dir = ROOT / "experiments" / "aleph"
    assert aleph_dir.is_dir(), "experiments/aleph/ directory not found"

    for filename in ALEPH_REQUIRED_FILES:
        path = aleph_dir / filename
        assert path.exists(), f"experiments/aleph/{filename} not found"
        with open(path) as f:
            data = yaml.safe_load(f)
        assert isinstance(data, dict), f"{filename} did not parse as valid YAML dict"
