"""Event selection engine, variable study, cut-flow, and plotting tools."""

from gad.selection.engine import SelectionEngine
from gad.selection.variables import study_variable_separation
from gad.selection.cutflow import format_cutflow_table, asimov_significance, create_binned_template
from gad.selection.plots import plot_n_minus_1, plot_variable_comparison

__all__ = [
    "SelectionEngine",
    "study_variable_separation",
    "format_cutflow_table",
    "asimov_significance",
    "create_binned_template",
    "plot_n_minus_1",
    "plot_variable_comparison",
]
