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

class NotificationWidget(QFrame):
    def __init__(self, parent, message):
        super().__init__(parent)
        self.parent = parent
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(105, 105, 105, 0.95); /* Darker Gray */
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout()
        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setStyleSheet("color: white; background-color: transparent;")
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.setMinimumWidth(300)
        self.adjustSize()
        self.hide()

    def show_notification(self):
        parent_width = self.parent.width()
        self_width = self.width()
        start_x = int((parent_width - self_width) / 2)
        
        self.move(start_x, -self.height())
        self.show()

        self.anim_down = QPropertyAnimation(self, b"geometry")
        self.anim_down.setDuration(300)
        start_pos = QRect(start_x, -self.height(), self.width(), self.height())
        end_pos = QRect(start_x, 20, self.width(), self.height())
        self.anim_down.setStartValue(start_pos)
        self.anim_down.setEndValue(end_pos)
        self.anim_down.start()

        QTimer.singleShot(3000, self.hide_notification)

    def hide_notification(self):
        start_pos = self.geometry()
        end_pos = QRect(start_pos.x(), -self.height(), start_pos.width(), start_pos.height())
        
        self.anim_up = QPropertyAnimation(self, b"geometry")
        self.anim_up.setDuration(300)
        self.anim_up.setStartValue(start_pos)
        self.anim_up.setEndValue(end_pos)
        self.anim_up.finished.connect(self.deleteLater)
        self.anim_up.start()

class AfkDialog(QDialog):
    yes_clicked = pyqtSignal()
    timed_out = pyqtSignal()

    def __init__(self, countdown_seconds=10, parent=None):
        super().__init__(parent)
        self.seconds_left = countdown_seconds

        # Set window flags for a more visible dialog
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set fixed size for better visibility
        self.setFixedSize(400, 250)
        
        # Create a frame with a more visible background
        self.frame = QFrame(self)
        self.frame.setObjectName("dialog_frame")
        self.frame.setGeometry(0, 0, 400, 250)  # Make sure frame fills the entire dialog
        
        # Apply strong colors with higher opacity for visibility
        self.frame.setStyleSheet("""
            #dialog_frame {
                background-color: rgba(20, 20, 40, 0.98);  /* Nearly opaque dark background */
                border: 3px solid #3498db;  /* Thicker blue border */
                border-radius: 10px;
            }
        """)
        
        # Create the main layout for dialog contents
        layout = QVBoxLayout(self.frame)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Add a title label with larger, bold text
        title_label = QLabel("AFK WARNING", self.frame)
        title_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #3498db;  /* Match the border color */
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Add question label with high contrast
        question_label = QLabel("Are you still in the game?", self.frame)
        question_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
        """)
        question_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(question_label)
        
        # Add countdown label with high visibility
        self.countdown_label = QLabel(f"Closing in: {self.seconds_left}s", self.frame)
        self.countdown_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #f39c12;  /* Orange for countdown */
            background-color: transparent;
            padding: 5px;
        """)
        self.countdown_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.countdown_label)
        
        # Add a spacer for better layout
        layout.addStretch(1)
        
        # Create a visually prominent button
        self.yes_button = QPushButton("I'm Still Here", self.frame)
        self.yes_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 16px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.yes_button.setCursor(Qt.PointingHandCursor)
        self.yes_button.clicked.connect(self.handle_yes)
        layout.addWidget(self.yes_button)
        
        # Apply overall dialog styling
        self.setStyleSheet("""
            QDialog {
                background-color: transparent;
            }
        """)
        
        # Set up the timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)
        
        # For dragging the window
        self.old_pos = None
        
        # Center the dialog on the screen for maximum visibility
        self.center_on_screen()
    
    def center_on_screen(self):
        """Center the dialog on the screen for maximum visibility"""
        try:
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.geometry()
                x = (screen_geometry.width() - self.width()) // 2
                y = (screen_geometry.height() - self.height()) // 2
                self.move(x, y)
            else:
                # Fallback for systems without a primary screen
                screen_geometry = QApplication.desktop().screenGeometry()
                x = (screen_geometry.width() - self.width()) // 2
                y = (screen_geometry.height() - self.height()) // 2
                self.move(x, y)
        except AttributeError:
            # Fallback for older Qt versions
            screen_geometry = QApplication.desktop().screenGeometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPos()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = None
            event.accept()

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

    # Override show event to ensure the dialog comes to front
    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()
        self.activateWindow()

