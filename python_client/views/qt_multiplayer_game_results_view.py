import os
from PyQt5 import uic
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QAbstractItemView, QHeaderView, QDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class RoundResultWidget(QFrame):
    def __init__(self, round_info):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_round_result_widget.ui')
        uic.loadUi(ui_path, self)

        self.round_label = self.findChild(QLabel, 'round_label')
        self.winner_label = self.findChild(QLabel, 'winner_label')

        round_num = round_info.get("roundNumber", "N/A")
        word = round_info.get("word", "******")
        winner = round_info.get("winner", "No Winner")

        self.round_label.setText(f"<b>Round {round_num}:</b> {word}")
        self.winner_label.setText(f"<i>Winner: {winner}</i>")

class MatchDetailsDialog(QDialog):
    def __init__(self, details, parent=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_match_details_dialog.ui')
        uic.loadUi(ui_path, self)

        self.winner_label = self.findChild(QLabel, 'winner_label')
        self.players_list_label = self.findChild(QLabel, 'players_list_label')
        self.scroll_area = self.findChild(QScrollArea, 'scroll_area')
        self.rounds_layout = self.findChild(QVBoxLayout, 'rounds_layout')
        self.ok_button = self.findChild(QPushButton, 'ok_button')
        
        self.winner_label.setText(f"Overall Winner: {details.get('overallWinner', 'None')}")
        self.players_list_label.setText(f"<b>Players:</b> {', '.join(details.get('players', []))}")

        for round_info in details.get('rounds', []):
            self.rounds_layout.addWidget(RoundResultWidget(round_info))

        self.ok_button.clicked.connect(self.accept)

class QtMultiplayerGameResultsView(QWidget):
    def __init__(self, main_window=None):
        super().__init__(main_window)
        self.main_window = main_window
        self.controller = None
        self.details_dialog = None
        self.match_details = None

        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_multiplayer_game_results_view.ui')
        uic.loadUi(ui_path, self)

        self.header_label = self.findChild(QLabel, 'header_label')
        self.table = self.findChild(QTableWidget, 'table')
        self.view_details_button = self.findChild(QPushButton, 'view_details_button')
        self.back_button = self.findChild(QPushButton, 'back_button')

        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        self.view_details_button.clicked.connect(self.show_details_dialog)
        self.back_button.clicked.connect(self.back_to_menu)

    def set_controller(self, controller):
        self.controller = controller

    def back_to_menu(self):
        if self.controller:
            self.controller.back_to_main_menu()

    def update_scoreboard(self, ranked_players, details):
        print("[DEBUG] update_scoreboard called with:")
        print("ranked_players:", ranked_players)
        print("details:", details)
        try:
            self.table.setRowCount(len(ranked_players))
            self.match_details = details
            self.view_details_button.setEnabled(bool(details))

            for row, player_data in enumerate(ranked_players):
                rank_item = QTableWidgetItem(str(player_data.get("rank", "?")))
                rank_item.setTextAlignment(Qt.AlignCenter)
                player_item = QTableWidgetItem(str(player_data.get("name", "?")))
                score_item = QTableWidgetItem(str(player_data.get("score", "?")))
                score_item.setTextAlignment(Qt.AlignCenter)

                self.table.setItem(row, 0, rank_item)
                self.table.setItem(row, 1, player_item)
                self.table.setItem(row, 2, score_item)
        except Exception as e:
            print("[ERROR] Exception in update_scoreboard:", e)
            import traceback
            traceback.print_exc()

    def show_details_dialog(self):
        if not self.match_details:
            return
        if self.details_dialog:
            self.details_dialog.close()
        self.details_dialog = MatchDetailsDialog(self.match_details, self)
        self.details_dialog.finished.connect(self._clear_details_dialog)
        self.details_dialog.show()

    def _clear_details_dialog(self, result):
        self.details_dialog = None

    def reset_view(self):
        self.table.setRowCount(0)
        self.match_details = None
        self.view_details_button.setEnabled(False) 