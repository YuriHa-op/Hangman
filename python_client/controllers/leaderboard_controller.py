from .base_controller import BaseController

class LeaderboardController(BaseController):
    def __init__(self, app_view, model):
        super().__init__(app_view, model)

    def on_show(self):
        """Called when the LeaderboardView is shown. Loads leaderboard data."""
        # print("LeaderboardController: on_show called")
        self.load_leaderboard()

    def load_leaderboard(self):
        leaderboard_view = self.app_view.frames.get("Leaderboard")
        if not leaderboard_view:
            print("LeaderboardController: LeaderboardView not found.")
            return
        try:
            # print("LeaderboardController: Loading leaderboard entries.")
            entries = self.model.get_leaderboard_entries()
            if entries is None: # Model might return None on error
                print("LeaderboardController: Received None for leaderboard entries. Assuming empty.")
                entries = []
            leaderboard_view.display_leaderboard(entries)
        except Exception as e:
            print(f"Error loading leaderboard: {e}")
            # Optionally show error in view (e.g., display empty or error message)
            leaderboard_view.display_leaderboard([]) # Display empty on error 