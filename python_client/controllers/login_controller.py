from .base_controller import BaseController
# from ..views.login_view import LoginView # Old Tkinter import
import LoginModule

class LoginController(BaseController):
    def __init__(self, model, view):
        super().__init__(model, view)
        self.view = view

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
                self.view.navigate_to_main_menu()
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
                self.view.navigate_to_main_menu()
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