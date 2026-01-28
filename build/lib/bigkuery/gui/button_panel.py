"""
ButtonPanel - Calculator button grid.
"""

from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QPushButton, QHBoxLayout,
    QVBoxLayout, QSizePolicy, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont


class ButtonPanel(QWidget):
    """
    Calculator button panel with grouped button sets.
    
    Provides buttons for:
    - Basic operations (numbers, operators)
    - Scientific functions (trig, log, etc.)
    - Constants (pi, e, etc.)
    """
    
    # Signal emitted when a button is clicked
    button_clicked = pyqtSignal(str)
    function_clicked = pyqtSignal(str)
    constant_clicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the button panel UI."""
        # Main layout is horizontal to place groups side-by-side
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)
        
        # Scientific Group (Left)
        sci_group = self._create_scientific_group()
        main_layout.addWidget(sci_group, stretch=2)
        
        # Basic Group (Center/Right)
        basic_group = self._create_basic_group()
        main_layout.addWidget(basic_group, stretch=2)
        
        # Constants Group (Right)
        const_group = self._create_constants_group()
        main_layout.addWidget(const_group, stretch=1)

    def _create_button(self, text: str, callback, style: str = "default") -> QPushButton:
        """Create a styled button."""
        btn = QPushButton(text)
        btn.setMinimumSize(40, 40) # Smaller minimum size
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        font = QFont("Segoe UI", 11)
        btn.setFont(font)
        
        styles = {
            "default": """
                QPushButton {
                    background-color: #3c3c3c;
                    color: #d4d4d4;
                    border: 1px solid #4a4a4a;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
                QPushButton:pressed {
                    background-color: #2d2d2d;
                }
            """,
            "operator": """
                QPushButton {
                    background-color: #0e639c;
                    color: #ffffff;
                    border: 1px solid #1177bb;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #1177bb;
                }
                QPushButton:pressed {
                    background-color: #0d5a8c;
                }
            """,
            "function": """
                QPushButton {
                    background-color: #2d2d2d;
                    color: #dcdcaa;
                    border: 1px solid #3c3c3c;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #3c3c3c;
                }
                QPushButton:pressed {
                    background-color: #252526;
                }
            """,
            "constant": """
                QPushButton {
                    background-color: #2d2d2d;
                    color: #4ec9b0;
                    border: 1px solid #3c3c3c;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #3c3c3c;
                }
                QPushButton:pressed {
                    background-color: #252526;
                }
            """,
            "clear": """
                QPushButton {
                    background-color: #6e3030;
                    color: #ffffff;
                    border: 1px solid #8b3a3a;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #8b3a3a;
                }
                QPushButton:pressed {
                    background-color: #5a2626;
                }
            """,
        }
        
        btn.setStyleSheet(styles.get(style, styles["default"]))
        btn.clicked.connect(callback)
        
        return btn
    
    def _create_basic_group(self) -> QWidget:
        """Create the basic operations widget."""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # Button layout: 5 columns, 5 rows
        buttons = [
            ("C", 0, 0, "clear", lambda: self.button_clicked.emit("CLEAR")),
            ("(", 0, 1, "default", lambda: self.button_clicked.emit("(")),
            (")", 0, 2, "default", lambda: self.button_clicked.emit(")")),
            ("%", 0, 3, "operator", lambda: self.button_clicked.emit("%")),
            ("÷", 0, 4, "operator", lambda: self.button_clicked.emit("/")),
            
            ("7", 1, 0, "default", lambda: self.button_clicked.emit("7")),
            ("8", 1, 1, "default", lambda: self.button_clicked.emit("8")),
            ("9", 1, 2, "default", lambda: self.button_clicked.emit("9")),
            ("×", 1, 3, "operator", lambda: self.button_clicked.emit("*")),
            ("^", 1, 4, "operator", lambda: self.button_clicked.emit("^")),
            
            ("4", 2, 0, "default", lambda: self.button_clicked.emit("4")),
            ("5", 2, 1, "default", lambda: self.button_clicked.emit("5")),
            ("6", 2, 2, "default", lambda: self.button_clicked.emit("6")),
            ("−", 2, 3, "operator", lambda: self.button_clicked.emit("-")),
            ("!", 2, 4, "operator", lambda: self.button_clicked.emit("!")),
            
            ("1", 3, 0, "default", lambda: self.button_clicked.emit("1")),
            ("2", 3, 1, "default", lambda: self.button_clicked.emit("2")),
            ("3", 3, 2, "default", lambda: self.button_clicked.emit("3")),
            ("+", 3, 3, "operator", lambda: self.button_clicked.emit("+")),
            ("√", 3, 4, "function", lambda: self.function_clicked.emit("sqrt")),
            
            ("0", 4, 0, "default", lambda: self.button_clicked.emit("0")),
            (".", 4, 1, "default", lambda: self.button_clicked.emit(".")),
            (",", 4, 2, "default", lambda: self.button_clicked.emit(",")),
            ("=", 4, 3, "operator", lambda: self.button_clicked.emit("EVAL")),
            ("⌫", 4, 4, "clear", lambda: self.button_clicked.emit("BACKSPACE")),
        ]
        
        for text, row, col, style, callback in buttons:
            btn = self._create_button(text, callback, style)
            layout.addWidget(btn, row, col)
        
        return widget
    
    def _create_scientific_group(self) -> QWidget:
        """Create the scientific functions widget."""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        functions = [
            # Row 0: Trig
            ("sin", 0, 0), ("cos", 0, 1), ("tan", 0, 2),
            ("asin", 0, 3), ("acos", 0, 4), ("atan", 0, 5),
            
            # Row 1: Hyperbolic
            ("sinh", 1, 0), ("cosh", 1, 1), ("tanh", 1, 2),
            ("asinh", 1, 3), ("acosh", 1, 4), ("atanh", 1, 5),
            
            # Row 2: Exponential/Log
            ("exp", 2, 0), ("log", 2, 1), ("ln", 2, 2),
            ("log10", 2, 3), ("log2", 2, 4), ("pow", 2, 5),
            
            # Row 3: Root/Power
            ("sqrt", 3, 0), ("cbrt", 3, 1), ("abs", 3, 2),
            ("floor", 3, 3), ("ceil", 3, 4), ("round", 3, 5),
            
            # Row 4: Special
            ("gamma", 4, 0), ("factorial", 4, 1), ("gcd", 4, 2),
            ("lcm", 4, 3), ("min", 4, 4), ("max", 4, 5),
        ]
        
        for name, row, col in functions:
            btn = self._create_button(
                name, 
                lambda checked, n=name: self.function_clicked.emit(n),
                "function"
            )
            layout.addWidget(btn, row, col)
        
        return widget
    
    def _create_constants_group(self) -> QWidget:
        """Create the constants widget."""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        constants = [
            ("π", "pi", 0, 0), ("e", "e", 0, 1),
            ("φ", "phi", 1, 0), ("τ", "tau", 1, 1),
            ("∞", "inf", 2, 0), ("γ", "euler", 2, 1),
            
            ("ans", "ans", 3, 0), ("x", "x", 3, 1),
            ("y", "y", 4, 0), ("z", "z", 4, 1),
            
        ]
        
        for display, value, row, col in constants:
            btn = self._create_button(
                display,
                lambda checked, v=value: self.constant_clicked.emit(v),
                "constant"
            )
            layout.addWidget(btn, row, col)
        
        return widget
