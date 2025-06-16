#!/usr/bin/env python3
import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import QFile, QTextStream

def apply_stylesheet(app, style_file):
    """Apply the QSS stylesheet to the application"""
    # Check if the file exists
    if not os.path.exists(style_file):
        print(f"Error: Style file {style_file} not found!")
        return False
    
    try:
        # Read the stylesheet from file
        with open(style_file, "r") as f:
            stylesheet = f.read()
            
        # Apply the stylesheet to the application
        app.setStyleSheet(stylesheet)
        print(f"Applied stylesheet from {style_file}")
        return True
    except Exception as e:
        print(f"Error applying stylesheet: {e}")
        return False

def main():
    # Get the absolute path to the assets directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    style_file = os.path.join(current_dir, "style", "multiplayergame.qss")
    
    print(f"Looking for style file at: {style_file}")
    
    # Create a minimal test application
    app = QApplication([])
    window = QMainWindow()
    window.setWindowTitle("QSS Style Test")
    
    # Apply the stylesheet
    if apply_stylesheet(app, style_file):
        # Create some test buttons to show styling
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        for letter in "ABCDEF":
            btn = QPushButton(letter)
            btn.setObjectName(f"button_{letter}")
            layout.addWidget(btn)
            
        window.setCentralWidget(central_widget)
        window.resize(300, 400)
        window.show()
        sys.exit(app.exec_())
    else:
        print("Failed to apply stylesheet. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    main() 