from PyQt5.QtWidgets import QWidget, QMessageBox, QLineEdit, QPushButton, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFontDatabase, QPainter
from PyQt5 import uic
import os

class QtLoginView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.login_controller = None
        self._logo_pixmap = None
        self._background_pixmap = None
        self._stylesheet = ""

        # --- Dynamic Path Setup ---
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(base_dir, 'ui', 'qt_login_view.ui')
        style_path = os.path.join(base_dir, 'style', 'login.qss')
        assets_path = os.path.join(base_dir, 'assets')
        logo_path = os.path.join(assets_path, 'logos.png')
        font_path = os.path.join(base_dir, 'fonts', 'Minecraftia.ttf')
        background_path = os.path.join(assets_path, 'login.png')
        
        # --- Load Custom Font ---
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id < 0:
                print(f"Error loading font at: {font_path}")
        else:
            print(f"Font not found at: {font_path}")

        uic.loadUi(ui_path, self)
        
        if self.main_window:
            self.main_window.setFixedSize(900, 600)

        self.setAutoFillBackground(True)

        # --- Load and Apply Stylesheet Dynamically ---
        try:
            with open(style_path, 'r') as f:
                self._stylesheet = f.read().replace("{assets_path}", assets_path.replace("\\", "/"))
                self.setStyleSheet(self._stylesheet)
        except FileNotFoundError:
            print(f"Stylesheet not found at: {style_path}")
        except Exception as e:
            print(f"Error loading stylesheet: {e}")

        # Find widgets by their object names
        self.username_input = self.findChild(QLineEdit, 'username_input')
        self.password_input = self.findChild(QLineEdit, 'password_input')
        self.login_button = self.findChild(QPushButton, 'login_button')
        self.create_account_button = self.findChild(QPushButton, 'create_account_button')
        self.logo_label = self.findChild(QLabel, 'logo_label')

        # Load logo image
        if self.logo_label and os.path.exists(logo_path):
            self._logo_pixmap = QPixmap(logo_path)
            # Initial pixmap set is not needed here, resizeEvent will handle it
        elif not os.path.exists(logo_path):
            print(f"Logo not found at: {logo_path}")

        if os.path.exists(background_path):
            self._background_pixmap = QPixmap(background_path)
        else:
            print(f"Background image not found at: {background_path}")

        # Connect signals to slots
        self.login_button.clicked.connect(self.handle_login)
        self.create_account_button.clicked.connect(self.handle_create_account)

    def paintEvent(self, event):
        """Paint the background image, preserving aspect ratio."""
        if self._background_pixmap:
            painter = QPainter(self)
            target_rect = self.rect()
            
            # Scale pixmap to fill the target rect, cropping excess
            scaled_pixmap = self._background_pixmap.scaled(
                target_rect.size(), 
                Qt.KeepAspectRatioByExpanding, 
                Qt.SmoothTransformation
            )
            
            # Center the scaled pixmap
            point = target_rect.center() - scaled_pixmap.rect().center()
            painter.drawPixmap(point, scaled_pixmap)

        super().paintEvent(event)

    def resizeEvent(self, event):
        """This event is called whenever the widget is resized."""
        super().resizeEvent(event)
        # Recalculate and set the pixmap for the logo on resize
        if self.logo_label and self._logo_pixmap:
            # Scale the pixmap to the label's current size
            self.logo_label.setPixmap(self._logo_pixmap.scaled(
                self.logo_label.width(),
                self.logo_label.height(),
                Qt.KeepAspectRatio,
                Qt.FastTransformation  # Keeps pixel art sharp
            ))

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
        
        # Apply the full stylesheet to the dialog
        if self._stylesheet:
            msg_box.setStyleSheet(self._stylesheet)

        # Set text and icon after stylesheet to ensure they are not overridden
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information if success else QMessageBox.Warning)
        
        # Remove window controls (minimize, maximize, close)
        msg_box.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
            
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