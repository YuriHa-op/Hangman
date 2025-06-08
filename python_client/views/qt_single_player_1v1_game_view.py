from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QMessageBox, QDialog, QApplication, QProgressBar, QGraphicsDropShadowEffect, QFrame)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QParallelAnimationGroup, QMargins, QEasingCurve, QPoint, QSize
from PyQt5.QtGui import QFont, QPainter, QPixmap, QFontDatabase, QColor, QPalette, QBrush, QLinearGradient
from PyQt5 import uic
import os
import re
import traceback
# Import shared effects
from .effects.confetti_effect import ConfettiEffect
from .effects.round_transition_effect import RoundTransitionEffect

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

        # Add pulsing effect
        self.pulse_effect = QPropertyAnimation(self, b"windowOpacity")
        self.pulse_effect.setDuration(1000)
        self.pulse_effect.setStartValue(0.9)
        self.pulse_effect.setEndValue(1.0)
        self.pulse_effect.setLoopCount(-1)
        self.pulse_effect.setEasingCurve(QEasingCurve.InOutQuad)
        self.pulse_effect.start()

    def update_countdown(self):
        self.remaining_seconds -= 1
        if self.remaining_seconds > 0:
            self.countdown_label.setText(f"Battle Begins in {self.remaining_seconds}...")
        else:
            self.pulse_effect.stop()
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

        # Add animation for game over dialog
        self.setWindowOpacity(0)
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(800)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_in.start()

    def accept_and_callback(self):
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(500)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0)
        self.fade_out.setEasingCurve(QEasingCurve.InCubic)
        self.fade_out.finished.connect(self._handle_fade_out_complete)
        self.fade_out.start()
    
    def _handle_fade_out_complete(self):
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

