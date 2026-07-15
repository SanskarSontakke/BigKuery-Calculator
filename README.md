# BigKuery Calculator

A symbolic scientific calculator built with Python, SymPy, and PyQt6. It rearranges
and solves equations, evaluates expressions step by step, propagates variables across
a whiteboard of calculation cards, and renders results as formatted math.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

- **Symbolic Math Engine (SymPy)**:
  - Solves and rearranges equations (`2x + 5 = 15`, `x^2 - 4 = 0`), not just arithmetic.
  - Shows the work: step-by-step reduction from input to result.
  - **Configurable numeric precision**: set the number of significant digits in Settings
    (default 15, up to 100) for high-precision numeric answers.

- **Rich Expression Support**:
  - **Implicit Multiplication**: natural syntax like `2x`, `3(x+1)`, and `(x+1)(x-1)`.
  - **Scientific Functions**: trigonometric (sin, cos, tan, sec, csc, cot and inverses),
    hyperbolic (sinh, cosh, tanh, etc.), exponential & logarithmic (exp, log, ln, log10,
    log2), roots (sqrt, cbrt), and combinatorics (factorial, binomial, gamma).
  - **Calculus**: derivatives `diff(f, x)`, integrals `integrate(f, x)` /
    `integrate(f, (x, a, b))`, and limits `limit(f, x, a)`.
  - **Complex numbers** via `i` (e.g. `sqrt(-1) → i`, `(2+3i)(1-i) → 5 + i`).
  - **Systems of equations**: separate equations with `;` to solve them together,
    e.g. `x + y = 5; x - y = 1 → x = 3, y = 2`.
  - **Plotting**: a 📈 button appears on any card with exactly one undefined
    variable (e.g. `sin(x)`, or `a*x` once `a` is defined elsewhere) — click it to
    plot the function inline.

- **Beautiful math rendering**:
  - Results are typeset with **KaTeX** (proper radicals, fractions, integrals,
    Greek letters). KaTeX is bundled, so rendering works fully offline.
  - Falls back automatically to lightweight HTML labels if `PyQt6-WebEngine` is
    unavailable.

- **Display options**:
  - **DEG/RAD** angle modes and an **ENG** toggle for engineering notation
    (exponents in multiples of 3).
  - **Result format** in Settings: **Scroll** lets cards grow as wide as needed;
    **Wrap** caps card width and wraps long results onto multiple lines instead.
  - Press **F1** for an in-app function reference.

- **Persistent workspaces**:
  - Your cards are **saved automatically** and restored next time you open the app.
  - **Save/Open** a workspace to a `.bkw` file (`Ctrl+S` / `Ctrl+O`) to back up or share.

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
git clone https://github.com/SanskarSontakke/BigKuery-Calculator.git
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
| *(live)* | Results update automatically as you type |
| **Ctrl+S** | Save workspace to a file |
| **Ctrl+O** | Open a saved workspace |
| **F1** | Show the function reference |
| **Shift+Enter** | Insert a new line in the input |
| **Tab** | Switch the virtual keyboard sheet (0-9 / a-z / α-ω) |
| **Escape** | Clear the current input |
| **Ctrl+L** | Clear all cards in the active workspace |
| **Ctrl+,** | Open settings |
| **Ctrl+Shift+C** | Copy the workspace results |
| **Ctrl+Q** | Exit |

### Examples

```
2 + 3 * 4          → 14
sin(90)            → 1          (degrees mode, the default)
sqrt(2)            → 1.41421356...
10!                → 3628800
log(e^5)           → 5          (log is the natural logarithm)
2(x+1)             → 2x + 2     (implicit multiplication)
x^2 - 4 = 0        → x = -2, 2  (equation solving)
```

Define a variable in one card (`x = 10`) and reference it in another (`x^2 → 100`);
definitions propagate across all cards in the workspace automatically.

## Architecture

The application follows a modular architecture separating the core logic from the GUI.

### Core (`bigkuery/core`)

The calculation engine is built on **SymPy**:

1.  **Solver (`solver.py`)**:
    - Parses each expression with SymPy (`parse_expr`), applying transformations for
      implicit multiplication and `^`-as-power.
    - Substitutes known variable definitions, then either **solves** the equation
      (`sympy.solve`, with a numeric `nsolve` fallback) or **reduces** the expression
      step by step, recording each intermediate form.
    - Renders the input and every step to formatted math via `sympy_to_html`.
    - Evaluates numeric results to the configured precision (`sympy.N`).

2.  **Context (`context.py`)**:
    - `CalcContext` holds the user-facing settings the solver needs: angle mode
      (degrees/radians) and numeric display precision.

### GUI (`bigkuery/gui`)

Built with PyQt6, utilizing a clean separation of concerns:

- `MainWindow`: Orchestrates the application state.
- `InputWidget`: Custom `QTextEdit` with specific input handling.
- `OutputDisplay`: The whiteboard canvas of draggable equation cards.
- `MathView`: Renders LaTeX results via KaTeX in a `QWebEngineView` (with an
  automatic HTML-label fallback).
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
│   ├── core/           # Logic: SymPy solver
│   │   ├── solver.py          # Parse, substitute, solve/reduce, render
│   │   └── context.py         # CalcContext (angle mode, precision)
│   ├── gui/            # Interface: Windows, Widgets
│   └── __main__.py     # Entry point
├── tests/              # Unit tests
├── main.py             # Launcher script
└── pyproject.toml      # Config
```

## Troubleshooting

-   **"Parsing Error: ..."**: SymPy could not parse the expression. Check for unmatched
    parentheses, mistyped operators, or an incomplete expression.
-   **"No symbolic solution found"**: The equation has no closed-form solution for the
    chosen variable; a numeric solution is attempted as a fallback.
-   **`log` vs `log10`**: `log` is the natural logarithm (base *e*). Use `log10` or
    `log2` for base-10 / base-2.
-   **Complex Numbers**: Complex values are supported in expressions via `i`
    (e.g., `i^2 → -1`, `sqrt(-1) → i`).

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
