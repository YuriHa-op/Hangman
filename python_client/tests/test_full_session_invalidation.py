from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QStackedWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
import sys
import threading
import time

# Mock classes to simulate the app structure
class BaseController:
    # Class-level flag to track if session invalidation is already being handled
    _session_invalidation_in_progress = False
    
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self._session_check_thread = None
        self._session_check_running = False
        
    def start_session_checking(self, interval=1.0):
        """Start a background thread to periodically check if the session is still valid"""
        # Stop any existing thread first
        self.stop_session_checking()
        
        # Start a new thread
        print(f"Starting session checking thread with interval {interval}s")
        self._session_check_thread = threading.Thread(
            target=self._session_check_worker, 
            args=(interval,),
            daemon=True
        )
        self._session_check_thread.start()
        
    def stop_session_checking(self):
        """Stop the session checking thread if it's running"""
        if hasattr(self, '_session_check_thread') and self._session_check_thread is not None:
            print("Stopping session checking thread")
            self._session_check_running = False
            
            # Only join the thread if it's not the current thread
            if self._session_check_thread != threading.current_thread():
                try:
                    # Set a short timeout to avoid blocking
                    self._session_check_thread.join(timeout=0.5)
                    if self._session_check_thread.is_alive():
                        print("Warning: Session check thread did not terminate within timeout")
                except Exception as e:
                    print(f"Error joining session check thread: {e}")
            else:
                print("Not joining session check thread as it is the current thread")
                
            self._session_check_thread = None
            
    def _session_check_worker(self, interval):
        """Background thread worker to check session validity"""
        print(f"Session check worker started with interval {interval}s")
        self._session_check_running = True
        
        while self._session_check_running:
            try:
                # If session invalidation is already being handled, stop checking
                if BaseController._session_invalidation_in_progress:
                    print("Session invalidation already in progress, stopping check worker")
                    self._session_check_running = False
                    break
                
                # Simulate session check
                result = self.model.keep_alive()
                print(f"Keepalive result: {result}")
                
                if not result and not BaseController._session_invalidation_in_progress:
                    print("Session invalid: keep_alive returned False")
                    # Session is invalid, handle it
                    self._session_check_running = False
                    self.handle_session_invalidated()
                    break
                    
            except Exception as e:
                print(f"Error in session check: {e}")
                # Don't break on errors, just continue checking
            
            # Sleep for the specified interval
            time.sleep(interval)
            
        print("Session check worker stopped")
        
    def handle_session_invalidated(self):
        """Handle when the session is invalidated"""
        # Check if session invalidation is already being handled
        if BaseController._session_invalidation_in_progress:
            print("Session invalidation already in progress, skipping duplicate handler")
            return
            
        # Set the flag to prevent multiple handlers
        BaseController._session_invalidation_in_progress = True
        
        print("Session invalidated! Handling in BaseController")
        
        # Stop the session checking thread
        self.stop_session_checking()
        
        # Get the main window
        main_window = None
        if hasattr(self.view, 'main_window'):
            main_window = self.view.main_window
            
        if main_window is None:
            print("Warning: Could not find main window for session invalidation")
            # Reset the flag since we're not proceeding
            BaseController._session_invalidation_in_progress = False
            return
            
        # Use QTimer.singleShot to ensure this runs on the main thread
        print("Using QTimer.singleShot to handle session invalidation")
        
        # If main_window has handle_session_invalidated method, use it directly
        if hasattr(main_window, 'handle_session_invalidated'):
            print("Using main_window.handle_session_invalidated directly")
            QTimer.singleShot(0, main_window.handle_session_invalidated)
        else:
            # Fall back to our own implementation
            print("Main window doesn't have handle_session_invalidated, using fallback")
            QTimer.singleShot(0, lambda: self._show_session_invalidated_dialog(main_window))

class MockModel:
    def __init__(self):
        self.session_valid = True
        self.username = "test_user"
        self.session_id = "test_session_id"
        
    def get_username(self):
        return self.username
        
    def get_session_id(self):
        return self.session_id
        
    def keep_alive(self):
        return self.session_valid
        
    def logout(self):
        print("Model: Logging out")
        self.session_valid = False
        self.username = None
        self.session_id = None
        
    def end_game_session(self):
        print("Model: Ending game session")

class LoginView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("Login View")
        layout.addWidget(label)
        
        # Add button to simulate login
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.simulate_login)
        layout.addWidget(login_button)
        
    def simulate_login(self):
        print("Simulating login")
        self.main_window.show_view("MainMenu")
        
    def show_session_invalidated_dialog(self, reason=""):
        """Show a dialog when session is invalidated"""
        print("Showing session invalidated dialog in Login view")
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Session Invalidated")
        msg.setInformativeText(f"Your session has been invalidated: {reason}")
        msg.setWindowTitle("Session Ended")
        msg.setStandardButtons(QMessageBox.Ok)
        print("Session invalidated dialog created in Login view, about to show")
        result = msg.exec_()
        print("Session invalidated dialog closed with result:", result)
        return result == QMessageBox.Ok

class MainMenuView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        label = QLabel("Main Menu View")
        layout.addWidget(label)
        
        # Add button to invalidate session
        invalidate_button = QPushButton("Invalidate Session")
        invalidate_button.clicked.connect(self.invalidate_session)
        layout.addWidget(invalidate_button)
        
    def invalidate_session(self):
        """Simulate session invalidation"""
        print("Simulating session invalidation")
        # Get the model from the controller
        controller = self.main_window.controllers.get("MainMenu")
        if controller and hasattr(controller, "model"):
            controller.model.session_valid = False
        
    def show_session_invalidated_dialog(self, reason=""):
        """Show a dialog when session is invalidated"""
        print("Showing session invalidated dialog in MainMenu view")
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Session Invalidated")
        msg.setInformativeText(f"Your session has been invalidated: {reason}")
        msg.setWindowTitle("Session Ended")
        msg.setStandardButtons(QMessageBox.Ok)
        print("Session invalidated dialog created in MainMenu view, about to show")
        result = msg.exec_()
        print("Session invalidated dialog closed with result:", result)
        return result == QMessageBox.Ok

class TestMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Session Invalidation Full Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize stacked widget
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)
        
        # Create views and controllers
        self.views = {}
        self.controllers = {}
        self.current_view_name = None
        
        # Create login view and controller
        self.views["Login"] = LoginView(self)
        self.stacked_widget.addWidget(self.views["Login"])
        
        # Create main menu view and controller
        self.views["MainMenu"] = MainMenuView(self)
        self.stacked_widget.addWidget(self.views["MainMenu"])
        
        # Create models and controllers
        login_model = MockModel()
        main_menu_model = MockModel()
        
        self.controllers["Login"] = BaseController(login_model, self.views["Login"])
        self.controllers["MainMenu"] = BaseController(main_menu_model, self.views["MainMenu"])
        
        # Show login view by default
        self.show_view("Login")
        
    def show_view(self, view_name):
        """Show the specified view"""
        if view_name in self.views:
            old_view_name = self.current_view_name
            self.current_view_name = view_name
            
            # Stop session checking in old view
            if old_view_name and old_view_name in self.controllers:
                self.controllers[old_view_name].stop_session_checking()
                
            # Show the new view
            self.stacked_widget.setCurrentWidget(self.views[view_name])
            self.setWindowTitle(f"Session Invalidation Test - {view_name}")
            
            # Start session checking in new view if it's not Login
            if view_name != "Login" and view_name in self.controllers:
                self.controllers[view_name].start_session_checking(1.0)
        else:
            print(f"Error: View '{view_name}' not found")
            
    @pyqtSlot()
    def handle_session_invalidated(self):
        """Handle session invalidation by showing a dialog and redirecting to login"""
        print("Session invalidated! Handling in MainWindow")
        
        try:
            # Force the application to process events
            QApplication.processEvents()
            
            # Get the current view
            current_view_name = self.current_view_name
            print(f"Current view in MainWindow: {current_view_name}")
            
            # Flag to track if dialog was shown
            dialog_shown = False
            
            # Try to show dialog from current view
            if current_view_name and current_view_name in self.views:
                current_view = self.views[current_view_name]
                if hasattr(current_view, 'show_session_invalidated_dialog'):
                    print(f"Showing session invalidated dialog from {current_view_name} view")
                    try:
                        current_view.show_session_invalidated_dialog("Your session has been invalidated")
                        dialog_shown = True
                        print(f"Dialog shown from {current_view_name} view")
                    except Exception as e:
                        print(f"Error showing dialog from current view: {e}")
                        import traceback
                        traceback.print_exc()
            
            # If dialog wasn't shown from current view, try login view
            if not dialog_shown and 'Login' in self.views:
                print("Trying to show dialog from Login view")
                try:
                    self.views['Login'].show_session_invalidated_dialog("Your session has been invalidated")
                    dialog_shown = True
                    print("Dialog shown from Login view")
                except Exception as e:
                    print(f"Error showing dialog from Login view: {e}")
                    import traceback
                    traceback.print_exc()
            
            # If still no dialog shown, create one directly
            if not dialog_shown:
                print("Creating session invalidated dialog directly")
                try:
                    from PyQt5.QtWidgets import QMessageBox
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Session Invalidated")
                    msg.setInformativeText("Your session has been invalidated. You will be logged out.")
                    msg.setWindowTitle("Session Ended")
                    msg.setStandardButtons(QMessageBox.Ok)
                    msg.exec_()
                    print("Direct dialog shown and closed")
                except Exception as e:
                    print(f"Error showing direct dialog: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Force events to process again
            QApplication.processEvents()
            
            # Schedule logout after a short delay
            QTimer.singleShot(1000, self.logout_user_and_show_login)
            print("Scheduled logout after dialog")
            
        except Exception as e:
            print(f"Error in handle_session_invalidated: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback: just logout
            self.logout_user_and_show_login()
            
    def logout_user_and_show_login(self):
        """Logout the user and show the login view"""
        try:
            print("Logging out user and showing login view")
            
            # Get the current controller
            current_controller = None
            if self.current_view_name in self.controllers:
                current_controller = self.controllers[self.current_view_name]
            
            # End any active game
            if current_controller and hasattr(current_controller.model, 'end_game_session'):
                try:
                    print("Ending active game session")
                    current_controller.model.end_game_session()
                except Exception as e:
                    print(f"Error ending game session: {e}")
            
            # Logout from the server
            if current_controller and hasattr(current_controller.model, 'logout'):
                try:
                    print("Logging out from server")
                    current_controller.model.logout()
                except Exception as e:
                    print(f"Error logging out: {e}")
            
            # Show the login view
            self.show_view('Login')
            
            # Reset the session invalidation flag
            BaseController._session_invalidation_in_progress = False
            print("Session invalidation flag reset")
        
        except Exception as e:
            print(f"Error in logout_user_and_show_login: {e}")
            import traceback
            traceback.print_exc()
            
            # Last resort: just show login view
            self.show_view('Login')
            BaseController._session_invalidation_in_progress = False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestMainWindow()
    window.show()
    sys.exit(app.exec_()) 