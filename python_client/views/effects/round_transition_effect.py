from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QPainter, QColor, QFont

class RoundTransitionEffect(QWidget):
    """Creates a round transition animation overlay effect"""
    
    def __init__(self, parent=None, text="Next Round"):
        super().__init__(parent)
        self.parent = parent
        self.text = text
        
        # Set up the widget to be transparent and ignore mouse events
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set size to match parent
        if parent:
            self.setGeometry(parent.rect())
        
        # Hide initially
        self.hide()
    
    def start_animation(self, duration=1000):
        """Start the transition animation"""
        self.show()
        
        # Create animation to fade in and out
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(duration)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setKeyValueAt(0.4, 0.8)  # Peak opacity at 40% of the animation
        self.fade_anim.setEndValue(0)
        self.fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        
        # Connect cleanup
        self.fade_anim.finished.connect(self._cleanup)
        
        # Start animation
        self.fade_anim.start()
        
    def _cleanup(self):
        """Clean up resources when animation is done"""
        self.hide()
        self.deleteLater()
    
    def set_text(self, text):
        """Set the text to display during transition"""
        self.text = text
        self.update()
    
    def paintEvent(self, event):
        """Custom paint event to draw the transition effect"""
        painter = QPainter(self)
        
        # Fill with semi-transparent black background
        painter.fillRect(self.rect(), QColor(0, 0, 0, int(self.windowOpacity() * 180)))
        
        # Set up font for the text
        font = QFont("Arial", 24, QFont.Bold)
        painter.setFont(font)
        
        # Draw text in white
        painter.setPen(Qt.white)
        painter.drawText(self.rect(), Qt.AlignCenter, self.text) 