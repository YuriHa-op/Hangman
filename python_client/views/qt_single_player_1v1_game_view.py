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

class GameOverDialog(QDialog):
    def __init__(self, result_text, on_ok_callback, parent=None):
        super().__init__(parent)
        self.on_ok_callback = on_ok_callback
        self.button_clicked = False  # Flag to prevent multiple clicks
        
        # Set window flags for frameless window with translucent background
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create content frame
        self.frame = QFrame()
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(30, 30, 30, 30)
        frame_layout.setSpacing(20)
        
        # Determine if this is a win or loss
        is_win = "Win" in result_text or "won" in result_text.lower()
        
        # Style the frame based on result
        if is_win:
            self.frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(0, 0, 0, 0.9);
                    border: 3px solid #FFD700;
                    border-radius: 15px;
                }
            """)
            title_color = "#FFD700"  # Gold for win
            button_color = "#D4AF37"
            button_hover = "#FFD700"
            title_text = "VICTORY!"
            message_text = "You've won the duel!"
        else:
            self.frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(0, 0, 0, 0.9);
                    border: 3px solid #C0392B;
                    border-radius: 15px;
                }
            """)
            title_color = "#C0392B"  # Red for loss
            button_color = "#922B21"
            button_hover = "#C0392B"
            title_text = "DEFEAT"
            message_text = "Better luck next time!"
        
        # Create title label
        self.title_label = QLabel(title_text)
        self.title_label.setStyleSheet(f"""
            font-size: 36px;
            font-weight: bold;
            font-family: 'JujutsuKaisen', Arial, sans-serif;
            color: {title_color};
            text-align: center;
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        
        # Create result label
        self.result_label = QLabel(result_text)
        self.result_label.setStyleSheet("""
            font-size: 18px;
            color: white;
            text-align: center;
        """)
        self.result_label.setAlignment(Qt.AlignCenter)
        
        # Create message label
        self.message_label = QLabel(message_text)
        self.message_label.setStyleSheet("""
            font-size: 16px;
            color: #CCCCCC;
            text-align: center;
        """)
        self.message_label.setAlignment(Qt.AlignCenter)
        
        # Create button
        self.ok_button = QPushButton("Continue")
        self.ok_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {button_color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {button_hover};
            }}
            QPushButton:pressed {{
                background-color: {button_color};
            }}
            QPushButton:disabled {{
                background-color: #555555;
            }}
        """)
        self.ok_button.setCursor(Qt.PointingHandCursor)
        self.ok_button.clicked.connect(self.accept_safely)
        
        # Add widgets to layout
        frame_layout.addWidget(self.title_label)
        frame_layout.addWidget(self.result_label)
        frame_layout.addWidget(self.message_label)
        frame_layout.addStretch()
        frame_layout.addWidget(self.ok_button)
        
        # Add frame to main layout
        main_layout.addWidget(self.frame)
        
        # Set size
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        
        # For dragging
        self.old_pos = None
        
        # Center on parent
        if parent:
            self.move(parent.rect().center() - self.rect().center())
            
        # Add animation for game over dialog
        self.setWindowOpacity(0)
        self.fade_in = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in.setDuration(800)
        self.fade_in.setStartValue(0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_in.start()
        
        # Add bounce animation for title
        self.title_animation = QPropertyAnimation(self.title_label, b"pos")
        self.title_animation.setDuration(1000)
        pos = self.title_label.pos()
        self.title_animation.setKeyValueAt(0.0, QPoint(pos.x(), pos.y() - 20))
        self.title_animation.setKeyValueAt(0.5, QPoint(pos.x(), pos.y() + 10))
        self.title_animation.setKeyValueAt(0.7, QPoint(pos.x(), pos.y() - 5))
        self.title_animation.setKeyValueAt(1.0, QPoint(pos.x(), pos.y()))
        self.title_animation.setEasingCurve(QEasingCurve.OutBounce)
        QTimer.singleShot(100, self.title_animation.start)

    def accept_safely(self):
        """Handle accepting the dialog safely with animation"""
        if self.button_clicked:
            return
            
        self.button_clicked = True
        self.ok_button.setEnabled(False)
        self.ok_button.setText("Please wait...")
        
        self.fade_out = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out.setDuration(500)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0)
        self.fade_out.setEasingCurve(QEasingCurve.InCubic)
        self.fade_out.finished.connect(self._handle_fade_out_complete)
        self.fade_out.start()
    
    def _handle_fade_out_complete(self):
        # Clean up animations to prevent memory leaks
        if hasattr(self, 'fade_in') and self.fade_in:
            self.fade_in.stop()
        if hasattr(self, 'fade_out') and self.fade_out:
            self.fade_out.stop()
        if hasattr(self, 'title_animation') and self.title_animation:
            self.title_animation.stop()
            
        # Accept the dialog (close it)
        self.accept()
        
        # Call the callback only after closing
        if self.on_ok_callback:
            try:
                # The view's hideEvent/on_hide_cleanup is the correct place for cleanup logic
                self.on_ok_callback()
            except Exception as e:
                print(f"Error in game over dialog callback: {e}")
                import traceback
                traceback.print_exc()

    def closeEvent(self, event):
        """Clean up resources when dialog is closed"""
        self.cleanup_resources()
        super().closeEvent(event)
        
    def cleanup_resources(self):
        """Clean up all animations and resources"""
        try:
            # Stop animations to prevent memory leaks
            if hasattr(self, 'fade_in') and self.fade_in:
                self.fade_in.stop()
                self.fade_in = None
                
            if hasattr(self, 'fade_out') and self.fade_out:
                self.fade_out.stop()
                self.fade_out = None
                
            if hasattr(self, 'title_animation') and self.title_animation:
                self.title_animation.stop()
                self.title_animation = None
                
            # Clear callback reference to prevent circular references
            self.on_ok_callback = None
        except Exception as e:
            print(f"Error cleaning up dialog resources: {e}")
    
    def reject(self):
        """Override reject to ensure cleanup"""
        self.cleanup_resources()
        super().reject()

    def mousePressEvent(self, event):
        """Enable dragging the dialog"""
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
            event.accept()

    def mouseMoveEvent(self, event):
        """Move the dialog when dragged"""
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPos()
            event.accept()

    def mouseReleaseEvent(self, event):
        """Stop dragging when mouse is released"""
        if event.button() == Qt.LeftButton:
            self.old_pos = None
            event.accept()

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
        
        # Clean up any existing visual effects before initializing
        self.cleanup_all_effects()
        
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

    def cleanup_all_effects(self):
        """Clean up all visual effects that may be lingering.
        This is a more robust cleanup that actively looks for effect widgets."""
        try:
            parent = self.main_window if self.main_window is not None else self
            if not parent:
                return

            # --- Robustly clean up ConfettiEffect instances ---
            try:
                from .effects.confetti_effect import ConfettiEffect
                ConfettiEffect.cleanup_all_instances()
                # Fallback manual cleanup
                for confetti_widget in parent.findChildren(ConfettiEffect):
                    if confetti_widget:
                        confetti_widget.stop_animation()
            except Exception as e:
                print(f"Error during robust cleanup of confetti effects: {e}")

            # --- Robustly clean up RoundTransitionEffect instances ---
            try:
                from .effects.round_transition_effect import RoundTransitionEffect
                RoundTransitionEffect.cleanup_all_instances()
                # Fallback manual cleanup
                for transition_widget in parent.findChildren(RoundTransitionEffect):
                    if transition_widget:
                        transition_widget.cleanup()
            except Exception as e:
                print(f"Error during robust cleanup of round transition effects: {e}")
        except Exception as e:
            if "wrapped C/C++ object" not in str(e):
                print(f"Error in robust cleanup_all_effects: {e}")

    def show_confetti_effect(self, duration=2000):
        """Show confetti explosion effect on win"""
        try:
            # First clean up any existing effects using the main window
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

    def animate_round_transition(self):
        """Show a round transition animation between rounds"""
        try:
            # First clean up any existing effects using the main window
            if self.main_window and hasattr(self.main_window, 'cleanup_all_visual_effects'):
                self.main_window.cleanup_all_visual_effects()
            else:
                # Fall back to local cleanup
                self.cleanup_all_effects()
            
            # Create and start the round transition animation
            parent = self.main_window if self.main_window is not None else self
            
            if parent and not parent.isHidden():  # Check if parent is valid and visible
                from .effects.round_transition_effect import RoundTransitionEffect
                transition_effect = RoundTransitionEffect(parent, text="Next Round")
                transition_effect.resize(parent.size())
                transition_effect.start_animation(duration=1000)
        except Exception as e:
            print(f"Error showing round transition: {str(e)}")

    def hideEvent(self, event):
        """Clean up when view is hidden"""
        self.cleanup_all_effects()
        self.on_hide_cleanup()
        super().hideEvent(event)
        
    def showEvent(self, event):
        """Clean up when view is shown"""
        self.cleanup_all_effects()
        super().showEvent(event)

    def on_hide_cleanup(self):
        self._close_dialogs()
        # Clean up all visual effects
        self.cleanup_all_effects()
        
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
        """Show single player game over dialog with improved cleanup"""
        self._close_dialogs()
        
        # Clean up any existing effects first
        self.cleanup_all_effects()
        
        # Show confetti for victory
        if "Win" in result_text or "won" in result_text.lower():
            self.show_confetti_effect(duration=3000)  # Longer duration for victory
            
            # Short delay before showing dialog to let confetti display first
            QTimer.singleShot(800, lambda: self._show_game_over_dialog_after_effects(result_text, on_ok_callback))
        else:
            # Show dialog immediately for loss
            self._show_game_over_dialog_after_effects(result_text, on_ok_callback)
    
    def _show_game_over_dialog_after_effects(self, result_text, on_ok_callback):
        """Show game over dialog after effects have started"""
        # Create the overlay
        self.overlay.resize(self.size())
        self.overlay.show()
        self.overlay.raise_()
        
        # Create the dialog with main_window as parent for better positioning
        self.game_over_dialog = GameOverDialog(result_text, on_ok_callback, self.main_window)
        
        # Center on screen rather than on parent widget
        try:
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.geometry()
                x = (screen_geometry.width() - self.game_over_dialog.width()) // 2
                y = (screen_geometry.height() - self.game_over_dialog.height()) // 2
                self.game_over_dialog.move(x, y)
            else:
                # Fallback to center on main window
                self.game_over_dialog.move(self.main_window.rect().center() - self.game_over_dialog.rect().center())
        except:
            # Final fallback
            if self.main_window:
                self.game_over_dialog.move(self.main_window.rect().center() - self.game_over_dialog.rect().center())
        
        # Ensure dialog is on top
        self.game_over_dialog.raise_()
        self.game_over_dialog.activateWindow()
        
        # Show the dialog
        self.game_over_dialog.exec_()
        
        # Hide overlay after dialog is closed
        self.overlay.hide()
        
        # Clear the dialog reference
        self.game_over_dialog = None

    def _close_dialogs(self):
        """Safely close all dialogs and clean up references"""
        # Close match found dialog
        if self.match_found_dialog and self.match_found_dialog.isVisible():
            try:
                self.match_found_dialog.accept()
            except:
                pass
        self.match_found_dialog = None
        
        # Close game over dialog
        if self.game_over_dialog and self.game_over_dialog.isVisible():
            try:
                # Stop any animations first
                if hasattr(self.game_over_dialog, 'fade_in') and self.game_over_dialog.fade_in:
                    self.game_over_dialog.fade_in.stop()
                if hasattr(self.game_over_dialog, 'fade_out') and self.game_over_dialog.fade_out:
                    self.game_over_dialog.fade_out.stop()
                if hasattr(self.game_over_dialog, 'title_animation') and self.game_over_dialog.title_animation:
                    self.game_over_dialog.title_animation.stop()
                    
                self.game_over_dialog.accept()
            except:
                pass
        self.game_over_dialog = None
        
        # Hide overlay
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.hide()
            
    def close_all_dialogs(self):
        """Public method to close all dialogs, used by controller"""
        self._close_dialogs()
