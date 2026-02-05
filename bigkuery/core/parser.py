"""
Parser - Expression parsing and AST generation.

This module provides the Parser class which converts a token stream
into an Abstract Syntax Tree (AST) for evaluation.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Union
from .tokenizer import Tokenizer, Token, TokenType


class NodeType(Enum):
    """AST node types."""
    NUMBER = auto()       # Numeric literal
    VARIABLE = auto()     # Variable reference
    UNARY_OP = auto()     # Unary operation
    BINARY_OP = auto()    # Binary operation
    FUNCTION_CALL = auto()  # Function call
    INTEGRAL = auto()     # Integral expression
    DERIVATIVE = auto()   # Derivative expression
    SUMMATION = auto()    # Summation expression
    PRODUCT = auto()      # Product expression
    ASSIGNMENT = auto()   # Variable assignment


class ASTNode(ABC):
    """Abstract syntax tree node base class."""
    
    @abstractmethod
    def node_type(self) -> NodeType:
        """Get the node type."""
        pass
    
    @abstractmethod
    def to_string(self) -> str:
        """Get string representation."""
        pass
    
    @abstractmethod
    def clone(self) -> 'ASTNode':
        """Create a deep copy of this node."""
        pass


@dataclass
class NumberNode(ASTNode):
    """Number literal node."""
    
    value: str
    
    def node_type(self) -> NodeType:
        return NodeType.NUMBER
    
    def to_string(self) -> str:
        return self.value
    
    def clone(self) -> 'NumberNode':
        return NumberNode(self.value)


@dataclass
class VariableNode(ASTNode):
    """Variable reference node."""
    
    name: str
    
    def node_type(self) -> NodeType:
        return NodeType.VARIABLE
    
    def to_string(self) -> str:
        return self.name
    
    def clone(self) -> 'VariableNode':
        return VariableNode(self.name)


@dataclass
class UnaryOpNode(ASTNode):
    """Unary operator node."""
    
    op: str
    operand: ASTNode
    is_prefix: bool = True
    
    def node_type(self) -> NodeType:
        return NodeType.UNARY_OP
    
    def to_string(self) -> str:
        if self.is_prefix:
            return f"({self.op}{self.operand.to_string()})"
        return f"({self.operand.to_string()}{self.op})"
    
    def clone(self) -> 'UnaryOpNode':
        return UnaryOpNode(self.op, self.operand.clone(), self.is_prefix)


@dataclass
class BinaryOpNode(ASTNode):
    """Binary operator node."""
    
    op: str
    left: ASTNode
    right: ASTNode
    
    def node_type(self) -> NodeType:
        return NodeType.BINARY_OP
    
    def to_string(self) -> str:
        return f"({self.left.to_string()} {self.op} {self.right.to_string()})"
    
    def clone(self) -> 'BinaryOpNode':
        return BinaryOpNode(self.op, self.left.clone(), self.right.clone())


@dataclass
class FunctionCallNode(ASTNode):
    """Function call node."""
    
    name: str
    arguments: List[ASTNode]
    
    def node_type(self) -> NodeType:
        return NodeType.FUNCTION_CALL
    
    def to_string(self) -> str:
        args = ", ".join(arg.to_string() for arg in self.arguments)
        return f"{self.name}({args})"
    
    def clone(self) -> 'FunctionCallNode':
        return FunctionCallNode(self.name, [arg.clone() for arg in self.arguments])


@dataclass
class AssignmentNode(ASTNode):
    """Variable assignment node."""
    
    variable: str
    expression: ASTNode
    
    def node_type(self) -> NodeType:
        return NodeType.ASSIGNMENT
    
    def to_string(self) -> str:
        return f"{self.variable} = {self.expression.to_string()}"
    
    def clone(self) -> 'AssignmentNode':
        return AssignmentNode(self.variable, self.expression.clone())


class ParseError(Exception):
    """Exception raised for parsing errors."""
    
    def __init__(self, message: str, position: int = 0):
        super().__init__(message)
        self.position = position


class Parser:
    """
    Parser for mathematical expressions.
    
    Converts a token stream into an Abstract Syntax Tree using
    a Pratt parser for proper operator precedence handling.
    """
    
    def __init__(self, expression: str):
        """
        Initialize parser with an expression.
        
        Args:
            expression: The mathematical expression to parse
        """
        self._tokenizer = Tokenizer(expression)
        self._current: Optional[Token] = None
        self._advance()
    
    def parse(self) -> ASTNode:
        """Parse the expression and return the AST root."""
        if self._check(TokenType.END_OF_INPUT):
            raise ParseError("Empty expression")
        
        result = self._parse_assignment()
        
        if not self._check(TokenType.END_OF_INPUT):
            raise ParseError(f"Unexpected token: {self._current.value}", self._current.position)
        
        return result
    
    def _parse_assignment(self) -> ASTNode:
        """Parse an assignment or expression."""
        # Try to parse as assignment: identifier = expression
        # This requires lookahead because an identifier could start a regular expression too (e.g., "x + 1")
        if self._check(TokenType.IDENTIFIER):
            name = self._current.value
            saved_pos = self._tokenizer.position
            self._advance()
            
            if self._check(TokenType.EQUALS):
                # Found "=", so it is an assignment
                self._advance()
                expr = self._parse_expression(0)
                return AssignmentNode(name, expr)
            
            # Not an assignment, backtrack to start
            # This is a bit expensive but robust
            self._tokenizer.reset()
            self._tokenizer._pos = 0
            self._tokenizer = Tokenizer(self._tokenizer.expression)
            self._advance()
        
        # Parse as standard expression if not an assignment
        return self._parse_expression(0)
    
    def _parse_expression(self, min_precedence: int) -> ASTNode:
        """Parse expression with operator precedence."""
        # Pratt Parsing (Top-Down Operator Precedence)
        # 1. Parse the "nud" (Null Denotation) - usually a literal or prefix op
        left = self._parse_unary()
        
        # 2. Loop while the next token has higher precedence than current context
        while True:
            if self._current is None or self._check(TokenType.END_OF_INPUT):
                break
            
            if not self._current.is_binary_operator():
                break
            
            # Check precedence
            precedence = self._current.precedence()
            if precedence < min_precedence:
                break
            
            # Parse the "led" (Left Denotation) - usually an infix op
            op = self._current.value
            is_right_assoc = self._current.is_right_associative()
            self._advance()
            
            # For right-associative operators (like ^), use same precedence to allow chaining
            # For left-associative (like +), use precedence + 1 to force grouping
            next_min_prec = precedence if is_right_assoc else precedence + 1
            right = self._parse_expression(next_min_prec)
            
            # Combine left and right into a new binary operation node
            left = BinaryOpNode(op, left, right)
        
        return left
    
    def _parse_unary(self) -> ASTNode:
        """Parse unary operators."""
        # Prefix operators
        if self._check(TokenType.PLUS) or self._check(TokenType.MINUS):
            op = self._current.value
            self._advance()
            operand = self._parse_unary()
            return UnaryOpNode(op, operand, is_prefix=True)
        
        return self._parse_postfix()
    
    def _parse_postfix(self) -> ASTNode:
        """Parse postfix operators."""
        left = self._parse_primary()
        
        # Postfix operators (factorial)
        while self._check(TokenType.FACTORIAL):
            op = self._current.value
            self._advance()
            left = UnaryOpNode(op, left, is_prefix=False)
        
        return left
    
    def _parse_primary(self) -> ASTNode:
        """Parse primary expressions (numbers, variables, functions, groups)."""
        # Case 1: Number literal
        if self._check(TokenType.NUMBER):
            value = self._current.value
            self._advance()
            return NumberNode(value)
        
        # Case 2: Identifier (variable or function call)
        if self._check(TokenType.IDENTIFIER):
            name = self._current.value
            self._advance()
            
            # Look ahead for '(' to distinguish function calls from variables
            if self._check(TokenType.LEFT_PAREN):
                return self._parse_function_call(name)
            
            return VariableNode(name)
        
        # Case 3: Parenthesized expression (grouping)
        if self._check(TokenType.LEFT_PAREN):
            self._advance()
            # Reset precedence counter for inside the parentheses
            expr = self._parse_expression(0)
            self._expect(TokenType.RIGHT_PAREN, "Expected ')'")
            return expr
        
        # Case 4: Absolute value |x|
        # Syntactic sugar for abs(x)
        if self._check(TokenType.PIPE):
            self._advance()
            expr = self._parse_expression(0)
            self._expect(TokenType.PIPE, "Expected '|'")
            return FunctionCallNode("abs", [expr])
        
        raise ParseError(
            f"Unexpected token: {self._current.value if self._current else 'EOF'}",
            self._current.position if self._current else 0
        )
    
    def _parse_function_call(self, name: str) -> FunctionCallNode:
        """Parse a function call with arguments."""
        self._expect(TokenType.LEFT_PAREN, "Expected '(' after function name")
        
        arguments: List[ASTNode] = []
        
        if not self._check(TokenType.RIGHT_PAREN):
            arguments.append(self._parse_expression(0))
            
            while self._check(TokenType.COMMA):
                self._advance()
                arguments.append(self._parse_expression(0))
        
        self._expect(TokenType.RIGHT_PAREN, "Expected ')' after arguments")
        
        return FunctionCallNode(name, arguments)
    
    def _advance(self) -> Token:
        """Advance to the next token."""
        previous = self._current
        self._current = self._tokenizer.next_token()
        return previous
    
    def _check(self, token_type: TokenType) -> bool:
        """Check if current token matches the given type."""
        if self._current is None:
            return False
        return self._current.type == token_type
    
    def _expect(self, token_type: TokenType, message: str) -> Token:
        """Expect a specific token type, raise error if not found."""
        if not self._check(token_type):
            raise ParseError(message, self._current.position if self._current else 0)
        return self._advance()
