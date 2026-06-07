"""
InputWidget - Expression input field with syntax highlighting.
"""

from PyQt6.QtWidgets import QTextEdit, QSizePolicy
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QKeyEvent


class InputWidget(QTextEdit):
    """
    Multi-line expression input widget.
    
    Provides a text input field for mathematical expressions
    with support for multi-line input and Enter key handling.
    """
    
    # Signal emitted when user presses Enter (without Shift)
    evaluate_requested = pyqtSignal()
    # Signal emitted when Tab key is pressed
    tab_pressed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the input widget UI."""
        # Font
        font = QFont("Consolas", 14)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        # Size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumHeight(60)
        self.setMaximumHeight(120)
        
        # Placeholder
        self.setPlaceholderText("Enter expression (e.g., 2 + 2, sin(pi/2), x = 5)")
        
        # Tab behavior - handle Tab key customly
        self.setTabChangesFocus(False)
        
        # Style
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 2px solid #3c3c3c;
                border-radius: 8px;
                padding: 10px;
                selection-background-color: #264f78;
            }
            QTextEdit:focus {
                border-color: #007acc;
            }
        """)
    
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events."""
        # Enter without Shift triggers evaluation
        if event.key() == Qt.Key.Key_Return and not (
            event.modifiers() & Qt.KeyboardModifier.ShiftModifier
        ):
            self.evaluate_requested.emit()
            return
        
        # Tab switches functions tabs
        if event.key() == Qt.Key.Key_Tab:
            self.tab_pressed.emit()
            return
        
        # Shift+Enter for new line
        super().keyPressEvent(event)
    
    def get_expression(self) -> str:
        """Get the current expression text."""
        return self.toPlainText().strip()
    
    def set_expression(self, expr: str):
        """Set the expression text."""
        self.setPlainText(expr)
    
    def clear_expression(self):
        """Clear the expression."""
        self.clear()
    
    def insert_text(self, text: str):
        """Insert text at current cursor position."""
        self.insertPlainText(text)
