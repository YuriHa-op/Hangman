from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QFontDatabase, QFont
import sys
import os

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Font Test")
        self.setGeometry(100, 100, 400, 200)
        
        # Create a label
        self.label = QLabel("Testing QFontDatabase", self)
        self.label.setGeometry(50, 50, 300, 100)
        
        # Try loading a font
        base_dir = os.path.dirname(os.path.abspath(__file__))
        font_path = os.path.join(base_dir, 'views', 'fonts', 'Minecraftia.ttf')
        
        if os.path.exists(font_path):
            print(f"Font file exists at: {font_path}")
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id >= 0:
                print("Font loaded successfully!")
                font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                print(f"Font family: {font_family}")
                
                # Apply the font
                font = QFont(font_family, 12)
                self.label.setFont(font)
            else:
                print("Failed to load font")
        else:
            print(f"Font file not found at: {font_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_()) 