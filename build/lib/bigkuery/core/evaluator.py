"""
Evaluator - Expression evaluation engine.

This module provides the Evaluator class which evaluates AST nodes
to compute expression results.
"""

from __future__ import annotations
from typing import Dict, Optional, Union
from dataclasses import dataclass, field
import mpmath

from .big_float import BigFloat
from .parser import (
    Parser, ASTNode, NodeType, NumberNode, VariableNode,
    UnaryOpNode, BinaryOpNode, FunctionCallNode, AssignmentNode, ParseError
)
from .math_functions import MathFunctions


@dataclass
class EvalResult:
    """Result of an evaluation - either a number or an error."""
    
    value: Optional[BigFloat] = None
    error: Optional[str] = None
    
    @property
    def is_number(self) -> bool:
        """Check if result is a number."""
        return self.value is not None and self.error is None
    
    @property
    def is_error(self) -> bool:
        """Check if result is an error."""
        return self.error is not None
    
    def to_string(self, digits: int = 15) -> str:
        """Convert result to string."""
        if self.is_error:
            return f"Error: {self.error}"
        if self.value is not None:
            return self.value.to_string(digits)
        return "undefined"
    
    @classmethod
    def from_value(cls, value: BigFloat) -> 'EvalResult':
        """Create a result from a value."""
        return cls(value=value)
    
    @classmethod
    def from_error(cls, error: str) -> 'EvalResult':
        """Create an error result."""
        return cls(error=error)


@dataclass
class EvalContext:
    """Evaluation context holding variables and settings."""
    
    variables: Dict[str, BigFloat] = field(default_factory=dict)
    precision: int = 256  # bits
    radians_mode: bool = False  # Default to degrees (more intuitive)
    
    def __post_init__(self):
        """Initialize built-in constants."""
        MathFunctions.initialize()
    
    def set_variable(self, name: str, value: BigFloat) -> None:
        """Set a variable value."""
        self.variables[name] = value
    
    def get_variable(self, name: str) -> Optional[BigFloat]:
        """Get a variable value."""
        # Check user variables first
        if name in self.variables:
            return self.variables[name]
        
        # Check built-in constants
        return MathFunctions.get_constant(name, self.precision)
    
    def has_variable(self, name: str) -> bool:
        """Check if a variable exists."""
        return name in self.variables or MathFunctions.has_constant(name)
    
    def clear_variables(self) -> None:
        """Clear all user-defined variables."""
        self.variables.clear()


