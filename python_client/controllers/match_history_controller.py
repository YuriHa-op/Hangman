from .base_controller import BaseController
# from ..views.match_history_view import MatchHistoryView # Old Tkinter import

class MatchHistoryController(BaseController):
    def __init__(self, model, view):
        super().__init__(model, view)
        # self.view is now QtMatchHistoryView

    def on_show(self):
        """Called when the match history view is shown. Fetches and displays the list of matches."""
        super().on_show()
        self.load_match_history_list()

    def load_match_history_list(self):
        print("[MatchHistoryController] Attempting to load match history...")
        try:
            # Using get_match_history() by default. 
            # Consider if get_single_player_match_history() should also be checked or combined.
            username = self.model.get_username()
            if not username:
                print("[MatchHistoryController] No user logged in, cannot fetch history.")
                self.view.display_match_history("[]")
                self.view.show_error_message("No user logged in to fetch history for.")
                return

            print(f"[MatchHistoryController] Fetching match history for user: {username}")
            match_history_json = self.model.get_match_history() 
            print(f"[MatchHistoryController] Raw match history JSON from model: {match_history_json}")
            
            if match_history_json and match_history_json.strip() != "[]":
                self.view.display_match_history(match_history_json)
            else:
                # If multiplayer history is empty, try fetching single player history as a fallback
                print("[MatchHistoryController] Multiplayer match history is empty or not found. Trying single player history...")
                single_player_history_json = self.model.get_single_player_match_history()
                print(f"[MatchHistoryController] Raw single player match history JSON from model: {single_player_history_json}")
                if single_player_history_json:
                    self.view.display_match_history(single_player_history_json)
                else:
                    print("[MatchHistoryController] Both multiplayer and single player histories are empty or unavailable.")
                    self.view.display_match_history("[]") # Display empty

        except Exception as e:
            print(f"[MatchHistoryController] Error loading match history list: {e}")
            self.view.display_match_history("[]") # Send empty JSON array on error
            self.view.show_error_message(f"Failed to load match history: {e}")

    def fetch_match_details(self, game_id):
        """Fetches details for a specific game_id and tells the view to display them."""
        print(f"[MatchHistoryController] Fetching details for game_id: {game_id}")
        try:
            # This might need to know if it was a single player or multiplayer game_id
            # For now, trying generic get_match_details first.
            details_string = self.model.get_match_details(game_id)
            print(f"[MatchHistoryController] Raw details for game {game_id} (attempt 1): {details_string}")

            if not details_string or details_string.strip() == "{}" or details_string.strip() == "[]":
                print(f"[MatchHistoryController] No details from get_match_details. Trying get_single_player_match_details for game {game_id}...")
                # Try fetching single player details if generic one is empty
                details_string = self.model.get_single_player_match_details(game_id)
                print(f"[MatchHistoryController] Raw details for game {game_id} (attempt 2 - single player): {details_string}")

            if details_string:
                self.view.display_match_details(details_string)
            else:
                message = "No details found for this match or an error occurred."
                print(f"[MatchHistoryController] {message}")
                self.view.display_match_details(message)
        except Exception as e:
            error_message = f"Error fetching details for game_id {game_id}: {e}"
            print(f"[MatchHistoryController] {error_message}")
            self.view.display_match_details(error_message)

    # go_back_to_main_menu() is inherited from BaseController

    def load_match_history(self, mode='multiplayer'):
        history_view = self.view.frames.get("MatchHistory")
        if not history_view:
            print("MatchHistoryController: MatchHistoryView not found.")
            return
        try:
            # print(f"MatchHistoryController: Loading {mode} match history.")
            if mode == 'singleplayer':
                history_json = self.model.get_single_player_match_history()
            else: # Default to multiplayer
                history_json = self.model.get_match_history()
            
            if history_json is None: # Model might return None on error or if user not set
                print(f"MatchHistoryController: Received None for {mode} match history. Assuming empty.")
                history_json = "[]"

            history_view.display_match_history(history_json, mode)
        except Exception as e:
            print(f"Error loading {mode} match history: {e}")
            # Optionally show error in view status bar if available
            history_view.display_match_history("[]", mode) # Display empty on error

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
            # Optionally show error in view or popup
            history_view.show_details_popup('{ "error": "Could not load details." }') 