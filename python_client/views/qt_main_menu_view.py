from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt

class QtMainMenuView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        # self.controller = None # Will be set by MainWindow, if needed by this view directly
                                 # Currently, buttons are connected in MainWindow to controller methods.
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle('Hangman - Main Menu')
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel('Main Menu')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title_label)

        self.single_player_button = QPushButton('Single Player Game')
        # Connection now done in MainWindow: self.single_player_button.clicked.connect(main_menu_controller.start_single_player)
        self.single_player_button.setStyleSheet("padding: 10px; font-size: 16px;")
        layout.addWidget(self.single_player_button)

        self.multiplayer_button = QPushButton('Multiplayer Game')
        self.multiplayer_button.setStyleSheet("padding: 10px; font-size: 16px;")
        layout.addWidget(self.multiplayer_button)

        self.leaderboard_button = QPushButton('Leaderboard')
        self.leaderboard_button.setStyleSheet("padding: 10px; font-size: 16px;")
        layout.addWidget(self.leaderboard_button)

        self.match_history_button = QPushButton('Match History')
        self.match_history_button.setStyleSheet("padding: 10px; font-size: 16px;")
        layout.addWidget(self.match_history_button)

        self.logout_button = QPushButton('Logout')
        # Connection now done in MainWindow: self.logout_button.clicked.connect(self.main_window.logout_user_and_show_login)
        self.logout_button.setStyleSheet("padding: 10px; font-size: 16px; margin-top: 20px;")
        layout.addWidget(self.logout_button)

        self.setLayout(layout)
        self.setMinimumSize(400, 300)

    # def handle_logout(self): # This method is no longer directly connected here if MainWindow connects the button.
    #     print("Logout button clicked in QtMainMenuView")
    #     if hasattr(self.main_window, 'logout_user_and_show_login'):
    #         self.main_window.logout_user_and_show_login()
    #     else:
    #         if hasattr(self.main_window, 'model') and self.main_window.model:
    #             self.main_window.model.logout()
    #         self.main_window.show_view("Login")

    def set_welcome_message(self, username):
        # Placeholder for future use, e.g., a QLabel to display "Welcome, [username]!"
        pass 