from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QMessageBox, QDialog, QApplication)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5 import uic
import os

class MatchFoundDialog(QDialog):
    def __init__(self, opponent_name, countdown_seconds, countdown_callback, parent=None):
        super().__init__(parent)
        self.countdown_callback = countdown_callback
        self.remaining_seconds = countdown_seconds

        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_match_found_dialog.ui')
        uic.loadUi(ui_path, self)

        self.opponent_label = self.findChild(QLabel, 'opponent_label')
        self.countdown_label = self.findChild(QLabel, 'countdown_label')

        self.opponent_label.setText(f"Match found! Your opponent: {opponent_name}")
        self.countdown_label.setText(str(self.remaining_seconds))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)

        if parent:
            try:
                self.move(parent.geometry().center() - self.rect().center())
            except Exception:
                pass

    def update_countdown(self):
        self.remaining_seconds -= 1
        if self.remaining_seconds > 0:
            self.countdown_label.setText(str(self.remaining_seconds))
        else:
            self.timer.stop()
            self.accept()
            if self.countdown_callback:
                self.countdown_callback()

    def closeEvent(self, event):
        self.timer.stop()
        super().closeEvent(event)

class GameOverDialog(QDialog):
    def __init__(self, result_text, on_ok_callback, parent=None):
        super().__init__(parent)
        self.on_ok_callback = on_ok_callback
        
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_game_over_dialog.ui')
        uic.loadUi(ui_path, self)

        self.result_label = self.findChild(QLabel, 'result_label')
        self.ok_button = self.findChild(QPushButton, 'ok_button')
        
        self.result_label.setText(result_text)
        self.ok_button.clicked.connect(self.accept_and_callback)

        if parent:
            try:
                self.move(parent.geometry().center() - self.rect().center())
            except Exception:
                pass

    def accept_and_callback(self):
        self.accept()
        if self.on_ok_callback:
            self.on_ok_callback()

    def closeEvent(self, event):
        if self.on_ok_callback:
            self.on_ok_callback()
        super().closeEvent(event)

