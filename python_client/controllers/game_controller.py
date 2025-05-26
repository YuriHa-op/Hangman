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
                print(f"Error polling multiplayer lobby state: {e}")
                # Optionally update view with error status
                self.polling_active = False # Stop polling on error
                self.app_view.after(0, self.show_frame, "MainMenu") # Go back to main menu on error
                break
            time.sleep(1) # Polling interval
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
    def load_match_history(self):
        history_view = self.app_view.frames.get("MatchHistory")
        try:
            history_json = self.model.get_match_history() # Model returns JSON string
            history_view.display_match_history(history_json)
        except Exception as e:
            print(f"Error loading match history: {e}")
            # Optionally show error in view

    def show_match_details(self, game_id):
        history_view = self.app_view.frames.get("MatchHistory")
        try:
            details_json = self.model.get_match_details(game_id) # Model returns JSON string
            history_view.show_details_popup(details_json)
        except Exception as e:
            print(f"Error loading match details: {e}")
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
                    if round_winner:
                        if round_winner == my_username:
                            status_display = "You won this round!"
                        else:
                            status_display = f"{round_winner} won this round."
                    else:
                        status_display = "No one won this round."
                    
                    # If game is not over, server should auto start next round, or client needs to trigger
                    if not game_winner and session_result == "ONGOING":
                        # Add a small delay before enabling UI for next round if server handles it
                        # If client needs to trigger:
                        # self.model.start_multiplayer_next_round() # Ensure this is idempotent or guarded
                        pass # Assuming server starts next round automatically or after a delay.
                
                if game_winner:
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
                print(f"Error polling multiplayer game state: {e}")
                # traceback.print_exc() # For more detailed error
                self.polling_active = False
                self.app_view.after(0, lambda: mp_game_view.set_status("Error in game. Returning to menu.", "red"))
                self.app_view.after(2000, lambda: self.show_frame("MainMenu")) # Delay then go to menu
                break
            time.sleep(0.5) # Polling interval, was 1, try 0.5 for responsiveness

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
            print(f"Error sending multiplayer guess: {e}")
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
            print(f"Error during back_to_menu cleanup from MP game: {e}")
        self.show_frame("MainMenu")

    # --- SinglePlayerGameView Handlers ---
    def start_single_player_game(self):
        self.stop_all_polling()
        self.polling_active = True
        sp_game_view = self.app_view.frames.get("SinglePlayerGame")
        sp_game_view.set_status("Starting game...")
        
        # Reset keyboard and display for a new game
        self.sp_attempted_letters.clear()
        self.sp_current_word = ""
        self.app_view.after(0, lambda: sp_game_view.update_display("_ _ _", "Time: --", "Incorrect: 0/5", "", self.sp_attempted_letters, self.sp_current_word, False, False))
        
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
            print(f"Error starting single player game: {e}")
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
        cleaned_up_session = False

        while self.polling_active and self.current_view == sp_game_view:
            try:
                state = self.model.get_game_state()
                if not state: # Should not happen if game started correctly
                    self.app_view.after(0, lambda: sp_game_view.set_status("Error fetching game state.", "red"))
                    self.polling_active = False
                    break

                # Extract details for view update
                masked_word = state.maskedWord
                timer_text = f"Time left: {state.remainingTime}s"
                incorrect_text = f"Incorrect guesses: {state.incorrectGuesses}/5"
                status_text = ""
                
                # Update sp_current_word if available and not yet set, or if it changed (new round)
                if hasattr(state, 'actualWord') and state.actualWord and self.sp_current_word != state.actualWord.upper():
                    self.sp_current_word = state.actualWord.upper()
                    self.sp_attempted_letters.clear() # Word changed, clear attempts for new word
                elif not self.sp_current_word and "_" not in masked_word: # Infer if word revealed and not set
                    self.sp_current_word = masked_word.replace(" ","").upper()

                if state.roundOver:
                    if not cleaned_up_session : # only call finishRound once per round ending
                        guessed_word_bool = "_" not in masked_word
                        self.model.finish_round(state.remainingTime, guessed_word_bool)
                        # Re-fetch state after finishRound as it might change winner etc.
                        # state = self.model.get_game_state() # Potentially, if finishRound updates it server-side immediately.
                        # For now, assume next poll cycle gets updated state after finishRound impact.

                    if state.roundWinner:
                        if state.roundWinner == self.model.get_username():
                            status_text = "You won this round!"
                        else:
                            status_text = f"{state.roundWinner} won this round."
                    else:
                        status_text = "No one won this round."
                    
                    # If game not over, start next round
                    if not state.gameOver and state.sessionResult == "ONGOING":
                        time.sleep(2) # Display round result for a bit
                        if self.polling_active: # Check if still active before starting new round
                            self.model.start_new_round()
                            self.sp_attempted_letters.clear() # Clear for new round
                            # Fetch new state to get new actualWord if possible
                            new_round_state = self.model.get_game_state()
                            if new_round_state and hasattr(new_round_state, 'actualWord') and new_round_state.actualWord:
                                self.sp_current_word = new_round_state.actualWord.upper()
                            else:
                                self.sp_current_word = "" # Reset if not available
                            
                            self.app_view.after(0, lambda: sp_game_view.update_display("_ _ _", "Time: --", "Incorrect: 0/5", "Starting next round...", self.sp_attempted_letters, self.sp_current_word, False, False))

                if state.sessionResult and state.sessionResult != "ONGOING":
                    if not cleaned_up_session:
                        self.model.end_game_session() # Ensure game session ends on server
                        self.model.cleanup_player_session()
                        self.sp_attempted_letters.clear() # Clear on game end
                        self.sp_current_word = ""
                        cleaned_up_session = True

                    if state.sessionResult == "WIN":
                        status_text = "🎉 You won the game! 🎉"
                    elif state.sessionResult == "LOSE":
                        status_text = "You lost the game."
                    else:
                        status_text = f"Game session result: {state.sessionResult}"
                    self.polling_active = False # Stop polling

                # Schedule view update
                # `revealed_letters` for keyboard state might need to be expanded with incorrectly guessed letters if tracked
                self.app_view.after(0, lambda: sp_game_view.update_display(
                    masked_word, timer_text, incorrect_text, status_text, 
                    self.sp_attempted_letters, self.sp_current_word, state.roundOver, state.gameOver
                ))
                
                if not self.polling_active: break

            except Exception as e:
                print(f"Error polling single player game state: {e}")
                # traceback.print_exc()
                self.app_view.after(0, lambda: sp_game_view.set_status("Error in game. Returning to menu.", "red"))
                self.polling_active = False
                self.app_view.after(2000, lambda: self.show_frame("MainMenu")) # Delay then go to menu
                break
            time.sleep(1) # Polling interval

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
            print(f"Error sending SP guess: {e}")
            self.app_view.after(0, lambda: sp_game_view.set_status(f"Error guessing: {e}", "red"))

    def handle_back_to_menu_from_sp_game(self):
        self.stop_all_polling()
        try:
            self.model.end_game_session()
            self.model.cleanup_player_session()
            self.sp_attempted_letters.clear() # Clear on back to menu
            self.sp_current_word = ""
        except Exception as e:
            print(f"Error during back_to_menu cleanup from SP game: {e}")
        self.show_frame("MainMenu")

    # --- LeaderboardView Handlers ---
    def load_leaderboard(self):
        leaderboard_view = self.app_view.frames.get("Leaderboard")
        try:
            entries = self.model.get_leaderboard_entries() # Model handles parsing logic
            leaderboard_view.display_leaderboard(entries)
        except Exception as e:
            print(f"Error loading leaderboard: {e}")
            # Optionally show error in view

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