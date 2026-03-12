"""Publication plot regeneration with mplhep styling."""

import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)


def setup_experiment_style(experiment_style: str) -> None:
    """Apply mplhep experiment style with graceful fallback.

    Parameters
    ----------
    experiment_style : str
        Experiment name, e.g. "ATLAS", "CMS", "LHCb".
        Falls back to default matplotlib if style not found or mplhep unavailable.
    """
    try:
        import mplhep
        style = getattr(mplhep.style, experiment_style, None)
        if style is not None:
            plt.style.use(style)
        else:
            logger.info(
                "mplhep style '%s' not found, using default matplotlib style",
                experiment_style,
            )
    except (ImportError, AttributeError):
        logger.info("mplhep not available, using default matplotlib style")


def regenerate_all_plots(config: dict) -> dict:
    """Regenerate publication plots from a config mapping.

    Parameters
    ----------
    config : dict
        Mapping of plot_name -> {"generator": callable, "output_path": str, "kwargs": dict}.
        Each generator is called with **kwargs and should return a matplotlib Figure.

    Returns
    -------
    dict
        {"total": int, "generated": int, "failed": list}
    """
    total = len(config)
    generated = 0
    failed = []

    for plot_name, spec in config.items():
        generator = spec["generator"]
        output_path = spec["output_path"]
        kwargs = spec.get("kwargs", {})

        try:
            fig = generator(**kwargs)
            # Save to PDF
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            if fig is not None and hasattr(fig, "savefig"):
                fig.savefig(output_path, bbox_inches="tight")
                plt.close(fig)
            generated += 1
            logger.info("Generated plot: %s -> %s", plot_name, output_path)
        except Exception as exc:
            logger.error("Failed to generate plot %s: %s", plot_name, exc)
            failed.append({"plot_name": plot_name, "error": str(exc)})

    return {"total": total, "generated": generated, "failed": failed}
