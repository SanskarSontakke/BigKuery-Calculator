"""
ErrorMessages - User-friendly error message formatting.

This module provides friendly, actionable error messages for common
calculator errors to improve user experience.
"""

import re
from typing import Optional


class ErrorFormatter:
    """
    Formats technical error messages into user-friendly explanations.
    """
    
    # Pattern matching for common errors
    ERROR_PATTERNS = [
        # Bracket errors
        (r"Expected '\)'", 
         "Missing closing bracket `)`. Check that every `(` has a matching `)`."),
        (r"Expected '\('",
         "Missing opening bracket `(`. Check your function calls."),
        (r"Expected '\|'",
         "Missing closing `|` for absolute value. Use `|x|` format."),
        
        # Division errors
        (r"[Dd]ivision by zero",
         "Cannot divide by zero. Check the denominator of your expression."),
        (r"[Mm]odulo by zero",
         "Cannot perform modulo by zero. The divisor must be non-zero."),
        
        # Domain errors
        (r"[Dd]omain error.*complex",
         "This operation produces a complex number (e.g., √−1), which is not supported."),
        (r"[Dd]omain error",
         "The input is outside the valid range for this function."),
        
        # Variable errors
        (r"[Uu]ndefined variable[:\s]+(\w+)",
         lambda m: f"Variable '{m.group(1)}' is not defined. Assign it first with `{m.group(1)} = value`."),
        
        # Function errors
        (r"[Uu]nknown function[:\s]+(\w+)",
         lambda m: f"Unknown function '{m.group(1)}'. Check the spelling or see available functions."),
        (r"[Ff]unction '(\w+)' requires (\d+) arguments?",
         lambda m: f"Function '{m.group(1)}' needs {m.group(2)} argument(s). Example: `{m.group(1)}(x, y)`."),
        
        # Token errors
        (r"[Uu]nexpected token[:\s]+(.+)",
         lambda m: f"Unexpected character `{m.group(1).strip()}`. Check for typos or missing operators."),
        (r"[Ee]mpty expression",
         "Please enter an expression to calculate."),
        
        # Parse errors
        (r"[Pp]arse error[:\s]+(.*)",
         lambda m: f"Could not understand: {m.group(1).strip()}. Check the syntax."),
        
        # Value errors
        (r"[Vv]alue error[:\s]+(.*)",
         lambda m: f"Invalid value: {m.group(1).strip()}."),
        (r"[Ii]nvalid number[:\s]+(.+)",
         lambda m: f"'{m.group(1).strip()}' is not a valid number."),
        
        # Assignment errors
        (r"[Cc]annot assign to constant[:\s]+(\w+)",
         lambda m: f"Cannot change the constant '{m.group(1)}'. Use a different variable name."),
        
        # Factorial errors
        (r"[Ff]actorial.*negative",
         "Factorial is only defined for non-negative integers."),
        (r"[Ff]actorial.*integer",
         "Factorial requires an integer value."),
        
        # Logarithm errors
        (r"[Ll]ogarithm.*non-positive",
         "Logarithm is only defined for positive numbers."),
        (r"[Ll]ogarithm.*base",
         "Logarithm base must be positive and not equal to 1."),
        
        # Power errors
        (r"0\^0|zero.*zero.*power",
         "0^0 is undefined."),
        
        # Overflow
        (r"[Oo]verflow",
         "The result is too large to compute. Try a smaller value."),
        
        # Specific domain errors (acos, asin, etc.)
        (r"acos.*out.*range|acos.*domain",
         "acos(x) requires x to be between -1 and 1."),
        (r"asin.*out.*range|asin.*domain",
         "asin(x) requires x to be between -1 and 1."),
        (r"acosh.*out.*range|acosh.*domain",
         "acosh(x) requires x to be at least 1."),
        (r"atanh.*out.*range|atanh.*domain",
         "atanh(x) requires x to be between -1 and 1 (exclusive)."),
        
        # Square root of negative
        (r"sqrt.*negative|square root.*negative",
         "Cannot take the square root of a negative number."),
        
        # Log of zero or negative
        (r"log.*zero|log.*negative|ln.*zero|ln.*negative",
         "Logarithm is only defined for positive numbers."),
        
        # Tangent undefined
        (r"tan.*undefined|tangent.*undefined",
         "Tangent is undefined at this angle (90°, 270°, etc.)."),
        
        # mpmath specific errors
        (r"mpc|complex",
         "This operation produces a complex number, which is not supported."),
    ]
    
    @classmethod
    def format_error(cls, error_message: str) -> str:
        """
        Convert a technical error message to a user-friendly one.
        
        Args:
            error_message: The original error message
            
        Returns:
            A friendly, actionable error message
        """
        if not error_message:
            return "An unknown error occurred."
        
        # Try each pattern
        for pattern, replacement in cls.ERROR_PATTERNS:
            match = re.search(pattern, error_message, re.IGNORECASE)
            if match:
                if callable(replacement):
                    return replacement(match)
                return replacement
        
        # If no pattern matched, clean up the original message
        # Remove "Error:" prefix if present
        cleaned = re.sub(r'^[Ee]rror[:\s]+', '', error_message)
        cleaned = cleaned.strip()
        
        # Capitalize first letter
        if cleaned:
            cleaned = cleaned[0].upper() + cleaned[1:]
            if not cleaned.endswith('.'):
                cleaned += '.'
        
        return cleaned if cleaned else "An error occurred. Please check your expression."


def format_error(error_message: str) -> str:
    """Convenience function to format an error message."""
    return ErrorFormatter.format_error(error_message)
