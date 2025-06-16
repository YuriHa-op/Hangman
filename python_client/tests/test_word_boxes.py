#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QLabel, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt

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

class MaskedWordContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setContentsMargins(5, 5, 5, 5)
        self.layout.setSpacing(5)
        self.letter_boxes = []

    def update_word(self, masked_word):
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

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("4 Pic 1 Word Style Test")
        self.setGeometry(100, 100, 400, 200)
        
        # Create central widget
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Create title label
        title_label = QLabel("4 Pic 1 Word Style Test")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        
        # Create masked word container
        self.masked_word_container = MaskedWordContainer()
        self.masked_word_container.update_word("HANGMAN")
        
        # Create partially revealed word container
        self.partial_word_container = MaskedWordContainer()
        self.partial_word_container.update_word("H_NGM_N")
        
        # Add widgets to layout
        main_layout.addWidget(title_label)
        main_layout.addWidget(QLabel("Complete word:"))
        main_layout.addWidget(self.masked_word_container)
        main_layout.addWidget(QLabel("Partially guessed word:"))
        main_layout.addWidget(self.partial_word_container)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Apply stylesheet if available
        self.load_stylesheet()
        
    def load_stylesheet(self):
        """Load QSS stylesheet for testing"""
        # Go up to the python_client directory
        base_path = os.path.dirname(os.path.abspath(__file__))
        style_path = os.path.join(base_path, 'style', 'multiplayergame.qss')
        
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                style = f.read()
                self.setStyleSheet(style)
            print(f"Applied stylesheet from {style_path}")
        else:
            print(f"Warning: Style sheet not found at {style_path}")

def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 