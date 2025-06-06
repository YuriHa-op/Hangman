from PyQt5.QtWidgets import QWidget, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt
from PyQt5 import uic
import os

class QtLeaderboardView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.controller = None # Will be set by MainWindow
        
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_leaderboard_view.ui')
        uic.loadUi(ui_path, self)

        self.leaderboard_table = self.findChild(QTableWidget, "leaderboard_table")
        self.leaderboard_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.back_button = self.findChild(QPushButton, "back_button")

    def set_controller(self, controller):
        self.controller = controller
        # Connect back button once controller is set, if controller handles back navigation
        self.back_button.clicked.connect(self.controller.go_back_to_main_menu)

    def display_leaderboard(self, entries):
        self.leaderboard_table.setRowCount(0) # Clear previous entries
        if not entries:
            # Handle case with no entries, maybe show a message in the table or a label
            self.leaderboard_table.setRowCount(1)
            no_entry_item = QTableWidgetItem("Leaderboard is currently empty.")
            no_entry_item.setTextAlignment(Qt.AlignCenter)
            self.leaderboard_table.setItem(0, 0, no_entry_item)
            self.leaderboard_table.setSpan(0, 0, 1, 2) # Span across both columns
            return

        self.leaderboard_table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            username_item = QTableWidgetItem(str(entry.username))
            wins_item = QTableWidgetItem(str(entry.wins))
            
            username_item.setTextAlignment(Qt.AlignCenter)
            wins_item.setTextAlignment(Qt.AlignCenter)
            
            self.leaderboard_table.setItem(row, 0, username_item)
            self.leaderboard_table.setItem(row, 1, wins_item)

    def show_error(self, message):
        # In a real app, might use QMessageBox or a status bar
        print(f"LeaderboardView Error: {message}")
        # For now, display error in the table
        self.leaderboard_table.setRowCount(1)
        error_item = QTableWidgetItem(message)
        error_item.setTextAlignment(Qt.AlignCenter)
        self.leaderboard_table.setItem(0, 0, error_item)
        self.leaderboard_table.setSpan(0, 0, 1, 2) 