
import pytest
import mpmath
from bigkuery.core.big_float import BigFloat

def test_initialization():
    bf = BigFloat(10)
    assert bf.to_int() == 10
    
    bf_str = BigFloat("3.14159")
    assert abs(bf_str.to_float() - 3.14159) < 1e-10

def test_arithmetic():
    a = BigFloat(10)
    b = BigFloat(2)
    
    assert (a + b).to_int() == 12
    assert (a - b).to_int() == 8
    assert (a * b).to_int() == 20
    assert (a / b).to_int() == 5
    assert (a ** b).to_int() == 100

def test_precision():
    # Use higher precision
    BigFloat.set_default_precision(100)
    pi = BigFloat.pi()
    assert pi.get_default_precision() == 100
    
    # Check that high precision is maintained
    with mpmath.workprec(53): # Standard double precision
        assert BigFloat.get_default_precision() == 53
    
    # Back to 100
    assert BigFloat.get_default_precision() == 100

def test_constants_safety():
    # Verify that calling constants doesn't permanently change precision
    old_prec = mpmath.mp.prec
    BigFloat.pi(precision=1000)
    assert mpmath.mp.prec == old_prec