class LastChanceDialog(QDialog):
    yes_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Set window flags for a modern, frameless look
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Create main frame
        self.frame = QFrame(self)
        self.frame.setObjectName("dialog_frame")
        self.frame.setStyleSheet("""
            #dialog_frame {
                background-color: rgba(30, 30, 30, 0.95);
                border: 2px solid #f39c12;
                border-radius: 10px;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QLabel#title_label {
                color: #f39c12;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #f39c12;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #d35400;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        
        # Set up layouts
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.frame)
        
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(15)
        
        # Add title
        title_label = QLabel("Last Chance!")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(title_label)
        
        # Add message
        message_label = QLabel("Game is stalled. Start next round?")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        frame_layout.addWidget(message_label)
        
        # Add button
        self.ok_button = QPushButton("Yes, Start Round")
        self.ok_button.setCursor(Qt.PointingHandCursor)
        self.ok_button.clicked.connect(self._handle_yes)
        frame_layout.addWidget(self.ok_button)
        
        # Set fixed size
        self.setFixedSize(350, 200)
        
        # For dragging the window
        self.old_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPos()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = None
            event.accept()

    def _handle_yes(self):
        self.ok_button.setEnabled(False)
        self.ok_button.setText("Processing...")
        self.yes_clicked.emit()
        self.accept()

class GameCleanedUpDialog(QDialog):
    ok_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Set window flags for a modern, frameless look
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Create main frame
        self.frame = QFrame(self)
        self.frame.setObjectName("dialog_frame")
        self.frame.setStyleSheet("""
            #dialog_frame {
                background-color: rgba(30, 30, 30, 0.95);
                border: 2px solid #e74c3c;
                border-radius: 10px;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QLabel#title_label {
                color: #e74c3c;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        
        # Set up layouts
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.frame)
        
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(15)
        
        # Add title
        title_label = QLabel("Game Over")
        title_label.setObjectName("title_label")
        title_label.setAlignment(Qt.AlignCenter)
        frame_layout.addWidget(title_label)
        
        # Add message
        message_label = QLabel("The game session has ended or been cleaned up by the server.")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        frame_layout.addWidget(message_label)
        
        # Add button
        self.ok_button = QPushButton("OK")
        self.ok_button.setCursor(Qt.PointingHandCursor)
        self.ok_button.clicked.connect(self._handle_ok)
        frame_layout.addWidget(self.ok_button)
        
        # Set fixed size
        self.setFixedSize(400, 200)
        
        # For dragging the window
        self.old_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPos()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = None
            event.accept()

    def _handle_ok(self):
        self.ok_clicked.emit()
        self.accept()

