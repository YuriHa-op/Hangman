from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGridLayout, QFrame, QScrollArea, QDialog, QMessageBox, QSizePolicy, QProgressBar, QGraphicsOpacityEffect, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QRect, QRectF, QPoint, QEasingCurve, QSequentialAnimationGroup, QParallelAnimationGroup
from PyQt5.QtGui import QFont, QIcon, QPainter, QColor, QPen, QPainterPath, QBrush, QPixmap, QRadialGradient, QLinearGradient
from PyQt5 import uic
import os
import math
import random
import traceback
import time
# Import shared effects
from .effects.confetti_effect import ConfettiEffect
from .effects.round_transition_effect import RoundTransitionEffect
# Import dialogs
from .dialogs.multiplayer_dialogs import NotificationWidget, AfkDialog, LastChanceDialog, GameCleanedUpDialog, InfoDialog, MultiplayerGameOverDialog
# Import widgets
from .widgets.multiplayer_widgets import HealthBar, CircularTimer, LetterBox, MaskedWordContainer, PlayerStatusWidget, VirtualKeyboard

# [NOTE: All widget classes (HealthBar, CircularTimer, LetterBox, MaskedWordContainer, PlayerStatusWidget, VirtualKeyboard) have been moved to python_client/views/widgets/multiplayer_widgets.py]

