from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QMessageBox, QDialog, 
                            QApplication, QGraphicsOpacityEffect, QFrame, QStyle)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtProperty, QPoint
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QPalette, QBrush, QFontDatabase, QIcon
from PyQt5 import uic
import os

class QtLoginView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.login_controller = None
        self._logo_pixmap = None
        self._background_pixmap = None
        self._stylesheet = ""

        # --- Dynamic Path Setup ---
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(base_dir, 'ui', 'qt_login_view.ui')
        style_path = os.path.join(base_dir, 'style', 'login.qss')
        assets_path = os.path.join(base_dir, 'assets')
        logo_path = os.path.join(assets_path, 'logos.png')
        font_path = os.path.join(base_dir, 'fonts', 'Minecraftia.ttf')
        background_path = os.path.join(assets_path, 'login.png')
        
        # --- Load Custom Font ---
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id < 0:
                print(f"Error loading font at: {font_path}")
        else:
            print(f"Font not found at: {font_path}")

        uic.loadUi(ui_path, self)
        
        if self.main_window:
            self.main_window.setFixedSize(900, 600)

        self.setAutoFillBackground(True)

        # --- Load and Apply Stylesheet Dynamically ---
        try:
            with open(style_path, 'r') as f:
                self._stylesheet = f.read().replace("{assets_path}", assets_path.replace("\\", "/"))
                self.setStyleSheet(self._stylesheet)
        except FileNotFoundError:
            print(f"Stylesheet not found at: {style_path}")
        except Exception as e:
            print(f"Error loading stylesheet: {e}")

        # Find widgets by their object names
        self.username_input = self.findChild(QLineEdit, 'username_input')
        self.password_input = self.findChild(QLineEdit, 'password_input')
        self.login_button = self.findChild(QPushButton, 'login_button')
        self.create_account_button = self.findChild(QPushButton, 'create_account_button')
        self.logo_label = self.findChild(QLabel, 'logo_label')

        # Set character limits
        self.username_input.setMaxLength(10)
        self.password_input.setMaxLength(15)

        # Load logo image
        if self.logo_label and os.path.exists(logo_path):
            self._logo_pixmap = QPixmap(logo_path)
            # Initial pixmap set is not needed here, resizeEvent will handle it
        elif not os.path.exists(logo_path):
            print(f"Logo not found at: {logo_path}")

        if os.path.exists(background_path):
            self._background_pixmap = QPixmap(background_path)
        else:
            print(f"Background image not found at: {background_path}")

        # Connect signals to slots
        self.login_button.clicked.connect(self.handle_login)
        self.create_account_button.clicked.connect(self.handle_create_account)

    def paintEvent(self, event):
        """Paint the background image, preserving aspect ratio."""
        if self._background_pixmap:
            painter = QPainter(self)
            target_rect = self.rect()
            
            # Scale pixmap to fill the target rect, cropping excess
            scaled_pixmap = self._background_pixmap.scaled(
                target_rect.size(), 
                Qt.KeepAspectRatioByExpanding, 
                Qt.SmoothTransformation
            )
            
            # Center the scaled pixmap
            point = target_rect.center() - scaled_pixmap.rect().center()
            painter.drawPixmap(point, scaled_pixmap)

        super().paintEvent(event)

    def resizeEvent(self, event):
        """This event is called whenever the widget is resized."""
        super().resizeEvent(event)
        # Recalculate and set the pixmap for the logo on resize
        if self.logo_label and self._logo_pixmap:
            # Scale the pixmap to the label's current size
            self.logo_label.setPixmap(self._logo_pixmap.scaled(
                self.logo_label.width(),
                self.logo_label.height(),
                Qt.KeepAspectRatio,
                Qt.FastTransformation  # Keeps pixel art sharp
            ))

    def handle_login(self):
        if not self.login_controller:
            self.show_message("Error", "Login controller not initialized.")
            return
        username = self.username_input.text()
        password = self.password_input.text()
        if not username or not password:
            self.show_message('Error', 'Username and password cannot be empty.')
            return
        self.login_controller.login(username, password)

    def handle_create_account(self):
        if not self.login_controller:
            self.show_message("Error", "Login controller not initialized.")
            return
        username = self.username_input.text()
        password = self.password_input.text()
        if not username or not password:
            self.show_message('Error', 'Username and password cannot be empty for account creation.')
            return
        self.login_controller.create_account(username, password)

    def show_message(self, title, message, success=False):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        
        # Apply the full stylesheet to the dialog
        if self._stylesheet:
            msg_box.setStyleSheet(self._stylesheet)

        # Set text and icon after stylesheet to ensure they are not overridden
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information if success else QMessageBox.Warning)
        
        # Remove window controls (minimize, maximize, close)
        msg_box.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
            
        msg_box.exec_()

    def clear_inputs(self):
        self.username_input.clear()
        self.password_input.clear()

    def show_login_error(self, message):
        self.show_message("Login Failed", message)

    def show_creation_success(self):
        self.show_message("Account Created", "Account created successfully! You can now log in.", success=True)
        self.clear_inputs()

    def show_creation_error(self, message):
        self.show_message("Account Creation Failed", message)

    def show_force_login_dialog(self):
        """Show a custom styled confirmation dialog for forcing logout of another session"""
        dialog = ForceLoginDialog(self)
        result = dialog.exec_()
        return result == QDialog.Accepted

    def show_session_invalidated_dialog(self, reason=""):
        """Show a dialog when session is invalidated by another login"""
        print("Showing session invalidated dialog in Login view")
        try:
            # Force the application to process events before showing the dialog
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()
            
            # Create and show the dialog
            dialog = SessionInvalidatedDialog(self, reason)
            
            # Make sure the dialog is shown on top
            dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowStaysOnTopHint)
            dialog.setWindowModality(Qt.ApplicationModal)
            
            print("Session invalidated dialog created in Login view, about to show")
            
            # Show the dialog and wait for it to close
            result = dialog.exec_()
            
            print("Session invalidated dialog closed with result:", result)
            
            # Force the application to process events again
            QApplication.processEvents()
            
            return result == QDialog.Accepted
        except Exception as e:
            print(f"Error showing session invalidated dialog: {e}")
            import traceback
            traceback.print_exc()
            return False


class ForceLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Account In Use")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #C6C6C6;
                border: 4px solid #555555;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Account Already In Use")
        title_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            font-family: 'Minecraft', sans-serif;
            color: #E64A19;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        # Message
        message_label = QLabel("This account is already logged in elsewhere.\nDo you want to force logout the previous session and login here?")
        message_label.setStyleSheet("""
            font-size: 14px;
            font-family: 'Minecraft', sans-serif;
            text-align: center;
        """)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        yes_button = QPushButton("Yes, Force Logout")
        yes_button.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                font-family: 'Minecraft', sans-serif;
                background-color: #43A047;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #66BB6A, stop:1 #43A047);
                border-radius: 0px;
                border: 2px solid #2d2d2d;
                color: white;
                min-width: 150px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #2E7D32;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #66BB6A, stop:1 #2E7D32);
            }
        """)
        
        no_button = QPushButton("No, Cancel")
        no_button.setStyleSheet("""
            QPushButton {
                font-size: 12px;
                font-family: 'Minecraft', sans-serif;
                background-color: #5c5c5c;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #9e9e9e, stop:1 #707070);
                border-radius: 0px;
                border: 2px solid #2d2d2d;
                color: white;
                min-width: 150px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #707070;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #9e9e9e, stop:1 #8a8a8a);
            }
        """)
        
        button_layout.addWidget(yes_button)
        button_layout.addWidget(no_button)
        
        # Add widgets to layout
        layout.addWidget(title_label)
        layout.addWidget(message_label)
        layout.addLayout(button_layout)
        
        # Connect buttons
        yes_button.clicked.connect(self.accept)
        no_button.clicked.connect(self.reject)
        
        # Set fixed size
        self.setFixedSize(450, 250)
        
    def showEvent(self, event):
        """Center the dialog when shown"""
        super().showEvent(event)
        
        # Get parent's geometry
        parent_pos = self.parent().mapToGlobal(self.parent().rect().center())
        
        # Center dialog on parent
        x = parent_pos.x() - (self.width() // 2)
        y = parent_pos.y() - (self.height() // 2)
        self.move(x, y)
        
        # Add fade-in animation
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()


class ShakeAnimation(QPropertyAnimation):
    """Animation that shakes a widget to draw attention"""
    def __init__(self, target, duration=500):
        super().__init__(target, b"pos")
        
        try:
            # Import QPoint
            from PyQt5.QtCore import QPoint
            
            # Get the current position
            start_pos = target.pos()
            
            # Set duration and curve
            self.setDuration(duration)
            self.setEasingCurve(QEasingCurve.OutElastic)
            
            # Set keyframes for the animation
            self.setKeyValueAt(0, start_pos)
            self.setKeyValueAt(0.1, start_pos + QPoint(10, 0))
            self.setKeyValueAt(0.2, start_pos + QPoint(-10, 0))
            self.setKeyValueAt(0.3, start_pos + QPoint(8, 0))
            self.setKeyValueAt(0.4, start_pos + QPoint(-8, 0))
            self.setKeyValueAt(0.5, start_pos + QPoint(6, 0))
            self.setKeyValueAt(0.6, start_pos + QPoint(-6, 0))
            self.setKeyValueAt(0.7, start_pos + QPoint(4, 0))
            self.setKeyValueAt(0.8, start_pos + QPoint(-4, 0))
            self.setKeyValueAt(0.9, start_pos + QPoint(2, 0))
            self.setKeyValueAt(1, start_pos)
        except Exception as e:
            print(f"Error setting up shake animation: {e}")
            import traceback
            traceback.print_exc()


class SessionInvalidatedDialog(QDialog):
    def __init__(self, parent=None, reason=""):
        super().__init__(parent)
        self.setWindowTitle("Session Ended")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #303030;
                border: 2px solid #FF5555;
                border-radius: 5px;
            }
            QLabel {
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #FF5555;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FF7777;
            }
            QPushButton:pressed {
                background-color: #CC4444;
            }
        """)
        
        # Force the dialog to be shown on top
        self.setWindowModality(Qt.ApplicationModal)
        
        self.setup_ui(reason)
        
    def setup_ui(self, reason):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        
        # Warning icon
        icon_label = QLabel()
        icon = QApplication.style().standardIcon(QStyle.SP_MessageBoxWarning)
        icon_label.setPixmap(icon.pixmap(32, 32))
        header_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel("Session Ended")
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #FF5555;
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Message
        message = "Your session has been ended because you logged in from another location."
        if reason and reason.strip():
            message = reason
            
        message_label = QLabel(message)
        message_label.setStyleSheet("""
            font-size: 12px;
            color: #EEEEEE;
        """)
        message_label.setWordWrap(True)
        
        # Button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("OK")
        ok_button.setFixedWidth(80)
        ok_button.setCursor(Qt.PointingHandCursor)
        button_layout.addWidget(ok_button)
        
        # Add widgets to layout
        layout.addLayout(header_layout)
        layout.addWidget(message_label)
        layout.addLayout(button_layout)
        
        # Connect button
        ok_button.clicked.connect(self.accept)
        
        # Set fixed size - more compact
        self.setFixedSize(350, 150)
        
    def showEvent(self, event):
        """Center the dialog and add animations when shown"""
        super().showEvent(event)
        
        print("Dialog show event triggered")
        
        # Get parent's geometry or center on screen if no parent
        if self.parent():
            parent_pos = self.parent().mapToGlobal(self.parent().rect().center())
        else:
            from PyQt5.QtWidgets import QApplication
            screen_geometry = QApplication.desktop().screenGeometry()
            parent_pos = screen_geometry.center()
        
        # Center dialog on parent
        x = parent_pos.x() - (self.width() // 2)
        y = parent_pos.y() - (self.height() // 2)
        self.move(x, y)
        
        # Add fade-in animation
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.start()
        
        # Add shake animation after fade-in
        QTimer.singleShot(200, self.start_shake_animation)
        
        # Play a system beep sound to get attention
        from PyQt5.QtWidgets import QApplication
        QApplication.beep()
        
        # Force the application to process events
        QApplication.processEvents()
        
        print("Dialog should now be visible")
        
    def start_shake_animation(self):
        """Start the shake animation"""
        try:
            self.shake_animation = ShakeAnimation(self, duration=500)
            self.shake_animation.start()
        except Exception as e:
            print(f"Error starting shake animation: {e}")
            import traceback
            traceback.print_exc() 