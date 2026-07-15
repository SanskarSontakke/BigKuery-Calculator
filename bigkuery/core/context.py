"""
CalcContext - Lightweight calculator state shared between the GUI and solver.

The calculator engine is SymPy-based (see ``solver.py``). This small dataclass
holds the user-facing settings the solver needs: angle mode and the display
precision (number of significant digits used when evaluating numeric results).
"""

from __future__ import annotations
from dataclasses import dataclass


# Sensible default for numeric display: enough to look "exact" for everyday use
# while staying fast. The Settings dialog lets the user raise this up to 100.
DEFAULT_PRECISION = 15


@dataclass
class CalcContext:
    """Holds calculator settings that influence evaluation and display."""

    radians_mode: bool = False  # default to degrees (more intuitive for users)
    precision: int = DEFAULT_PRECISION  # significant digits for numeric output
    result_format: str = "scroll"  # "scroll" (grow wide) or "wrap" (cap width)

    def clamp_precision(self) -> int:
        """Return the precision clamped to a safe, supported range."""
        return max(1, min(1000, int(self.precision)))

    def is_wrap(self) -> bool:
        """Whether results should word-wrap within a capped width."""
        return self.result_format == "wrap"
