from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGridLayout, QFrame, QScrollArea, QDialog)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon
from PyQt5 import uic
import os

class AfkDialog(QDialog):
    yes_clicked = pyqtSignal()
    timed_out = pyqtSignal()

    def __init__(self, countdown_seconds=10, parent=None):
        super().__init__(parent)
        self.seconds_left = countdown_seconds

        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_afk_dialog.ui')
        uic.loadUi(ui_path, self)
        
        self.countdown_label = self.findChild(QLabel, 'countdown_label')
        self.yes_button = self.findChild(QPushButton, 'yes_button')
        
        self.countdown_label.setText(f"Closing in: {self.seconds_left}s")
        self.yes_button.clicked.connect(self.handle_yes)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)

    def update_countdown(self):
        self.seconds_left -= 1
        if self.seconds_left > 0:
            self.countdown_label.setText(f"Closing in: {self.seconds_left}s")
        else:
            self.timer.stop()
            self.timed_out.emit()
            self.reject()

    def handle_yes(self):
        self.timer.stop()
        self.yes_button.setEnabled(False)
        self.yes_button.setText("Processing...")
        self.yes_clicked.emit()
        self.accept()

    def closeEvent(self, event):
        self.timer.stop()
        if self.yes_button.isEnabled():
            self.timed_out.emit()
        super().closeEvent(event)

class LastChanceDialog(QDialog):
    yes_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Re-using a simple UI, assuming it has 'text_label' and 'ok_button'
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_info_dialog.ui')
        uic.loadUi(ui_path, self)
        
        self.setWindowTitle("Last Chance!")
        self.findChild(QLabel, 'text_label').setText("Game is stalled. Start next round?")
        
        self.ok_button = self.findChild(QPushButton, 'ok_button')
        self.ok_button.setText("Yes, Start Round")
        self.ok_button.clicked.connect(self._handle_yes)

    def _handle_yes(self):
        self.ok_button.setEnabled(False)
        self.ok_button.setText("Processing...")
        self.yes_clicked.emit()
        self.accept()

class GameCleanedUpDialog(QDialog):
    ok_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_info_dialog.ui')
        uic.loadUi(ui_path, self)
        
        self.setWindowTitle("Game Over")
        self.findChild(QLabel, 'text_label').setText("The game session has ended or been cleaned up by the server.")
        
        self.ok_button = self.findChild(QPushButton, 'ok_button')
        self.ok_button.setText("OK")
        self.ok_button.clicked.connect(self._handle_ok)

    def _handle_ok(self):
        self.ok_clicked.emit()
        self.accept()

class GameOverDialog(QDialog):
    def __init__(self, result_text, parent=None):
        super().__init__(parent)
        
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_multiplayer_game_over_dialog.ui')
        uic.loadUi(ui_path, self)
        
        self.icon_label = self.findChild(QLabel, 'icon_label')
        self.message_label = self.findChild(QLabel, 'message_label')
        self.ok_button = self.findChild(QPushButton, 'ok_button')
        
        message = "You Won!" if result_text == "WIN" else "You Lost"
        if result_text == "WIN":
            self.icon_label.setText("🏆") 
            color = "#FFD700"
        else:
            self.icon_label.setText("👎")
            color = "#A9A9A9"
        
        self.message_label.setText(message)
        self.message_label.setStyleSheet(f"color: {color};")
        self.ok_button.clicked.connect(self.accept)

class InfoDialog(QDialog):
    def __init__(self, title, text, button_text="OK", parent=None):
        super().__init__(parent)
        
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_info_dialog.ui')
        uic.loadUi(ui_path, self)
        
        self.text_label = self.findChild(QLabel, 'text_label')
        self.ok_button = self.findChild(QPushButton, 'ok_button')
        
        self.setWindowTitle(title)
        self.text_label.setText(text)
        self.ok_button.setText(button_text)
        self.ok_button.clicked.connect(self.accept)

