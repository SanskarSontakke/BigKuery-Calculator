"""
Tokenizer - Lexical analysis for mathematical expressions.

This module provides the Tokenizer class which converts string expressions
into a sequence of tokens for parsing.
"""

from __future__ import annotations
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    """Token types for mathematical expressions."""
    
    # Literals
    NUMBER = auto()      # Numeric literal (integer or float)
    IDENTIFIER = auto()  # Variable or function name
    
    # Operators
    PLUS = auto()        # +
    MINUS = auto()       # -
    MULTIPLY = auto()    # * or ×
    DIVIDE = auto()      # / or ÷
    POWER = auto()       # ^ or **
    MODULO = auto()      # %
    FACTORIAL = auto()   # !
    
    # Brackets
    LEFT_PAREN = auto()    # (
    RIGHT_PAREN = auto()   # )
    LEFT_BRACKET = auto()  # [
    RIGHT_BRACKET = auto() # ]
    LEFT_BRACE = auto()    # {
    RIGHT_BRACE = auto()   # }
    
    # Delimiters
    COMMA = auto()       # ,
    SEMICOLON = auto()   # ;
    
    # Special
    EQUALS = auto()      # =
    PIPE = auto()        # | (for absolute value |x|)
    
    # Calculus operators
    INTEGRAL = auto()    # ∫
    DERIVATIVE = auto()  # d/dx
    SUMMATION = auto()   # Σ
    PRODUCT = auto()     # Π
    
    # Special tokens
    END_OF_INPUT = auto()  # End of expression
    UNKNOWN = auto()       # Unknown token


# Operator precedence table
PRECEDENCE = {
    TokenType.PLUS: 1,
    TokenType.MINUS: 1,
    TokenType.MULTIPLY: 2,
    TokenType.DIVIDE: 2,
    TokenType.MODULO: 2,
    TokenType.POWER: 3,
    TokenType.FACTORIAL: 4,
}

# Right-associative operators
RIGHT_ASSOCIATIVE = {TokenType.POWER}


@dataclass
class Token:
    """A single token from the expression."""
    
    type: TokenType
    value: str
    position: int
    length: int
    
    def type_name(self) -> str:
        """Get human-readable type name."""
        return self.type.name
    
    def is_operator(self) -> bool:
        """Check if token is an operator."""
        return self.type in (
            TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY,
            TokenType.DIVIDE, TokenType.POWER, TokenType.MODULO,
            TokenType.FACTORIAL
        )
    
    def is_binary_operator(self) -> bool:
        """Check if token is a binary operator."""
        return self.type in (
            TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY,
            TokenType.DIVIDE, TokenType.POWER, TokenType.MODULO
        )
    
    def is_unary_prefix(self) -> bool:
        """Check if token is a unary prefix operator."""
        return self.type in (TokenType.PLUS, TokenType.MINUS)
    
    def is_unary_postfix(self) -> bool:
        """Check if token is a unary postfix operator."""
        return self.type == TokenType.FACTORIAL
    
    def precedence(self) -> int:
        """Get operator precedence (higher = binds tighter)."""
        return PRECEDENCE.get(self.type, 0)
    
    def is_right_associative(self) -> bool:
        """Check if operator is right-associative."""
        return self.type in RIGHT_ASSOCIATIVE


