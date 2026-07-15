"""
Plotting - Render a single-variable expression as a PNG image.

Uses matplotlib's non-interactive Agg backend (no display required) and SymPy's
``lambdify`` to turn a parsed expression into a fast numeric function. Kept
independent of the GUI so it can be tested headlessly.
"""

from __future__ import annotations

import io
from typing import Optional

import sympy
from sympy.parsing.sympy_parser import parse_expr

from .solver import get_sympy_dicts, transformations, log10, log2

try:
    import matplotlib
    matplotlib.use("Agg")  # must be set before importing pyplot
    import numpy as np
    PLOT_AVAILABLE = True
except Exception:
    PLOT_AVAILABLE = False


def _preprocess(expr_str: str) -> str:
    return (
        expr_str.replace('×', '*').replace('÷', '/')
        .replace('−', '-').replace('°', ' deg')
    )


def free_symbol_for_plot(expr_str: str, deg_mode: bool = True, known_names=None) -> Optional[str]:
    """Return the lone plottable variable name if expr_str is plottable, else None.

    ``known_names`` (variables already defined elsewhere in the workspace, e.g.
    "a" from another card) are excluded from the count, since they'll be
    substituted with a fixed value rather than treated as the plot axis. So
    "a*x" is plottable-in-x once "a" is defined, even though it has 2 raw
    free symbols.

    Not plottable: equations (contains '='), systems (contains ';'), empty
    expressions, or expressions with zero or more than one *undefined* symbol.
    """
    if not PLOT_AVAILABLE:
        return None
    text = expr_str.strip()
    if not text or '=' in text or ';' in text:
        return None
    try:
        processed = _preprocess(text)
        _, display_dict = get_sympy_dicts(deg_mode)
        expr = parse_expr(processed, local_dict=display_dict, transformations=transformations)
        known = set(known_names or ())
        free = {s for s in expr.free_symbols if s.name not in known}
        if len(free) != 1:
            return None
        return next(iter(free)).name
    except Exception:
        return None


def render_plot_png(
    expr_str: str,
    var_name: str,
    definitions: Optional[dict] = None,
    deg_mode: bool = True,
    x_range=(-10, 10),
    num_points: int = 400,
    dark: bool = True,
    figsize=(4.4, 2.8),
    dpi: int = 110,
) -> bytes:
    """Render y = expr_str over x_range as a PNG, returned as raw bytes.

    ``definitions`` (a {name: sympy value} dict from other workspace cards) are
    substituted for every free symbol except ``var_name``, so the curve reflects
    the calculator's current parameter values. Raises ValueError if the
    expression still has undefined parameters after substitution.
    """
    if not PLOT_AVAILABLE:
        raise RuntimeError("Plotting requires matplotlib and numpy.")

    import matplotlib.pyplot as plt  # local import: keeps module import cheap

    definitions = definitions or {}
    processed = _preprocess(expr_str)
    eval_dict, _ = get_sympy_dicts(deg_mode)
    expr = parse_expr(processed, local_dict=eval_dict, transformations=transformations)
    expr = expr.replace(log10, lambda x: sympy.log(x, 10)).replace(log2, lambda x: sympy.log(x, 2))

    subs_map = {
        sympy.Symbol(name): val for name, val in definitions.items() if name != var_name
    }
    if subs_map:
        expr = expr.subs(subs_map)

    var = sympy.Symbol(var_name)
    remaining = expr.free_symbols - {var}
    if remaining:
        names = ", ".join(sorted(s.name for s in remaining))
        raise ValueError(f"Undefined parameter(s): {names}")

    f = sympy.lambdify(var, expr, modules=["numpy"])
    x_min, x_max = x_range
    xs = np.linspace(x_min, x_max, num_points)
    with np.errstate(all="ignore"):
        ys = np.asarray(f(xs), dtype=float)
        if ys.shape == ():  # constant expression broadcast to a scalar
            ys = np.full_like(xs, float(ys))
    ys = np.where(np.isfinite(ys), ys, np.nan)

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    fig.patch.set_alpha(0)
    if dark:
        ax.set_facecolor("#20242c")
        line_color, grid_color, text_color = "#58a6ff", "#3c4048", "#d4d4d4"
    else:
        ax.set_facecolor("#ffffff")
        line_color, grid_color, text_color = "#1f77b4", "#cccccc", "#222222"

    ax.tick_params(colors=text_color, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(grid_color)
    ax.plot(xs, ys, color=line_color, linewidth=1.6)
    ax.axhline(0, color=grid_color, linewidth=0.8)
    ax.axvline(0, color=grid_color, linewidth=0.8)
    ax.grid(True, color=grid_color, alpha=0.3, linewidth=0.5)
    ax.set_xlabel(var_name, color=text_color, fontsize=9)
    fig.tight_layout(pad=0.6)

    buf = io.BytesIO()
    fig.savefig(buf, format="png", transparent=True)
    plt.close(fig)
    return buf.getvalue()
