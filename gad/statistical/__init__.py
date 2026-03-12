"""Statistical model construction, fitting, diagnostics, and datacard export.

Provides WorkspaceBuilder for pyhf HistFactory workspace construction,
Fitter for MLE fits and expected CLs limit computation via cabinetry,
and Diagnostics for fit diagnostic plots and constraint analysis.
"""

from gad.statistical.workspace import WorkspaceBuilder
from gad.statistical.fitter import Fitter
from gad.statistical.diagnostics import Diagnostics
from gad.statistical.datacard import DatacardExporter, SensitivityOptimizer

__all__ = [
    "WorkspaceBuilder",
    "Fitter",
    "Diagnostics",
    "DatacardExporter",
    "SensitivityOptimizer",
]
