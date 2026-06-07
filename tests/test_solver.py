import pytest
import sympy
from bigkuery.core.solver import solve_equation, sympy_to_html

def test_sympy_to_html_basic():
    # Test integer formatting
    assert sympy_to_html(sympy.Integer(5)) == "5"
    
    # Test addition and subtraction ordering
    expr = sympy.parse_expr("x - y + 3")
    html = sympy_to_html(expr)
    assert "x" in html
    assert "y" in html
    assert "3" in html

def test_sympy_to_html_fractions():
    # Test fraction formatting as HTML tables
    expr = sympy.parse_expr("x / 2")
    html = sympy_to_html(expr)
    assert "<table" in html
    assert "border-bottom:1px solid" in html
    assert "x" in html
    assert "2" in html

def test_sympy_to_html_trig_deg():
    # Test degrees conversion and presentation in DEG mode
    expr = sympy.parse_expr("sin(30)", local_dict={'sin': sympy.sin})
    html = sympy_to_html(expr, deg_mode=True)
    assert "sin(30°)" in html

def test_solve_simple_equation():
    # Solve linear equation x - 5 = 0
    res = solve_equation("x - 5 = 0")
    # Should show standard form, solved form, and numerical approximation
    assert any("x = 5" in line for line in res)
    assert any("5" in line for line in res if "≈" in line or "{" in line)

def test_solve_quadratic_equation():
    # Solve x^2 - 4 = 0 -> solutions -2, 2
    res = solve_equation("x^2 - 4 = 0")
    # Standard form representation
    assert any("x<sup>2</sup> - 4 = 0" in line for line in res)
    # Solution array
    assert any("-2" in line and "2" in line for line in res)

def test_solve_trig_equation():
    # Solve sin(x) = 0.5 in RAD mode
    res = solve_equation("sin(x) = 0.5", deg_mode=False)
    # Check if a solution exists (e.g. pi/6)
    assert len(res) >= 3
    # Solve sin(369) + cos(55)/sin(65) = abs(g)
    res_complex = solve_equation("sin(369) + cos(55)/sin(65) = abs(g)", deg_mode=True)
    assert len(res_complex) >= 3
    assert any("g" in line for line in res_complex)

def test_evaluate_expression():
    # Simple expression with numbers (step-by-step)
    res = solve_equation("2 + 3 * 4")
    assert len(res) >= 3
    assert any("14" in line for line in res)
    
    # Large numbers / powers
    res_large = solve_equation("10^5")
    assert any("100000" in line for line in res_large)

def test_cumulative_workspace_solving():
    from bigkuery.core.solver import solve_workspace_equation
    defs = {}
    r1, d1 = solve_workspace_equation("x = 3", defs)
    defs.update(d1)
    assert "x" in defs
    assert float(defs["x"]) == 3
    
    r2, d2 = solve_workspace_equation("x + 2", defs)
    assert any("5" in line for line in r2)

def test_singleton_preservation_and_no_type_leaking():
    from bigkuery.core.solver import substitute_unevaluated, get_sympy_dicts, sympy_to_html
    
    # 1. Check get_sympy_dicts display_dict contains no lambdas
    _, display_dict = get_sympy_dicts()
    for name, obj in display_dict.items():
        is_lambda = isinstance(obj, type(lambda: None)) and getattr(obj, '__name__', '') == '<lambda>'
        assert not is_lambda, f"Lambda found in display_dict: {name}"
        
    # 2. Check substitute_unevaluated preserves singleton identities
    expr = sympy.parse_expr("x + I + pi", evaluate=False)
    subbed = substitute_unevaluated(expr, sympy.Symbol("x"), sympy.Integer(5))
    
    # The subbed expression should still contain the exact same singletons by identity
    found_I = False
    found_pi = False
    for arg in subbed.args:
        if arg is sympy.I:
            found_I = True
        elif arg is sympy.pi:
            found_pi = True
            
    assert found_I, "Imaginary unit singleton identity was destroyed"
    assert found_pi, "Pi singleton identity was destroyed"
    
    # 3. Check sympy_to_html does not leak type names
    assert sympy_to_html(sympy.I) == "i"
    assert sympy_to_html(sympy.Rational(1, 2)) == "1/2"

