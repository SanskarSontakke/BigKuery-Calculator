import sys
from PyQt6.QtWidgets import QApplication
from bigkuery.gui.output_display import EquationBlock

app = QApplication(sys.argv)
block = EquationBlock(0, "sin(x)")
block.show()

print("Initial minimum size:", block.minimumWidth(), block.minimumHeight())
print("Initial size hint:", block.sizeHint().width(), block.sizeHint().height())

# Set a very long expression
block.set_expression("sin(x)^2/sin(x) + cos(x) - tan(x) + log(x) + e^x + pi^2")
print("After long expression minimum size:", block.minimumWidth(), block.minimumHeight())
print("After long expression size hint:", block.sizeHint().width(), block.sizeHint().height())

# Set many steps
block.set_result([
    "step 1: very long line with step description here that should stretch horizontally",
    "step 2: second step that is also long",
    "step 3",
    "step 4",
    "step 5: final answer is here"
])
print("After steps minimum size:", block.minimumWidth(), block.minimumHeight())
print("After steps size hint:", block.sizeHint().width(), block.sizeHint().height())
print("Actual size:", block.width(), block.height())
