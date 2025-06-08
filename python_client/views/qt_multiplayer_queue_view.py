from PyQt5.QtWidgets import QWidget, QLabel, QListWidget, QPushButton, QProgressBar, QDialog
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFontDatabase, QFont, QPalette, QBrush, QPixmap, QColor, QPainter
from PyQt5 import uic
import os

class NoMatchFoundDialog(QDialog):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window

        # Remove window controls
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_nomatch_dialog.ui')
        uic.loadUi(ui_path, self)

        self.ok_button = self.findChild(QPushButton, 'ok_button')
        self.ok_button.clicked.connect(self.handle_ok)
        
        self.load_stylesheet()
        self.load_font()

    def load_stylesheet(self):
        style_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'style', 'nomatch_dialog_style.qss')
        try:
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Stylesheet for dialog not found.")
            
    def load_font(self):
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts', 'Jujutsu Kaisen.ttf')
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                font_family = font_families[0]
                jk_font = QFont(font_family, 14)
                message_label = self.findChild(QLabel, 'message_label')
                if message_label:
                    message_label.setFont(jk_font)
                if self.ok_button:
                    self.ok_button.setFont(jk_font)
        else:
            print("Failed to load JJK font.")

    def handle_ok(self):
        self.accept()
        self.main_window.show_view("MainMenu")

class MatchFoundDialog(QDialog):
    def __init__(self, countdown_seconds=5, parent=None):
        super().__init__(parent)
        self.seconds_left = countdown_seconds
        
        # Remove window controls
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_multiplayer_match_found_dialog.ui')
        uic.loadUi(ui_path, self)

        self.countdown_label = self.findChild(QLabel, 'countdown_label')
        self.countdown_label.setText(f"Starting in {self.seconds_left}...")
        
        # Set background image with left offset
        image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'match.png')
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            
            # Create a new pixmap with extra space on right to shift image left
            shifted_pixmap = QPixmap(pixmap.width() + 160, pixmap.height())
            shifted_pixmap.fill(Qt.transparent)
            
            # Draw the original pixmap with offset
            painter = QPainter(shifted_pixmap)
            painter.drawPixmap(-75, 0, pixmap)  # -50 shifts left by 50px
            painter.end()
            
            palette = QPalette()
            palette.setBrush(QPalette.Window, QBrush(shifted_pixmap))
            self.setAutoFillBackground(True)
            self.setPalette(palette)
        
        # Load and apply JJK font
        self.load_font()
        
        # Increase dialog size
        self.setMinimumSize(500, 300)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)
    
    def load_font(self):
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts', 'Jujutsu Kaisen.ttf')
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                font_family = font_families[0]
                jk_font = QFont(font_family, 24)  # Increased font size
                self.countdown_label.setFont(jk_font)
                self.countdown_label.setStyleSheet("color: white;")  # Make text white
        else:
            print("Failed to load JJK font for match found dialog.")

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

        # Don't apply background color to the entire view
        self.load_font()
        self.load_stylesheet()

    def load_font(self):
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts', 'Jujutsu Kaisen.ttf')
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                font_family = font_families[0]
                jk_font = QFont(font_family, 12)
                self.setFont(jk_font)
                self._set_font_recursive(self, jk_font)
        else:
            print("Failed to load JJK font for lobby.")

    def _set_font_recursive(self, widget, font):
        widget.setFont(font)
        for child in widget.findChildren(QWidget):
            child.setFont(font)

    def load_stylesheet(self):
        style_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'style', 'multiplayer_queue_style.qss')
        try:
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Stylesheet not found.")

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

    def show_no_match_dialog(self):
        dialog = NoMatchFoundDialog(self.main_window, parent=self)
        dialog.exec_() 