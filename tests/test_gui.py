import pytest
import gc
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMouseEvent
from bigkuery.gui.output_display import OutputDisplay, EquationBlock
from bigkuery.gui.main_window import MainWindow

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    return app

def test_output_display_instantiation(qapp):
    display = OutputDisplay()
    assert display is not None
    assert display.canvas is not None

def test_equation_block_instantiation(qapp):
    block = EquationBlock(0, "1 + 1")
    assert block is not None
    assert block.get_expression() == "1 + 1"
    
    block.set_result(["2"])
    assert block.steps_layout.count() == 1

def test_global_definition_propagation(qapp):
    window = MainWindow()
    
    # Clear all to start with a clean single equation block
    window.clear_all()
    
    # 1. Focus block 0, set its expression to sin(x), and evaluate
    window._on_block_clicked(0)
    window._input_widget.set_expression("sin(x)")
    window.evaluate()
    
    # 2. Add a new equation block (focuses block 1 and clears input)
    window.add_new_equation()
    
    # 3. Set second block's expression to x = 30 and evaluate
    window._input_widget.set_expression("x = 30")
    window.evaluate()
    
    # In DEG mode (default), sin(30) should propagate and evaluate to 0.5
    result_text = window._output_display.get_result()
    assert "0.5" in result_text
    
    # Clean up window
    window.close()

def test_plot_toggle_for_single_variable_expression(qapp):
    from bigkuery.core.plotting import PLOT_AVAILABLE
    if not PLOT_AVAILABLE:
        pytest.skip("matplotlib/numpy not installed")

    window = MainWindow()
    window.clear_all()

    window._on_block_clicked(0)
    window._input_widget.set_expression("sin(x)")
    window.evaluate()

    ws = window._workspaces[window._current_workspace_idx]
    widget = ws.blocks[ws.current_index].widget
    assert widget._plot_var == "x"

    widget.toggle_plot()
    assert widget._plot_visible is True
    assert not widget.plot_label.pixmap().isNull()

    widget.toggle_plot()
    assert widget._plot_visible is False

    window.close()


def test_plot_unavailable_for_multi_variable_or_equation(qapp):
    window = MainWindow()
    window.clear_all()

    window._on_block_clicked(0)
    window._input_widget.set_expression("x + y")
    window.evaluate()
    ws = window._workspaces[window._current_workspace_idx]
    assert ws.blocks[ws.current_index].widget._plot_var is None

    window._input_widget.set_expression("x = 5")
    window.evaluate()
    assert ws.blocks[ws.current_index].widget._plot_var is None

    window.close()


def test_plot_uses_cross_card_parameter_definitions(qapp):
    from bigkuery.core.plotting import PLOT_AVAILABLE
    if not PLOT_AVAILABLE:
        pytest.skip("matplotlib/numpy not installed")

    window = MainWindow()
    window.clear_all()

    window._on_block_clicked(0)
    window._input_widget.set_expression("a = 3")
    window.evaluate()
    window.add_new_equation()
    window._input_widget.set_expression("a*x")
    window.evaluate()

    ws = window._workspaces[window._current_workspace_idx]
    widget = ws.blocks[ws.current_index].widget
    assert widget._plot_var == "x"

    widget.toggle_plot()
    assert widget._plot_visible is True
    assert not widget.plot_label.pixmap().isNull()

    window.close()


def test_result_format_wrap_caps_card_width(qapp):
    # A short input but a long numeric result: wrap mode should cap the card
    # width well below what scroll mode allows, while growing height instead.
    window_scroll = MainWindow()
    window_scroll.clear_all()
    window_scroll._context.result_format = "scroll"
    window_scroll._context.precision = 80
    window_scroll._on_block_clicked(0)
    window_scroll._input_widget.set_expression("sqrt(2)")
    window_scroll.evaluate()
    ws = window_scroll._workspaces[window_scroll._current_workspace_idx]
    scroll_widget = ws.blocks[ws.current_index].widget

    window_wrap = MainWindow()
    window_wrap.clear_all()
    window_wrap._context.result_format = "wrap"
    window_wrap._context.precision = 80
    window_wrap._on_block_clicked(0)
    window_wrap._input_widget.set_expression("sqrt(2)")
    window_wrap.evaluate()
    ws2 = window_wrap._workspaces[window_wrap._current_workspace_idx]
    wrap_widget = ws2.blocks[ws2.current_index].widget

    assert wrap_widget.width() < scroll_widget.width()
    assert wrap_widget._wrap is True
    assert scroll_widget._wrap is False

    window_scroll.close()
    window_wrap.close()


