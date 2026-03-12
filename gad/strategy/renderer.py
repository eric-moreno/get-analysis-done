"""Strategy document renderer.

Fills the ANALYSIS_STRATEGY_TEMPLATE.md with experiment context data and
physics prompt content to produce a complete analysis strategy document.
"""

import re
from datetime import date
from pathlib import Path


class StrategyRenderer:
    """Renders analysis strategy documents from template + experiment context.

    Parameters
    ----------
    template_path : str
        Path to the ANALYSIS_STRATEGY_TEMPLATE.md file.

    Attributes
    ----------
    REQUIRED_SECTIONS : list[str]
        The 13 required section headers for a complete strategy document.
    """

    REQUIRED_SECTIONS = [
        "Executive Summary",
        "Signal Process",
        "Backgrounds",
        "Dataset and Luminosity",
        "Object Definitions",
        "Blinding Protocol",
        "Event Selection Strategy",
        "Categorization Plan",
        "Background Estimation",
        "Systematic Uncertainties",
        "Statistical Approach",
        "Target Sensitivity",
        "Quality Gate Criteria",
    ]

    def __init__(self, template_path: str = "templates/ANALYSIS_STRATEGY_TEMPLATE.md"):
        self._template_path = Path(template_path)

    def render(
        self,
        physics_prompt: str,
        experiment_context=None,
        config=None,
    ) -> str:
        """Render the strategy template with context data.

        Parameters
        ----------
        physics_prompt : str
            Description of the physics analysis (signal process, goals).
        experiment_context : ExperimentContext, optional
            Experiment context providing detector, objects, MC info.
        config : AnalysisConfig, optional
            Analysis configuration with signal region, samples, etc.

        Returns
        -------
        str
            Rendered markdown strategy document.

        Raises
        ------
        ValueError
            If physics_prompt is empty or None.
        FileNotFoundError
            If the template file does not exist.
        """
        if not physics_prompt:
            raise ValueError(
                "physics_prompt must be a non-empty string describing "
                "the analysis"
            )

        template = self._template_path.read_text()

        # Build substitution map
        subs = {
            "signal_process": physics_prompt,
            "date": date.today().isoformat(),
        }

        if experiment_context is not None:
            subs.update(self._extract_experiment_fields(experiment_context))

        if config is not None:
            subs.update(self._extract_config_fields(config))

        # Apply substitutions -- replace {{key}} with value
        rendered = template
        for key, value in subs.items():
            rendered = rendered.replace("{{" + key + "}}", str(value))

        return rendered

    def validate_rendered(self, rendered: str) -> list:
        """Check that all 13 required sections are present.

        Parameters
        ----------
        rendered : str
            The rendered strategy document content.

        Returns
        -------
        list[str]
            List of missing section names. Empty if all present.
        """
        missing = []
        for section in self.REQUIRED_SECTIONS:
            # Check for ## or # header with section name
            pattern = r"^#{1,2}\s+" + re.escape(section)
            if not re.search(pattern, rendered, re.MULTILINE):
                missing.append(section)
        return missing

    def _extract_experiment_fields(self, ctx) -> dict:
        """Extract template fields from an ExperimentContext.

        Parameters
        ----------
        ctx : ExperimentContext
            The experiment context object.

        Returns
        -------
        dict
            Mapping of template placeholder names to values.
        """
        fields = {}

        # Detector-level fields
        detector = ctx.detector or {}
        fields["experiment_name"] = detector.get("experiment", "Unknown")
        fields["collider"] = detector.get("collider", "Unknown")

        sqrt_s_range = detector.get("sqrt_s_range", [])
        if sqrt_s_range:
            fields["sqrt_s"] = f"{sqrt_s_range[0]}-{sqrt_s_range[-1]}"
        else:
            fields["sqrt_s"] = "TBD"

        # Object definitions formatted as markdown
        objects = ctx.objects or {}
        if objects:
            lines = []
            for obj_name, obj_def in objects.items():
                desc = obj_def.get("description", "")
                cuts = obj_def.get("cuts", [])
                lines.append(f"### {obj_name}")
                lines.append(f"*{desc}*\n")
                if cuts:
                    lines.append("| Variable | Operator | Threshold | Unit |")
                    lines.append("|----------|----------|-----------|------|")
                    for cut in cuts:
                        var = cut.get("variable", "")
                        op = cut.get("operator", "")
                        thr = cut.get("threshold", "")
                        unit = cut.get("unit", "")
                        abs_note = " (absolute)" if cut.get("absolute") else ""
                        lines.append(f"| {var} | {op} | {thr}{abs_note} | {unit} |")
                lines.append("")
            fields["object_definitions"] = "\n".join(lines)
        else:
            fields["object_definitions"] = "*No object definitions available.*"

        # MC generators
        mc = ctx.mc_generators or {}
        generators = mc.get("generators", {})
        if generators:
            gen_lines = []
            for gen_key, gen_info in generators.items():
                name = gen_info.get("name", gen_key)
                version = gen_info.get("version", "")
                use = gen_info.get("use", "")
                gen_lines.append(f"- **{name}** v{version}: {use}")
            fields["mc_generators"] = "\n".join(gen_lines)
        else:
            fields["mc_generators"] = "*No MC generator information available.*"

        # References
        refs = ctx.references or {}
        key_papers = refs.get("key_papers", {})
        if key_papers:
            ref_lines = []
            for ref_key, ref_info in key_papers.items():
                title = ref_info.get("title", ref_key)
                journal = ref_info.get("journal", "")
                ref_lines.append(f"- {title}, {journal}")
            fields["key_references"] = "\n".join(ref_lines)
        else:
            fields["key_references"] = "*No references available.*"

        # Available objects list (for detector subsystems)
        subsystems = detector.get("subsystems", {})
        if subsystems:
            sub_lines = []
            for sub_key, sub_info in subsystems.items():
                name = sub_info.get("name", sub_key)
                stype = sub_info.get("type", "")
                sub_lines.append(f"- **{name}**: {stype}")
            fields["detector_subsystems"] = "\n".join(sub_lines)
        else:
            fields["detector_subsystems"] = "*No subsystem information available.*"

        # Available objects as a list string
        available = ", ".join(objects.keys()) if objects else "none"
        fields["available_objects"] = available

        return fields

    def _extract_config_fields(self, config) -> dict:
        """Extract template fields from an AnalysisConfig.

        Parameters
        ----------
        config : AnalysisConfig
            The analysis configuration object.

        Returns
        -------
        dict
            Mapping of template placeholder names to values.
        """
        fields = {}

        if config.sqrt_s is not None:
            fields["sqrt_s"] = str(config.sqrt_s)

        if config.signal_region:
            sr = config.signal_region
            sr_name = sr.get("name", "SR")
            cuts = sr.get("cuts", [])
            cut_strs = []
            for c in cuts:
                cut_strs.append(
                    f"{c.get('variable', '')} {c.get('operator', '')} "
                    f"{c.get('threshold', '')}"
                )
            fields["signal_region_definition"] = (
                f"{sr_name}: " + ", ".join(cut_strs) if cut_strs
                else sr_name
            )

        return fields
