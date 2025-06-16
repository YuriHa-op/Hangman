from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer
from views.qt_login_view import SessionInvalidatedDialog
import sys

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Session Dialog Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        
        # Button to show dialog
        show_dialog_button = QPushButton("Show Session Invalidated Dialog")
        show_dialog_button.clicked.connect(self.show_dialog)
        layout.addWidget(show_dialog_button)
        
        # Button to show dialog after delay
        delayed_button = QPushButton("Show Dialog After 2 Seconds")
        delayed_button.clicked.connect(self.show_dialog_delayed)
        layout.addWidget(delayed_button)
        
    def show_dialog(self):
        """Show the session invalidated dialog"""
        print("Showing session invalidated dialog")
        dialog = SessionInvalidatedDialog(self, "Test Session Invalidation")
        result = dialog.exec_()
        print(f"Dialog closed with result: {result}")
        
    def show_dialog_delayed(self):
        """Show the dialog after a delay"""
        print("Will show dialog after 2 seconds")
        QTimer.singleShot(2000, self.show_dialog)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_()) 