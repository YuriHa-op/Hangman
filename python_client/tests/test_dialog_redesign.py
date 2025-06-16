from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer
import sys

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Dialog Redesign Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        
        # Button to show dialog
        show_dialog_button = QPushButton("Show Redesigned Dialog")
        show_dialog_button.clicked.connect(self.show_dialog)
        layout.addWidget(show_dialog_button)
        
        # Button to test session flag reset
        reset_button = QPushButton("Test Session Flag Reset")
        reset_button.clicked.connect(self.test_flag_reset)
        layout.addWidget(reset_button)
        
    def show_dialog(self):
        """Show the redesigned session invalidated dialog"""
        try:
            from views.qt_login_view import SessionInvalidatedDialog
            dialog = SessionInvalidatedDialog(self, "Your session has been ended because you logged in from another location.")
            print("Dialog created, about to show")
            result = dialog.exec_()
            print(f"Dialog closed with result: {result}")
        except Exception as e:
            print(f"Error showing dialog: {e}")
            import traceback
            traceback.print_exc()
            
    def test_flag_reset(self):
        """Test the session invalidation flag reset"""
        try:
            # Import BaseController
            from controllers.base_controller import BaseController
            
            # Set the flag
            BaseController._session_invalidation_in_progress = True
            print(f"Flag set to: {BaseController._session_invalidation_in_progress}")
            
            # Simulate login
            print("Simulating login...")
            
            # Reset the flag as login would
            BaseController._session_invalidation_in_progress = False
            print(f"Flag after login reset: {BaseController._session_invalidation_in_progress}")
            
            # Show the dialog after reset
            QTimer.singleShot(1000, self.show_dialog)
            
        except Exception as e:
            print(f"Error testing flag reset: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_()) 