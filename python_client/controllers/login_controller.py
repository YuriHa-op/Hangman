from .base_controller import BaseController
# from ..views.login_view import LoginView # Old Tkinter import
from GameModule import AlreadyLoggedInException # Assuming GameModule is accessible

class LoginController(BaseController):
    def __init__(self, model, view):
        super().__init__(model, view)

    def login(self, username, password):
        try:
            if self.model.login(username, password):
                # self.view.master.master.master.show_frame("MainMenu") # Old Tkinter navigation
                # self.view.master.master.show_frame("MainMenu") # Old Tkinter navigation
                self.view.navigate_to_main_menu() # New PyQt5 navigation
            else:
                # self.view.show_error("Login failed. Please check your credentials.")
                self.view.show_login_error("Login failed. Please check your credentials.")
        except AlreadyLoggedInException as e:
            # Display a user-friendly message instead of the raw exception.
            self.view.show_login_error("This user is already logged in on another device.")
        except Exception as e:
            # print(f"An unexpected error occurred during login: {e}") # For debugging
            # self.view.show_error("An unexpected error occurred. Please try again.")
            self.view.show_login_error(f"An unexpected error occurred: {e}")

    def create_account(self, username, password):
        try:
            if self.model.create_player(username, password):
                # self.view.show_success("Account created successfully! You can now log in.")
                self.view.show_creation_success()
            else:
                # self.view.show_error("Account creation failed. Username might already exist.")
                self.view.show_creation_error("Account creation failed. Username might already exist.")
        except Exception as e: # Catching a broader exception for now
            # print(f"An unexpected error occurred during account creation: {e}") # For debugging
            # self.view.show_error("An unexpected error occurred during account creation.")
            self.view.show_creation_error(f"An unexpected error occurred: {e}")

    def switch_to_create_account(self):
        # This was specific to Tkinter structure, may not be needed or handled differently in PyQt
        # self.view.master.master.show_frame("CreateAccountView") 
        # In PyQt, often the same view handles both or it's a dialog.
        # For now, QtLoginView handles both inputs directly.
        pass

    def switch_to_login(self):
        # Similar to above, handled within QtLoginView or by switching widgets in MainWindow
        # self.view.master.master.show_frame("LoginView")
        pass

    # The handle_exit_app is inherited from BaseController, which calls app_view.handle_exit()
    # LoginView calls self.controller.handle_exit_app() 