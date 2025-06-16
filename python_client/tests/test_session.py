from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDialog, QLabel
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
import sys
import threading
import time

class SessionInvalidatedDialog(QDialog):
    def __init__(self, parent=None, reason=""):
        super().__init__(parent)
        self.setWindowTitle("SESSION ENDED")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #C6C6C6; border: 6px solid #FF0000;")
        
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("SESSION ENDED")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #FF0000;")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Message
        message = "YOUR SESSION HAS BEEN ENDED BECAUSE YOU LOGGED IN FROM ANOTHER LOCATION."
        if reason:
            message = f"YOUR SESSION HAS BEEN ENDED: {reason.upper()}"
            
        message_label = QLabel(message)
        message_label.setStyleSheet("font-size: 16px; color: #FF0000;")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        
        # Button
        ok_button = QPushButton("OK")
        ok_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                background-color: #FF0000;
                border: 2px solid #2d2d2d;
                color: white;
                min-width: 150px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #FF5555;
            }
        """)
        
        # Add widgets to layout
        layout.addWidget(title_label)
        layout.addWidget(message_label)
        layout.addWidget(ok_button)
        
        # Connect button
        ok_button.clicked.connect(self.accept)
        
        # Set fixed size
        self.setFixedSize(500, 300)

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Session Test")
        self.setGeometry(100, 100, 400, 200)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create buttons
        self.start_thread_button = QPushButton("Start Background Thread")
        self.start_thread_button.clicked.connect(self.start_background_thread)
        layout.addWidget(self.start_thread_button)
        
        self.show_dialog_button = QPushButton("Show Dialog Directly")
        self.show_dialog_button.clicked.connect(self.show_dialog_directly)
        layout.addWidget(self.show_dialog_button)
        
    def start_background_thread(self):
        """Start a background thread that will show a dialog after a delay"""
        print("Starting background thread")
        thread = threading.Thread(target=self.background_task)
        thread.daemon = True
        thread.start()
        
    def background_task(self):
        """Background task that will show a dialog after a delay"""
        print("Background thread started")
        # Simulate some work
        time.sleep(2)
        
        print("Background thread showing dialog")
        # Use QTimer.singleShot to show dialog on the main thread
        QTimer.singleShot(0, lambda: self._show_session_invalidated_dialog())
        
    def _show_session_invalidated_dialog(self):
        """Helper method to show the session invalidated dialog on the main thread"""
        try:
            print("Executing session invalidation on main thread")
            self.handle_session_invalidated()
        except Exception as e:
            print(f"Error showing session invalidated dialog: {e}")
            import traceback
            traceback.print_exc()
    
    @pyqtSlot()
    def handle_session_invalidated(self):
        """Handle when the session is invalidated"""
        print("Session invalidated! Handling in MainWindow")
        self.show_dialog_directly()
        
    def show_dialog_directly(self):
        """Show the session invalidated dialog directly"""
        print("Showing dialog directly")
        dialog = SessionInvalidatedDialog(self, "Test Reason")
        result = dialog.exec_()
        print("Dialog closed with result:", result)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_()) 