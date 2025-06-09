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
        """Start the animation sequence"""
        self.show()
        self.raise_()
        
        # Set a timer to hide the effect after the duration
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.cleanup)
        self.timer.start(duration)
    
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
    
    def cleanup(self):
        """Clean up resources safely"""
        try:
            # Store reference to timer locally and set instance variable to None first
            # to prevent multiple accesses to a potentially deleted timer
            local_timer = None
            if hasattr(self, 'timer'):
                local_timer = self.timer
                self.timer = None  # Clear reference immediately
            
            # Now work with the local reference
            if local_timer is not None:
                try:
                    if local_timer.isActive():
                        local_timer.stop()
                    
                    # Try to disconnect signals
                    try:
                        local_timer.timeout.disconnect()
                    except:
                        pass
                except RuntimeError:
                    # Timer already deleted, nothing to do
                    pass
            
            # Hide if visible - use try/except to catch deleted widget errors
            try:
                if self.isVisible():
                    self.hide()
            
                # Queue for deletion
                self.deleteLater()
            except RuntimeError:
                # Widget already deleted, nothing to do
                pass
        except Exception as e:
            # Suppress specific "wrapped C/C++ object" errors to reduce log noise
            if "wrapped C/C++ object" not in str(e):
                print(f"Error cleaning up round transition effect: {e}")
                import traceback
                traceback.print_exc() 