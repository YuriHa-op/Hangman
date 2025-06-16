import sys
import os
import time
import json
from omniORB import CORBA
import GameModule
import LoginModule
import CosNaming

# Default ORB settings (change if your server uses different host/port)
ORB_HOST = os.environ.get('ORB_HOST', 'localhost')
ORB_PORT = os.environ.get('ORB_PORT', '900')

class GameModel:
    def __init__(self):
        self.orb = CORBA.ORB_init([
            '-ORBInitRef', f'NameService=corbaloc:iiop:{ORB_HOST}:{ORB_PORT}/NameService'
        ], CORBA.ORB_ID)
        self.game_service = self._get_service("GameService", GameModule.GameService)
        self.login_service = self._get_service("LoginService", LoginModule.LoginService)
        self.username = None
        self.session_id = None  # Store the session ID
        self.lobby_state = None
        self.game_state = None
        self.last_game_id = None

    def _get_service(self, service_name, helper_class):
        try:
            obj = self.orb.resolve_initial_references('NameService')
            naming_context = obj._narrow(CosNaming.NamingContext)
            if naming_context is None:
                print(f'Failed to narrow the naming context for {service_name}')
                sys.exit(1)
            
            name = [CosNaming.NameComponent(service_name, '')]
            obj_ref = naming_context.resolve(name)
            service = obj_ref._narrow(helper_class)
            
            if service is None:
                print(f'{service_name} reference is not valid')
                sys.exit(1)
            
            print(f"Successfully connected to {service_name}")
            return service
        except Exception as e:
            print(f'Could not resolve {service_name}: {e}')
            sys.exit(1)

    def login(self, username, password):
        try:
            # Try to use the enhanced loginWithSession method if available
            try:
                response = self.login_service.loginWithSession(username, password)
                if response.success == LoginModule.BOOL_TRUE:
                    self.username = username
                    self.session_id = response.sessionId
                    print(f"Logged in with session ID: {self.session_id}")
                    return True
                return False
            except (AttributeError, CORBA.BAD_OPERATION):
                # Fallback to regular login if the enhanced method is not available
                print("Server doesn't support session-based login, falling back to regular login")
                result = self.login_service.login(username, password)
                if result == LoginModule.BOOL_TRUE:
                    self.username = username
                    return True
                return False
        except LoginModule.AlreadyLoggedInException as e:
            raise e  # Re-raise the exception
        except CORBA.SystemException as e:
            print(f"CORBA SystemException during login: {e}")
            return False

    def force_login(self, username, password):
        """Force login when account is already logged in elsewhere"""
        try:
            # Try to use the enhanced loginWithSession method
            response = self.login_service.loginWithSession(username, password)
            if response.success == LoginModule.BOOL_TRUE:
                self.username = username
                self.session_id = response.sessionId
                print(f"Force logged in with session ID: {self.session_id}")
                return True
            return False
        except Exception as e:
            print(f"Error during force login: {e}")
            return False

    def validate_session(self):
        """Validate if the current session is still valid"""
        if not self.username:
            print("No username to validate session")
            return False
            
        try:
            # Try the straightforward way first - use checkSessionValid
            try:
                print(f"Validating session for {self.username} using checkSessionValid")
                is_valid = self.login_service.checkSessionValid(self.username)
                valid_result = is_valid == LoginModule.BOOL_TRUE
                print(f"Session validation result for {self.username}: {valid_result}")
                return valid_result
            except (AttributeError, CORBA.BAD_OPERATION) as e:
                print(f"checkSessionValid not available: {e}")
                # Fall back to validateSession if we have a session ID
                if self.session_id:
                    try:
                        print(f"Validating session for {self.username} using validateSession with session ID {self.session_id}")
                        is_valid = self.login_service.validateSession(self.username, self.session_id)
                        valid_result = is_valid == LoginModule.BOOL_TRUE
                        print(f"Session validation result for {self.username}: {valid_result}")
                        return valid_result
                    except (AttributeError, CORBA.BAD_OPERATION) as e:
                        print(f"validateSession not available: {e}")
                        # Method not available, fall back to basic check
                        pass
                else:
                    print(f"No session ID available for {self.username}")
                
                # Last resort - try to get player stats - this will throw an exception if session is invalid
                try:
                    print(f"Trying fallback validation for {self.username} using getPlayerWins")
                    self.game_service.getPlayerWins(self.username)
                    print(f"Fallback validation successful for {self.username}")
                    return True
                except Exception as e:
                    print(f"Fallback validation failed for {self.username}: {e}")
                    return False
        except Exception as e:
            print(f"Error validating session for {self.username}: {e}")
            return False

    def keep_alive(self):
        """Check if session is still valid by passing our current session ID to the server."""
        if not self.username or not self.session_id:
            return False

        try:
            # Prefer validateSession(username, sessionId) if available – it detects replacement sessions.
            try:
                result = self.login_service.validateSession(self.username, self.session_id)
                return result == LoginModule.BOOL_TRUE
            except (AttributeError, CORBA.BAD_OPERATION):
                # Fallback to checkSessionValid(username) – less strict but better than nothing.
                result = self.login_service.checkSessionValid(self.username)
                return result == LoginModule.BOOL_TRUE
        except Exception as e:
            print(f"Error during session validation for {self.username}: {e}")
            return False

    def create_player(self, username, password):
        try:
            result = self.login_service.createPlayer(username, password) # Ensure this matches the IDL method name
            return result == LoginModule.BOOL_TRUE
        except CORBA.SystemException as e:
            print(f"CORBA SystemException during create_player: {e}")
            return False

    def logout(self, skip_server_logout=False):
        if self.username and not skip_server_logout:
            try:
                self.login_service.logout(self.username)
            except Exception as e:
                print(f"Error during server logout for {self.username}: {e}")
        
        # Always clear local credentials
        self.username = None
        self.session_id = None
        print("Local session cleared.")

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
            return False
        try:
            result_corba_bool = self.game_service.sendGuess(self.username, guess)
            
            # Revert to direct comparison with GameModule.BOOL_TRUE
            # It's the most explicit way if BOOL_TRUE is the defined constant for true.
            is_correct_guess = (result_corba_bool == GameModule.BOOL_TRUE)
            
            # --- DEBUG PRINT ---
            print(f"[DEBUG GameModel.send_guess] Letter: {guess}, Server Raw: {result_corba_bool} (Type: {type(result_corba_bool)}), " \
                  f"GameModule.BOOL_TRUE: {GameModule.BOOL_TRUE} (Type: {type(GameModule.BOOL_TRUE)}), " \
                  f"Comparison Result (is_correct_guess): {is_correct_guess}")
            # --- END DEBUG PRINT ---
            
            return is_correct_guess
        except Exception as e:
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
        try:
            # Convert the guess to lowercase before sending to the server
            result = self.game_service.sendMultiplayerGuess(self.username, guess.lower())
            is_correct_guess = (result == GameModule.BOOL_TRUE)
            return is_correct_guess
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False

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
                return True
            except Exception as e:
                print(f"Error leaving multiplayer game: {e}")
                return False
        return False

    # Utility to get current username
    def get_username(self):
        return self.username
        
    # Get the current session ID
    def get_session_id(self):
        return self.session_id

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

    def get_mp_game_id(self):
        game_data = self.get_mp_game_state_data()
        return game_data.get("gameId", None)

    def get_mp_player_finish_times(self):
        game_data = self.get_mp_game_state_data()
        return game_data.get("allPlayerFinishTimes", {})

    def get_mp_player_finish_times(self):
        game_data = self.get_mp_game_state_data()
        return game_data.get("allPlayerFinishTimes", {})

    def set_last_game_id(self, game_id):
        self.last_game_id = game_id

    def get_last_game_id(self):
        return self.last_game_id

    def get_ranked_players_for_game(self, game_id):
        """Get a list of ranked players for a specific game"""
        details = self.get_match_details(game_id)
        if not details:
            return []
        if isinstance(details, str):
            try:
                details = json.loads(details)
            except Exception as e:
                print("[ERROR] Could not parse match details JSON:", e)
                return []
        # Now details is a dict
        player_scores = {player: 0 for player in details.get('players', [])}
        for round_info in details.get('rounds', []):
            winner = round_info.get('winner')
            if winner:
                player_scores[winner] = player_scores.get(winner, 0) + 1
        ranked = sorted(player_scores.items(), key=lambda x: x[1], reverse=True)
        return [
            {"rank": i+1, "name": name, "score": score}
            for i, (name, score) in enumerate(ranked)
        ]
            
    def force_win_count_update(self, username=None):
        """Force an update of the win count for a player by directly calling the server.
        If username is None, uses the current logged-in player."""
        if not username:
            username = self.username
            
        if not username:
            return False
            
        try:
            # can't directly update the win count through the GameService interface
            # Instead, we'll trigger the win processing logic by calling startMultiplayerNextRound
            # This should cause the server to process any pending wins
            print(f"[GameModel] Forcing win processing for {username}")
            
            # First, check current win count for logging purposes
            try:
                current_wins = self.game_service.getPlayerWins(username)
                print(f"[GameModel] Current win count for {username}: {current_wins}")
            except Exception as e:
                print(f"[GameModel] Error getting player wins: {e}")
            
            # Call startMultiplayerNextRound to trigger win processing
            try:
                result = self.game_service.startMultiplayerNextRound(username)
                print(f"[GameModel] Start next round result: {result}")
            except Exception as e:
                print(f"[GameModel] Error starting next round: {e}")
            
            # Check if win count was updated
            try:
                new_wins = self.game_service.getPlayerWins(username)
                print(f"[GameModel] New win count for {username}: {new_wins}")
                return True
            except Exception as e:
                print(f"[GameModel] Error getting updated player wins: {e}")
                return False
                
        except Exception as e:
            print(f"[GameModel] Error in force_win_count_update: {e}")
            return False 