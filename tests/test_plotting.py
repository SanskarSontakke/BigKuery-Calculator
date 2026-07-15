import pytest

from bigkuery.core.plotting import PLOT_AVAILABLE, free_symbol_for_plot, render_plot_png

pytestmark = pytest.mark.skipif(not PLOT_AVAILABLE, reason="matplotlib/numpy not installed")


def test_free_symbol_for_plot_detects_single_variable():
    assert free_symbol_for_plot("sin(x)") == "x"
    assert free_symbol_for_plot("2*y + 1") == "y"


def test_free_symbol_for_plot_rejects_non_plottable():
    assert free_symbol_for_plot("2 + 2") is None          # no free symbols
    assert free_symbol_for_plot("x + y") is None           # two free symbols
    assert free_symbol_for_plot("x = 5") is None            # equation
    assert free_symbol_for_plot("x + y = 5; x - y = 1") is None  # system
    assert free_symbol_for_plot("") is None


def test_free_symbol_for_plot_excludes_known_definitions():
    # "a*x" has 2 raw free symbols, but once 'a' is a known definition it's
    # plottable in x alone.
    assert free_symbol_for_plot("a*x", known_names={"a"}) == "x"
    assert free_symbol_for_plot("a*x") is None


def test_render_plot_png_produces_valid_png():
    png = render_plot_png("sin(x)", "x")
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert len(png) > 100


def test_render_plot_png_substitutes_definitions():
    png = render_plot_png("a*x + 1", "x", definitions={"a": 3})
    assert png[:8] == b"\x89PNG\r\n\x1a\n"


def test_render_plot_png_raises_on_undefined_parameter():
    with pytest.raises(ValueError, match="Undefined parameter"):
        render_plot_png("a*x + b", "x", definitions={})
