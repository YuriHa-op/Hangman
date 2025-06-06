from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtCore import Qt
from PyQt5 import uic
import os

class QtMainMenuView(QWidget):
    def __init__(self, main_window=None):
        super().__init__(main_window)
        self.main_window = main_window
        
        # Load the UI file
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_main_menu_view.ui')
        uic.loadUi(ui_path, self)

        # Find buttons
        self.single_player_button = self.findChild(QPushButton, "single_player_button")
        self.multiplayer_button = self.findChild(QPushButton, "multiplayer_button")
        self.leaderboard_button = self.findChild(QPushButton, "leaderboard_button")
        self.match_history_button = self.findChild(QPushButton, "match_history_button")
        self.logout_button = self.findChild(QPushButton, "logout_button")

    def set_welcome_message(self, username):
        # Placeholder for future use, e.g., a QLabel to display "Welcome, [username]!"
        pass 