class VirtualKeyboard(QWidget):
    letterClicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttons = {}
        
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_virtual_keyboard.ui')
        uic.loadUi(ui_path, self)

        layout_config = [
            "QWERTYUIOP",
            "ASDFGHJKL",
            "ZXCVBNM"
        ]
        
        all_letters = "".join(layout_config)

        for letter in all_letters:
            button = self.findChild(QPushButton, f'button_{letter}')
            if button:
                button.clicked.connect(lambda checked, l=letter: self.letterClicked.emit(l))
                self.buttons[letter] = button

    def set_button_pending(self, letter):
        button = self.buttons.get(letter)
        if button:
            button.setDisabled(True)
            button.setStyleSheet("background-color: #f0e68c;") # Khaki

    def update_button_color(self, letter, is_correct):
        button = self.buttons.get(letter)
        if button:
            if is_correct:
                button.setStyleSheet("background-color: #2E8B57; color: white;")
            else:
                button.setStyleSheet("background-color: #C70039; color: white;")

    def update_keyboard(self, all_guessed_letters, correctly_guessed_letters, enabled=True):
        for letter, button in self.buttons.items():
            # Use uppercase for comparison with button object names
            if letter in all_guessed_letters:
                button.setDisabled(True)
                if letter in correctly_guessed_letters:
                    button.setStyleSheet("background-color: #2E8B57; color: white;") # More vivid green
                else:
                    button.setStyleSheet("background-color: #C70039; color: white;") # More vivid red
            else:
                button.setEnabled(enabled)
                button.setStyleSheet("") # Reset non-guessed buttons

class PlayerStatusWidget(QFrame):
    def __init__(self, username):
        super().__init__()
        
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_player_status_widget.ui')
        uic.loadUi(ui_path, self)

        self.username_label = self.findChild(QLabel, 'username_label')
        self.score_label = self.findChild(QLabel, 'score_label')
        self.masked_word_label = self.findChild(QLabel, 'masked_word_label')
        self.status_label = self.findChild(QLabel, 'status_label')

        self.username_label.setText(username)

    def update_widget(self, score, masked_word, is_finished):
        self.score_label.setText(f"Score: {score}")
        self.masked_word_label.setText(masked_word.replace("", " ").strip())
        if is_finished:
            self.status_label.setText("Finished!")
            self.status_label.setStyleSheet("color: #00AA00; font-weight: bold;")
        else:
            self.status_label.setText("Playing...")
            self.status_label.setStyleSheet("")

