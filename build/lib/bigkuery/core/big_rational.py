"""
BigRational - Arbitrary precision rational arithmetic.

This module provides the BigRational class which wraps Python's
fractions.Fraction for exact rational arithmetic.
"""

from __future__ import annotations
from typing import Union
from fractions import Fraction
import math


class BigRational:
    """
    Arbitrary precision rational number class wrapping fractions.Fraction.
    
    Represents exact fractions as numerator/denominator pairs using
    arbitrary precision integers.
    """
    
    def __init__(
        self,
        numerator: Union[int, float, str, Fraction, 'BigRational'] = 0,
        denominator: Union[int, None] = None
    ):
        """
        Initialize a BigRational.
        
        Args:
            numerator: The numerator or full value
            denominator: The denominator (if numerator is just numerator)
        """
        if isinstance(numerator, BigRational):
            self._value = numerator._value
        elif isinstance(numerator, Fraction):
            self._value = numerator
        elif denominator is not None:
            self._value = Fraction(numerator, denominator)
        elif isinstance(numerator, str):
            self._value = Fraction(numerator)
        elif isinstance(numerator, float):
            self._value = Fraction(numerator).limit_denominator()
        else:
            self._value = Fraction(numerator)
    
    @property
    def numerator(self) -> int:
        """Get the numerator."""
        return self._value.numerator
    
    @property
    def denominator(self) -> int:
        """Get the denominator."""
        return self._value.denominator
    
    # Arithmetic operators
    def __add__(self, other: Union['BigRational', int, float, Fraction]) -> 'BigRational':
        if isinstance(other, BigRational):
            return BigRational(self._value + other._value)
        return BigRational(self._value + Fraction(other))
    
    def __radd__(self, other: Union[int, float]) -> 'BigRational':
        return BigRational(Fraction(other) + self._value)
    
    def __sub__(self, other: Union['BigRational', int, float, Fraction]) -> 'BigRational':
        if isinstance(other, BigRational):
            return BigRational(self._value - other._value)
        return BigRational(self._value - Fraction(other))
    
    def __rsub__(self, other: Union[int, float]) -> 'BigRational':
        return BigRational(Fraction(other) - self._value)
    
    def __mul__(self, other: Union['BigRational', int, float, Fraction]) -> 'BigRational':
        if isinstance(other, BigRational):
            return BigRational(self._value * other._value)
        return BigRational(self._value * Fraction(other))
    
    def __rmul__(self, other: Union[int, float]) -> 'BigRational':
        return BigRational(Fraction(other) * self._value)
    
    def __truediv__(self, other: Union['BigRational', int, float, Fraction]) -> 'BigRational':
        if isinstance(other, BigRational):
            return BigRational(self._value / other._value)
        return BigRational(self._value / Fraction(other))
    
    def __rtruediv__(self, other: Union[int, float]) -> 'BigRational':
        return BigRational(Fraction(other) / self._value)
    
    def __pow__(self, n: int) -> 'BigRational':
        """Compute this^n (integer exponent)."""
        return BigRational(self._value ** n)
    
    def __neg__(self) -> 'BigRational':
        return BigRational(-self._value)
    
    def __pos__(self) -> 'BigRational':
        return BigRational(+self._value)
    
    def __abs__(self) -> 'BigRational':
        return BigRational(abs(self._value))
    
    # Comparison operators
    def __eq__(self, other: object) -> bool:
        if isinstance(other, BigRational):
            return self._value == other._value
        if isinstance(other, (int, float, Fraction)):
            return self._value == Fraction(other)
        return NotImplemented
    
    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result
    
    def __lt__(self, other: Union['BigRational', int, float, Fraction]) -> bool:
        if isinstance(other, BigRational):
            return self._value < other._value
        return self._value < Fraction(other)
    
    def __le__(self, other: Union['BigRational', int, float, Fraction]) -> bool:
        if isinstance(other, BigRational):
            return self._value <= other._value
        return self._value <= Fraction(other)
    
    def __gt__(self, other: Union['BigRational', int, float, Fraction]) -> bool:
        if isinstance(other, BigRational):
            return self._value > other._value
        return self._value > Fraction(other)
    
    def __ge__(self, other: Union['BigRational', int, float, Fraction]) -> bool:
        if isinstance(other, BigRational):
            return self._value >= other._value
        return self._value >= Fraction(other)
    
    # Mathematical functions
    def reciprocal(self) -> 'BigRational':
        """Compute 1/this."""
        return BigRational(1, 1) / self
    
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
        """Check if value is an integer (denominator == 1)."""
        return self._value.denominator == 1
    
    def sign(self) -> int:
        """Get sign (-1, 0, or 1)."""
        if self._value > 0:
            return 1
        elif self._value < 0:
            return -1
        return 0
    
    def to_float(self) -> float:
        """Convert to float (may lose precision)."""
        return float(self._value)
    
    def to_decimal(self, decimal_places: int = 10) -> str:
        """Convert to decimal string with fixed precision."""
        value = float(self._value)
        return f"{value:.{decimal_places}f}"
    
    @property
    def fraction_value(self) -> Fraction:
        """Get the underlying Fraction value."""
        return self._value
    
    def __str__(self) -> str:
        if self._value.denominator == 1:
            return str(self._value.numerator)
        return f"{self._value.numerator}/{self._value.denominator}"
    
    def __repr__(self) -> str:
        return f"BigRational({self._value.numerator}, {self._value.denominator})"
    
    def __float__(self) -> float:
        return float(self._value)
    
    def __int__(self) -> int:
        return int(self._value)
    
    def __hash__(self) -> int:
        return hash(self._value)
    
    @staticmethod
    def gcd(a: int, b: int) -> int:
        """Compute greatest common divisor."""
        return math.gcd(a, b)
    
    @staticmethod
    def lcm(a: int, b: int) -> int:
        """Compute least common multiple."""
        return abs(a * b) // math.gcd(a, b) if a and b else 0
