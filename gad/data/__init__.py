"""Data access layer for GAD analysis framework."""

from .reader import DataReader
from .inventory import VariableInventory, scan_variable_inventory
from .quality import DataQualityScan

__all__ = [
    "DataReader",
    "VariableInventory",
    "scan_variable_inventory",
    "DataQualityScan",
]