class QtSinglePlayer1v1GameView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.controller = None
        self.keyboard_buttons = {}
        self.match_found_dialog = None
        self.game_over_dialog = None
        
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_single_player_1v1_game_view.ui')
        uic.loadUi(ui_path, self)

        # Find all widgets from the UI file
        self.word_label = self.findChild(QLabel, 'word_label')
        self.timer_label = self.findChild(QLabel, 'timer_label')
        self.round_label = self.findChild(QLabel, 'round_label')
        self.score_label = self.findChild(QLabel, 'score_label')
        self.incorrect_label = self.findChild(QLabel, 'incorrect_label')
        self.status_label = self.findChild(QLabel, 'status_label')
        self.back_button = self.findChild(QPushButton, 'back_button')
        self.kb_container_widget = self.findChild(QWidget, 'kb_container_widget')

        self._create_keyboard()
        self.back_button.clicked.connect(self.handle_back_button_press)

    def _create_keyboard(self):
        kb_v_layout = QVBoxLayout(self.kb_container_widget)
        keyboard_rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        for row_str in keyboard_rows:
            row_h_layout = QHBoxLayout()
            row_h_layout.addStretch()
            for letter in row_str:
                btn = QPushButton(letter)
                btn.setFixedSize(40, 40)
                btn.setFont(QFont("Arial", 12, QFont.Bold))
                btn.clicked.connect(lambda checked, l=letter: self.controller.handle_single_player_guess(l) if self.controller else None)
                row_h_layout.addWidget(btn)
                self.keyboard_buttons[letter] = btn
            row_h_layout.addStretch()
            kb_v_layout.addLayout(row_h_layout)

    def set_controller(self, controller):
        self.controller = controller
        if self.controller:
            try: self.back_button.clicked.disconnect()
            except TypeError: pass
            self.back_button.clicked.connect(self.controller.handle_back_to_menu_from_sp_game)

    def handle_back_button_press(self):
        if self.controller:
            self.controller.handle_back_to_menu_from_sp_game()
        else:
            if self.main_window:
                self.main_window.show_view("MainMenu")

    def update_display(self, masked_word, timer_text, incorrect_text, status_text, player_wins, total_rounds, current_round_num, attempted_letters, current_word_upper, round_over, game_over, timer_color="black"):
        self.word_label.setText(" ".join(list(masked_word)) if masked_word else "_ _ _")
        self.timer_label.setText(timer_text)
        self.timer_label.setStyleSheet(f"color: {timer_color}; font-size: 16pt; font-family: Arial;")
        self.incorrect_label.setText(incorrect_text)
        self.set_status(status_text)
        self.score_label.setText(f"Score: {player_wins}/{total_rounds}")
        self.round_label.setText(f"Round: {current_round_num + 1}/{total_rounds}")
        self.update_keyboard(attempted_letters, current_word_upper if current_word_upper else "", round_over or game_over)

    def update_keyboard(self, attempted_letters, current_word_upper, disable_all):
        default_style = "QPushButton { background-color: #E0E0E0; color: black; border: 1px solid #B0B0B0; } QPushButton:hover { background-color: #D0D0D0; }"
        correct_style = "QPushButton { background-color: #4CAF50; color: white; border: 1px solid #388E3C; }"
        incorrect_style = "QPushButton { background-color: #f44336; color: white; border: 1px solid #D32F2F; }"
        disabled_default_style = "QPushButton { background-color: #F5F5F5; color: #A0A0A0; border: 1px solid #E0E0E0; }"

        final_word_to_check = current_word_upper.upper() if current_word_upper else ""

        for letter, btn in self.keyboard_buttons.items():
            letter_lower = letter.lower()

            if disable_all:
                btn.setEnabled(False)
                if final_word_to_check and final_word_to_check != "_ _ _":
                    if letter_lower in final_word_to_check.lower():
                        btn.setStyleSheet(correct_style)
                    elif letter_lower in attempted_letters:
                        btn.setStyleSheet(incorrect_style)
                    else:
                        btn.setStyleSheet(disabled_default_style)
                else:
                    if btn.styleSheet() != correct_style and btn.styleSheet() != incorrect_style:
                        btn.setStyleSheet(disabled_default_style)
            else:
                if letter_lower in attempted_letters:
                    btn.setEnabled(False)
                else:
                    btn.setEnabled(True)
                    btn.setStyleSheet(default_style)

    def feedback_guess(self, letter, is_correct):
        btn = self.keyboard_buttons.get(letter.upper())
        if btn:
            style = "QPushButton { background-color: #4CAF50; color: white; border: 1px solid #388E3C; }" if is_correct \
                else "QPushButton { background-color: #f44336; color: white; border: 1px solid #D32F2F; }"
            btn.setStyleSheet(style)
            btn.setEnabled(False)

    def set_status(self, message, color="blue"):
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color}; font-size: 14pt; font-family: Arial;")

    def show_match_found_countdown(self, countdown_callback, opponent_name="Opponent", countdown_seconds=5):
        self._close_dialogs()
        self.match_found_dialog = MatchFoundDialog(opponent_name, countdown_seconds, countdown_callback, self.main_window)
        self.match_found_dialog.exec_()

    def show_sp_game_over_dialog(self, result_text, on_ok_callback):
        self._close_dialogs()
        self.game_over_dialog = GameOverDialog(result_text, on_ok_callback, self.main_window)
        self.game_over_dialog.exec_()

    def _close_dialogs(self):
        if self.match_found_dialog:
            if self.match_found_dialog.isVisible(): self.match_found_dialog.accept()
            self.match_found_dialog.deleteLater()
            self.match_found_dialog = None
        if self.game_over_dialog:
            if self.game_over_dialog.isVisible(): self.game_over_dialog.accept()
            self.game_over_dialog.deleteLater()
            self.game_over_dialog = None

    def on_hide_cleanup(self):
        self._close_dialogs()
        for letter, btn in self.keyboard_buttons.items():
            btn.setEnabled(True)
            btn.setStyleSheet("")
        self.set_status("Waiting to start...", color="blue")
