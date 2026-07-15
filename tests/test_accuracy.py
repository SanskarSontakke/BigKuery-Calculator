import pytest
import sympy
from bigkuery.core.solver import solve_workspace_expression_steps, solve_workspace_equation, get_sympy_dicts

def test_algebraic_simplification_accuracy():
    # 1. Undefined variable trigonometric simplification (from user request)
    res, _ = solve_workspace_expression_steps("sin(x)^2 / sin(x)", {}, deg_mode=True)
    assert any("sin(x°)" in line for line in res)
    
    # 2. Algebraic simplification: (x+1)*(x-1) -> x^2 - 1
    res2, _ = solve_workspace_expression_steps("(x + 1) * (x - 1)", {}, deg_mode=True)
    assert any("x<sup>2</sup> - 1" in line for line in res2)
    
    # 3. Logarithmic simplification: log(e^y) -> y
    res3, _ = solve_workspace_expression_steps("log(e^y)", {}, deg_mode=False)
    assert any("y" in line for line in res3)

def test_arbitrary_precision_output():
    # sqrt(2) to 50 significant digits (stays symbolic until final formatting)
    res, _ = solve_workspace_expression_steps("sqrt(2)", {}, deg_mode=True, precision=50)
    assert any("1.4142135623730950488016887242096980785696718753769" in line for line in res)

    # pi via 4*atan(1) to 40 digits (precision must survive the atan reduction)
    res_pi, _ = solve_workspace_expression_steps("4*atan(1)", {}, deg_mode=False, precision=40)
    assert any("3.14159265358979323846264338327950288419" in line for line in res_pi)

    # e via exp(1) to 40 digits
    res_e, _ = solve_workspace_expression_steps("exp(1)", {}, deg_mode=False, precision=40)
    assert any("2.71828182845904523536028747135266249775" in line for line in res_e)

    # Lower precision really does truncate (not always full precision)
    res_low, _ = solve_workspace_expression_steps("sqrt(2)", {}, deg_mode=True, precision=8)
    assert any("1.4142136" in line for line in res_low)
    assert not any("1.41421356237309" in line for line in res_low)


def test_complex_number_output():
    # sqrt(-1) -> i
    res, _ = solve_workspace_expression_steps("sqrt(-1)", {}, deg_mode=True, precision=15)
    assert any(line.rstrip().endswith("i") for line in res)

    # (2 + 3i)(1 - i) = 5 + i
    res2, _ = solve_workspace_expression_steps("(2 + 3*I)*(1 - I)", {}, deg_mode=True, precision=15)
    assert any("5" in line and "+" in line and line.rstrip().endswith("i") for line in res2)


def test_calculus_functions():
    # Derivative
    res, _ = solve_workspace_expression_steps("diff(x^2, x)", {}, deg_mode=False)
    assert any("2" in line and "x" in line for line in res)
    # Definite integral
    res2, _ = solve_workspace_expression_steps("integrate(x^2, (x, 0, 1))", {}, deg_mode=False, precision=12)
    assert any("0.333" in line for line in res2)
    # Limit
    res3, _ = solve_workspace_expression_steps("limit(sin(x)/x, x, 0)", {}, deg_mode=False)
    assert any(line.strip().endswith("1") for line in res3)


def test_engineering_notation():
    res, _ = solve_workspace_expression_steps("1500000", {}, deg_mode=False, precision=6, eng=True)
    assert any("10<sup>6</sup>" in line for line in res)
    assert any("1.5" in line for line in res)


def test_integer_results_have_no_trailing_decimal():
    res, _ = solve_workspace_expression_steps("2 + 3*4", {}, deg_mode=True)
    assert any(line.strip().endswith("14") for line in res)
    assert not any("14.0" in line for line in res)


def test_system_of_equations_linear():
    res, defs = solve_workspace_equation("x + y = 5; x - y = 1", {}, deg_mode=False, precision=10)
    assert "x" in defs and "y" in defs
    assert abs(float(defs["x"]) - 3.0) < 1e-9
    assert abs(float(defs["y"]) - 2.0) < 1e-9
    assert any("x = 3" in line for line in res)
    assert any("y = 2" in line for line in res)


def test_system_of_equations_three_variables():
    res, defs = solve_workspace_equation(
        "a + b + c = 6; a - b = 0; c = 2", {}, deg_mode=False, precision=10
    )
    assert abs(float(defs["a"]) - 2.0) < 1e-9
    assert abs(float(defs["b"]) - 2.0) < 1e-9
    assert abs(float(defs["c"]) - 2.0) < 1e-9


def test_system_of_equations_nonlinear_multiple_solutions():
    res, defs = solve_workspace_equation("x^2 + y^2 = 25; x = 3", {}, deg_mode=False)
    assert any("-4" in line for line in res)
    assert any(line.strip().endswith("4") for line in res)
    # Multiple solution sets -> no single-valued definitions captured
    assert defs == {}


