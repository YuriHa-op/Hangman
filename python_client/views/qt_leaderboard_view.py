from PyQt5.QtWidgets import QWidget, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QFontDatabase, QFont, QColor
from PyQt5 import uic
import os

class QtLeaderboardView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.controller = None # Will be set by MainWindow
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(base_dir, 'ui', 'qt_leaderboard_view.ui')
        style_path = os.path.join(base_dir, 'style', 'leaderboard.qss')
        assets_path = os.path.join(base_dir, 'assets')
        fonts_path = os.path.join(base_dir, 'fonts', 'Minecraftia.ttf')

        self._background_pixmap = QPixmap(os.path.join(assets_path, 'leaderboard.png'))
        self._avatar_pixmap = QPixmap(os.path.join(assets_path, 'avatar.png'))
        
        uic.loadUi(ui_path, self)

        # Load font
        font_id = QFontDatabase.addApplicationFont(fonts_path)
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                print(f"Successfully loaded font: '{font_families[0]}'")
        else:
            print("Error: Could not load font from path.")

        # Load stylesheet
        try:
            with open(style_path, 'r') as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Error loading leaderboard stylesheet: {e}")

        # --- Find Widgets ---
        # Podium widgets
        self.first_place_avatar_label = self.findChild(QLabel, "first_place_avatar_label")
        self.first_place_name_label = self.findChild(QLabel, "first_place_name_label")
        self.first_place_score_label = self.findChild(QLabel, "first_place_score_label")
        self.second_place_avatar_label = self.findChild(QLabel, "second_place_avatar_label")
        self.second_place_name_label = self.findChild(QLabel, "second_place_name_label")
        self.second_place_score_label = self.findChild(QLabel, "second_place_score_label")
        self.third_place_avatar_label = self.findChild(QLabel, "third_place_avatar_label")
        self.third_place_name_label = self.findChild(QLabel, "third_place_name_label")
        self.third_place_score_label = self.findChild(QLabel, "third_place_score_label")
        
        # Table and back button
        self.leaderboard_table = self.findChild(QTableWidget, "leaderboard_table")
        self.leaderboard_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.leaderboard_table.verticalHeader().setVisible(False)
        self.back_button = self.findChild(QPushButton, "back_button")

    def paintEvent(self, event):
        """Paint the background image."""
        if not self._background_pixmap.isNull():
            painter = QPainter(self)
            scaled_pixmap = self._background_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            point = self.rect().center() - scaled_pixmap.rect().center()
            painter.drawPixmap(point, scaled_pixmap)
        super().paintEvent(event)

    def set_controller(self, controller):
        self.controller = controller
        self.back_button.clicked.connect(self.controller.go_back_to_main_menu)

    def display_leaderboard(self, entries):
        # Clear previous entries from podium and table
        self._clear_leaderboard()

        if not entries:
            self._show_empty_message()
            return

        # Separate top 3 from the rest
        top_3 = entries[:3]
        rest = entries[3:]

        # Populate podium
        self._populate_podium(top_3)
        
        # Populate table
        self._populate_table(rest)

    def _clear_leaderboard(self):
        # Reset podium labels
        self.first_place_avatar_label.setPixmap(QPixmap())
        self.first_place_name_label.setText("")
        self.first_place_score_label.setText("")
        self.second_place_avatar_label.setPixmap(QPixmap())
        self.second_place_name_label.setText("")
        self.second_place_score_label.setText("")
        self.third_place_avatar_label.setPixmap(QPixmap())
        self.third_place_name_label.setText("")
        self.third_place_score_label.setText("")
        # Clear table
        self.leaderboard_table.setRowCount(0)

    def _show_empty_message(self):
        self.leaderboard_table.setRowCount(1)
        no_entry_item = QTableWidgetItem("Leaderboard is currently empty.")
        no_entry_item.setTextAlignment(Qt.AlignCenter)
        self.leaderboard_table.setItem(0, 0, no_entry_item)
        self.leaderboard_table.setSpan(0, 0, 1, self.leaderboard_table.columnCount())

    def _populate_podium(self, top_3):
        podium_widgets = [
            (self.first_place_avatar_label, self.first_place_name_label, self.first_place_score_label),
            (self.second_place_avatar_label, self.second_place_name_label, self.second_place_score_label),
            (self.third_place_avatar_label, self.third_place_name_label, self.third_place_score_label)
        ]
        for i, entry in enumerate(top_3):
            avatar_label, name_label, score_label = podium_widgets[i]
            if not self._avatar_pixmap.isNull():
                avatar_label.setPixmap(self._avatar_pixmap.scaled(avatar_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            name_label.setText(entry.username)
            score_label.setText(str(entry.wins))

    def _populate_table(self, rest_of_entries):
        self.leaderboard_table.setRowCount(len(rest_of_entries))
        for row, entry in enumerate(rest_of_entries):
            rank = row + 4 # Starts from 4th place
            
            rank_item = QTableWidgetItem(str(rank))
            username_item = QTableWidgetItem(str(entry.username))
            wins_item = QTableWidgetItem(str(entry.wins))

            yellow_color = QColor("yellow")
            rank_item.setForeground(yellow_color)
            username_item.setForeground(yellow_color)
            wins_item.setForeground(yellow_color)

            rank_item.setTextAlignment(Qt.AlignCenter)
            username_item.setTextAlignment(Qt.AlignCenter)
            wins_item.setTextAlignment(Qt.AlignCenter)

            self.leaderboard_table.setItem(row, 0, rank_item)
            self.leaderboard_table.setItem(row, 1, username_item)
            self.leaderboard_table.setItem(row, 2, wins_item)

    def show_error(self, message):
        self._clear_leaderboard()
        self.leaderboard_table.setRowCount(1)
        error_item = QTableWidgetItem(message)
        error_item.setTextAlignment(Qt.AlignCenter)
        self.leaderboard_table.setItem(0, 0, error_item)
        self.leaderboard_table.setSpan(0, 0, 1, self.leaderboard_table.columnCount()) 