class QtMultiplayerGameView(QWidget):
    def __init__(self, main_window=None):
        super().__init__(main_window)
        self.main_window = main_window
        self.controller = None
        self.player_status_widgets = {}
        self.afk_dialog = None
        self.last_chance_dialog = None
        self.game_cleaned_up_dialog = None
        self._game_over_dialog = None

        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_multiplayer_game_view.ui')
        uic.loadUi(ui_path, self)

        # Find main containers and widgets
        self.right_panel = self.findChild(QFrame, 'right_panel')
        self.status_label = self.findChild(QLabel, 'status_label')
        self.timer_label = self.findChild(QLabel, 'timer_label')
        self.my_score_label = self.findChild(QLabel, 'my_score_label')
        self.round_label = self.findChild(QLabel, 'round_label')
        self.my_masked_word_label = self.findChild(QLabel, 'my_masked_word_label')
        self.main_menu_button = self.findChild(QPushButton, 'main_menu_button')
        self.virtual_keyboard_container = self.findChild(QWidget, 'virtual_keyboard_container')
        self.scroll_area_layout = self.findChild(QVBoxLayout, 'scroll_area_layout')

        # Create and add the virtual keyboard
        self.virtual_keyboard = VirtualKeyboard()
        kb_container_layout = QVBoxLayout(self.virtual_keyboard_container)
        kb_container_layout.setContentsMargins(0,0,0,0)
        kb_container_layout.addWidget(self.virtual_keyboard)
        
        # Connect signals
        self.virtual_keyboard.letterClicked.connect(self.make_guess)
        self.main_menu_button.clicked.connect(self.back_to_main_menu)

        self.right_panel.hide()
        self.virtual_keyboard.update_keyboard([], "", enabled=False)

    def set_controller(self, controller):
        self.controller = controller

    def make_guess(self, guess):
        if self.controller:
            self.controller.make_guess(guess)

    def back_to_main_menu(self):
        if self.controller:
            self.controller.forfeit_and_go_back()

    def update_view_from_state(self, game_state, current_player_username):
        if not game_state:
            self.reset_view()
            self.status_label.setText("Waiting for game data...")
            return
            
        game_data = game_state.get("gameState")
        if not game_data:
            players = game_state.get("players", [])
            self.status_label.setText(f"In lobby with {len(players)} players. Waiting for game to start...")
            self.my_masked_word_label.setText(". . .")
            self.virtual_keyboard.update_keyboard([], "", enabled=False)
            self.right_panel.hide()
            return

        # --- Game has started, process game_data ---
        
        # 1. Update own view (left panel)
        self.timer_label.setText(f"Time: {game_data.get('remainingTime', 0)}")
        current_round = game_data.get('currentRound', 0) + 1
        self.round_label.setText(f"Round: {current_round}")

        scores = game_data.get("scores", {})
        my_score = scores.get(current_player_username, 0)
        self.my_score_label.setText(f"Your Score: {my_score}")

        masked_words = game_data.get("maskedWords", {})
        my_masked_word = masked_words.get(current_player_username, "_ _ _")
        self.my_masked_word_label.setText(my_masked_word.replace("", " ").strip())

        # 2. Determine if player is done with the round
        finish_times = game_data.get("allPlayerFinishTimes", {})
        incorrect_guesses_map = game_data.get("incorrectGuessesMap", {})
        my_incorrects = incorrect_guesses_map.get(current_player_username, 0)
        player_is_done_this_round = (current_player_username in finish_times and finish_times[current_player_username] > 0) or my_incorrects >= 6

        if player_is_done_this_round:
            self.right_panel.show()
        else:
            self.right_panel.hide()

        # 3. Update status label based on round/game winner
        round_winner = game_data.get("roundWinner", "")
        game_winner = game_data.get("gameWinner", "")

        if game_winner:
            self.status_label.setText(f"Game Over! Winner is {game_winner}!")
            self.main_menu_button.setText("Back to Main Menu")
        elif not game_data.get("roundInProgress", True):
            winner_text = f"Round Over! Winner: {round_winner}" if round_winner else "Round Over! No winner."
            self.status_label.setText(winner_text)
        else:
            self.status_label.setText(f"Round {current_round} in Progress")

        # 4. Determine keyboard state
        is_round_in_progress = game_data.get("roundInProgress", True)
        keyboard_enabled = is_round_in_progress and not player_is_done_this_round and not game_winner

        # 5. Update the virtual keyboard based on the player's own guesses
        my_guesses = {char.upper() for char in game_data.get("playerGuessesMap", {}).get(current_player_username, [])}
        my_masked_word = masked_words.get(current_player_username, "")
        
        # Determine correctly guessed letters from the masked word, converting to uppercase for comparison
        letters_in_masked_word = {char.upper() for char in my_masked_word if char.isalpha()}

        self.virtual_keyboard.update_keyboard(my_guesses, letters_in_masked_word, enabled=(not player_is_done_this_round))

        # 6. Update opponent panel (right panel)
        all_players_in_game = set(game_state.get("players", []))
        opponents = all_players_in_game - {current_player_username}
        
        current_widgets = set(self.player_status_widgets.keys())
        
        for player in current_widgets - opponents:
            widget = self.player_status_widgets.pop(player)
            widget.deleteLater()
            
        for player_name in opponents:
            if player_name not in self.player_status_widgets:
                widget = PlayerStatusWidget(player_name)
                self.scroll_area_layout.addWidget(widget)
                self.player_status_widgets[player_name] = widget
            
            widget = self.player_status_widgets[player_name]
            player_score = scores.get(player_name, 0)
            player_masked_word = masked_words.get(player_name, "_ _ _")
            player_incorrects = incorrect_guesses_map.get(player_name, 0)
            player_is_finished = (player_name in finish_times and finish_times[player_name] > 0) or player_incorrects >= 6
            widget.update_widget(player_score, player_masked_word, player_is_finished)

    def reset_view(self):
        self.status_label.setText("Game has ended. Returning to menu...")
        self.timer_label.setText("Time: 0")
        self.my_score_label.setText("Your Score: 0")
        self.round_label.setText("Round: 1")
        self.my_masked_word_label.setText("_ _ _")
        self.virtual_keyboard.update_keyboard([], "", enabled=False)
        self.main_menu_button.setText("Back to Main Menu (Forfeit)")

        for _ in range(self.scroll_area_layout.count()):
            widget = self.scroll_area_layout.takeAt(0).widget()
            widget.deleteLater()
        self.close_all_dialogs()

    def close_all_dialogs(self):
        self.close_afk_dialog()
        self.close_last_chance_dialog()
        self.close_game_cleaned_up_dialog()
        if self._game_over_dialog:
            self._game_over_dialog.accept()
            self._game_over_dialog = None

    def show_afk_dialog(self):
        if self.afk_dialog and self.afk_dialog.isVisible():
            return
        
        self.afk_dialog = AfkDialog(parent=self)
        if self.controller:
            self.afk_dialog.yes_clicked.connect(self.controller._handle_afk_yes)
            self.afk_dialog.timed_out.connect(self.controller._handle_afk_timeout)
        self.afk_dialog.show()

    def close_afk_dialog(self):
        if self.afk_dialog:
            self.afk_dialog.accept()
            self.afk_dialog = None

    def is_afk_dialog_showing(self):
        return self.afk_dialog is not None and self.afk_dialog.isVisible()

    def show_last_chance_dialog(self):
        if self.last_chance_dialog and self.last_chance_dialog.isVisible():
            return

        self.last_chance_dialog = LastChanceDialog(parent=self)
        if self.controller:
            self.last_chance_dialog.yes_clicked.connect(self.controller._handle_last_chance_yes)
        self.last_chance_dialog.show()

    def close_last_chance_dialog(self):
        if self.last_chance_dialog:
            self.last_chance_dialog.accept()
            self.last_chance_dialog = None

    def show_game_cleaned_up_dialog(self, on_ok_callback):
        if self.game_cleaned_up_dialog and self.game_cleaned_up_dialog.isVisible():
            return
        
        self.close_all_dialogs()
        
        self.game_cleaned_up_dialog = GameCleanedUpDialog(self)
        self.game_cleaned_up_dialog.ok_clicked.connect(on_ok_callback)
        self.game_cleaned_up_dialog.show()

    def close_game_cleaned_up_dialog(self):
        if self.game_cleaned_up_dialog and self.game_cleaned_up_dialog.isVisible():
            self.game_cleaned_up_dialog.accept()
        self.game_cleaned_up_dialog = None

    def show_game_over_dialog(self, message, on_ok_callback):
        if self._game_over_dialog is None:
            # Use main_window as parent to avoid parent deletion issues
            parent = self.main_window if self.main_window is not None else self
            self._game_over_dialog = GameOverDialog(message, parent)
            self._game_over_dialog.finished.connect(lambda _: on_ok_callback())
            self._game_over_dialog.finished.connect(self._clear_game_over_dialog)
            self._game_over_dialog.show()

    def _clear_game_over_dialog(self, result):
        self._game_over_dialog = None 