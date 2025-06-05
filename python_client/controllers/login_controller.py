from .base_controller import BaseController
import GameModule # For GameModule.AlreadyLoggedInException

class LoginController(BaseController):
    def __init__(self, app_view, model):
        super().__init__(app_view, model)

    def handle_login(self, username, password):
        login_view = self.app_view.frames.get("Login")
        if not login_view: return # Should not happen

        if not username or not password:
            login_view.set_status("Username and password cannot be empty.")
            return
        try:
            if self.model.login(username, password):
                login_view.clear_entries()
                login_view.set_status("") # Clear status
                self.show_frame("MainMenu")
            else:
                login_view.set_status("Login failed. Check your credentials.")
        except GameModule.AlreadyLoggedInException as e:
            login_view.set_status(f"Error: {e.message if hasattr(e, 'message') else str(e)}")
        except Exception as e:
            login_view.set_status(f"Login error: {e}")

    def handle_create_account(self, username, password):
        login_view = self.app_view.frames.get("Login")
        if not login_view: return # Should not happen

        if not username or not password:
            login_view.set_status("Username and password cannot be empty for account creation.")
            return
        try:
            if self.model.create_player(username, password):
                login_view.set_status("Account created! You can now log in.", color="green")
                login_view.clear_entries()
            else:
                login_view.set_status("Account creation failed. Username may already exist.")
        except Exception as e:
            login_view.set_status(f"Creation error: {e}")

    # The handle_exit_app is inherited from BaseController, which calls app_view.handle_exit()
    # LoginView calls self.controller.handle_exit_app() 