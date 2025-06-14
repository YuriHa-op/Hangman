from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt

class BaseDialog(QDialog):
    """Base class for all dialogs with common functionality."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.old_pos = None

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