
import pytest
from bigkuery.core.parser import Parser, NodeType, ParseError

def test_number_parsing():
    parser = Parser("123.456")
    node = parser.parse()
    assert node.node_type() == NodeType.NUMBER
    assert node.value == "123.456"

def test_basic_arithmetic_parsing():
    parser = Parser("1 + 2 * 3")
    node = parser.parse()
    assert node.node_type() == NodeType.BINARY_OP
    assert node.op == "+"
    assert node.right.node_type() == NodeType.BINARY_OP
    assert node.right.op == "*"

def test_parentheses():
    parser = Parser("(1 + 2) * 3")
    node = parser.parse()
    assert node.node_type() == NodeType.BINARY_OP
    assert node.op == "*"
    assert node.left.node_type() == NodeType.BINARY_OP
    assert node.left.op == "+"

def test_implicit_multiplication():
    # 2x -> 2 * x
    parser = Parser("2x")
    node = parser.parse()
    assert node.node_type() == NodeType.BINARY_OP
    assert node.op == "*"
    assert node.left.value == "2"
    assert node.right.name == "x"

def test_function_call():
    parser = Parser("sin(x)")
    node = parser.parse()
    assert node.node_type() == NodeType.FUNCTION_CALL
    assert node.name == "sin"
    assert len(node.arguments) == 1

def test_error_handling():
    with pytest.raises(ParseError):
        Parser("1 +").parse()
