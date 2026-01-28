
import pytest
from bigkuery.core.evaluator import Evaluator, EvalContext
from bigkuery.core.big_float import BigFloat

def test_basic_evaluation():
    evaluator = Evaluator()
    result = evaluator.evaluate("2 + 2")
    assert result.is_number
    assert result.value.to_int() == 4

def test_variables():
    context = EvalContext()
    evaluator = Evaluator(context)
    
    context.set_variable("x", BigFloat(10))
    result = evaluator.evaluate("x * 2")
    assert result.value.to_int() == 20

def test_assignment():
    evaluator = Evaluator()
    evaluator.evaluate("x = 5")
    result = evaluator.evaluate("x + 1")
    assert result.value.to_int() == 6

def test_functions():
    evaluator = Evaluator()
    result = evaluator.evaluate("sqrt(16)")
    assert result.value.to_int() == 4

def test_trig_modes():
    context = EvalContext()
    evaluator = Evaluator(context)
    
    # Degrees (default)
    result = evaluator.evaluate("sin(90)")
    assert result.value.to_int() == 1
    
    # Radians
    context.radians_mode = True
    # sin(pi/2) approx 1
    result = evaluator.evaluate(f"sin({BigFloat.pi().to_string()}/2)") 
    # Use close assertion due to floating point
    assert abs(result.value.to_float() - 1.0) < 1e-10

def test_errors():
    evaluator = Evaluator()
    result = evaluator.evaluate("1 / 0")
    assert result.is_error
    assert "divide" in result.error.lower() or "division" in result.error.lower()
