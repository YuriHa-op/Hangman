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

        # Flags for single-player game state management
        self.game_session_cleaned_up = False
        self.sp_client_timeout_sent_for_round = {} # Tracks if client sent timeout for a round_num
        self._last_processed_server_round_for_word_clear = -1 # Helper for sp_current_word logic
        self.current_sp_server_round_processed_for_next_attempt = -1 # Tracks if start_new_round called for an ended server round

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
        self.spectating_player = None # Reset spectate on game start
        self.last_keyboard_state_mp = None # Reset keyboard state
        # Initial state might already be in model.lobby_state from queue
        # Or we might need a fresh fetch if joining mid-game (not current design)
        self.mp_game_polling_thread = threading.Thread(target=self._poll_mp_game_state, daemon=True)
        self.mp_game_polling_thread.start()

    def _poll_mp_game_state(self):
        mp_game_view = self.app_view.frames.get("MultiplayerGame")
        my_username = self.model.get_username()
        cleaned_up_session = False

        while self.polling_active and self.current_view == mp_game_view:
            try:
                # Model's get_multiplayer_lobby_state refreshes self.model.lobby_state
                _ = self.model.get_multiplayer_lobby_state() # Fetches and updates model internal state

                players = self.model.get_lobby_players()
                if self.spectating_player and self.spectating_player not in players:
                    self.spectating_player = None # Player left, return to self view

                pov_username = self.spectating_player if self.spectating_player else my_username

                masked_words = self.model.get_mp_masked_words()
                all_current_words = self.model.get_mp_all_current_words()
                player_guesses_map = self.model.get_mp_player_guesses_map()
                incorrect_guesses_map = self.model.get_mp_incorrect_guesses_map()
                remaining_time = self.model.get_mp_remaining_time()
                current_round = self.model.get_mp_current_round()
                scores = self.model.get_mp_scores()
                round_in_progress = self.model.is_mp_round_in_progress()
                round_winner = self.model.get_mp_round_winner()
                game_winner = self.model.get_mp_game_winner()
                session_result = self.model.get_mp_session_result()

                word_display = masked_words.get(pov_username, "_ _ _")
                timer_display = f"Time left: {remaining_time}s"
                round_display = f"Round: {current_round + 1}"
                status_display = ""

                # Refined logic for enabling/disabling keyboard for POV
                pov_masked_word = masked_words.get(pov_username, "")
                pov_incorrect_guesses = incorrect_guesses_map.get(pov_username, 0)
                pov_is_done_guessing = (pov_incorrect_guesses >= 5) or (pov_masked_word and "_" not in pov_masked_word)

                can_truly_guess = (pov_username == my_username) and \
                                  not self.spectating_player and \
                                  round_in_progress and \
                                  not game_winner and \
                                  not pov_is_done_guessing # Check if current user (my_username) is done with their word
                
                interaction_over_for_pov = bool(game_winner) or (not round_in_progress) or pov_is_done_guessing

                # For spectate button logic (is the *actual user* done?)
                my_actual_masked = masked_words.get(my_username, "")
                my_actual_incorrect = incorrect_guesses_map.get(my_username, 0)
                is_user_done_guessing_for_spectate_button = (my_actual_incorrect >= 5) or (my_actual_masked and "_" not in my_actual_masked)

                # Keyboard state for the current POV
                current_keyboard_state = (frozenset(player_guesses_map.get(pov_username, [])), all_current_words.get(pov_username, ""), current_round)

                if not round_in_progress: # Round is over
                    # If AFK dialog was shown, it should be closed by its own callbacks or by game progression
                    # self.app_view.after(0, mp_game_view.close_afk_dialog) # Ensure it's closed if round ends for any reason
                    # The logic below for showing AFK dialog handles the specific case of "no winner"

                    if round_winner:
                        if round_winner == my_username:
                            status_display = "You won this round!"
                        else:
                            status_display = f"{round_winner} won this round."
                        # If there's a winner, ensure AFK dialog is closed and reset flags
                        if self.afk_dialog_active:
                            self.app_view.after(0, mp_game_view.close_afk_dialog)
                            self.afk_dialog_active = False
                    else: # No round winner
                        status_display = "No one won this round."
                        # Potentially show AFK dialog if conditions met
                        if not game_winner and session_result == "ONGOING" and \
                           remaining_time <= 0 and \
                           not self.afk_dialog_active and \
                           time.time() > self.afk_dialog_cooldown_until:
                            self.afk_dialog_active = True # Set flag before showing
                            self.app_view.after(0, lambda: mp_game_view.show_afk_dialog(
                                on_yes_callback=self._handle_afk_yes,
                                on_timeout_callback=self._handle_afk_timeout
                            ))
                    
                    # If game is not over, server should auto start next round, or client needs to trigger
                    if not game_winner and session_result == "ONGOING":
                        # If AFK dialog is NOT shown (e.g. there was a winner), client might tell server to start next round
                        # Or assume server handles it. For now, if AFK dialog is shown, its callback handles next round.
                        if round_winner: # If there was a winner, implies server will/should start next round
                             # Potentially model.start_multiplayer_next_round() if client needs to trigger it
                             # and there wasn't an AFK dialog active to do it.
                             pass
                elif round_in_progress and self.afk_dialog_active: # Round started while AFK dialog was up
                    self.app_view.after(0, mp_game_view.close_afk_dialog)
                    self.afk_dialog_active = False
                
                if game_winner:
                    if self.afk_dialog_active: # Game ended while AFK dialog was up
                        self.app_view.after(0, mp_game_view.close_afk_dialog)
                        self.afk_dialog_active = False
                    if not cleaned_up_session:
                        try:
                            self.model.end_game_session() # General end session
                            self.model.cleanup_player_session() # Specific cleanup
                        except Exception as e_clean:
                            print(f"Error during end game cleanup: {e_clean}")
                        cleaned_up_session = True
                    
                    if game_winner == my_username:
                        status_display = "🎉 You won the game! 🎉"
                    else:
                        status_display = f"{game_winner} won the game."
                    self.polling_active = False # Stop polling

                # Auto-return from spectate if spectated player finished their part
                if self.spectating_player:
                    spectated_masked = masked_words.get(self.spectating_player, "")
                    spectated_incorrect = incorrect_guesses_map.get(self.spectating_player, 0)
                    if (spectated_incorrect >= 5) or (spectated_masked and "_" not in spectated_masked):
                        self.spectating_player = None
                        pov_username = my_username # Update pov for current cycle
                        can_truly_guess = True # Re-evaluate can_truly_guess
                        current_keyboard_state = (frozenset(player_guesses_map.get(pov_username, [])), all_current_words.get(pov_username, ""), current_round)

                # Schedule view update
                self.app_view.after(0, lambda pov_u=pov_username, p_guesses_map=dict(player_guesses_map), act_words_map=dict(all_current_words), c_truly_guess=can_truly_guess, interact_over=interaction_over_for_pov: mp_game_view.update_display(
                    word_display, timer_display, round_display, status_display,
                    players, scores, pov_u, 
                    p_guesses_map, act_words_map, 
                    c_truly_guess, is_user_done_guessing_for_spectate_button, # is_user_done_guessing is for spectate button
                    interact_over # interaction_over_for_pov for keyboard
                ))
                
                # This direct call to update_keyboard might be redundant if update_display always calls it.
                # However, it ensures keyboard updates if only keyboard-relevant state changes.
                if current_keyboard_state != self.last_keyboard_state_mp:
                     self.app_view.after(0, lambda pov_u=pov_username, p_guesses_map=dict(player_guesses_map), act_words_map=dict(all_current_words), c_truly_guess=can_truly_guess, interact_over=interaction_over_for_pov: 
                        mp_game_view.update_keyboard(pov_u, p_guesses_map, act_words_map, c_truly_guess, interact_over))
                     self.last_keyboard_state_mp = current_keyboard_state

                if not self.polling_active: break # Exit if polling was stopped (e.g. game over)

            except Exception as e:
                # print(f"Error polling multiplayer game state: {e}")
                # traceback.print_exc() # For more detailed error
                self.polling_active = False
                self.app_view.after(0, lambda: mp_game_view.set_status("Error in game. Returning to menu.", "red"))
                self.app_view.after(2000, lambda: self.show_frame("MainMenu")) # Delay then go to menu
                break
            time.sleep(0.25) # Polling interval (new)

    def handle_multiplayer_guess(self, letter):
        if self.spectating_player: return # No guesses while spectating
        if not self.polling_active: return # Game might be over
        
        # Optimistically update UI for the guess, then confirm with next poll
        # Or, rely on polling to update. For now, let poll handle update.
        try:
            # correct = self.model.send_multiplayer_guess(letter.lower())
            # mp_game_view = self.app_view.frames.get("MultiplayerGame")
            # mp_game_view.feedback_guess_mp(letter, correct) # View needs this method
            # The guess will change the server state, which the poll will pick up.
            # No direct feedback needed from sendMultiplayerGuess if poll is frequent enough.
            self.model.send_multiplayer_guess(letter.lower())
            # The next poll cycle will reflect the guess.
        except Exception as e:
            # print(f"Error sending multiplayer guess: {e}")
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

    def _initialize_and_poll_sp_game(self):
        sp_game_view = self.app_view.frames.get("SinglePlayerGame")
        try:
            masked_word_init = self.model.start_game() # startGame on model
            # After starting game, try to get the full game state to know the word for keyboard coloring
            initial_state = self.model.get_game_state()
            if initial_state and hasattr(initial_state, 'actualWord') and initial_state.actualWord:
                 self.sp_current_word = initial_state.actualWord.upper()
            elif initial_state:
                 # Fallback if actualWord is not available, keyboard coloring for correct letters might be delayed
                 # We can try to infer from maskedWord if it's fully revealed later
                 pass 

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
            
            # Match found, show countdown dialog via view, then start polling.
            # The countdown_callback will be self._poll_sp_game_state
            self.app_view.after(0, lambda: sp_game_view.show_match_found_countdown(self._poll_sp_game_state_after_countdown))

        except Exception as e:
            # print(f"Error starting single player game: {e}")
            self.app_view.after(0, lambda: sp_game_view.set_status(f"Error: {e}"))
            self.polling_active = False
            self.sp_attempted_letters.clear()
            self.sp_current_word = ""

    def _poll_sp_game_state_after_countdown(self):
        # This is the callback after the countdown finishes
        # Start the actual game state polling loop
        self.sp_polling_thread = threading.Thread(target=self._poll_sp_game_state_loop, daemon=True)
        self.sp_polling_thread.start()

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
                    self.app_view.after(0, lambda s=state, st=status_text: sp_game_view.update_display(
                        s.maskedWord, f"Time left: {s.remainingTime}s", f"Incorrect guesses: {s.incorrectGuesses}/5", st, 
                        s.playerWins, 
                        s.currentRound, # Pass current round number
                        self.sp_attempted_letters, self.sp_current_word, True, s.gameOver == GameModule.BOOL_TRUE
                    ))

                elif state.gameOver == GameModule.BOOL_TRUE or (state.sessionResult and state.sessionResult != "ONGOING"):
                    if not self.game_session_cleaned_up:
                        self.model.end_game_session()
                        self.model.cleanup_player_session()
                        self.game_session_cleaned_up = True
                    
                    status_text = self._determine_sp_game_over_status_text(state)
                    self.polling_active = False # Stop polling
                    
                    # Final UI update before showing dialog
                    self.app_view.after(0, lambda s=state, st=status_text: sp_game_view.update_display(
                        s.maskedWord, f"Time left: {s.remainingTime}s", f"Incorrect guesses: {s.incorrectGuesses}/5", st, 
                        s.playerWins, 
                        s.currentRound, # Pass current round number
                        self.sp_attempted_letters, self.sp_current_word, True, True # roundOver=True, gameOver=True
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
                    self.app_view.after(0, lambda s=state, st=status_text: sp_game_view.update_display(
                        s.maskedWord, f"Time left: {s.remainingTime}s", f"Incorrect guesses: {s.incorrectGuesses}/5", st, 
                        s.playerWins, 
                        s.currentRound, # Pass current round number
                        self.sp_attempted_letters, self.sp_current_word, False, False # roundOver=False, gameOver=False
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

    def _handle_afk_yes(self):
        # print("AFK Dialog: Yes clicked.")
        self.afk_dialog_active = False # Dialog will be closed by its own mechanism
        self.afk_dialog_cooldown_until = time.time() + self.AFK_DIALOG_COOLDOWN_SECONDS
        try:
            self.model.start_multiplayer_next_round()
        except Exception as e:
            # print(f"Error starting next round after AFK dialog: {e}")
            pass # Gracefully handle if start next round fails

    def _handle_afk_timeout(self):
        # print("AFK Dialog: Timed out or closed by user.")
        self.afk_dialog_active = False # Dialog will be closed by its own mechanism
        self.afk_dialog_cooldown_until = time.time() + self.AFK_DIALOG_COOLDOWN_SECONDS
        # Server-side stall check should handle game cleanup if player is truly AFK.
        # Client does not explicitly end game here; relies on server timeout or next poll finding game ended. 