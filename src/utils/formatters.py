"""Formatting utilities for currency, dates, and other data display."""
from typing import Dict, Any

def format_dollar(amount: float) -> str:
    """Format a number as a dollar amount with proper sign handling."""
    if amount < 0:
        return f"-${abs(amount):.2f}"
    return f"${amount:.2f}"

def dict_to_md_table(d: Dict[str, Any]) -> str:
    """Convert a dictionary to a markdown table."""
    if not d:
        return 'None'
    header = '| Category | Count |\n|---|---|'
    rows = [f"| {k} | {v} |" for k, v in d.items()]
    return '\n'.join([header] + rows)

def format_percentage(value: float, decimals: int = 1) -> str:
    """Format a number as a percentage."""
    return f"{value:.{decimals}f}%"

def truncate_description(description: str, max_length: int = 50) -> str:
    """Truncate a description to a maximum length with ellipsis."""
    if len(description) <= max_length:
        return description
    return description[:max_length-3] + "..."
