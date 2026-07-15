"""
BigKuery Core Module

The calculation engine is built on SymPy. This package exposes:
- The SymPy-based solver (equation solving, step-by-step evaluation, rendering)
- CalcContext, a small holder for calculator settings (angle mode, precision)
"""

from bigkuery.core.context import CalcContext
from bigkuery.core.solver import (
    solve_equation,
    solve_workspace_equation,
    solve_workspace_expression_steps,
    sympy_to_html,
)

__all__ = [
    "CalcContext",
    "solve_equation",
    "solve_workspace_equation",
    "solve_workspace_expression_steps",
    "sympy_to_html",
]