# Importing shared confetti effect
from .effects.confetti_effect import ConfettiEffect

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
        self.last_remaining_time = 60  # Default value
        self.previous_round = None  # Track previous round for animations
        self.round_transition_animation = None  # Animation for round transitions
        self._confetti_effect = None  # Track confetti animation

        # Clean up any existing visual effects that might be leftover from other views
        self.cleanup_all_effects()

        ui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ui', 'qt_multiplayer_game_view.ui')
        uic.loadUi(ui_path, self)
        
        self.setAttribute(Qt.WA_TranslucentBackground) # Make this widget's background transparent

        # Set the window size to 950x950
        self.setMinimumSize(950, 950)
        if self.main_window:
            self.main_window.resize(950, 950)
            
        # Adjust main layout to give more space for panels
        main_layout = self.findChild(QHBoxLayout, 'main_layout')
        if main_layout:
            main_layout.setContentsMargins(10, 10, 10, 10)
            main_layout.setSpacing(15)  # Spacing between left and right panel
            
            # Make the left panel take more space than the right panel
            main_layout.setStretch(0, 7)  # Left panel gets 70% of space
            main_layout.setStretch(1, 3)  # Right panel gets 30% of space

        # Load QSS file
        self.load_style_sheet()

        # Find main containers and widgets
        self.right_panel = self.findChild(QFrame, 'right_panel')
        self.status_label = self.findChild(QLabel, 'status_label')
        self.timer_label = self.findChild(QLabel, 'timer_label')
        self.my_score_label = self.findChild(QLabel, 'my_score_label')
        self.round_label = self.findChild(QLabel, 'round_label')
        self.my_masked_word_label = self.findChild(QLabel, 'my_masked_word_label')
        self.virtual_keyboard_container = self.findChild(QWidget, 'virtual_keyboard_container')
        self.scroll_area_layout = self.findChild(QVBoxLayout, 'scroll_area_layout')
        self.leave_button = self.findChild(QPushButton, 'leave_button')
        self.scroll_area = self.findChild(QScrollArea, 'scroll_area')
        self.top_bar_layout = self.findChild(QHBoxLayout, 'horizontalLayout')
        
        # Create and add Health Bar
        self.health_bar = HealthBar()
        
        # Configure scroll area to show full width of contents (eliminate horizontal scrollbar)
        if self.scroll_area:
            self.scroll_area.setWidgetResizable(True)
            self.scroll_area.setMinimumWidth(290)  # Wider scroll area to fit wider widgets
            self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.scroll_area.setStyleSheet("""
                QScrollArea { 
                    background: transparent;
                    border: none;
                }
                QScrollBar:vertical {
                    background: rgba(255, 255, 255, 0.1);
                    width: 8px;
                    border-radius: 4px;
                }
                QScrollBar::handle:vertical {
                    background: rgba(255, 255, 255, 0.3);
                    border-radius: 4px;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                }
            """)
            
            # Set transparent background for scroll area content
            viewport = self.scroll_area.viewport()
            viewport.setStyleSheet("background: transparent;")
            
            # Add spacing to scroll area layout
            if self.scroll_area_layout:
                self.scroll_area_layout.setContentsMargins(5, 5, 5, 5)
                self.scroll_area_layout.setSpacing(10)
            
        # Make right panel wider
        if self.right_panel:
            self.right_panel.setMinimumWidth(290)
            
        # Style the other players label
        if hasattr(self, 'other_players_label'):
            self.other_players_label.setStyleSheet("""
                color: white;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 10px;
                padding-bottom: 5px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.3);
            """)
            
        # Hide the original masked word label
        self.my_masked_word_label.hide()

        # Create circular timer
        self.timer_container = QWidget()
        self.timer_container.setObjectName("timer_circle_container")
        timer_layout = QHBoxLayout(self.timer_container)
        
        self.circular_timer = CircularTimer()
        self.circular_timer.setText("60s")
        
        timer_layout.addWidget(self.circular_timer)
        timer_layout.setAlignment(Qt.AlignCenter)
        
        # Find the layout containing the timer label and replace it with our circular timer
        left_layout = self.findChild(QVBoxLayout, 'left_layout')
        timer_index = left_layout.indexOf(self.timer_label)
        if timer_index != -1:
            self.timer_label.hide()
            left_layout.insertWidget(timer_index, self.timer_container)

        # Create and add the masked word container
        self.masked_word_container = MaskedWordContainer()
        left_layout_index = left_layout.indexOf(self.my_masked_word_label)
        if left_layout_index != -1:
            left_layout.insertWidget(left_layout_index, self.masked_word_container)

        # Move Health Bar below score
        health_bar_container = QWidget()
        health_bar_layout = QHBoxLayout(health_bar_container)
        health_bar_layout.addStretch()
        health_bar_layout.addWidget(self.health_bar)
        health_bar_layout.addStretch()
        score_index = left_layout.indexOf(self.my_score_label)
        if score_index != -1:
            left_layout.insertWidget(score_index + 1, health_bar_container)

        # Create and set up the Hangman image view
        self.hangman_image_label = QLabel()
        self.hangman_image_label.setAlignment(Qt.AlignCenter)
        self.hangman_image_label.setFixedHeight(150) # Set a fixed, smaller height
        round_label_index = left_layout.indexOf(self.round_label)
        if round_label_index != -1:
            self.round_label.hide()
            left_layout.insertWidget(round_label_index, self.hangman_image_label)

        # Create and add the virtual keyboard
        self.virtual_keyboard = VirtualKeyboard()
        kb_container_layout = QVBoxLayout(self.virtual_keyboard_container)
        kb_container_layout.setContentsMargins(5, 5, 5, 15)  # Reduced horizontal margins and kept bottom margin
        kb_container_layout.addWidget(self.virtual_keyboard)
        
        # Ensure the container is large enough
        self.virtual_keyboard_container.setMinimumHeight(180)  # Set minimum height to fit all rows
        
        # Connect signals
        self.virtual_keyboard.letterClicked.connect(self.make_guess)
        if self.leave_button:
            self.leave_button.clicked.connect(self.confirm_leave_game)
            self.setup_leave_button_icon()

        self.right_panel.hide()
        self.virtual_keyboard.update_keyboard(set(), set(), enabled=False)
        
        # Initialize with a placeholder masked word
        self.masked_word_container.update_word("____")
        
        # Initialize previous guesses tracking
        self._previous_guesses = set()
        
        # Initial state setup
        self.reset_view()

    def load_style_sheet(self):
        """Load QSS stylesheet for the multiplayer game"""
        style_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'style', 'multiplayer.qss')
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                self.setStyleSheet(f.read())
        else:
            print(f"Warning: Style sheet not found at {style_path}")

    def setup_leave_button_icon(self):
        # Go up one level from 'views' to the 'python_client' directory, then into 'assets'
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_path, 'views/assets', 'leave.png')
        if os.path.exists(icon_path):
            self.leave_button.setIcon(QIcon(icon_path))
            # Text is already set to empty in the .ui file, but we can ensure it here.
            self.leave_button.setText("")
            self.leave_button.setToolTip("Leave Game")
        else:
            print(f"Warning: Icon not found at {icon_path}. Displaying text instead.")
            # Fallback text if icon is not found
            self.leave_button.setText("Leave")

    def set_controller(self, controller):
        self.controller = controller

    def make_guess(self, guess):
        if self.controller:
            self.controller.make_guess(guess)
            # No need for additional visual feedback here as the keyboard handles it
            letter_upper = guess.upper()
            self.virtual_keyboard.set_button_pending(letter_upper)

    def confirm_leave_game(self):
        # Create a custom styled dialog instead of using QMessageBox
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        dialog.setAttribute(Qt.WA_TranslucentBackground)
        
        # Create main frame
        frame = QFrame(dialog)
        frame.setObjectName("dialog_frame")
        frame.setStyleSheet("""
            #dialog_frame {
                background-color: rgba(30, 30, 30, 0.95);
                border: 2px solid #3498db;
                border-radius: 10px;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QLabel#title_label {
                color: #3498db;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton#yes_button {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton#yes_button:hover {
                background-color: #c0392b;
            }
            QPushButton#no_button {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton#no_button:hover {
                background-color: #2980b9;
            }
        """)
        
        # Set up layouts
        main_layout = QVBoxLayout(dialog)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(frame)
        
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(15)
        
        # Add title
        title_label = QLabel("Confirm Leave")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(title_label)
        
        # Add message
        message_label = QLabel("Are you sure you want to leave the game? This action cannot be undone.")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        frame_layout.addWidget(message_label)
        
        # Add buttons in a horizontal layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        no_button = QPushButton("No")
        no_button.setObjectName("no_button")
        no_button.setCursor(Qt.PointingHandCursor)
        no_button.clicked.connect(dialog.reject)
        
        yes_button = QPushButton("Yes, Leave Game")
        yes_button.setObjectName("yes_button")
        yes_button.setCursor(Qt.PointingHandCursor)
        
        button_layout.addWidget(no_button)
        button_layout.addWidget(yes_button)
        frame_layout.addLayout(button_layout)
        
        # Set fixed size
        dialog.setFixedSize(400, 200)
        
        # Set up dragging functionality
        old_pos = None
        
        def mousePressEvent(event):
            nonlocal old_pos
            if event.button() == Qt.LeftButton:
                old_pos = event.globalPos()
                event.accept()

        def mouseMoveEvent(event):
            nonlocal old_pos
            if old_pos:
                delta = event.globalPos() - old_pos
                dialog.move(dialog.pos() + delta)
                old_pos = event.globalPos()
                event.accept()

        def mouseReleaseEvent(event):
            nonlocal old_pos
            if event.button() == Qt.LeftButton:
                old_pos = None
                event.accept()
        
        # Connect drag events
        dialog.mousePressEvent = mousePressEvent
        dialog.mouseMoveEvent = mouseMoveEvent
        dialog.mouseReleaseEvent = mouseReleaseEvent
        
        # Connect yes button
        def on_yes_click():
            if self.controller:
                self.controller.leave_game_and_go_back()
            dialog.accept()
        
        yes_button.clicked.connect(on_yes_click)
        
        # Center dialog on parent
        parent_rect = self.geometry()
        dialog.move(
            parent_rect.x() + (parent_rect.width() - dialog.width()) // 2,
            parent_rect.y() + (parent_rect.height() - dialog.height()) // 2
        )
        
        # Show the dialog
        dialog.exec_()

    def back_to_main_menu(self):
        if self.controller:
            self.controller.leave_game_and_go_back()

    def update_view_from_state(self, game_state, current_player_username):
        if not game_state:
            self.reset_view()
            self.status_label.setText("Waiting for game data...")
            return
            
        game_data = game_state.get("gameState")
        if not game_data:
            players = game_state.get("players", [])
            self.status_label.setText(f"In lobby with {len(players)} players. Waiting for game to start...")
            # Only update the new container, old label is hidden
            self.masked_word_container.update_word("____")
            self.virtual_keyboard.update_keyboard([], "", enabled=False)
            self.right_panel.hide()
            return

        # --- Game has started, process game_data ---
        
        # 1. Update own view (left panel)
        remaining_time = game_data.get('remainingTime', 0)
        
        # Update both the original timer label (for compatibility) and the circular timer
        self.timer_label.setText(f"Time: {remaining_time}")
        
        # Check if time has changed before updating circular timer
        if remaining_time != self.last_remaining_time:
            # Find the max round time (for percentage calculation)
            max_time = 60  # Default
            if hasattr(self.controller, 'round_time'):
                max_time = self.controller.round_time
                
            # Calculate percentage
            percentage = min(100, max(0, (remaining_time / max_time) * 100))
            
            # Update circular timer
            self.circular_timer.setValue(percentage)
            self.circular_timer.setText(f"{remaining_time}s")
            
            # Change color based on remaining time thresholds
            if remaining_time <= 5:  # 0-5 seconds left
                self.circular_timer.setColor("#E53935")  # Red for urgent
            elif remaining_time <= 15:  # 5-15 seconds left
                self.circular_timer.setColor("#FFEB3B")  # Yellow for warning
            else:
                self.circular_timer.setColor("#FFFFFF")  # White for normal
            
            # Store the last time
            self.last_remaining_time = remaining_time
            
        current_round = game_data.get('currentRound', 0) + 1
        
        # Check for game winner first - this affects round transition behavior
        game_winner = game_data.get("gameWinner", "")
        
        # FIXED ROUND TRANSITION LOGIC:
        # 1. Don't show transition animation when the view first loads (previous_round is None)
        # 2. Only show transition for actual round changes (not round 0 to 1)
        # 3. Don't show transition if there's a game winner
        # 4. Make sure previous_round is properly initialized
        
        # Initialize previous_round if it's None
        if self.previous_round is None:
            self.previous_round = current_round
        # Only animate if there's a legitimate round change and no game winner
        elif not game_winner and current_round > self.previous_round and self.previous_round > 0:
            try:
                # Make sure we clean up any existing effects first through the main window
                if self.main_window and hasattr(self.main_window, 'cleanup_all_visual_effects'):
                    self.main_window.cleanup_all_visual_effects()
                else:
                    # Fall back to local cleanup
                    self.cleanup_all_effects()
                    
                # Create the transition with proper parent and error handling
                if self.main_window and not self.main_window.isHidden():
                    from .effects.round_transition_effect import RoundTransitionEffect
                    transition_effect = RoundTransitionEffect(self.main_window, text="Next Round")
                    transition_effect.resize(self.main_window.size())
                    transition_effect.start_animation(duration=1000)
            except Exception as e:
                print(f"Failed to show round transition: {str(e)}")
                # Don't store reference if creation failed
            
        # Update previous round after animation check
        self.previous_round = current_round

        # Rest of the method remains unchanged
        scores = game_data.get("scores", {})
        my_score = scores.get(current_player_username, 0)
        self.my_score_label.setText(f"Your Score: {my_score}")

        masked_words = game_data.get("maskedWords", {})
        my_masked_word = masked_words.get(current_player_username, "_ _ _").replace(" ", "")

        # Only update the new masked word container
        self.masked_word_container.update_word(my_masked_word)

        # 2. Determine if player is done with the round and update health
        finish_times = game_data.get("allPlayerFinishTimes", {})
        incorrect_guesses_map = game_data.get("incorrectGuessesMap", {})
        my_incorrects = incorrect_guesses_map.get(current_player_username, 0)
        player_is_done_this_round = (current_player_username in finish_times and finish_times[current_player_username] > 0) or my_incorrects >= 5

        self.health_bar.update_health(my_incorrects)
        self.update_hangman_image(my_incorrects)

        if player_is_done_this_round:
            self.right_panel.show()
            self.health_bar.hide()
        else:
            self.right_panel.hide()
            self.health_bar.show()

        # 3. Update status label based on round/game winner
        round_winner = game_data.get("roundWinner", "")

        # Check for game winner
        if game_winner:
            self.status_label.setText(f"Game Over! Winner is {game_winner}!")
            # Show confetti if current player won the game
            if game_winner == current_player_username and hasattr(self, '_last_game_winner') and self._last_game_winner != game_winner:
                # Use main window's centralized cleanup first
                if self.main_window and hasattr(self.main_window, 'cleanup_all_visual_effects'):
                    self.main_window.cleanup_all_visual_effects()
                    
                self.show_confetti_effect(duration=3000)  # Longer confetti for game win
                
        # Check for round winner
        elif not game_data.get("roundInProgress", True):
            winner_text = f"Round Over! Winner: {round_winner}" if round_winner else "Round Over! No winner."
            self.status_label.setText(winner_text)
            
            # Show confetti if current player won the round and we haven't shown it for this round yet
            if round_winner == current_player_username:
                # Keep track of the last round winner we showed confetti for
                last_round_confetti = getattr(self, '_last_round_confetti', -1)
                if last_round_confetti != current_round:
                    # Use main window's centralized cleanup first
                    if self.main_window and hasattr(self.main_window, 'cleanup_all_visual_effects'):
                        self.main_window.cleanup_all_visual_effects()
                        
                    self.show_confetti_effect(duration=2000)  # Shorter confetti for round win
                    self._last_round_confetti = current_round
        else:
            status_text = f"Round {current_round} in Progress"
            self.status_label.setText(status_text)
            
        # Store last game winner to prevent multiple confetti animations
        self._last_game_winner = game_winner

        # 4. Determine keyboard state
        is_round_in_progress = game_data.get("roundInProgress", True)
        keyboard_enabled = is_round_in_progress and not player_is_done_this_round and not game_winner

        # 5. Update the virtual keyboard based on the player's own guesses
        previous_guesses = set(self.get_previous_guesses(game_state, current_player_username))
        current_guesses = {char.upper() for char in game_data.get("playerGuessesMap", {}).get(current_player_username, [])}
        
        # Determine correctly guessed letters from the masked word, converting to uppercase for comparison
        letters_in_masked_word = {char.upper() for char in my_masked_word if char.isalpha()}

        self.virtual_keyboard.update_keyboard(current_guesses, letters_in_masked_word, enabled=(not player_is_done_this_round))

        # 6. Update opponent panel (right panel)
        all_players_in_game = set(game_state.get("players", []))
        opponents = all_players_in_game - {current_player_username}
        
        current_widgets = set(self.player_status_widgets.keys())
        
        for player in current_widgets - opponents:
            widget = self.player_status_widgets.pop(player)
            widget.deleteLater()
            
        # Get player win streaks
        win_streaks = game_data.get("playerWinStreaks", {})
            
        for player_name in opponents:
            if player_name not in self.player_status_widgets:
                widget = PlayerStatusWidget(player_name)
                self.scroll_area_layout.addWidget(widget)
                self.player_status_widgets[player_name] = widget
            
            widget = self.player_status_widgets[player_name]
            player_score = scores.get(player_name, 0)
            player_masked_word = masked_words.get(player_name, "_ _ _")
            player_incorrects = incorrect_guesses_map.get(player_name, 0)
            player_is_finished = (player_name in finish_times and finish_times[player_name] > 0) or player_incorrects >= 5
            widget.update_widget(player_score, player_masked_word, player_is_finished)
            
            # Update the player's health bar
            widget.update_health(player_incorrects)
            
            # Update win streak and apply golden glow if streak >= 2
            player_streak = win_streaks.get(player_name, 0)
            widget.update_win_streak(player_streak)

    def get_previous_guesses(self, game_state, username):
        """Track previous guesses to detect new ones for feedback"""
        if not hasattr(self, '_previous_guesses'):
            self._previous_guesses = set()
        
        current_guesses = set()
        if game_state and 'gameState' in game_state:
            guesses_map = game_state['gameState'].get('playerGuessesMap', {})
            current_guesses = set(guesses_map.get(username, []))
        
        result = self._previous_guesses
        self._previous_guesses = current_guesses
        return result

    def reset_view(self):
        # Clean up all visual effects first
        self.cleanup_all_effects()
        
        # Reset labels to initial state
        self.status_label.setText("Connecting to game...")
        self.timer_label.setText("Time: -")
        self.my_score_label.setText("Your Score: 0")
        # self.round_label.setText("Round: -") # Replaced by hangman image
        
        # Reset circular timer
        if hasattr(self, 'circular_timer'):
            self.circular_timer.setValue(100)
            self.circular_timer.setText("60s")
            self.circular_timer.setColor("#FFFFFF")  # Changed to white

        # Reset previous round tracking
        self.previous_round = None

        # Reset health bar
        if hasattr(self, 'health_bar'):
            self.health_bar.update_health(0)
            self.health_bar.show()

        # Reset hangman image
        if hasattr(self, 'hangman_image_label'):
            self.update_hangman_image(0)
        
        # Only update the new container, old label is hidden
        self.masked_word_container.update_word("____")
        self.right_panel.hide()
        
        # Reset the virtual keyboard completely
        self.virtual_keyboard.update_keyboard(set(), set(), enabled=False)

        # Thoroughly clear all opponent player widgets
        for widget in list(self.player_status_widgets.values()):
            widget.deleteLater()
        self.player_status_widgets.clear()

        # Close any open dialogs associated with this view
        self.close_all_dialogs()

        # Reset previous guesses tracking
        self._previous_guesses = set()
        
        # Reset win tracking properties
        if hasattr(self, '_last_round_confetti'):
            self._last_round_confetti = -1
        if hasattr(self, '_last_game_winner'):
            self._last_game_winner = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Update hangman image on resize to keep it scaled nicely
        if self.controller and self.controller.model.game_state:
             game_state = self.controller.model.game_state
             game_data = game_state.get("gameState")
             if game_data:
                 my_incorrects = game_data.get("incorrectGuessesMap", {}).get(self.controller.model.username, 0)
                 self.update_hangman_image(my_incorrects)
        else:
            self.update_hangman_image(0)

    def close_all_dialogs(self):
        self.close_afk_dialog()
        self.close_last_chance_dialog()
        self.close_game_cleaned_up_dialog()
        if self._game_over_dialog:
            try:
                self._game_over_dialog.accept()
            finally:
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
        """Show game over dialog with proper cleanup handling"""
        # First clean up any existing effects
        self.cleanup_all_effects()
        
        # Close any existing game over dialog first
        if self._game_over_dialog:
            try:
                # For MultiplayerGameOverDialog, no cleanup_resources method needed
                if hasattr(self._game_over_dialog, 'ok_clicked'):
                    self._game_over_dialog.ok_clicked.disconnect()  # Disconnect any signals
                self._game_over_dialog.accept()
            except:
                pass
            self._game_over_dialog = None
            
        # Use main_window as parent to avoid parent deletion issues
        parent = self.main_window if self.main_window is not None else self
            
        # Create the new, dedicated multiplayer game over dialog
        self._game_over_dialog = MultiplayerGameOverDialog(message, parent)
        
        # Connect the callback directly - no need for the complex safe_callback
        self._game_over_dialog.ok_clicked.connect(on_ok_callback)
        
        # Center on the screen using a more reliable method
        try:
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.geometry()
                x = (screen_geometry.width() - self._game_over_dialog.width()) // 2
                y = (screen_geometry.height() - self._game_over_dialog.height()) // 2
                self._game_over_dialog.move(x, y)
            else: # Fallback
                self._game_over_dialog.move(parent.rect().center() - self._game_over_dialog.rect().center())
        except: # Fallback for older versions or no screen
            self._game_over_dialog.move(parent.rect().center() - self._game_over_dialog.rect().center())

        # Disconnect old dialog reference when this one is done
        def clear_dialog_reference():
            self._game_over_dialog = None
            
        self._game_over_dialog.finished.connect(clear_dialog_reference)
        
        # Show the dialog
        self._game_over_dialog.show()

    def display_game_event(self, event_message):
        # Use main_window as parent so notification appears on top of the whole view
        if not self.main_window: return
        notification = NotificationWidget(self.main_window, event_message)
        notification.show_notification() 

    def update_hangman_image(self, incorrect_guesses):
        image_number = min(incorrect_guesses, 5) # Assuming images are hangman0 to hangman5
        image_path = os.path.join(os.path.dirname(__file__), 'assets', 'hangman', f'hangman{image_number}.png')
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            self.hangman_image_label.setPixmap(pixmap.scaled(
                self.hangman_image_label.width(),
                self.hangman_image_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
        else:
            self.hangman_image_label.setText(f"Image not found: hangman{image_number}.png") 

    def animate_round_transition(self):
        """Animate the round transition with a flash effect"""
        # Don't show round transition if game is over (when there's a game winner)
        if self.controller and self.controller.model and self.controller.model.game_state:
            game_data = self.controller.model.game_state.get("gameState", {})
            if game_data.get("gameWinner"):
                # Skip the round transition animation for the final round
                return
        
        try:
            # First clean up any existing effects through the main window
            if self.main_window and hasattr(self.main_window, 'cleanup_all_visual_effects'):
                self.main_window.cleanup_all_visual_effects()
            else:
                # Fall back to local cleanup
                self.cleanup_all_effects()
                
            # Create and start the round transition animation using main_window as parent
            parent = self.main_window if self.main_window is not None else self
            
            if parent and not parent.isHidden():  # Check if parent is valid and visible
                from .effects.round_transition_effect import RoundTransitionEffect
                transition_effect = RoundTransitionEffect(parent, text="Next Round")
                transition_effect.resize(parent.size())
                transition_effect.start_animation(duration=1000)
        except Exception as e:
            print(f"Failed to show round transition: {str(e)}")
            # We won't store the reference anymore since the effect handles its own lifecycle
            self.round_transition_animation = None

    def show_confetti_effect(self, duration=3000):
        """Show confetti explosion effect on win"""
        try:
            # First clean up any existing effects through the main window
            if self.main_window and hasattr(self.main_window, 'cleanup_all_visual_effects'):
                self.main_window.cleanup_all_visual_effects()
            else:
                # Fall back to local cleanup
                self.cleanup_all_effects()
                
            # Create confetti effect at the game window level (main_window)
            parent = self.main_window if self.main_window is not None else self
            
            if parent and not parent.isHidden():  # Check if parent is valid and visible
                # Create and start the confetti animation using the shared class
                from .effects.confetti_effect import ConfettiEffect
                confetti = ConfettiEffect(parent)
                confetti.resize(parent.size())
                confetti.start_animation(duration)
                
                # Set a timer to ensure cleanup even if the animation doesn't clean itself up
                QTimer.singleShot(duration + 500, lambda: self._ensure_confetti_cleanup())
        except Exception as e:
            # Only show non-"wrapped C/C++ object" errors
            if "wrapped C/C++ object" not in str(e):
                print(f"Error showing confetti effect: {str(e)}")
            
    def _ensure_confetti_cleanup(self):
        """Ensure confetti is cleaned up after animation"""
        try:
            # Use the class-level cleanup method
            from .effects.confetti_effect import ConfettiEffect
            ConfettiEffect.cleanup_all_instances()
        except Exception as e:
            if "wrapped C/C++ object" not in str(e):
                print(f"Error during confetti cleanup: {str(e)}")

    def cleanup_all_effects(self):
        """Clean up all visual effects that may be lingering from other views.
        This is a more robust cleanup that actively looks for effect widgets."""
        try:
            parent = self.main_window if self.main_window is not None else self
            if not parent:
                return

            # --- Robustly clean up ConfettiEffect instances ---
            try:
                from .effects.confetti_effect import ConfettiEffect
                # Use the class-level cleanup first, as it's the designed way
                ConfettiEffect.cleanup_all_instances()
                
                # As a fallback, manually find and destroy any lingering instances
                for confetti_widget in parent.findChildren(ConfettiEffect):
                    if confetti_widget:
                        confetti_widget.stop_animation()
            except Exception as e:
                print(f"Error during robust cleanup of confetti effects: {e}")

            # --- Robustly clean up RoundTransitionEffect instances ---
            try:
                from .effects.round_transition_effect import RoundTransitionEffect
                # Use the class-level cleanup first
                RoundTransitionEffect.cleanup_all_instances()

                # Fallback manual cleanup
                for transition_widget in parent.findChildren(RoundTransitionEffect):
                    if transition_widget:
                        transition_widget.cleanup()
            except Exception as e:
                print(f"Error during robust cleanup of round transition effects: {e}")

            # --- Clean up local references ---
            self.round_transition_animation = None
            self._confetti_effect = None
        except Exception as e:
            # Catch errors if main_window or other objects are already deleted
            if "wrapped C/C++ object" not in str(e):
                print(f"Error in robust cleanup_all_effects: {e}")

    def hideEvent(self, event):
        """Ensure proper cleanup when the view is hidden"""
        # First clean up all effects
        self.cleanup_all_effects()
        # Then clean up the view itself
        self.reset_view()
        super().hideEvent(event)
        
    def closeEvent(self, event):
        """Ensure proper cleanup when the view is closed"""
        # First clean up all effects
        self.cleanup_all_effects()
        # Then clean up the view itself
        self.reset_view()
        super().closeEvent(event)

    def showEvent(self, event):
        """Handle actions when view is shown"""
        super().showEvent(event)
        # Clean up any existing visual effects when view is shown
        self.cleanup_all_effects()
        # Reset tracking variables
        self.previous_round = None
        self._last_round_confetti = -1
        self._last_game_winner = None
