from .base_controller import BaseController

class MatchHistoryController(BaseController):
    def __init__(self, app_view, model):
        super().__init__(app_view, model)

    # The MatchHistoryView's on_show method calls its own load_selected_history,
    # which then calls this controller's load_match_history method.
    # So, no specific on_show override is strictly needed here if that pattern is maintained.
    # However, for explicit clarity or if view logic changes, an on_show here could call view.load_selected_history().
    # def on_show(self):
    #     history_view = self.app_view.frames.get("MatchHistory")
    #     if history_view and hasattr(history_view, 'load_selected_history'):
    #         history_view.load_selected_history()

    def load_match_history(self, mode='multiplayer'):
        history_view = self.app_view.frames.get("MatchHistory")
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
        history_view = self.app_view.frames.get("MatchHistory")
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