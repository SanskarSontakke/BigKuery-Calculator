"""
BigFloat - Arbitrary precision floating-point arithmetic.

This module provides the BigFloat class which wraps mpmath's mpf
for arbitrary precision floating-point operations.
"""

from __future__ import annotations
from typing import Union
import mpmath
from mpmath import mpf, mp


class BigFloat:
    """
    Arbitrary precision floating-point class wrapping mpmath's mpf.
    
    This class provides a Python interface for arbitrary precision
    floating-point arithmetic using the mpmath library.
    """
    
    DEFAULT_PRECISION = 53  # bits (equivalent to double precision)
    
    def __init__(
        self,
        value: Union[int, float, str, 'BigFloat', mpf] = 0,
        precision: int = None
    ):
        """
        Initialize a BigFloat.
        
        Args:
            value: Initial value (int, float, string, or another BigFloat)
            precision: Precision in bits (None uses current mpmath precision)
        """
        if precision is not None:
            old_prec = mp.prec
            mp.prec = precision
            
        if isinstance(value, BigFloat):
            self._value = mpf(value._value)
        elif isinstance(value, mpf):
            self._value = value
        elif isinstance(value, mpmath.mpc) or (isinstance(value, complex)):
            # Handle complex number
            # If imaginary part is non-zero (within precision), it's a domain error for this Real-only class
            # We use is_almost_eq to allow for small floating point errors if result should be real
            
            # Using mpmath.mp.eps * 100 as a safe tolerance for "zero"
            tolerance = mpmath.mp.eps * 100
            
            # Get imaginary magnitude
            try:
                imag_val = abs(value.imag)
            except:
                imag_val = abs(mpmath.im(value))

            if imag_val > tolerance:
                raise ValueError("Domain error: Result is complex")
            try:
                self._value = mpf(value.real)
            except:
                self._value = mpf(mpmath.re(value))
        else:
            self._value = mpf(value)
            
        if precision is not None:
            mp.prec = old_prec
            
        self._precision = precision or mp.prec
    
    @classmethod
    def set_default_precision(cls, precision: int) -> None:
        """Set the default precision for all new BigFloat operations."""
        mp.prec = precision
        cls.DEFAULT_PRECISION = precision
    
    @classmethod
    def get_default_precision(cls) -> int:
        """Get the current default precision."""
        return mp.prec
    
    # Arithmetic operators
    def __add__(self, other: Union['BigFloat', int, float]) -> 'BigFloat':
        if isinstance(other, BigFloat):
            return BigFloat(self._value + other._value)
        return BigFloat(self._value + mpf(other))
    
    def __radd__(self, other: Union[int, float]) -> 'BigFloat':
        return BigFloat(mpf(other) + self._value)
    
    def __sub__(self, other: Union['BigFloat', int, float]) -> 'BigFloat':
        if isinstance(other, BigFloat):
            return BigFloat(self._value - other._value)
        return BigFloat(self._value - mpf(other))
    
    def __rsub__(self, other: Union[int, float]) -> 'BigFloat':
        return BigFloat(mpf(other) - self._value)
    
    def __mul__(self, other: Union['BigFloat', int, float]) -> 'BigFloat':
        if isinstance(other, BigFloat):
            return BigFloat(self._value * other._value)
        return BigFloat(self._value * mpf(other))
    
    def __rmul__(self, other: Union[int, float]) -> 'BigFloat':
        return BigFloat(mpf(other) * self._value)
    
    def __truediv__(self, other: Union['BigFloat', int, float]) -> 'BigFloat':
        if isinstance(other, BigFloat):
            return BigFloat(self._value / other._value)
        return BigFloat(self._value / mpf(other))
    
    def __rtruediv__(self, other: Union[int, float]) -> 'BigFloat':
        return BigFloat(mpf(other) / self._value)
    
    def __floordiv__(self, other: Union['BigFloat', int, float]) -> 'BigFloat':
        if isinstance(other, BigFloat):
            return BigFloat(mpmath.floor(self._value / other._value))
        return BigFloat(mpmath.floor(self._value / mpf(other)))
    
    def __mod__(self, other: Union['BigFloat', int, float]) -> 'BigFloat':
        if isinstance(other, BigFloat):
            return BigFloat(mpmath.fmod(self._value, other._value))
        return BigFloat(mpmath.fmod(self._value, mpf(other)))
    
    def __pow__(self, other: Union['BigFloat', int, float]) -> 'BigFloat':
        if isinstance(other, BigFloat):
            return BigFloat(self._value ** other._value)
        return BigFloat(self._value ** mpf(other))
    
    def __rpow__(self, other: Union[int, float]) -> 'BigFloat':
        return BigFloat(mpf(other) ** self._value)
    
    def __neg__(self) -> 'BigFloat':
        return BigFloat(-self._value)
    
    def __pos__(self) -> 'BigFloat':
        return BigFloat(+self._value)
    
    def __abs__(self) -> 'BigFloat':
        return BigFloat(abs(self._value))
    
    # Comparison operators
    def __eq__(self, other: object) -> bool:
        if isinstance(other, BigFloat):
            return self._value == other._value
        if isinstance(other, (int, float)):
            return self._value == mpf(other)
        return NotImplemented
    
    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result
    
    def __lt__(self, other: Union['BigFloat', int, float]) -> bool:
        if isinstance(other, BigFloat):
            return self._value < other._value
        return self._value < mpf(other)
    
    def __le__(self, other: Union['BigFloat', int, float]) -> bool:
        if isinstance(other, BigFloat):
            return self._value <= other._value
        return self._value <= mpf(other)
    
    def __gt__(self, other: Union['BigFloat', int, float]) -> bool:
        if isinstance(other, BigFloat):
            return self._value > other._value
        return self._value > mpf(other)
    
    def __ge__(self, other: Union['BigFloat', int, float]) -> bool:
        if isinstance(other, BigFloat):
            return self._value >= other._value
        return self._value >= mpf(other)
    
    # Mathematical functions
    def sqrt(self) -> 'BigFloat':
        """Compute the square root."""
        return BigFloat(mpmath.sqrt(self._value))
    
    def exp(self) -> 'BigFloat':
        """Compute e^x."""
        return BigFloat(mpmath.exp(self._value))
    
    def log(self) -> 'BigFloat':
        """Compute natural logarithm."""
        return BigFloat(mpmath.log(self._value))
    
    def log10(self) -> 'BigFloat':
        """Compute base-10 logarithm."""
        return BigFloat(mpmath.log10(self._value))
    
    def log2(self) -> 'BigFloat':
        """Compute base-2 logarithm."""
        return BigFloat(mpmath.log(self._value, 2))
    
    def sin(self) -> 'BigFloat':
        """Compute sine."""
        return BigFloat(mpmath.sin(self._value))
    
    def cos(self) -> 'BigFloat':
        """Compute cosine."""
        return BigFloat(mpmath.cos(self._value))
    
    def tan(self) -> 'BigFloat':
        """Compute tangent."""
        return BigFloat(mpmath.tan(self._value))
    
    def asin(self) -> 'BigFloat':
        """Compute arc sine."""
        return BigFloat(mpmath.asin(self._value))
    
    def acos(self) -> 'BigFloat':
        """Compute arc cosine."""
        return BigFloat(mpmath.acos(self._value))
    
    def atan(self) -> 'BigFloat':
        """Compute arc tangent."""
        return BigFloat(mpmath.atan(self._value))
    
    def sinh(self) -> 'BigFloat':
        """Compute hyperbolic sine."""
        return BigFloat(mpmath.sinh(self._value))
    
    def cosh(self) -> 'BigFloat':
        """Compute hyperbolic cosine."""
        return BigFloat(mpmath.cosh(self._value))
    
    def tanh(self) -> 'BigFloat':
        """Compute hyperbolic tangent."""
        return BigFloat(mpmath.tanh(self._value))
    
    def floor(self) -> 'BigFloat':
        """Compute floor."""
        return BigFloat(mpmath.floor(self._value))
    
    def ceil(self) -> 'BigFloat':
        """Compute ceiling."""
        return BigFloat(mpmath.ceil(self._value))
    
    def round(self, n: int = 0) -> 'BigFloat':
        """Round to n decimal places."""
        if n == 0:
            return BigFloat(mpmath.nint(self._value))
        factor = mpf(10) ** n
        return BigFloat(mpmath.nint(self._value * factor) / factor)
    
    # Utility methods
    def is_zero(self) -> bool:
        """Check if value is zero."""
        return self._value == 0
    
    def is_positive(self) -> bool:
        """Check if value is positive."""
        return self._value > 0
    
    def is_negative(self) -> bool:
        """Check if value is negative."""
        return self._value < 0
    
    def is_integer(self) -> bool:
        """Check if value is an integer."""
        return self._value == mpmath.floor(self._value)
    
    def is_finite(self) -> bool:
        """Check if value is finite."""
        return mpmath.isfinite(self._value)
    
    def is_nan(self) -> bool:
        """Check if value is NaN."""
        return mpmath.isnan(self._value)
    
    def is_inf(self) -> bool:
        """Check if value is infinite."""
        return mpmath.isinf(self._value)
    
    def sign(self) -> int:
        """Get sign (-1, 0, or 1)."""
        if self._value > 0:
            return 1
        elif self._value < 0:
            return -1
        return 0
    
    def to_int(self) -> int:
        """Convert to integer."""
        return int(self._value)
    
    def to_float(self) -> float:
        """Convert to float (may lose precision)."""
        return float(self._value)
    
    def to_string(self, digits: int = 15) -> str:
        """Convert to string with specified decimal digits."""
        return mpmath.nstr(self._value, digits)
    
    @property
    def mpf_value(self) -> mpf:
        """Get the underlying mpmath mpf value."""
        return self._value
    
    def __str__(self) -> str:
        return str(self._value)
    
    def __repr__(self) -> str:
        return f"BigFloat('{self._value}')"
    
    def __float__(self) -> float:
        return float(self._value)
    
    def __int__(self) -> int:
        return int(self._value)
    
    def __hash__(self) -> int:
        return hash(self._value)
    
    # Class methods for constants
    @classmethod
    def pi(cls, precision: int = None) -> 'BigFloat':
        """Get pi with specified precision."""
        if precision:
            with mpmath.workprec(precision):
                return BigFloat(mpmath.pi)
        return BigFloat(mpmath.pi)
    
    @classmethod
    def e(cls, precision: int = None) -> 'BigFloat':
        """Get e (Euler's number) with specified precision."""
        if precision:
            with mpmath.workprec(precision):
                return BigFloat(mpmath.e)
        return BigFloat(mpmath.e)
    
    @classmethod
    def phi(cls, precision: int = None) -> 'BigFloat':
        """Get phi (golden ratio) with specified precision."""
        if precision:
            with mpmath.workprec(precision):
                return BigFloat(mpmath.phi)
        return BigFloat(mpmath.phi)
    
    @classmethod
    def euler_gamma(cls, precision: int = None) -> 'BigFloat':
        """Get Euler-Mascheroni constant with specified precision."""
        if precision:
            with mpmath.workprec(precision):
                return BigFloat(mpmath.euler)
        return BigFloat(mpmath.euler)
    
    @classmethod
    def inf(cls) -> 'BigFloat':
        """Get positive infinity."""
        return BigFloat(mpmath.inf)
    
    @classmethod
    def nan(cls) -> 'BigFloat':
        """Get NaN (Not a Number)."""
        return BigFloat(mpmath.nan)
