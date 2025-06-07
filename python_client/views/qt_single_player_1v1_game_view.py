from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QMessageBox, QDialog, QApplication, QProgressBar, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QParallelAnimationGroup, QMargins
from PyQt5.QtGui import QFont, QPainter, QPixmap, QFontDatabase, QColor
from PyQt5 import uic
import os
import re

class ThemedDialog(QDialog):
    """Base class for themed dialogs to apply JJK style."""
    def __init__(self, ui_path, parent=None):
        super().__init__(parent)
        uic.loadUi(ui_path, self)

        # Common styling
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        style_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'style', 'dialog.qss')
        try:
            with open(style_path, 'r') as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Error loading dialog stylesheet: {e}")
        
        if parent:
            self.move(parent.geometry().center() - self.rect().center())


class MatchFoundDialog(ThemedDialog):
    def __init__(self, opponent_name, countdown_seconds, countdown_callback, parent=None):
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_match_found_dialog.ui')
        super().__init__(ui_path, parent)
        
        self.countdown_callback = countdown_callback
        self.remaining_seconds = countdown_seconds

        self.opponent_label = self.findChild(QLabel, 'opponent_label')
        self.countdown_label = self.findChild(QLabel, 'countdown_label')

        self.opponent_label.setText(f"Opponent Found: {opponent_name}")
        self.countdown_label.setText(f"Battle Begins in {self.remaining_seconds}...")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)

    def update_countdown(self):
        self.remaining_seconds -= 1
        if self.remaining_seconds > 0:
            self.countdown_label.setText(f"Battle Begins in {self.remaining_seconds}...")
        else:
            self.timer.stop()
            self.accept()
            if self.countdown_callback:
                self.countdown_callback()

class GameOverDialog(ThemedDialog):
    def __init__(self, result_text, on_ok_callback, parent=None):
        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_game_over_dialog.ui')
        super().__init__(ui_path, parent)

        self.on_ok_callback = on_ok_callback
        
        self.result_label = self.findChild(QLabel, 'result_label')
        self.ok_button = self.findChild(QPushButton, 'ok_button')
        
        self.result_label.setText(result_text)
        self.ok_button.clicked.connect(self.accept_and_callback)

    def accept_and_callback(self):
        self.accept()
        if self.on_ok_callback:
            self.on_ok_callback()

class OverlayWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAutoFillBackground(False)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor(0, 0, 0, 180))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())
        super().paintEvent(event)

