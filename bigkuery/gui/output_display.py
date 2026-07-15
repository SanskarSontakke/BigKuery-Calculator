"""
OutputDisplay -Whiteboard canvas viewport with draggable, inline-editable equation blocks.
"""

import re

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLineEdit, QLabel, QPushButton,
    QScrollArea, QWidget, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QByteArray
from PyQt6.QtGui import QPainter, QColor, QFont, QCursor, QFontMetrics, QPixmap

from .math_view import KATEX_AVAILABLE
if KATEX_AVAILABLE:
    from .math_view import MathView

from bigkuery.core.plotting import PLOT_AVAILABLE, render_plot_png


def _strip_markup(s: str) -> str:
    """Reduce an HTML or LaTeX display line to readable plain text (for copy)."""
    # HTML tags and a few entities
    s = re.sub(r"<[^<]+?>", "", s)
    for ent, ch in (("&times;", "×"), ("&rarr;", "→"), ("&pi;", "π"),
                    ("&infin;", "∞"), ("&phi;", "φ"), ("&gamma;", "γ"),
                    ("&minus;", "−"), ("&nbsp;", " ")):
        s = s.replace(ent, ch)
    # Common LaTeX constructs -> plain text
    s = s.replace("\\left", "").replace("\\right", "")
    s = re.sub(r"\\frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}", r"(\1)/(\2)", s)
    s = re.sub(r"\\sqrt\s*\{([^{}]*)\}", r"sqrt(\1)", s)
    s = s.replace("\\times", "×").replace("\\approx", "≈").replace("\\to", "→")
    s = re.sub(r"\\(?:operatorname|text|mathrm)\s*\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\[a-zA-Z]+", "", s)        # drop remaining commands (\cos, \pi, …)
    s = s.replace("\\{", "{").replace("\\}", "}")
    s = s.replace("{", "").replace("}", "")
    return s.strip()


