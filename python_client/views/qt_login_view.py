from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

class QtLoginView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window # To allow switching views
        self.login_controller = None # Will be set by MainWindow after instantiation
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle('Login - Hangman')
        self.setGeometry(300, 300, 300, 200) # x, y, width, height

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20) # Add some padding
        layout.setSpacing(15) # Spacing between widgets

        # Title
        title_label = QLabel('Hangman Game Login')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Username
        self.username_label = QLabel('Username:')
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        # Password
        self.password_label = QLabel('Password:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter your password")
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        # Buttons
        button_layout = QHBoxLayout()
        self.login_button = QPushButton('Login')
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setStyleSheet("padding: 8px 15px; font-size: 14px;")

        self.create_account_button = QPushButton('Create Account')
        self.create_account_button.clicked.connect(self.handle_create_account)
        self.create_account_button.setStyleSheet("padding: 8px 15px; font-size: 14px;")
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.create_account_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

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