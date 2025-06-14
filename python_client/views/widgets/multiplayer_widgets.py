from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QGridLayout, QFrame, QScrollArea, QDialog, QMessageBox, QSizePolicy, QProgressBar, QGraphicsOpacityEffect, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QRect, QRectF, QPoint, QEasingCurve, QSequentialAnimationGroup, QParallelAnimationGroup
from PyQt5.QtGui import QFont, QIcon, QPainter, QColor, QPen, QPainterPath, QBrush, QPixmap, QRadialGradient, QLinearGradient
from PyQt5 import uic
import os

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

    def update_health(self, incorrect_guesses, max_guesses=5):
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
            
            #player_health::chunk {{
                background-color: #e74c3c;
                border-radius: 2px;
            }}
        """)
    
    def update_widget(self, score, masked_word, is_finished):
        """Update the widget with new player data"""
        self.score_label.setText(f"Score: {score}")
        self.masked_word_label.setText(masked_word)
        
        # Update status indicator
        if is_finished:
            self.status_indicator.setStyleSheet("background-color: #3498db;") # Blue when finished
        else:
            self.status_indicator.setStyleSheet("background-color: #2ecc71;") # Green if still active
            
        # Calculate and update completion progress based on masked word
        revealed_count = sum(1 for char in masked_word if char.isalpha())
        total_count = sum(1 for char in masked_word if char.isalpha() or char == '_')
        
        if total_count > 0:
            completion_percentage = int((revealed_count / total_count) * 100)
            self.progress_bar.setValue(completion_percentage)
        else:
            self.progress_bar.setValue(0)
    
    def update_health(self, incorrect_guesses, max_guesses=5):
        """Update the health bar based on incorrect guesses"""
        if max_guesses <= 0:
            health_percent = 100
        else:
            health_percent = int(((max_guesses - incorrect_guesses) / max_guesses) * 100)
        
        self.health_bar.setValue(health_percent)
        
        # Update health bar color based on health percentage
        if health_percent <= 25:
            color = "#e74c3c"  # Red when nearly depleted
        elif health_percent <= 50:
            color = "#f39c12"  # Orange when half depleted
        else:
            color = "#2ecc71"  # Green when healthy
            
        self.health_bar.setStyleSheet(f"""
            #player_health {{
                background-color: rgba(50, 50, 50, 0.5);
                border-radius: 2px;
                border: none;
            }}
            
            #player_health::chunk {{
                background-color: {color};
                border-radius: 2px;
            }}
        """)
    
    def update_win_streak(self, streak):
        """Update the win streak and apply golden glow for streaks >= 2"""
        self.win_streak = streak
        
        if streak >= 2:
            # Show golden glow effect for win streak
            self.setStyleSheet("""
                #player_status_widget {
                    background-color: rgba(30, 30, 30, 0.7);
                    border-radius: 10px;
                    border: 1px solid rgba(212, 175, 55, 0.8);
                    box-shadow: 0 0 10px rgba(212, 175, 55, 0.5);
                }
                
                #player_header {
                    background-color: rgba(40, 40, 40, 0.9);
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    border-bottom: 1px solid rgba(212, 175, 55, 0.5);
                }
                
                #username_label {
                    color: rgba(212, 175, 55, 1.0);
                    font-weight: bold;
                    font-size: 12px;
                }
                
                #score_label {
                    color: rgba(212, 175, 55, 1.0);
                    font-weight: bold;
                    font-size: 11px;
                }
            """)
            
            # Start the glow animation if not running
            if not self.glow_animation.state() == QPropertyAnimation.Running:
                self.glow_animation.start()
                
            # Update score label to show streak
            self.score_label.setText(f"Score: {self.score_label.text().split(':')[1].strip()} 🔥{streak}")
        else:
            # Reset to default style
            self.apply_stylesheets()
            
            # Stop the glow animation
            self.glow_animation.stop()
            self.glow_effect.setOpacity(1.0)

class VirtualKeyboard(QWidget):
    """A customizable on-screen virtual keyboard for letter selection"""
    
    # Define signal to emit when a letter is clicked
    letterClicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Keyboard layout settings
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)  # Reduced spacing between rows
        self.setMinimumWidth(450)  # Ensure minimum width to fit all keys
        
        # Create rows of buttons
        self.row1 = QHBoxLayout()
        self.row2 = QHBoxLayout()
        self.row3 = QHBoxLayout()
        
        # Set spacing between buttons in each row
        self.row1.setSpacing(6)  # Reduced button spacing
        self.row2.setSpacing(6)  # Reduced button spacing
        self.row3.setSpacing(6)  # Reduced button spacing
        
        # Set alignment for all rows to prevent cutting off
        self.row1.setAlignment(Qt.AlignCenter)
        self.row2.setAlignment(Qt.AlignCenter)
        self.row3.setAlignment(Qt.AlignCenter)
        
        # Add rows to main layout
        self.layout.addLayout(self.row1)
        self.layout.addLayout(self.row2)
        self.layout.addLayout(self.row3)
        
        # Dictionary to store button references
        self.buttons = {}
        
        # Create buttons for each row - make all rows centered for consistent spacing
        self.create_row_buttons(self.row1, "QWERTYUIOP", center=True)
        self.create_row_buttons(self.row2, "ASDFGHJKL", center=True)
        self.create_row_buttons(self.row3, "ZXCVBNM", center=True)
        
        # Apply styling
        self.apply_styling()
        
        # Set of letters that are currently in a "pending" state
        self.pending_letters = set()
        
        # Store guessed letters and correct letters
        self.guessed_letters = set()
        self.correct_letters = set()
        
    def create_row_buttons(self, row_layout, letters, center=False):
        """Create buttons for a row of the keyboard"""
        if center:
            row_layout.addStretch()
            
        for letter in letters:
            button = QPushButton(letter)
            button.setFixedSize(40, 40)  # Reduced button size 
            button.setFocusPolicy(Qt.NoFocus)  # Prevent focus outline
            button.clicked.connect(lambda checked, l=letter: self.on_letter_clicked(l))
            row_layout.addWidget(button)
            self.buttons[letter] = button
            
        if center:
            row_layout.addStretch()
    
    def apply_styling(self):
        """Apply default styling to the keyboard and buttons"""
        # Style for the main widget
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
            
            QPushButton {
                background-color: rgba(52, 73, 94, 0.8);
                border: 1px solid rgba(52, 73, 94, 0.9);
                border-radius: 5px;
                color: white;
                font-weight: bold;
                font-size: 14px;  /* Reduced font size */
                font-family: Arial;
                min-width: 40px;  /* Reduced min width */
                min-height: 40px; /* Reduced min height */
                padding: 3px;     /* Reduced padding */
            }
            
            QPushButton:hover {
                background-color: rgba(52, 73, 94, 1.0);
            }
            
            QPushButton:pressed {
                background-color: rgba(44, 62, 80, 1.0);
            }
            
            QPushButton:disabled {
                background-color: rgba(127, 140, 141, 0.6);
                color: rgba(236, 240, 241, 0.5);
            }
        """)
    
    def on_letter_clicked(self, letter):
        """Handle letter button click events"""
        if letter in self.guessed_letters:
            # Already guessed, do nothing
            return
            
        # Set to pending state
        self.set_button_pending(letter)
        
        # Animate the button press
        if letter in self.buttons:
            self.animate_button_press(self.buttons[letter])
        
        # Emit signal with the letter that was clicked
        self.letterClicked.emit(letter)
    
    def animate_button_press(self, button):
        """Animate button press with a simple scale down/up effect"""
        # Store original size and geometry
        original_size = button.size()
        original_geometry = button.geometry()
        
        # Create animation group
        animation_group = QSequentialAnimationGroup(button)
        
        # Create "press down" animation (scale down slightly)
        press_anim = QPropertyAnimation(button, b"geometry")
        press_anim.setDuration(50)  # Very short duration
        
        # Calculate the scaled down size (90% of original)
        scaled_width = int(original_size.width() * 0.9)
        scaled_height = int(original_size.height() * 0.9)
        
        # Calculate position adjustment to keep button centered
        x_offset = (original_size.width() - scaled_width) // 2
        y_offset = (original_size.height() - scaled_height) // 2
        
        press_anim.setStartValue(original_geometry)
        press_anim.setEndValue(QRect(
            original_geometry.x() + x_offset,
            original_geometry.y() + y_offset,
            scaled_width,
            scaled_height
        ))
        
        # Create "release" animation (back to original size)
        release_anim = QPropertyAnimation(button, b"geometry")
        release_anim.setDuration(50)
        release_anim.setStartValue(QRect(
            original_geometry.x() + x_offset,
            original_geometry.y() + y_offset,
            scaled_width,
            scaled_height
        ))
        release_anim.setEndValue(original_geometry)
        
        # Add animations to the group and start
        animation_group.addAnimation(press_anim)
        animation_group.addAnimation(release_anim)
        animation_group.start()
    
    def set_button_pending(self, letter):
        """Set a button to a 'pending' state while waiting for guess result"""
        if letter not in self.buttons:
            return
            
        button = self.buttons[letter]
        button.setStyleSheet("""
            background-color: rgba(241, 196, 15, 0.8);
            color: #34495e;
            border: 1px solid rgba(241, 196, 15, 1.0);
            border-radius: 5px;
            font-weight: bold;
        """)
        
        # Add to pending set
        self.pending_letters.add(letter)
        
    def update_button_color(self, letter, is_correct):
        """Update button color based on whether the guess was correct"""
        if letter not in self.buttons:
            return
            
        button = self.buttons[letter]
        
        # Remove from pending set
        self.pending_letters.discard(letter)
        
        # Add to guessed set
        self.guessed_letters.add(letter)
        
        # Update correct letters set if needed
        if is_correct:
            self.correct_letters.add(letter)
            # Animate success
            self.animate_button_success(button)
        else:
            # Animate failure
            self.animate_button_failure(button)
        
        if is_correct:
            # Correct guess - green
            button.setStyleSheet("""
                background-color: #2ecc71;
                color: white;
                border: 1px solid #27ae60;
                border-radius: 5px;
                font-weight: bold;
            """)
        else:
            # Incorrect guess - red
            button.setStyleSheet("""
                background-color: #e74c3c;
                color: white;
                border: 1px solid #c0392b;
                border-radius: 5px;
                font-weight: bold;
            """)
        
        # Disable the button
        button.setEnabled(False)
    
    def animate_button_success(self, button):
        """Animate the button with a success animation (bounce)"""
        original_pos = button.pos()
        
        animation = QSequentialAnimationGroup(button)
        
        # Small bounce up
        bounce_up = QPropertyAnimation(button, b"pos")
        bounce_up.setDuration(120)
        bounce_up.setStartValue(original_pos)
        bounce_up.setEndValue(QPoint(original_pos.x(), original_pos.y() - 10))
        bounce_up.setEasingCurve(QEasingCurve.OutQuad)
        
        # Bounce down
        bounce_down = QPropertyAnimation(button, b"pos")
        bounce_down.setDuration(120)
        bounce_down.setStartValue(QPoint(original_pos.x(), original_pos.y() - 10))
        bounce_down.setEndValue(original_pos)
        bounce_down.setEasingCurve(QEasingCurve.OutBounce)
        
        animation.addAnimation(bounce_up)
        animation.addAnimation(bounce_down)
        animation.start()
    
    def animate_button_failure(self, button):
        """Animate the button with a failure animation (shake)"""
        original_pos = button.pos()
        
        animation = QSequentialAnimationGroup(button)
        
        # Small shake left and right
        for i in range(2):
            # Shake right
            shake_right = QPropertyAnimation(button, b"pos")
            shake_right.setDuration(50)
            shake_right.setStartValue(original_pos)
            shake_right.setEndValue(QPoint(original_pos.x() + 5, original_pos.y()))
            
            # Shake left
            shake_left = QPropertyAnimation(button, b"pos")
            shake_left.setDuration(50)
            shake_left.setStartValue(QPoint(original_pos.x() + 5, original_pos.y()))
            shake_left.setEndValue(QPoint(original_pos.x() - 5, original_pos.y()))
            
            animation.addAnimation(shake_right)
            animation.addAnimation(shake_left)
        
        # Return to original position
        return_anim = QPropertyAnimation(button, b"pos")
        return_anim.setDuration(50)
        return_anim.setStartValue(QPoint(original_pos.x() - 5, original_pos.y()))
        return_anim.setEndValue(original_pos)
        
        animation.addAnimation(return_anim)
        animation.start()
        
    def update_keyboard(self, guessed_letters, correct_letters, enabled=True):
        """Update the keyboard state with new guesses"""
        # Store the sets for later use
        self.guessed_letters = {letter.upper() for letter in guessed_letters}
        self.correct_letters = {letter.upper() for letter in correct_letters}
        self.pending_letters = set()
        
        # Reset all buttons first
        for letter, button in self.buttons.items():
            # Reset style
            button.setStyleSheet("")
            button.setEnabled(enabled)
            
            # If this letter has been guessed
            if letter in self.guessed_letters:
                if letter in self.correct_letters:
                    # Correct guess - green
                    button.setStyleSheet("""
                        background-color: #2ecc71;
                        color: white;
                        border: 1px solid #27ae60;
                        border-radius: 5px;
                        font-weight: bold;
                    """)
                else:
                    # Incorrect guess - red
                    button.setStyleSheet("""
                        background-color: #e74c3c;
                        color: white;
                        border: 1px solid #c0392b;
                        border-radius: 5px;
                        font-weight: bold;
                    """)
                button.setEnabled(False)

