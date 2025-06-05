from .base_controller import BaseController
# from ..views.leaderboard_view import LeaderboardView # Old Tkinter import

class LeaderboardController(BaseController):
    def __init__(self, model, view):
        super().__init__(model, view)
        # self.view is now QtLeaderboardView

    def on_show(self):
        """Called when the leaderboard view is shown. Fetches and displays data."""
        super().on_show() # Call base class on_show if it has any logic
        self.load_leaderboard_data()

    def load_leaderboard_data(self):
        try:
            # Assuming get_leaderboard_entries returns a list of objects 
            # with 'username' and 'wins' attributes, as per GameModel.
            entries = self.model.get_leaderboard_entries()
            if entries is not None:
                self.view.display_leaderboard(entries)
            else:
                self.view.show_error("Could not retrieve leaderboard data.")
        except Exception as e:
            print(f"Error loading leaderboard data: {e}")
            self.view.show_error(f"Error: {e}")

    # go_back_to_main_menu() is inherited from BaseController
    # def go_back_to_main_menu(self):
    #     self.view.main_window.show_view("MainMenu") 