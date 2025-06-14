from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QLabel, QPushButton, 
                             QApplication, QDialog)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QRect
from PyQt5.QtGui import QFont
from .base_dialog import BaseDialog
import os

class NotificationWidget(QFrame):
    def __init__(self, parent, message):
        super().__init__(parent)
        self.parent = parent
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(105, 105, 105, 0.95);
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

class AfkDialog(BaseDialog):
    yes_clicked = pyqtSignal()
    timed_out = pyqtSignal()

    def __init__(self, countdown_seconds=10, parent=None):
        super().__init__(parent)
        self.seconds_left = countdown_seconds
        self.setFixedSize(400, 250)
        
        # Create main frame
        self.frame = QFrame(self)
        self.frame.setObjectName("dialog_frame")
        self.frame.setGeometry(0, 0, 400, 250)
        
        # Apply styling
        self.frame.setStyleSheet("""
            #dialog_frame {
                background-color: rgba(20, 20, 40, 0.98);
                border: 3px solid #3498db;
                border-radius: 10px;
            }
        """)
        
        # Create layout
        layout = QVBoxLayout(self.frame)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Add title
        title_label = QLabel("AFK WARNING", self.frame)
        title_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #3498db;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Add question
        question_label = QLabel("Are you still in the game?", self.frame)
        question_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
        """)
        question_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(question_label)
        
        # Add countdown
        self.countdown_label = QLabel(f"Closing in: {self.seconds_left}s", self.frame)
        self.countdown_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #f39c12;
            background-color: transparent;
            padding: 5px;
        """)
        self.countdown_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.countdown_label)
        
        layout.addStretch(1)
        
        # Add button
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
        
        # Set up timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)
        
        # Center dialog
        self.center_on_screen()

    def center_on_screen(self):
        try:
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.geometry()
                x = (screen_geometry.width() - self.width()) // 2
                y = (screen_geometry.height() - self.height()) // 2
                self.move(x, y)
            else:
                screen_geometry = QApplication.desktop().screenGeometry()
                x = (screen_geometry.width() - self.width()) // 2
                y = (screen_geometry.height() - self.height()) // 2
                self.move(x, y)
        except AttributeError:
            pass

    def update_countdown(self):
        self.seconds_left -= 1
        self.countdown_label.setText(f"Closing in: {self.seconds_left}s")
        
        if self.seconds_left <= 0:
            self.timer.stop()
            self.timed_out.emit()
            self.close()

    def handle_yes(self):
        self.timer.stop()
        self.yes_clicked.emit()
        self.close()

    def closeEvent(self, event):
        self.timer.stop()
        super().closeEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        self.timer.start()

class LastChanceDialog(BaseDialog):
    yes_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 250)
        
        # Create main frame
        self.frame = QFrame(self)
        self.frame.setObjectName("dialog_frame")
        self.frame.setGeometry(0, 0, 400, 250)
        
        # Apply styling
        self.frame.setStyleSheet("""
            #dialog_frame {
                background-color: rgba(20, 20, 40, 0.98);
                border: 3px solid #f39c12;
                border-radius: 10px;
            }
        """)
        
        # Create layout
        layout = QVBoxLayout(self.frame)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Add title
        title_label = QLabel("LAST CHANCE!", self.frame)
        title_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #f39c12;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Add message
        message_label = QLabel("Start next round?", self.frame)
        message_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
        """)
        message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(message_label)
        
        layout.addStretch(1)
        
        # Add button
        self.yes_button = QPushButton("Yes, Start Next Round", self.frame)
        self.yes_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 16px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #d35400;
            }
        """)
        self.yes_button.setCursor(Qt.PointingHandCursor)
        self.yes_button.clicked.connect(self._handle_yes)
        layout.addWidget(self.yes_button)
        
        # Center dialog
        self.center_on_screen()

    def center_on_screen(self):
        try:
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.geometry()
                x = (screen_geometry.width() - self.width()) // 2
                y = (screen_geometry.height() - self.height()) // 2
                self.move(x, y)
            else:
                screen_geometry = QApplication.desktop().screenGeometry()
                x = (screen_geometry.width() - self.width()) // 2
                y = (screen_geometry.height() - self.height()) // 2
                self.move(x, y)
        except AttributeError:
            pass

    def _handle_yes(self):
        self.yes_clicked.emit()
        self.close()

