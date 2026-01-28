"""Entry point for running BigKuery Calculator as a module."""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from bigkuery.gui.main_window import MainWindow


def main():
    """Main entry point for the BigKuery Calculator application."""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("BigKuery Calculator")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("BigKuery")
    app.setOrganizationDomain("bigkuery.com")
    
    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
