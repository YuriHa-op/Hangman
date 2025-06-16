from .base_controller import BaseController


class MatchHistoryController(BaseController):
    def __init__(self, model, view):
        super().__init__(model, view)
        self.active_mode = 'multiplayer' # Default to multiplayer
        # self.view is now QtMatchHistoryView

    def on_show(self):
        """Called when the view is shown. Fetches the default history type."""
        super().on_show()
        self.fetch_history(self.active_mode)

    def fetch_history(self, mode='multiplayer'):
        """Fetches and displays the match history list for the given mode."""
        self.active_mode = mode
        print(f"[MatchHistoryController] Fetching {mode} history...")
        try:
            username = self.model.get_username()
            if not username:
                self.view.show_error_message("No user logged in to fetch history for.")
                self.view.display_match_history("[]")
                return

            if mode == 'single_player':
                history_json = self.model.get_single_player_match_history()
            else: # Default to multiplayer
                history_json = self.model.get_match_history()
            
            if history_json:
                self.view.display_match_history(history_json)
            else:
                self.view.display_match_history("[]") # Display empty if None or empty

        except Exception as e:
            print(f"[MatchHistoryController] Error loading {mode} history: {e}")
            self.view.show_error_message(f"Failed to load {mode} match history: {e}")
            self.view.display_match_history("[]") # Display empty on error

    def fetch_match_details(self, game_id):
        """Fetches details for a specific game_id based on the currently active mode."""
        print(f"[MatchHistoryController] Fetching details for game_id: {game_id} (mode: {self.active_mode})")
        try:
            if self.active_mode == 'single_player':
                details_json = self.model.get_single_player_match_details(game_id)
            else:
                details_json = self.model.get_match_details(game_id)

            if details_json and details_json.strip() and details_json != "null":
                self.view.display_match_details(details_json)
            else:
                message = f"No details found for this {self.active_mode} match."
                print(f"[MatchHistoryController] {message}")
                self.view.show_error_message(message)
        except Exception as e:
            error_message = f"Error fetching details for game_id {game_id}: {e}"
            print(f"[MatchHistoryController] {error_message}")
            self.view.show_error_message(error_message)

    # go_back_to_main_menu() is inherited from BaseController

    def show_match_details(self, game_id, mode='multiplayer'):
        history_view = self.view.frames.get("MatchHistory")
        if not history_view:
            print("MatchHistoryController: MatchHistoryView not found.")
            return
        try:
            # print(f"MatchHistoryController: Showing details for game_id {game_id}, mode {mode}.")
            if mode == 'singleplayer':
                details_json = self.model.get_single_player_match_details(game_id)
            else:
                details_json = self.model.get_match_details(game_id)
            
            if details_json is None:
                print(f"MatchHistoryController: Received None for {mode} match details (game_id: {game_id}).")
                # Show a generic error or empty details in the popup
                history_view.show_details_popup('{ "error": "Details not found." }')
                return

            history_view.show_details_popup(details_json)
        except Exception as e:
            print(f"Error loading {mode} match details for game_id {game_id}: {e}")
            # show error in view or popup
            history_view.show_details_popup('{ "error": "Could not load details." }') 