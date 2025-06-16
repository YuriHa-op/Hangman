from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PyQt5.QtCore import QSize, pyqtSlot, QTimer
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
        self.views = {}
        self.controllers = {}
        self.current_view_name = None
        self.username = None # Will be set after login
        
        # Get absolute path to this script
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Set window properties
        self.setWindowTitle("Hangman Game")
        self.resize(900, 600)
        self.setMinimumSize(900, 600)
        
        # Initialize stacked widget to hold all views
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)
        
        # Clean up any lingering visual effects from previous runs
        self._setup_cleanup_method()
        self.cleanup_visual_effects()
        
        self._create_views_and_controllers()
        
        # Show login view by default
        self.show_view("Login")

    def _setup_cleanup_method(self):
        """Setup the cleanup method first so it can be called during init"""
        # This is a minimal version that will be replaced by the full version
        # once the whole class is initialized
        def minimal_cleanup():
            try:
                effects_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'views', 'effects')
                for effect_file in ['confetti_effect.py', 'round_transition_effect.py']:
                    try:
                        effect_path = os.path.join(effects_dir, effect_file)
                        if os.path.exists(effect_path):
                            import importlib.util
                            spec = importlib.util.spec_from_file_location(effect_file[:-3], effect_path)
                            effect_module = importlib.util.module_from_spec(spec)
                            spec.loader.exec_module(effect_module)
                            for name in dir(effect_module):
                                if 'Effect' in name and hasattr(getattr(effect_module, name), 'cleanup_all_instances'):
                                    getattr(effect_module, name).cleanup_all_instances()
                    except Exception:
                        pass
            except Exception:
                pass
                
        # Assign the minimal cleanup to the instance
        self.cleanup_visual_effects = minimal_cleanup

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

    def cleanup_visual_effects(self):
        """Clean up any lingering visual effects in a centralized way"""
        try:
            # Get direct access to the effect modules using absolute paths
            effects_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'views', 'effects')
            
            # Dynamic import of the confetti effect
            confetti_path = os.path.join(effects_dir, 'confetti_effect.py')
            if os.path.exists(confetti_path):
                import importlib.util
                spec = importlib.util.spec_from_file_location("confetti_effect", confetti_path)
                confetti_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(confetti_module)
                if hasattr(confetti_module, 'ConfettiEffect') and hasattr(confetti_module.ConfettiEffect, 'cleanup_all_instances'):
                    confetti_module.ConfettiEffect.cleanup_all_instances()
                    
            # Dynamic import of the round transition effect
            transition_path = os.path.join(effects_dir, 'round_transition_effect.py')
            if os.path.exists(transition_path):
                spec = importlib.util.spec_from_file_location("round_transition_effect", transition_path)
                transition_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(transition_module)
                if hasattr(transition_module, 'RoundTransitionEffect') and hasattr(transition_module.RoundTransitionEffect, 'cleanup_all_instances'):
                    transition_module.RoundTransitionEffect.cleanup_all_instances()
                    
        except Exception as e:
            print(f"Warning: could not clean up visual effects: {e}")
            import traceback
            traceback.print_exc()

    def show_view(self, view_name):
        """Show the specified view and handle view transitions"""
        if view_name not in self.views:
            print(f"View '{view_name}' not found")
            return
            
        # Get the current and new views
        old_view_name = self.current_view_name
        new_view = self.views[view_name]
        
        # Clean up any lingering visual effects before switching views
        self.cleanup_visual_effects()
        
        # If we're showing the login view, reset any session invalidation flag
        if view_name == 'Login':
            try:
                from controllers.base_controller import BaseController
                if hasattr(BaseController, '_session_invalidation_in_progress'):
                    BaseController._session_invalidation_in_progress = False
                    print("Reset session invalidation flag when showing Login view")
            except Exception as e:
                print(f"Error resetting session invalidation flag: {e}")
        
        # Call on_hide for the current view's controller
        if old_view_name and old_view_name in self.controllers:
            try:
                self.controllers[old_view_name].on_hide()
            except Exception as e:
                print(f"Error calling on_hide for {old_view_name}: {e}")
        
        # Update current view
        self.current_view_name = view_name
        
        # Show the new view
        self.stacked_widget.setCurrentWidget(new_view)
        
        # Handle window size based on view
        try:
            # Preserve the window size for non-login views
            if view_name != "Login":
                # Remember the current size for non-login views
                if hasattr(self, '_last_window_size') and self._last_window_size:
                    # Restore the last window size
                    self.resize(self._last_window_size)
                    # Allow resizing
                    self.setMinimumSize(0, 0)
                    self.setMaximumSize(16777215, 16777215)
                else:
                    # Set a default size if no previous size
                    self.resize(800, 600)
            else:
                # For login view, store current size if not login
                if old_view_name and old_view_name != "Login":
                    self._last_window_size = self.size()
                
                # Set fixed size for login view
                login_size = new_view.sizeHint()
                if login_size.isValid():
                    self.setFixedSize(login_size)
                else:
                    # Fallback size for login
                    self.setFixedSize(450, 550)
        except Exception as e:
            print(f"Error handling window size: {e}")
            import traceback
            traceback.print_exc()
        
        # Call on_show for the new view's controller
        if view_name in self.controllers:
            try:
                self.controllers[view_name].on_show()
            except Exception as e:
                print(f"Error calling on_show for {view_name}: {e}")
                
        # Update window title
        self.setWindowTitle(f"Hangman Game - {view_name}")
        
        print(f"Switched to view: {view_name}")

    def logout_user_and_show_login(self, skip_server_logout=False):
        """Log out current user (optionally skip server-side logout) and show login view"""
        print("Logging out user and showing login view")
        
        try:
            # Get the current controller
            current_controller = None
            try:
                current_controller = self.controllers[self.current_view_name]
            except Exception as e:
                print(f"Error getting current controller: {e}")
            
            # End any active game
            if current_controller and hasattr(current_controller.model, 'end_game_session'):
                try:
                    print("Ending active game session")
                    current_controller.model.end_game_session()
                except Exception as e:
                    print(f"Error ending game session: {e}")
            
            # Only call server logout if not skipping
            if (not skip_server_logout) and current_controller and hasattr(current_controller.model, 'logout'):
                try:
                    print("Logging out from server")
                    current_controller.model.logout()
                except Exception as e:
                    print(f"Error logging out: {e}")
            
            # If skip_server_logout is True, clear local credentials so further session checks won't fire endlessly
            elif skip_server_logout and current_controller and hasattr(current_controller.model, 'username'):
                try:
                    print("Clearing local credentials without server logout")
                    current_controller.model.username = None
                    current_controller.model.session_id = None
                except Exception as e:
                    print(f"Error clearing credentials: {e}")
            
            # Show the login view
            self.show_view('Login')
            
            # Reset the session invalidation flag if it exists in the BaseController class
            try:
                from controllers.base_controller import BaseController
                if hasattr(BaseController, '_session_invalidation_in_progress'):
                    BaseController._session_invalidation_in_progress = False
                    print("Session invalidation flag reset")
            except Exception as e:
                print(f"Error resetting session invalidation flag: {e}")
        
        except Exception as e:
            print(f"Error in logout_user_and_show_login: {e}")
            import traceback
            traceback.print_exc()
            
            # Last resort: just show login view
            self.show_view('Login')

    @pyqtSlot()
    def handle_session_invalidated(self):
        """Handle session invalidation by showing a dialog and redirecting to login"""
        print("Session invalidated! Handling in MainWindow")
        
        try:
            # Force the application to process events
            QApplication.processEvents()
            
            # Get the current view
            current_view_name = self.current_view_name
            print(f"Current view in MainWindow: {current_view_name}")
            
            # Flag to track if dialog was shown
            dialog_shown = False
            
            # Try to show dialog from current view
            if current_view_name and current_view_name in self.views:
                current_view = self.views[current_view_name]
                if hasattr(current_view, 'show_session_invalidated_dialog'):
                    print(f"Showing session invalidated dialog from {current_view_name} view")
                    try:
                        current_view.show_session_invalidated_dialog("Your session has been invalidated")
                        dialog_shown = True
                        print(f"Dialog shown from {current_view_name} view")
                    except Exception as e:
                        print(f"Error showing dialog from current view: {e}")
                        import traceback
                        traceback.print_exc()
            
            # If dialog wasn't shown from current view, try login view
            if not dialog_shown and 'Login' in self.views:
                print("Trying to show dialog from Login view")
                try:
                    self.views['Login'].show_session_invalidated_dialog("Your session has been invalidated")
                    dialog_shown = True
                    print("Dialog shown from Login view")
                except Exception as e:
                    print(f"Error showing dialog from Login view: {e}")
                    import traceback
                    traceback.print_exc()
            
            # If still no dialog shown, create one directly
            if not dialog_shown:
                print("Creating session invalidated dialog directly")
                try:
                    from views.qt_login_view import SessionInvalidatedDialog
                    dialog = SessionInvalidatedDialog(self, "Your session has been invalidated")
                    dialog.exec_()
                    print("Direct dialog shown and closed")
                except Exception as e:
                    print(f"Error showing direct dialog: {e}")
                    import traceback
                    traceback.print_exc()
                    
                    # Last resort: QMessageBox
                    try:
                        print("Showing QMessageBox as last resort")
                        from PyQt5.QtWidgets import QMessageBox
                        msg = QMessageBox(self)
                        msg.setIcon(QMessageBox.Critical)
                        msg.setText("Session Invalidated")
                        msg.setInformativeText("Your session has been invalidated. You will be logged out.")
                        msg.setWindowTitle("Session Ended")
                        msg.setStandardButtons(QMessageBox.Ok)
                        msg.exec_()
                        print("QMessageBox shown and closed")
                    except Exception as e2:
                        print(f"Error showing QMessageBox: {e2}")
                        traceback.print_exc()
            
            # Force events to process again
            QApplication.processEvents()
            
            # Schedule logout after a short delay
            QTimer.singleShot(1000, lambda: self.logout_user_and_show_login(skip_server_logout=True))
            print("Scheduled logout after dialog")
            
        except Exception as e:
            print(f"Error in handle_session_invalidated: {e}")
            import traceback
            traceback.print_exc()
            
            # Fallback: just logout
            self.logout_user_and_show_login()

    def cleanup_on_exit(self):
        print("Application is about to quit. Performing cleanup...")
        # Clean up visual effects
        self.cleanup_visual_effects()
        
        # Clean up dialogs - use reflection to find and clean up all active dialogs
        try:
            # Force cleanup any dialogs in both single and multiplayer views
            for view_name in ["SinglePlayer1v1Game", "MultiplayerGame"]:
                if view_name in self.views:
                    view = self.views[view_name]
                    # Look for dialog objects and close them
                    for attr_name in dir(view):
                        if "dialog" in attr_name.lower() and not attr_name.startswith("__"):
                            try:
                                dialog = getattr(view, attr_name)
                                if dialog and hasattr(dialog, "accept"):
                                    print(f"Closing dialog {attr_name} in {view_name}")
                                    dialog.accept()  # Close any lingering dialogs
                                    setattr(view, attr_name, None)  # Clear the reference
                            except:
                                pass
        except Exception as e:
            print(f"Warning: Error cleaning up dialogs: {e}")
        
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
        # Clean up visual effects first
        self.cleanup_visual_effects()
        # Then do regular cleanup
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
