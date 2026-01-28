"""
MathFunctions - Registry of mathematical functions and constants.

This module provides the MathFunctions class which maintains a registry
of mathematical functions that can be called by name from expressions.
"""

from __future__ import annotations
from typing import Callable, Dict, List, Optional
import mpmath
import math

from .big_float import BigFloat


# Type aliases for function signatures
UnaryFunc = Callable[[BigFloat], BigFloat]
BinaryFunc = Callable[[BigFloat, BigFloat], BigFloat]
TernaryFunc = Callable[[BigFloat, BigFloat, BigFloat], BigFloat]


class MathFunctions:
    """
    Collection of mathematical functions and constants.
    
    Provides a registry of mathematical functions that can be called
    by name from the expression parser.
    """
    
    _unary_functions: Dict[str, UnaryFunc] = {}
    _binary_functions: Dict[str, BinaryFunc] = {}
    _ternary_functions: Dict[str, TernaryFunc] = {}
    _constants: Dict[str, Callable[[int], BigFloat]] = {}
    _initialized: bool = False
    
    @classmethod
    def initialize(cls) -> None:
        """Initialize the function registry with all built-in functions."""
        if cls._initialized:
            return
        
        # Unary functions
        cls._unary_functions = {
            # Trigonometric
            "sin": lambda x: BigFloat(mpmath.sin(x.mpf_value)),
            "cos": lambda x: BigFloat(mpmath.cos(x.mpf_value)),
            "tan": lambda x: BigFloat(mpmath.tan(x.mpf_value)),
            "cot": lambda x: BigFloat(mpmath.cot(x.mpf_value)),
            "sec": lambda x: BigFloat(mpmath.sec(x.mpf_value)),
            "csc": lambda x: BigFloat(mpmath.csc(x.mpf_value)),
            
            # Inverse trigonometric
            "asin": lambda x: BigFloat(mpmath.asin(x.mpf_value)),
            "acos": lambda x: BigFloat(mpmath.acos(x.mpf_value)),
            "atan": lambda x: BigFloat(mpmath.atan(x.mpf_value)),
            "acot": lambda x: BigFloat(mpmath.acot(x.mpf_value)),
            "asec": lambda x: BigFloat(mpmath.asec(x.mpf_value)),
            "acsc": lambda x: BigFloat(mpmath.acsc(x.mpf_value)),
            
            # Hyperbolic
            "sinh": lambda x: BigFloat(mpmath.sinh(x.mpf_value)),
            "cosh": lambda x: BigFloat(mpmath.cosh(x.mpf_value)),
            "tanh": lambda x: BigFloat(mpmath.tanh(x.mpf_value)),
            "coth": lambda x: BigFloat(mpmath.coth(x.mpf_value)),
            "sech": lambda x: BigFloat(mpmath.sech(x.mpf_value)),
            "csch": lambda x: BigFloat(mpmath.csch(x.mpf_value)),
            
            # Inverse hyperbolic
            "asinh": lambda x: BigFloat(mpmath.asinh(x.mpf_value)),
            "acosh": lambda x: BigFloat(mpmath.acosh(x.mpf_value)),
            "atanh": lambda x: BigFloat(mpmath.atanh(x.mpf_value)),
            
            # Exponential and logarithmic
            "exp": lambda x: BigFloat(mpmath.exp(x.mpf_value)),
            "log": lambda x: BigFloat(mpmath.log(x.mpf_value)),
            "ln": lambda x: BigFloat(mpmath.log(x.mpf_value)),
            "log10": lambda x: BigFloat(mpmath.log10(x.mpf_value)),
            "log2": lambda x: BigFloat(mpmath.log(x.mpf_value, 2)),
            
            # Power and root
            "sqrt": lambda x: BigFloat(mpmath.sqrt(x.mpf_value)),
            "cbrt": lambda x: BigFloat(mpmath.cbrt(x.mpf_value)),
            
            # Rounding
            "floor": lambda x: BigFloat(mpmath.floor(x.mpf_value)),
            "ceil": lambda x: BigFloat(mpmath.ceil(x.mpf_value)),
            "round": lambda x: BigFloat(mpmath.nint(x.mpf_value)),
            "trunc": lambda x: BigFloat(int(x.mpf_value)),
            
            # Other
            "abs": lambda x: BigFloat(abs(x.mpf_value)),
            "sign": lambda x: BigFloat(mpmath.sign(x.mpf_value)),
            "factorial": cls.factorial,
            "gamma": lambda x: BigFloat(mpmath.gamma(x.mpf_value)),
            "lgamma": lambda x: BigFloat(mpmath.loggamma(x.mpf_value)),
            
            # Angle conversion
            "deg": cls.to_degrees,
            "rad": cls.to_radians,
            "degrees": cls.to_degrees,
            "radians": cls.to_radians,
        }
        
        # Binary functions
        cls._binary_functions = {
            "pow": lambda x, y: BigFloat(mpmath.power(x.mpf_value, y.mpf_value)),
            "log": lambda x, b: BigFloat(mpmath.log(x.mpf_value, b.mpf_value)),
            "atan2": lambda y, x: BigFloat(mpmath.atan2(y.mpf_value, x.mpf_value)),
            "hypot": cls.hypot,
            "gcd": cls.gcd,
            "lcm": cls.lcm,
            "min": lambda x, y: BigFloat(min(x.mpf_value, y.mpf_value)),
            "max": lambda x, y: BigFloat(max(x.mpf_value, y.mpf_value)),
            "mod": cls.mod,
            "fmod": cls.mod,
            "binomial": cls.binomial,
            "nCr": cls.binomial,
            "nPr": lambda n, r: cls.factorial(n) / cls.factorial(BigFloat(n.mpf_value - r.mpf_value)),
        }
        
        # Ternary functions
        cls._ternary_functions = {
            "clamp": cls.clamp,
            "lerp": cls.lerp,
            "if": lambda cond, t, f: t if cond.mpf_value != 0 else f,
        }
        
        # Constants
        cls._constants = {
            "pi": lambda p: BigFloat(mpmath.pi),
            "e": lambda p: BigFloat(mpmath.e),
            "phi": lambda p: BigFloat(mpmath.phi),
            "tau": lambda p: BigFloat(2 * mpmath.pi),
            "euler": lambda p: BigFloat(mpmath.euler),
            "inf": lambda p: BigFloat(mpmath.inf),
            "nan": lambda p: BigFloat(mpmath.nan),
        }
        
        cls._initialized = True
    
    @classmethod
    def has_unary_function(cls, name: str) -> bool:
        """Check if a unary function exists."""
        cls.initialize()
        return name.lower() in cls._unary_functions
    
    @classmethod
    def has_binary_function(cls, name: str) -> bool:
        """Check if a binary function exists."""
        cls.initialize()
        return name.lower() in cls._binary_functions
    
    @classmethod
    def has_ternary_function(cls, name: str) -> bool:
        """Check if a ternary function exists."""
        cls.initialize()
        return name.lower() in cls._ternary_functions
    
    @classmethod
    def get_unary_function(cls, name: str) -> Optional[UnaryFunc]:
        """Get a unary function by name."""
        cls.initialize()
        return cls._unary_functions.get(name.lower())
    
    @classmethod
    def get_binary_function(cls, name: str) -> Optional[BinaryFunc]:
        """Get a binary function by name."""
        cls.initialize()
        return cls._binary_functions.get(name.lower())
    
    @classmethod
    def get_ternary_function(cls, name: str) -> Optional[TernaryFunc]:
        """Get a ternary function by name."""
        cls.initialize()
        return cls._ternary_functions.get(name.lower())
    
    @classmethod
    def get_constant(cls, name: str, precision: int = 256) -> Optional[BigFloat]:
        """Get a constant value by name."""
        cls.initialize()
        func = cls._constants.get(name.lower())
        if func:
            return func(precision)
        return None
    
    @classmethod
    def has_constant(cls, name: str) -> bool:
        """Check if a constant exists."""
        cls.initialize()
        return name.lower() in cls._constants
    
    @classmethod
    def get_available_functions(cls) -> List[str]:
        """Get list of all available function names."""
        cls.initialize()
        funcs = set(cls._unary_functions.keys())
        funcs.update(cls._binary_functions.keys())
        funcs.update(cls._ternary_functions.keys())
        return sorted(funcs)
    
    @classmethod
    def get_available_constants(cls) -> List[str]:
        """Get list of all available constant names."""
        cls.initialize()
        return sorted(cls._constants.keys())
    
    # Special function implementations
    
    @staticmethod
    def factorial(n: BigFloat) -> BigFloat:
        """Factorial (n!)."""
        val = int(n.mpf_value)
        if val < 0:
            raise ValueError("Factorial is not defined for negative numbers")
        return BigFloat(mpmath.factorial(val))
    
    @staticmethod
    def binomial(n: BigFloat, k: BigFloat) -> BigFloat:
        """Binomial coefficient (n choose k)."""
        return BigFloat(mpmath.binomial(int(n.mpf_value), int(k.mpf_value)))
    
    @staticmethod
    def gcd(a: BigFloat, b: BigFloat) -> BigFloat:
        """Greatest common divisor."""
        return BigFloat(math.gcd(int(a.mpf_value), int(b.mpf_value)))
    
    @staticmethod
    def lcm(a: BigFloat, b: BigFloat) -> BigFloat:
        """Least common multiple."""
        ai, bi = int(a.mpf_value), int(b.mpf_value)
        return BigFloat(abs(ai * bi) // math.gcd(ai, bi) if ai and bi else 0)
    
    @staticmethod
    def mod(a: BigFloat, b: BigFloat) -> BigFloat:
        """Modulo operation."""
        return BigFloat(mpmath.fmod(a.mpf_value, b.mpf_value))
    
    @staticmethod
    def floor_div(a: BigFloat, b: BigFloat) -> BigFloat:
        """Floor division."""
        return BigFloat(mpmath.floor(a.mpf_value / b.mpf_value))
    
    @staticmethod
    def clamp(value: BigFloat, min_val: BigFloat, max_val: BigFloat) -> BigFloat:
        """Clamp value between min and max."""
        if value.mpf_value < min_val.mpf_value:
            return min_val
        if value.mpf_value > max_val.mpf_value:
            return max_val
        return value
    
    @staticmethod
    def lerp(a: BigFloat, b: BigFloat, t: BigFloat) -> BigFloat:
        """Linear interpolation."""
        return BigFloat(a.mpf_value + (b.mpf_value - a.mpf_value) * t.mpf_value)
    
    @staticmethod
    def to_radians(degrees: BigFloat) -> BigFloat:
        """Convert degrees to radians."""
        return BigFloat(degrees.mpf_value * mpmath.pi / 180)
    
    @staticmethod
    def to_degrees(radians: BigFloat) -> BigFloat:
        """Convert radians to degrees."""
        return BigFloat(radians.mpf_value * 180 / mpmath.pi)
    
    @staticmethod
    def hypot(a: BigFloat, b: BigFloat) -> BigFloat:
        """Hypotenuse (sqrt(a^2 + b^2))."""
        return BigFloat(mpmath.hypot(a.mpf_value, b.mpf_value))
