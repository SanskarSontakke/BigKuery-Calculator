"""
CalculatorController - Controller connecting GUI to core.
"""

from typing import Optional
from bigkuery.core import Evaluator, EvalContext, EvalResult


class CalculatorController:
    """
    Calculator controller.
    
    Provides a high-level interface for the GUI to interact
    with the core calculation engine.
    """
    
    def __init__(self):
        """Initialize the calculator controller."""
        self._context = EvalContext()
        self._evaluator = Evaluator(self._context)
    
    @property
    def context(self) -> EvalContext:
        """Get the evaluation context."""
        return self._context
    
    @property
    def evaluator(self) -> Evaluator:
        """Get the evaluator."""
        return self._evaluator
    
    def evaluate(self, expression: str) -> EvalResult:
        """
        Evaluate an expression.
        
        Args:
            expression: The mathematical expression to evaluate
            
        Returns:
            EvalResult containing the value or error
        """
        return self._evaluator.evaluate(expression)
    
    def set_precision(self, precision_bits: int) -> None:
        """Set the calculation precision in bits."""
        self._context.precision = precision_bits
    
    def set_radians_mode(self, radians: bool) -> None:
        """Set the angle mode (radians or degrees)."""
        self._context.radians_mode = radians
    
    def set_variable(self, name: str, value: float) -> None:
        """Set a variable value."""
        from bigkuery.core import BigFloat
        self._context.set_variable(name, BigFloat(value))
    
    def get_variable(self, name: str) -> Optional[float]:
        """Get a variable value."""
        value = self._context.get_variable(name)
        if value is not None:
            return float(value)
        return None
    
    def clear_variables(self) -> None:
        """Clear all user-defined variables."""
        self._context.clear_variables()
