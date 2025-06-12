from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPainter, QColor, QFont
import traceback

class RoundTransitionEffect(QWidget):
    """Creates a round transition animation overlay effect"""
    
    # Class-level variable to track created instances (to prevent multiple instances)
    _active_instances = []
    
    @classmethod
    def cleanup_all_instances(cls):
        """Static method to clean up all active instances"""
        for instance in cls._active_instances[:]:  # Use a copy of the list to avoid modification during iteration
            try:
                if instance is not None:
                    instance.cleanup()
            except Exception:
                # Silently handle any errors during cleanup
                pass
        cls._active_instances.clear()
    
    def __init__(self, parent=None, text="Next Round"):
        # Clean up any existing instances first
        RoundTransitionEffect.cleanup_all_instances()
        
        super().__init__(parent)
        self.text = text
        self.opacity = 0.0
        self.timer = None  # Initialize timer to None
        self.animation = None  # Track animation object
        
        # Ensure we're a top-level overlay
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)  # Allow clicking through
        
        # Set parent size with fallback
        if parent and not parent.isHidden():
            self.setFixedSize(parent.size())
        else:
            self.setFixedSize(800, 600)  # Default size
        
        # Hide initially
        self.hide()
        
        # Register this instance
        RoundTransitionEffect._active_instances.append(self)
    
    def start_animation(self, duration=1000):
        """Start the flash animation"""
        try:
            if self.animation is not None:
                self.animation.stop()
            
            self.show()
            self.raise_()  # Ensure it's on top
            
            # Create and set up fade in/out animation
            self.animation = QPropertyAnimation(self, b"windowOpacity")
            self.animation.setDuration(duration)
            self.animation.setStartValue(0.0)
            self.animation.setKeyValueAt(0.5, 1.0)
            self.animation.setEndValue(0.0)
            self.animation.setEasingCurve(QEasingCurve.InOutQuad)
            self.animation.finished.connect(self.cleanup)
            self.animation.start()
        except Exception as e:
            print(f"Error starting round transition animation: {e}")
            self.cleanup()  # Clean up on error
    
    def set_text(self, text):
        """Update the text displayed in the transition"""
        self.text = text
        self.update()  # Trigger repaint
    
    def paintEvent(self, event):
        """Paint the transition effect"""
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Fill background with semi-transparent black
            painter.fillRect(self.rect(), QColor(0, 0, 0, 180))
            
            # Draw the text
            font = QFont("Arial", 36, QFont.Bold)
            painter.setFont(font)
            painter.setPen(QColor(255, 255, 255))
            
            # Center the text
            text_rect = self.rect()
            painter.drawText(text_rect, Qt.AlignCenter, self.text)
            
        except Exception as e:
            print(f"Error in round transition paint event: {e}")
    
    def cleanup(self):
        """Clean up resources to prevent memory leaks or crashes"""
        try:
            # If the underlying C++ object has already been destroyed, bail out.
            try:
                import sip
                if sip.isdeleted(self):
                    return
            except ImportError:
                pass

            # Store local references to avoid issues if attributes are cleared mid-execution
            local_animation = self.animation if hasattr(self, 'animation') else None
            local_timer = self.timer if hasattr(self, 'timer') else None
            
            # Stop and delete any one-shot timer created elsewhere
            if hasattr(self, '_duration_timer') and self._duration_timer:
                try:
                    if self._duration_timer.isActive():
                        self._duration_timer.stop()
                    self._duration_timer.timeout.disconnect()
                except Exception:
                    pass
                self._duration_timer = None
            
            # Clear instance attributes first to avoid circular references
            self.animation = None
            self.timer = None
            
            # Clean up animation
            if local_animation is not None:
                try:
                    if local_animation.state() == QPropertyAnimation.Running:
                        local_animation.stop()
                    
                    # Disconnect any signals
                    try:
                        local_animation.finished.disconnect()
                    except (RuntimeError, TypeError):
                        pass
                except Exception:
                    pass
            
            # Clean up timer
            if local_timer is not None:
                try:
                    if local_timer.isActive():
                        local_timer.stop()
                    
                    # Disconnect any signals
                    try:
                        local_timer.timeout.disconnect()
                    except (RuntimeError, TypeError):
                        pass
                except Exception:
                    pass
            
            # Remove from active instances list
            try:
                if self in RoundTransitionEffect._active_instances:
                    RoundTransitionEffect._active_instances.remove(self)
            except Exception:
                pass
            
            # Hide and schedule deletion
            try:
                self.hide()
                self.setParent(None)  # Unparent to avoid parent-related crashes
                self.deleteLater()
            except Exception:
                pass
                
        except Exception as e:
            # Only print non-"wrapped C/C++ object" errors to reduce log noise
            if "wrapped C/C++ object" not in str(e):
                print(f"Error in round transition cleanup: {str(e)}")
    
    def __del__(self):
        """Destructor to ensure cleanup when object is garbage collected"""
        try:
            if self in RoundTransitionEffect._active_instances:
                RoundTransitionEffect._active_instances.remove(self)
        except Exception:
            pass 