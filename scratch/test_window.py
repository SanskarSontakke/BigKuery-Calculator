import sys
from PyQt6.QtWidgets import QApplication
from bigkuery.gui.main_window import MainWindow

print("Initializing QApplication...")
app = QApplication(sys.argv)
print("Creating MainWindow...")
window = MainWindow()
print("MainWindow created successfully!")
window.close()
print("MainWindow closed successfully!")
