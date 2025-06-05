from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QMessageBox, QDialog, QApplication)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

class MatchFoundDialog(QDialog):
    def __init__(self, opponent_name, countdown_seconds, countdown_callback, parent=None):
        super().__init__(parent)
        self.countdown_callback = countdown_callback
        self.remaining_seconds = countdown_seconds

        self.setWindowTitle("Match Found")
        self.setModal(True)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(f"Match found! Your opponent: {opponent_name}", font=QFont("Arial", 15)), alignment=Qt.AlignCenter)
        layout.addWidget(QLabel("The game will start in...", font=QFont("Arial", 14)), alignment=Qt.AlignCenter)

        self.countdown_label = QLabel(str(self.remaining_seconds), font=QFont("Arial", 32, QFont.Bold))
        self.countdown_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.countdown_label)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)

        self.setFixedSize(400, 180)
        if parent:
            try:
                self.move(parent.geometry().center() - self.rect().center())
            except Exception:
                pass # Fallback if parent geometry isn't available early

    def update_countdown(self):
        self.remaining_seconds -= 1
        if self.remaining_seconds > 0:
            self.countdown_label.setText(str(self.remaining_seconds))
        else:
            self.timer.stop()
            self.accept() # Close the dialog
            if self.countdown_callback:
                self.countdown_callback()

    def closeEvent(self, event):
        self.timer.stop() # Ensure timer stops if dialog is closed manually
        # Consider if closing MatchFoundDialog via 'X' should trigger countdown_callback
        # or if controller should handle this scenario (e.g. player aborted queue)
        # if self.countdown_callback:
        #     self.countdown_callback() # Potentially call to not get stuck
        super().closeEvent(event)

