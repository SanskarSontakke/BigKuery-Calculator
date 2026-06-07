"""
ButtonPanel - Multi-sheet virtual keyboard matching the screenshots.
"""

from PyQt6.QtWidgets import (
    QWidget, QGridLayout, QPushButton, QHBoxLayout,
    QVBoxLayout, QSizePolicy, QStackedWidget
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont


class ButtonPanel(QWidget):
    """
    Calculator keyboard panel supporting three layout sheets:
    1. Math & Numbers (Main)
    2. Greek Alphabet
    3. QWERTY Alphabet
    Allows switching sheets via tab buttons or the 'Tab' key.
    """
    
    button_clicked = pyqtSignal(str)
    function_clicked = pyqtSignal(str)
    constant_clicked = pyqtSignal(str)
    workspace_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._buttons = []
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up keyboard panel layout."""
        self._main_layout = QVBoxLayout(self)
        self._main_layout.setContentsMargins(0, 0, 0, 0)
        self._main_layout.setSpacing(6)
        
        # 1. Top sheet selector bar
        selector_layout = QHBoxLayout()
        selector_layout.setContentsMargins(10, 2, 10, 2)
        
        # Left sheet tabs: 1, 2, 3 (Workspace Selectors)
        self._left_tabs = []
        for i, text in enumerate(["1", "2", "3"]):
            btn = QPushButton(text)
            btn.setFixedSize(26, 26)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.clicked.connect(lambda checked, idx=i: self.workspace_changed.emit(idx))
            self._left_tabs.append(btn)
            selector_layout.addWidget(btn)
            
        selector_layout.addStretch()
        
        # Right sheet labels: 0-9, a-z, α-ω
        self._right_tabs = []
        right_labels = ["0-9", "a-z", "α-ω"]
        for i, text in enumerate(right_labels):
            btn = QPushButton(text)
            btn.setFixedHeight(26)
            btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            btn.clicked.connect(lambda checked, idx=i: self.set_sheet_index(idx))
            self._right_tabs.append(btn)
            selector_layout.addWidget(btn)
            
        self._main_layout.addLayout(selector_layout)
        
        # 2. Stacked widget for the keyboard sheets
        self._stack = QStackedWidget()
        self._main_layout.addWidget(self._stack)
        
        # Create sheets
        self._sheet_math = self._create_math_sheet()
        self._sheet_greek = self._create_greek_sheet()
        self._sheet_alpha = self._create_alpha_sheet()
        
        self._stack.addWidget(self._sheet_math)
        self._stack.addWidget(self._sheet_alpha)  # index 1 maps to a-z
        self._stack.addWidget(self._sheet_greek)  # index 2 maps to α-ω
        
        # Set active sheet and update tab highlights
        self.set_sheet_index(0)
        
    def set_sheet_index(self, index: int):
        """Set the active keyboard sheet index."""
        self._stack.setCurrentIndex(index)
        self._update_tab_highlights()
        
    def switch_to_next_tab(self):
        """Switch to the next keyboard sheet."""
        next_idx = (self._stack.currentIndex() + 1) % self._stack.count()
        self.set_sheet_index(next_idx)
        
    def _update_tab_highlights(self):
        """Update styling of top tab selectors to indicate active sheet."""
        idx = self._stack.currentIndex()
        
        # Right tabs (0-9, a-z, α-ω) highlights
        # Mapping: idx 0 -> 0-9, idx 1 -> a-z, idx 2 -> α-ω
        for i, btn in enumerate(self._right_tabs):
            if i == idx:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1e1e1e;
                        color: #58a6ff;
                        border: 2px solid #58a6ff;
                        font-weight: bold;
                        border-radius: 4px;
                        padding: 2px 6px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1e1e1e;
                        color: #888888;
                        border: 1px solid #444444;
                        border-radius: 4px;
                        padding: 2px 6px;
                    }
                """)

    def set_active_workspace_highlight(self, idx: int):
        """Update styling of top left workspace selectors to show active workspace."""
        for i, btn in enumerate(self._left_tabs):
            if i == idx:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1e1e1e;
                        color: #58a6ff;
                        border: 2px solid #58a6ff;
                        font-weight: bold;
                        border-radius: 2px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #1e1e1e;
                        color: #888888;
                        border: 1px solid #444444;
                        border-radius: 2px;
                    }
                """)

    def _create_button(self, text: str, callback, style: str = "default") -> QPushButton:
        """Create a styled keyboard key."""
        btn = QPushButton(text)
        btn.setMinimumSize(35, 35)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        font = QFont("Segoe UI", 11)
        btn.setFont(font)
        self._buttons.append(btn)
        
        styles = {
            "default": """
                QPushButton {
                    background-color: #2d2d2d;
                    color: #d4d4d4;
                    border: 1px solid #3c3c3c;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #3e3e3e;
                }
                QPushButton:pressed {
                    background-color: #1e1e1e;
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
                    background-color: #1a2d3d;
                    color: #4fc9b0;
                    border: 1px solid #203a4f;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #203a4f;
                }
                QPushButton:pressed {
                    background-color: #101e2b;
                }
            """,
            "constant": """
                QPushButton {
                    background-color: #252d24;
                    color: #dcdcaa;
                    border: 1px solid #2f3b2d;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #2f3b2d;
                }
                QPushButton:pressed {
                    background-color: #171d16;
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
            "equal": """
                QPushButton {
                    background-color: #2ea44f;
                    color: #ffffff;
                    border: 1px solid #2c974b;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #34d058;
                }
                QPushButton:pressed {
                    background-color: #24883d;
                }
            """,
        }
        
        btn.setStyleSheet(styles.get(style, styles["default"]))
        btn.clicked.connect(callback)
        return btn

    def _create_math_sheet(self) -> QWidget:
        """Create Sheet 1: Math and Numbers keyboard grid."""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(4)
        
        # Left functions (Col 0 to Col 4) and Right numbers (Col 5 to Col 9)
        keys = [
            # Row 0
            ("π", 0, 0, "constant", lambda: self.constant_clicked.emit("pi")),
            ("e", 0, 1, "constant", lambda: self.constant_clicked.emit("e")),
            ("°", 0, 2, "constant", lambda: self.button_clicked.emit("°")),
            ("n!", 0, 3, "function", lambda: self.button_clicked.emit("!")),
            ("ans", 0, 4, "constant", lambda: self.constant_clicked.emit("ans")),
            ("7", 0, 5, "default", lambda: self.button_clicked.emit("7")),
            ("8", 0, 6, "default", lambda: self.button_clicked.emit("8")),
            ("9", 0, 7, "default", lambda: self.button_clicked.emit("9")),
            ("÷", 0, 8, "operator", lambda: self.button_clicked.emit("÷")),
            ("(", 0, 9, "operator", lambda: self.button_clicked.emit("(")),
            
            # Row 1
            ("sin", 1, 0, "function", lambda: self.function_clicked.emit("sin")),
            ("|x|", 1, 1, "function", lambda: self.function_clicked.emit("abs")),
            ("x^n", 1, 2, "function", lambda: self.button_clicked.emit("^")),
            ("arcsin", 1, 3, "function", lambda: self.function_clicked.emit("asin")),
            ("x", 1, 4, "constant", lambda: self.constant_clicked.emit("x")),
            ("4", 1, 5, "default", lambda: self.button_clicked.emit("4")),
            ("5", 1, 6, "default", lambda: self.button_clicked.emit("5")),
            ("6", 1, 7, "default", lambda: self.button_clicked.emit("6")),
            ("×", 1, 8, "operator", lambda: self.button_clicked.emit("×")),
            (")", 1, 9, "operator", lambda: self.button_clicked.emit(")")),
            
            # Row 2
            ("cos", 2, 0, "function", lambda: self.function_clicked.emit("cos")),
            ("y", 2, 1, "constant", lambda: self.constant_clicked.emit("y")),
            ("√", 2, 2, "operator", lambda: self.function_clicked.emit("sqrt")),
            ("arccos", 2, 3, "function", lambda: self.function_clicked.emit("acos")),
            ("z", 2, 4, "constant", lambda: self.constant_clicked.emit("z")),
            ("1", 2, 5, "default", lambda: self.button_clicked.emit("1")),
            ("2", 2, 6, "default", lambda: self.button_clicked.emit("2")),
            ("3", 2, 7, "default", lambda: self.button_clicked.emit("3")),
            ("−", 2, 8, "operator", lambda: self.button_clicked.emit("−")),
            ("=", 2, 9, "equal", lambda: self.button_clicked.emit("=")),
            
            # Row 3
            ("tan", 3, 0, "function", lambda: self.function_clicked.emit("tan")),
            ("i", 3, 1, "constant", lambda: self.constant_clicked.emit("i")),
            ("ln", 3, 2, "function", lambda: self.function_clicked.emit("ln")),
            ("arctan", 3, 3, "function", lambda: self.function_clicked.emit("atan")),
            ("log", 3, 4, "function", lambda: self.function_clicked.emit("log")),
            ("0", 3, 5, "default", lambda: self.button_clicked.emit("0")),
            (".", 3, 6, "default", lambda: self.button_clicked.emit(".")),
            (",", 3, 7, "default", lambda: self.button_clicked.emit(",")),
            ("+", 3, 8, "operator", lambda: self.button_clicked.emit("+")),
            ("⌫", 3, 9, "clear", lambda: self.button_clicked.emit("BACKSPACE")),
        ]
        
        for text, row, col, style, callback in keys:
            btn = self._create_button(text, callback, style)
            layout.addWidget(btn, row, col)
            
        return widget

    def _create_greek_sheet(self) -> QWidget:
        """Create Sheet 3: Greek alphabet keyboard grid."""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(4)
        
        greek_letters = [
            # Row 0
            ("α", 0, 0), ("β", 0, 1), ("γ", 0, 2), ("δ", 0, 3), ("ε", 0, 4), ("ζ", 0, 5), ("η", 0, 6), ("θ", 0, 7), ("ι", 0, 8),
            # Row 1
            ("κ", 1, 0), ("λ", 1, 1), ("μ", 1, 2), ("ν", 1, 3), ("ξ", 1, 4), ("ο", 1, 5), ("π", 1, 6), ("ρ", 1, 7), ("σ", 1, 8),
            # Row 2
            ("τ", 2, 0), ("υ", 2, 1), ("φ", 2, 2), ("χ", 2, 3), ("ψ", 2, 4), ("ω", 2, 5), ("(", 2, 6), (")", 2, 7), (",", 2, 8),
        ]
        
        for letter, row, col in greek_letters:
            btn = self._create_button(
                letter, 
                lambda checked, char=letter: self.constant_clicked.emit(char), 
                "default"
            )
            layout.addWidget(btn, row, col)
            
        # Row 3 controls
        layout.addWidget(self._create_button("0-9", lambda: self.set_sheet_index(0), "function"), 3, 0, 1, 2)
        
        space_btn = self._create_button("Space", lambda: self.button_clicked.emit(" "), "default")
        layout.addWidget(space_btn, 3, 2, 1, 3)
        
        left_arrow = self._create_button("←", lambda: self.button_clicked.emit("LEFT"), "operator")
        layout.addWidget(left_arrow, 3, 5)
        
        right_arrow = self._create_button("→", lambda: self.button_clicked.emit("RIGHT"), "operator")
        layout.addWidget(right_arrow, 3, 6)
        
        eval_btn = self._create_button("=", lambda: self.button_clicked.emit("="), "equal")
        layout.addWidget(eval_btn, 3, 7)
        
        backspace_btn = self._create_button("⌫", lambda: self.button_clicked.emit("BACKSPACE"), "clear")
        layout.addWidget(backspace_btn, 3, 8)
        
        return widget

    def _create_alpha_sheet(self) -> QWidget:
        """Create Sheet 2: QWERTY alphabetical keyboard grid."""
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(4)
        
        qwerty = [
            # Row 0
            ("q", 0, 0), ("w", 0, 1), ("e", 0, 2), ("r", 0, 3), ("t", 0, 4), ("y", 0, 5), ("u", 0, 6), ("i", 0, 7), ("o", 0, 8), ("p", 0, 9),
            # Row 1
            ("a", 1, 0), ("s", 1, 1), ("d", 1, 2), ("f", 1, 3), ("g", 1, 4), ("h", 1, 5), ("j", 1, 6), ("k", 1, 7), ("l", 1, 8), ("(", 1, 9),
            # Row 2
            ("z", 2, 0), ("x", 2, 1), ("c", 2, 2), ("v", 2, 3), ("b", 2, 4), ("n", 2, 5), ("m", 2, 6), (")", 2, 7), (",", 2, 8), ("=", 2, 9),
        ]
        
        for char, row, col in qwerty:
            style = "equal" if char == "=" else "default"
            btn = self._create_button(
                char, 
                lambda checked, val=char: self.constant_clicked.emit(val) if val not in "()=" else self.button_clicked.emit(val), 
                style
            )
            layout.addWidget(btn, row, col)
            
        # Row 3 controls
        layout.addWidget(self._create_button("α-ω", lambda: self.set_sheet_index(2), "function"), 3, 0, 1, 2)
        
        space_btn = self._create_button("Space", lambda: self.button_clicked.emit(" "), "default")
        layout.addWidget(space_btn, 3, 2, 1, 4)
        
        left_arrow = self._create_button("←", lambda: self.button_clicked.emit("LEFT"), "operator")
        layout.addWidget(left_arrow, 3, 6)
        
        right_arrow = self._create_button("→", lambda: self.button_clicked.emit("RIGHT"), "operator")
        layout.addWidget(right_arrow, 3, 7)
        
        eval_btn = self._create_button("=", lambda: self.button_clicked.emit("="), "equal")
        layout.addWidget(eval_btn, 3, 8)
        
        backspace_btn = self._create_button("⌫", lambda: self.button_clicked.emit("BACKSPACE"), "clear")
        layout.addWidget(backspace_btn, 3, 9)
        
        return widget

    def resizeEvent(self, event):
        """Handle scaling of buttons dynamically based on layout space."""
        super().resizeEvent(event)
        width = event.size().width()
        height = event.size().height()
        
        # Calculate dynamic base size
        base_size = 11
        scale_w = width / 900.0
        scale_h = height / 300.0
        scale = min(scale_w, scale_h)
        font_size = max(10, min(18, int(base_size * scale)))
        
        for btn in self._buttons:
            font = btn.font()
            # Digits, operators, arrows and backspace should stand out
            if len(btn.text()) == 1 or btn.text() in ("ans", "Space", "0-9", "a-z", "α-ω"):
                font.setPointSize(font_size + 2)
                font.setBold(True)
            else:
                font.setPointSize(font_size)
                font.setBold(False)
            btn.setFont(font)
