from .base_controller import BaseController

class MainMenuController(BaseController):
    def __init__(self, app_view, model):
        super().__init__(app_view, model)

    def handle_logout(self):
        try:
            self.model.logout()
        except Exception as e:
            print(f"Error during logout: {e}")
            # Optionally, show an error message to the user via a status bar if MainMenuView has one
            # or a popup, though typically logout errors are less critical to display prominently.
        self.show_frame("Login")

    # get_username() is inherited from BaseController for the welcome message in MainMenuView
    # show_frame() is inherited from BaseController for navigation buttons in MainMenuView 