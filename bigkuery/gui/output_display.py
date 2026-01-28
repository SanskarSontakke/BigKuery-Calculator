"""
OutputDisplay - Result display widget with horizontal scrolling.
"""

from PyQt6.QtWidgets import QLabel, QSizePolicy, QFrame, QVBoxLayout, QScrollArea
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class OutputDisplay(QFrame):
    """
    Result display widget with horizontal scrolling.
    
    Shows the computed result left-aligned, allowing users to scroll
    right to see more digits for large numbers.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._result_text = "0"
    
    def _setup_ui(self):
        """Set up the output display UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Scroll area for horizontal scrolling
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        # Enable horizontal scroll, hide vertical
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Result label - left aligned, no wrap (single line scroll)
        self._label = QLabel("0")
        font = QFont("Consolas", 24)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self._label.setFont(font)
        self._label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self._label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse |
            Qt.TextInteractionFlag.TextSelectableByKeyboard
        )
        self._label.setWordWrap(False)  # No wrap - horizontal scroll instead
        
        self._scroll_area.setWidget(self._label)
        layout.addWidget(self._scroll_area)
        
        # Size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumHeight(80)
        self.setMaximumHeight(120)
        
        # Style
        self.setStyleSheet("""
            QFrame {
                background-color: #252526;
                border: 2px solid #3c3c3c;
                border-radius: 8px;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QLabel {
                color: #4ec9b0;
                background-color: transparent;
                padding: 5px;
            }
            QScrollBar:horizontal {
                height: 10px;
                background: #2d2d2d;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal {
                background: #4a4a4a;
                border-radius: 5px;
                min-width: 30px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #5a5a5a;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)

    def set_view_mode(self, mode: str):
        """
        Set the view mode.
        
        Args:
            mode: 'wrap' or 'scroll'
        """
        if mode == 'scroll':
            self._label.setWordWrap(False)
            self._label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        else:
            self._label.setWordWrap(True)
            self._label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def set_result(self, result: str, is_error: bool = False):
        """
        Set the displayed result.
        
        Args:
            result: The result text to display
            is_error: Whether this is an error message
        """
        self._result_text = result
        self._label.setText(result)
        
        if is_error:
            self._label.setStyleSheet("color: #f14c4c; background: transparent;")
        else:
            self._label.setStyleSheet("color: #4ec9b0; background: transparent;")
        
        # Reset scroll to left (show beginning of number)
        self._scroll_area.horizontalScrollBar().setValue(0)
    
    def get_result(self) -> str:
        """Get the current result text."""
        return self._result_text
    
    def clear_result(self):
        """Clear the result display."""
        self._result_text = "0"
        self._label.setText("0")
        self._label.setStyleSheet("color: #4ec9b0; background: transparent;")
        self._scroll_area.horizontalScrollBar().setValue(0)
