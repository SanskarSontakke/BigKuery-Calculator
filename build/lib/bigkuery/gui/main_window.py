"""
MainWindow - Main application window.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QDockWidget, QMenuBar, QMenu, QStatusBar,
    QMessageBox, QApplication, QSplitter, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QAction, QCloseEvent, QKeySequence

from .input_widget import InputWidget
from .output_display import OutputDisplay
from .button_panel import ButtonPanel
from .settings_dialog import SettingsDialog

from bigkuery.core import Evaluator, EvalContext


class MainWindow(QMainWindow):
    """
    Main application window for BigKuery Calculator.
    
    Contains the input widget, output display, button panel,
    and dockable history panel.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize evaluator
        self._context = EvalContext()
        self._evaluator = Evaluator(self._context)
        
        # Settings
        self._settings = QSettings("BigKuery", "Calculator")
        self._current_theme = "dark"
        
        # UI components (initialized in _setup_ui)
        self._input_widget = None
        self._output_display = None
        self._button_panel = None
        self._button_panel = None
        self._settings_dialog = None
        
        self._setup_ui()
        self._setup_menus()
        self._setup_status_bar()
        self._load_settings()
        self._apply_theme(self._current_theme)
        
        # Apply result format
        result_format = self._settings.value("result_format", "wrap", type=str)
        self._output_display.set_view_mode(result_format)
    
    def _setup_ui(self):
        """Set up the main window UI."""
        self.setWindowTitle("BigKuery Calculator")
        self.setMinimumSize(600, 500)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Output display (top)
        self._output_display = OutputDisplay()
        main_layout.addWidget(self._output_display)
        
        # Input widget
        self._input_widget = InputWidget()
        self._input_widget.evaluate_requested.connect(self.evaluate)
        main_layout.addWidget(self._input_widget)
        
        # Button panel
        self._button_panel = ButtonPanel()
        self._button_panel.button_clicked.connect(self._on_button_clicked)
        self._button_panel.function_clicked.connect(self._on_function_clicked)
        self._button_panel.constant_clicked.connect(self._on_constant_clicked)
        main_layout.addWidget(self._button_panel, stretch=1)
        
        # Settings dialog
        self._settings_dialog = SettingsDialog(self)
        self._settings_dialog.settings_changed.connect(self._on_settings_changed)
    
    def _setup_menus(self):
        """Set up the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        clear_action = QAction("&Clear", self)
        clear_action.setShortcut(QKeySequence("Ctrl+L"))
        clear_action.triggered.connect(self.clear)
        file_menu.addAction(clear_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        copy_action = QAction("&Copy Result", self)
        copy_action.setShortcut(QKeySequence("Ctrl+C"))
        copy_action.triggered.connect(self.copy_result)
        edit_menu.addAction(copy_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        settings_action = QAction("&Settings...", self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self.show_settings)
        view_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def _setup_status_bar(self):
        """Set up the status bar."""
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        
        # Permanent widgets
        self._mode_label = QLabel()
        self._mode_label.setStyleSheet("padding: 0 10px;")
        self._status_bar.addPermanentWidget(self._mode_label)
        
        self._precision_label = QLabel()
        self._precision_label.setStyleSheet("padding: 0 10px;")
        self._status_bar.addPermanentWidget(self._precision_label)
        
        self._settings_button = QPushButton("Settings")
        self._settings_button.clicked.connect(self.show_settings)
        self._settings_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 3px;
                padding: 2px 8px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self._status_bar.addPermanentWidget(self._settings_button)
        
        self._update_status()
    
    def _update_status(self):
        """Update the status bar."""
        mode = "RAD" if self._context.radians_mode else "DEG"
        # Convert bits to digits (approx)
        digits = int(self._context.precision / 3.32)
        
        self._mode_label.setText(f"Mode: {mode}")
        self._precision_label.setText(f"Precision: {digits} digits")
    
    def _apply_theme(self, theme: str):
        """Apply the specified theme."""
        self._current_theme = theme
        
        if theme == "dark":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1e1e1e;
                }
                QMenuBar {
                    background-color: #2d2d2d;
                    color: #d4d4d4;
                }
                QMenuBar::item:selected {
                    background-color: #3c3c3c;
                }
                QMenu {
                    background-color: #2d2d2d;
                    color: #d4d4d4;
                    border: 1px solid #3c3c3c;
                }
                QMenu::item:selected {
                    background-color: #094771;
                }
                QStatusBar {
                    background-color: #007acc;
                    color: white;
                }
                QDockWidget {
                    color: #d4d4d4;
                }
                QDockWidget::title {
                    background-color: #2d2d2d;
                    padding: 5px;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f3f3f3;
                }
                QMenuBar {
                    background-color: #e5e5e5;
                    color: #333333;
                }
                QMenuBar::item:selected {
                    background-color: #c5c5c5;
                }
                QMenu {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #c5c5c5;
                }
                QMenu::item:selected {
                    background-color: #0078d4;
                    color: white;
                }
                QStatusBar {
                    background-color: #0078d4;
                    color: white;
                }
            """)
    
    def _load_settings(self):
        """Load settings from storage."""
        self._context.precision = self._settings.value("precision", 256, type=int)
        self._context.radians_mode = self._settings.value("radians_mode", False, type=bool)  # Default to degrees
        self._current_theme = self._settings.value("theme", "dark", type=str)
        
        # Window geometry
        geometry = self._settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        state = self._settings.value("state")
        if state:
            self.restoreState(state)
        
        # Update settings dialog
        self._settings_dialog.set_settings({
            "precision": self._context.precision // 3,  # Convert bits to digits approx
            "radians_mode": self._context.radians_mode,
            "theme": self._current_theme,
            "result_format": self._settings.value("result_format", "wrap", type=str),
        })
        
        self._update_status()
    
    def _save_settings(self):
        """Save settings to storage."""
        self._settings.setValue("precision", self._context.precision)
        self._settings.setValue("radians_mode", self._context.radians_mode)
        self._settings.setValue("theme", self._current_theme)
        # result_format is updated dynamically, but we should make sure expected value is present.
        # However, _on_settings_changed handles the update. We need to save it back.
        # But wait, self._settings.value is how we read it.
        # Let's save the current format from settings or track it.
        # Simpler: just ensure we don't overwrite it here unless we track it.
        # Better: let's track it in a variable self._current_result_format
        # For now, let's assume _save_settings is called on close.
        # Note: self._settings object is persistent. We need to set 'result_format' when changed.
        # Optimization: Just let _on_settings_changed save it directly or update self._settings instantly.
        # Actually standard practice is updating QSettings immediately.
        
        self._settings.setValue("geometry", self.saveGeometry())
        self._settings.setValue("state", self.saveState())
    
    def evaluate(self):
        """Evaluate the current expression."""
        expr = self._input_widget.get_expression()
        if not expr:
            return
        
        result = self._evaluator.evaluate(expr)
        
        if result.is_error:
            self._output_display.set_result(result.error, is_error=True)
        else:
            # Calculate display digits from precision bits
            display_digits = max(15, self._context.precision // 4)
            result_str = result.to_string(display_digits)
            self._output_display.set_result(result_str)
    
    def clear(self):
        """Clear the input and output."""
        self._input_widget.clear_expression()
        self._output_display.clear_result()
    
    def copy_result(self):
        """Copy the current result to clipboard."""
        result = self._output_display.get_result()
        clipboard = QApplication.clipboard()
        clipboard.setText(result)
        self._status_bar.showMessage("Result copied to clipboard", 2000)
    
    def show_settings(self):
        """Show the settings dialog."""
        self._settings_dialog.exec()
    
    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About BigKuery Calculator",
            """<h2>BigKuery Calculator</h2>
            <p>Version 1.0.0</p>
            <p>An arbitrary precision scientific calculator with symbolic math support.</p>
            <p>Features:</p>
            <ul>
                <li>Arbitrary precision arithmetic</li>
                <li>Scientific functions (trig, log, etc.)</li>
                <li>Variable assignment</li>
            </ul>
            <p>&copy; 2024 BigKuery</p>
            """
        )
    
    def _on_button_clicked(self, text: str):
        """Handle button panel button clicks."""
        if text == "CLEAR":
            self.clear()
        elif text == "EVAL":
            self.evaluate()
        elif text == "BACKSPACE":
            cursor = self._input_widget.textCursor()
            cursor.deletePreviousChar()
        else:
            self._input_widget.insert_text(text)
    
    def _on_function_clicked(self, func_name: str):
        """Handle function button clicks."""
        self._input_widget.insert_text(f"{func_name}(")
    
    def _on_constant_clicked(self, constant: str):
        """Handle constant button clicks."""
        self._input_widget.insert_text(constant)
    
    def _on_settings_changed(self, settings: dict):
        """Handle settings changes."""
        if "precision" in settings:
            # Convert digits to bits (approx 3.32 bits per digit)
            self._context.precision = int(settings["precision"] * 3.32)
        
        if "radians_mode" in settings:
            self._context.radians_mode = settings["radians_mode"]
        
        if "theme" in settings:
            self._apply_theme(settings["theme"])
        
        if "result_format" in settings:
            self._output_display.set_view_mode(settings["result_format"])
            self._settings.setValue("result_format", settings["result_format"])
        
        self._update_status()
    
    def closeEvent(self, event: QCloseEvent):
        """Handle window close event."""
        self._save_settings()
        event.accept()
