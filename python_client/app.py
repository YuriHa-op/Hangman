from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt5.QtCore import QSize
import sys
import os
from models.game_model import GameModel
# from views.app_view import HangmanApp # Updated import for HangmanApp # TODO: Will be replaced with PyQt5 main window
# Specific view and controller imports are handled within HangmanApp (app_view.py)

# Import PyQt Views
from views.qt_login_view import QtLoginView
from views.qt_main_menu_view import QtMainMenuView
from views.qt_leaderboard_view import QtLeaderboardView
from views.qt_match_history_view import QtMatchHistoryView
# from views.qt_single_player_game_view import QtSinglePlayerGameView # Old solo game view
from views.qt_single_player_1v1_game_view import QtSinglePlayer1v1GameView # New 1v1 game view
from views.qt_multiplayer_queue_view import QtMultiplayerQueueView
from views.qt_multiplayer_game_view import QtMultiplayerGameView
from views.qt_multiplayer_game_results_view import QtMultiplayerGameResultsView

# Import Controllers
from controllers.login_controller import LoginController
from controllers.main_menu_controller import MainMenuController
from controllers.leaderboard_controller import LeaderboardController
from controllers.match_history_controller import MatchHistoryController
from controllers.single_player_game_controller import SinglePlayerGameController
from controllers.multiplayer_queue_controller import MultiplayerQueueController
from controllers.multiplayer_game_controller import MultiplayerGameController
from controllers.multiplayer_game_results_controller import MultiplayerGameResultsController

