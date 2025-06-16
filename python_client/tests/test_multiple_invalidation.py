from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt, QTimer
import sys
import threading
import time

# Mock BaseController class to test the flag mechanism
class BaseController:
    # Class-level flag to track if session invalidation is already being handled
    _session_invalidation_in_progress = False
    
    def __init__(self):
        self.invalidation_count = 0
        
    def handle_session_invalidated(self):
        """Handle when the session is invalidated"""
        # Check if session invalidation is already being handled
        if BaseController._session_invalidation_in_progress:
            print("Session invalidation already in progress, skipping duplicate handler")
            return
            
        # Set the flag to prevent multiple handlers
        BaseController._session_invalidation_in_progress = True
        
        print("Session invalidated! Handling in BaseController")
        self.invalidation_count += 1
        
        # Simulate some work
        print("Doing some work...")
        time.sleep(1)
        print(f"Work done. Invalidation count: {self.invalidation_count}")
        
        # Reset the flag when done
        BaseController._session_invalidation_in_progress = False
        print("Flag reset")

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Multiple Invalidation Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create controller
        self.controller = BaseController()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        
        # Status label
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        # Button to trigger single invalidation
        single_button = QPushButton("Trigger Single Invalidation")
        single_button.clicked.connect(self.trigger_single_invalidation)
        layout.addWidget(single_button)
        
        # Button to trigger multiple invalidations
        multiple_button = QPushButton("Trigger 5 Simultaneous Invalidations")
        multiple_button.clicked.connect(self.trigger_multiple_invalidations)
        layout.addWidget(multiple_button)
        
        # Button to trigger rapid invalidations
        rapid_button = QPushButton("Trigger 10 Rapid Invalidations")
        rapid_button.clicked.connect(self.trigger_rapid_invalidations)
        layout.addWidget(rapid_button)
        
    def trigger_single_invalidation(self):
        """Trigger a single invalidation"""
        self.status_label.setText("Triggering single invalidation...")
        self.controller.handle_session_invalidated()
        self.status_label.setText(f"Single invalidation complete. Count: {self.controller.invalidation_count}")
        
    def trigger_multiple_invalidations(self):
        """Trigger multiple invalidations simultaneously"""
        self.status_label.setText("Triggering 5 simultaneous invalidations...")
        
        # Create and start 5 threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=self.controller.handle_session_invalidated)
            thread.daemon = True
            threads.append(thread)
            
        # Start all threads
        for thread in threads:
            thread.start()
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        self.status_label.setText(f"Multiple invalidations complete. Count: {self.controller.invalidation_count}")
        
    def trigger_rapid_invalidations(self):
        """Trigger invalidations in rapid succession"""
        self.status_label.setText("Triggering 10 rapid invalidations...")
        
        # Trigger invalidations with short delays
        for i in range(10):
            QTimer.singleShot(i * 100, self.controller.handle_session_invalidated)
            
        # Update status after all should be complete
        QTimer.singleShot(1500, lambda: self.status_label.setText(
            f"Rapid invalidations complete. Count: {self.controller.invalidation_count}"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_()) 