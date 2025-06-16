from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDialog, QLabel, QStackedWidget
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
        self.setWindowModality(Qt.ApplicationModal)
        
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
        
    def showEvent(self, event):
        """Center the dialog and add animations when shown"""
        super().showEvent(event)
        
        print("Dialog show event triggered")
        
        # Get parent's geometry or center on screen if no parent
        if self.parent():
            parent_pos = self.parent().mapToGlobal(self.parent().rect().center())
        else:
            screen_geometry = QApplication.desktop().screenGeometry()
            parent_pos = screen_geometry.center()
        
        # Center dialog on parent
        x = parent_pos.x() - (self.width() // 2)
        y = parent_pos.y() - (self.height() // 2)
        self.move(x, y)
        
        # Force the application to process events
        QApplication.processEvents()
        
        print("Dialog should now be visible")

class LoginView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("Login View")
        layout.addWidget(label)
        
    def show_session_invalidated_dialog(self, reason=""):
        """Show a dialog when session is invalidated by another login"""
        print("Showing session invalidated dialog in Login view")
        try:
            # Force the application to process events before showing the dialog
            QApplication.processEvents()
            
            # Create and show the dialog
            dialog = SessionInvalidatedDialog(self, reason)
            
            print("Session invalidated dialog created in Login view, about to show")
            
            # Show the dialog and wait for it to close
            result = dialog.exec_()
            
            print("Session invalidated dialog closed with result:", result)
            
            # Force the application to process events again
            QApplication.processEvents()
            
            return result == QDialog.Accepted
        except Exception as e:
            print(f"Error showing session invalidated dialog: {e}")
            import traceback
            traceback.print_exc()
            return False

class MainMenuView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        label = QLabel("Main Menu View")
        layout.addWidget(label)
        
        invalidate_button = QPushButton("Simulate Session Invalidation")
        invalidate_button.clicked.connect(self.simulate_invalidation)
        layout.addWidget(invalidate_button)
        
        thread_button = QPushButton("Simulate Invalidation in Thread")
        thread_button.clicked.connect(self.simulate_thread_invalidation)
        layout.addWidget(thread_button)
        
    def simulate_invalidation(self):
        """Simulate session invalidation"""
        print("Simulating session invalidation")
        self.main_window.handle_session_invalidated()
        
    def simulate_thread_invalidation(self):
        """Simulate session invalidation in a background thread"""
        print("Starting background thread for session invalidation")
        thread = threading.Thread(target=self.background_task)
        thread.daemon = True
        thread.start()
        
    def background_task(self):
        """Background task that will invalidate session after a delay"""
        print("Background thread started")
        # Simulate some work
        time.sleep(2)
        
        print("Background thread invalidating session")
        # Use QTimer.singleShot to invalidate session on the main thread
        QTimer.singleShot(0, self.main_window.handle_session_invalidated)
        
    def show_session_invalidated_dialog(self, reason=""):
        """Show a dialog when session is invalidated by another login"""
        print("Showing session invalidated dialog in MainMenu view")
        try:
            # Force the application to process events before showing the dialog
            QApplication.processEvents()
            
            # Create and show the dialog
            dialog = SessionInvalidatedDialog(self, reason)
            
            print("Session invalidated dialog created in MainMenu view, about to show")
            
            # Show the dialog and wait for it to close
            result = dialog.exec_()
            
            print("Session invalidated dialog closed with result:", result)
            
            # Force the application to process events again
            QApplication.processEvents()
            
            return result == QDialog.Accepted
        except Exception as e:
            print(f"Error showing session invalidated dialog: {e}")
            import traceback
            traceback.print_exc()
            return False

class TestMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Session Invalidation Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create views
        self.views = {}
        self.current_view_name = None
        
        # Initialize stacked widget
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)
        
        # Create views
        self.login_view = LoginView(self)
        self.main_menu_view = MainMenuView(self)
        
        # Add views to stacked widget
        self.views["Login"] = self.login_view
        self.views["MainMenu"] = self.main_menu_view
        self.stacked_widget.addWidget(self.login_view)
        self.stacked_widget.addWidget(self.main_menu_view)
        
        # Show main menu by default
        self.show_view("MainMenu")
        
    def show_view(self, view_name):
        """Show the specified view"""
        if view_name in self.views:
            self.current_view_name = view_name
            self.stacked_widget.setCurrentWidget(self.views[view_name])
            self.setWindowTitle(f"Session Invalidation Test - {view_name}")
        else:
            print(f"Error: View '{view_name}' not found")
            
    @pyqtSlot()
    def handle_session_invalidated(self):
        """Handle when the session is invalidated"""
        print("Session invalidated! Handling in MainWindow")
        
        # Get the current view
        if self.current_view_name and self.current_view_name in self.views:
            current_view = self.views[self.current_view_name]
            print(f"Current view: {self.current_view_name}")
            
            # Show the session invalidated dialog
            if hasattr(current_view, 'show_session_invalidated_dialog'):
                print(f"Showing session invalidated dialog in {self.current_view_name} view")
                current_view.show_session_invalidated_dialog("Test Invalidation")
            elif hasattr(self.views.get('Login'), 'show_session_invalidated_dialog'):
                print("Showing session invalidated dialog in Login view")
                self.views['Login'].show_session_invalidated_dialog("Test Invalidation")
        else:
            # No current view, just use login view
            print("No current view, using Login view for session invalidated dialog")
            if hasattr(self.views.get('Login'), 'show_session_invalidated_dialog'):
                self.views['Login'].show_session_invalidated_dialog("Test Invalidation")
        
        # Logout and show login view
        print("Logging out user and showing login view")
        self.logout_user_and_show_login()
        
    def logout_user_and_show_login(self):
        """Logout the user and show the login view"""
        print("Logging out user and showing login view")
        self.show_view("Login")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestMainWindow()
    window.show()
    sys.exit(app.exec_()) 