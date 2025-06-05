import threading
import time
import GameModule  # For GameStateDTO, BOOL_TRUE, BOOL_FALSE
from PyQt5.QtCore import QMetaObject, Qt, pyqtSignal, QObject
from .base_controller import BaseController

class WorkerSignals(QObject):
    update_view_signal = pyqtSignal(dict)
    show_match_found_signal = pyqtSignal(str)
    show_game_over_signal = pyqtSignal(str, str) # result_text, game_status (WIN/LOSE/etc)
    set_status_signal = pyqtSignal(str, str) # message, color
    polling_stopped_signal = pyqtSignal()

class SinglePlayerGameController(BaseController):
    def __init__(self, model, view):
        super().__init__(model, view) # self.view is QtSinglePlayer1v1GameView
        self.polling_thread = None
        self.polling_active = False
        self.signals = WorkerSignals()

        # Connect signals from worker to view/controller methods
        self.signals.update_view_signal.connect(self._update_view_from_thread)
        self.signals.show_match_found_signal.connect(self._show_match_found_dialog_from_thread)
        self.signals.show_game_over_signal.connect(self._show_game_over_dialog_from_thread)
        self.signals.set_status_signal.connect(self.view.set_status)
        self.signals.polling_stopped_signal.connect(self._on_polling_stopped)

        # Game state attributes, similar to Tkinter version
        self.dialog_completion_event = None # For synchronizing dialog completion
        self.game_session_cleaned_up = True # Start as true, set to false when game starts
        self.client_timeout_sent_for_round = {}
        self.last_processed_server_round_for_word_clear = -1
        self.current_server_round_processed_for_next_attempt = -1
        self.attempted_letters_current_round = set()
        self.current_actual_word_revealed = "" # Store the actual word when server reveals it
        self.full_round_time = 30 # Default, should be fetched (e.g., from GameStateDTO.roundTime if available or fixed config)
        self.total_rounds = 3 # Assuming a best of 3, from Tkinter version's "Score: X/3"
        self.max_incorrect_guesses = 5 # As per Tkinter view

    def on_show(self):
        super().on_show()
        print("[SP1v1Controller] on_show called.")
        self.start_single_player_1v1_game()

    def on_hide(self):
        super().on_hide()
        print("[SP1v1Controller] on_hide called.")
        self.stop_polling_and_cleanup_game()
        if self.view and hasattr(self.view, 'on_hide_cleanup'):
            self.view.on_hide_cleanup() # Close any view-specific dialogs

    def stop_polling_and_cleanup_game(self):
        print("[SP1v1Controller] Stopping polling and cleaning up game.")
        self.polling_active = False
        if self.polling_thread and self.polling_thread.is_alive():
            try:
                self.polling_thread.join(timeout=1.0) # Wait for thread to finish
            except Exception as e:
                print(f"[SP1v1Controller] Error joining polling_thread: {e}")
        self.polling_thread = None

        if not self.game_session_cleaned_up:
            try:
                print("[SP1v1Controller] Cleaning up game session on server.")
                self.model.end_game_session()
                self.model.cleanup_player_session()
                self.game_session_cleaned_up = True
            except Exception as e:
                print(f"[SP1v1Controller] Error during server cleanup: {e}")
        
        # Reset controller state for next game
        self._reset_controller_game_state()

    def _reset_controller_game_state(self):
        self.client_timeout_sent_for_round.clear()
        self.last_processed_server_round_for_word_clear = -1
        self.current_server_round_processed_for_next_attempt = -1
        self.attempted_letters_current_round.clear()
        self.current_actual_word_revealed = ""
        if self.dialog_completion_event: # Clear event if it exists
            self.dialog_completion_event.set() # Unblock if anyone is waiting, then clear
        self.dialog_completion_event = None

    def _on_polling_stopped(self):
        print("[SP1v1Controller] Polling stopped signal received.")
        # This can be used for any UI updates needed after polling fully stops, if any.

    def start_single_player_1v1_game(self):
        if self.polling_active:
            print("[SP1v1Controller] Game already in progress or starting.")
            return
        
        print("[SP1v1Controller] Starting 1v1 single player game.")
        self._reset_controller_game_state() # Reset state for a new game
        self.game_session_cleaned_up = False # Mark that a session is now active
        self.polling_active = True

        self.view.set_status("Initializing game...", "blue")
        # Reset view to a clean state for a new game
        self.view.update_display(
            masked_word="_ _ _", timer_text="Time: --", incorrect_text=f"Incorrect: 0/{self.max_incorrect_guesses}",
            status_text="Initializing...", player_wins=0, total_rounds=self.total_rounds,
            current_round_num=0, attempted_letters=set(), current_word_upper="",
            round_over=False, game_over=False
        )
        self.view.update_keyboard(set(), "", disable_all=False)


        self.polling_thread = threading.Thread(target=self._initialize_and_poll_game_loop, daemon=True)
        self.polling_thread.start()

    def _initialize_and_poll_game_loop(self):
        """Handles initial game setup (like waiting for match) and then transitions to polling game state."""
        try:
            initial_server_response = self.model.start_game() # This might block or return immediately
            if not initial_server_response: # Indicates an immediate issue with starting game
                self.signals.set_status_signal.emit("Error: Could not start game.", "red")
                self.polling_active = False
                return

            if initial_server_response == "WAITING_FOR_MATCH":
                self.signals.set_status_signal.emit("Waiting for match allocation...", "blue")
                wait_start_time = time.time()
                # Max wait time, e.g. 60 seconds, to prevent indefinite waiting client-side
                # The server might also timeout the request.
                max_wait_duration = self.model.get_waiting_time() if hasattr(self.model, 'get_waiting_time') else 60 
                
                while self.polling_active and (time.time() - wait_start_time < max_wait_duration):
                    current_masked_word = self.model.get_masked_word() # This is the check for match found
                    if current_masked_word and current_masked_word != "WAITING_FOR_MATCH":
                        initial_server_response = current_masked_word # Match found
                        break
                    time.sleep(0.5) # Poll interval for match
                
                if initial_server_response == "WAITING_FOR_MATCH": # Still waiting after timeout
                    self.signals.set_status_signal.emit("No match found. Try again later.", "orange")
                    self.polling_active = False
                    if not self.game_session_cleaned_up:
                        try: self.model.end_game_session(); self.model.cleanup_player_session(); self.game_session_cleaned_up = True
                        except Exception as e: print(f"SP1v1 Init No Match Cleanup Error: {e}")
                    return
            
            # Match found, proceed to get initial state and show countdown
            initial_game_state = self.model.get_game_state() # Should now have opponent info
            opponent_name = "Opponent"
            if initial_game_state and hasattr(initial_game_state, 'opponentUsername') and initial_game_state.opponentUsername:
                opponent_name = initial_game_state.opponentUsername
            
            # Update full_round_time if available from game state
            if initial_game_state and hasattr(initial_game_state, 'roundTime') and initial_game_state.roundTime > 0:
                 self.full_round_time = initial_game_state.roundTime
            if initial_game_state and hasattr(initial_game_state, 'maxRounds') and initial_game_state.maxRounds > 0:
                 self.total_rounds = initial_game_state.maxRounds

            # Prepare for dialog synchronization
            self.dialog_completion_event = threading.Event()
            self.signals.show_match_found_signal.emit(opponent_name)
            
            # Worker thread waits for dialog to complete (max 10 seconds for safety)
            # The dialog is shown in the main thread via the signal.
            # The dialog's callback (_signal_dialog_event_from_main_thread) will set this event.
            print("[SP1v1Controller] Worker thread waiting for match_found_dialog completion...")
            dialog_completed_in_time = self.dialog_completion_event.wait(timeout=10.0) # e.g., 10s timeout
            current_event = self.dialog_completion_event # Store before clearing
            self.dialog_completion_event = None # Clear the event for next use

            if not self.polling_active: # Check if polling was stopped during wait
                print("[SP1v1Controller] Polling stopped while waiting for dialog. Aborting.")
                if current_event and not current_event.is_set(): current_event.set() # Ensure no deadlocks if thread is re-used
                self.signals.polling_stopped_signal.emit()
                return

            if not dialog_completed_in_time:
                print("[SP1v1Controller] Match found dialog timed out or was closed prematurely. Aborting game start.")
                self.signals.set_status_signal.emit("Dialog timeout. Returning to menu.", "orange")
                self.polling_active = False
                if not self.game_session_cleaned_up:
                    try: self.model.end_game_session(); self.model.cleanup_player_session(); self.game_session_cleaned_up = True
                    except Exception as e: print(f"SP1v1 Dialog Timeout Cleanup Error: {e}")
                self.signals.polling_stopped_signal.emit()
                return
            
            # Dialog completed, proceed in worker thread
            print("[SP1v1Controller] Match found dialog completed. Worker thread signaling player ready.")
            if self.model.get_username():
                try:
                    self.model.player_ready_for_first_round()
                except Exception as e:
                    print(f"[SP1v1Controller] Error signaling player ready: {e}")
                    self.signals.set_status_signal.emit("Error starting round. Try again.", "red")
                    self.polling_active = False
                    self.signals.polling_stopped_signal.emit()
                    return
            else: # Should not happen if login is enforced
                self.signals.set_status_signal.emit("User not identified. Cannot start round.", "red")
                self.polling_active = False
                self.signals.polling_stopped_signal.emit()
                return
            
            # Now, start the main game state polling loop IN THIS WORKER THREAD
            if self.polling_active:
                self._poll_game_state_loop()
            else:
                print("[SP1v1Controller] Polling became inactive before starting game state loop post-dialog.")
                self.signals.polling_stopped_signal.emit()

        except Exception as e:
            print(f"[SP1v1Controller] Error during game initialization: {e}")
            import traceback; traceback.print_exc()
            self.signals.set_status_signal.emit(f"Initialization Error: {e}", "red")
            self.polling_active = False
            # Ensure cleanup if initialization fails
            if not self.game_session_cleaned_up:
                try: self.model.end_game_session(); self.model.cleanup_player_session(); self.game_session_cleaned_up = True
                except Exception as clean_e: print(f"SP1v1 Init Hard Fail Cleanup Error: {clean_e}")
        
        if not self.polling_active: # If init failed or was aborted
            self.signals.polling_stopped_signal.emit()

    def _poll_game_state_loop(self):
        """Main loop for polling game state from the server."""
        print("[SP1v1Controller] Starting main game state polling loop.")
        while self.polling_active:
            try:
                state: GameModule.GameStateDTO = self.model.get_game_state()
                if not state:
                    self.signals.set_status_signal.emit("Error fetching game state. Disconnecting.", "red")
                    self.polling_active = False
                    break # Exit polling loop

                server_current_round = state.currentRound
                status_text = "Guess the word!"
                timer_display_text = f"Time: {state.remainingTime}s"
                timer_color = "black"
                if state.remainingTime <= 10 and state.remainingTime > 5 : timer_color = "orange"
                if state.remainingTime <= 5: timer_color = "red"
                if state.remainingTime == self.full_round_time and state.roundOver == GameModule.BOOL_FALSE and state.gameOver == GameModule.BOOL_FALSE :
                     timer_display_text = "Time: --" # Before first real tick


                # Handle actual word revelation (for keyboard coloring at round end)
                if hasattr(state, 'actualWord') and state.actualWord and state.actualWord != "_ _ _":
                    self.current_actual_word_revealed = state.actualWord.upper()
                
                # Reset attempted letters if new round has started (server side)
                if server_current_round != self.last_processed_server_round_for_word_clear:
                    self.attempted_letters_current_round.clear()
                    self.client_timeout_sent_for_round.pop(server_current_round, None)
                    self.current_actual_word_revealed = "" # Clear revealed word for new round start
                    if hasattr(state, 'actualWord') and state.actualWord and state.actualWord != "_ _ _": # Pre-fill if available
                         self.current_actual_word_revealed = state.actualWord.upper()
                    self.last_processed_server_round_for_word_clear = server_current_round
                    self.signals.set_status_signal.emit("New round starting!", "green")


                # Client-side round timeout check (if server doesn\'t handle it quickly)
                if state.remainingTime <= 0 and \
                   state.roundOver == GameModule.BOOL_FALSE and \
                   state.gameOver == GameModule.BOOL_FALSE and \
                   not self.client_timeout_sent_for_round.get(server_current_round, False):
                    try:
                        print(f"[SP1v1Controller] Client-side timeout for round {server_current_round}. Sending finish_round.")
                        self.model.finish_round(0, False) # Guessed word is false on timeout
                        self.client_timeout_sent_for_round[server_current_round] = True
                        # Server should update state.roundOver soon after this.
                    except Exception as e:
                        print(f"[SP1v1Controller] Error sending finish_round on timeout: {e}")

                # Update view with current state
                view_update_payload = {
                    "masked_word": state.maskedWord,
                    "timer_text": timer_display_text,
                    "incorrect_text": f"Incorrect: {state.incorrectGuesses}/{self.max_incorrect_guesses}", # Assuming DTO has incorrectGuesses
                    "status_text": status_text,
                    "player_wins": state.playerWins,
                    "total_rounds": self.total_rounds, # Or state.maxRounds if available
                    "current_round_num": state.currentRound,
                    "attempted_letters": self.attempted_letters_current_round.copy(), # Send a copy
                    "current_word_upper": self.current_actual_word_revealed,
                    "round_over": state.roundOver == GameModule.BOOL_TRUE,
                    "game_over": state.gameOver == GameModule.BOOL_TRUE,
                    "timer_color": timer_color
                }
                
                # Handle Round Over
                if state.roundOver == GameModule.BOOL_TRUE and state.gameOver == GameModule.BOOL_FALSE:
                    status_text = self._determine_round_status_text(state)
                    view_update_payload["status_text"] = status_text
                    view_update_payload["current_word_upper"] = state.actualWord.upper() if hasattr(state, 'actualWord') and state.actualWord else self.current_actual_word_revealed
                    
                    if state.sessionResult == "ONGOING": # Check if more rounds
                        # Logic to attempt to start a new round
                        if server_current_round > self.current_server_round_processed_for_next_attempt:
                            if self.polling_active:
                                try: 
                                    print(f"[SP1v1Controller] Round {server_current_round} ended. Attempting to start next round.")
                                    new_round_ok = self.model.start_new_round() # Server starts new round
                                    self.current_server_round_processed_for_next_attempt = server_current_round
                                    if new_round_ok:
                                        self.signals.set_status_signal.emit("Starting next round...", "blue")
                                        # Attempted letters and actual word will be reset by the check at loop start
                                    else: # Should not happen if server logic is correct
                                        self.signals.set_status_signal.emit("Failed to start new round from server.", "orange")
                                except Exception as e:
                                    print(f"[SP1v1Controller] Error calling start_new_round: {e}")
                    # else: Game might be over but gameOver flag not yet set, sessionResult might indicate it.

                self.signals.update_view_signal.emit(view_update_payload)

                # Handle Game Over
                if state.gameOver == GameModule.BOOL_TRUE or (state.sessionResult and state.sessionResult != "ONGOING"):
                    print(f"[SP1v1Controller] Game over condition met. Session result: {state.sessionResult}")
                    self.polling_active = False # Stop polling
                    
                    final_status_text = self._determine_game_over_status_text(state)
                    # Ensure final view update reflects game over state
                    view_update_payload["status_text"] = final_status_text
                    view_update_payload["current_word_upper"] = state.actualWord.upper() if hasattr(state, 'actualWord') and state.actualWord else self.current_actual_word_revealed
                    self.signals.update_view_signal.emit(view_update_payload) # Final update before dialog

                    dialog_result_text = "You Won!" if state.sessionResult == "WIN" else \
                                         ("You Lost." if state.sessionResult == "LOSE" else \
                                          (f"Game Over: {state.sessionResult}" if state.sessionResult else "Game Ended"))
                    
                    self.signals.show_game_over_signal.emit(dialog_result_text, state.sessionResult)
                    if not self.game_session_cleaned_up:
                        try: 
                            self.model.end_game_session()
                            self.model.cleanup_player_session()
                            self.game_session_cleaned_up = True
                        except Exception as e: 
                            print(f"SP1v1 Game Over Cleanup Error: {e}")
                    break # Exit polling loop
                
                if not self.polling_active: break
                time.sleep(0.3) # Polling interval

            except CORBA.COMM_FAILURE as e:
                print(f"[SP1v1Controller] CORBA Communication Failure: {e}. Stopping polling.")
                self.signals.set_status_signal.emit("Connection to server lost. Returning to menu.", "red")
                self.polling_active = False
                # Consider navigating back to main menu after a delay
                # QTimer.singleShot(3000, lambda: self.view.main_window.show_view("MainMenu"))
                break
            except Exception as e:
                print(f"[SP1v1Controller] Error polling game state: {e}")
                import traceback; traceback.print_exc()
                self.signals.set_status_signal.emit("Error in game. Returning to menu.", "red")
                self.polling_active = False
                break # Exit polling loop
        
        print("[SP1v1Controller] Polling loop finished.")
        self.signals.polling_stopped_signal.emit()
        # Final cleanup if loop exited unexpectedly while session was active
        if not self.game_session_cleaned_up:
            try: 
                self.model.end_game_session()
                self.model.cleanup_player_session()
                self.game_session_cleaned_up = True
            except Exception as e: 
                print(f"SP1v1 Poll Loop Exit Cleanup Error: {e}")


    def _update_view_from_thread(self, payload):
        if self.view and self.polling_active: # Check polling_active to avoid updates after game ends but before view switches
            self.view.update_display(**payload)
        elif self.view and payload.get("game_over"): # Allow final game over update, even if polling_active turned false
             self.view.update_display(**payload)


    def _show_match_found_dialog_from_thread(self, opponent_name):
        if self.view:
            self.view.show_match_found_countdown(
                countdown_callback=self._signal_dialog_event_from_main_thread, # Changed callback
                opponent_name=opponent_name
            )

    def _signal_dialog_event_from_main_thread(self):
        """Called from the main thread (by dialog callback) to signal the worker thread."""
        print("[SP1v1Controller] Dialog callback executed in main thread. Setting event for worker.")
        if self.dialog_completion_event:
            self.dialog_completion_event.set()
        else:
            print("[SP1v1Controller] Warning: _signal_dialog_event_from_main_thread called but no event was set.")

    def _show_game_over_dialog_from_thread(self, result_text, game_status):
        if self.view:
            self.view.show_sp_game_over_dialog(
                result_text=result_text,
                on_ok_callback=self.handle_back_to_menu_from_sp_game # Or specific game over logic
            )

    def _determine_round_status_text(self, state: GameModule.GameStateDTO) -> str:
        if state.roundWinner:
            my_username = self.model.get_username()
            if state.roundWinner == my_username:
                return "You won this round!"
            elif state.roundWinner == "NONE" or not state.roundWinner : # "NONE" or empty means no one won (e.g. timeout for both)
                 return "Round over. No winner."
            else:
                return f"{state.roundWinner} won this round."
        return "Round over." # Default if no winner info

    def _determine_game_over_status_text(self, state: GameModule.GameStateDTO) -> str:
        if state.sessionResult == "WIN": return "🎉 You won the game! 🎉"
        elif state.sessionResult == "LOSE": return "You lost the game."
        elif state.sessionResult == "DRAW": return "The game is a draw."
        return f"Game over. Result: {state.sessionResult}" if state.sessionResult and state.sessionResult != "ONGOING" else "Game has ended."

    def handle_single_player_guess(self, letter_guessed: str):
        if not self.polling_active or not self.view: return

        current_state = self.model.get_game_state() # Get fresh state before guess
        if not current_state or current_state.roundOver == GameModule.BOOL_TRUE or current_state.gameOver == GameModule.BOOL_TRUE:
            print("[SP1v1Controller] Guess attempt when round/game is over.")
            return

        letter_lower = letter_guessed.lower()
        if letter_lower in self.attempted_letters_current_round:
            self.view.set_status(f"Letter '{letter_lower.upper()}\' already guessed this round.", "orange")
            return

        try:
            # Optimistically add to attempted_letters; server state is truth
            self.attempted_letters_current_round.add(letter_lower)
            
            is_correct = self.model.send_guess(letter_lower) # is_correct is a Python boolean (True/False)
            
            # Pass the Python boolean `is_correct` directly to feedback_guess.
            # The previous incorrect comparison (is_correct == GameModule.BOOL_TRUE) was causing the issue.
            self.view.feedback_guess(letter_guessed.upper(), is_correct)
            
            # Optionally, trigger a faster poll or wait for the natural poll cycle
            # For quicker feedback beyond button color, could fetch state again here, but might be complex.
            # Polling loop will refresh word, score, etc.

        except Exception as e:
            print(f"[SP1v1Controller] Error sending guess '{letter_lower}': {e}")
            self.signals.set_status_signal.emit(f"Error guessing: {e}", "red")
            # Remove from optimistic set if send failed
            if letter_lower in self.attempted_letters_current_round:
                 self.attempted_letters_current_round.remove(letter_lower)


    def handle_back_to_menu_from_sp_game(self):
        print("[SP1v1Controller] User requested back to Main Menu from 1v1 game.")
        self.stop_polling_and_cleanup_game() # This handles stopping poll and server cleanup
        if self.view: # Ensure view reference is valid
            self.view.main_window.show_view("MainMenu")
        else: # Fallback if view somehow became None
            print("[SP1v1Controller] View not available to navigate back to MainMenu.")
            # Potentially access main_window through a different path if needed, or log error.


# Need to import CORBA if it's used for exceptions like CORBA.COMM_FAILURE
try:
    from omniORB import CORBA
except ImportError:
    # Define a dummy CORBA object if omniORB is not available,
    # to prevent NameError if CORBA.COMM_FAILURE is caught.
    class CORBA:
        class COMM_FAILURE(Exception): pass
        class SystemException(Exception): pass # For other CORBA errors if needed 