def test_system_of_equations_no_solution_does_not_crash():
    res, defs = solve_workspace_equation("x = 1; x = 2", {}, deg_mode=False)
    assert any("No solution" in line for line in res)


def test_single_equation_still_works_with_semicolon_in_other_card():
    # A lone equation (no ';') must still take the normal single-equation path.
    res, defs = solve_workspace_equation("x = 5", {}, deg_mode=True)
    assert defs.get("x") is not None
    assert abs(float(defs["x"]) - 5.0) < 1e-9


def test_equation_solves_for_lhs_symbol():
    # Assignment-like form must solve for the LHS symbol (y), not the
    # alphabetically-first free variable (a).
    res, defs = solve_workspace_equation("y = 2*a + b", {"a": 3, "b": 4}, deg_mode=True)
    assert "y" in defs
    assert abs(float(defs["y"]) - 10.0) < 1e-9


def test_double_equals_normalized():
    # 'x == 5' should be treated as the equation 'x = 5'
    res, defs = solve_workspace_equation("x == 5", {}, deg_mode=True)
    assert "x" in defs
    assert abs(float(defs["x"]) - 5.0) < 1e-9


def test_trig_eval_accuracy():
    # DEG Mode trig evaluation: sin(30) = 0.5, cos(60) = 0.5, tan(45) = 1
    eval_dict_deg, _ = get_sympy_dicts(deg_mode=True)
    
    sin_func = eval_dict_deg['sin']
    assert abs(float(sin_func(30).evalf()) - 0.5) < 1e-12
    
    cos_func = eval_dict_deg['cos']
    assert abs(float(cos_func(60).evalf()) - 0.5) < 1e-12
    
    tan_func = eval_dict_deg['tan']
    assert abs(float(tan_func(45).evalf()) - 1.0) < 1e-12
    
    # RAD Mode trig evaluation: sin(pi/6) = 0.5
    eval_dict_rad, _ = get_sympy_dicts(deg_mode=False)
    sin_rad = eval_dict_rad['sin']
    pi_val = sympy.pi
    assert abs(float(sin_rad(pi_val / 6).evalf()) - 0.5) < 1e-12

def test_equation_solving_accuracy():
    # Solve linear equation 2x + 5 = 15 -> x = 5
    res, defs = solve_workspace_equation("2*x + 5 = 15", {}, deg_mode=True)
    assert "x" in defs
    assert abs(float(defs["x"]) - 5.0) < 1e-12
    
    # Solve quadratic equation x^2 - 5*x + 6 = 0 -> x = 2, 3
    res2, defs2 = solve_workspace_equation("x^2 - 5*x + 6 = 0", {}, deg_mode=True)
    assert any("2" in line and "3" in line for line in res2 if "≈" in line or "{" in line)

def test_inverse_trig_deg_accuracy():
    # asin(0.5) in DEG mode should yield 30 degrees
    eval_dict_deg, _ = get_sympy_dicts(deg_mode=True)
    asin_func = eval_dict_deg['asin']
    assert abs(float(asin_func(0.5).evalf()) - 30.0) < 1e-12
    
    # acos(0.5) in DEG mode should yield 60 degrees
    acos_func = eval_dict_deg['acos']
    assert abs(float(acos_func(0.5).evalf()) - 60.0) < 1e-12

def test_complex_scientific_equation():
    # The complex equation that previously failed with TypeError due to deg/° handling
    eq_str = "abs( ln(i^i) + ( sin(45 deg) * acos(sqrt(3) / 2) ) / ( log10(1000) * exp(pi * i) ) ) - cbrt(x^2 + 5) = 0"
    
    # 1. Test in DEG mode
    res_deg, defs_deg = solve_workspace_equation(eq_str, {}, deg_mode=True)
    assert len(res_deg) >= 3
    approx_line = res_deg[-1]
    assert "25.3059" in approx_line
    assert "-25.3059" in approx_line
    
    # 2. Test in RAD mode
    res_rad, defs_rad = solve_workspace_equation(eq_str, {}, deg_mode=False)
    assert len(res_rad) >= 3

def test_complex_scientific_equation_with_degree_symbol():
    # Test identical equation using ° instead of deg
    eq_str = "abs( ln(i^i) + ( sin(45°) * acos(sqrt(3) / 2) ) / ( log10(1000) * exp(pi * i) ) ) - cbrt(x^2 + 5) = 0"
    
    res_deg, defs_deg = solve_workspace_equation(eq_str, {}, deg_mode=True)
    approx_line = res_deg[-1]
    assert "25.3059" in approx_line