class Evaluator:
    """
    Expression evaluator.
    
    Evaluates AST nodes to compute expression results using
    arbitrary precision arithmetic.
    """
    
    def __init__(self, context: Optional[EvalContext] = None):
        """
        Initialize the evaluator.
        
        Args:
            context: Evaluation context (creates new one if not provided)
        """
        self._context = context or EvalContext()
        self._last_result = BigFloat(0)
        MathFunctions.initialize()
    
    @property
    def context(self) -> EvalContext:
        """Get the evaluation context."""
        return self._context
    
    @property
    def last_result(self) -> BigFloat:
        """Get the last computed result."""
        return self._last_result
    
    def evaluate(self, expr: Union[str, ASTNode]) -> EvalResult:
        """
        Evaluate an expression.
        
        Args:
            expr: Expression string or AST node
            
        Returns:
            EvalResult containing the value or error
        """
        # Set precision
        mpmath.mp.prec = self._context.precision
        
        try:
            if isinstance(expr, str):
                if not expr.strip():
                    return EvalResult.from_error("Empty expression")
                parser = Parser(expr)
                node = parser.parse()
            else:
                node = expr
            
            result = self._evaluate_node(node)
            
            if result.is_number and result.value is not None:
                self._last_result = result.value
                # Store as 'ans' variable
                self._context.set_variable("ans", result.value)
            
            return result
            
        except ParseError as e:
            return EvalResult.from_error(f"Parse error: {e}")
        except ValueError as e:
            return EvalResult.from_error(f"Value error: {e}")
        except ZeroDivisionError:
            return EvalResult.from_error("Division by zero")
        except Exception as e:
            return EvalResult.from_error(str(e))
    
    def _evaluate_node(self, node: ASTNode) -> EvalResult:
        """Evaluate an AST node."""
        node_type = node.node_type()
        
        if node_type == NodeType.NUMBER:
            return self._evaluate_number(node)
        elif node_type == NodeType.VARIABLE:
            return self._evaluate_variable(node)
        elif node_type == NodeType.UNARY_OP:
            return self._evaluate_unary_op(node)
        elif node_type == NodeType.BINARY_OP:
            return self._evaluate_binary_op(node)
        elif node_type == NodeType.FUNCTION_CALL:
            return self._evaluate_function_call(node)
        elif node_type == NodeType.ASSIGNMENT:
            return self._evaluate_assignment(node)
        else:
            return EvalResult.from_error(f"Unknown node type: {node_type}")
    
    def _evaluate_number(self, node: NumberNode) -> EvalResult:
        """Evaluate a number node."""
        try:
            value = BigFloat(node.value)
            return EvalResult.from_value(value)
        except Exception as e:
            return EvalResult.from_error(f"Invalid number: {node.value}")
    
    def _evaluate_variable(self, node: VariableNode) -> EvalResult:
        """Evaluate a variable node."""
        value = self._context.get_variable(node.name)
        
        if value is None:
            return EvalResult.from_error(f"Undefined variable: {node.name}")
        
        return EvalResult.from_value(value)
    
    def _evaluate_unary_op(self, node: UnaryOpNode) -> EvalResult:
        """Evaluate a unary operation."""
        operand_result = self._evaluate_node(node.operand)
        
        if operand_result.is_error:
            return operand_result
        
        operand = operand_result.value
        
        if node.op == '+':
            return EvalResult.from_value(operand)
        elif node.op == '-':
            return EvalResult.from_value(-operand)
        elif node.op == '!':
            # Factorial
            try:
                result = MathFunctions.factorial(operand)
                return EvalResult.from_value(result)
            except ValueError as e:
                return EvalResult.from_error(str(e))
        else:
            return EvalResult.from_error(f"Unknown unary operator: {node.op}")
    
    def _evaluate_binary_op(self, node: BinaryOpNode) -> EvalResult:
        """Evaluate a binary operation."""
        left_result = self._evaluate_node(node.left)
        if left_result.is_error:
            return left_result
        
        right_result = self._evaluate_node(node.right)
        if right_result.is_error:
            return right_result
        
        left = left_result.value
        right = right_result.value
        
        try:
            if node.op == '+':
                result = left + right
            elif node.op == '-':
                result = left - right
            elif node.op == '*':
                result = left * right
            elif node.op == '/':
                if right.is_zero():
                    return EvalResult.from_error("Division by zero")
                result = left / right
            elif node.op == '^' or node.op == '**':
                result = left ** right
            elif node.op == '%':
                if right.is_zero():
                    return EvalResult.from_error("Modulo by zero")
                result = left % right
            else:
                return EvalResult.from_error(f"Unknown operator: {node.op}")
            
            return EvalResult.from_value(result)
            
        except Exception as e:
            return EvalResult.from_error(str(e))
    
    def _evaluate_function_call(self, node: FunctionCallNode) -> EvalResult:
        """Evaluate a function call."""
        # Evaluate all arguments
        args = []
        for arg_node in node.arguments:
            arg_result = self._evaluate_node(arg_node)
            if arg_result.is_error:
                return arg_result
            args.append(arg_result.value)
        
        name = node.name.lower()
        num_args = len(args)
        
        try:
            # Handle angle mode conversion for trig functions
            if not self._context.radians_mode and name in (
                'sin', 'cos', 'tan', 'cot', 'sec', 'csc'
            ) and num_args == 1:
                # Convert degrees to radians
                args[0] = MathFunctions.to_radians(args[0])
            
            # Try to find the appropriate function
            if num_args == 1:
                func = MathFunctions.get_unary_function(name)
                if func:
                    result = func(args[0])
                    
                    # Convert back to degrees for inverse trig functions
                    if not self._context.radians_mode and name in (
                        'asin', 'acos', 'atan', 'acot', 'asec', 'acsc'
                    ):
                        result = MathFunctions.to_degrees(result)
                    
                    return EvalResult.from_value(result)
                
                # Check if it's a binary function called with 1 arg (error)
                if MathFunctions.has_binary_function(name):
                    return EvalResult.from_error(
                        f"Function '{name}' requires 2 arguments"
                    )
            
            elif num_args == 2:
                func = MathFunctions.get_binary_function(name)
                if func:
                    result = func(args[0], args[1])
                    return EvalResult.from_value(result)
                
                # Special case: log with base
                if name == 'log':
                    func = MathFunctions.get_binary_function('log')
                    if func:
                        result = func(args[0], args[1])
                        return EvalResult.from_value(result)
            
            elif num_args == 3:
                func = MathFunctions.get_ternary_function(name)
                if func:
                    result = func(args[0], args[1], args[2])
                    return EvalResult.from_value(result)
            
            return EvalResult.from_error(
                f"Unknown function: {name} with {num_args} argument(s)"
            )
            
        except Exception as e:
            return EvalResult.from_error(f"Error in {name}: {e}")
    
    def _evaluate_assignment(self, node: AssignmentNode) -> EvalResult:
        """Evaluate a variable assignment."""
        # Check if trying to assign to a constant
        if MathFunctions.has_constant(node.variable):
            return EvalResult.from_error(
                f"Cannot assign to constant: {node.variable}"
            )
        
        expr_result = self._evaluate_node(node.expression)
        
        if expr_result.is_error:
            return expr_result
        
        self._context.set_variable(node.variable, expr_result.value)
        return expr_result
