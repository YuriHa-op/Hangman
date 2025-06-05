class BaseController:
    def __init__(self, app_view, model):
        self.app_view = app_view  # This will be the HangmanApp instance
        self.model = model
        self.polling_active = False # Common flag for polling

    def show_frame(self, frame_name):
        """Utility method to ask the main app view to switch frames."""
        self.app_view.show_frame(frame_name)

    def get_username(self):
        """Utility method to get the current username from the model."""
        return self.model.get_username()

    def on_show(self):
        """Called when the controller's associated view is shown.
        Subclasses should override this to start polling or load data.
        """
        pass

    def on_hide(self):
        """Called when the controller's associated view is hidden.
        Subclasses should override this to stop polling and clean up resources.
        """
        self.stop_polling() # Default behavior

    def stop_polling(self):
        """Placeholder for stopping polling.
        Subclasses that implement polling should override this.
        """
        self.polling_active = False
        # print(f"{self.__class__.__name__} polling stopped.")

    def handle_exit_app(self):
        """Delegates application exit to the main app view."""
        if hasattr(self.app_view, 'handle_exit'):
            self.app_view.handle_exit()
        else:
            # Fallback if handle_exit is not on app_view (e.g. direct sys.exit)
            # This part should ideally be centralized in HangmanApp.
            print("Attempting to exit application...")
            if self.model.get_username():
                try:
                    self.model.logout()
                except Exception as e:
                    print(f"Error during logout on exit: {e}")
            if hasattr(self.app_view, 'destroy'):
                self.app_view.destroy()
            import sys
            sys.exit(0) 