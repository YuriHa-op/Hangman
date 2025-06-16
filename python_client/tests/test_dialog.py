from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
import sys
import os

# Import the dialog directly
from tests.views.qt_login_view import SessionInvalidatedDialog

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Session Dialog Test")
        self.setGeometry(100, 100, 400, 200)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create button to show dialog
        self.show_dialog_button = QPushButton("Show Session Invalidated Dialog")
        self.show_dialog_button.clicked.connect(self.show_session_invalidated_dialog)
        layout.addWidget(self.show_dialog_button)
        
    def show_session_invalidated_dialog(self):
        """Show the session invalidated dialog"""
        print("Showing session invalidated dialog")
        dialog = SessionInvalidatedDialog(self, "You logged in from another device")
        # Make sure the dialog is shown on top
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowStaysOnTopHint)
        print("Session invalidated dialog created, about to show")
        result = dialog.exec_()
        print("Session invalidated dialog closed with result:", result)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_()) 