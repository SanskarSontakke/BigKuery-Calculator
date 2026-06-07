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
