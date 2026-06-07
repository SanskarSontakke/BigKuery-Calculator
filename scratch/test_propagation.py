import sys
from PyQt6.QtWidgets import QApplication
from bigkuery.gui.main_window import MainWindow

print("Initializing application...")
app = QApplication(sys.argv)

print("Creating MainWindow...")
window = MainWindow()

print("Clearing all...")
window.clear_all()

print("Setting sin(x)...")
window._on_block_clicked(0)
window._input_widget.set_expression("sin(x)")
window.evaluate()

print("Adding new equation...")
window.add_new_equation()

print("Setting x = 30...")
window._input_widget.set_expression("x = 30")
window.evaluate()

print("Getting result...")
result_text = window._output_display.get_result()
print("Result text:")
print(result_text)

assert "0.5" in result_text
print("Assertion passed successfully!")

window.close()
print("Window closed.")
