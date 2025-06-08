import os
from PyQt5 import uic
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QAbstractItemView, QHeaderView, QDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

class RoundResultWidget(QFrame):
    def __init__(self, round_info):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_round_result_widget.ui')
        uic.loadUi(ui_path, self)

        self.round_label = self.findChild(QLabel, 'round_label')
        self.winner_label = self.findChild(QLabel, 'winner_label')

        # Set the frame properties
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        round_num = round_info.get("roundNumber", "N/A")
        word = round_info.get("word", "******")
        winner = round_info.get("winner", "No Winner")

        # Format the round info with a more styled appearance
        self.round_label.setText(f"<b>Round {round_num}:</b> {word}")
        
        # Style the winner text differently depending on if there was a winner
        if winner != "No Winner":
            self.winner_label.setText(f"<b>Winner:</b> <span style='color: #FFD700;'>{winner}</span>")
        else:
            self.winner_label.setText(f"<b>Winner:</b> <span style='color: #AAAAAA;'>{winner}</span>")

class MatchDetailsDialog(QDialog):
    def __init__(self, details, parent=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_match_details_dialog.ui')
        uic.loadUi(ui_path, self)

        # Load stylesheet
        style_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'style', 'match_results.qss')
        with open(style_path, 'r') as file:
            self.setStyleSheet(file.read())
            
        # Remove window controls and make dialog modal
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setModal(True)

        self.winner_label = self.findChild(QLabel, 'winner_label')
        self.players_list_label = self.findChild(QLabel, 'players_list_label')
        self.scroll_area = self.findChild(QScrollArea, 'scroll_area')
        self.rounds_layout = self.findChild(QVBoxLayout, 'rounds_layout')
        self.ok_button = self.findChild(QPushButton, 'ok_button')
        
        # Set winner with appropriate styling
        winner = details.get('overallWinner', 'None')
        self.winner_label.setText(f"Overall Winner: {winner}")
        
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

        # Load stylesheet
        style_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'style', 'match_results.qss')
        with open(style_path, 'r') as file:
            self.setStyleSheet(file.read())

        self.header_label = self.findChild(QLabel, 'header_label')
        self.table = self.findChild(QTableWidget, 'table')
        self.view_details_button = self.findChild(QPushButton, 'view_details_button')
        self.back_button = self.findChild(QPushButton, 'back_button')

        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)

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

                # Highlight top players
                if row == 0:  # First place
                    gold_color = QColor(255, 215, 0)  # Gold
                    rank_item.setForeground(gold_color)
                    font = rank_item.font()
                    font.setBold(True)
                    rank_item.setFont(font)
                    player_item.setFont(font)
                    score_item.setFont(font)
                    score_item.setForeground(gold_color)
                elif row == 1:  # Second place
                    silver_color = QColor(192, 192, 192)  # Silver
                    rank_item.setForeground(silver_color)
                elif row == 2:  # Third place
                    bronze_color = QColor(205, 127, 50)  # Bronze
                    rank_item.setForeground(bronze_color)

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
        # Using exec_ instead of show() to make the dialog modal and block interaction
        self.details_dialog.exec_()

    def _clear_details_dialog(self, result):
        self.details_dialog = None

    def reset_view(self):
        self.table.setRowCount(0)
        self.match_details = None
        self.view_details_button.setEnabled(False) 