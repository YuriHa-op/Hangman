import tkinter as tk
import sys # For sys.exit in the fallback of handle_exit

# Import all specific view classes
from .login_view import LoginView
from .main_menu_view import MainMenuView
from .multiplayer_queue_view import MultiplayerQueueView
from .match_history_view import MatchHistoryView
from .multiplayer_game_view import MultiplayerGameView
from .single_player_game_view import SinglePlayerGameView
from .leaderboard_view import LeaderboardView

# Import all controller classes needed for setup
from controllers.login_controller import LoginController
from controllers.main_menu_controller import MainMenuController
from controllers.multiplayer_queue_controller import MultiplayerQueueController
from controllers.match_history_controller import MatchHistoryController
from controllers.multiplayer_game_controller import MultiplayerGameController
from controllers.single_player_game_controller import SinglePlayerGameController
from controllers.leaderboard_controller import LeaderboardController

class HangmanApp(tk.Tk):
    def __init__(self, model):
        super().__init__()
        self.title("Hangman - Python Client")
        self.geometry("800x600")
        self.frames = {}
        self.controllers = {} 
        self.current_frame_name = None
        self.model = model

    def setup_frames_and_controllers(self):
        """Initializes all frames and their specific controllers."""
        self._add_frame_with_controller(LoginView, "Login", LoginController(self, self.model))
        self._add_frame_with_controller(MainMenuView, "MainMenu", MainMenuController(self, self.model))
        self._add_frame_with_controller(MultiplayerQueueView, "MultiplayerQueue", MultiplayerQueueController(self, self.model))
        self._add_frame_with_controller(MatchHistoryView, "MatchHistory", MatchHistoryController(self, self.model))
        self._add_frame_with_controller(MultiplayerGameView, "MultiplayerGame", MultiplayerGameController(self, self.model))
        self._add_frame_with_controller(SinglePlayerGameView, "SinglePlayerGame", SinglePlayerGameController(self, self.model))
        self._add_frame_with_controller(LeaderboardView, "Leaderboard", LeaderboardController(self, self.model))

    def _add_frame_with_controller(self, FrameClass, frame_name, controller_instance):
        """Internal method to add a frame and associate it with its controller."""
        self.controllers[frame_name] = controller_instance
        frame = FrameClass(self, controller_instance) # Pass specific controller to view
        self.frames[frame_name] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        return frame

    def show_frame(self, frame_name):
        if self.current_frame_name and self.current_frame_name in self.controllers:
            old_controller = self.controllers.get(self.current_frame_name)
            if old_controller and hasattr(old_controller, 'on_hide'):
                old_controller.on_hide()
        
        frame = self.frames[frame_name]
        frame.tkraise()

        new_controller = self.controllers.get(frame_name)
        if new_controller and hasattr(new_controller, 'on_show'):
            new_controller.on_show()

        if hasattr(frame, "on_show"): # View's own on_show, if defined
            frame.on_show() 

        self.current_frame_name = frame_name
        
    def get_username(self):
        if self.model:
            return self.model.get_username()
        # Fallback in case model is not set or accessible, though it should be.
        # Active controller might be another source, but model is more direct.
        print("Warning: get_username called on HangmanApp when model was not directly available or returned None.")
        return "Player" # Default/fallback

    def run(self):
        self.mainloop()

    def handle_exit(self):
        """Handles application cleanup and exit."""
        print("HangmanApp: Initiating exit sequence.")
        if self.current_frame_name and self.current_frame_name in self.controllers:
            active_controller = self.controllers.get(self.current_frame_name)
            if active_controller and hasattr(active_controller, 'stop_polling'):
                print(f"HangmanApp: Stopping polling for {self.current_frame_name} controller.")
                active_controller.stop_polling()
        
        # Stop polling for ALL controllers, not just the active one, to be safe
        for controller_name, controller_instance in self.controllers.items():
            if controller_instance and hasattr(controller_instance, 'stop_polling') and controller_instance != active_controller:
                print(f"HangmanApp: Stopping polling for inactive controller {controller_name}.")
                controller_instance.stop_polling()
        
        if self.model and self.model.get_username():
            try:
                print("HangmanApp: Logging out user.")
                self.model.logout()
            except Exception as e:
                print(f"HangmanApp: Error during logout on exit: {e}")
        
        print("HangmanApp: Destroying main window.")
        self.destroy()
        print("HangmanApp: Exiting application.")
        sys.exit(0) 