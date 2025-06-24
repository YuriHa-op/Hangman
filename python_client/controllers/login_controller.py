import threading
import time
from PyQt5.QtCore import QObject, pyqtSlot
import LoginModule
import subprocess
import sys
import os

class BaseController:
    # Class-level flag to track if session invalidation is already being handled
    _session_invalidation_in_progress = False
    
    def __init__(self, model, view):
        self.model = model
        self.view = view # This will be the specific Qt view (e.g., QtLoginView)
        self.polling_thread = None
        self.is_polling = False
        self.session_check_thread = None
        self.is_session_checking = False
        self.session_invalidated = False
        self._session_check_thread = None
        self._session_check_running = False

    def get_username(self):
        return self.model.get_username()

    def logout(self):
        try:
            # Stop any active polling
            self.stop_polling()
            
            # Stop session checking
            self.stop_session_checking()
            
            # Perform logout
            self.model.logout()
            
            # Navigate back to login view
            if hasattr(self.view, 'main_window'):
                self.view.main_window.logout_user_and_show_login()
        except Exception as e:
            print(f"Error during logout: {e}")

    def go_back_to_main_menu(self):
        # Stop any active polling
        self.stop_polling()
        
        # Navigate to main menu
        if hasattr(self.view, 'main_window'):
            self.view.main_window.show_view("MainMenu")

    def exit_application(self):
        try:
            # First, stop all polling threads
            self.stop_polling()
            self.stop_session_checking()
            
            # Perform logout if logged in
            if self.model.get_username():
                try:
                    self.model.logout()
                except Exception as e:
                    print(f"Error during logout on exit: {e}")
            
            # Close the application
            if hasattr(self.view, 'main_window'):
                self.view.main_window.close()
        except Exception as e:
            print(f"Error during application exit: {e}")
            # Force exit as a last resort
            import sys
            sys.exit(0)

    def on_show(self):
        """Called when the controller's associated view is shown.
        Override in subclasses to perform actions when the view becomes active,
        like starting polling.
        """
        # Start session checking if not already running
        self.start_session_checking()

    def on_hide(self):
        """Called when the controller's associated view is hidden.
        Override in subclasses to perform actions when the view becomes inactive,
        like stopping polling.
        """
        # Stop polling when view is hidden
        self.stop_polling()

    def stop_polling(self):
        """Stop any active polling threads"""
        self.is_polling = False
        if self.polling_thread and self.polling_thread.is_alive():
            self.polling_thread.join(1.0)  # Wait up to 1 second for thread to end
            self.polling_thread = None

    def start_session_checking(self, interval=5.0):
        """Start a background thread to periodically check if the session is still valid"""
        # Stop any existing thread first
        self.stop_session_checking()
        
        # Import required modules
        import threading
        import time
        
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
            import threading
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
        """Background thread worker to check if session has been invalidated by another login"""
        print(f"Session invalidation check worker started with interval {interval}s")
        self._session_check_running = True
        import time
        
        while self._session_check_running:
            try:
                # If session invalidation is already being handled, stop checking
                if BaseController._session_invalidation_in_progress:
                    print("Session invalidation already in progress, stopping check worker")
                    self._session_check_running = False
                    break
                
                # Get username and session ID
                username = self.model.get_username()
                session_id = self.model.get_session_id()
                
                if not username or not session_id:
                    # No active session, no need to check
                    time.sleep(interval)
                    continue
                    
                # Check if session is still valid (may have been invalidated by another login)
                result = self.model.keep_alive()
                
                if not result and not BaseController._session_invalidation_in_progress:
                    print(f"Session invalid: session check returned False for {username}")
                    # Session is invalid, handle it
                    self._session_check_running = False
                    self.handle_session_invalidated()
                    break
                    
            except Exception as e:
                print(f"Error in session check: {e}")
                # Don't break on errors, just continue checking
            
            # Sleep for the specified interval
            time.sleep(interval)
            
        print("Session invalidation check worker stopped")

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
        elif hasattr(self.view, 'parent') and self.view.parent():
            main_window = self.view.parent()
            
        if main_window is None:
            print("Warning: Could not find main window for session invalidation")
            # Reset the flag since we're not proceeding
            BaseController._session_invalidation_in_progress = False
            return
            
        # Use QTimer.singleShot to ensure this runs on the main thread
        from PyQt5.QtCore import QTimer
        print("Using QTimer.singleShot to handle session invalidation")
        
        # If main_window has handle_session_invalidated method, use it directly
        if hasattr(main_window, 'handle_session_invalidated'):
            print("Using main_window.handle_session_invalidated directly")
            QTimer.singleShot(0, main_window.handle_session_invalidated)
            # The main window will handle resetting the flag after logout
        else:
            # Fall back to our own implementation
            print("Main window doesn't have handle_session_invalidated, using fallback")
            QTimer.singleShot(0, lambda: self._show_session_invalidated_dialog(main_window))

    def _show_session_invalidated_dialog(self, main_window):
        """Helper method to show the session invalidated dialog on the main thread"""
        try:
            print("Executing session invalidation on main thread")
            
            # Debug main_window object
            print(f"Main window type: {type(main_window)}")
            print(f"Main window attributes: {dir(main_window)}")
            
            # Force the application to process events before showing the dialog
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()
            
            # Show dialog directly without using handle_session_invalidated method
            print("Showing session invalidated dialog directly")
            
            # Get current view
            current_view_name = main_window.current_view_name
            print(f"Current view: {current_view_name}")
            
            # Debug available views
            print(f"Available views: {list(main_window.views.keys()) if hasattr(main_window, 'views') else 'No views attribute'}")
            
            dialog_shown = False
            
            if current_view_name and hasattr(main_window, 'views') and current_view_name in main_window.views:
                current_view = main_window.views[current_view_name]
                print(f"Current view object type: {type(current_view)}")
                print(f"Current view attributes: {dir(current_view)}")
                
                if hasattr(current_view, 'show_session_invalidated_dialog'):
                    print(f"Showing session invalidated dialog from {current_view_name} view")
                    try:
                        current_view.show_session_invalidated_dialog("Your session has been invalidated")
                        dialog_shown = True
                        print("Dialog show method called successfully")
                    except Exception as e:
                        print(f"Error showing dialog from current view: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"View {current_view_name} does not have show_session_invalidated_dialog method")
                    # Try login view as fallback
                    if 'Login' in main_window.views and hasattr(main_window.views['Login'], 'show_session_invalidated_dialog'):
                        print("Showing session invalidated dialog from Login view")
                        try:
                            main_window.views['Login'].show_session_invalidated_dialog("Your session has been invalidated")
                            dialog_shown = True
                            print("Dialog show method called successfully from Login view")
                        except Exception as e:
                            print(f"Error showing dialog from Login view: {e}")
                            import traceback
                            traceback.print_exc()
            else:
                print("No current view or view not found in main_window.views")
                # Try login view as fallback
                if hasattr(main_window, 'views') and 'Login' in main_window.views and hasattr(main_window.views['Login'], 'show_session_invalidated_dialog'):
                    print("Showing session invalidated dialog from Login view")
                    try:
                        main_window.views['Login'].show_session_invalidated_dialog("Your session has been invalidated")
                        dialog_shown = True
                        print("Dialog show method called successfully from Login view")
                    except Exception as e:
                        print(f"Error showing dialog from Login view: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    print("Could not find Login view or it doesn't have show_session_invalidated_dialog method")
                    # Last resort: try to create and show dialog directly
                    try:
                        print("Attempting to create and show dialog directly")
                        from PyQt5.QtWidgets import QMessageBox
                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText("Session Invalidated")
                        msg.setInformativeText("Your session has been invalidated. You will be logged out.")
                        msg.setWindowTitle("Session Ended")
                        msg.setStandardButtons(QMessageBox.Ok)
                        msg.setModal(True)
                        msg.show()
                        print("Direct dialog created and shown")
                        dialog_shown = True
                    except Exception as e:
                        print(f"Error showing direct dialog: {e}")
                        import traceback
                        traceback.print_exc()
            
            # Force application to process events again
            QApplication.processEvents()
            
            # Always logout and show login view after a short delay
            from PyQt5.QtCore import QTimer
            print("Scheduling logout and login view display")
            QTimer.singleShot(2000, lambda: self._logout_and_reset_flag(main_window))
            print("Scheduled logout and show login view after dialog")
            
        except Exception as e:
            print(f"Error showing session invalidated dialog: {e}")
            import traceback
            traceback.print_exc()
            
            # Reset the flag since we encountered an error
            BaseController._session_invalidation_in_progress = False
            
            # Fallback: just logout and show login view
            try:
                main_window.logout_user_and_show_login(skip_server_logout=True)
            except Exception as e2:
                print(f"Error in fallback logout: {e2}")
                traceback.print_exc()
                
    def _logout_and_reset_flag(self, main_window):
        """Helper method to logout and reset the session invalidation flag"""
        try:
            # Logout and show login view
            main_window.logout_user_and_show_login(skip_server_logout=True)
        finally:
            # Always reset the flag, even if logout fails
            BaseController._session_invalidation_in_progress = False
            print("Session invalidation handling completed, flag reset")

    def handle_exit_app(self):
        """Delegates application exit to the main app view."""
        self.exit_application()

class LoginController(BaseController):
    def __init__(self, model, view):
        super().__init__(model, view)
        self.view = view

    def _launch_main_app(self, username, session_id):
        """Launches the main Tkinter game application in a new process."""
        try:
            # Assuming main_game_app.py is in the python_client directory
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # Path to python_client/main_game_app.py
            main_app_path = os.path.join(base_dir, '..', 'main_game_app.py')

            # We need to find the python executable
            python_executable = sys.executable
            
            command = [python_executable, main_app_path, username, session_id]
            
            print(f"Launching main app with command: {' '.join(command)}")
            
            # On Windows, launch the main game in a new console window
            # so we can see any errors that cause it to close prematurely.
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NEW_CONSOLE
            
            subprocess.Popen(command, creationflags=creation_flags)
            
            # Close the login window
            if hasattr(self.view, 'main_window') and self.view.main_window:
                self.view.main_window.close()
        except Exception as e:
            self.view.show_message("Error", f"Could not launch the main application: {e}")
            print(f"Error launching main app: {e}")

    def login(self, username, password):
        """Attempt to login with the provided credentials"""
        try:
            # Completely reset any session invalidation state
            try:
                from controllers.base_controller import BaseController
                
                # Reset the flag
                if hasattr(BaseController, '_session_invalidation_in_progress'):
                    BaseController._session_invalidation_in_progress = False
                    print("Reset session invalidation flag before login")
                
                # Also reset the session_invalidated flag in all controllers
                if hasattr(self.view, 'main_window') and hasattr(self.view.main_window, 'controllers'):
                    for controller_name, controller in self.view.main_window.controllers.items():
                        if hasattr(controller, 'session_invalidated'):
                            controller.session_invalidated = False
                    print("Reset session_invalidated flags in all controllers")
                
                # Cancel any pending session invalidation timers
                # We can't directly find all timers, but we can try to stop any timers in the main window
                if hasattr(self.view, 'main_window'):
                    from PyQt5.QtCore import QTimer
                    main_window = self.view.main_window
                    
                    # Find all QTimer children of the main window
                    timers = main_window.findChildren(QTimer)
                    for timer in timers:
                        try:
                            timer.stop()
                        except Exception as e:
                            print(f"Error stopping timer: {e}")
                    
                    print(f"Stopped {len(timers)} timers in main window")
                
            except Exception as e:
                print(f"Error resetting session invalidation state: {e}")
                import traceback
                traceback.print_exc()
                
            # Attempt login
            result = self.model.login(username, password)
            
            if result:
                # Login successful
                self._launch_main_app(username, self.model.session_id)
                return True
            else:
                # Login failed
                self.view.show_login_error("Invalid username or password")
                return False
                
        except LoginModule.AlreadyLoggedInException:
            # Show force login dialog
            if self.view.show_force_login_dialog():
                return self.force_login(username, password)
            return False
        except Exception as e:
            # Other error
            self.view.show_login_error(f"Login error: {str(e)}")
            return False
    
    def force_login(self, username, password):
        """Force login by closing any existing session"""
        try:
            # Completely reset any session invalidation state
            try:
                from controllers.base_controller import BaseController
                
                # Reset the flag
                if hasattr(BaseController, '_session_invalidation_in_progress'):
                    BaseController._session_invalidation_in_progress = False
                    print("Reset session invalidation flag before force login")
                
                # Also reset the session_invalidated flag in all controllers
                if hasattr(self.view, 'main_window') and hasattr(self.view.main_window, 'controllers'):
                    for controller_name, controller in self.view.main_window.controllers.items():
                        if hasattr(controller, 'session_invalidated'):
                            controller.session_invalidated = False
                    print("Reset session_invalidated flags in all controllers")
                
                # Cancel any pending session invalidation timers
                if hasattr(self.view, 'main_window'):
                    from PyQt5.QtCore import QTimer
                    main_window = self.view.main_window
                    
                    # Find all QTimer children of the main window
                    timers = main_window.findChildren(QTimer)
                    for timer in timers:
                        try:
                            timer.stop()
                        except Exception as e:
                            print(f"Error stopping timer: {e}")
                    
                    print(f"Stopped {len(timers)} timers in main window")
                
            except Exception as e:
                print(f"Error resetting session invalidation state: {e}")
                import traceback
                traceback.print_exc()
                
            # Attempt force login
            result = self.model.force_login(username, password)
            
            if result:
                # Force login successful
                self._launch_main_app(username, self.model.session_id)
                return True
            else:
                # Force login failed
                self.view.show_login_error("Force login failed. Please try again.")
                return False
                
        except Exception as e:
            # Other error
            self.view.show_login_error(f"Force login error: {str(e)}")
            return False

    def create_account(self, username, password):
        if not username or not password:
            self.view.show_creation_error("Username and password cannot be empty")
            return
            
        # Add validation for username and password length
        if len(username) > 10:
            self.view.show_creation_error("Username must be at most 10 characters")
            return
            
        if len(password) > 15:
            self.view.show_creation_error("Password must be at most 15 characters")
            return

        try:
            success = self.model.create_player(username, password)
            if success:
                self.view.show_creation_success()
                self.view.clear_inputs()
            else:
                self.view.show_creation_error("Username already exists. Please choose another.")
        except Exception as e:
            self.view.show_creation_error(f"Error connecting to server: {str(e)}")

    def switch_to_create_account(self):
        # Handle UI change to show create account form
        pass

    def switch_to_login(self):
        # Handle UI change to show login form
        pass

    # The handle_exit_app is inherited from BaseController, which calls app_view.handle_exit()