"""
SettingsDialog - Calculator settings dialog.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QSpinBox, QComboBox, QCheckBox,
    QPushButton, QGroupBox
)
from PyQt6.QtCore import pyqtSignal


class SettingsDialog(QDialog):
    """
    Settings dialog for calculator configuration.
    
    Allows user to configure:
    - Precision (decimal places)
    - Angle mode (radians/degrees)
    - Theme
    """
    
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the settings dialog UI."""
        self.setWindowTitle("Settings")
        self.setMinimumWidth(350)
        
        layout = QVBoxLayout(self)
        
        # Calculation settings group
        calc_group = QGroupBox("Calculation")
        calc_layout = QFormLayout(calc_group)
        
        # Precision
        self._precision_spin = QSpinBox()
        self._precision_spin.setRange(10, 1000)
        self._precision_spin.setValue(50)
        self._precision_spin.setSuffix(" digits")
        calc_layout.addRow("Precision:", self._precision_spin)
        
        # Angle mode
        self._angle_mode = QComboBox()
        self._angle_mode.addItems(["Radians", "Degrees"])
        calc_layout.addRow("Angle Mode:", self._angle_mode)
        
        layout.addWidget(calc_group)
        
        # Display settings group
        display_group = QGroupBox("Display")
        display_layout = QFormLayout(display_group)
        
        # Theme
        self._theme = QComboBox()
        self._theme.addItems(["Dark", "Light"])
        display_layout.addRow("Theme:", self._theme)
        
        # Result Format
        self._result_format = QComboBox()
        self._result_format.addItems(["Multiline (Wrap)", "One Line (Scroll)"])
        display_layout.addRow("Result Format:", self._result_format)
        
        # Show history
        self._show_history = QCheckBox()
        self._show_history.setChecked(True)
        display_layout.addRow("Show History:", self._show_history)
        
        layout.addWidget(display_group)
        
        # Buttons
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.addWidget(cancel_btn)
        
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self._apply_settings)
        buttons.addWidget(apply_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self._ok_clicked)
        buttons.addWidget(ok_btn)
        
        layout.addLayout(buttons)
        
        # Style
        self.setStyleSheet("""
            QDialog {
                background-color: #252526;
            }
            QGroupBox {
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #d4d4d4;
            }
            QSpinBox, QComboBox {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 4px;
            }
            QCheckBox {
                color: #d4d4d4;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #0d5a8c;
            }
        """)
    
    def get_settings(self) -> dict:
        """Get current settings as a dictionary."""
        return {
            "precision": self._precision_spin.value(),
            "radians_mode": self._angle_mode.currentIndex() == 0,
            "theme": self._theme.currentText().lower(),
            "result_format": "wrap" if self._result_format.currentIndex() == 0 else "scroll",
            "show_history": self._show_history.isChecked(),
        }
    
    def set_settings(self, settings: dict):
        """Set settings from a dictionary."""
        if "precision" in settings:
            self._precision_spin.setValue(settings["precision"])
        if "radians_mode" in settings:
            self._angle_mode.setCurrentIndex(0 if settings["radians_mode"] else 1)
        if "theme" in settings:
            index = 0 if settings["theme"] == "dark" else 1
            self._theme.setCurrentIndex(index)
        if "result_format" in settings:
            index = 0 if settings["result_format"] == "wrap" else 1
            self._result_format.setCurrentIndex(index)
        if "show_history" in settings:
            self._show_history.setChecked(settings["show_history"])
    
    def _apply_settings(self):
        """Apply settings and emit signal."""
        self.settings_changed.emit(self.get_settings())
    
    def _ok_clicked(self):
        """Apply settings and close dialog."""
        self._apply_settings()
        self.accept()
