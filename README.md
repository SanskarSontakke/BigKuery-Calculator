# BigKuery Calculator

An arbitrary precision scientific calculator built with Python and PyQt6.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

- **Arbitrary Precision Arithmetic** - Calculate with configurable precision (1-100 digits)
- **Scientific Functions** - 50+ mathematical functions including:
  - Trigonometric (sin, cos, tan, and inverses)
  - Hyperbolic (sinh, cosh, tanh, and inverses)
  - Exponential & Logarithmic (exp, log, ln, log10, log2)
  - Special functions (gamma, factorial, gcd, lcm)
- **Variables** - Assign and use variables (`x = 5`, `2*x + 1`)
- **Constants** - Built-in constants (π, e, φ, τ, γ, ∞)
- **Responsive UI** - Adapts to window size (tabs on small screens, combined layout on large)
- **User-Friendly Errors** - Clear, actionable error messages

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/BigKuery-Calculator.git
cd BigKuery-Calculator

# Install dependencies
pip install .

# Or install with development dependencies
pip install .[dev]
```

## Usage

```bash
# Run the calculator
python main.py
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Enter** | Evaluate expression |
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
```

## Project Structure

```
BigKuery-Calculator/
├── bigkuery/
│   ├── core/           # Core calculation engine
│   │   ├── big_float.py       # Arbitrary precision float
│   │   ├── big_rational.py    # Rational number support
│   │   ├── tokenizer.py       # Expression tokenizer
│   │   ├── parser.py          # Expression parser
│   │   ├── evaluator.py       # Expression evaluator
│   │   ├── math_functions.py  # Function registry
│   │   └── error_messages.py  # User-friendly errors
│   ├── gui/            # PyQt6 GUI components
│   │   ├── main_window.py     # Main application window
│   │   ├── button_panel.py    # Calculator buttons
│   │   ├── input_widget.py    # Expression input
│   │   ├── output_display.py  # Result display
│   │   └── settings_dialog.py # Settings dialog
│   └── __main__.py     # Application entry point
├── tests/              # Unit tests
├── main.py             # Alternative entry point
└── pyproject.toml      # Project configuration
```

## Development

```bash
# Install dev dependencies
pip install .[dev]

# Run tests
pytest tests/ -v

# Run the application
python main.py
```

## Settings

- **Precision**: Number of significant digits (default: 8)
- **Angle Mode**: Degrees or Radians for trigonometric functions
- **Result Format**: Scroll (one line) or Wrap (multiline)
- **Export/Import**: Backup and restore settings as JSON

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
