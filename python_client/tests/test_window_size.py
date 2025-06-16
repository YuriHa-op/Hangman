from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QStackedWidget, QLabel
from PyQt5.QtCore import Qt, QTimer, QSize
import sys

class LoginView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        label = QLabel("Login View (Fixed Size)")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.simulate_login)
        layout.addWidget(login_button)
        
    def simulate_login(self):
        print("Simulating login")
        self.main_window.show_view("MainMenu")
        
    def sizeHint(self):
        return QSize(400, 500)

class MainMenuView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        label = QLabel("Main Menu View (Resizable)")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        logout_button = QPushButton("Logout")
        logout_button.clicked.connect(self.simulate_logout)
        layout.addWidget(logout_button)
        
        invalidate_button = QPushButton("Invalidate Session")
        invalidate_button.clicked.connect(self.invalidate_session)
        layout.addWidget(invalidate_button)
        
    def simulate_logout(self):
        print("Simulating logout")
        self.main_window.show_view("Login")
        
    def invalidate_session(self):
        print("Simulating session invalidation")
        self.main_window.handle_session_invalidated()
        
    def sizeHint(self):
        return QSize(800, 600)

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Window Size Test")
        self._last_window_size = None
        
        # Initialize stacked widget
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)
        
        # Create views
        self.views = {}
        self.controllers = {}
        self.current_view_name = None
        
        # Create views
        self.views["Login"] = LoginView(self)
        self.views["MainMenu"] = MainMenuView(self)
        
        # Add views to stacked widget
        self.stacked_widget.addWidget(self.views["Login"])
        self.stacked_widget.addWidget(self.views["MainMenu"])
        
        # Show login view by default
        self.show_view("Login")
        
    def show_view(self, view_name):
        """Show the specified view and handle view transitions"""
        if view_name not in self.views:
            print(f"View '{view_name}' not found")
            return
            
        # Get the current and new views
        old_view_name = self.current_view_name
        new_view = self.views[view_name]
        
        # Update current view
        self.current_view_name = view_name
        
        # Show the new view
        self.stacked_widget.setCurrentWidget(new_view)
        
        # Handle window size based on view
        try:
            # Preserve the window size for non-login views
            if view_name != "Login":
                # Remember the current size for non-login views
                if hasattr(self, '_last_window_size') and self._last_window_size:
                    # Restore the last window size
                    self.resize(self._last_window_size)
                    # Allow resizing
                    self.setMinimumSize(0, 0)
                    self.setMaximumSize(16777215, 16777215)
                else:
                    # Set a default size if no previous size
                    self.resize(800, 600)
                print(f"Set resizable window size: {self.width()}x{self.height()}")
            else:
                # For login view, store current size if not login
                if old_view_name and old_view_name != "Login":
                    self._last_window_size = self.size()
                    print(f"Stored window size: {self._last_window_size.width()}x{self._last_window_size.height()}")
                
                # Set fixed size for login view
                login_size = new_view.sizeHint()
                if login_size.isValid():
                    self.setFixedSize(login_size)
                    print(f"Set fixed login size: {login_size.width()}x{login_size.height()}")
                else:
                    # Fallback size for login
                    self.setFixedSize(450, 550)
                    print("Set fallback fixed login size: 450x550")
        except Exception as e:
            print(f"Error handling window size: {e}")
            import traceback
            traceback.print_exc()
            
        print(f"Switched to view: {view_name}")
        
    def handle_session_invalidated(self):
        """Handle session invalidation by showing a dialog and redirecting to login"""
        print("Session invalidated! Handling in TestWindow")
        
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Session Invalidated")
        msg.setInformativeText("Your session has been invalidated. You will be logged out.")
        msg.setWindowTitle("Session Ended")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        
        # Schedule logout after a short delay
        QTimer.singleShot(1000, self.logout_user_and_show_login)
        print("Scheduled logout after dialog")
        
    def logout_user_and_show_login(self):
        """Logout the user and show the login view"""
        print("Logging out user and showing login view")
        self.show_view("Login")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_()) 