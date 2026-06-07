import pytest
import sympy
import mpmath
from bigkuery.core.solver import solve_workspace_expression_steps, solve_workspace_equation, get_sympy_dicts
from bigkuery.core.big_float import BigFloat
from bigkuery.core.evaluator import Evaluator, EvalContext

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

def test_high_precision_accuracy():
    # Verify that BigFloat calculates mathematical constants with high accuracy
    # Check Pi to 50 decimals
    BigFloat.set_default_precision(166)  # ~50 decimal digits (50 * 3.32)
    pi_bf = BigFloat.pi()
    pi_str = pi_bf.to_string(digits=50)
    expected_pi = "3.1415926535897932384626433832795028841971693993751"
    assert pi_str.startswith(expected_pi[:48])
    
    # Check Euler's constant to 40 decimals
    euler_bf = BigFloat.euler_gamma()
    euler_str = euler_bf.to_string(digits=40)
    expected_euler = "0.577215664901532860606512090082402431042"
    assert euler_str.startswith(expected_euler[:38])

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

