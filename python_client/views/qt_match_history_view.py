import json
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
    QComboBox, QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QHeaderView
)
from PyQt5.QtCore import Qt
from PyQt5 import uic
import os
from datetime import datetime
from functools import partial

class MatchDetailsDialog(QDialog):
    """A dialog to show the detailed results of a single match."""
    def __init__(self, details_json, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Match Details")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout(self)

        try:
            details = json.loads(details_json)
        except json.JSONDecodeError:
            layout.addWidget(QLabel("Error: Could not parse match details."))
            return

        # Game ID and Winner
        game_id = details.get('gameId', 'N/A')
        winner = details.get('overallWinner', 'N/A')
        layout.addWidget(QLabel(f"<b>Game ID:</b> {game_id}"))
        layout.addWidget(QLabel(f"<b>Winner:</b> {winner}"))

        # Rounds Table
        rounds_table = QTableWidget()
        rounds_table.setColumnCount(3)
        rounds_table.setHorizontalHeaderLabels(["Round #", "Word", "Winner"])
        rounds_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        rounds_table.setEditTriggers(QTableWidget.NoEditTriggers)

        round_results = details.get('rounds', [])
        rounds_table.setRowCount(len(round_results))
        for i, round_data in enumerate(round_results):
            rounds_table.setItem(i, 0, QTableWidgetItem(str(round_data.get('roundNumber', i + 1))))
            rounds_table.setItem(i, 1, QTableWidgetItem(round_data.get('word', 'N/A')))
            rounds_table.setItem(i, 2, QTableWidgetItem(round_data.get('winner', 'N/A')))
        
        layout.addWidget(rounds_table)

        # Close button
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)


class QtMatchHistoryView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.controller = None

        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_match_history_view.ui')
        uic.loadUi(ui_path, self)

        self.history_table = self.findChild(QTableWidget, "history_table")
        self.history_type_combo = self.findChild(QComboBox, "history_type_combo")
        self.back_button = self.findChild(QPushButton, "back_button")
        
        self.history_type_combo.addItems(["Multiplayer", "1v1 (Single Player)"])
        self.history_type_combo.currentTextChanged.connect(self.on_history_type_changed)

    def set_controller(self, controller):
        self.controller = controller
        if self.controller:
            self.back_button.clicked.connect(self.controller.go_back_to_main_menu)

    def on_history_type_changed(self, text):
        if not self.controller:
            return
        mode = 'single_player' if "1v1" in text else 'multiplayer'
        self.controller.fetch_history(mode)

    def display_match_history(self, matches_json_string):
        self.history_table.setRowCount(0)
        try:
            matches = json.loads(matches_json_string)
            if not matches:
                return

            self.history_table.setRowCount(len(matches))
            for row, match_summary in enumerate(matches):
                dt_object = datetime.fromtimestamp(match_summary.get('gameEndTime', 0) / 1000)
                date_item = QTableWidgetItem(dt_object.strftime('%Y-%m-%d %H:%M:%S'))
                
                players_item = QTableWidgetItem(", ".join(match_summary.get('players', [])))
                winner_item = QTableWidgetItem(match_summary.get('overallWinner', 'N/A'))
                rounds_item = QTableWidgetItem(str(match_summary.get('totalRounds', 'N/A')))

                details_button = QPushButton("Details")
                game_id = match_summary.get('gameId')
                if game_id:
                    details_button.clicked.connect(partial(self.controller.fetch_match_details, game_id))

                self.history_table.setItem(row, 0, date_item)
                self.history_table.setItem(row, 1, players_item)
                self.history_table.setItem(row, 2, winner_item)
                self.history_table.setItem(row, 3, rounds_item)
                self.history_table.setCellWidget(row, 4, details_button)

        except json.JSONDecodeError:
            self.show_error_message("Error: Could not parse match history data.")
        except Exception as e:
            self.show_error_message(f"An error occurred: {e}")

    def show_details_dialog(self, details_json):
        """Creates and shows the match details dialog."""
        dialog = MatchDetailsDialog(details_json, self)
        dialog.exec_()

    def show_error_message(self, message):
        QMessageBox.warning(self, 'Match History Error', message) 