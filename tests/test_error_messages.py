
import pytest
from bigkuery.core.error_messages import ErrorFormatter, format_error


class TestErrorFormatter:
    """Tests for user-friendly error message formatting."""
    
    def test_bracket_error(self):
        result = format_error("Expected ')'")
        assert ")" in result
        assert "bracket" in result.lower() or "closing" in result.lower()
    
    def test_division_by_zero(self):
        result = format_error("Division by zero")
        assert "zero" in result.lower()
        assert "divide" in result.lower() or "cannot" in result.lower()
    
    def test_undefined_variable(self):
        result = format_error("Undefined variable: x")
        assert "x" in result
        assert "defined" in result.lower() or "assign" in result.lower()
    
    def test_unknown_function(self):
        result = format_error("Unknown function: foobar with 1 argument(s)")
        assert "foobar" in result
        assert "unknown" in result.lower() or "function" in result.lower()
    
    def test_empty_expression(self):
        result = format_error("Empty expression")
        assert "expression" in result.lower() or "enter" in result.lower()
    
    def test_domain_error_complex(self):
        result = format_error("Domain error: Result is complex")
        assert "complex" in result.lower()
    
    def test_passthrough_unknown(self):
        result = format_error("Some random weird error")
        assert result  # Should not crash, should return something