class GameOverDialog(QDialog):
    """Enhanced game over dialog with animations and visual effects"""
    
    ok_clicked = pyqtSignal()
    
    def __init__(self, result_text, parent=None, word=None):
        super().__init__(parent)
        self.result = result_text
        self.word = word or ""
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Animation storage to prevent garbage collection
        self.animations = []
        self.label_visibility_timers = []
        self.button_clicked = False  # Flag to prevent multiple clicks
        
        # Set up main layout
        main_layout = QVBoxLayout(self)
        self.frame = QFrame()
        
        # Configure frame based on result
        if result_text == "WIN":
            self.setup_win_dialog()
        else:
            self.setup_lose_dialog()
        
        main_layout.addWidget(self.frame)
        self.setMinimumSize(500, 400)
        
        # Make dialog draggable
        self.old_pos = None
        
        # Initialize effects
        if result_text == "WIN":
            self.confetti_particles = []
            self.confetti_timer = QTimer(self)
            self.confetti_timer.timeout.connect(self.update_confetti)
            self.confetti_timer.start(50)
            
            # Start animations when shown
            QTimer.singleShot(100, self.start_win_animations)

    def accept_safely(self):
        """Safely accept the dialog, preventing multiple clicks"""
        if not self.button_clicked:
            self.button_clicked = True
            
            # Disable the button immediately to prevent additional clicks
            if hasattr(self, 'ok_button'):
                self.ok_button.setEnabled(False)
                self.ok_button.setText("Please wait...")
            
            # Clean up before accepting
            self.cleanup_resources()
            
            # Signal and accept
            self.ok_clicked.emit()
            self.accept()
            
    def cleanup_resources(self):
        """Clean up all animations and timers before closing"""
        try:
            # Stop confetti timer if active
            if hasattr(self, 'confetti_timer') and self.confetti_timer and self.confetti_timer.isActive():
                self.confetti_timer.stop()
                try:
                    self.confetti_timer.timeout.disconnect()
                except:
                    pass
                    
            # Stop all animations
            for anim in self.animations:
                if anim.state() == QPropertyAnimation.Running:
                    anim.stop()
            
            # Stop any pending label visibility timers
            for timer in self.label_visibility_timers:
                timer.stop()
            self.label_visibility_timers = []
                    
            # Clear all particle data
            if hasattr(self, 'confetti_particles'):
                self.confetti_particles = []
        except Exception as e:
            print(f"Error cleaning up dialog resources: {e}")
            
    def reject(self):
        """Override reject to ensure cleanup"""
        self.cleanup_resources()
        super().reject()

    def setup_win_dialog(self):
        """Set up the victory dialog with gold border and animations"""
        layout = QVBoxLayout(self.frame)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Style the frame
        self.frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 0.85);
                border: 2px solid gold;
                border-radius: 15px;
            }
        """)
        
        # Victory label
        self.victory_label = QLabel("VICTORY!")
        self.victory_label.setStyleSheet("""
            font-size: 48px;
            font-weight: bold;
            color: gold;
        """)
        self.victory_label.setAlignment(Qt.AlignCenter)
        
        # Word label
        self.word_label = QLabel(f"The word was: {self.word}")
        self.word_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #55FF55;
        """)
        self.word_label.setAlignment(Qt.AlignCenter)
        
        # Message label
        self.message_label = QLabel("Congratulations!")
        self.message_label.setStyleSheet("""
            font-size: 18px;
            color: white;
        """)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setWordWrap(True)
        
        # Continue button
        self.ok_button = QPushButton("Continue")
        self.ok_button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                background-color: #55AA55;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #6EC06E;
            }
            QPushButton:pressed {
                background-color: #458945;
            }
            QPushButton:disabled {
                background-color: #777777;
            }
        """)
        # Connect to safer accept method
        self.ok_button.clicked.connect(self.accept_safely)
        
        # Add widgets to layout
        layout.addWidget(self.victory_label)
        layout.addWidget(self.word_label)
        layout.addWidget(self.message_label)
        layout.addStretch()
        layout.addWidget(self.ok_button)

    def setup_lose_dialog(self):
        """Set up the loss dialog with dark theme and background image"""
        layout = QVBoxLayout(self.frame)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Use end.png as background in a label
        background_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                      'views', 'assets', 'end.png')
        
        # Set background image through stylesheet with semi-transparent overlay
        self.frame.setStyleSheet(f"""
            QFrame {{
                border: 2px solid #660000;
                border-radius: 15px;
                background-image: url({background_path.replace('\\', '/')});
                background-position: center;
                background-repeat: no-repeat;
                background-color: rgba(30, 30, 30, 0.9);
            }}
        """)
        
        # Game over label
        self.title_label = QLabel("GAME OVER")
        self.title_label.setStyleSheet("""
            font-size: 48px;
            font-weight: bold;
            color: #FF3333;
            text-shadow: 2px 2px 4px #000000;
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        
        # Word label if we have it
        if self.word:
            self.word_label = QLabel(f"The word was: {self.word}")
            self.word_label.setStyleSheet("""
                font-size: 24px;
                color: #AAAAAA;
                text-shadow: 1px 1px 2px #000000;
            """)
            self.word_label.setAlignment(Qt.AlignCenter)
        else:
            self.word_label = QLabel("")
        
        # Message
        self.message_label = QLabel("You Lost")
        self.message_label.setStyleSheet("""
            font-size: 24px;
            color: white;
            text-shadow: 1px 1px 2px #000000;
        """)
        self.message_label.setAlignment(Qt.AlignCenter)
        
        # OK button
        self.ok_button = QPushButton("Try Again")
        self.ok_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                background-color: #AA5555;
                color: white;
                padding: 8px 16px;
                border-radius: 5px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #CC6666;
            }
            QPushButton:pressed {
                background-color: #884444;
            }
            QPushButton:disabled {
                background-color: #777777;
            }
        """)
        # Connect to safer accept method
        self.ok_button.clicked.connect(self.accept_safely)
        
        # Add widgets to layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.word_label)
        layout.addWidget(self.message_label)
        layout.addStretch()
        layout.addWidget(self.ok_button)
    
    def mousePressEvent(self, event):
        """Enable dragging the dialog by clicking anywhere on it"""
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
    
    def start_win_animations(self):
        """Start victory animations"""
        try:
            # Simple bounce animation for victory label
            self.bounce_animation = QPropertyAnimation(self.victory_label, b"pos")
            self.bounce_animation.setDuration(500)
            pos = self.victory_label.pos()
            
            # Move up then down with bounce
            self.bounce_animation.setKeyValueAt(0.0, QPoint(pos.x(), pos.y()))
            self.bounce_animation.setKeyValueAt(0.3, QPoint(pos.x(), pos.y() - 20))
            self.bounce_animation.setKeyValueAt(0.6, QPoint(pos.x(), pos.y() + 10))
            self.bounce_animation.setKeyValueAt(0.8, QPoint(pos.x(), pos.y() - 5))
            self.bounce_animation.setKeyValueAt(1.0, QPoint(pos.x(), pos.y()))
            
            self.bounce_animation.setEasingCurve(QEasingCurve.OutBounce)
            self.animations.append(self.bounce_animation)
            self.bounce_animation.start()
            
            # No fade effects to avoid crashes
            self.word_label.setVisible(False)
            self.message_label.setVisible(False)
            
            # Show text with a delay instead, using timers we can clean up
            timer1 = QTimer(self)
            timer1.setSingleShot(True)
            timer1.timeout.connect(lambda: self.word_label.setVisible(True))
            timer1.start(600)
            self.label_visibility_timers.append(timer1)

            timer2 = QTimer(self)
            timer2.setSingleShot(True)
            timer2.timeout.connect(lambda: self.message_label.setVisible(True))
            timer2.start(900)
            self.label_visibility_timers.append(timer2)
            
        except Exception as e:
            print(f"Animation error: {e}")
    
    def update_confetti(self):
        """Update confetti particles for the win animation"""
        try:
            if self.result != "WIN":
                return
                
            if len(self.confetti_particles) < 50:  # Reduced particle count
                # Add new particles
                for _ in range(3):  # Reduced number of new particles
                    particle = {
                        'x': random.randint(0, self.width()),
                        'y': -20,
                        'size': random.randint(5, 15),
                        'speed': random.randint(2, 8),
                        'swing': random.choice([-1, 1]) * random.random() * 2,
                        'color': QColor(
                            random.randint(0, 255),
                            random.randint(0, 255),
                            random.randint(0, 255)
                        ),
                        'rotation': random.randint(0, 360)
                    }
                    self.confetti_particles.append(particle)
            
            # Update existing particles
            for particle in self.confetti_particles[:]:
                particle['y'] += particle['speed']
                particle['x'] += particle['swing']
                particle['rotation'] += 5
                
                # Remove particles that have fallen off the screen
                if particle['y'] > self.height():
                    self.confetti_particles.remove(particle)
            
            # Redraw
            self.update()
        except Exception as e:
            print(f"Confetti error: {e}")
            self.confetti_timer.stop()
    
    def closeEvent(self, event):
        """Clean up resources when dialog is closed"""
        self.cleanup_resources()
        super().closeEvent(event)
    
    def paintEvent(self, event):
        """Custom paint event to draw confetti"""
        super().paintEvent(event)
        
        try:
            if hasattr(self, 'confetti_particles') and self.result == "WIN":
                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                
                for particle in self.confetti_particles:
                    painter.save()
                    painter.translate(particle['x'], particle['y'])
                    painter.rotate(particle['rotation'])
                    
                    painter.setBrush(QBrush(particle['color']))
                    painter.setPen(Qt.NoPen)
                    
                    # Draw confetti piece (rectangle with slight 3D effect)
                    # Convert floats to ints to fix the error
                    size = int(particle['size'])
                    half_size = int(size / 2)
                    third_size = int(size / 3)
                    painter.drawRect(-half_size, -half_size, size, third_size)
                    
                    painter.restore()
        except Exception as e:
            # Print errors to help debug painting issues
            print(f"Error during GameOverDialog paint event: {e}")
            pass

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

class HealthBar(QProgressBar):
    """A simple health bar to show remaining guesses."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0, 100)
        self.setValue(100)
        self.setTextVisible(False)
        self.setFixedHeight(15)
        self.setFixedWidth(120)
        self.set_stylesheet(100)

    def set_stylesheet(self, percentage):
        if percentage <= 25:
            color = "#e74c3c"  # Red
        elif percentage <= 50:
            color = "#f1c40f"  # Yellow
        else:
            color = "#2ecc71"  # Green

        self.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #AAAAAA;
                border-radius: 5px;
                background-color: #E0E0E0;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 4px;
                margin: 1px;
            }}
        """)

    def update_health(self, incorrect_guesses, max_guesses=6):
        if max_guesses <= 0:
            health_percent = 100
        else:
            health_percent = int(((max_guesses - incorrect_guesses) / max_guesses) * 100)
        
        self.setValue(health_percent)
        self.set_stylesheet(health_percent)

class CircularTimer(QWidget):
    """A circular progress bar timer widget that visually shows remaining time"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.percentage = 100
        self.animation_duration = 800  # milliseconds
        self.color = QColor('#FFFFFF')  # White default color (changed from gold)
        self.setMinimumSize(80, 80)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.text = ""
        self.animation = None
        self.old_percentage = 100

    def setValue(self, value):
        """Set the percentage value (0-100) and animate the change"""
        if value == self.percentage:
            return
        
        self.old_percentage = self.percentage
        self.percentage = value
        
        # Create animation for smooth transitions
        if hasattr(self, 'animation') and self.animation is not None:
            self.animation.stop()
        
        self.animation = QPropertyAnimation(self, b"animValue")
        self.animation.setDuration(self.animation_duration)
        self.animation.setStartValue(self.old_percentage)
        self.animation.setEndValue(self.percentage)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.valueChanged.connect(self.updateAnimValue)
        self.animation.start()

    def updateAnimValue(self, value):
        """Update the animation value and trigger repaint"""
        self.percentage = value
        self.update()

    def setColor(self, color_str):
        """Set the color of the progress bar"""
        self.color = QColor(color_str)
        self.update()

    def setText(self, text):
        """Set the text displayed in the center of the timer"""
        self.text = text
        self.update()

    def paintEvent(self, event):
        """Paint the circular timer"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate sizes
        width = self.width()
        height = self.height()
        size = min(width, height)
        padding = 5
        
        # Draw background circle
        painter.setPen(QPen(QColor('#555555'), 8))  # Darker background for better contrast
        painter.drawArc(padding, padding, size-2*padding, size-2*padding, 0, 360*16)
        
        # Calculate and draw progress arc
        progress_angle = int(-self.percentage * 360 / 100 * 16)  # Convert to 16th of a degree
        
        # Change color based on remaining time
        if self.percentage <= 15:  # 0-15% (less than 5 seconds) - Red
            color = QColor('#E53935')  # Red for urgent
        elif self.percentage <= 25:  # 15-25% (5-15 seconds) - Yellow
            color = QColor('#FFEB3B')  # Yellow for warning
        else:
            color = self.color  # White default color
            
        painter.setPen(QPen(color, 8))
        painter.drawArc(padding, padding, size-2*padding, size-2*padding, 90*16, progress_angle)
        
        # Draw text
        painter.setPen(QColor('#FFFFFF'))  # Changed to white text
        font = painter.font()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRectF(0, 0, width, height), Qt.AlignCenter, self.text)

class LetterBox(QLabel):
    def __init__(self, letter=" ", parent=None):
        super().__init__(parent)
        self.setText(letter)
        self.setAlignment(Qt.AlignCenter)
        self.setObjectName("letter_cell")
        self.setMinimumSize(40, 40)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setStyleSheet("""
            background-color: #f0f0f0;
            border: 2px solid #bdc3c7;
            border-radius: 5px;
            padding: 5px;
            margin: 2px;
            min-width: 40px;
            min-height: 40px;
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        """)
        
    def animate_reveal(self):
        """Animate letter reveal with a bounce effect"""
        # Store the original size
        original_size = self.size()
        
        # Create sequential animations
        animation_group = QSequentialAnimationGroup(self)
        
        # 1. Scale up animation
        scale_up = QPropertyAnimation(self, b"geometry")
        scale_up.setDuration(150)
        scale_up.setStartValue(QRect(self.x(), self.y(), original_size.width(), original_size.height()))
        scale_up.setEndValue(QRect(
            self.x() - 5, 
            self.y() - 5, 
            original_size.width() + 10, 
            original_size.height() + 10
        ))
        scale_up.setEasingCurve(QEasingCurve.OutQuad)
        
        # 2. Scale down animation (bounce back)
        scale_down = QPropertyAnimation(self, b"geometry")
        scale_down.setDuration(150)
        scale_down.setStartValue(QRect(
            self.x() - 5, 
            self.y() - 5, 
            original_size.width() + 10, 
            original_size.height() + 10
        ))
        scale_down.setEndValue(QRect(self.x(), self.y(), original_size.width(), original_size.height()))
        scale_down.setEasingCurve(QEasingCurve.OutBounce)
        
        # Add animations to group and start
        animation_group.addAnimation(scale_up)
        animation_group.addAnimation(scale_down)
        animation_group.start()

class MaskedWordContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        self.letter_boxes = []
        self.current_word = ""
        self.previous_word = ""  # Track previous word to detect new reveals

    def update_word(self, masked_word):
        # Only update if the word has actually changed to avoid flickering
        if masked_word == self.current_word:
            return
            
        self.previous_word = self.current_word  # Store previous word
        self.current_word = masked_word
        
        # Clear existing boxes
        for box in self.letter_boxes:
            self.layout.removeWidget(box)
            box.deleteLater()
        self.letter_boxes.clear()

        # Create new letter boxes
        for char in masked_word:
            if char.isalpha() or char == '_':
                letter_box = LetterBox(char)
                self.layout.addWidget(letter_box)
                self.letter_boxes.append(letter_box)
            # Skip spaces or other formatting characters
            
        # Apply special styling to reveal boxes
        self.highlight_revealed_letters()
        
        # Animate newly revealed letters
        self.animate_new_reveals()
    
    def highlight_revealed_letters(self):
        """Apply special styling to revealed letters"""
        for box in self.letter_boxes:
            if box.text().isalpha():
                box.setStyleSheet("""
                    background-color: #2ecc71;
                    color: white;
                    border: 2px solid #27ae60;
                    border-radius: 5px;
                    padding: 5px;
                    margin: 2px;
                    min-width: 40px;
                    min-height: 40px;
                    font-size: 24px;
                    font-weight: bold;
                """)
            else:
                # Underscore style
                box.setStyleSheet("""
                    background-color: #f0f0f0;
                    border: 2px solid #bdc3c7;
                    border-radius: 5px;
                    padding: 5px;
                    margin: 2px;
                    min-width: 40px;
                    min-height: 40px;
                    font-size: 24px;
                    font-weight: bold;
                    color: #2c3e50;
                """)
                
    def animate_new_reveals(self):
        """Animate newly revealed letters by comparing with previous word"""
        if not self.previous_word or len(self.previous_word) != len(self.current_word):
            return  # Skip animation if this is the first word or length changed
            
        for i, (box, prev_char, curr_char) in enumerate(zip(
            self.letter_boxes, self.previous_word, self.current_word
        )):
            # If this letter was just revealed (was _ and now is a letter)
            if prev_char == '_' and curr_char.isalpha():
                # Delay slightly to create a cascade effect if multiple letters revealed
                QTimer.singleShot(i * 50, box.animate_reveal)

class PlayerStatusWidget(QFrame):
    def __init__(self, username):
        super().__init__()
        
        # Create a modern looking frame with custom styling
        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("player_status_widget")
        
        # Base layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Header with background color and player name
        self.header_frame = QFrame()
        self.header_frame.setObjectName("player_header")
        self.header_frame.setMinimumHeight(30)
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(8, 4, 8, 4)
        
        self.username_label = QLabel(username)
        self.username_label.setObjectName("username_label")
        self.username_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(12, 12)
        self.status_indicator.setObjectName("status_indicator")
        
        header_layout.addWidget(self.status_indicator)
        header_layout.addWidget(self.username_label)
        header_layout.addStretch()
        
        # Create score label with nice styling
        self.score_label = QLabel("Score: 0")
        self.score_label.setObjectName("score_label")
        self.score_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        header_layout.addWidget(self.score_label)
        
        # Content area for masked word
        self.content_frame = QFrame()
        self.content_frame.setObjectName("player_content")
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(8)
        
        # Word display - make it bigger and more prominent with word wrap enabled
        self.masked_word_label = QLabel("_ _ _")
        self.masked_word_label.setObjectName("masked_word_label")
        self.masked_word_label.setAlignment(Qt.AlignCenter)
        self.masked_word_label.setWordWrap(True) # Enable word wrap
        self.masked_word_label.setMinimumHeight(40) # Ensure enough height for multiple lines
        content_layout.addWidget(self.masked_word_label)
        
        # Health bar to show incorrect guesses
        self.health_bar = QProgressBar()
        self.health_bar.setRange(0, 100)
        self.health_bar.setValue(100)
        self.health_bar.setTextVisible(False)
        self.health_bar.setFixedHeight(8)
        self.health_bar.setObjectName("player_health")
        content_layout.addWidget(self.health_bar)
        
        # Progress bar to show completion
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setObjectName("player_progress")
        content_layout.addWidget(self.progress_bar)
        
        # Add all components to main layout
        layout.addWidget(self.header_frame)
        layout.addWidget(self.content_frame)
        
        # Set fixed width to prevent horizontal scrolling - make it wider
        self.setMinimumWidth(260)
        self.setMaximumWidth(260)
        self.setMinimumHeight(130)
        
        # Apply stylesheets
        self.apply_stylesheets()
        
        # Glow animation for win streaks
        self.glow_effect = QGraphicsOpacityEffect(self)
        self.glow_effect.setOpacity(0.8)  # Start with reasonable opacity
        self.setGraphicsEffect(self.glow_effect)
        
        self.glow_animation = QPropertyAnimation(self.glow_effect, b"opacity")
        self.glow_animation.setDuration(1500)  # 1.5 seconds per cycle
        self.glow_animation.setLoopCount(-1)  # Loop indefinitely
        self.glow_animation.setStartValue(0.8)
        self.glow_animation.setEndValue(1.0)
        self.glow_animation.setEasingCurve(QEasingCurve.InOutSine)
        
        # Store win streak information
        self.win_streak = 0

    def apply_stylesheets(self):
        """Apply styling to make the widget look nice"""
        self.setStyleSheet("""
            #player_status_widget {
                background-color: rgba(30, 30, 30, 0.7);
                border-radius: 10px;
                border: 1px solid rgba(120, 120, 120, 0.5);
            }
            
            #player_header {
                background-color: rgba(40, 40, 40, 0.9);
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom: 1px solid rgba(100, 100, 100, 0.5);
            }
            
            #username_label {
                color: white;
                font-weight: bold;
                font-size: 12px;
            }
            
            #score_label {
                color: #2ecc71;
                font-weight: bold;
                font-size: 11px;
            }
            
            #status_indicator {
                background-color: #f39c12;
                border-radius: 6px;
            }
            
            #player_content {
                background-color: transparent;
            }
            
            #masked_word_label {
                color: white;
                font-family: 'Courier New';
                font-size: 18px;
                font-weight: bold;
                letter-spacing: 4px;
                margin: 5px 0;
            }
            
            #player_progress {
                background-color: rgba(50, 50, 50, 0.5);
                border-radius: 2px;
                border: none;
            }
            
            #player_progress::chunk {
                background-color: #3498db;
                border-radius: 2px;
            }
            
            #player_health {
                background-color: rgba(50, 50, 50, 0.5);
                border-radius: 2px;
                border: none;
            }
            
            #player_health::chunk {
                background-color: #e74c3c;
                border-radius: 2px;
            }
        """)

    def update_widget(self, score, masked_word, is_finished):
        # Update score
        self.score_label.setText(f"Score: {score}")
        
        # Update masked word with better spacing
        # Use fewer spaces between characters to fit more in the width
        self.masked_word_label.setText(masked_word.replace("", " ").strip())
        
        # Calculate progress based on revealed letters
        revealed_count = sum(1 for char in masked_word if char.isalpha())
        total_letters = masked_word.count("_") + revealed_count
        
        if total_letters > 0:
            progress = int((revealed_count / total_letters) * 100)
        else:
            progress = 0
        
        self.progress_bar.setValue(progress)
        
        # Update status indicator
        if is_finished:
            self.status_indicator.setStyleSheet("background-color: #2ecc71;")  # Green for finished
            self.header_frame.setStyleSheet("background-color: rgba(46, 204, 113, 0.3);")
        else:
            self.status_indicator.setStyleSheet("background-color: #f39c12;")  # Orange for playing
            self.header_frame.setStyleSheet("background-color: rgba(40, 40, 40, 0.9);")

    def update_health(self, incorrect_guesses, max_guesses=6):
        """Update health bar to show remaining attempts"""
        if max_guesses <= 0:
            health_percent = 100
        else:
            health_percent = int(((max_guesses - incorrect_guesses) / max_guesses) * 100)
        
        self.health_bar.setValue(health_percent)
        
        # Change color based on health
        if health_percent <= 25:
            self.health_bar.setStyleSheet("""
                #player_health {
                    background-color: rgba(50, 50, 50, 0.5);
                    border-radius: 2px;
                    border: none;
                }
                #player_health::chunk {
                    background-color: #e74c3c;  /* Red */
                    border-radius: 2px;
                }
            """)
        elif health_percent <= 50:
            self.health_bar.setStyleSheet("""
                #player_health {
                    background-color: rgba(50, 50, 50, 0.5);
                    border-radius: 2px;
                    border: none;
                }
                #player_health::chunk {
                    background-color: #f39c12;  /* Orange */
                    border-radius: 2px;
                }
            """)
        else:
            self.health_bar.setStyleSheet("""
                #player_health {
                    background-color: rgba(50, 50, 50, 0.5);
                    border-radius: 2px;
                    border: none;
                }
                #player_health::chunk {
                    background-color: #2ecc71;  /* Green */
                    border-radius: 2px;
                }
            """)
            
    def update_win_streak(self, streak):
        """Update the win streak and apply golden glow if streak >= 2"""
        self.win_streak = streak
        
        if streak >= 2:
            # Apply golden border and glow effect
            self.setStyleSheet(f"""
                #player_status_widget {{
                    background-color: rgba(30, 30, 30, 0.7);
                    border-radius: 10px;
                    border: 2px solid gold;
                    box-shadow: 0 0 10px gold;
                }}
                
                #player_header {{
                    background-color: rgba(70, 60, 0, 0.7);
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    border-bottom: 1px solid gold;
                }}
                
                #username_label {{
                    color: gold;
                    font-weight: bold;
                }}
                
                #score_label {{
                    color: gold;
                    font-weight: bold;
                }}
                
                #masked_word_label {{
                    color: white;
                    font-family: 'Courier New';
                    font-size: 18px;
                    font-weight: bold;
                    letter-spacing: 4px;
                }}
            """)
            
            # Start glow animation if not running
            if self.glow_animation.state() != QPropertyAnimation.Running:
                self.glow_animation.start()
        else:
            # Stop animation and reset default style
            if self.glow_animation.state() == QPropertyAnimation.Running:
                self.glow_animation.stop()
            self.glow_effect.setOpacity(1.0)  # Reset opacity
            self.apply_stylesheets()  # Reset to normal style

    # ------------------------------------------------------------------
    # Cleanup helpers
    # ------------------------------------------------------------------

    def stop_animations(self):
        """Stop any running animations/effects to avoid crashes after the
        underlying C++ object is deleted."""
        try:
            if hasattr(self, 'glow_animation') and self.glow_animation:
                self.glow_animation.stop()
            if hasattr(self, 'glow_effect') and self.glow_effect:
                # Reset opacity to avoid painting on a deleted effect
                self.glow_effect.setOpacity(0.0)
        except Exception:
            pass

    def cleanup(self):
        """Public method called before the widget is deleted."""
        self.stop_animations()

    def closeEvent(self, event):
        # When the widget closes (e.g., via deleteLater), stop animations.
        self.stop_animations()
        super().closeEvent(event)

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

        # Add padding to the main layout to create space at the bottom
        self.layout().setContentsMargins(10, 10, 10, 25)
        
        # Add more spacing between the keyboard rows
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if isinstance(item, QHBoxLayout):
                item.setContentsMargins(5, 5, 5, 10)
                item.setSpacing(6)

        for letter in all_letters:
            button = self.findChild(QPushButton, f'button_{letter}')
            if button:
                button.clicked.connect(lambda checked, l=letter: self.on_button_clicked(l))
                self.buttons[letter] = button
                
    def on_button_clicked(self, letter):
        """Handle button click with animation and emit signal"""
        button = self.buttons.get(letter)
        if button:
            self.animate_button_press(button)
            self.letterClicked.emit(letter)
            
    def animate_button_press(self, button):
        """Animate button press with a quick scale effect"""
        # Store the original style sheet
        original_stylesheet = button.styleSheet()
        
        # Create sequential animations
        animation = QSequentialAnimationGroup(button)
        
        # Scale down effect
        scale_down = QPropertyAnimation(button, b"geometry")
        scale_down.setDuration(50)
        original_rect = button.geometry()
        compressed_rect = QRect(
            original_rect.x() + 2,
            original_rect.y() + 2,
            original_rect.width() - 4,
            original_rect.height() - 4
        )
        scale_down.setStartValue(original_rect)
        scale_down.setEndValue(compressed_rect)
        
        # Scale up effect
        scale_up = QPropertyAnimation(button, b"geometry")
        scale_up.setDuration(100)
        scale_up.setStartValue(compressed_rect)
        scale_up.setEndValue(original_rect)
        scale_up.setEasingCurve(QEasingCurve.OutBounce)
        
        # Add animations to group
        animation.addAnimation(scale_down)
        animation.addAnimation(scale_up)
        animation.start()

    def set_button_pending(self, letter):
        """Set a button to pending state while waiting for server response"""
        button = self.buttons.get(letter)
        if button:
            button.setDisabled(True)
            button.setStyleSheet("background-color: #f0e68c; color: #333;") # Khaki with darker text
            button.setProperty("pending", True)
            
            # Force style update
            button.style().unpolish(button)
            button.style().polish(button)

    def update_button_color(self, letter, is_correct):
        """Update button color based on correct/incorrect guess"""
        button = self.buttons.get(letter)
        if button:
            button.setProperty("pending", False)
            if is_correct:
                button.setProperty("correct", True)
                button.setStyleSheet("background-color: #2E8B57; color: white;")
                # Add a little animation for correct guesses
                self.animate_button_success(button)
            else:
                button.setProperty("incorrect", True)
                button.setStyleSheet("background-color: #C70039; color: white;")
                # Add a shake animation for incorrect guesses
                self.animate_button_failure(button)
            
            # Force style update
            button.style().unpolish(button)
            button.style().polish(button)
            
            # No need to return position anymore
            return None
        return None
        
    def animate_button_success(self, button):
        """Animate successful button press with a glow effect"""
        # Flash animation using opacity
        glow_animation = QPropertyAnimation(button, b"windowOpacity")
        glow_animation.setDuration(400)
        glow_animation.setStartValue(0.7)
        glow_animation.setEndValue(1.0)
        glow_animation.setEasingCurve(QEasingCurve.OutQuad)
        glow_animation.start()
        
    def animate_button_failure(self, button):
        """Animate incorrect button press with a shake effect"""
        # Shake animation
        shake_animation = QSequentialAnimationGroup(button)
        
        for i in range(2):
            # Move right
            move_right = QPropertyAnimation(button, b"pos")
            move_right.setDuration(50)
            move_right.setStartValue(button.pos())
            move_right.setEndValue(QPoint(button.x() + 5, button.y()))
            
            # Move left
            move_left = QPropertyAnimation(button, b"pos")
            move_left.setDuration(50)
            move_left.setStartValue(QPoint(button.x() + 5, button.y()))
            move_left.setEndValue(button.pos())
            
            shake_animation.addAnimation(move_right)
            shake_animation.addAnimation(move_left)
        
        shake_animation.start()

    def update_keyboard(self, all_guessed_letters, correctly_guessed_letters, enabled=True):
        """Update all keyboard buttons based on game state"""
        for letter, button in self.buttons.items():
            # Check for letters already guessed
            if letter in all_guessed_letters:
                button.setDisabled(True)
                button.setProperty("pending", False)
                
                if letter in correctly_guessed_letters:
                    button.setProperty("correct", True)
                    button.setProperty("incorrect", False)
                    button.setStyleSheet("background-color: #2E8B57; color: white;") # More vivid green
                else:
                    button.setProperty("correct", False)
                    button.setProperty("incorrect", True)
                    button.setStyleSheet("background-color: #C70039; color: white;") # More vivid red
            else:
                # Letters not guessed yet
                button.setEnabled(enabled)
                button.setProperty("correct", False)
                button.setProperty("incorrect", False)
                button.setProperty("pending", False)
                button.setStyleSheet("") # Reset non-guessed buttons

            # Force style update
            button.style().unpolish(button)
            button.style().polish(button)

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
        kb_container_layout.setContentsMargins(10, 10, 10, 20)  # Add extra bottom margin
        kb_container_layout.addWidget(self.virtual_keyboard)
        
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
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        style_path = os.path.join(base_path, 'style', 'multiplayergame.qss')
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                # Read the base stylesheet
                base_style = f.read()
                
                # Add additional styles for player widgets
                additional_styles = """
                /* Opponent panel styling */
                #right_panel {
                    background-color: rgba(0, 0, 0, 0.5);
                    border-radius: 15px;
                    border: none;
                }
                
                #other_players_label {
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                
                QScrollArea {
                    background: transparent;
                    border: none;
                }
                
                QScrollArea > QWidget > QWidget {
                    background: transparent;
                }
                """
                
                # Combine styles and apply
                self.setStyleSheet(base_style + additional_styles)
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
        player_is_done_this_round = (current_player_username in finish_times and finish_times[current_player_username] > 0) or my_incorrects >= 6

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
            player_is_finished = (player_name in finish_times and finish_times[player_name] > 0) or player_incorrects >= 6
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

class MultiplayerGameOverDialog(QDialog):
    """A simple, dedicated game over dialog for multiplayer mode only."""
    
    ok_clicked = pyqtSignal()
    
    def __init__(self, result_text, parent=None):
        super().__init__(parent)
        self.result = result_text
        self.loading_timer = QTimer(self)
        self.loading_dots = 0
        
        # Use frameless window with translucent background
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Create layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create content frame
        self.frame = QFrame()
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(30, 30, 30, 30)
        frame_layout.setSpacing(15) # Reduced spacing
        
        # Style the frame based on result
        if result_text == "WIN":
            self.frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(0, 0, 0, 0.85);
                    border: 2px solid #2ecc71;
                    border-radius: 15px;
                }
            """)
            title_color = "#2ecc71"  # Green for win
            button_color = "#27ae60"
            button_hover = "#2ecc71"
        else:
            self.frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(0, 0, 0, 0.85);
                    border: 2px solid #e74c3c;
                    border-radius: 15px;
                }
            """)
            title_color = "#e74c3c"  # Red for loss
            button_color = "#c0392b"
            button_hover = "#e74c3c"
        
        # Create labels
        self.title_label = QLabel("VICTORY!" if result_text == "WIN" else "DEFEAT")
        self.title_label.setStyleSheet(f"""
            font-size: 36px;
            font-weight: bold;
            color: {title_color};
        """)
        self.title_label.setAlignment(Qt.AlignCenter)
        
        self.message_label = QLabel("Congratulations!" if result_text == "WIN" else "Better luck next time!")
        self.message_label.setStyleSheet("""
            font-size: 18px;
            color: white;
        """)
        self.message_label.setAlignment(Qt.AlignCenter)

        # Create loading label (initially hidden)
        self.loading_label = QLabel("Processing result...")
        self.loading_label.setStyleSheet("font-size: 14px; color: #bdc3c7;")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.hide()
        
        # Create button
        self.ok_button = QPushButton("Continue to Results")
        self.ok_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {button_color};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {button_hover};
            }}
            QPushButton:pressed {{
                background-color: {button_color};
            }}
            QPushButton:disabled {{
                background-color: #7f8c8d;
            }}
        """)
        self.ok_button.setCursor(Qt.PointingHandCursor)
        self.ok_button.clicked.connect(self.accept_dialog)
        
        # Add widgets to layout
        frame_layout.addWidget(self.title_label)
        frame_layout.addWidget(self.message_label)
        frame_layout.addStretch()
        frame_layout.addWidget(self.loading_label)
        frame_layout.addWidget(self.ok_button)
        
        # Add frame to main layout
        main_layout.addWidget(self.frame)
        
        # Set size
        self.setMinimumWidth(400)
        self.setMinimumHeight(280) # Increased height for loading label
        
        # For dragging
        self.old_pos = None
        
        # Center on parent
        if parent:
            self.move(parent.rect().center() - self.rect().center())

    def _update_loading_text(self):
        """Cycle through dots for a simple animation"""
        self.loading_dots = (self.loading_dots + 1) % 4
        dots = "." * self.loading_dots
        self.loading_label.setText(f"Processing result{dots}")
            
    def accept_dialog(self):
        """Handle dialog acceptance with button disable to prevent double-clicks"""
        # Disable button and show loading animation
        self.ok_button.setEnabled(False)
        self.ok_button.hide()
        self.loading_label.show()

        # Start the timer for the loading dots animation
        self.loading_timer.timeout.connect(self._update_loading_text)
        self.loading_timer.start(500) # Update every 500ms
        
        # Emit the signal so the controller can start processing
        self.ok_clicked.emit()
        
        # Do NOT call self.accept() here. The controller will close the view.

    def closeEvent(self, event):
        """Ensure timer is stopped when dialog is closed"""
        self.loading_timer.stop()
        super().closeEvent(event)
        
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