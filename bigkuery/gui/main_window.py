"""
MainWindow - Main application window.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QDockWidget, QMenuBar, QMenu, QStatusBar,
    QMessageBox, QApplication, QSplitter, QLabel, QPushButton,
    QDialog, QTextBrowser, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QAction, QCloseEvent, QKeySequence, QShortcut

from .input_widget import InputWidget
from .output_display import OutputDisplay
from .button_panel import ButtonPanel
from .settings_dialog import SettingsDialog

from bigkuery.core import Evaluator, EvalContext


class HelpDialog(QDialog):
    """Help dialog showing available functions and constants."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Function Reference")
        self.setMinimumSize(500, 400)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        browser.setHtml(self._get_help_content())
        layout.addWidget(browser)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)
        
        self.setStyleSheet("""
            QDialog { background-color: #252526; }
            QTextBrowser { 
                background-color: #1e1e1e; 
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 10px;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
        """)
    
    def _get_help_content(self) -> str:
        return """
        <h2 style="color:#4ec9b0;">BigKuery Calculator - Function Reference</h2>
        
        <h3 style="color:#dcdcaa;">Keyboard Shortcuts</h3>
        <table style="color:#d4d4d4;">
            <tr><td><b>Enter</b></td><td>Evaluate expression</td></tr>
            <tr><td><b>Ctrl+C</b></td><td>Copy result</td></tr>
            <tr><td><b>Ctrl+L</b></td><td>Clear input/output</td></tr>
            <tr><td><b>Ctrl+,</b></td><td>Open settings</td></tr>
            <tr><td><b>F1</b></td><td>Show this help</td></tr>
            <tr><td><b>Escape</b></td><td>Clear input</td></tr>
        </table>
        
        <h3 style="color:#dcdcaa;">Trigonometric Functions</h3>
        <p style="color:#d4d4d4;">
            <code>sin</code>, <code>cos</code>, <code>tan</code>, <code>cot</code>, <code>sec</code>, <code>csc</code><br>
            <code>asin</code>, <code>acos</code>, <code>atan</code>, <code>acot</code>, <code>asec</code>, <code>acsc</code>
        </p>
        
        <h3 style="color:#dcdcaa;">Hyperbolic Functions</h3>
        <p style="color:#d4d4d4;">
            <code>sinh</code>, <code>cosh</code>, <code>tanh</code>, <code>coth</code>, <code>sech</code>, <code>csch</code><br>
            <code>asinh</code>, <code>acosh</code>, <code>atanh</code>
        </p>
        
        <h3 style="color:#dcdcaa;">Exponential & Logarithmic</h3>
        <p style="color:#d4d4d4;">
            <code>exp(x)</code> - e^x<br>
            <code>log(x)</code>, <code>ln(x)</code> - natural log<br>
            <code>log10(x)</code> - base-10 log<br>
            <code>log2(x)</code> - base-2 log<br>
            <code>pow(x, y)</code> - x^y
        </p>
        
        <h3 style="color:#dcdcaa;">Roots & Powers</h3>
        <p style="color:#d4d4d4;">
            <code>sqrt(x)</code> - square root<br>
            <code>cbrt(x)</code> - cube root<br>
            <code>x^y</code> - power<br>
            <code>x!</code> - factorial
        </p>
        
        <h3 style="color:#dcdcaa;">Rounding</h3>
        <p style="color:#d4d4d4;">
            <code>floor</code>, <code>ceil</code>, <code>round</code>, <code>trunc</code>, <code>abs</code>
        </p>
        
        <h3 style="color:#dcdcaa;">Special Functions</h3>
        <p style="color:#d4d4d4;">
            <code>gamma(x)</code> - gamma function<br>
            <code>factorial(n)</code> - n!<br>
            <code>gcd(a, b)</code> - greatest common divisor<br>
            <code>lcm(a, b)</code> - least common multiple<br>
            <code>min(a, b)</code>, <code>max(a, b)</code><br>
            <code>clamp(x, min, max)</code>
        </p>
        
        <h3 style="color:#dcdcaa;">Constants</h3>
        <p style="color:#d4d4d4;">
            <code>pi</code> (π), <code>e</code>, <code>phi</code> (φ), <code>tau</code> (τ), <code>euler</code> (γ), <code>inf</code> (∞)
        </p>
        
        <h3 style="color:#dcdcaa;">Variables</h3>
        <p style="color:#d4d4d4;">
            Assign: <code>x = 5</code><br>
            Use: <code>2 * x + 1</code><br>
            <code>ans</code> - last result
        </p>
        
        <h3 style="color:#dcdcaa;">Examples</h3>
        <p style="color:#d4d4d4;">
            <code>2 + 3 * 4</code> → 14<br>
            <code>sin(pi/2)</code> → 1<br>
            <code>sqrt(2)</code> → 1.414...<br>
            <code>10!</code> → 3628800<br>
            <code>log(e^5)</code> → 5
        </p>
        """


