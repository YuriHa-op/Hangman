class BaseController:
    def __init__(self, model, view):
        self.model = model
        self.view = view # This will be the specific Qt view (e.g., QtLoginView)
        self.polling_active = False

    def get_username(self):
        return self.model.get_username()

    def logout(self):
        current_username = self.model.get_username()
        if current_username:
            print(f"Logging out user: {current_username}")
            self.model.logout()
            if hasattr(self.view, 'main_window') and hasattr(self.view.main_window, 'show_view'):
                 self.view.main_window.show_view("Login") # Navigate to Login after logout
        else:
            print("No user currently logged in.")

    def go_back_to_main_menu(self):
        if hasattr(self.view, 'main_window') and hasattr(self.view.main_window, 'show_view'):
            self.view.main_window.show_view("MainMenu")
        else:
            print("DEBUG: Cannot go_back_to_main_menu. main_window or show_view not available.")

    def exit_application(self):
        print("BaseController: Attempting to exit application...")
        # Ensure logout before exiting
        if self.model.get_username():
            self.model.logout()
            print(f"User {self.model.get_username()} logged out during exit.")
            # Model username should be None now, but to be safe, we pass the prior username or rely on model's internal state for logout.

        if hasattr(self.view, 'main_window') and hasattr(self.view.main_window, 'close'):
            self.view.main_window.close() 
        elif hasattr(self.view, 'close'): 
            self.view.close()
        else:
            from PyQt5.QtWidgets import QApplication
            QApplication.instance().quit()
            print("DEBUG: Exited application using QApplication.instance().quit()")

    def on_show(self):
        """Called when the controller's associated view is shown.
        Override in subclasses to perform actions when the view becomes active,
        like starting polling.
        """
        pass

    def on_hide(self):
        """Called when the controller's associated view is hidden.
        Override in subclasses to perform actions when the view becomes inactive,
        like stopping polling.
        """
        self.polling_active = False # Default behavior: stop polling when hidden

    def stop_polling(self):
        """Placeholder for stopping polling.
        Subclasses that implement polling should override this.
        """
        self.polling_active = False
        # print(f"{self.__class__.__name__} polling stopped.")

    def handle_exit_app(self):
        """Delegates application exit to the main app view."""
        if hasattr(self.view, 'handle_exit'):
            self.view.handle_exit()
        else:
            # Fallback if handle_exit is not on view (e.g. direct sys.exit)
            # This part should ideally be centralized in HangmanApp.
            print("Attempting to exit application...")
            if self.model.get_username():
                try:
                    self.model.logout()
                except Exception as e:
                    print(f"Error during logout on exit: {e}")
            if hasattr(self.view, 'destroy'):
                self.view.destroy()
            import sys
            sys.exit(0) 