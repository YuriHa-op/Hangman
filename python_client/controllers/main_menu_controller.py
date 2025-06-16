from .base_controller import BaseController
import threading
import time

class MainMenuController(BaseController):
    def __init__(self, model, view):
        super().__init__(model, view)
        self.view = view
        # self.view is QtMainMenuView, which has self.main_window

    def on_show(self):
        """Called when the view is shown"""
        super().on_show()  # Call base class method to start session checking
        
        # Set welcome message with username
        username = self.model.get_username()
        if username:
            self.view.set_welcome_message(username)

    def start_single_player(self):
        # Start a single player game
        if hasattr(self.view, 'main_window'):
            self.view.main_window.show_view("SinglePlayer1v1Game")

    def go_to_multiplayer_queue(self):
        # Go to multiplayer queue
        if hasattr(self.view, 'main_window'):
            self.view.main_window.show_view("MultiplayerQueue")

    def show_leaderboard(self):
        # Show leaderboard
        if hasattr(self.view, 'main_window'):
            self.view.main_window.show_view("Leaderboard")

    def show_match_history(self):
        # Show match history
        if hasattr(self.view, 'main_window'):
            self.view.main_window.show_view("MatchHistory")

    # get_username() is inherited from BaseController for the welcome message in MainMenuView
    # show_frame() is inherited from BaseController for navigation buttons in MainMenuView