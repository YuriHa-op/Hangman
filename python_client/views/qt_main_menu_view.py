from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QGraphicsView, QGraphicsScene, QGridLayout
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QFontDatabase, QPainter, QTransform, QIcon
from PyQt5 import uic
import os

class SlantedLabel(QLabel):
    """A custom QLabel that is slanted."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rotation = -15  # Static slant

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        transform = QTransform()
        cx = self.width() / 2
        cy = self.height() / 2
        
        transform.translate(cx, cy)
        transform.rotate(self._rotation)
        transform.translate(-cx, -cy)
        
        painter.setTransform(transform)
        super().paintEvent(event)

class QtMainMenuView(QWidget):
    def __init__(self, main_window=None):
        super().__init__(main_window)
        self.main_window = main_window
        self._stylesheet = ""
        self._background_pixmap = None
        self._logo_pixmap = None

        base_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(base_dir, 'ui', 'qt_main_menu_view.ui')
        style_path = os.path.join(base_dir, 'style', 'menu.qss')
        assets_path = os.path.join(base_dir, 'assets')
        logo_path = os.path.join(assets_path, 'logos.png')
        background_path = os.path.join(assets_path, 'menu.png')

        uic.loadUi(ui_path, self)

        # Load Stylesheet
        try:
            with open(style_path, 'r') as f:
                self._stylesheet = f.read()
                self.setStyleSheet(self._stylesheet)
        except Exception as e:
            print(f"Error loading menu stylesheet: {e}")

        # Load Images
        if os.path.exists(logo_path):
            self._logo_pixmap = QPixmap(logo_path)
        if os.path.exists(background_path):
            self._background_pixmap = QPixmap(background_path)

        # Find widgets
        self.single_player_button = self.findChild(QPushButton, "single_player_button")
        self.multiplayer_button = self.findChild(QPushButton, "multiplayer_button")
        self.leaderboard_button = self.findChild(QPushButton, "leaderboard_button")
        self.match_history_button = self.findChild(QPushButton, "match_history_button")
        self.logout_button = self.findChild(QPushButton, "logout_button")
        self.logo_label = self.findChild(QLabel, "logo_label")
        self.footer_left_label = self.findChild(QLabel, "footer_left_label")
        self.footer_right_label = self.findChild(QLabel, "footer_right_label")
        self.splash_container = self.findChild(QWidget, "splash_container")

        # Set logo and footer text
        if self.logo_label and self._logo_pixmap:
            self.logo_label.setPixmap(self._logo_pixmap)
            self.logo_label.setScaledContents(True)

        self.footer_left_label.setText("Hangman 0.69")
        self.footer_right_label.setText("ultimatum edition")

        self._set_button_icons()

        # Create splash text
        self._setup_splash_text()

    def _set_button_icons(self):
        assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
        icon_size = QSize(24, 24)

        button_icons = {
            self.single_player_button: 'games.png',
            self.multiplayer_button: 'multiplayer.png',
            self.leaderboard_button: 'trophy.png',
            self.match_history_button: 'history.png',
            self.logout_button: 'leave.png'
        }

        for button, icon_file in button_icons.items():
            icon_path = os.path.join(assets_path, icon_file)
            if button and os.path.exists(icon_path):
                button.setIcon(QIcon(icon_path))
                button.setIconSize(icon_size)

    def _setup_splash_text(self):
        if not self.splash_container:
            return

        self.splash_label = SlantedLabel("9491-Team02_FinProject")
        self.splash_label.setObjectName("splash_label")
        self.splash_label.setStyleSheet(self._stylesheet)
        self.splash_label.setAlignment(Qt.AlignCenter)

        layout = self.splash_container.layout()
        if layout is None:
            layout = QVBoxLayout()
            self.splash_container.setLayout(layout)
        layout.addWidget(self.splash_label)

    def paintEvent(self, event):
        """Paint the background image."""
        if self._background_pixmap:
            painter = QPainter(self)
            scaled_pixmap = self._background_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            point = self.rect().center() - scaled_pixmap.rect().center()
            painter.drawPixmap(point, scaled_pixmap)
        super().paintEvent(event)

    def set_welcome_message(self, username):
        # Placeholder for future use, e.g., a QLabel to display "Welcome, [username]!"
        pass 