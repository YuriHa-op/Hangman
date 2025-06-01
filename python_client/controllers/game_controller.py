import tkinter as tk # For type hinting if needed, not for creating widgets here
import threading
import time
import sys
import json # For parsing match history/details if model returns JSON strings
from models.game_model import GameModel # Adjusted import
from views.main_view import LoginView, MainMenuView, MultiplayerQueueView, MatchHistoryView, MultiplayerGameView, SinglePlayerGameView, LeaderboardView # Adjusted import
import GameModule # For GameModule.AlreadyLoggedInException

class GameController:
    def __init__(self, app_view, game_model):
        self.app_view = app_view  # This is the HangmanApp (main Tk window)
        self.model = game_model
        self.current_view = None
        self.polling_active = False
        self.spectating_player = None # For multiplayer spectate
        self.last_keyboard_state_mp = None # For multiplayer keyboard updates
        self.sp_polling_thread = None
        self.mp_queue_polling_thread = None
        self.mp_game_polling_thread = None
        self.sp_attempted_letters = set() # Track attempted letters in SP
        self.sp_current_word = "" # Track current word in SP for keyboard coloring
        self.afk_dialog_active = False
        self.afk_dialog_cooldown_until = 0
        self.AFK_DIALOG_COOLDOWN_SECONDS = 20 # Cooldown period for AFK dialog

        # New attributes for 4-second pre-AFK delay
        self.afk_pre_check_delay_active = False
        self.afk_pre_check_timer_id = None
        self.round_at_afk_check_start = -1

        # Flags for single-player game state management
        self.game_session_cleaned_up = False
        self.sp_client_timeout_sent_for_round = {} # Tracks if client sent timeout for a round_num
        self._last_processed_server_round_for_word_clear = -1 # Helper for sp_current_word logic
        self.current_sp_server_round_processed_for_next_attempt = -1 # Tracks if start_new_round called for an ended server round

        # For multiplayer: track if this client initiated a delayed next round attempt
        # after its player finished the current round. Keyed by round number.
        self.my_player_finished_sent_next_round_for_round = {} 
        self.delayed_next_round_attempt_timer_id = None
        self.round_for_which_delayed_attempt_is_scheduled = -1 # Tracks the round for the active delayed timer

        # Timer for delayed next round start in MP
        self.mp_next_round_timer_id = None
        self.mp_next_round_scheduled_for_round = -1

    def setup_frames(self):
        # Initialize all frames and add them to the app_view
        self.app_view.add_frame(LoginView, "Login")
        self.app_view.add_frame(MainMenuView, "MainMenu")
        self.app_view.add_frame(MultiplayerQueueView, "MultiplayerQueue")
        self.app_view.add_frame(MatchHistoryView, "MatchHistory")
        self.app_view.add_frame(MultiplayerGameView, "MultiplayerGame")
        self.app_view.add_frame(SinglePlayerGameView, "SinglePlayerGame")
        self.app_view.add_frame(LeaderboardView, "Leaderboard")

    def start(self):
        self.setup_frames()
        self.show_frame("Login") # Start with the login view
        self.app_view.run() # Start the Tkinter main loop

    def show_frame(self, frame_name):
        # Stop any active polling before switching frames
        self.stop_all_polling()

        # If the current view was MultiplayerQueueView, ensure its dialogs are closed
        if isinstance(self.current_view, MultiplayerQueueView):
            self.current_view.close_no_match_found_dialog()
            # If MultiplayerQueueView had other specific dialogs, close them here too

        self.current_view = self.app_view.frames[frame_name]
        # No longer need to pass mode to MatchHistoryView here
        self.app_view.show_frame(frame_name)

    def get_username(self):
        return self.model.get_username()

    # --- LoginView Handlers ---
    def handle_login(self, username, password):
        login_view = self.app_view.frames.get("Login")
        if not username or not password:
            login_view.set_status("Username and password cannot be empty.")
            return
        try:
            if self.model.login(username, password):
                login_view.clear_entries()
                login_view.set_status("") # Clear status
                self.show_frame("MainMenu")
            else:
                login_view.set_status("Login failed. Check your credentials.")
        except GameModule.AlreadyLoggedInException as e:
            login_view.set_status(f"Error: {e.message}")
        except Exception as e:
            login_view.set_status(f"Login error: {e}")

    def handle_create_account(self, username, password):
        login_view = self.app_view.frames.get("Login")
        if not username or not password:
            login_view.set_status("Username and password cannot be empty for account creation.")
            return
        try:
            if self.model.create_player(username, password):
                login_view.set_status("Account created! You can now log in.", color="green")
                login_view.clear_entries()
            else:
                login_view.set_status("Account creation failed. Username may already exist.")
        except Exception as e:
            login_view.set_status(f"Creation error: {e}")

    def handle_exit(self):
        self.stop_all_polling()
        # Perform any cleanup if necessary via model
        if self.model.get_username():
            self.model.logout() # Ensure logout on exit
        self.app_view.destroy() # Close the Tkinter window
        sys.exit(0)

    # --- MainMenuView Handlers ---
    def handle_logout(self):
        self.model.logout()
        self.show_frame("Login")

    # --- MultiplayerQueueView Handlers ---
    def start_multiplayer_queue_poll(self):
        self.stop_all_polling() # Ensure other polls are stopped
        self.polling_active = True
        self.model.start_multiplayer_game() # Join/start lobby in model
        self.mp_queue_polling_thread = threading.Thread(target=self._poll_mp_lobby_state, daemon=True)
        self.mp_queue_polling_thread.start()

    def _poll_mp_lobby_state(self):
        queue_view = self.app_view.frames.get("MultiplayerQueue")
        while self.polling_active and self.current_view == queue_view:
            try:
                # Model now returns parsed dict from get_multiplayer_lobby_state
                lobby_state_data = self.model.get_multiplayer_lobby_state()
                
                players = self.model.get_lobby_players()
                max_players = self.model.get_lobby_max_players()
                creation_time_ms = self.model.get_lobby_creation_time()
                queue_time_s = self.model.get_lobby_queue_time_seconds()
                lobby_status = self.model.get_lobby_status_state()

                now_ms = int(time.time() * 1000)
                seconds_left = max(0, queue_time_s - int((now_ms - creation_time_ms) / 1000))
                
                # Update view (ensure calls are thread-safe if view methods aren't)
                # Tkinter updates should ideally be scheduled via master.after or queue
                self.app_view.after(0, lambda: queue_view.update_queue_display(
                    f"Time left: {seconds_left}",
                    f"{len(players)}/{max_players} players"
                ))

                if lobby_status == "STARTED" and seconds_left == 0:
                    self.polling_active = False # Stop polling
                    self.app_view.after(0, lambda: queue_view.show_match_found_dialog(players, self._mp_queue_countdown_finished))
                    break 
                elif lobby_status == "NOMATCH" or (lobby_status == "WAITING" and seconds_left == 0) :
                    self.polling_active = False # Stop polling
                    self.app_view.after(0, queue_view.show_no_match_found_dialog)
                    # View's dialog OK button will call handle_no_match_found_dialog_ok
                    break

            except Exception as e:
                # print(f"Error polling multiplayer lobby state: {e}")
                # Optionally update view with error status
                self.polling_active = False # Stop polling on error
                self.app_view.after(0, self.show_frame, "MainMenu") # Go back to main menu on error
                break
            time.sleep(0.25) # Polling interval (new)
        if not self.polling_active:
             self.model.cleanup_player_session() # Clean up if polling stopped prematurely

    def _mp_queue_countdown_finished(self):
        # This is called by the view after its countdown dialog finishes
        self.show_frame("MultiplayerGame")

    def handle_no_match_found_dialog_ok(self):
        # Called when user clicks OK on the "No Match Found" dialog in MultiplayerQueueView
        self.model.cleanup_player_session()
        self.show_frame("MainMenu")

    def cancel_multiplayer_queue(self):
        self.stop_all_polling()
        self.model.cleanup_player_session() # Tell model to clean up server-side if needed
        
        # Explicitly close the dialog if it's open
        queue_view = self.app_view.frames.get("MultiplayerQueue")
        if queue_view:
            queue_view.close_no_match_found_dialog()

        self.show_frame("MainMenu")

    # --- MatchHistoryView Handlers ---
    def load_match_history(self, mode='multiplayer'): # Default to multiplayer for compatibility
        history_view = self.app_view.frames.get("MatchHistory")
        try:
            if mode == 'singleplayer':
                history_json = self.model.get_single_player_match_history()
            else: # Default to multiplayer
                history_json = self.model.get_match_history() # Existing multiplayer history
            history_view.display_match_history(history_json, mode)
        except Exception as e:
            print(f"Error loading {mode} match history: {e}")
            # Optionally show error in view

    def show_match_details(self, game_id, mode='multiplayer'):
        history_view = self.app_view.frames.get("MatchHistory")
        try:
            if mode == 'singleplayer':
                details_json = self.model.get_single_player_match_details(game_id)
            else:
                details_json = self.model.get_match_details(game_id)
            history_view.show_details_popup(details_json)
        except Exception as e:
            print(f"Error loading {mode} match details: {e}")
            # Optionally show error in view or popup

    # --- MultiplayerGameView Handlers ---
    def start_multiplayer_game_poll(self):
        self.stop_all_polling()
        self.polling_active = True
        self.spectating_player = None 
        self.last_keyboard_state_mp = None 
        
        self.mp_game_polling_thread = threading.Thread(target=self._poll_mp_game_state, daemon=True)
        self.mp_game_polling_thread.start()

    def _poll_mp_game_state(self):
        mp_game_view = self.app_view.frames.get("MultiplayerGame")
        my_username = self.model.get_username()
        cleaned_up_session = False

        while self.polling_active and self.current_view == mp_game_view:
            try:
                previous_mp_game_was_ongoing = getattr(self, '_mp_game_was_ongoing', False)
                _ = self.model.get_multiplayer_lobby_state() 

                # --- Fetch all relevant server states --- 
                lobby_status_current = self.model.get_lobby_status_state()
                current_round_server = self.model.get_mp_current_round()
                round_in_progress_server = self.model.is_mp_round_in_progress()
                game_winner_server = self.model.get_mp_game_winner()
                session_result_server = self.model.get_mp_session_result()
                round_winner_server = self.model.get_mp_round_winner()
                
                masked_words = self.model.get_mp_masked_words()
                incorrect_guesses_map = self.model.get_mp_incorrect_guesses_map()
                all_current_words = self.model.get_mp_all_current_words() 
                player_guesses_map = self.model.get_mp_player_guesses_map() 
                scores = self.model.get_mp_scores()
                remaining_time = self.model.get_mp_remaining_time() 
                player_finish_times_map = self.model.get_mp_player_finish_times() # Get the new map
                players = self.model.get_lobby_players() # Fetch players after getting lobby state

                # Update _mp_game_was_ongoing for the current poll iteration AFTER fetching all current states
                self._mp_game_was_ongoing = (lobby_status_current == "STARTED" or session_result_server == "ONGOING")

                # --- Initial Server Cleanup / NOMATCH checks (early exit) --- 
                if previous_mp_game_was_ongoing and lobby_status_current == "NOMATCH":
                    # Game cleaned up by server detection (e.g., server timed out lobby or game)
                    self.polling_active = False
                    if self.afk_pre_check_timer_id: self.app_view.after_cancel(self.afk_pre_check_timer_id); self.afk_pre_check_timer_id = None
                    
                    self.app_view.after(0, mp_game_view.close_afk_dialog)
                    self.app_view.after(50, mp_game_view.close_last_chance_dialog) # Small delay for last_chance close
                    
                    self.app_view.after(200, lambda: mp_game_view.show_game_cleaned_up_dialog(on_ok_callback=lambda: self.show_frame("MainMenu")))
                    if not cleaned_up_session:
                        try: self.model.cleanup_player_session(); 
                        except Exception: pass; 
                        cleaned_up_session = True
                    break # Exit polling loop

                if not players and previous_mp_game_was_ongoing: 
                    # Game cleaned up due to no players detected (e.g., all players left)
                    self.polling_active = False
                    if self.afk_pre_check_timer_id: self.app_view.after_cancel(self.afk_pre_check_timer_id); self.afk_pre_check_timer_id = None

                    self.app_view.after(0, mp_game_view.close_afk_dialog)
                    self.app_view.after(50, mp_game_view.close_last_chance_dialog) # Small delay for last_chance close
                    
                    self.app_view.after(200, lambda: mp_game_view.show_game_cleaned_up_dialog(on_ok_callback=lambda: self.show_frame("MainMenu")))
                    if not cleaned_up_session:
                        try: self.model.cleanup_player_session(); 
                        except Exception: pass; 
                        cleaned_up_session = True
                    break # Exit polling loop

                word_display = masked_words.get(self.spectating_player if self.spectating_player else my_username, "_ _ _")
                timer_display = f"Time left: {remaining_time}s"
                round_display = f"Round: {current_round_server + 1}"
                status_display = ""

                my_masked_word = masked_words.get(my_username, "")
                my_incorrect_guesses = incorrect_guesses_map.get(my_username, 0)
                my_player_is_done_this_round = (my_incorrect_guesses >= 5) or \
                                               (my_masked_word and "_" not in my_masked_word)

                # --- Handle cancellation of AFK pre_check_timer if game ended or new round truly started ---
                if self.afk_pre_check_timer_id: # Check if timer exists
                    is_game_over_for_cancel = game_winner_server or (session_result_server not in ["ONGOING", None, ""])
                    is_new_round_started_for_cancel = round_in_progress_server and \
                                                    current_round_server != self.round_at_afk_check_start
                    if is_game_over_for_cancel or is_new_round_started_for_cancel:
                        self.app_view.after_cancel(self.afk_pre_check_timer_id)
                        self.afk_pre_check_timer_id = None
                        self.afk_pre_check_delay_active = False # Reset this flag too

                # --- Spectator logic (pov_username determination) --- 
                if self.spectating_player and self.spectating_player not in players: self.spectating_player = None 
                pov_username = self.spectating_player if self.spectating_player else my_username
                if self.spectating_player:
                    spectated_masked = masked_words.get(self.spectating_player, "")
                    spectated_incorrect = incorrect_guesses_map.get(self.spectating_player, 0)
                    if (spectated_incorrect >= 5) or (spectated_masked and "_" not in spectated_masked) or not round_in_progress_server:
                        self.spectating_player = None; pov_username = my_username 
                
                # --- UI Interaction flags (can_truly_guess, interaction_over_for_pov, etc.) --- 
                pov_is_done_guessing = (incorrect_guesses_map.get(pov_username, 0) >= 5) or (masked_words.get(pov_username, "") and "_" not in masked_words.get(pov_username, ""))
                can_truly_guess = (pov_username == my_username) and not self.spectating_player and round_in_progress_server and not game_winner_server and not my_player_is_done_this_round
                interaction_over_for_pov = bool(game_winner_server) or (not round_in_progress_server and pov_username == my_username) or (pov_username == my_username and my_player_is_done_this_round) or (self.spectating_player and pov_is_done_guessing)
                is_user_done_guessing_for_spectate_button = my_player_is_done_this_round or not round_in_progress_server


                # --- Main Game Logic Flow (Game Over / Round In Progress / Round Over) ---
                if game_winner_server or (session_result_server not in ["ONGOING", None, ""]):
                    # Game Over Logic
                    status_display = f"{game_winner_server} won the game." if game_winner_server else f"Game Over: {session_result_server}"
                    if game_winner_server == my_username: status_display = "🎉 You won the game! 🎉"
                    self.polling_active = False 
                    if self.afk_pre_check_timer_id: self.app_view.after_cancel(self.afk_pre_check_timer_id); self.afk_pre_check_timer_id = None
                    self.app_view.after(0, mp_game_view.close_afk_dialog); self.app_view.after(0, mp_game_view.close_last_chance_dialog)
                    if not cleaned_up_session: 
                        try: self.model.end_game_session(); self.model.cleanup_player_session(); 
                        except Exception: pass; 
                        cleaned_up_session = True
                
                elif round_in_progress_server: 
                    # Round is ONGOING according to server
                    status_display = "Guess the word!"
                    if my_player_is_done_this_round: status_display = "Waiting for other players..."
                    if self.spectating_player: status_display = f"Spectating {self.spectating_player}"

                    # If round is in progress, cancel any AFK mechanisms
                    if self.afk_dialog_active: self.app_view.after(0, mp_game_view.close_afk_dialog); self.afk_dialog_active = False
                    self.app_view.after(0, mp_game_view.close_last_chance_dialog)
                    if self.afk_pre_check_delay_active:
                        if self.afk_pre_check_timer_id: self.app_view.after_cancel(self.afk_pre_check_timer_id); self.afk_pre_check_timer_id = None
                        self.afk_pre_check_delay_active = False
                else: # Server says round is NOT in progress (and game is not over yet)
                    if round_winner_server:
                        # Round ended WITH a winner
                        status_display = f"{round_winner_server} won this round."
                        if round_winner_server == my_username: status_display = "You won this round!"
                        
                        if self.afk_dialog_active: self.app_view.after(0, mp_game_view.close_afk_dialog); self.afk_dialog_active = False
                        self.app_view.after(0, mp_game_view.close_last_chance_dialog)
                        if self.afk_pre_check_delay_active: 
                            if self.afk_pre_check_timer_id: self.app_view.after_cancel(self.afk_pre_check_timer_id); self.afk_pre_check_timer_id = None
                            self.afk_pre_check_delay_active = False
                        
                        if session_result_server == "ONGOING": 
                            self._schedule_next_round_attempt_mp(current_round_server)
                    else: # No round winner, server says round is over
                        status_display = "No one won this round."
                        current_time_poll = time.strftime("%H:%M:%S", time.localtime())
                        # print(f"[{current_time_poll}] GAME CTRL ({my_username}): Poller sees round {current_round_server} ended with no winner.")
                        
                        if session_result_server == "ONGOING":
                            # print(f"[{current_time_poll}] GAME CTRL ({my_username}): Player Finish Times Map from server: {player_finish_times_map}")

                            if player_finish_times_map: 
                                # print(f"[{current_time_poll}] GAME CTRL ({my_username}): player_finish_times_map is NOT empty. Attempting next round via poller.")
                                self._schedule_next_round_attempt_mp(current_round_server)
                            else:
                                # print(f"[{current_time_poll}] GAME CTRL ({my_username}): player_finish_times_map IS EMPTY. Letting AFK logic run.")
                                pass

                        # AFK logic follows directly.
                        conditions_for_afk_initiation = (
                            not game_winner_server and session_result_server == "ONGOING" and
                            not self.afk_dialog_active and not self.afk_pre_check_delay_active and 
                            time.time() > self.afk_dialog_cooldown_until
                        )
                        if conditions_for_afk_initiation:
                            self.round_at_afk_check_start = current_round_server 
                            self.afk_pre_check_delay_active = True
                            if self.afk_pre_check_timer_id: self.app_view.after_cancel(self.afk_pre_check_timer_id) # Cancel previous if any
                            self.afk_pre_check_timer_id = self.app_view.after(4000, self._trigger_first_afk_dialog_if_conditions_met)

                # --- UI Update Scheduling & Keyboard State --- 
                self.app_view.after(0, lambda pov_u=pov_username, p_guesses=dict(player_guesses_map), act_words=dict(all_current_words), c_truly_g=can_truly_guess, interact_o=interaction_over_for_pov, wd=word_display, td=timer_display, rd=round_display, sd=status_display, pl=list(players), sc=dict(scores), iudgfsb=is_user_done_guessing_for_spectate_button: 
                    mp_game_view.update_display(wd, td, rd, sd, pl, sc, pov_u, p_guesses, act_words, c_truly_g, iudgfsb, interact_o)
                )
                current_keyboard_state_tuple = (pov_username, frozenset(player_guesses_map.get(pov_username, [])), all_current_words.get(pov_username, ""), can_truly_guess, interaction_over_for_pov, current_round_server)
                if current_keyboard_state_tuple != self.last_keyboard_state_mp:
                     self.app_view.after(0, lambda pov_u=pov_username, p_guesses=dict(player_guesses_map), act_words=dict(all_current_words), c_truly_g=can_truly_guess, interact_o=interaction_over_for_pov: 
                        mp_game_view.update_keyboard(pov_u, p_guesses, act_words, c_truly_g, interact_o))
                     self.last_keyboard_state_mp = current_keyboard_state_tuple
                
                if not self.polling_active: # Check polling_active again before sleep, if it was set to False inside loop
                    break

            except Exception as e:
                # Error handling
                # print(f"Error in _poll_mp_game_state: {e}") # Optional: log detailed error
                # import traceback; traceback.print_exc() # Optional: for detailed stack trace
                self.polling_active = False
                if mp_game_view: # Ensure view exists
                    self.app_view.after(0, lambda: mp_game_view.set_status("Error in game. Returning to menu.", "red"))
                    self.app_view.after(2000, lambda: self.show_frame("MainMenu")) 
                break # Exit polling loop on error
            time.sleep(0.25)

        # --- Polling Loop Cleanup --- 
        # Ensure all timers are cancelled
        if self.afk_pre_check_timer_id: self.app_view.after_cancel(self.afk_pre_check_timer_id); self.afk_pre_check_timer_id = None
        self.afk_pre_check_delay_active = False

        mp_game_view = self.app_view.frames.get("MultiplayerGame")
        if mp_game_view: # Ensure view still exists before trying to close its dialogs
            self.app_view.after(0, mp_game_view.close_afk_dialog)
            self.app_view.after(0, mp_game_view.close_last_chance_dialog)
            self.app_view.after(0, mp_game_view.close_game_cleaned_up_dialog) # If this new dialog exists
        self.mp_game_polling_thread = None 

    def handle_multiplayer_guess(self, letter):
        if self.spectating_player: return 
        if not self.polling_active: return 
        
        try:
            self.model.send_multiplayer_guess(letter.lower())
            # Immediate UI feedback for the pressed key can be added here if desired,
            # but the authoritative state comes from the next poll.
            # For example, disable the button optimistically:
            # mp_game_view = self.app_view.frames.get("MultiplayerGame")
            # if mp_game_view:
            #     mp_game_view.feedback_guess_mp_optimistic(letter) 
        except Exception as e:
            mp_game_view = self.app_view.frames.get("MultiplayerGame")
            if mp_game_view:
                self.app_view.after(0, lambda: mp_game_view.set_status(f"Error sending guess: {e}", "red"))

    def set_spectate_player(self, player_username):
        self.spectating_player = player_username
        # The poll will pick this up and change the POV.
        # Force an immediate mini-refresh of keyboard etc. might be good but poll should handle it.
        self.last_keyboard_state_mp = None # Force keyboard refresh on next poll for new POV

    def handle_back_to_menu_from_mp_game(self):
        self.stop_all_polling()
        try:
            self.model.end_game_session() # Attempt to clean up game if it was ongoing
            self.model.cleanup_player_session()
        except Exception as e:
            # print(f"Error during back_to_menu cleanup from MP game: {e}")
            pass
        self.show_frame("MainMenu")

    # --- SinglePlayerGameView Handlers ---
    def start_single_player_game(self):
        self.stop_all_polling()
        self.polling_active = True
        sp_game_view = self.app_view.frames.get("SinglePlayerGame")
        sp_game_view.set_status("Starting game...")
        
        # Reset SP game state flags for the controller
        self.game_session_cleaned_up = False
        self.sp_client_timeout_sent_for_round.clear()
        self._last_processed_server_round_for_word_clear = -1
        self.current_sp_server_round_processed_for_next_attempt = -1

        # Reset keyboard and display for a new game
        self.sp_attempted_letters.clear()
        self.sp_current_word = ""
        # Initial display needs to match the full signature, including player_wins and current_round_num
        self.app_view.after(0, lambda: sp_game_view.update_display(
            "_ _ _", "Time: --", "Incorrect: 0/5", 
            "", # status_text
            0,  # player_wins (initially 0)
            0,  # current_round_num (initially 0)
            self.sp_attempted_letters, self.sp_current_word, 
            False, # round_over
            False  # game_over
        ))
        
        self.sp_polling_thread = threading.Thread(target=self._initialize_and_poll_sp_game, daemon=True)
        self.sp_polling_thread.start()

    def _sp_match_dialog_finished_and_signal_ready(self):
        """Called after the SP match found dialog countdown finishes."""
        if self.model.get_username(): # Ensure user is still valid
            self.model.player_ready_for_first_round()
        # Now start the actual game state polling loop
        self.sp_polling_thread = threading.Thread(target=self._poll_sp_game_state_loop, daemon=True)
        self.sp_polling_thread.start()

    def _initialize_and_poll_sp_game(self):
        sp_game_view = self.app_view.frames.get("SinglePlayerGame")
        try:
            masked_word_init = self.model.start_game() # startGame on model
            # Fetch initial round time for SP mode
            try:
                self.sp_full_round_time = self.model.game_service.getRoundTime()
            except Exception as e:
                print(f"Error getting sp_full_round_time: {e}, defaulting to 15")
                self.sp_full_round_time = 15 # Default if call fails

            # After starting game, try to get the full game state to know the word for keyboard coloring
            initial_state = self.model.get_game_state()
            if initial_state and hasattr(initial_state, 'actualWord') and initial_state.actualWord:
                 self.sp_current_word = initial_state.actualWord.upper()
            elif initial_state:
                 # Fallback if actualWord is not available, keyboard coloring for correct letters might be delayed
                 # We can try to infer from maskedWord if it's fully revealed later
                 pass 

            # --- NEW: Get opponent name for dialog ---
            opponent = getattr(initial_state, 'opponentUsername', None)
            if not opponent:
                opponent = "Opponent"

            if masked_word_init == 'WAITING_FOR_MATCH':
                self.app_view.after(0, lambda: sp_game_view.set_status("Waiting for match allocation..."))
                waiting_time = self.model.get_waiting_time()
                start_wait = time.time()
                while time.time() - start_wait < waiting_time:
                    if not self.polling_active: return # Check if cancelled
                    time.sleep(0.5)
                    masked_word_init = self.model.get_masked_word()
                    if masked_word_init != 'WAITING_FOR_MATCH' and masked_word_init:
                        break
                if masked_word_init == 'WAITING_FOR_MATCH' or not masked_word_init:
                    self.app_view.after(0, lambda: sp_game_view.set_status("No match found. Try again later."))
                    self.polling_active = False
                    self.model.end_game_session() # Clean up if no match
                    self.model.cleanup_player_session()
                    self.sp_attempted_letters.clear() # Clear attempts
                    self.sp_current_word = ""
                    return
            
            # Match found, show countdown dialog via view.
            # The countdown_callback will now be _sp_match_dialog_finished_and_signal_ready
            self.app_view.after(0, lambda: sp_game_view.show_match_found_countdown(self._sp_match_dialog_finished_and_signal_ready, opponent))

        except Exception as e:
            # print(f"Error starting single player game: {e}")
            self.app_view.after(0, lambda: sp_game_view.set_status(f"Error: {e}"))
            self.polling_active = False
            self.sp_attempted_letters.clear()
            self.sp_current_word = ""

    def _poll_sp_game_state_loop(self):
        sp_game_view = self.app_view.frames.get("SinglePlayerGame")
        # self.game_session_cleaned_up is managed by start_single_player_game

        while self.polling_active and self.current_view == sp_game_view:
            try:
                state = self.model.get_game_state()
                if not state:
                    self.app_view.after(0, lambda: sp_game_view.set_status("Error fetching game state.", "red"))
                    self.polling_active = False
                    break

                server_current_round = state.currentRound
                status_text = "" # Default status

                # Determine timer text and color
                timer_display_text = ""
                timer_color = "black" # Default color for timer text

                is_pre_first_round_awaiting_server_start = (
                    state.maskedWord != "WAITING_FOR_MATCH" and
                    state.roundOver == GameModule.BOOL_FALSE and
                    state.gameOver == GameModule.BOOL_FALSE and
                    hasattr(self, 'sp_full_round_time') and # Ensure sp_full_round_time is set
                    state.remainingTime == self.sp_full_round_time
                )

                if is_pre_first_round_awaiting_server_start:
                    timer_display_text = "" # Blank during pre-first-round dialog
                elif state.remainingTime <= 0:
                    timer_display_text = "Time left: 0s"
                    timer_color = "red"
                else:
                    timer_display_text = f"Time left: {state.remainingTime}s"
                    if state.remainingTime <= 5:
                        timer_color = "red"
                    elif state.remainingTime <= 15:
                        timer_color = "yellow"
                    # Else, default black is fine

                # 1. Client-side timeout detection and notification to server
                if state.remainingTime <= 0 and \
                   state.roundOver == GameModule.BOOL_FALSE and \
                   not self.sp_client_timeout_sent_for_round.get(server_current_round, False):
                    
                    self.model.finish_round(0, False) # Tell server client timed out this round
                    self.sp_client_timeout_sent_for_round[server_current_round] = True
                    # Next poll cycle will reflect the server's updated state due to this finish_round call.
                    # We don't immediately change UI; rely on next poll.

                # 2. Process state: round over, game over, or ongoing
                if state.roundOver == GameModule.BOOL_TRUE:
                    status_text = self._determine_sp_round_status_text(state)

                    if state.gameOver == GameModule.BOOL_FALSE and state.sessionResult == "ONGOING":
                        # Check if we haven't tried to start the next round for this *ended* server_current_round yet
                        if server_current_round > self.current_sp_server_round_processed_for_next_attempt:
                            if self.polling_active:
                                new_round_started_successfully = self.model.start_new_round()
                                self.current_sp_server_round_processed_for_next_attempt = server_current_round
                                
                                if new_round_started_successfully:
                                    status_text = "Starting next round..." # Indicate attempt
                                    # Attempted letters and actual word will be updated when the new round's state is polled.
                                    # Specifically, sp_attempted_letters.clear() and sp_current_word update
                                    # will happen in the 'else' (round ongoing) block of the next poll cycle
                                    # when server_current_round has actually incremented.
                                else:
                                    # Failed to trigger start_new_round, status_text remains round over message.
                                    pass 
                    
                    # Update UI based on current 'state' (which is roundOver)
                    self.app_view.after(0, lambda s=state, st=status_text, tdt=timer_display_text, tc=timer_color: sp_game_view.update_display(
                        s.maskedWord, tdt, f"Incorrect guesses: {s.incorrectGuesses}/5", st, 
                        s.playerWins, 
                        s.currentRound, # Pass current round number
                        self.sp_attempted_letters, self.sp_current_word, True, s.gameOver == GameModule.BOOL_TRUE,
                        timer_color=tc
                    ))

                elif state.gameOver == GameModule.BOOL_TRUE or (state.sessionResult and state.sessionResult != "ONGOING"):
                    if not self.game_session_cleaned_up:
                        self.model.end_game_session()
                        self.model.cleanup_player_session()
                        self.game_session_cleaned_up = True
                    
                    status_text = self._determine_sp_game_over_status_text(state)
                    self.polling_active = False # Stop polling
                    
                    # Final UI update before showing dialog
                    self.app_view.after(0, lambda s=state, st=status_text, tdt=timer_display_text, tc=timer_color: sp_game_view.update_display(
                        s.maskedWord, tdt, f"Incorrect guesses: {s.incorrectGuesses}/5", st, 
                        s.playerWins, 
                        s.currentRound, # Pass current round number
                        self.sp_attempted_letters, self.sp_current_word, True, True, # roundOver=True, gameOver=True
                        timer_color=tc
                    ))

                    # Show game over dialog
                    dialog_result_text = "You Won!" if state.sessionResult == "WIN" else "You Lost."
                    if state.sessionResult == "DRAW": # Example, if you add DRAW state
                        dialog_result_text = "It's a Draw!"
                    elif state.sessionResult != "WIN" and state.sessionResult != "LOSE": # Other results
                        dialog_result_text = f"Game Over: {state.sessionResult}"

                    self.app_view.after(0, lambda drt=dialog_result_text: 
                        sp_game_view.show_sp_game_over_dialog(drt, lambda: self.show_frame("MainMenu"))
                    )
                    break # Exit polling loop

                else: # Round is ongoing, game is not over
                    # Update current word and clear attempts if it's a new round number compared to last processed
                    if hasattr(state, 'actualWord') and state.actualWord and self.sp_current_word != state.actualWord.upper():
                        self.sp_current_word = state.actualWord.upper()
                    
                    if server_current_round != self._last_processed_server_round_for_word_clear:
                         self.sp_attempted_letters.clear()
                         # Reset client timeout flag for this newly started round
                         self.sp_client_timeout_sent_for_round.pop(server_current_round, None) 
                         self._last_processed_server_round_for_word_clear = server_current_round

                    status_text = "" # Or e.g. "Your turn!" or based on whose turn if applicable
                    self.app_view.after(0, lambda s=state, st=status_text, tdt=timer_display_text, tc=timer_color: sp_game_view.update_display(
                        s.maskedWord, tdt, f"Incorrect guesses: {s.incorrectGuesses}/5", st, 
                        s.playerWins, 
                        s.currentRound, # Pass current round number
                        self.sp_attempted_letters, self.sp_current_word, False, False, # roundOver=False, gameOver=False
                        timer_color=tc
                    ))
                
                if not self.polling_active: break

            except Exception as e:
                # print(f"Error polling single player game state: {e}")
                # import traceback
                # traceback.print_exc()
                self.app_view.after(0, lambda: sp_game_view.set_status("Error in game. Returning to menu.", "red"))
                self.polling_active = False
                self.app_view.after(2000, lambda: self.show_frame("MainMenu"))
                break
            time.sleep(0.25) # Polling interval (new)

    def _determine_sp_round_status_text(self, state: GameModule.GameStateDTO) -> str:
        if state.roundWinner:
            if state.roundWinner == self.model.get_username():
                return "You won this round!"
            else:
                return f"{state.roundWinner} won this round."
        else:
            # If round is over but no winner (e.g. both timed out, or server determined draw)
            return "Round over. No winner for this round."

    def _determine_sp_game_over_status_text(self, state: GameModule.GameStateDTO) -> str:
        if state.sessionResult == "WIN":
            return "🎉 You won the game! 🎉"
        elif state.sessionResult == "LOSE":
            return "You lost the game."
        elif state.sessionResult and state.sessionResult != "ONGOING": # Other game end reasons
            return f"Game over. Result: {state.sessionResult}"
        else: # Should not happen if called when game is over
            return "Game has ended."

    def handle_single_player_guess(self, letter):
        if not self.polling_active: return
        sp_game_view = self.app_view.frames.get("SinglePlayerGame")
        try:
            is_correct = self.model.send_guess(letter.lower())
            self.sp_attempted_letters.add(letter.lower()) # Add to attempted letters
            # View gives immediate feedback on button color and disables it.
            self.app_view.after(0, lambda: sp_game_view.feedback_guess(letter, is_correct))
            # The full state update (masked word, score) will come from the next poll cycle.
        except Exception as e:
            # print(f"Error sending SP guess: {e}")
            self.app_view.after(0, lambda: sp_game_view.set_status(f"Error guessing: {e}", "red"))

    def handle_back_to_menu_from_sp_game(self):
        self.stop_all_polling()
        try:
            self.model.end_game_session()
            self.model.cleanup_player_session()
            self.sp_attempted_letters.clear() # Clear on back to menu
            self.sp_current_word = ""
        except Exception as e:
            # print(f"Error during back_to_menu cleanup from SP game: {e}")
            pass
        self.show_frame("MainMenu")

    # --- LeaderboardView Handlers ---
    def load_leaderboard(self):
        leaderboard_view = self.app_view.frames.get("Leaderboard")
        try:
            entries = self.model.get_leaderboard_entries() # Model handles parsing logic
            leaderboard_view.display_leaderboard(entries)
        except Exception as e:
            # print(f"Error loading leaderboard: {e}")
            # Optionally show error in view
            pass

    # --- General polling management ---
    def stop_all_polling(self):
        self.polling_active = False # Signal all polling loops to stop
        # Wait for threads to finish if they are joinable and running
        # This requires threads to check self.polling_active frequently
        if self.sp_polling_thread and self.sp_polling_thread.is_alive():
            # self.sp_polling_thread.join(timeout=1.5) # Wait briefly
            pass # Daemon threads will exit when main program exits or if loop condition met
        if self.mp_queue_polling_thread and self.mp_queue_polling_thread.is_alive():
            # self.mp_queue_polling_thread.join(timeout=1.5)
            pass
        if self.mp_game_polling_thread and self.mp_game_polling_thread.is_alive():
            # self.mp_game_polling_thread.join(timeout=1.5)
            pass
        self.sp_polling_thread = None
        self.mp_queue_polling_thread = None
        self.mp_game_polling_thread = None 

        if hasattr(self, 'mp_next_round_timer_id') and self.mp_next_round_timer_id:
            self.app_view.after_cancel(self.mp_next_round_timer_id)
            self.mp_next_round_timer_id = None

    def _handle_afk_yes(self):
        # print("AFK Dialog: Yes clicked.")
        self.afk_dialog_active = False # Dialog will be closed by its own mechanism
        # View should close the dialog immediately on button click before this callback.
        mp_game_view = self.app_view.frames.get("MultiplayerGame")
        if mp_game_view and mp_game_view.is_afk_dialog_showing(): # Double check
             self.app_view.after(0, mp_game_view.close_afk_dialog)

        self.afk_dialog_cooldown_until = time.time() + self.AFK_DIALOG_COOLDOWN_SECONDS
        try:
            self.model.start_multiplayer_next_round()
        except Exception as e:
            # print(f"Error starting next round after AFK dialog: {e}")
            pass # Gracefully handle if start next round fails

    def _handle_afk_timeout(self):
        # print("AFK Dialog: Timed out or closed by user.")
        self.afk_dialog_active = False # Dialog will be closed by its own mechanism
        mp_game_view = self.app_view.frames.get("MultiplayerGame")
        if mp_game_view and mp_game_view.is_afk_dialog_showing(): # Double check
            self.app_view.after(0, mp_game_view.close_afk_dialog)

        self.afk_dialog_cooldown_until = time.time() + self.AFK_DIALOG_COOLDOWN_SECONDS
        
        # print("GAME CONTROLLER: First AFK dialog timed out. Triggering Last Chance dialog.")
        if mp_game_view: # Ensure view exists
            self.app_view.after(0, lambda: mp_game_view.show_last_chance_dialog(
                on_last_chance_callback=self._handle_last_chance_yes
            ))

    # New method to be called after the 4s delay
    def _trigger_first_afk_dialog_if_conditions_met(self):
        self.afk_pre_check_timer_id = None # Timer has fired
        self.afk_pre_check_delay_active = False
        mp_game_view = self.app_view.frames.get("MultiplayerGame")

        current_server_round = self.model.get_mp_current_round()
        is_round_still_in_progress = self.model.is_mp_round_in_progress()
        current_game_winner = self.model.get_mp_game_winner()
        current_session_result = self.model.get_mp_session_result()

        # print(f"GAME CONTROLLER: 4s pre-AFK check ended. Stored round: {self.round_at_afk_check_start}, Current server round: {current_server_round}, Round in progress: {is_round_still_in_progress}")

        if not current_game_winner and current_session_result == "ONGOING" and \
           self.round_at_afk_check_start == current_server_round and \
           not is_round_still_in_progress and \
           not self.afk_dialog_active and \
           time.time() > self.afk_dialog_cooldown_until:
            
            # print("GAME CONTROLLER: Conditions met after 4s delay. Showing first AFK dialog.")
            self.afk_dialog_active = True 
            if mp_game_view:
                self.app_view.after(0, lambda: mp_game_view.show_afk_dialog(
                    on_yes_callback=self._handle_afk_yes,
                    on_timeout_callback=self._handle_afk_timeout
                ))
        else:
            # print("GAME CONTROLLER: Conditions NOT met after 4s delay, or AFK dialog already active. Not showing first AFK dialog.")
            pass # Explicitly do nothing

    # New method for the "Last Chance" dialog's button
    def _handle_last_chance_yes(self):
        # print("GAME CONTROLLER: Last Chance Dialog - Yes clicked.")
        try:
            self.model.start_multiplayer_next_round()
        except Exception as e:
            mp_game_view = self.app_view.frames.get("MultiplayerGame")
            if mp_game_view:
                 self.app_view.after(0, lambda err_e=e: mp_game_view.set_status(f"Error starting next round: {str(err_e)}", "red")) 

    def _schedule_next_round_attempt_mp(self, round_just_ended):
        # Ensure we only schedule this once per ended round for this client
        if self.mp_next_round_scheduled_for_round == round_just_ended and self.mp_next_round_timer_id is not None:
            # print(f"Python Client: Next round attempt already scheduled for round {round_just_ended}")
            return

        if self.mp_next_round_timer_id: # Cancel any previous timer from this client
            self.app_view.after_cancel(self.mp_next_round_timer_id)
            # print(f"Python Client: Cancelled previous next round timer.")

        self.mp_next_round_scheduled_for_round = round_just_ended
        # print(f"Python Client: Scheduling next round attempt after round {round_just_ended} in 3 seconds.")
        self.mp_next_round_timer_id = self.app_view.after(3000, self._execute_start_multiplayer_next_round)

    def _execute_start_multiplayer_next_round(self):
        self.mp_next_round_timer_id = None # Timer has fired
        # print("Python Client: Executing delayed start_multiplayer_next_round.")
        
        # Check if still in the correct view and polling is active
        if not self.polling_active or self.current_view != self.app_view.frames.get("MultiplayerGame"):
            # print("Python Client: Polling stopped or view changed. Not executing next round.")
            return

        try:
            # Refresh the model's understanding of the current game state
            _ = self.model.get_multiplayer_lobby_state() 
            is_now_round_in_progress = self.model.is_mp_round_in_progress()
            game_is_over = self.model.get_mp_game_winner() or (self.model.get_mp_session_result() not in ["ONGOING", None, ""])

            if game_is_over:
                # print("Python Client: Game is over. Not starting next round.")
                return

            # If a round is NOT in progress (implying no one else started it in the last 3s)
            if not is_now_round_in_progress:
                # print("Python Client: Round not in progress. Attempting to start next round.")
                self.model.start_multiplayer_next_round()
            # else:
                # print("Python Client: Next round already started by someone else or state changed. Skipping.")
        except Exception as e:
            # print(f"Python Client: Error in _execute_start_multiplayer_next_round: {e}")
            pass

    def _schedule_next_round_attempt_sp(self, round_just_ended):
        # Ensure we only schedule this once per ended round for this client
        if self.sp_next_round_scheduled_for_round == round_just_ended and self.sp_next_round_timer_id is not None:
            # print(f"Python Client: Next round attempt already scheduled for round {round_just_ended}")
            return

        if self.sp_next_round_timer_id: # Cancel any previous timer from this client
            self.app_view.after_cancel(self.sp_next_round_timer_id)
            # print(f"Python Client: Cancelled previous next round timer.")

        self.sp_next_round_scheduled_for_round = round_just_ended
        # print(f"Python Client: Scheduling next round attempt after round {round_just_ended} in 3 seconds.")
        self.sp_next_round_timer_id = self.app_view.after(3000, self._execute_start_single_player_next_round)

    def _execute_start_single_player_next_round(self):
        self.sp_next_round_timer_id = None # Timer has fired
        # print("Python Client: Executing delayed start_single_player_next_round.")
        
        # Check if still in the correct view and polling is active
        if not self.polling_active or self.current_view != self.app_view.frames.get("SinglePlayerGame"):
            # print("Python Client: Polling stopped or view changed. Not executing next round.")
            return

        try:
            # Refresh the model's understanding of the current game state
            state = self.model.get_game_state()
            if state:
                # print("Python Client: Starting next round.")
                self.model.start_new_round()
            else:
                # print("Python Client: Error fetching game state. Not starting next round.")
                pass
        except Exception as e:
            # print(f"Python Client: Error in _execute_start_single_player_next_round: {e}")
            pass 