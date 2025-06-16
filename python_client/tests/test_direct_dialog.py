from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDialog
from PyQt5.QtCore import Qt, QTimer
import sys

class DirectDialogTest(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Direct Dialog Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        
        # Button to show direct dialog
        direct_button = QPushButton("Show Direct Dialog")
        direct_button.clicked.connect(self.show_direct_dialog)
        layout.addWidget(direct_button)
        
        # Button to show QMessageBox
        message_button = QPushButton("Show QMessageBox")
        message_button.clicked.connect(self.show_message_box)
        layout.addWidget(message_button)
        
        # Button to show dialog after delay
        delayed_button = QPushButton("Show Dialog After 2 Seconds")
        delayed_button.clicked.connect(self.show_delayed_dialog)
        layout.addWidget(delayed_button)
        
    def show_direct_dialog(self):
        """Show a direct dialog"""
        try:
            print("Creating direct dialog")
            from views.qt_login_view import SessionInvalidatedDialog
            dialog = SessionInvalidatedDialog(self, "Direct Test")
            print("Dialog created, about to show")
            result = dialog.exec_()
            print(f"Dialog closed with result: {result}")
        except Exception as e:
            print(f"Error showing direct dialog: {e}")
            import traceback
            traceback.print_exc()
            
    def show_message_box(self):
        """Show a QMessageBox"""
        try:
            print("Creating QMessageBox")
            from PyQt5.QtWidgets import QMessageBox
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Session Invalidated")
            msg.setInformativeText("Your session has been invalidated. You will be logged out.")
            msg.setWindowTitle("Session Ended")
            msg.setStandardButtons(QMessageBox.Ok)
            print("QMessageBox created, about to show")
            result = msg.exec_()
            print(f"QMessageBox closed with result: {result}")
        except Exception as e:
            print(f"Error showing QMessageBox: {e}")
            import traceback
            traceback.print_exc()
            
    def show_delayed_dialog(self):
        """Show dialog after a delay"""
        print("Will show dialog after 2 seconds")
        QTimer.singleShot(2000, self.show_direct_dialog)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DirectDialogTest()
    window.show()
    sys.exit(app.exec_()) 