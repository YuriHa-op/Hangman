import json
from collections import defaultdict
from .base_controller import BaseController

class MultiplayerGameResultsController(BaseController):
    def __init__(self, model, view):
        super().__init__(model, view)
        
    def on_show(self):
        self.view.reset_view()
        game_id = self.model.get_last_game_id()
        print("[DEBUG] game_id:", game_id)
        if not game_id:
            print("No game ID found to show results.")
            self.view.update_scoreboard([], None)
            return
        try:
            print("[DEBUG] About to call get_ranked_players_for_game")
            ranked_players = self.model.get_ranked_players_for_game(game_id)
            print("[DEBUG] About to call get_match_details")
            details = self.model.get_match_details(game_id)
            print("[DEBUG] Real ranked_players:", ranked_players)
            print("[DEBUG] Real details:", details)
            if isinstance(details, str):
                try:
                    details = json.loads(details)
                except Exception as e:
                    print("[ERROR] Could not parse match details JSON for view:", e)
                    details = None
            self.view.update_scoreboard(ranked_players, details)
        except Exception as e:
            print("[ERROR] Exception in on_show with real data:", e)
            import traceback
            traceback.print_exc()

    def on_hide(self):
        self.model.set_last_game_id(None)
        self.view.reset_view()
        if self.model.get_username():
            self.model.end_game_session()
            self.model.cleanup_player_session()

    def back_to_main_menu(self):
        self.view.main_window.show_view("MainMenu") 