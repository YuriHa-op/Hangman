import json
from PyQt5.QtWidgets import (
    QWidget, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
    QLabel, QHeaderView, QButtonGroup
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap, QFontDatabase, QFont, QColor
from PyQt5 import uic
import os
from datetime import datetime
from functools import partial

class QtMatchHistoryView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.controller = None
        self._background_pixmap = None

        # --- Paths ---
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(base_dir, 'ui', 'qt_match_history_view.ui')
        style_path = os.path.join(base_dir, 'style', 'history.qss')
        font_path = os.path.join(base_dir, 'fonts', 'Jujutsu Kaisen.ttf')
        background_path = os.path.join(base_dir, 'assets', 'histor.png')

        # --- Load UI ---
        uic.loadUi(ui_path, self)

        # --- Load Assets ---
        self._background_pixmap = QPixmap(background_path)
        
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            print(f"Loaded font: {font_families[0]}")
        else:
            print("Failed to load Jujutsu Kaisen.ttf font.")

        try:
            with open(style_path, 'r') as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Error loading history stylesheet: {e}")

        # --- Find Widgets ---
        self.mission_list_table = self.findChild(QTableWidget, "mission_list_table")
        self.multiplayer_button = self.findChild(QPushButton, "multiplayer_button")
        self.singleplayer_button = self.findChild(QPushButton, "singleplayer_button")
        self.back_button = self.findChild(QPushButton, "back_button")
        
        # Briefing panel widgets
        self.briefing_content_label = self.findChild(QLabel, "briefing_content_label")
        self.rounds_table = self.findChild(QTableWidget, "rounds_table")

        # --- Widget Setup ---
        # Mission Tabs
        self.mission_tabs = QButtonGroup()
        self.mission_tabs.addButton(self.multiplayer_button)
        self.mission_tabs.addButton(self.singleplayer_button)
        self.mission_tabs.setExclusive(True)
        self.multiplayer_button.clicked.connect(lambda: self.on_history_type_changed('multiplayer'))
        self.singleplayer_button.clicked.connect(lambda: self.on_history_type_changed('single_player'))
        
        # Mission List Table
        self.mission_list_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.mission_list_table.verticalHeader().setVisible(False)
        self.mission_list_table.itemSelectionChanged.connect(self.on_mission_selected)
        
        # Rounds Table
        self.rounds_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.rounds_table.verticalHeader().setVisible(False)

        # Store game IDs to fetch details later
        self.current_matches = []

    def set_controller(self, controller):
        self.controller = controller
        if self.controller:
            self.back_button.clicked.connect(self.controller.go_back_to_main_menu)

    def on_history_type_changed(self, mode):
        self.controller.fetch_history(mode)

    def on_mission_selected(self):
        selected_items = self.mission_list_table.selectedItems()
        if not selected_items:
            return
        
        selected_row = selected_items[0].row()
        game_id = self.current_matches[selected_row].get('gameId')
        if game_id and self.controller:
            self.controller.fetch_match_details(game_id)

    def display_match_history(self, matches_json_string):
        self.mission_list_table.setRowCount(0)
        self.clear_briefing()
        try:
            self.current_matches = json.loads(matches_json_string)
            if not self.current_matches:
                self.briefing_content_label.setText("No missions found for this category.")
                return

            self.mission_list_table.setRowCount(len(self.current_matches))
            current_username = self.controller.model.get_username() if self.controller and self.controller.model else ""
            for row, match in enumerate(self.current_matches):
                dt_object = datetime.fromtimestamp(match.get('gameEndTime', 0) / 1000)
                date_item = QTableWidgetItem(dt_object.strftime('%Y-%m-%d'))
                
                outcome = "Victory" if current_username == match.get('overallWinner') else "Defeat"
                outcome_item = QTableWidgetItem(outcome)

                if outcome == "Victory":
                    outcome_item.setForeground(QColor("#FFD700")) # Theme's gold/yellow
                else: # Defeat
                    outcome_item.setForeground(QColor("#E53935")) # A nice red
                
                self.mission_list_table.setItem(row, 0, date_item)
                self.mission_list_table.setItem(row, 1, outcome_item)
            
            # Optionally, select the first mission by default
            if self.mission_list_table.rowCount() > 0:
                self.mission_list_table.selectRow(0)

        except json.JSONDecodeError:
            self.show_error_message("Error: Could not parse mission data.")
        except Exception as e:
            self.show_error_message(f"An error occurred: {e}")

    def display_match_details(self, details_json):
        self.clear_briefing(clear_title=False)
        try:
            details = json.loads(details_json)
            
            # Populate briefing text
            winner = details.get('overallWinner', 'N/A')
            players = ", ".join(details.get('players', []))
            briefing_text = (
                f"<b>Game ID:</b> {details.get('gameId', 'N/A')}<br>"
                f"<b>Combatants:</b> {players}<br>"
                f"<b>Outcome:</b> Mission success for {winner}."
            )
            self.briefing_content_label.setText(briefing_text)

            # Populate rounds table
            self.rounds_table.setColumnCount(3)
            self.rounds_table.setHorizontalHeaderLabels(["Round #", "Target", "Victor"])
            round_results = details.get('rounds', [])
            self.rounds_table.setRowCount(len(round_results))
            for i, round_data in enumerate(round_results):
                self.rounds_table.setItem(i, 0, QTableWidgetItem(str(round_data.get('roundNumber', i + 1))))
                self.rounds_table.setItem(i, 1, QTableWidgetItem(round_data.get('word', 'N/A')))
                self.rounds_table.setItem(i, 2, QTableWidgetItem(round_data.get('winner', 'N/A')))

        except json.JSONDecodeError:
            self.briefing_content_label.setText("Error: Could not parse mission briefing.")

    def clear_briefing(self, clear_title=True):
        if clear_title:
            self.briefing_content_label.setText("Select a mission to view its briefing.")
        else:
            self.briefing_content_label.setText("")
        self.rounds_table.setRowCount(0)
        self.rounds_table.setColumnCount(0)

    def show_error_message(self, message):
        QMessageBox.warning(self, 'Mission Archive Error', message)
        
    def paintEvent(self, event):
        if self._background_pixmap and not self._background_pixmap.isNull():
            painter = QPainter(self)
            painter.drawPixmap(self.rect(), self._background_pixmap)
        super().paintEvent(event) 