class QtSinglePlayer1v1GameView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.controller = None
        self.keyboard_buttons = {}
        self.match_found_dialog = None
        self.game_over_dialog = None
        self._background_pixmap = None
        self.player_pulse_group = None
        self.opponent_pulse_group = None
        self.overlay = None
        
        # --- Paths & UI Load ---
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(base_dir, 'ui', 'qt_single_player_1v1_game_view.ui')
        style_path = os.path.join(base_dir, 'style', 'single_player_1v1_game.qss')
        font_path = os.path.join(base_dir, 'fonts', 'JujutsuKaisen.ttf')
        background_path = os.path.join(base_dir, 'assets', '1v1.png')
        uic.loadUi(ui_path, self)

        # --- Font, Stylesheet & Background ---
        self._background_pixmap = QPixmap(background_path)
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1: print("Failed to load JujutsuKaisen.ttf font.")
        
        try:
            with open(style_path, 'r') as f: self.setStyleSheet(f.read())
        except Exception as e: print(f"Error loading stylesheet: {e}")

        # --- Find Widgets ---
        self.word_label = self.findChild(QLabel, 'word_label')
        self.timer_label = self.findChild(QLabel, 'timer_label')
        self.round_label = self.findChild(QLabel, 'round_label')
        self.score_label = self.findChild(QLabel, 'score_label')
        self.status_label = self.findChild(QLabel, 'status_label')
        self.back_button = self.findChild(QPushButton, 'back_button')
        self.kb_container_widget = self.findChild(QWidget, 'kb_container_widget')
        self.word_container_widget = self.findChild(QWidget, 'word_container_widget')
        
        # Player HUD
        self.player_name_label = self.findChild(QLabel, 'player_name_label')
        self.player_health_bar = self.findChild(QProgressBar, 'player_health_bar')
        self.player_hud_widget = self.findChild(QWidget, 'player_hud_widget')
        # Opponent HUD
        self.opponent_name_label = self.findChild(QLabel, 'opponent_name_label')
        self.opponent_health_bar = self.findChild(QProgressBar, 'opponent_health_bar')

        self.overlay = OverlayWidget(self)
        self.overlay.hide()
        self._create_keyboard()
        self._setup_pulse_animations()
        self.back_button.clicked.connect(self.handle_back_button_press)
        
        # Set initial names
        if self.main_window and hasattr(self.main_window, 'username') and self.main_window.username:
             self.player_name_label.setText(self.main_window.username)
        else: # Fallback
             self.player_name_label.setText("You")

    def _setup_pulse_animations(self):
        # --- Player Pulse Animation ---
        self.player_shadow_effect = QGraphicsDropShadowEffect(self)
        self.player_shadow_effect.setBlurRadius(20)
        self.player_shadow_effect.setOffset(0, 0)
        self.player_shadow_effect.setColor(QColor(255, 0, 0, 0))
        self.player_hud_widget.setGraphicsEffect(self.player_shadow_effect)

        player_color_anim = QPropertyAnimation(self.player_shadow_effect, b"color")
        player_color_anim.setDuration(1200)
        player_color_anim.setStartValue(QColor(255, 0, 0, 0))
        player_color_anim.setKeyValueAt(0.5, QColor(255, 0, 0, 255))
        player_color_anim.setEndValue(QColor(255, 0, 0, 0))
        
        player_blur_anim = QPropertyAnimation(self.player_shadow_effect, b"blurRadius")
        player_blur_anim.setDuration(1200)
        player_blur_anim.setStartValue(20)
        player_blur_anim.setKeyValueAt(0.5, 60)
        player_blur_anim.setEndValue(20)

        self.player_pulse_group = QParallelAnimationGroup()
        self.player_pulse_group.addAnimation(player_color_anim)
        self.player_pulse_group.addAnimation(player_blur_anim)
        self.player_pulse_group.setLoopCount(-1)

        # --- Opponent Pulse Animation ---
        self.opponent_shadow_effect = QGraphicsDropShadowEffect(self)
        self.opponent_shadow_effect.setBlurRadius(20)
        self.opponent_shadow_effect.setOffset(0, 0)
        self.opponent_shadow_effect.setColor(QColor(255, 0, 0, 0))
        self.opponent_hud_widget.setGraphicsEffect(self.opponent_shadow_effect)

        opponent_color_anim = QPropertyAnimation(self.opponent_shadow_effect, b"color")
        opponent_color_anim.setDuration(1200)
        opponent_color_anim.setStartValue(QColor(255, 0, 0, 0))
        opponent_color_anim.setKeyValueAt(0.5, QColor(255, 0, 0, 255))
        opponent_color_anim.setEndValue(QColor(255, 0, 0, 0))
        
        opponent_blur_anim = QPropertyAnimation(self.opponent_shadow_effect, b"blurRadius")
        opponent_blur_anim.setDuration(1200)
        opponent_blur_anim.setStartValue(20)
        opponent_blur_anim.setKeyValueAt(0.5, 60)
        opponent_blur_anim.setEndValue(20)

        self.opponent_pulse_group = QParallelAnimationGroup()
        self.opponent_pulse_group.addAnimation(opponent_color_anim)
        self.opponent_pulse_group.addAnimation(opponent_blur_anim)
        self.opponent_pulse_group.setLoopCount(-1)

    def _create_keyboard(self):
        kb_v_layout = QVBoxLayout(self.kb_container_widget)
        keyboard_rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        for row_str in keyboard_rows:
            row_h_layout = QHBoxLayout()
            row_h_layout.addStretch()
            for letter in row_str:
                btn = QPushButton(letter)
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
            
            # Set player name from model if available
            player_name = self.controller.model.get_username()
            if player_name:
                self.player_name_label.setText(player_name)

    def handle_back_button_press(self):
        # Delegate to controller if it exists
        if self.controller:
            self.controller.handle_back_to_menu_from_sp_game()
        elif self.main_window: # Fallback
            self.main_window.show_view("MainMenu")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.resize(self.size())

    def paintEvent(self, event):
        """Draw the background image."""
        if self._background_pixmap and not self._background_pixmap.isNull():
            painter = QPainter(self)
            painter.drawPixmap(self.rect(), self._background_pixmap)
        super().paintEvent(event)

    def update_display(self, masked_word, timer_text, incorrect_text, status_text, player_wins, opponent_wins, total_rounds, current_round_num, attempted_letters, current_word_upper, round_over, game_over, timer_color="white", is_new_round=False, round_result_status="ONGOING"):
        # Word
        self.word_label.setText(" ".join(list(masked_word)) if masked_word else "")
        # Timer and Round
        self.timer_label.setText(timer_text)
        self.timer_label.setStyleSheet(f"color: {timer_color};")
        self.round_label.setText(f"Round: {current_round_num}")
        # Status
        self.set_status(status_text)
        # Score
        self.score_label.setText(f"{player_wins} - {opponent_wins}")

        # --- Word Container Style ---
        if self.word_container_widget:
            # Set a dynamic property to be used by the stylesheet
            self.word_container_widget.setProperty("roundStatus", round_result_status.lower())
            
            # Force a style refresh
            self.word_container_widget.style().unpolish(self.word_container_widget)
            self.word_container_widget.style().polish(self.word_container_widget)

        # Health Bars
        health_percent = 100
        opponent_health_percent = 100
        try:
            # Player health based on their incorrect guesses
            match = re.search(r'(\d+)/(\d+)', incorrect_text)
            if match:
                incorrect_guesses = int(match.group(1))
                max_guesses = int(match.group(2))
                health_percent = int(((max_guesses - incorrect_guesses) / max_guesses) * 100)
                self.player_health_bar.setValue(health_percent)

            # Opponent health based on player wins (race to total_rounds)
            if total_rounds > 0:
                opponent_health_percent = int(((total_rounds - player_wins) / float(total_rounds)) * 100)
                self.opponent_health_bar.setValue(opponent_health_percent)

        except (ValueError, TypeError, IndexError):
            self.player_health_bar.setValue(100)
            self.opponent_health_bar.setValue(100)
            
        # Player Health Pulse Animation
        if self.player_pulse_group:
            if health_percent <= 35:
                if self.player_pulse_group.state() != QPropertyAnimation.Running:
                    self.player_pulse_group.start()
            else:
                if self.player_pulse_group.state() == QPropertyAnimation.Running:
                    self.player_pulse_group.stop()
                    self.player_shadow_effect.setColor(QColor(255, 0, 0, 0))

        # Opponent Health Pulse Animation
        if self.opponent_pulse_group:
            if opponent_health_percent <= 35:
                if self.opponent_pulse_group.state() != QPropertyAnimation.Running:
                    self.opponent_pulse_group.start()
            else:
                if self.opponent_pulse_group.state() == QPropertyAnimation.Running:
                    self.opponent_pulse_group.stop()
                    self.opponent_shadow_effect.setColor(QColor(255, 0, 0, 0))
            
        # Keyboard
        self.update_keyboard(attempted_letters, current_word_upper, round_over or game_over, is_new_round)

    def update_keyboard(self, attempted_letters, current_word_upper, disable_all, is_new_round):
        correct_style = "background-color: #4CAF50; color: white; border: 1px solid #388E3C;"
        incorrect_style = "background-color: #f44336; color: white; border: 1px solid #D32F2F;"
        
        if is_new_round:
            for btn in self.keyboard_buttons.values():
                btn.setStyleSheet("")

        for letter, btn in self.keyboard_buttons.items():
            letter_lower = letter.lower()
            btn.setEnabled(not disable_all and letter_lower not in attempted_letters)
            
            if disable_all and current_word_upper and letter_lower in current_word_upper.lower():
                btn.setStyleSheet(correct_style)

    def feedback_guess(self, letter, is_correct):
        btn = self.keyboard_buttons.get(letter.upper())
        if btn:
            style = "background-color: #4CAF50; color: white; border: 1px solid #388E3C;" if is_correct \
                else "background-color: #f44336; color: white; border: 1px solid #D32F2F;"
            btn.setStyleSheet(style)
            btn.setEnabled(False)

    def set_status(self, message, color="#E53935"):
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color};")
    
    def show_match_found_countdown(self, countdown_callback, opponent_name="Opponent", countdown_seconds=5):
        self._close_dialogs()
        self.opponent_name_label.setText(opponent_name)
        self.overlay.resize(self.size())
        self.overlay.show()
        self.overlay.raise_()
        self.match_found_dialog = MatchFoundDialog(opponent_name, countdown_seconds, countdown_callback, self.main_window)
        self.match_found_dialog.exec_()
        self.overlay.hide()

    def show_sp_game_over_dialog(self, result_text, on_ok_callback):
        self._close_dialogs()
        self.overlay.resize(self.size())
        self.overlay.show()
        self.overlay.raise_()
        self.game_over_dialog = GameOverDialog(result_text, on_ok_callback, self.main_window)
        self.game_over_dialog.exec_()
        self.overlay.hide()

    def _close_dialogs(self):
        if self.match_found_dialog and self.match_found_dialog.isVisible(): self.match_found_dialog.accept()
        if self.game_over_dialog and self.game_over_dialog.isVisible(): self.game_over_dialog.accept()
        self.match_found_dialog = None
        self.game_over_dialog = None
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.hide()

    def on_hide_cleanup(self):
        self._close_dialogs()
        if self.player_pulse_group and self.player_pulse_group.state() == QPropertyAnimation.Running:
            self.player_pulse_group.stop()
            self.player_shadow_effect.setColor(QColor(255, 0, 0, 0))
        if self.opponent_pulse_group and self.opponent_pulse_group.state() == QPropertyAnimation.Running:
            self.opponent_pulse_group.stop()
            self.opponent_shadow_effect.setColor(QColor(255, 0, 0, 0))
        self.update_keyboard(set(), "", disable_all=False, is_new_round=True) # Reset keyboard
        self.set_status("Waiting to start...", color="white")
