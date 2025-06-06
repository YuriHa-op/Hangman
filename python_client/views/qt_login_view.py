from PyQt5.QtWidgets import QWidget, QMessageBox, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from PyQt5 import uic
import os

class QtLoginView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window # To allow switching views
        self.login_controller = None # Will be set by MainWindow after instantiation
        
        # Get the absolute path to the .ui file
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_login_view.ui')
        uic.loadUi(ui_path, self)

        # Find widgets by their object names
        self.username_input = self.findChild(QLineEdit, 'username_input')
        self.password_input = self.findChild(QLineEdit, 'password_input')
        self.login_button = self.findChild(QPushButton, 'login_button')
        self.create_account_button = self.findChild(QPushButton, 'create_account_button')

        # Connect signals to slots
        self.login_button.clicked.connect(self.handle_login)
        self.create_account_button.clicked.connect(self.handle_create_account)

    def handle_login(self):
        if not self.login_controller:
            self.show_message("Error", "Login controller not initialized.")
            return
        username = self.username_input.text()
        password = self.password_input.text()
        if not username or not password:
            self.show_message('Error', 'Username and password cannot be empty.')
            return
        self.login_controller.login(username, password)

    def handle_create_account(self):
        if not self.login_controller:
            self.show_message("Error", "Login controller not initialized.")
            return
        username = self.username_input.text()
        password = self.password_input.text()
        if not username or not password:
            self.show_message('Error', 'Username and password cannot be empty for account creation.')
            return
        self.login_controller.create_account(username, password)

    def show_message(self, title, message, success=False):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information if success else QMessageBox.Warning)
        msg_box.exec_()

    def clear_inputs(self):
        self.username_input.clear()
        self.password_input.clear()

    def navigate_to_main_menu(self):
        # This method will be called by the controller upon successful login
        print("DEBUG: Navigating to main menu (placeholder)")
        # Example: self.main_window.show_main_menu() 
        # We'll implement this in MainWindow later
        self.show_message("Login Successful", "Welcome!", success=True)
        self.main_window.show_view("MainMenu")


    def show_login_error(self, message):
        self.show_message("Login Failed", message)

    def show_creation_success(self):
        self.show_message("Account Created", "Account created successfully! You can now log in.", success=True)
        self.clear_inputs()

    def show_creation_error(self, message):
        self.show_message("Account Creation Failed", message) 