class GameCleanedUpDialog(BaseDialog):
    ok_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 250)
        
        # Create main frame
        self.frame = QFrame(self)
        self.frame.setObjectName("dialog_frame")
        self.frame.setGeometry(0, 0, 400, 250)
        
        # Apply styling
        self.frame.setStyleSheet("""
            #dialog_frame {
                background-color: rgba(20, 20, 40, 0.98);
                border: 3px solid #e74c3c;
                border-radius: 10px;
            }
        """)
        
        # Create layout
        layout = QVBoxLayout(self.frame)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Add title
        title_label = QLabel("Game Over", self.frame)
        title_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #e74c3c;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Add message
        message_label = QLabel("The game session has ended or been cleaned up by the server.", self.frame)
        message_label.setStyleSheet("""
            font-size: 16px;
            color: white;
        """)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        layout.addStretch(1)
        
        # Add button
        self.ok_button = QPushButton("OK", self.frame)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 16px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.ok_button.setCursor(Qt.PointingHandCursor)
        self.ok_button.clicked.connect(self._handle_ok)
        layout.addWidget(self.ok_button)
        
        # Center dialog
        self.center_on_screen()

    def center_on_screen(self):
        try:
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.geometry()
                x = (screen_geometry.width() - self.width()) // 2
                y = (screen_geometry.height() - self.height()) // 2
                self.move(x, y)
            else:
                screen_geometry = QApplication.desktop().screenGeometry()
                x = (screen_geometry.width() - self.width()) // 2
                y = (screen_geometry.height() - self.height()) // 2
                self.move(x, y)
        except AttributeError:
            pass

    def _handle_ok(self):
        self.ok_clicked.emit()
        self.close()

class InfoDialog(BaseDialog):
    def __init__(self, title, text, button_text="OK", parent=None):
        super().__init__(parent)
        self.setFixedSize(400, 250)
        
        # Create main frame
        self.frame = QFrame(self)
        self.frame.setObjectName("dialog_frame")
        self.frame.setGeometry(0, 0, 400, 250)
        
        # Apply styling
        self.frame.setStyleSheet("""
            #dialog_frame {
                background-color: rgba(20, 20, 40, 0.98);
                border: 3px solid #3498db;
                border-radius: 10px;
            }
        """)
        
        # Create layout
        layout = QVBoxLayout(self.frame)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # Add title
        title_label = QLabel(title, self.frame)
        title_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #3498db;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Add message
        message_label = QLabel(text, self.frame)
        message_label.setStyleSheet("""
            font-size: 16px;
            color: white;
        """)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        layout.addStretch(1)
        
        # Add button
        self.ok_button = QPushButton(button_text, self.frame)
        self.ok_button.setStyleSheet("""
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
        """)
        self.ok_button.setCursor(Qt.PointingHandCursor)
        self.ok_button.clicked.connect(self.accept)
        layout.addWidget(self.ok_button)
        
        # Center dialog
        self.center_on_screen()

    def center_on_screen(self):
        try:
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.geometry()
                x = (screen_geometry.width() - self.width()) // 2
                y = (screen_geometry.height() - self.height()) // 2
                self.move(x, y)
            else:
                screen_geometry = QApplication.desktop().screenGeometry()
                x = (screen_geometry.width() - self.width()) // 2
                y = (screen_geometry.height() - self.height()) // 2
                self.move(x, y)
        except AttributeError:
            pass

class MultiplayerGameOverDialog(BaseDialog):
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
        
        # For dragging is handled by BaseDialog
        
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
        
    def closeEvent(self, event):
        """Ensure timer is stopped when dialog is closed"""
        self.loading_timer.stop()
        super().closeEvent(event) 