class MainWindow(QMainWindow):
    """
    Main application window for BigKuery Calculator.
    
    Contains the input widget, output display, and button panel.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize evaluator
        self._context = EvalContext()
        self._evaluator = Evaluator(self._context)
        
        # Settings
        self._settings = QSettings("BigKuery", "Calculator")
        
        # UI components (initialized in _setup_ui)
        self._input_widget = None
        self._output_display = None
        self._button_panel = None
        self._settings_dialog = None
        self._help_dialog = None
        
        self._setup_ui()
        self._setup_menus()
        self._setup_shortcuts()
        self._setup_status_bar()
        self._load_settings()
        self._apply_theme()
        
        # Apply result format
        result_format = self._settings.value("result_format", "scroll", type=str)
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
        
        # Dialogs
        self._settings_dialog = SettingsDialog(self)
        self._settings_dialog.settings_changed.connect(self._on_settings_changed)
        self._help_dialog = HelpDialog(self)
    
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
        copy_action.setShortcut(QKeySequence("Ctrl+Shift+C"))
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
        
        help_action = QAction("&Function Reference", self)
        help_action.setShortcut(QKeySequence("F1"))
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def _setup_shortcuts(self):
        """Set up additional keyboard shortcuts."""
        # Escape to clear input
        escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        escape_shortcut.activated.connect(self._input_widget.clear_expression)
    
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
    
    def _apply_theme(self):
        """Apply the dark theme."""
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
    
    def _load_settings(self):
        """Load settings from storage."""
        # Precision stored in bits, default 27 bits (~8 digits)
        self._context.precision = self._settings.value("precision", 27, type=int)
        self._context.radians_mode = self._settings.value("radians_mode", False, type=bool)
        
        # Window geometry
        geometry = self._settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        state = self._settings.value("state")
        if state:
            self.restoreState(state)
        
        # Update settings dialog (convert bits to digits)
        digits = int(self._context.precision / 3.32)
        self._settings_dialog.set_settings({
            "precision": max(1, digits),
            "radians_mode": self._context.radians_mode,
            "result_format": self._settings.value("result_format", "scroll", type=str),
        })
        
        self._update_status()
    
    def _save_settings(self):
        """Save settings to storage."""
        self._settings.setValue("precision", self._context.precision)
        self._settings.setValue("radians_mode", self._context.radians_mode)
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
            display_digits = max(8, int(self._context.precision / 3.32))
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
    
    def show_help(self):
        """Show the help/function reference dialog."""
        self._help_dialog.exec()
    
    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About BigKuery Calculator",
            """<h2>BigKuery Calculator</h2>
            <p>Version 1.0.0</p>
            <p>An arbitrary precision scientific calculator.</p>
            <p>Features:</p>
            <ul>
                <li>Arbitrary precision arithmetic</li>
                <li>Scientific functions (trig, log, etc.)</li>
                <li>Variable assignment</li>
                <li>Responsive UI</li>
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
            self._settings.setValue("precision", self._context.precision)
        
        if "radians_mode" in settings:
            self._context.radians_mode = settings["radians_mode"]
            self._settings.setValue("radians_mode", self._context.radians_mode)
        
        if "result_format" in settings:
            self._output_display.set_view_mode(settings["result_format"])
            self._settings.setValue("result_format", settings["result_format"])
        
        self._update_status()
    
    def closeEvent(self, event: QCloseEvent):
        """Handle window close event."""
        self._save_settings()
        event.accept()
