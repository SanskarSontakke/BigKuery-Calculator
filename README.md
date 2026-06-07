# BigKuery Calculator

An arbitrary precision scientific calculator built with Python and PyQt6. It provides a robust engine for mathematical expression evaluation, supporting extremely high precision calculations, symbolic variables, and a wide range of functions.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

- **Arbitrary Precision Arithmetic**:
  - Calculate with configurable precision (default ~50 digits, up to 100+).
  - Powered by `mpmath` for reliable high-precision floating-point operations.

- **Advanced Mathematical Engine**:
  - **Pratt Parser**: Handles operator precedence and associativity correctly.
  - **Implicit Multiplication**: Supports natural syntax like `2x`, `3(x+1)`, and `(x+1)(x-1)`.
  - **Scientific Functions**: Over 50 functions including:
    - Trigonometric (sin, cos, tan, sec, csc, cot and inverses)
    - Hyperbolic (sinh, cosh, tanh, etc.)
    - Exponential & Logarithmic (exp, log, ln, log10, log2)
    - Combinatorics (factorial, nCr, nPr, gamma)

- **Variables & Constants**:
  - Assign variables: `x = 5`, `result = 2*x + 10`
  - Use previous result: `ans + 5`
  - Built-in constants: `pi` (π), `e`, `phi` (φ), `tau` (τ), `euler` (γ), `inf` (∞)

- **Modern User Interface & Whiteboard Canvas**:
  - **Infinite Grid Canvas**: Calculation cards exist as independent widgets on a 2D whiteboard background.
  - **Draggable Cards & Viewport**: Click and drag individual cards to reposition them. Pan the view by clicking and dragging on the background grid.
  - **Manual Resizing**: Adjust card dimensions manually by clicking and dragging the visual resize grip (diagonal lines) in the bottom-right corner.
  - **Grow-Only Sizing**: Cards automatically scale up to fit longer expressions and evaluation steps, but never shrink unless cleared, ensuring contents are never cut off.

- **Global Variable Propagation & Bidirectional Solving**:
  - **Multi-Pass Solver**: Defining a variable in one card (e.g. `x = 2`) automatically updates and solves equations referencing `x` in all other cards in real-time.
  - **Bidirectional Evaluation**: Variable definitions propagate across cards regardless of creation order.
  - **Automatic Garbage Collection**: Deleting cards detaches widgets from the visual hierarchy and collects memory to ensure zero leakages.
  - **Keyboard Friendly**: Tab switches between virtual keyboard sheets, with custom DEG/RAD and scientific layouts.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/BigKuery-Calculator.git
cd BigKuery-Calculator

# Install dependencies
pip install .

# Or install with development dependencies (for testing)
pip install .[dev]
```

## Usage

To launch the calculator GUI:

```bash
python main.py
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Enter** | Evaluate expression |
| **Shift+Enter** | Insert new line |
| **Escape** | Clear input |
| **F1** | Show function reference |
| **Ctrl+L** | Clear input/output |
| **Ctrl+,** | Open settings |
| **Ctrl+Shift+C** | Copy result |
| **Ctrl+Q** | Exit |

### Examples

```
2 + 3 * 4          → 14
sin(pi/2)          → 1
sqrt(2)            → 1.41421356...
10!                → 3628800
log(e^5)           → 5
x = 10; x^2        → 100
2(x+1)             → 22  (Implicit multiplication)
```

## Architecture

The application follows a modular architecture separating the core logic from the GUI.

### Core (`bigkuery/core`)

The calculation engine processes expressions in three stages:

1.  **Tokenizer (`tokenizer.py`)**:
    - Converts the input string into a stream of `Token` objects.
    - Handles implicit multiplication detection (e.g., inserting `*` in `2x`).
    - Recognizes numbers, identifiers, operators, and Unicode symbols.

2.  **Parser (`parser.py`)**:
    - Takes the token stream and builds an **Abstract Syntax Tree (AST)**.
    - Uses a **Pratt Parser** (Top-Down Operator Precedence) to handle complex precedence rules (e.g., `*` before `+`, `^` is right-associative).
    - Generates nodes like `BinaryOpNode`, `FunctionCallNode`, `AssignmentNode`, etc.

3.  **Evaluator (`evaluator.py`)**:
    - Traverses the AST recursively to compute the result.
    - Uses `BigFloat` (wrapper around `mpmath.mpf`) for all numeric calculations to maintain high precision.
    - Manages the `EvalContext`, which stores variables and settings (precision, angle mode).

### GUI (`bigkuery/gui`)

Built with PyQt6, utilizing a clean separation of concerns:

- `MainWindow`: Orchestrates the application state.
- `InputWidget`: Custom `QTextEdit` with specific input handling.
- `OutputDisplay`: Renders results and errors.
- `ButtonPanel`: Provides a clickable interface for common functions.

## Development & Testing

### Running Tests

The project uses `pytest` for testing. To run the test suite:

```bash
# Install test dependencies
pip install .[dev]

# Run all tests
pytest tests/ -v
```

### Project Structure

```
BigKuery-Calculator/
├── bigkuery/
│   ├── core/           # Logic: Tokenizer, Parser, Evaluator
│   │   ├── big_float.py       # Arbitrary precision float wrapper
│   │   ├── tokenizer.py       # Lexical analysis
│   │   ├── parser.py          # AST generation
│   │   ├── evaluator.py       # AST evaluation
│   │   └── ...
│   ├── gui/            # Interface: Windows, Widgets
│   └── __main__.py     # Entry point
├── tests/              # Unit tests
├── main.py             # Launcher script
└── pyproject.toml      # Config
```

## Troubleshooting

-   **"Unknown function 'x' requires 2 arguments"**: You might be using a binary function like `pow` with only one argument. Check the help (F1) for signatures.
-   **"Parse error: Unexpected token"**: Check for unmatched parentheses or mistyped operators.
-   **"Cannot assign to constant"**: You tried to assign a value to `pi` or `e`. Use a different variable name.
-   **Complex Numbers**: Currently, the calculator supports real numbers only. Operations resulting in complex numbers (like `sqrt(-1)`) will raise a domain error.

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