class EquationBlock(QFrame):
    """
    Draggable calculation card widget showing the equation input
    and step-by-step evaluation results.
    """
    expression_changed = pyqtSignal(int, str)
    position_changed = pyqtSignal(int, int, int)
    clicked = pyqtSignal(int)
    deleted = pyqtSignal(int)
    
    def __init__(self, index, expression, parent=None):
        super().__init__(parent)
        self.index = index
        self._selected = False
        self._is_dragging = False
        self._drag_start_pos = None
        self._block_start_pos = None
        
        # Resizing states
        self._is_resizing = False
        self._resize_start_pos = None
        self._block_start_size = None
        self._initial_size_set = False
        self.setMouseTracking(True)
        
        self.setObjectName("EquationBlock")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        
        # Apply shadow effect for floating card look
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)
        
        self.set_selected(False)
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 8, 10, 10)
        self.main_layout.setSpacing(6)
        
        # Header Row
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.index_label = QLabel(f"#{index + 1}:")
        self.index_label.setStyleSheet("color: #58a6ff; font-weight: bold; font-size: 13px;")
        header_layout.addWidget(self.index_label)
        
        header_layout.addStretch()

        self.plot_btn = QPushButton("\U0001F4C8")  # chart emoji
        self.plot_btn.setFixedSize(20, 20)
        self.plot_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.plot_btn.setToolTip("Show/hide plot")
        self.plot_btn.setVisible(False)
        self.plot_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #8b949e;
                font-size: 12px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1a2d3d;
                color: #4fc9b0;
            }
        """)
        self.plot_btn.clicked.connect(self.toggle_plot)
        header_layout.addWidget(self.plot_btn)

        self.delete_btn = QPushButton("×")
        self.delete_btn.setFixedSize(20, 20)
        self.delete_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #8b949e;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #6e3030;
                color: #ffffff;
            }
        """)
        self.delete_btn.clicked.connect(lambda: self.deleted.emit(self.index))
        header_layout.addWidget(self.delete_btn)
        
        self.main_layout.addLayout(header_layout)
        
        # Inline Equation Input
        self.input_edit = QLineEdit(expression)
        self.input_edit.setStyleSheet("""
            QLineEdit {
                background-color: #16191f;
                color: #ffffff;
                border: 1px solid #2d3139;
                border-radius: 4px;
                padding: 4px 6px;
                font-family: Consolas, monospace;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #58a6ff;
            }
        """)
        self.input_edit.textChanged.connect(self._on_text_changed)
        # Focus in event notification to set as active block
        self.input_edit.installEventFilter(self)
        self.main_layout.addWidget(self.input_edit)
        
        # Steps layout
        self.steps_widget = QWidget()
        self.steps_layout = QVBoxLayout(self.steps_widget)
        self.steps_layout.setContentsMargins(5, 5, 5, 5)
        self.steps_layout.setSpacing(4)
        self.main_layout.addWidget(self.steps_widget)

        # KaTeX renderer (created lazily) and the last rendered lines (for copy).
        self._math_view = None
        self._result_lines = []
        self._wrap = False

        # Plot state: a chart toggle shown only for single-variable expressions.
        # MainWindow keeps this up to date via set_plot_context() on every evaluate.
        self.plot_label = QLabel()
        self.plot_label.setVisible(False)
        self.plot_label.setStyleSheet("background: transparent;")
        self.main_layout.addWidget(self.plot_label)
        self._plot_var = None
        self._plot_defs = {}
        self._plot_deg_mode = True
        self._plot_visible = False

        self.adjustSize()
        
    def _on_text_changed(self, text):
        self.expression_changed.emit(self.index, text)
        self.update_size()
        
    def get_expression(self):
        return self.input_edit.text()
        
    def set_expression(self, text):
        self.input_edit.blockSignals(True)
        self.input_edit.setText(text)
        self.input_edit.blockSignals(False)
        self.update_size()
        
    def set_index(self, index):
        self.index = index
        self.index_label.setText(f"#{index + 1}:")
        
    def set_selected(self, selected: bool):
        self._selected = selected
        if selected:
            self.setStyleSheet("""
                #EquationBlock {
                    background-color: #22272e;
                    border: 2px solid #58a6ff;
                    border-radius: 8px;
                }
            """)
        else:
            self.setStyleSheet("""
                #EquationBlock {
                    background-color: #20242c;
                    border: 2px solid #2d3139;
                    border-radius: 8px;
                }
            """)
            
    def _clear_step_labels(self):
        """Remove step QLabels but keep a persistent MathView, if present."""
        for i in reversed(range(self.steps_layout.count())):
            w = self.steps_layout.itemAt(i).widget()
            if w is not None and w is not self._math_view:
                w.setParent(None)
                w.deleteLater()

    def set_empty(self):
        self._result_lines = []
        if self._math_view is not None:
            self._math_view.set_lines([])
        else:
            self._clear_step_labels()
            lbl = QLabel("[empty]")
            lbl.setStyleSheet("color: #555555; font-style: italic; font-family: Consolas, monospace;")
            self.steps_layout.addWidget(lbl)

        # Reset constraints so that it can shrink back to default empty size
        self.setMinimumSize(150, 100)
        self.resize(150, 100)
        self._initial_size_set = False
        self.update_size()

    # Width cap (px) applied to the content area when result_format is "wrap".
    WRAP_MAX_WIDTH = 420

    def set_result(self, lines, wrap=False):
        self._result_lines = list(lines)
        self._wrap = bool(wrap)
        if KATEX_AVAILABLE:
            self._set_result_katex(lines, self._wrap)
        else:
            self._set_result_html(lines, self._wrap)

    def _ensure_math_view(self):
        """Create the MathView on first use (keeps empty cards lightweight)."""
        if self._math_view is None:
            self._clear_step_labels()
            self._math_view = MathView(self.steps_widget)
            self._math_view.content_resized.connect(self._on_math_resized)
            self.steps_layout.addWidget(self._math_view)
        return self._math_view

    def _on_math_resized(self, w, h):
        self.update_size()

    def _set_result_katex(self, latex_lines, wrap=False):
        mv = self._ensure_math_view()
        mv.set_lines(latex_lines, wrap=wrap)
        self.update_size()

    def _set_result_html(self, html_lines, wrap=False):
        self._clear_step_labels()
        width_style = f"max-width: {self.WRAP_MAX_WIDTH}px;" if wrap else ""
        for idx, line in enumerate(html_lines):
            lbl = QLabel()
            lbl.setTextFormat(Qt.TextFormat.RichText)
            lbl.setWordWrap(wrap)
            if wrap:
                # setFixedWidth (not just maximumWidth) forces Qt to actually
                # reflow the text and report a wrapped sizeHint/heightForWidth;
                # maximumWidth alone leaves sizeHint() reporting the unwrapped width.
                lbl.setFixedWidth(self.WRAP_MAX_WIDTH)
            else:
                lbl.setMinimumWidth(0)
                lbl.setMaximumWidth(16777215)  # Qt's QWIDGETSIZE_MAX: remove any prior cap

            # Rich colors: blue for steps, bold green for final answer
            if idx == len(html_lines) - 1:
                lbl.setText(f"<div style='color: #56d364; font-weight: bold; font-family: Consolas, monospace; font-size: 14px; {width_style}'>{line}</div>")
            else:
                lbl.setText(f"<div style='color: #79c0ff; font-family: Consolas, monospace; font-size: 14px; {width_style}'>{line}</div>")

            self.steps_layout.addWidget(lbl)
        self.update_size()

    # --- Plotting ---------------------------------------------------------
    def set_plot_context(self, var_name, definitions, deg_mode):
        """Update what this card would plot. Called by MainWindow on every evaluate."""
        self._plot_var = var_name
        self._plot_defs = dict(definitions or {})
        self._plot_deg_mode = deg_mode
        self.plot_btn.setVisible(PLOT_AVAILABLE and var_name is not None)

        if var_name is None:
            if self._plot_visible:
                self._hide_plot()
        elif self._plot_visible:
            self._render_plot()  # refresh an already-open plot with new context

    def toggle_plot(self):
        if self._plot_visible:
            self._hide_plot()
        else:
            self._show_plot()

    def _show_plot(self):
        if self._plot_var is None:
            return
        self._render_plot()
        self.plot_label.setVisible(True)
        self._plot_visible = True
        self.update_size()

    def _hide_plot(self):
        self.plot_label.setVisible(False)
        self._plot_visible = False
        self.update_size()

    def _render_plot(self):
        try:
            png = render_plot_png(
                self.get_expression(), self._plot_var,
                definitions=self._plot_defs, deg_mode=self._plot_deg_mode,
            )
            pix = QPixmap()
            pix.loadFromData(QByteArray(png), "PNG")
            self.plot_label.setPixmap(pix)
            self.plot_label.setFixedSize(pix.size())
            self.plot_label.setText("")
        except Exception as e:
            self.plot_label.setPixmap(QPixmap())
            self.plot_label.setText(f"Plot error: {e}")
            self.plot_label.setStyleSheet("color: #f14c4c; background: transparent;")
            self.plot_label.setFixedSize(self.plot_label.sizeHint())
        self.update_size()

    def update_size(self):
        """Adjust block size dynamically, growing in both directions but not shrinking."""
        # 1. Measure input text width
        font = self.input_edit.font()
        metrics = QFontMetrics(font)
        text_width = metrics.horizontalAdvance(self.input_edit.text())
        # Provide safe minimum and padding
        input_width = max(150, text_width + 30)
        self.input_edit.setMinimumWidth(input_width)
        
        # 2. Measure step labels width
        # QLabel.sizeHint() reports the *unwrapped* preferred width regardless of
        # any setFixedWidth()/setMaximumWidth() constraint (those are enforced by
        # the layout engine, not reflected in sizeHint() itself). So in wrap mode,
        # where labels are fixed-width, skip this measurement entirely and just
        # use the wrap cap; only in scroll mode does the natural label width matter.
        max_step_width = 150
        if not self._wrap:
            for i in range(self.steps_layout.count()):
                widget = self.steps_layout.itemAt(i).widget()
                if isinstance(widget, QLabel):
                    max_step_width = max(max_step_width, widget.sizeHint().width())
        elif self.steps_layout.count() > 0:
            max_step_width = self.WRAP_MAX_WIDTH

        # 3. Apply width to card frame
        card_width = max(input_width + 25, max_step_width + 25)
        
        # 4. Force layout system to recalculate geometries and size hints immediately
        self.steps_widget.updateGeometry()
        self.steps_layout.activate()
        self.updateGeometry()
        self.main_layout.activate()
        
        # 5. Determine the ideal size and resize the widget in both directions
        hint = self.sizeHint()
        target_w = max(hint.width(), card_width)
        target_h = hint.height()
        
        # Keep current sizes if they are already larger (prevent shrinking, only allow growing)
        current_w = self.width()
        current_h = self.height()
        
        if not self._initial_size_set:
            new_w = target_w
            new_h = target_h
            # Only count as set if it's non-trivial (e.g. not empty initialization)
            if self.get_expression().strip() or self.steps_layout.count() > 1:
                self._initial_size_set = True
        else:
            new_w = max(current_w, target_w)
            new_h = max(current_h, target_h)
            
        self.setMinimumWidth(new_w)
        self.setMinimumHeight(new_h)
        self.resize(new_w, new_h)
        
    def eventFilter(self, obj, event):
        # Notify MainWindow when user focuses the input line edit of this block
        if obj == self.input_edit and event.type() == event.Type.FocusIn:
            self.clicked.emit(self.index)
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.index)
            pos = event.position().toPoint()
            
            # Check if clicked in bottom-right corner resize zone
            if pos.x() >= self.width() - 15 and pos.y() >= self.height() - 15:
                self._is_resizing = True
                self._resize_start_pos = event.globalPosition().toPoint()
                self._block_start_size = self.size()
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
                event.accept()
                return
            else:
                self._drag_start_pos = event.globalPosition().toPoint()
                self._block_start_pos = self.pos()
                self._is_dragging = True
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                event.accept()
                return
                
        super().mousePressEvent(event)
            
    def mouseMoveEvent(self, event):
        # 1. Hover cursor update (with no buttons pressed, requires setMouseTracking(True))
        pos = event.position().toPoint()
        in_resize_zone = (pos.x() >= self.width() - 15 and pos.y() >= self.height() - 15)
        
        if not self._is_dragging and not self._is_resizing:
            if in_resize_zone:
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
                
        # 2. Resize behavior
        if self._is_resizing and self._resize_start_pos is not None:
            delta = event.globalPosition().toPoint() - self._resize_start_pos
            new_width = max(150, self._block_start_size.width() + delta.x())
            new_height = max(100, self._block_start_size.height() + delta.y())
            
            # Lock the minimum size to the manual sizing
            self.setMinimumSize(new_width, new_height)
            self.resize(new_width, new_height)
            
            self.position_changed.emit(self.index, self.x(), self.y())
            event.accept()
            return
            
        # 3. Drag behavior
        if self._is_dragging and self._drag_start_pos is not None:
            delta = event.globalPosition().toPoint() - self._drag_start_pos
            new_pos = self._block_start_pos + delta
            
            parent = self.parentWidget()
            if parent:
                max_x = parent.width() - self.width()
                max_y = parent.height() - self.height()
                new_pos.setX(max(0, min(new_pos.x(), max_x)))
                new_pos.setY(max(0, min(new_pos.y(), max_y)))
                
            self.move(new_pos)
            self.position_changed.emit(self.index, new_pos.x(), new_pos.y())
            event.accept()
            return
            
        super().mouseMoveEvent(event)
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False
            self._is_resizing = False
            self._drag_start_pos = None
            self._resize_start_pos = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
            
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        
        # Draw a small resize grip at bottom right
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        painter.setPen(QColor("#8b949e")) # soft grey color matching the delete btn
        
        # Draw three small diagonal lines
        painter.drawLine(w - 4, h - 12, w - 12, h - 4)
        painter.drawLine(w - 4, h - 8, w - 8, h - 4)
        painter.drawLine(w - 4, h - 4, w - 4, h - 4)
        
        painter.end()


