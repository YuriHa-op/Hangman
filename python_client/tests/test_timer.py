from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDialog, QLabel
from PyQt5.QtCore import Qt, QTimer
import sys
import threading
import time

class TestDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Test Dialog")
        self.setGeometry(100, 100, 300, 200)
        
        layout = QVBoxLayout(self)
        label = QLabel("This dialog was shown from a background thread using QTimer.singleShot")
        layout.addWidget(label)
        
        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("QTimer Test")
        self.setGeometry(100, 100, 400, 200)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create button to start background thread
        self.start_thread_button = QPushButton("Start Background Thread")
        self.start_thread_button.clicked.connect(self.start_background_thread)
        layout.addWidget(self.start_thread_button)
        
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
        QTimer.singleShot(0, self.show_dialog_on_main_thread)
        
    def show_dialog_on_main_thread(self):
        """Show dialog on the main thread"""
        print("Showing dialog on main thread")
        dialog = TestDialog(self)
        result = dialog.exec_()
        print("Dialog closed with result:", result)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_()) 