class FeedbackPopup(QLabel):
    """Label used for feedback animations when user makes a guess"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAlignment(Qt.AlignCenter)
        
        # Setup shadow for better visibility
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 160))
        self.setGraphicsEffect(shadow)
        
        self.hide()
        
    def show_feedback(self, text, color, target_pos):
        """Show animated feedback at position"""
        self.setText(text)
        self.setStyleSheet(f"""
            color: {color};
            font-size: 18px;  /* Smaller font */
            font-weight: bold;
            background-color: transparent;
        """)
        
        # Position above the target button
        self.adjustSize()
        self.move(target_pos.x() - self.width()//2, target_pos.y() - self.height() - 15)
        self.show()
        
        # Setup animations
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(600)  # Shorter duration
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setKeyValueAt(0.2, 1.0) 
        self.fade_anim.setEndValue(0.0)
        
        self.move_anim = QPropertyAnimation(self, b"pos")
        self.move_anim.setDuration(600)  # Shorter duration
        self.move_anim.setStartValue(self.pos())
        self.move_anim.setEndValue(QPoint(self.pos().x(), self.pos().y() - 30))
        
        self.anim_group = QParallelAnimationGroup()
        self.anim_group.addAnimation(self.fade_anim)
        self.anim_group.addAnimation(self.move_anim)
        self.anim_group.finished.connect(self.hide)
        self.anim_group.start()



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
        self.feedback_popup = None
        self.keyboard_reset_needed = True
        self.last_known_total_seconds = 30  # Store this for timer calculations
        self._last_round_confetti = -1  # Track the last round we displayed confetti for
        self._last_player_score = 0  # Track the player's score to detect increases
        self._previous_round_number = -1  # Track the previous round number for transitions
        
        # --- Paths & UI Load ---
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(base_dir, 'ui', 'qt_single_player_1v1_game_view.ui')
        style_path = os.path.join(base_dir, 'style', 'single_player_1v1_game.qss')
        font_path = os.path.join(base_dir, 'fonts', 'JujutsuKaisen.ttf')
        background_path = os.path.join(base_dir, 'assets', '1v1.png')
        uic.loadUi(ui_path, self)

        # --- Font Loading ---
        self._load_fonts(base_dir)
        
        # --- Background and Stylesheets ---
        self._background_pixmap = QPixmap(background_path)
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
        self.opponent_hud_widget = self.findChild(QWidget, 'opponent_hud_widget')

        # --- Initialize UI Components ---
        self.overlay = OverlayWidget(self)
        self.overlay.hide()
        self.feedback_popup = FeedbackPopup(self)
        
        # --- Simple Timer Text ---
        timer_layout = QHBoxLayout()
        timer_layout.setSpacing(2)  # Reduce spacing
        # Add a small fixed spacer (2px) to move the timer slightly to the right
        timer_layout.addSpacing(2)
        self.timer_text = QLabel("30s", self)
        self.timer_text.setStyleSheet("color: white; font-weight: bold; font-size: 28px;")  # Larger font
        self.timer_text.setAlignment(Qt.AlignCenter)
        timer_layout.addWidget(self.timer_text)
        timer_layout.addStretch()
        
        # Add timer to the top of the central score area instead of top_info_layout
        timer_container = QWidget()
        timer_container.setLayout(timer_layout)
        
        # Hide the original timer label
        self.timer_label.hide()
        
        # Insert the timer into the huds_layout above the score_label
        huds_layout = self.findChild(QHBoxLayout, 'huds_layout')
        if huds_layout:
            # Create a vertical layout for the center column
            center_layout = QVBoxLayout()
            center_layout.addWidget(timer_container)
            center_layout.addWidget(self.score_label)
            center_layout.setAlignment(Qt.AlignCenter)
            center_layout.setContentsMargins(0, 0, 0, 0)
            center_layout.setSpacing(8)  # Add space between timer and score
            
            # Enhance score label
            self.score_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #FFD700;")
            
            # Remove score_label from its original position
            huds_layout.removeWidget(self.score_label)
            
            # Create a container for the center column
            center_container = QWidget()
            center_container.setLayout(center_layout)
            
            # Add the center container to the huds_layout at index 1 (middle position)
            huds_layout.insertWidget(1, center_container)
        
        # Configure the word container to be smaller
        self.word_container_widget.setFixedHeight(100)  # Set fixed height to match the red area in the image
        self.word_container_widget.setMaximumWidth(650)  # Limit width
        
        # Center the word container
        word_layout = self.word_container_widget.layout()
        if word_layout:
            word_layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins to make it more compact
            
        # Adjust word label font size and styling to fit the smaller container
        self.word_label.setStyleSheet("""
            font-size: 32px; 
            font-weight: bold;
            letter-spacing: 8px;
            color: #FFFFFF;
        """)
        self.word_label.setAlignment(Qt.AlignCenter)  # Ensure text is centered
        
        # For better centering, make sure the word_label gets enough space in the layout
        if word_layout:
            word_layout.setAlignment(self.word_label, Qt.AlignCenter)
        
        # Set fixed container margins instead of content margins
        if self.word_container_widget and self.word_container_widget.layout():
            self.word_container_widget.layout().setContentsMargins(20, 20, 20, 20)
        
        # Center the word container in the main layout
        main_layout = self.findChild(QVBoxLayout, 'main_layout')
        if main_layout:
            index = main_layout.indexOf(self.word_container_widget)
            if index >= 0:
                main_layout.setAlignment(self.word_container_widget, Qt.AlignCenter)
        
        # Center the names in the HP bars
        self.player_name_label.setAlignment(Qt.AlignCenter)
        self.opponent_name_label.setAlignment(Qt.AlignCenter)
        
        # Move round counter to top of timer in center layout
        if huds_layout:
            # First, remove round_label from its current position
            top_info_layout = self.findChild(QHBoxLayout, 'top_info_layout')
            if top_info_layout:
                top_info_layout.removeWidget(self.round_label)
                
            # Set larger font for round label
            self.round_label.setStyleSheet("font-size: 18px; font-weight: bold;")
            
            # Insert round label at the top of center layout
            center_layout.insertWidget(0, self.round_label)

        self._create_keyboard()
        self._setup_hud_animations()
        self.back_button.clicked.connect(self.handle_back_button_press)
        
        # Set initial names
        if self.main_window and hasattr(self.main_window, 'username') and self.main_window.username:
             self.player_name_label.setText(self.main_window.username)
        else: # Fallback
             self.player_name_label.setText("You")

    def _load_fonts(self, base_dir):
        """Load modern and themed fonts"""
        # JJK themed font
        jjk_font_path = os.path.join(base_dir, 'fonts', 'JujutsuKaisen.ttf')
        font_id = QFontDatabase.addApplicationFont(jjk_font_path)
        if font_id == -1: 
            print("Failed to load JujutsuKaisen.ttf font.")
        
        # Try to load Inter/Roboto or other modern fonts if available
        modern_fonts_dir = os.path.join(base_dir, 'fonts', 'modern')
        try:
            if os.path.exists(modern_fonts_dir):
                for font_file in os.listdir(modern_fonts_dir):
                    if font_file.endswith('.ttf') or font_file.endswith('.otf'):
                        font_path = os.path.join(modern_fonts_dir, font_file)
                        font_id = QFontDatabase.addApplicationFont(font_path)
                        if font_id != -1:
                            print(f"Successfully loaded font: {font_file}")
        except Exception as e:
            print(f"Error loading modern fonts: {e}")

    def _setup_hud_animations(self):
        # --- Player HUD Animations ---
        self._setup_hud_pulse_animation(self.player_hud_widget, "player")
        
        # --- Opponent HUD Animations ---
        self._setup_hud_pulse_animation(self.opponent_hud_widget, "opponent")
        
        # --- Health Bar Animations ---
        self._setup_health_bar_animation(self.player_health_bar)
        self._setup_health_bar_animation(self.opponent_health_bar)

    def _setup_health_bar_animation(self, health_bar):
        # Store current value to animate from
        health_bar.previous_value = health_bar.value()
        
        # Save original setValue method
        health_bar.original_setValue = health_bar.setValue
        
        # Override setValue to animate transitions
        def animated_setValue(value):
            # Create animation only if there's a significant change
            if abs(health_bar.previous_value - value) > 3:
                anim = QPropertyAnimation(health_bar, b"value")
                anim.setDuration(500)  # Faster animation
                anim.setStartValue(health_bar.previous_value)
                anim.setEndValue(value)
                anim.setEasingCurve(QEasingCurve.OutQuad)
                anim.start()
            else:
                health_bar.original_setValue(value)
            health_bar.previous_value = value
                
        health_bar.setValue = animated_setValue

    def _setup_hud_pulse_animation(self, hud_widget, name_prefix):
        # Create shadow effect for glow
        shadow_effect = QGraphicsDropShadowEffect(self)
        shadow_effect.setBlurRadius(20)
        shadow_effect.setOffset(0, 0)
        shadow_effect.setColor(QColor(255, 0, 0, 0))
        hud_widget.setGraphicsEffect(shadow_effect)

        # Create color animation
        color_anim = QPropertyAnimation(shadow_effect, b"color")
        color_anim.setDuration(1000)  # Faster animation
        color_anim.setStartValue(QColor(255, 0, 0, 0))
        color_anim.setKeyValueAt(0.5, QColor(255, 0, 0, 255))
        color_anim.setEndValue(QColor(255, 0, 0, 0))
        
        # Create blur radius animation
        blur_anim = QPropertyAnimation(shadow_effect, b"blurRadius")
        blur_anim.setDuration(1000)  # Faster animation
        blur_anim.setStartValue(15)  # Smaller blur
        blur_anim.setKeyValueAt(0.5, 40)  # Smaller peak blur
        blur_anim.setEndValue(15)  # Smaller blur

        # Create animation group
        pulse_group = QParallelAnimationGroup()
        pulse_group.addAnimation(color_anim)
        pulse_group.addAnimation(blur_anim)
        pulse_group.setLoopCount(-1)

        # Store references 
        setattr(self, f"{name_prefix}_shadow_effect", shadow_effect)
        setattr(self, f"{name_prefix}_pulse_group", pulse_group)

    def _create_keyboard(self):
        kb_v_layout = QVBoxLayout(self.kb_container_widget)
        kb_v_layout.setSpacing(3)  # Reduce spacing between rows
        kb_v_layout.setContentsMargins(10, 5, 10, 5)  # Smaller margins
        keyboard_rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        for row_str in keyboard_rows:
            row_h_layout = QHBoxLayout()
            row_h_layout.setSpacing(2)  # Reduce spacing between buttons
            row_h_layout.addStretch()
            for letter in row_str:
                btn = QPushButton(letter)
                # Connect button click to both letter guess and visual feedback
                btn.clicked.connect(lambda checked, letter=letter, btn=btn: 
                                   self._handle_keyboard_button_click(letter, btn))
                row_h_layout.addWidget(btn)
                self.keyboard_buttons[letter] = btn
            row_h_layout.addStretch()
            kb_v_layout.addLayout(row_h_layout)

    def _handle_keyboard_button_click(self, letter, btn):
        # Play button press animation
        self._animate_button_press(btn)
        
        # Pass the letter to the controller
        if self.controller:
            self.controller.handle_single_player_guess(letter)
    
    def _animate_button_press(self, button):
        """Animate button press with scaling effect"""
        anim = QPropertyAnimation(button, b"geometry")
        anim.setDuration(100)  # Faster animation
        orig_geom = button.geometry()
        
        # Create a slightly smaller geometry for the "pressed" state
        smaller = orig_geom.adjusted(2, 2, -2, -2)
        
        anim.setStartValue(orig_geom)
        anim.setEndValue(smaller)
        anim.setKeyValueAt(0.5, smaller)
        anim.setEndValue(orig_geom)
        anim.setEasingCurve(QEasingCurve.OutInQuad)
        anim.start()

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
        # Animate button press
        self._animate_button_press(self.back_button)
        
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

    def show_confetti_effect(self, duration=2000):
        """Show confetti explosion effect on win"""
        try:
            # Create confetti effect at the game window level (main_window)
            parent = self.main_window if self.main_window is not None else self
            
            # Create and start the confetti animation
            confetti = ConfettiEffect(parent)
            confetti.resize(parent.size())
            confetti.start_animation(duration)
        except Exception as e:
            print(f"Error showing confetti effect: {str(e)}")
            traceback.print_exc()
            
    def update_display(self, masked_word, timer_text, incorrect_text, status_text, player_wins, opponent_wins, total_rounds, current_round_num, attempted_letters, current_word_upper, round_over, game_over, timer_color="white", is_new_round=False, round_result_status="ONGOING"):
        # Check for round transitions - animate when the round number increases
        if current_round_num > self._previous_round_number and self._previous_round_number > 0:
            self.animate_round_transition()
        
        # Update the round tracking variable
        self._previous_round_number = current_round_num
        
        # When a new round starts, set timer to full
        if is_new_round and hasattr(self, 'timer_text') and self.timer_text is not None:
            total_seconds = 30  # Default
            if self.controller and hasattr(self.controller, 'full_round_time'):
                total_seconds = self.controller.full_round_time
                self.last_known_total_seconds = total_seconds  # Update stored value
            else:
                total_seconds = self.last_known_total_seconds  # Use stored value
                
            self.timer_text.setText(f"{total_seconds}s")
            self.timer_text.setStyleSheet("color: white; font-weight: bold; font-size: 28px;")  # Reset color
            
        # Show confetti when score increases (player wins a round)
        if player_wins > self._last_player_score:
            self.show_confetti_effect()
            self._last_round_confetti = current_round_num
        
        # Update the last known score
        self._last_player_score = player_wins
            
        # Word
        if masked_word:
            # Use a wider space for better visibility of individual characters
            spaced_word = " ".join(list(masked_word))
            self.word_label.setText(spaced_word)
            
            # Don't set minimum width as it might be causing crashes
            # self.word_label.setMinimumWidth(self.word_container_widget.width() * 0.9)
        else:
            self.word_label.setText("")
        
        # Timer - update text timer
        match = re.search(r'(\d+)', timer_text)
        if match and hasattr(self, 'timer_text') and self.timer_text is not None:
            remaining_seconds = int(match.group(1))
            # Get the actual round time from controller
            if self.controller and hasattr(self.controller, 'full_round_time'):
                total_seconds = self.controller.full_round_time
                self.last_known_total_seconds = total_seconds  # Update stored value
            else:
                total_seconds = self.last_known_total_seconds  # Use stored value
            
            # Special case: at the start of a round, the timer might show "--" 
            # In that case, set to full
            if timer_text == "Time: --":
                remaining_seconds = total_seconds
                
            # Update timer text
            self.timer_text.setText(f"{remaining_seconds}s")
            
            # Update timer color based on remaining time
            if remaining_seconds <= 5:
                self.timer_text.setStyleSheet("color: #E53935; font-weight: bold; font-size: 28px;")  # Red for urgent
            elif remaining_seconds <= 15:
                self.timer_text.setStyleSheet("color: #FFEB3B; font-weight: bold; font-size: 28px;")  # Yellow for warning
            else:
                self.timer_text.setStyleSheet("color: white; font-weight: bold; font-size: 28px;")  # White for normal
                
        elif timer_text == "Time: --" and hasattr(self, 'timer_text') and self.timer_text is not None:
            # When timer shows "--", show it as full
            if self.controller and hasattr(self.controller, 'full_round_time'):
                total_seconds = self.controller.full_round_time
                self.last_known_total_seconds = total_seconds  # Update stored value
            else:
                total_seconds = self.last_known_total_seconds  # Use stored value
            self.timer_text.setText(f"{total_seconds}s")
            self.timer_text.setStyleSheet("color: white; font-weight: bold; font-size: 28px;")  # Reset color
        
        # Round
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
                opponent_health_percent = int(((total_rounds - player_wins) / total_rounds) * 100)
                self.opponent_health_bar.setValue(opponent_health_percent)

        except (ValueError, TypeError, IndexError):
            self.player_health_bar.setValue(100)
            self.opponent_health_bar.setValue(100)
            
        # Player Health Pulse Animation
        if hasattr(self, 'player_pulse_group') and self.player_pulse_group:
            if health_percent <= 35:
                if self.player_pulse_group.state() != QPropertyAnimation.Running:
                    self.player_pulse_group.start()
            else:
                if self.player_pulse_group.state() == QPropertyAnimation.Running:
                    self.player_pulse_group.stop()
                    self.player_shadow_effect.setColor(QColor(255, 0, 0, 0))

        # Opponent Health Pulse Animation
        if hasattr(self, 'opponent_pulse_group') and self.opponent_pulse_group:
            if opponent_health_percent <= 35:
                if self.opponent_pulse_group.state() != QPropertyAnimation.Running:
                    self.opponent_pulse_group.start()
            else:
                if self.opponent_pulse_group.state() == QPropertyAnimation.Running:
                    self.opponent_pulse_group.stop()
                    self.opponent_shadow_effect.setColor(QColor(255, 0, 0, 0))
        
        # Reset keyboard on new round
        if is_new_round and self.keyboard_reset_needed:
            self.update_keyboard(set(), "", disable_all=False, is_new_round=True)
            self.keyboard_reset_needed = False
        else:
            # Regular keyboard update
            self.update_keyboard(attempted_letters, current_word_upper, round_over or game_over, is_new_round)
            
            # Mark keyboard as needing reset for next round
            if round_over:
                self.keyboard_reset_needed = True

    def update_keyboard(self, attempted_letters, current_word_upper, disable_all, is_new_round):
        if is_new_round:
            for letter, btn in self.keyboard_buttons.items():
                btn.setEnabled(True)
                btn.setProperty("correct", None)
                btn.setProperty("incorrect", None)
                btn.setStyleSheet("")  # Reset style
                btn.style().unpolish(btn)
                btn.style().polish(btn)

        for letter, btn in self.keyboard_buttons.items():
            letter_lower = letter.lower()
            btn.setEnabled(not disable_all and letter_lower not in attempted_letters)
            
            if disable_all and current_word_upper and letter_lower in current_word_upper.lower():
                btn.setProperty("correct", True)
                btn.setProperty("incorrect", None)
            elif letter_lower in attempted_letters and current_word_upper and letter_lower not in current_word_upper.lower():
                btn.setProperty("correct", None)
                btn.setProperty("incorrect", True)
                
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def feedback_guess(self, letter, is_correct):
        btn = self.keyboard_buttons.get(letter.upper())
        if btn:
            # Set button style
            btn.setProperty("correct", is_correct)
            btn.setProperty("incorrect", not is_correct)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.setEnabled(False)

            # Show animated popup feedback
            text = "✓ Correct!" if is_correct else "✗ Wrong!"
            color = "#4CAF50" if is_correct else "#E53935"
            global_pos = btn.mapToGlobal(QPoint(btn.width() // 2, 0))
            local_pos = self.mapFromGlobal(global_pos)
            self.feedback_popup.show_feedback(text, color, local_pos)

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
        if self.match_found_dialog and self.match_found_dialog.isVisible():
            self.match_found_dialog.accept()
        if self.game_over_dialog and self.game_over_dialog.isVisible():
            self.game_over_dialog.accept()
        self.match_found_dialog = None
        self.game_over_dialog = None
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.hide()

    def on_hide_cleanup(self):
        self._close_dialogs()
        if hasattr(self, 'player_pulse_group') and self.player_pulse_group and self.player_pulse_group.state() == QPropertyAnimation.Running:
            self.player_pulse_group.stop()
            self.player_shadow_effect.setColor(QColor(255, 0, 0, 0))
        if hasattr(self, 'opponent_pulse_group') and self.opponent_pulse_group and self.opponent_pulse_group.state() == QPropertyAnimation.Running:
            self.opponent_pulse_group.stop()
            self.opponent_shadow_effect.setColor(QColor(255, 0, 0, 0))
        self.update_keyboard(set(), "", disable_all=False, is_new_round=True) # Reset keyboard
        self.set_status("Waiting to start...", color="white")
        self.keyboard_reset_needed = True  # Reset flag
        self._last_round_confetti = -1  # Reset confetti tracking
        self._last_player_score = 0  # Reset score tracking
        self._previous_round_number = -1  # Reset round number tracking

    def animate_round_transition(self):
        """Show a round transition animation between rounds"""
        # Create and start the round transition animation
        parent = self.main_window if self.main_window is not None else self
        transition_effect = RoundTransitionEffect(parent, text="Next Round")
        transition_effect.resize(parent.size())
        transition_effect.start_animation(duration=1000)
