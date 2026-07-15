"""
BigKuery Calculator - Symbolic Scientific Calculator

A calculator supporting symbolic math, equation rearranging/solving,
step-by-step evaluation, and high-precision numeric results, powered by SymPy.
"""

__version__ = "1.0.0"
__author__ = "BigKuery"

from bigkuery.core import (
    CalcContext,
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