def test_result_format_persists_through_settings(qapp):
    from PyQt6.QtCore import QSettings
    try:
        window = MainWindow()
        window._context.result_format = "wrap"
        window._save_settings()

        window2 = MainWindow()
        assert window2._context.result_format == "wrap"

        window.close()
        window2.close()
    finally:
        QSettings("BigKuery", "Calculator").remove("result_format")
        QSettings("BigKuery", "Calculator").remove("workspace_state")


def test_workspace_save_restore_roundtrip(qapp):
    window = MainWindow()
    window.clear_all()

    # Workspace 0: two cards
    window._on_block_clicked(0)
    window._input_widget.set_expression("x = 5")
    window.evaluate()
    window.add_new_equation()
    window._input_widget.set_expression("x^2 + 1")
    window.evaluate()

    # Workspace 1: one card
    window.switch_workspace(1)
    window._input_widget.set_expression("2 + 2")
    window.evaluate()

    state = window._serialize_state()
    assert state["current_workspace"] == 1

    # Restore into a fresh window
    window2 = MainWindow()
    assert window2._restore_state(state)

    exprs0 = [b.expression for b in window2._workspaces[0].blocks]
    assert "x = 5" in exprs0
    assert "x^2 + 1" in exprs0

    exprs1 = [b.expression for b in window2._workspaces[1].blocks]
    assert "2 + 2" in exprs1

    assert window2._current_workspace_idx == 1

    window.close()
    window2.close()


def test_restore_state_rejects_garbage(qapp):
    window = MainWindow()
    # Invalid payloads must not raise and must be reported as failure
    assert window._restore_state({}) is False
    assert window._restore_state("not a dict") is False
    window.close()


def test_workspace_autopersist_across_sessions(qapp):
    from PyQt6.QtCore import QSettings
    try:
        window = MainWindow()
        window.clear_all()
        window._on_block_clicked(0)
        window._input_widget.set_expression("a = 42")
        window.evaluate()
        window._save_settings()   # persist to (isolated) QSettings
        window.close()

        # A fresh window should auto-restore the saved card during __init__
        window2 = MainWindow()
        exprs = [b.expression for ws in window2._workspaces for b in ws.blocks]
        assert "a = 42" in exprs
        window2.close()
    finally:
        # Keep other tests isolated from this persisted state
        QSettings("BigKuery", "Calculator").remove("workspace_state")


def test_equation_block_resizing_and_grow_only(qapp):
    block = EquationBlock(0, "1 + 1")
    block.show()
    block.update_size()
    w1 = block.width()
    h1 = block.height()
    
    # Set a much longer expression to trigger auto-growth
    block.set_expression("1 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 + 10")
    w2 = block.width()
    h2 = block.height()
    
    # The size must increase in width to fit the longer content
    assert w2 >= w1
    
    # Change it back to a short expression - it should NOT shrink (grow-only)
    block.set_expression("1")
    w3 = block.width()
    h3 = block.height()
    assert w3 == w2
    assert h3 == h2
    
    # Set empty to verify size resets on empty state
    block.set_empty()
    assert block.width() < w3 or block.height() < h3

def test_memory_handling_and_garbage_collection(qapp):
    # Verify that block deletion triggers explicit garbage collection cleanly
    window = MainWindow()
    workspace = window._workspaces[window._current_workspace_idx]
    
    window.add_new_equation()
    window.add_new_equation()
    assert len(workspace.blocks) == 3
    
    # Deleting a block triggers deleteLater and gc.collect()
    window._on_block_deleted(1)
    assert len(workspace.blocks) == 2
    
    gc.collect()
    window.close()