def load_stylesheet(app, style_name):
    """Load a QSS stylesheet from the assets directory"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    style_path = os.path.join(base_path, 'assets', style_name)
    
    if os.path.exists(style_path):
        with open(style_path, "r") as f:
            style = f.read()
            app.setStyleSheet(style)
        print(f"Applied stylesheet: {style_name}")
        return True
    else:
        print(f"Warning: Style sheet not found at {style_path}")
        return False

# Placeholder for the main PyQt5 window - this will be expanded
class MainWindow(QMainWindow):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.setWindowTitle("Hangman Game - PyQt Edition")
        # self.setGeometry(100, 100, 800, 600) # Removed to allow LoginView to set fixed size

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.views = {}
        self.controllers = {}
        self.current_view_name = None

        self._create_views_and_controllers()
        self.show_view("Login")

    def _create_views_and_controllers(self):
        # Login View
        login_view = QtLoginView(main_window=self) # Removed controller_factory, controller will be set by MainWindow
        login_controller = LoginController(self.model, login_view)
        login_view.login_controller = login_controller # Ensure view has its controller if needed for direct calls
        self.add_view("Login", login_view, login_controller)

        # Main Menu View
        main_menu_view = QtMainMenuView(main_window=self) # Removed controller_factory
        main_menu_controller = MainMenuController(self.model, main_menu_view)
        # Connect main menu buttons to their respective controller methods
        main_menu_view.single_player_button.clicked.connect(main_menu_controller.start_single_player)
        main_menu_view.multiplayer_button.clicked.connect(main_menu_controller.go_to_multiplayer_queue)
        main_menu_view.leaderboard_button.clicked.connect(main_menu_controller.show_leaderboard)
        main_menu_view.match_history_button.clicked.connect(main_menu_controller.show_match_history)
        main_menu_view.logout_button.clicked.connect(self.logout_user_and_show_login) # Connect to MainWindow method
        self.add_view("MainMenu", main_menu_view, main_menu_controller)

        # Leaderboard View
        leaderboard_view = QtLeaderboardView(main_window=self)
        leaderboard_controller = LeaderboardController(self.model, leaderboard_view)
        leaderboard_view.set_controller(leaderboard_controller) # Assign controller to view
        self.add_view("Leaderboard", leaderboard_view, leaderboard_controller)

        # Match History View
        match_history_view = QtMatchHistoryView(main_window=self)
        match_history_controller = MatchHistoryController(self.model, match_history_view)
        match_history_view.set_controller(match_history_controller)
        self.add_view("MatchHistory", match_history_view, match_history_controller)

        # Single Player 1v1 Game View
        single_player_1v1_game_view = QtSinglePlayer1v1GameView(main_window=self)
        # The SinglePlayerGameController should now contain the 1v1 logic
        single_player_game_controller = SinglePlayerGameController(self.model, single_player_1v1_game_view)
        single_player_1v1_game_view.set_controller(single_player_game_controller)
        self.add_view("SinglePlayer1v1Game", single_player_1v1_game_view, single_player_game_controller)

        # Multiplayer Queue View
        multiplayer_queue_view = QtMultiplayerQueueView(main_window=self)
        multiplayer_queue_controller = MultiplayerQueueController(self.model, multiplayer_queue_view)
        multiplayer_queue_view.set_controller(multiplayer_queue_controller)
        self.add_view("MultiplayerQueue", multiplayer_queue_view, multiplayer_queue_controller)

        # Multiplayer Game View
        multiplayer_game_view = QtMultiplayerGameView(main_window=self)
        multiplayer_game_controller = MultiplayerGameController(self.model, multiplayer_game_view)
        multiplayer_game_view.set_controller(multiplayer_game_controller)
        self.add_view("MultiplayerGame", multiplayer_game_view, multiplayer_game_controller)

        # Multiplayer Game Results View
        multiplayer_results_view = QtMultiplayerGameResultsView(main_window=self)
        multiplayer_results_controller = MultiplayerGameResultsController(self.model, multiplayer_results_view)
        multiplayer_results_view.set_controller(multiplayer_results_controller)
        self.add_view("MultiplayerGameResults", multiplayer_results_view, multiplayer_results_controller)

        # TODO: Instantiate and add other views and controllers here
        # Example for a placeholder view that might exist:
        # placeholder_view = QWidget() # Replace with actual view class
        # placeholder_label = QLabel("This is a Placeholder View")
        # placeholder_layout = QVBoxLayout()
        # placeholder_layout.addWidget(placeholder_label)
        # placeholder_view.setLayout(placeholder_layout)
        # self.add_view("Placeholder", placeholder_view, None) # No controller for simple placeholder

    def add_view(self, name, view_widget, controller):
        self.views[name] = view_widget
        if controller:
            self.controllers[name] = controller
        self.stacked_widget.addWidget(view_widget)

    def set_window_background(self, image_path=None):
        if image_path and os.path.exists(image_path):
            style = f"""
                MainWindow {{
                    background-image: url({image_path.replace('\\', '/')});
                    background-position: center;
                    background-repeat: no-repeat;
                    background-size: cover;
                }}
            """
            self.setStyleSheet(style)
        else:
            self.setStyleSheet("") # Clear background

    def show_view(self, view_name):
        if view_name in self.views:
            if self.current_view_name and self.current_view_name in self.controllers and hasattr(self.controllers[self.current_view_name], 'on_hide'):
                self.controllers[self.current_view_name].on_hide()
            
            # Unset fixed size from previous view (e.g., Login) to allow resizing
            self.setMinimumSize(0, 0)
            self.setMaximumSize(16777215, 16777215)
            
            # Set background for multiplayer game view
            if view_name == "MultiplayerGame":
                base_path = os.path.dirname(os.path.abspath(__file__))
                image_path = os.path.join(base_path, 'assets', 'img.png')
                self.set_window_background(image_path)
            else:
                self.set_window_background(None) # Remove for other views

            current_widget = self.views[view_name]
            self.stacked_widget.setCurrentWidget(current_widget)
            self.current_view_name = view_name
            
            # Resize window to fit the new view's size.
            self.resize(current_widget.size())

            # If the new view is the login view, make the window fixed size again.
            # The login view itself sets this, but we ensure it here as well for consistency.
            if view_name == "Login":
                self.setFixedSize(current_widget.size())
            
            if view_name in self.controllers and hasattr(self.controllers[view_name], 'on_show'):
                self.controllers[view_name].on_show()
            
            # Update window title based on view
            current_widget_title = self.views[view_name].windowTitle()
            if current_widget_title:
                self.setWindowTitle(f"Hangman Game - {current_widget_title}")
            else:
                self.setWindowTitle(f"Hangman Game - {view_name}")
        else:
            print(f"Error: View '{view_name}' not found.")
            QMessageBox.critical(self, "Navigation Error", f"View '{view_name}' does not exist or is not yet implemented.")

    def logout_user_and_show_login(self):
        # First, ensure any active game is properly ended if current view is a game view
        current_game_view_name = "SinglePlayer1v1Game" # Updated name
        if self.current_view_name == current_game_view_name and current_game_view_name in self.controllers:
            print(f"MainWindow: Logging out during active {current_game_view_name} game. Attempting to end game.")
            # Ensure the controller has a method to handle game exit properly
            if hasattr(self.controllers[current_game_view_name], 'handle_back_to_menu_from_sp_game'):
                 self.controllers[current_game_view_name].handle_back_to_menu_from_sp_game()
            elif hasattr(self.controllers[current_game_view_name], 'on_hide'): # Fallback
                 self.controllers[current_game_view_name].on_hide()
            # The show_view("Login") call will happen after this, ensuring proper state change.
        # Add similar checks for multiplayer game if it's active.

        current_user = self.model.get_username()
        if current_user:
            self.model.logout()
            print(f"User '{current_user}' logged out.")
        else:
            print("No user was logged in to log out.")
        
        self.show_view("Login")
        login_view_widget = self.views.get("Login")
        if login_view_widget and hasattr(login_view_widget, 'clear_inputs'):
            login_view_widget.clear_inputs()

    def cleanup_on_exit(self):
        print("Application is about to quit. Performing cleanup...")
        # Ensure any game in progress is cleaned up
        current_game_view_name = "SinglePlayer1v1Game" # Updated name
        if self.current_view_name == current_game_view_name and current_game_view_name in self.controllers:
            if hasattr(self.controllers[current_game_view_name], 'on_hide'):
                 self.controllers[current_game_view_name].on_hide() # This should handle server cleanup
        # Add similar for multiplayer if it has an on_hide that cleans up server state.

        current_user = self.model.get_username()
        if current_user: # Check if a user is *still* logged in (on_hide might have logged them out)
            self.model.logout()
            print(f"User '{current_user}' logged out during application exit.")
        print("Cleanup complete.")

    def closeEvent(self, event):
        self.cleanup_on_exit()
        super().closeEvent(event)


    def create_login_controller(self, view):
        # This was in QtLoginView, assuming it might call controller_factory.create_login_controller()
        # However, MainWindow now directly assigns login_view.login_controller.
        # If QtLoginView still calls this, it should return the already created controller.
        return self.controllers.get("Login")

    def create_main_menu_controller(self, view):
        return self.controllers.get("MainMenu")

    def create_leaderboard_controller(self, view):
        return self.controllers.get("Leaderboard")

    def create_match_history_controller(self, view):
        return self.controllers.get("MatchHistory")

    def create_single_player_game_controller(self, view):
        # This now refers to the controller for the 1v1 game
        return self.controllers.get("SinglePlayer1v1Game")

    def create_multiplayer_queue_controller(self, view):
        return self.controllers.get("MultiplayerQueue")

    def create_multiplayer_game_controller(self, view):
        return self.controllers.get("MultiplayerGame")

    def create_multiplayer_game_results_controller(self, view):
        return self.controllers.get("MultiplayerGameResults")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    model = GameModel()

    
    main_window = MainWindow(model) # Create the main PyQt5 window
    
    app.aboutToQuit.connect(main_window.cleanup_on_exit) # Connect to signal for graceful shutdown
    
    main_window.show() # Show the main window
    sys.exit(app.exec_()) # Start the PyQt5 event loop
