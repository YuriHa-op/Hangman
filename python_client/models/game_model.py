import sys
import os
import time
import json
from omniORB import CORBA
import GameModule
import LoginModule  # Import LoginModule
import CosNaming

# Default ORB settings (change if your server uses different host/port)
ORB_HOST = os.environ.get('ORB_HOST', 'localhost')
ORB_PORT = os.environ.get('ORB_PORT', '900')

class GameModel:
    def __init__(self):
        self.orb = CORBA.ORB_init([
            '-ORBInitRef', f'NameService=corbaloc:iiop:{ORB_HOST}:{ORB_PORT}/NameService'
        ], CORBA.ORB_ID)
        self.naming_context = self._get_naming_context()
        
        self.game_service = self._resolve_service("GameService", GameModule.GameService)
        self.login_service = self._resolve_service("LoginService", LoginModule.LoginService)

        self.username = None
        self.session_id = None
        self.lobby_state = None
        self.game_state = None

    def _get_naming_context(self):
        try:
            obj = self.orb.resolve_initial_references('NameService')
            naming_context = obj._narrow(CosNaming.NamingContext)
            if naming_context is None:
                print('Failed to narrow the naming context')
                sys.exit(1)
            return naming_context
        except CORBA.ORB.InvalidName:
            print(f"Could not resolve NameService. Is the server at {ORB_HOST}:{ORB_PORT} running?")
            sys.exit(1)
        except CORBA.SystemException as e:
            print(f"CORBA system exception while getting naming context: {e}")
            sys.exit(1)

    def _resolve_service(self, service_name, service_type):
        if self.naming_context is None:
            print(f"Cannot resolve {service_name} because naming context is not available.")
            sys.exit(1)
        
        name = [CosNaming.NameComponent(service_name, '')]
        try:
            obj_ref = self.naming_context.resolve(name)
            service = obj_ref._narrow(service_type)
            if service is None:
                print(f'{service_name} reference is not valid')
                sys.exit(1)
            print(f"{service_name} resolved successfully.")
            return service
        except CosNaming.NamingContext.NotFound:
            print(f'Could not resolve {service_name}: Not found in the naming service.')
            sys.exit(1)
        except Exception as e:
            print(f'Could not resolve {service_name}: {e}')
            sys.exit(1)

    def login(self, username, password):
        try:
            response = self.login_service.loginWithSession(username, password)
            if response.success == LoginModule.BOOL_TRUE:
                self.username = username
                self.session_id = response.sessionId
                print(f"Login successful for {username}. Session ID: {self.session_id}")
                return True
            else:
                print(f"Login failed for {username}.")
                return False
        except LoginModule.AlreadyLoggedInException as e:
            # Re-raise the exception to be handled by the controller
            raise e
        except CORBA.SystemException as e:
            print(f"CORBA SystemException during login: {e}")
            return False

    def force_login(self, username, password):
        try:
            response = self.login_service.forceLoginWithSession(username, password)
            if response.success == LoginModule.BOOL_TRUE:
                self.username = username
                self.session_id = response.sessionId
                print(f"Force login successful for {username}. Session ID: {self.session_id}")
                return True
            else:
                print(f"Force login failed for {username}.")
                return False
        except CORBA.SystemException as e:
            print(f"CORBA SystemException during force login: {e}")
            return False

    def set_user_session(self, username, session_id):
        self.username = username
        self.session_id = session_id
        print(f"Session set for user {self.username}")

    def create_player(self, username, password):
        try:
            result = self.login_service.createPlayer(username, password)
            return result == LoginModule.BOOL_TRUE
        except CORBA.SystemException as e:
            print(f"CORBA SystemException during create_player: {e}")
            return False

    def logout(self):
        if self.username:
            try:
                self.login_service.logout(self.username)
                print(f"Logout signal sent for {self.username}.")
            except CORBA.SystemException as e:
                print(f"CORBA error during logout: {e}")
            finally:
                self.username = None
                self.session_id = None

    def keep_alive(self):
        if not self.username or not self.session_id:
            return False
        try:
            result = self.login_service.keepAlive(self.username, self.session_id)
            return result == LoginModule.BOOL_TRUE
        except CORBA.SystemException as e:
            print(f"Keep-alive failed: {e}")
            return False

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

    def leave_multiplayer_game(self):
        if self.username:
            try:
                self.game_service.leaveMultiplayerGame(self.username)
                print(f"Sent leave multiplayer game signal for {self.username}")
            except CORBA.SystemException as e:
                print(f"Error sending leave multiplayer game signal: {e}")

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