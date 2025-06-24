import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from models.game_model import GameModel
from views.qt_login_view import QtLoginView
from controllers.login_controller import LoginController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hangman Login")
        self.view = None

    def show_view(self, view_name):
        # This is a placeholder to prevent crashes, as the app will close on successful login.
        print(f"Attempting to show view: {view_name}, but application should close.")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create the main window that will contain our views
    main_window = MainWindow()

    # Create MVC components
    model = GameModel()
    login_view = QtLoginView(main_window)
    login_controller = LoginController(model, login_view)

    # Connect controller to the view
    login_view.login_controller = login_controller

    # Set the central widget and show the main window
    main_window.setCentralWidget(login_view)
    main_window.show()

    sys.exit(app.exec_())