class CanvasWidget(QWidget):
    """
    Whiteboard background: draws the grid and supports panning the view by
    click-dragging on empty space.
    """
    def __init__(self, parent_scroll_area):
        super().__init__()
        self._scroll_area = parent_scroll_area
        self._pan_start_pos = None
        self._start_h_val = 0
        self._start_v_val = 0
        self.setMinimumSize(3000, 3000)
        self.setStyleSheet("background-color: #1e1e1e;")

    def paintEvent(self, event):
        painter = QPainter(self)

        # Only repaint the exposed region. The canvas is 3000x3000, so drawing the
        # full grid every paint would be ~240 long lines; clipping to event.rect()
        # keeps painting proportional to what's actually visible.
        rect = event.rect()
        painter.fillRect(rect, QColor("#1e1e1e"))

        painter.setPen(QColor(50, 50, 50, 100))  # dark grey grid lines
        grid_size = 25
        left = rect.left() - (rect.left() % grid_size)
        top = rect.top() - (rect.top() % grid_size)

        x = left
        while x <= rect.right():
            painter.drawLine(x, rect.top(), x, rect.bottom())
            x += grid_size

        y = top
        while y <= rect.bottom():
            painter.drawLine(rect.left(), y, rect.right(), y)
            y += grid_size

        painter.end()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._pan_start_pos = event.globalPosition().toPoint()
            self._start_h_val = self._scroll_area.horizontalScrollBar().value()
            self._start_v_val = self._scroll_area.verticalScrollBar().value()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            
    def mouseMoveEvent(self, event):
        if self._pan_start_pos is not None:
            delta = event.globalPosition().toPoint() - self._pan_start_pos
            h_bar = self._scroll_area.horizontalScrollBar()
            v_bar = self._scroll_area.verticalScrollBar()
            h_bar.setValue(self._start_h_val - delta.x())
            v_bar.setValue(self._start_v_val - delta.y())
            event.accept()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._pan_start_pos = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()


class OutputDisplay(QScrollArea):
    """
    Touchpad-compatible scrollable viewport containing the grid canvas.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.setStyleSheet("""
            QScrollArea {
                background-color: #1e1e1e;
                border: 2px solid #3c3c3c;
                border-radius: 8px;
            }
            QScrollBar:vertical {
                border: none;
                background: #1e1e1e;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #2d3139;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background: #58a6ff;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                border: none;
                background: #1e1e1e;
                height: 10px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #2d3139;
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::handle:horizontal:hover {
                background: #58a6ff;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)
        
        self.canvas = CanvasWidget(self)
        self.setWidget(self.canvas)
        
    def clear_canvas(self):
        for block in self.canvas.findChildren(EquationBlock):
            block.deleteLater()
            
    def clear_result(self):
        self.clear_canvas()
        
    def get_result(self) -> str:
        blocks = list(self.canvas.findChildren(EquationBlock))
        blocks.sort(key=lambda b: (b.y(), b.x()))
        lines = []
        for block in blocks:
            lines.append(f"#{block.index + 1}: {block.get_expression()}")
            for line in getattr(block, "_result_lines", []):
                lines.append(f"  {_strip_markup(line)}")
        return "\n".join(lines)
