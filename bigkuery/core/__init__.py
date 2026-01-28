"""
BigKuery Core Module

This module provides the core mathematical functionality including:
- Arbitrary precision number types (BigFloat, BigRational)
- Expression tokenization and parsing
- Expression evaluation
- Mathematical functions registry
"""

from bigkuery.core.big_float import BigFloat
from bigkuery.core.big_rational import BigRational
from bigkuery.core.tokenizer import Tokenizer, Token, TokenType
from bigkuery.core.parser import Parser
from bigkuery.core.evaluator import Evaluator, EvalContext, EvalResult
from bigkuery.core.math_functions import MathFunctions
from bigkuery.core.error_messages import ErrorFormatter, format_error

__all__ = [
    "BigFloat",
    "BigRational",
    "Tokenizer",
    "Token",
    "TokenType",
    "Parser",
    "Evaluator",
    "EvalContext",
    "EvalResult",
    "MathFunctions",
    "ErrorFormatter",
    "format_error",
]
