import pytest
import gc
import weakref
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from PyQt6 import sip
from bigkuery.gui.main_window import MainWindow

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    return app

def test_block_widget_garbage_collection(qapp):
    # This test verifies that deleting an equation card releases its memory 
    # and leaves no dangling reference cycles.
    window = MainWindow()
    window.clear_all()
    
    # 1. Add a block
    window.add_new_equation()
    workspace = window._workspaces[window._current_workspace_idx]
    assert len(workspace.blocks) == 2
    
    block_widget = workspace.blocks[1].widget
    
    # Create a weak reference to the block widget
    widget_ref = weakref.ref(block_widget)
    
    # Verify the reference is alive
    assert widget_ref() is not None
    
    # 2. Delete the block (triggers setParent(None), deleteLater, and workspace pop)
    window._on_block_deleted(1)
    
    # The block object is removed from workspace blocks list
    assert len(workspace.blocks) == 1
    
    # Remove the local reference so it can be garbage collected
    del block_widget
    
    # Spin the event loop briefly to process the deferred deletion
    QTimer.singleShot(10, qapp.quit)
    qapp.exec()
    
    # Force Python's cyclic garbage collector to clean up wrapper
    gc.collect()
    
    # The widget memory should be freed, so weak reference becomes None
    assert widget_ref() is None or sip.isdeleted(widget_ref())
    
    window.close()

def test_clear_all_memory_cleanup(qapp):
    window = MainWindow()
    workspace = window._workspaces[window._current_workspace_idx]
    
    # Add multiple blocks
    for _ in range(5):
        window.add_new_equation()
    
    # Store weak refs to all created widgets
    widgets = [block.widget for block in workspace.blocks]
    refs = [weakref.ref(w) for w in widgets]
    
    # Clear all back to a single empty block
    window.clear_all()
    
    assert len(workspace.blocks) == 1
    
    # Remove local references
    del widgets
    
    # Spin event loop to process deferred deletes
    QTimer.singleShot(10, qapp.quit)
    qapp.exec()
    
    gc.collect()
    
    # The cleared widgets (indices 1 to 5) should be freed/deleted
    for i in range(1, len(refs)):
        assert refs[i]() is None or sip.isdeleted(refs[i]())
        
    window.close()
