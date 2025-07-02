"""
lil' bank buddy: Your friendly CLI for bank account analysis and reporting.

A Python CLI tool for analyzing bank transactions, generating reports, 
and splitting expenses between multiple people.
"""

from .core.database import DatabaseManager
from .core.analysis import BankAnalyzer, ExpenseSplitter
from .core.report import ReportGenerator

__version__ = "0.1.0"
__author__ = "Your Name"

# Expose main components
__all__ = [
    "DatabaseManager",
    "BankAnalyzer", 
    "ExpenseSplitter",
    "ReportGenerator",
]
