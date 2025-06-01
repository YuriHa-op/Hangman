import sys
import os
import time
import json
from omniORB import CORBA
import GameModule
import CosNaming

# Default ORB settings (change if your server uses different host/port)
ORB_HOST = os.environ.get('ORB_HOST', 'localhost')
ORB_PORT = os.environ.get('ORB_PORT', '900')

class GameModel:
    def __init__(self):
        self.game_service = self._get_game_service()
        self.username = None
        self.lobby_state = None
        self.game_state = None

    def _get_game_service(self):
        orb = CORBA.ORB_init([
            '-ORBInitRef', f'NameService=corbaloc:iiop:{ORB_HOST}:{ORB_PORT}/NameService'
        ], CORBA.ORB_ID)
        obj = orb.resolve_initial_references('NameService')
        naming_context = obj._narrow(CosNaming.NamingContext)
        if naming_context is None:
            print('Failed to narrow the naming context')
            # Consider raising an exception here instead of sys.exit
            sys.exit(1)
        name = [CosNaming.NameComponent('GameService', '')]
        try:
            obj_ref = naming_context.resolve(name)
            game_service = obj_ref._narrow(GameModule.GameService)
            if game_service is None:
                print('GameService reference is not valid')
                # Consider raising an exception here
                sys.exit(1)
            return game_service
        except Exception as e:
            print('Could not resolve GameService:', e)
            # Consider raising an exception here
            sys.exit(1)

    def login(self, username, password):
        try:
            # Assuming GameModule.Bool maps to an enum with members BOOL_TRUE, BOOL_FALSE
            # or integer constants where BOOL_TRUE might be 1.
            # For omniidl, it's typically GameModule.BOOL_TRUE for enums.
            result = self.game_service.login(username, password)
            if result == GameModule.BOOL_TRUE: # Compare with GameModule.BOOL_TRUE
                self.username = username
                return True
            return False
        except GameModule.AlreadyLoggedInException as e:
            # It's better to let the controller handle UI-specific error messages
            raise e # Re-raise the exception
        # It's good practice to also handle potential CORBA system exceptions
        except CORBA.SystemException as e:
            print(f"CORBA SystemException during login: {e}")
            return False # Or raise a custom exception

    def create_player(self, username, password):
        try:
            result = self.game_service.createPlayer(username, password) # createPlayer returns Bool
            return result == GameModule.BOOL_TRUE # Compare with GameModule.BOOL_TRUE
        except CORBA.SystemException as e:
            print(f"CORBA SystemException during create_player: {e}")
            return False # Or raise a custom exception

    def logout(self):
        if self.username:
            self.game_service.logout(self.username)
            self.username = None

    def start_game(self):
        if not self.username:
            return None # Or raise an error
        return self.game_service.startGame(self.username)

    def get_masked_word(self):
        if not self.username:
            return None
        return self.game_service.getMaskedWord(self.username)

    def get_waiting_time(self):
        return self.game_service.getWaitingTime()

    def end_game_session(self):
        if self.username:
            self.game_service.endGameSession(self.username)

    def cleanup_player_session(self):
        if self.username:
            self.game_service.cleanupPlayerSession(self.username)
    
    def player_ready_for_first_round(self):
        if self.username:
            try:
                self.game_service.playerReadyForFirstRound(self.username)
            except Exception as e:
                print(f"Error signaling player ready for first round (Python client): {e}")

    def get_game_state(self):
        if not self.username:
            return None
        # Assuming getGameState returns a structure, not JSON
        self.game_state = self.game_service.getGameState(self.username)
        return self.game_state

    def send_guess(self, guess):
        if not self.username:
            # print("[DEBUG] send_guess: No username, returning False")
            return False
        try:
            # print(f"[DEBUG SP CLIENT] Attempting to send guess: username='{self.username}', letter='{guess}' (type: {type(guess)})")
            result_corba_bool = self.game_service.sendGuess(self.username, guess)
            # print(f"[DEBUG SP CLIENT] Raw response from server sendGuess: {result_corba_bool} (type: {type(result_corba_bool)})")
            
            bool_true_val = GameModule.BOOL_TRUE
            # print(f"[DEBUG SP CLIENT] GameModule.BOOL_TRUE is: {bool_true_val} (type: {type(bool_true_val)})")
            
            is_correct_guess = (result_corba_bool == bool_true_val)
            # print(f"[DEBUG SP CLIENT] Comparison (result_corba_bool == GameModule.BOOL_TRUE): {is_correct_guess}")
            
            return is_correct_guess
        except Exception as e:
            # print(f"[ERROR SP CLIENT] Exception in send_guess: {e}")
            import traceback
            traceback.print_exc() 
            return False 

    def finish_round(self, remaining_time, guessed_word):
        if self.username:
            # Convert Python boolean to GameModule.Bool
            guessed_word_bool = GameModule.BOOL_TRUE if guessed_word else GameModule.BOOL_FALSE
            self.game_service.finishRound(self.username, remaining_time, guessed_word_bool)

    def start_new_round(self):
        if not self.username:
            return False
        # Convert GameModule.Bool to Python boolean
        result = self.game_service.startNewRound(self.username)
        return result == GameModule.BOOL_TRUE

    def view_leaderboard(self):
        return self.game_service.viewLeaderboard()

    def get_leaderboard_entries(self):
        try:
            return self.game_service.getLeaderboardEntries()
        except AttributeError: # Fallback if method doesn't exist on server
            text_leaderboard = self.game_service.viewLeaderboard()
            entries = []
            for line in text_leaderboard.splitlines():
                if ':' in line:
                    user, wins_str = line.split(':', 1)
                    # Create a simple object or dict to mimic LeaderboardEntry
                    entry = type('LeaderboardEntry', (object,), {'username': user.strip(), 'wins': int(wins_str.strip().replace(' wins', ''))})()
                    entries.append(entry)
            return entries


    def get_match_history(self):
        if not self.username:
            return "[]" # Return empty JSON array string
        return self.game_service.getMatchHistory(self.username)

    def get_match_details(self, game_id):
        return self.game_service.getMatchDetails(game_id)

    # --- Single Player Match History Methods ---
    def get_single_player_match_history(self):
        if not self.username:
            return "[]" # Return empty JSON array string
        # Assuming the CORBA GameService object will have this method after IDL update and recompilation
        return self.game_service.getSinglePlayerMatchHistory(self.username)

    def get_single_player_match_details(self, game_id):
        # Assuming the CORBA GameService object will have this method
        return self.game_service.getSinglePlayerMatchDetails(game_id)

    # --- Multiplayer specific methods ---
    def start_multiplayer_game(self):
        if self.username:
            self.game_service.startMultiplayerGame(self.username)

    def get_multiplayer_lobby_state(self):
        if not self.username:
            return "{}" # Return empty JSON object string
        state_json = self.game_service.getMultiplayerLobbyState(self.username)
        self.lobby_state = json.loads(state_json) # Store parsed state
        return self.lobby_state # Return parsed state directly

    def send_multiplayer_guess(self, guess):
        if not self.username:
            return False
        # Convert GameModule.Bool to Python boolean
        result = self.game_service.sendMultiplayerGuess(self.username, guess)
        return result == GameModule.BOOL_TRUE

    def start_multiplayer_next_round(self):
        if self.username:
            # Convert GameModule.Bool to Python boolean
            result = self.game_service.startMultiplayerNextRound(self.username)
            return result == GameModule.BOOL_TRUE
        return False

    # Utility to get current username
    def get_username(self):
        return self.username

    # Potentially add methods to store/retrieve specific parts of game_state or lobby_state
    # to avoid repeated parsing or direct access from controller/view.
    def get_lobby_players(self):
        return self.lobby_state.get("players", []) if self.lobby_state else []

    def get_lobby_max_players(self):
        return self.lobby_state.get("maxPlayers", 8) if self.lobby_state else 8

    def get_lobby_creation_time(self):
        return self.lobby_state.get("creationTime", int(time.time() * 1000)) if self.lobby_state else int(time.time() * 1000)

    def get_lobby_queue_time_seconds(self):
        return self.lobby_state.get("queueTimeSeconds", 30) if self.lobby_state else 30
    
    def get_lobby_status_state(self):
         return self.lobby_state.get("state", "UNKNOWN") if self.lobby_state else "UNKNOWN"

    def get_mp_game_state_data(self):
        return self.lobby_state.get("gameState", {}) if self.lobby_state else {}

    def get_mp_masked_words(self):
        game_data = self.get_mp_game_state_data()
        return game_data.get("maskedWords", {})

    def get_mp_all_current_words(self):
        game_data = self.get_mp_game_state_data()
        return game_data.get("allCurrentWords", {})

    def get_mp_player_guesses_map(self):
        game_data = self.get_mp_game_state_data()
        return game_data.get("playerGuessesMap", {})
    
    def get_mp_incorrect_guesses_map(self):
        game_data = self.get_mp_game_state_data()
        return game_data.get("incorrectGuessesMap", {})

    def get_mp_remaining_time(self):
        game_data = self.get_mp_game_state_data()
        return game_data.get("remainingTime", 0)

    def get_mp_current_round(self):
        game_data = self.get_mp_game_state_data()
        return game_data.get("currentRound", 0)

    def get_mp_scores(self):
        game_data = self.get_mp_game_state_data()
        return game_data.get("scores", {})
    
    def is_mp_round_in_progress(self):
        game_data = self.get_mp_game_state_data()
        return game_data.get("roundInProgress", True)

    def get_mp_round_winner(self):
        game_data = self.get_mp_game_state_data()
        return game_data.get("roundWinner", "")

    def get_mp_game_winner(self):
        game_data = self.get_mp_game_state_data()
        return game_data.get("gameWinner", "")

    def get_mp_session_result(self):
        game_data = self.get_mp_game_state_data()
        return game_data.get("sessionResult", "ONGOING")

    def get_mp_player_finish_times(self):
        game_data = self.get_mp_game_state_data()
        return game_data.get("allPlayerFinishTimes", {}) 