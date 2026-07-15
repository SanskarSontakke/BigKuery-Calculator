"""
MainWindow - Main application window.
"""

import json

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QMessageBox, QApplication, QLabel, QPushButton, QFileDialog
)
from PyQt6.QtCore import Qt, QSettings, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QCloseEvent, QKeySequence, QShortcut

from .input_widget import InputWidget
from .output_display import OutputDisplay, EquationBlock
from .button_panel import ButtonPanel
from .settings_dialog import SettingsDialog
from .math_view import KATEX_AVAILABLE
from bigkuery.core.solver import solve_workspace_equation, solve_workspace_expression_steps
from bigkuery.core import CalcContext
from bigkuery.core.plotting import PLOT_AVAILABLE, free_symbol_for_plot


class BlockData:
    """Represents the data of a single equation block on the canvas."""
    def __init__(self, expression="", x=20, y=20):
        self.expression = expression
        self.x = x
        self.y = y
        self.widget = None
        self.is_custom_positioned = False


class Workspace:
    """Represents an independent calculation workspace with multiple equations."""
    def __init__(self):
        self.blocks = []  # list of BlockData objects
        self.current_index = 0


class MainWindow(QMainWindow):
    """
    Main application window for BigKuery Calculator.
    
    Contains the mobile-inspired desktop header, input widget, 
    graph-grid output display canvas, and responsive virtual keyboard.
    Supports 3 independent workspaces and cumulative equation solving.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Calculator state (angle mode + display precision)
        self._context = CalcContext()
        self._eng_mode = False
        
        # Initialize 3 independent workspaces
        self._workspaces = [Workspace(), Workspace(), Workspace()]
        self._current_workspace_idx = 0
        
        # Settings
        self._settings = QSettings("BigKuery", "Calculator")

        # Debounce timer: coalesce rapid edits (typing, dragging) into a single
        # solve after a short idle, so we don't re-run SymPy on every keystroke.
        self._eval_timer = QTimer(self)
        self._eval_timer.setSingleShot(True)
        self._eval_timer.setInterval(180)
        self._eval_timer.timeout.connect(self.evaluate)

        # UI components
        self._input_widget = None
        self._output_display = None
        self._button_panel = None
        self._settings_dialog = None
        
        self._setup_ui()
        
        # Setup initial blocks for the workspaces
        for ws in self._workspaces:
            self._create_block_for_workspace(ws, "", 20, 20)
            
        self._setup_menus()
        self._setup_shortcuts()
        self._load_settings()
        self._apply_theme()
        
        # Update highlights on start
        self._button_panel.set_active_workspace_highlight(self._current_workspace_idx)
        self._update_active_block_highlight()

        # Restore cards from the previous session, if any (persists across runs)
        self._restore_saved_workspaces()
        
    def _create_block_for_workspace(self, workspace, expression, x, y):
        """Create a block widget and its associated data container."""
        idx = len(workspace.blocks)
        
        # Widget parent is the canvas widget inside OutputDisplay
        widget = EquationBlock(idx, expression, self._output_display.canvas)
        widget.move(x, y)
        
        # Connect signals
        widget.expression_changed.connect(self._on_block_expression_changed)
        widget.position_changed.connect(self._on_block_position_changed)
        widget.clicked.connect(self._on_block_clicked)
        widget.deleted.connect(self._on_block_deleted)
        
        block_data = BlockData(expression, x, y)
        block_data.widget = widget
        workspace.blocks.append(block_data)
        
        # Set visibility based on active workspace state
        if workspace != self._workspaces[self._current_workspace_idx]:
            widget.hide()
        else:
            widget.show()
            
        return block_data
        
    def _setup_ui(self):
        """Set up the main window layout."""
        self.setWindowTitle("BigKuery Calculator")
        self.setMinimumSize(850, 650)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        
        # 1. Custom Mobile-to-Desktop Header Bar
        header_widget = QWidget()
        header_widget.setObjectName("HeaderWidget")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 4, 10, 4)
        
        menu_btn = QPushButton("≡")
        menu_btn.setFixedSize(30, 30)
        menu_btn.setObjectName("HeaderIconBtn")
        menu_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        menu_btn.clicked.connect(self.show_about)
        header_layout.addWidget(menu_btn)
        
        title_label = QLabel("Calculator")
        title_label.setObjectName("HeaderTitle")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Clickable DEG/RAD Toggle
        self._deg_btn = QPushButton("DEG")
        self._deg_btn.setFixedSize(50, 30)
        self._deg_btn.setObjectName("HeaderToggleBtn")
        self._deg_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._deg_btn.clicked.connect(self._toggle_angle_mode)
        header_layout.addWidget(self._deg_btn)
        
        # Clickable ENG mode Toggle
        self._eng_btn = QPushButton("ENG")
        self._eng_btn.setFixedSize(50, 30)
        self._eng_btn.setObjectName("HeaderToggleBtn")
        self._eng_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._eng_btn.clicked.connect(self._toggle_eng_mode)
        header_layout.addWidget(self._eng_btn)
        
        more_btn = QPushButton("⋮")
        more_btn.setFixedSize(30, 30)
        more_btn.setObjectName("HeaderIconBtn")
        more_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        more_btn.clicked.connect(self.show_settings)
        header_layout.addWidget(more_btn)
        
        main_layout.addWidget(header_widget)
        
        # 2. Input Box layout (Expression Input + Red Clear Button)
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(6)
        
        self._input_widget = InputWidget()
        self._input_widget.textChanged.connect(self._schedule_evaluate)  # debounced live eval
        input_layout.addWidget(self._input_widget, stretch=1)
        
        clear_btn = QPushButton("C")
        clear_btn.setFixedSize(45, 45)
        clear_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #6e3030;
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                border: 1px solid #8b3a3a;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #8b3a3a;
            }
            QPushButton:pressed {
                background-color: #5a2626;
            }
        """)
        clear_btn.clicked.connect(self.clear)
        input_layout.addWidget(clear_btn)
        
        main_layout.addWidget(input_container)
        
        # 3. Output display (infinite grid canvas)
        self._output_display = OutputDisplay()
        main_layout.addWidget(self._output_display, stretch=3)
        
        # Floating Action Button (+) overlaying the display to add new equation
        self._plus_btn = QPushButton("+", self._output_display)
        self._plus_btn.setFixedSize(50, 50)
        self._plus_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._plus_btn.setStyleSheet("""
            QPushButton {
                background-color: #0b6285;
                color: white;
                font-size: 24px;
                font-weight: bold;
                border-radius: 25px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0e7fa8;
            }
            QPushButton:pressed {
                background-color: #084964;
            }
        """)
        self._plus_btn.clicked.connect(self.add_new_equation)
        
        # 4. Multi-sheet Virtual Keyboard
        self._button_panel = ButtonPanel()
        self._button_panel.button_clicked.connect(self._on_button_clicked)
        self._button_panel.function_clicked.connect(self._on_function_clicked)
        self._button_panel.constant_clicked.connect(self._on_constant_clicked)
        self._button_panel.workspace_changed.connect(self.switch_workspace)
        main_layout.addWidget(self._button_panel, stretch=2)
        
        # Connect keyboard tab switching to the input widget
        self._input_widget.tab_pressed.connect(self._button_panel.switch_to_next_tab)
        
        # Settings Dialog
        self._settings_dialog = SettingsDialog(self)
        self._settings_dialog.settings_changed.connect(self._on_settings_changed)
        
    def _setup_menus(self):
        """Set up standard desktop menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")

        save_action = QAction("&Save Workspace...", self)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        save_action.triggered.connect(self.save_workspace_to_file)
        file_menu.addAction(save_action)

        open_action = QAction("&Open Workspace...", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self.open_workspace_from_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        clear_action = QAction("&Clear All", self)
        clear_action.setShortcut(QKeySequence("Ctrl+L"))
        clear_action.triggered.connect(self.clear_all)
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
        
    def _setup_shortcuts(self):
        """Set up helper keyboard shortcuts."""
        escape_shortcut = QShortcut(QKeySequence("Escape"), self)
        escape_shortcut.activated.connect(self._input_widget.clear_expression)

        f1_shortcut = QShortcut(QKeySequence("F1"), self)
        f1_shortcut.activated.connect(self.show_function_reference)
        
    def _toggle_angle_mode(self):
        """Toggle between DEG and RAD modes."""
        self._context.radians_mode = not self._context.radians_mode
        self._deg_btn.setText("RAD" if self._context.radians_mode else "DEG")
        self.evaluate()
            
    def _toggle_eng_mode(self):
        """Toggle engineering mode highlighting."""
        self._eng_mode = not self._eng_mode
        self._eng_btn.setStyleSheet(
            "background-color: #0e639c; font-weight: bold; border-radius: 4px;" if self._eng_mode 
            else "background-color: #3c3c3c; border-radius: 4px;"
        )
        self.evaluate()

    def _apply_theme(self):
        """Apply a dark theme styled like the mobile reference screens."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #16191f;
            }
            #HeaderWidget {
                background-color: #20242c;
                border-radius: 6px;
                border: 1px solid #2d3139;
            }
            #HeaderTitle {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                padding-left: 5px;
            }
            #HeaderIconBtn {
                background-color: transparent;
                color: #d4d4d4;
                border: none;
                font-size: 18px;
            }
            #HeaderIconBtn:hover {
                background-color: #2d3139;
                border-radius: 4px;
            }
            #HeaderToggleBtn {
                background-color: #2d3139;
                color: #d4d4d4;
                border: 1px solid #3c4048;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
            }
            #HeaderToggleBtn:hover {
                background-color: #3c4048;
            }
            QMenuBar {
                background-color: #1e222b;
                color: #d4d4d4;
            }
            QMenuBar::item:selected {
                background-color: #2d3139;
            }
            QMenu {
                background-color: #1e222b;
                color: #d4d4d4;
                border: 1px solid #2d3139;
            }
            QMenu::item:selected {
                background-color: #094771;
            }
        """)
        
    def _load_settings(self):
        """Load settings configuration."""
        self._context.radians_mode = self._settings.value("radians_mode", False, type=bool)
        self._context.precision = self._settings.value("precision", self._context.precision, type=int)
        self._context.result_format = self._settings.value("result_format", self._context.result_format, type=str)
        self._deg_btn.setText("RAD" if self._context.radians_mode else "DEG")

        # Window size & state
        geometry = self._settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
    def _save_settings(self):
        """Save settings configuration."""
        self._settings.setValue("radians_mode", self._context.radians_mode)
        self._settings.setValue("precision", self._context.precision)
        self._settings.setValue("result_format", self._context.result_format)
        self._settings.setValue("geometry", self.saveGeometry())
        try:
            self._settings.setValue("workspace_state", json.dumps(self._serialize_state()))
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    # Workspace persistence (save/load all cards across sessions & files) #
    # ------------------------------------------------------------------ #
    def _serialize_state(self) -> dict:
        """Capture all workspaces and their cards as a JSON-serializable dict."""
        return {
            "version": 1,
            "current_workspace": self._current_workspace_idx,
            "workspaces": [
                {
                    "current_index": ws.current_index,
                    "blocks": [
                        {
                            "expression": b.expression,
                            "x": b.widget.x(),
                            "y": b.widget.y(),
                            "custom": b.is_custom_positioned,
                        }
                        for b in ws.blocks
                    ],
                }
                for ws in self._workspaces
            ],
        }

    def _restore_state(self, data: dict) -> bool:
        """Rebuild all workspaces/cards from a serialized dict. Returns success."""
        if not isinstance(data, dict) or "workspaces" not in data:
            return False
        ws_list = data["workspaces"]

        # Remove every existing card widget
        for ws in self._workspaces:
            for b in ws.blocks:
                b.widget.setParent(None)
                b.widget.deleteLater()
            ws.blocks = []

        # Set the active workspace first so new widgets get correct visibility
        self._current_workspace_idx = int(data.get("current_workspace", 0))
        if not (0 <= self._current_workspace_idx < len(self._workspaces)):
            self._current_workspace_idx = 0

        for i, ws in enumerate(self._workspaces):
            wd = ws_list[i] if i < len(ws_list) else {}
            for bd in wd.get("blocks", []):
                blk = self._create_block_for_workspace(
                    ws, bd.get("expression", ""),
                    int(bd.get("x", 20)), int(bd.get("y", 20)),
                )
                blk.is_custom_positioned = bool(bd.get("custom", False))
            if not ws.blocks:
                self._create_block_for_workspace(ws, "", 20, 20)
            ws.current_index = wd.get("current_index", 0)
            if not (0 <= ws.current_index < len(ws.blocks)):
                ws.current_index = 0

        # Ensure only the active workspace's cards are visible
        for i, ws in enumerate(self._workspaces):
            for b in ws.blocks:
                b.widget.setVisible(i == self._current_workspace_idx)

        # Sync the top input box to the active card
        active_ws = self._workspaces[self._current_workspace_idx]
        active_block = active_ws.blocks[active_ws.current_index]
        self._input_widget.blockSignals(True)
        self._input_widget.set_expression(active_block.expression)
        self._input_widget.blockSignals(False)
        return True

    def _restore_saved_workspaces(self):
        """Restore the auto-saved workspace state from the previous session."""
        raw = self._settings.value("workspace_state", "", type=str)
        if not raw:
            return
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return
        if self._restore_state(data):
            self._button_panel.set_active_workspace_highlight(self._current_workspace_idx)
            self._update_active_block_highlight()
            self.evaluate()

    def save_workspace_to_file(self):
        """Save all workspaces/cards to a JSON file for sharing or backup."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Workspace", "workspace.bkw",
            "BigKuery Workspace (*.bkw);;JSON Files (*.json);;All Files (*)"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._serialize_state(), f, indent=2)
        except OSError as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save workspace: {e}")

    def open_workspace_from_file(self):
        """Load all workspaces/cards from a previously saved JSON file."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Workspace", "",
            "BigKuery Workspace (*.bkw);;JSON Files (*.json);;All Files (*)"
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            QMessageBox.critical(self, "Open Error", f"Failed to open workspace: {e}")
            return
        if self._restore_state(data):
            self._button_panel.set_active_workspace_highlight(self._current_workspace_idx)
            self._update_active_block_highlight()
            self.evaluate()
            self._input_widget.setFocus()
        else:
            QMessageBox.warning(self, "Open Workspace", "That file is not a valid workspace.")
        
    def _update_active_block_highlight(self):
        """Apply selected highlight borders to active block and normal borders to inactive blocks."""
        workspace = self._workspaces[self._current_workspace_idx]
        for idx, block in enumerate(workspace.blocks):
            if idx == workspace.current_index:
                block.widget.set_selected(True)
            else:
                block.widget.set_selected(False)
                
    def _on_block_expression_changed(self, idx, text):
        """Sync inline block editing back to core and trigger workspace solve."""
        workspace = self._workspaces[self._current_workspace_idx]
        if 0 <= idx < len(workspace.blocks):
            block = workspace.blocks[idx]
            block.expression = text
            if idx == workspace.current_index:
                self._input_widget.blockSignals(True)
                self._input_widget.set_expression(text)
                self._input_widget.blockSignals(False)
            self._schedule_evaluate()

    def _on_block_position_changed(self, idx, x, y):
        """Update block position and trigger evaluation (as dragging can change vertical layout order)."""
        workspace = self._workspaces[self._current_workspace_idx]
        if 0 <= idx < len(workspace.blocks):
            block = workspace.blocks[idx]
            block.x = x
            block.y = y
            block.is_custom_positioned = True
            self._schedule_evaluate()
            
    def _on_block_clicked(self, idx):
        """Handle clicks on equation blocks to set active focus."""
        workspace = self._workspaces[self._current_workspace_idx]
        if 0 <= idx < len(workspace.blocks):
            workspace.current_index = idx
            self._update_active_block_highlight()
            
            # Sync main input field
            block = workspace.blocks[idx]
            self._input_widget.blockSignals(True)
            self._input_widget.set_expression(block.expression)
            self._input_widget.blockSignals(False)
            
    def _on_block_deleted(self, idx):
        """Handle deleting equation cards from the workspace."""
        workspace = self._workspaces[self._current_workspace_idx]
        if 0 <= idx < len(workspace.blocks):
            block = workspace.blocks[idx]
            block.widget.setParent(None)
            block.widget.deleteLater()
            workspace.blocks.pop(idx)

            # Qt's deleteLater() + Python refcounting reclaim the widget; no manual
            # gc.collect() needed (it would stall the UI on every delete).

            # Keep workspace non-empty
            if not workspace.blocks:
                self._create_block_for_workspace(workspace, "", 20, 20)
                workspace.current_index = 0
            else:
                workspace.current_index = min(workspace.current_index, len(workspace.blocks) - 1)
                
            self._update_active_block_highlight()
            
            # Load current index text to top input
            active_block = workspace.blocks[workspace.current_index]
            self._input_widget.blockSignals(True)
            self._input_widget.set_expression(active_block.expression)
            self._input_widget.blockSignals(False)
            
            self.evaluate()
        
    def _schedule_evaluate(self):
        """Request an evaluation, debounced to coalesce bursts of rapid edits."""
        self._eval_timer.start()

    def evaluate(self):
        """Parse and solve all workspace equations sequentially, supporting cumulative definitions."""
        # A pending debounced run is now subsumed by this immediate run.
        self._eval_timer.stop()
        # Guard against recursive signals during UI setup
        if not self._input_widget or not hasattr(self, "_workspaces"):
            return
            
        workspace = self._workspaces[self._current_workspace_idx]
        
        # 1. Update the active block's expression with the content of the top input box
        if 0 <= workspace.current_index < len(workspace.blocks):
            active_block = workspace.blocks[workspace.current_index]
            expr = self._input_widget.get_expression()
            active_block.expression = expr
            active_block.widget.set_expression(expr)
            
        # 2. Sort the blocks in the workspace list by their y-coordinate (top-to-bottom)
        # This matches evaluation sequence with the visual top-to-bottom layout
        active_block = workspace.blocks[workspace.current_index]
        workspace.blocks.sort(key=lambda b: (b.widget.y(), b.widget.x()))
        workspace.current_index = workspace.blocks.index(active_block)
        
        # 3. Multi-pass evaluation to propagate definitions globally (both forward and backward)
        deg_mode = not self._context.radians_mode
        prec = self._context.clamp_precision()
        eng = self._eng_mode
        wrap = self._context.is_wrap()
        fmt = 'latex' if KATEX_AVAILABLE else 'html'
        definitions = {}
        max_passes = 5

        for p in range(max_passes):
            prev_defs = definitions.copy()
            for block in workspace.blocks:
                expr_str = block.expression
                if not expr_str.strip():
                    continue
                processed = expr_str.replace('×', '*').replace('÷', '/').replace('−', '-')
                if '=' in processed:
                    # Use the same fmt as the final render pass so both share one
                    # memoized solve per equation (rather than solving twice).
                    _, next_defs = solve_workspace_equation(expr_str, definitions, deg_mode=deg_mode, precision=prec, eng=eng, fmt=fmt)
                    definitions.update(next_defs)

            if prev_defs == definitions:
                break
                
        # 4. Final pass: Apply results to the widgets using the stabilized definitions
        for i, block in enumerate(workspace.blocks):
            expr_str = block.expression
            if not expr_str.strip():
                block.widget.set_empty()
                block.widget.set_plot_context(None, definitions, deg_mode)
                continue

            processed = expr_str.replace('×', '*').replace('÷', '/').replace('−', '-')
            if '=' in processed:
                res_lines, _ = solve_workspace_equation(expr_str, definitions, deg_mode=deg_mode, precision=prec, eng=eng, fmt=fmt)
            else:
                res_lines, _ = solve_workspace_expression_steps(expr_str, definitions, deg_mode=deg_mode, precision=prec, eng=eng, fmt=fmt)

            block.widget.set_result(res_lines, wrap=wrap)

            # Single-variable, non-equation expressions can be plotted (e.g. "sin(x)",
            # or "a*x" once "a" is defined elsewhere in the workspace).
            plot_var = (
                free_symbol_for_plot(expr_str, deg_mode, known_names=definitions.keys())
                if PLOT_AVAILABLE else None
            )
            block.widget.set_plot_context(plot_var, definitions, deg_mode)
            
        # 5. Auto-layout non-custom positioned blocks in a vertical stack to prevent overlaps on resize
        # This runs AFTER results are set, so we use the correct, updated card heights
        current_y = 20
        for idx, block in enumerate(workspace.blocks):
            block.widget.set_index(idx)
            
            if not block.is_custom_positioned:
                block.widget.move(20, current_y)
                block.x = 20
                block.y = current_y
                block.widget.update_size()
                
            current_y = block.widget.y() + block.widget.height() + 20
            
        self._update_active_block_highlight()
        
    def add_new_equation(self):
        """Append a new empty equation block below the lowest block on the canvas."""
        workspace = self._workspaces[self._current_workspace_idx]
        
        # Save current active block expression
        active_block = workspace.blocks[workspace.current_index]
        active_block.expression = self._input_widget.get_expression()
        active_block.widget.set_expression(active_block.expression)
        
        # Find lowest y position
        max_y = 0
        for block in workspace.blocks:
            y_bottom = block.widget.y() + block.widget.height()
            if y_bottom > max_y:
                max_y = y_bottom
                
        new_y = max(20, max_y + 20)
        new_x = 20
        
        # Create block
        self._create_block_for_workspace(workspace, "", new_x, new_y)
        
        # Focus the new block
        workspace.current_index = len(workspace.blocks) - 1
        self._update_active_block_highlight()
        
        self._input_widget.blockSignals(True)
        self._input_widget.clear_expression()
        self._input_widget.blockSignals(False)
        self._input_widget.setFocus()
        
        self.evaluate()
        
    def switch_workspace(self, index: int):
        """Switch active calculation workspace (1, 2, or 3)."""
        # Save current active block input
        current_ws = self._workspaces[self._current_workspace_idx]
        if 0 <= current_ws.current_index < len(current_ws.blocks):
            active_block = current_ws.blocks[current_ws.current_index]
            active_block.expression = self._input_widget.get_expression()
            active_block.widget.set_expression(active_block.expression)
            
        # Hide current workspace widgets
        for block in current_ws.blocks:
            block.widget.hide()
            
        # Switch index
        self._current_workspace_idx = index
        self._button_panel.set_active_workspace_highlight(index)
        
        # Show new workspace widgets
        new_ws = self._workspaces[index]
        for block in new_ws.blocks:
            block.widget.show()
            
        # Load new workspace active block
        new_active_block = new_ws.blocks[new_ws.current_index]
        self._input_widget.blockSignals(True)
        self._input_widget.set_expression(new_active_block.expression)
        self._input_widget.blockSignals(False)
        
        self._update_active_block_highlight()
        self.evaluate()
        self._input_widget.setFocus()
        
    def clear(self):
        """Clear the current active equation."""
        workspace = self._workspaces[self._current_workspace_idx]
        if 0 <= workspace.current_index < len(workspace.blocks):
            active_block = workspace.blocks[workspace.current_index]
            active_block.expression = ""
            active_block.widget.set_expression("")
            
        self._input_widget.blockSignals(True)
        self._input_widget.clear_expression()
        self._input_widget.blockSignals(False)
        
        self.evaluate()
        self._input_widget.setFocus()
        
    def clear_all(self):
        """Clear all equations in the current active workspace, resetting to a single empty block."""
        workspace = self._workspaces[self._current_workspace_idx]
        
        # Delete widgets
        while len(workspace.blocks) > 1:
            block = workspace.blocks.pop()
            block.widget.setParent(None)
            block.widget.deleteLater()

        # Reset the first block to empty at default coordinate (20, 20)
        first_block = workspace.blocks[0]
        first_block.expression = ""
        first_block.widget.set_expression("")
        first_block.widget.move(20, 20)
        first_block.x = 20
        first_block.y = 20
        first_block.is_custom_positioned = False
        first_block.widget.show()
        
        workspace.current_index = 0
        
        self._input_widget.blockSignals(True)
        self._input_widget.clear_expression()
        self._input_widget.blockSignals(False)
        
        self._update_active_block_highlight()
        self.evaluate()
        self._input_widget.setFocus()
        
    def copy_result(self):
        """Copy plaintext result content to clipboard."""
        result = self._output_display.get_result()
        clipboard = QApplication.clipboard()
        clipboard.setText(result)
        
    def show_settings(self):
        """Show settings configuration dialog, preloaded with the current state."""
        self._settings_dialog.set_settings({
            "precision": self._context.precision,
            "radians_mode": self._context.radians_mode,
            "result_format": self._context.result_format,
        })
        self._settings_dialog.exec()
        
    def show_function_reference(self):
        """Show a reference of supported functions and constants (F1)."""
        html = (
            "<h3>Function Reference</h3>"
            "<p><b>Arithmetic:</b> <code>+ - * / ^</code> (power), <code>!</code> (factorial), "
            "<code>|x|</code> (absolute value), <code>%</code> (modulo)</p>"
            "<p><b>Trigonometric:</b> sin cos tan cot sec csc and inverses "
            "asin acos atan acot asec acsc (respects DEG/RAD)</p>"
            "<p><b>Hyperbolic:</b> sinh cosh tanh coth sech csch and inverses "
            "asinh acosh atanh</p>"
            "<p><b>Exp / Log:</b> exp, ln / log (natural log), log10, log2, sqrt, cbrt</p>"
            "<p><b>Calculus:</b> <code>diff(f, x)</code>, <code>integrate(f, x)</code>, "
            "<code>integrate(f, (x, a, b))</code>, <code>limit(f, x, a)</code></p>"
            "<p><b>Combinatorics:</b> factorial(n), binomial(n, k), gamma(x)</p>"
            "<p><b>Number theory:</b> gcd(a, b), lcm(a, b), floor, ceil, sign, min, max</p>"
            "<p><b>Constants:</b> pi (&pi;), e, phi (&phi;), tau (&tau;), euler (&gamma;), "
            "i (imaginary unit), inf (&infin;)</p>"
            "<p><b>Equations:</b> include an <code>=</code> to solve, e.g. "
            "<code>x^2 - 4 = 0</code></p>"
            "<p><b>Systems of equations:</b> separate with <code>;</code> to solve "
            "together, e.g. <code>x + y = 5; x - y = 1</code></p>"
            "<p><b>Plotting:</b> the 📈 button appears on any card with exactly one "
            "undefined variable (e.g. <code>sin(x)</code>) &mdash; click to plot it.</p>"
            "<p><b>Variables:</b> define in one card (<code>x = 5</code>) and reference it "
            "in others &mdash; definitions propagate across the workspace.</p>"
        )
        QMessageBox.information(self, "Function Reference", html)

    def show_about(self):
        """Show standard calculator about message."""
        QMessageBox.about(
            self,
            "About BigKuery Calculator",
            "<h3>BigKuery Calculator</h3>"
            "<p>An advanced equation rearranging and solving calculator powered by SymPy.</p>"
            "<p>&copy; 2026 Sanskar Sontakke</p>"
        )
        
    def _on_button_clicked(self, text: str):
        """Handle button panel click events."""
        if text == "CLEAR":
            self.clear()
        elif text == "BACKSPACE":
            cursor = self._input_widget.textCursor()
            cursor.deletePreviousChar()
        elif text == "LEFT":
            self._input_widget.moveCursor(self._input_widget.textCursor().MoveOperation.Left)
        elif text == "RIGHT":
            self._input_widget.moveCursor(self._input_widget.textCursor().MoveOperation.Right)
        else:
            self._input_widget.insert_text(text)
            
    def _on_function_clicked(self, func_name: str):
        """Handle scientific function clicks."""
        self._input_widget.insert_text(f"{func_name}(")
        
    def _on_constant_clicked(self, constant: str):
        """Handle variable and constant clicks."""
        self._input_widget.insert_text(constant)
        
    def _on_settings_changed(self, settings: dict):
        """Handle changes emitted by settings dialog."""
        if "radians_mode" in settings:
            self._context.radians_mode = settings["radians_mode"]
            self._deg_btn.setText("RAD" if self._context.radians_mode else "DEG")
        if "precision" in settings:
            self._context.precision = int(settings["precision"])
        if "result_format" in settings:
            self._context.result_format = settings["result_format"]
        self.evaluate()
            
    def resizeEvent(self, event):
        """Handle floating layout overlays on window resize."""
        super().resizeEvent(event)
        # Re-position the floating "+" action button over the display widget
        if hasattr(self, "_plus_btn") and hasattr(self, "_output_display"):
            margin = 15
            x = self._output_display.width() - self._plus_btn.width() - margin
            y = self._output_display.height() - self._plus_btn.height() - margin
            self._plus_btn.move(x, y)
            
    def closeEvent(self, event: QCloseEvent):
        """Save settings on application close."""
        self._save_settings()
        event.accept()
