from PyQt5.QtWidgets import QWidget, QLabel, QListWidget, QPushButton, QProgressBar, QDialog
from PyQt5.QtCore import QTimer, Qt
from PyQt5 import uic
import os

class MatchFoundDialog(QDialog):
    def __init__(self, countdown_seconds=5, parent=None):
        super().__init__(parent)
        self.seconds_left = countdown_seconds
        
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_multiplayer_match_found_dialog.ui')
        uic.loadUi(ui_path, self)

        self.countdown_label = self.findChild(QLabel, 'countdown_label')
        self.countdown_label.setText(f"Starting in {self.seconds_left}...")
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)

    def update_countdown(self):
        self.seconds_left -= 1
        if self.seconds_left > 0:
            self.countdown_label.setText(f"Starting in {self.seconds_left}...")
        else:
            self.timer.stop()
            self.accept()

class QtMultiplayerQueueView(QWidget):
    def __init__(self, main_window=None):
        super().__init__(main_window)
        self.main_window = main_window
        self.controller = None
        
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_multiplayer_queue_view.ui')
        uic.loadUi(ui_path, self)

        self.status_label = self.findChild(QLabel, 'status_label')
        self.players_list_widget = self.findChild(QListWidget, 'players_list_widget')
        self.countdown_progress_bar = self.findChild(QProgressBar, 'countdown_progress_bar')
        self.back_button = self.findChild(QPushButton, 'back_button')

        self.countdown_progress_bar.setRange(0, 100)
        self.countdown_progress_bar.setValue(0)
        
        self.back_button.clicked.connect(self.handle_back_to_menu)

    def set_controller(self, controller):
        self.controller = controller

    def update_lobby_state(self, lobby_state):
        if not lobby_state or lobby_state.get('state') == 'NOMATCH':
            self.status_label.setText("Disconnected from lobby.")
            self.players_list_widget.clear()
            self.countdown_progress_bar.setValue(0)
            self.countdown_progress_bar.setFormat("N/A")
            return

        players = lobby_state.get("players", [])
        max_players = lobby_state.get("maxPlayers", 8)
        self.status_label.setText(f"Waiting for players... ({len(players)}/{max_players})")
        
        self.players_list_widget.clear()
        self.players_list_widget.addItems(players)

        creation_time_ms = lobby_state.get("creationTime", 0)
        queue_time_sec = lobby_state.get("queueTimeSeconds", 30)
        
        if self.controller:
            self.controller.update_timer(creation_time_ms, queue_time_sec)

    def update_countdown(self, remaining_seconds, total_seconds):
        self.countdown_progress_bar.setRange(0, total_seconds)
        self.countdown_progress_bar.setValue(total_seconds - remaining_seconds)
        self.countdown_progress_bar.setFormat(f"{remaining_seconds} seconds remaining")

    def handle_back_to_menu(self):
        if self.controller:
            self.controller.leave_lobby_and_go_back()

    def clear_view(self):
        self.status_label.setText("Connecting to lobby...")
        self.players_list_widget.clear()
        self.countdown_progress_bar.setValue(0)
        self.countdown_progress_bar.setFormat("")
        
    def show_match_found_dialog(self):
        dialog = MatchFoundDialog(parent=self)
        dialog.exec_() 