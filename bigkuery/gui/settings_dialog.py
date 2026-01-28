"""
SettingsDialog - Calculator settings dialog.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QSpinBox, QComboBox, QPushButton, QGroupBox,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, QSettings
import json
import os


class SettingsDialog(QDialog):
    """
    Settings dialog for calculator configuration.
    
    Allows user to configure:
    - Precision (decimal digits)
    - Angle mode (radians/degrees)
    - Result format (wrap/scroll)
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
        
        # Precision (in digits, default 8)
        self._precision_spin = QSpinBox()
        self._precision_spin.setRange(1, 100)
        self._precision_spin.setValue(8)
        self._precision_spin.setSuffix(" digits")
        self._precision_spin.setToolTip("Number of significant digits for calculations")
        calc_layout.addRow("Precision:", self._precision_spin)
        
        # Angle mode
        self._angle_mode = QComboBox()
        self._angle_mode.addItems(["Degrees", "Radians"])
        self._angle_mode.setToolTip("Angle unit for trigonometric functions")
        calc_layout.addRow("Angle Mode:", self._angle_mode)
        
        layout.addWidget(calc_group)
        
        # Display settings group
        display_group = QGroupBox("Display")
        display_layout = QFormLayout(display_group)
        
        # Result Format
        self._result_format = QComboBox()
        self._result_format.addItems(["Scroll (One Line)", "Wrap (Multiline)"])
        self._result_format.setToolTip("How to display long results")
        display_layout.addRow("Result Format:", self._result_format)
        
        layout.addWidget(display_group)
        
        # Import/Export group
        io_group = QGroupBox("Settings Backup")
        io_layout = QHBoxLayout(io_group)
        
        export_btn = QPushButton("Export...")
        export_btn.clicked.connect(self._export_settings)
        io_layout.addWidget(export_btn)
        
        import_btn = QPushButton("Import...")
        import_btn.clicked.connect(self._import_settings)
        io_layout.addWidget(import_btn)
        
        layout.addWidget(io_group)
        
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
            "radians_mode": self._angle_mode.currentIndex() == 1,  # Radians is index 1
            "result_format": "scroll" if self._result_format.currentIndex() == 0 else "wrap",
        }
    
    def set_settings(self, settings: dict):
        """Set settings from a dictionary."""
        if "precision" in settings:
            self._precision_spin.setValue(settings["precision"])
        if "radians_mode" in settings:
            self._angle_mode.setCurrentIndex(1 if settings["radians_mode"] else 0)
        if "result_format" in settings:
            index = 0 if settings["result_format"] == "scroll" else 1
            self._result_format.setCurrentIndex(index)
    
    def _apply_settings(self):
        """Apply settings and emit signal."""
        self.settings_changed.emit(self.get_settings())
    
    def _ok_clicked(self):
        """Apply settings and close dialog."""
        self._apply_settings()
        self.accept()
    
    def _export_settings(self):
        """Export settings to a JSON file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Settings", "bigkuery_settings.json",
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.get_settings(), f, indent=2)
                QMessageBox.information(self, "Export", "Settings exported successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {e}")
    
    def _import_settings(self):
        """Import settings from a JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Settings", "",
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    settings = json.load(f)
                self.set_settings(settings)
                QMessageBox.information(self, "Import", "Settings imported. Click Apply to use them.")
            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to import: {e}")