class GameOverDialog(QDialog):
    def __init__(self, result_text, on_ok_callback, parent=None):
        super().__init__(parent)
        self.on_ok_callback = on_ok_callback
        self.setWindowTitle("Game Over")
        self.setModal(True)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel(result_text, font=QFont("Arial", 18)), alignment=Qt.AlignCenter)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept_and_callback)
        layout.addWidget(ok_button, alignment=Qt.AlignCenter)
        self.setFixedSize(300, 150)
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
        # If closed via 'X', call the ok_callback to ensure consistent behavior (e.g., returning to menu)
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
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("1v1 Hangman Challenge")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        title_label = QLabel("1v1 Hangman Challenge", font=QFont("Arial", 20))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        top_info_frame = QHBoxLayout()
        self.word_label = QLabel("_ _ _ _ _", font=QFont("Consolas", 30, QFont.Bold))
        self.word_label.setStyleSheet("letter-spacing: 4px;")
        self.timer_label = QLabel("Time: --", font=QFont("Arial", 16))
        top_info_frame.addWidget(self.word_label, alignment=Qt.AlignCenter)
        top_info_frame.addStretch()
        top_info_frame.addWidget(self.timer_label, alignment=Qt.AlignRight | Qt.AlignVCenter)
        main_layout.addLayout(top_info_frame)

        stats_frame = QHBoxLayout()
        self.round_label = QLabel("Round: -/-", font=QFont("Arial", 14))
        self.score_label = QLabel("Score: -/-", font=QFont("Arial", 14))
        self.incorrect_label = QLabel("Incorrect: -/-", font=QFont("Arial", 12))
        stats_frame.addWidget(self.round_label)
        stats_frame.addStretch(1)
        stats_frame.addWidget(self.score_label)
        stats_frame.addStretch(1)
        stats_frame.addWidget(self.incorrect_label)
        main_layout.addLayout(stats_frame)

        self.status_label = QLabel("Waiting to start...", font=QFont("Arial", 14))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: blue;")
        main_layout.addWidget(self.status_label)

        kb_container_widget = QWidget() # Use a container to center the grid
        kb_layout = QGridLayout(kb_container_widget)
        kb_layout.setSpacing(4)
        keyboard_rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        for row_idx, row_str in enumerate(keyboard_rows):
            num_keys = len(row_str)
            # Simple centering for rows with fewer keys, assuming max 10 keys wide
            start_col = (10 - num_keys) // 2 if num_keys < 10 else 0
            for col_idx_in_row, letter in enumerate(row_str):
                actual_col_idx = start_col + col_idx_in_row
                btn = QPushButton(letter)
                btn.setFixedSize(35, 35)
                btn.setFont(QFont("Arial", 9, QFont.Bold))
                btn.clicked.connect(lambda checked, l=letter: self.controller.handle_single_player_guess(l) if self.controller else None)
                kb_layout.addWidget(btn, row_idx, actual_col_idx) # Add to grid layout by row, actual_col_idx
                self.keyboard_buttons[letter] = btn
        main_layout.addWidget(kb_container_widget, alignment=Qt.AlignCenter) # Center the keyboard grid

        main_layout.addStretch(1)

        self.back_button = QPushButton("Back to Main Menu")
        self.back_button.setFont(QFont("Arial", 12))
        self.back_button.clicked.connect(self.handle_back_button_press) # Connect here, controller will set its own handler
        main_layout.addWidget(self.back_button, alignment=Qt.AlignCenter)

        self.setLayout(main_layout)
        self.setMinimumSize(550, 480)

    def set_controller(self, controller):
        self.controller = controller
        # Controller will connect its specific method if back_button is meant to be handled by it
        # For now, if controller needs to handle it, it should disconnect default and connect its own,
        # or we connect directly to controller.handle_back_to_menu_from_sp_game
        if self.controller:
            # Disconnect previous if any, then connect to controller's method
            try: self.back_button.clicked.disconnect()
            except TypeError: pass # No connection to disconnect
            self.back_button.clicked.connect(self.controller.handle_back_to_menu_from_sp_game)


    def handle_back_button_press(self): # Default action if controller not set or doesn't override
        if self.controller:
            self.controller.handle_back_to_menu_from_sp_game()
        else:
            # Fallback if controller is not set, though ideally it always should be
            if self.main_window:
                self.main_window.show_view("MainMenu")


    def update_display(self, masked_word, timer_text, incorrect_text, status_text, player_wins, total_rounds, current_round_num, attempted_letters, current_word_upper, round_over, game_over, timer_color="black"):
        self.word_label.setText(" ".join(list(masked_word)) if masked_word else "_ _ _")
        self.timer_label.setText(timer_text)
        self.timer_label.setStyleSheet(f"color: {timer_color}; font-size: 16pt; font-family: Arial;")
        self.incorrect_label.setText(incorrect_text)
        self.set_status(status_text) # Uses its own method for color
        self.score_label.setText(f"Score: {player_wins}/{total_rounds}")
        self.round_label.setText(f"Round: {current_round_num + 1}/{total_rounds}")
        self.update_keyboard(attempted_letters, current_word_upper if current_word_upper else "", round_over or game_over)

    def update_keyboard(self, attempted_letters, current_word_upper, disable_all):
        default_style = "QPushButton { background-color: #E0E0E0; color: black; border: 1px solid #B0B0B0; } QPushButton:hover { background-color: #D0D0D0; }"
        correct_style = "QPushButton { background-color: #4CAF50; color: white; border: 1px solid #388E3C; }"
        incorrect_style = "QPushButton { background-color: #f44336; color: white; border: 1px solid #D32F2F; }"
        disabled_default_style = "QPushButton { background-color: #F5F5F5; color: #A0A0A0; border: 1px solid #E0E0E0; }"

        # Ensure current_word_upper is actually uppercase for reliable comparison
        final_word_to_check = current_word_upper.upper() if current_word_upper else ""

        for letter, btn in self.keyboard_buttons.items():
            letter_lower = letter.lower()

            if disable_all:  # Round or Game is Over - Keyboard is informational
                btn.setEnabled(False)
                if final_word_to_check and final_word_to_check != "_ _ _":
                    if letter_lower in final_word_to_check.lower():
                        btn.setStyleSheet(correct_style)
                    elif letter_lower in attempted_letters: # Attempted and not in the final word
                        btn.setStyleSheet(incorrect_style)
                    else: # Not attempted, and not in the final word (though less likely to be styled)
                        btn.setStyleSheet(disabled_default_style)
                else: # Final word not available, use generic disabled style
                    # If already colored by feedback_guess, preserve it, otherwise generic disable
                    if btn.styleSheet() != correct_style and btn.styleSheet() != incorrect_style:
                        btn.setStyleSheet(disabled_default_style)
                    # else, its existing color (from feedback_guess) remains.
            else:  # Game is in progress
                if letter_lower in attempted_letters:
                    # feedback_guess has already set the style and disabled the button.
                    # Do not override the style here mid-round.
                    btn.setEnabled(False) # Ensure it stays disabled
                else:
                    # This letter has not been attempted in the current round, so reset to default and enable.
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
        self._close_dialogs() # Ensure no old dialogs are lingering
        self.match_found_dialog = MatchFoundDialog(opponent_name, countdown_seconds, countdown_callback, self.main_window)
        self.match_found_dialog.exec_()

    def show_sp_game_over_dialog(self, result_text, on_ok_callback):
        self._close_dialogs()
        self.game_over_dialog = GameOverDialog(result_text, on_ok_callback, self.main_window)
        self.game_over_dialog.exec_()

    def _close_dialogs(self):
        if self.match_found_dialog:
            if self.match_found_dialog.isVisible(): self.match_found_dialog.accept() # or .close() or .reject()
            self.match_found_dialog.deleteLater() # Important for PyQt resource management
            self.match_found_dialog = None
        if self.game_over_dialog:
            if self.game_over_dialog.isVisible(): self.game_over_dialog.accept()
            self.game_over_dialog.deleteLater()
            self.game_over_dialog = None

    def on_hide_cleanup(self): # Called by controller or MainWindow when view is hidden
        self._close_dialogs()