class Tokenizer:
    """
    Tokenizer for mathematical expressions.
    
    Converts a string expression into a sequence of tokens.
    Supports:
    - Numbers (integers, decimals, scientific notation)
    - Unicode math symbols (π, ∫, ∞, etc.)
    - Standard operators and functions
    - Implicit multiplication (2x, 3(x+1))
    """
    
    # Unicode symbol mappings
    UNICODE_CONSTANTS = {
        'π': 'pi',
        'φ': 'phi',
        'τ': 'tau',
        '∞': 'inf',
        'γ': 'euler',
    }
    
    UNICODE_OPERATORS = {
        '×': TokenType.MULTIPLY,
        '÷': TokenType.DIVIDE,
        '∫': TokenType.INTEGRAL,
        'Σ': TokenType.SUMMATION,
        '∏': TokenType.PRODUCT,
        'Π': TokenType.PRODUCT,
    }
    
    def __init__(self, expression: str):
        """
        Initialize tokenizer for the given expression.
        
        Args:
            expression: The mathematical expression to tokenize
        """
        self._expression = expression
        self._pos = 0
        self._implicit_mult = True
        self._peeked: Optional[Token] = None
        self._last_token: Optional[Token] = None
    
    @property
    def expression(self) -> str:
        """Get original expression."""
        return self._expression
    
    @property
    def position(self) -> int:
        """Get current position."""
        return self._pos
    
    def set_implicit_multiplication(self, enable: bool) -> None:
        """Enable/disable implicit multiplication detection."""
        self._implicit_mult = enable
    
    def tokenize(self) -> List[Token]:
        """Tokenize the entire expression."""
        tokens = []
        self.reset()
        
        while self.has_more():
            token = self.next_token()
            tokens.append(token)
            if token.type == TokenType.END_OF_INPUT:
                break
        
        return tokens
    
    def next_token(self) -> Token:
        """Get the next token."""
        if self._peeked is not None:
            token = self._peeked
            self._peeked = None
            self._last_token = token
            return token
        
        # Check for implicit multiplication
        if self._implicit_mult and self._needs_implicit_multiply():
            token = Token(TokenType.MULTIPLY, "*", self._pos, 0)
            self._last_token = token
            return token
        
        self._skip_whitespace()
        
        if self._at_end():
            return Token(TokenType.END_OF_INPUT, "", self._pos, 0)
        
        token = self._read_token()
        self._last_token = token
        return token
    
    def peek_token(self) -> Token:
        """Peek at the next token without consuming it."""
        if self._peeked is None:
            self._peeked = self.next_token()
        return self._peeked
    
    def has_more(self) -> bool:
        """Check if there are more tokens."""
        return not self._at_end() or self._peeked is not None
    
    def reset(self) -> None:
        """Reset to beginning of expression."""
        self._pos = 0
        self._peeked = None
        self._last_token = None
    
    def _read_token(self) -> Token:
        """Read and return the next token."""
        start = self._pos
        c = self._current()
        
        # Check for number
        if self._is_digit(c) or (c == '.' and self._is_digit(self._peek())):
            return self._read_number()
        
        # Check for identifier
        if self._is_identifier_start(c):
            return self._read_identifier()
        
        # Check for Unicode operators
        if c in self.UNICODE_OPERATORS:
            self._advance()
            return Token(self.UNICODE_OPERATORS[c], c, start, 1)
        
        # Check for Unicode constants
        if c in self.UNICODE_CONSTANTS:
            self._advance()
            return Token(TokenType.IDENTIFIER, self.UNICODE_CONSTANTS[c], start, 1)
        
        # Single-character tokens
        self._advance()
        
        token_map = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULTIPLY,
            '/': TokenType.DIVIDE,
            '%': TokenType.MODULO,
            '^': TokenType.POWER,
            '!': TokenType.FACTORIAL,
            '(': TokenType.LEFT_PAREN,
            ')': TokenType.RIGHT_PAREN,
            '[': TokenType.LEFT_BRACKET,
            ']': TokenType.RIGHT_BRACKET,
            '{': TokenType.LEFT_BRACE,
            '}': TokenType.RIGHT_BRACE,
            ',': TokenType.COMMA,
            ';': TokenType.SEMICOLON,
            '=': TokenType.EQUALS,
            '|': TokenType.PIPE,
        }
        
        # Check for ** (power)
        if c == '*' and self._current() == '*':
            self._advance()
            return Token(TokenType.POWER, "**", start, 2)
        
        if c in token_map:
            return Token(token_map[c], c, start, 1)
        
        return Token(TokenType.UNKNOWN, c, start, 1)
    
    def _read_number(self) -> Token:
        """Read a number token."""
        start = self._pos
        
        # Read integer part
        while not self._at_end() and self._is_digit(self._current()):
            self._advance()
        
        # Read decimal part
        if not self._at_end() and self._current() == '.':
            self._advance()
            while not self._at_end() and self._is_digit(self._current()):
                self._advance()
        
        # Read exponent part (scientific notation)
        if not self._at_end() and self._current() in ('e', 'E'):
            self._advance()
            if not self._at_end() and self._current() in ('+', '-'):
                self._advance()
            while not self._at_end() and self._is_digit(self._current()):
                self._advance()
        
        value = self._expression[start:self._pos]
        return Token(TokenType.NUMBER, value, start, self._pos - start)
    
    def _read_identifier(self) -> Token:
        """Read an identifier (variable/function name)."""
        start = self._pos
        
        while not self._at_end() and self._is_identifier_part(self._current()):
            self._advance()
        
        value = self._expression[start:self._pos]
        return Token(TokenType.IDENTIFIER, value, start, self._pos - start)
    
    def _skip_whitespace(self) -> None:
        """Skip whitespace characters."""
        while not self._at_end() and self._current().isspace():
            self._advance()
    
    def _current(self) -> str:
        """Get current character."""
        if self._at_end():
            return '\0'
        return self._expression[self._pos]
    
    def _peek(self, offset: int = 1) -> str:
        """Get character at offset from current position."""
        pos = self._pos + offset
        if pos >= len(self._expression):
            return '\0'
        return self._expression[pos]
    
    def _advance(self) -> str:
        """Advance position and return current character."""
        c = self._current()
        self._pos += 1
        return c
    
    def _at_end(self) -> bool:
        """Check if at end of input."""
        return self._pos >= len(self._expression)
    
    @staticmethod
    def _is_digit(c: str) -> bool:
        """Check if character is a digit."""
        return c.isdigit()
    
    @staticmethod
    def _is_identifier_start(c: str) -> bool:
        """Check if character can start an identifier."""
        return c.isalpha() or c == '_'
    
    @staticmethod
    def _is_identifier_part(c: str) -> bool:
        """Check if character can continue an identifier."""
        return c.isalnum() or c == '_'
    
    def _needs_implicit_multiply(self) -> bool:
        """Check if implicit multiplication should be inserted."""
        if self._last_token is None:
            return False
        
        last_type = self._last_token.type
        
        # Save position and check next token type
        saved_pos = self._pos
        self._skip_whitespace()
        
        if self._at_end():
            return False
        
        c = self._current()
        
        # Determine what the next token would be
        next_is_number = self._is_digit(c)
        next_is_identifier = self._is_identifier_start(c) or c in self.UNICODE_CONSTANTS
        next_is_left_paren = c == '('
        
        # Restore position
        self._pos = saved_pos
        
        # Cases for implicit multiplication:
        # 1. number followed by identifier: 2x -> 2*x
        # 2. number followed by (: 2(x+1) -> 2*(x+1)
        # 3. ) followed by number: (x+1)2 -> (x+1)*2
        # 4. ) followed by (: (x)(y) -> (x)*(y)
        # 5. ) followed by identifier: (x)y -> (x)*y
        # 6. identifier followed by (: sin(x) is NOT implicit mult (it's function call)
        #    but x(2) is implicit mult
        
        if last_type == TokenType.NUMBER:
            if next_is_identifier or next_is_left_paren:
                return True
        
        if last_type == TokenType.RIGHT_PAREN:
            if next_is_number or next_is_identifier or next_is_left_paren:
                return True
        
        if last_type == TokenType.IDENTIFIER:
            # Only if not a function call
            if next_is_left_paren:
                # This is a function call, not implicit mult
                return False
            if next_is_number:
                return True
        
        return False
