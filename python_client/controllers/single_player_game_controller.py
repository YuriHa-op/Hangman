import threading
import time
import GameModule # For GameStateDTO, BOOL_TRUE, BOOL_FALSE
from .base_controller import BaseController

class SinglePlayerGameController(BaseController):
    def __init__(self, app_view, model):
        super().__init__(app_view, model)
        self.sp_polling_thread = None
        
        # Single-player game state attributes
        self.game_session_cleaned_up = False
        self.sp_client_timeout_sent_for_round = {}
        self._last_processed_server_round_for_word_clear = -1
        self.current_sp_server_round_processed_for_next_attempt = -1
        self.sp_attempted_letters = set()
        self.sp_current_word = ""
        self.sp_full_round_time = 15 # Default, will be fetched

    def on_show(self):
        # print("SinglePlayerGameController: on_show called")
        self.start_single_player_game()

    def on_hide(self):
        # print("SinglePlayerGameController: on_hide called")
        super().on_hide() # Calls self.stop_polling()
        sp_game_view = self.app_view.frames.get("SinglePlayerGame")
        if sp_game_view:
            # Close any specific dialogs if the view has them (e.g., match found, game over)
            if hasattr(sp_game_view, 'popup') and sp_game_view.popup and sp_game_view.popup.winfo_exists():
                sp_game_view.popup.destroy()
                sp_game_view.popup = None
            if hasattr(sp_game_view, 'game_over_popup') and sp_game_view.game_over_popup and sp_game_view.game_over_popup.winfo_exists():
                sp_game_view.game_over_popup.destroy()
                sp_game_view.game_over_popup = None

    def stop_polling(self):
        super().stop_polling() # Sets self.polling_active to False
        if self.sp_polling_thread and self.sp_polling_thread.is_alive():
            try:
                self.sp_polling_thread.join(timeout=0.5)
            except Exception as e:
                print(f"Error joining sp_polling_thread: {e}")
        self.sp_polling_thread = None
        # print("SinglePlayerGameController: Polling stopped and thread cleaned up.")

    def start_single_player_game(self):
        if self.polling_active:
            return
        # print("SinglePlayerGameController: Starting single player game.")
        self.polling_active = True
        sp_game_view = self.app_view.frames.get("SinglePlayerGame")
        if sp_game_view:
            sp_game_view.set_status("Starting game...")
        
        self.game_session_cleaned_up = False
        self.sp_client_timeout_sent_for_round.clear()
        self._last_processed_server_round_for_word_clear = -1
        self.current_sp_server_round_processed_for_next_attempt = -1
        self.sp_attempted_letters.clear()
        self.sp_current_word = ""

        if sp_game_view:
            self.app_view.after(0, lambda: sp_game_view.update_display(
                "_ _ _", "Time: --", "Incorrect: 0/5", 
                "", 0, 0, self.sp_attempted_letters, self.sp_current_word, 
                False, False
            ))
        
        self.sp_polling_thread = threading.Thread(target=self._initialize_and_poll_sp_game, daemon=True)
        self.sp_polling_thread.start()

    def _sp_match_dialog_finished_and_signal_ready(self):
        if self.model.get_username():
            try:
                self.model.player_ready_for_first_round()
            except Exception as e:
                print(f"SP Controller: Error signaling player ready: {e}")
        
        if self.polling_active: # Check if still active before starting new thread
            self.sp_polling_thread = threading.Thread(target=self._poll_sp_game_state_loop, daemon=True)
            self.sp_polling_thread.start()
        else:
            print("SP Controller: Polling became inactive before starting game state loop.")

    def _initialize_and_poll_sp_game(self):
        sp_game_view = self.app_view.frames.get("SinglePlayerGame")
        if not sp_game_view:
            self.polling_active = False
            return
        try:
            masked_word_init = self.model.start_game()
            try:
                self.sp_full_round_time = self.model.game_service.getRoundTime()
            except Exception as e:
                print(f"Error getting sp_full_round_time: {e}, defaulting to 15")
                self.sp_full_round_time = 15

            initial_state = self.model.get_game_state()
            if initial_state and hasattr(initial_state, 'actualWord') and initial_state.actualWord:
                 self.sp_current_word = initial_state.actualWord.upper()
            
            opponent_name = "Opponent"
            if initial_state and hasattr(initial_state, 'opponentUsername') and initial_state.opponentUsername:
                opponent_name = initial_state.opponentUsername

            if masked_word_init == 'WAITING_FOR_MATCH':
                self.app_view.after(0, lambda: sp_game_view.set_status("Waiting for match allocation..."))
                waiting_time = self.model.get_waiting_time()
                start_wait = time.time()
                while time.time() - start_wait < waiting_time:
                    if not self.polling_active: return
                    time.sleep(0.5)
                    current_masked_word = self.model.get_masked_word()
                    if current_masked_word != 'WAITING_FOR_MATCH' and current_masked_word:
                        masked_word_init = current_masked_word # Update if match found
                        break
                if masked_word_init == 'WAITING_FOR_MATCH' or not masked_word_init:
                    self.app_view.after(0, lambda: sp_game_view.set_status("No match found. Try again later."))
                    self.polling_active = False
                    if not self.game_session_cleaned_up:
                        try: self.model.end_game_session(); self.model.cleanup_player_session(); self.game_session_cleaned_up = True
                        except Exception as e: print(f"SP Init Error Cleanup: {e}")
                    self.sp_attempted_letters.clear(); self.sp_current_word = ""
                    return
            
            self.app_view.after(0, lambda: sp_game_view.show_match_found_countdown(self._sp_match_dialog_finished_and_signal_ready, opponent_name))

        except Exception as e:
            print(f"Error starting single player game: {e}")
            self.app_view.after(0, lambda: sp_game_view.set_status(f"Error: {e}", "red"))
            self.polling_active = False
            self.sp_attempted_letters.clear(); self.sp_current_word = ""
            # Ensure cleanup if initialization fails badly
            if not self.game_session_cleaned_up:
                try: self.model.end_game_session(); self.model.cleanup_player_session(); self.game_session_cleaned_up = True
                except Exception as clean_e: print(f"SP Init Hard Fail Cleanup Error: {clean_e}")

    def _poll_sp_game_state_loop(self):
        sp_game_view = self.app_view.frames.get("SinglePlayerGame")
        if not sp_game_view:
            self.polling_active = False; return

        while self.polling_active:
            try:
                state = self.model.get_game_state()
                if not state: # Could be due to CORBA error or session issue
                    self.app_view.after(0, lambda: sp_game_view.set_status("Error fetching game state. Returning to menu.", "red"))
                    self.polling_active = False
                    self.app_view.after(2000, lambda: self.show_frame("MainMenu"))
                    if not self.game_session_cleaned_up: # Ensure cleanup on critical error
                        try: self.model.end_game_session(); self.model.cleanup_player_session(); self.game_session_cleaned_up = True
                        except Exception as e: print(f"SP Poll Error Cleanup: {e}")
                    break

                server_current_round = state.currentRound
                status_text = ""
                timer_display_text = ""
                timer_color = "black"

                is_pre_first_round_awaiting_server_start = (
                    state.maskedWord != "WAITING_FOR_MATCH" and
                    state.roundOver == GameModule.BOOL_FALSE and
                    state.gameOver == GameModule.BOOL_FALSE and
                    hasattr(self, 'sp_full_round_time') and 
                    state.remainingTime == self.sp_full_round_time
                )

                if is_pre_first_round_awaiting_server_start:
                    timer_display_text = ""
                elif state.remainingTime <= 0:
                    timer_display_text = "Time left: 0s"; timer_color = "red"
                else:
                    timer_display_text = f"Time left: {state.remainingTime}s"
                    if state.remainingTime <= 5: timer_color = "red"
                    elif state.remainingTime <= 15: timer_color = "orange" # Changed from yellow for better visibility
                
                if state.remainingTime <= 0 and \
                   state.roundOver == GameModule.BOOL_FALSE and \
                   not self.sp_client_timeout_sent_for_round.get(server_current_round, False):
                    try: self.model.finish_round(0, False); self.sp_client_timeout_sent_for_round[server_current_round] = True
                    except Exception as e: print(f"SP: Error sending finish_round on timeout: {e}")

                if state.roundOver == GameModule.BOOL_TRUE:
                    status_text = self._determine_sp_round_status_text(state)
                    if state.gameOver == GameModule.BOOL_FALSE and state.sessionResult == "ONGOING":
                        if server_current_round > self.current_sp_server_round_processed_for_next_attempt:
                            if self.polling_active:
                                try: 
                                    new_round_started = self.model.start_new_round()
                                    self.current_sp_server_round_processed_for_next_attempt = server_current_round
                                    if new_round_started: status_text = "Starting next round..."
                                except Exception as e: print(f"SP: Error calling start_new_round: {e}")
                    self.app_view.after(0, lambda s=state, st=status_text, tdt=timer_display_text, tc=timer_color: sp_game_view.update_display(
                        s.maskedWord, tdt, f"Incorrect guesses: {s.incorrectGuesses}/5", st, 
                        s.playerWins, s.currentRound, self.sp_attempted_letters, self.sp_current_word, True, s.gameOver == GameModule.BOOL_TRUE, timer_color=tc))

                elif state.gameOver == GameModule.BOOL_TRUE or (state.sessionResult and state.sessionResult != "ONGOING"):
                    if not self.game_session_cleaned_up:
                        try: self.model.end_game_session(); self.model.cleanup_player_session(); self.game_session_cleaned_up = True
                        except Exception as e: print(f"SP Game Over Cleanup Error: {e}")
                    status_text = self._determine_sp_game_over_status_text(state)
                    self.polling_active = False 
                    self.app_view.after(0, lambda s=state, st=status_text, tdt=timer_display_text, tc=timer_color: sp_game_view.update_display(
                        s.maskedWord, tdt, f"Incorrect guesses: {s.incorrectGuesses}/5", st, 
                        s.playerWins, s.currentRound, self.sp_attempted_letters, self.sp_current_word, True, True, timer_color=tc))
                    dialog_result_text = "You Won!" if state.sessionResult == "WIN" else ("You Lost." if state.sessionResult == "LOSE" else f"Game Over: {state.sessionResult}")
                    self.app_view.after(100, lambda drt=dialog_result_text: sp_game_view.show_sp_game_over_dialog(drt, lambda: self.show_frame("MainMenu")))
                    break 

                else: # Round ongoing
                    if hasattr(state, 'actualWord') and state.actualWord and self.sp_current_word != state.actualWord.upper():
                        self.sp_current_word = state.actualWord.upper()
                    if server_current_round != self._last_processed_server_round_for_word_clear:
                         self.sp_attempted_letters.clear()
                         self.sp_client_timeout_sent_for_round.pop(server_current_round, None) 
                         self._last_processed_server_round_for_word_clear = server_current_round
                    status_text = "Guess the word!"
                    self.app_view.after(0, lambda s=state, st=status_text, tdt=timer_display_text, tc=timer_color: sp_game_view.update_display(
                        s.maskedWord, tdt, f"Incorrect guesses: {s.incorrectGuesses}/5", st, 
                        s.playerWins, s.currentRound, self.sp_attempted_letters, self.sp_current_word, False, False, timer_color=tc))
                
                if not self.polling_active: break
            except Exception as e:
                print(f"Error polling single player game state: {e}")
                import traceback; traceback.print_exc()
                self.app_view.after(0, lambda: sp_game_view.set_status("Error in game. Returning to menu.", "red"))
                self.polling_active = False
                self.app_view.after(2000, lambda: self.show_frame("MainMenu"))
                if not self.game_session_cleaned_up: # Ensure cleanup on critical error
                    try: self.model.end_game_session(); self.model.cleanup_player_session(); self.game_session_cleaned_up = True
                    except Exception as clean_e: print(f"SP Poll Hard Fail Cleanup Error: {clean_e}")
                break
            time.sleep(0.25)

    def _determine_sp_round_status_text(self, state: GameModule.GameStateDTO) -> str:
        if state.roundWinner:
            return "You won this round!" if state.roundWinner == self.model.get_username() else f"{state.roundWinner} won this round."
        return "Round over. No winner for this round."

    def _determine_sp_game_over_status_text(self, state: GameModule.GameStateDTO) -> str:
        if state.sessionResult == "WIN": return "🎉 You won the game! 🎉"
        elif state.sessionResult == "LOSE": return "You lost the game."
        return f"Game over. Result: {state.sessionResult}" if state.sessionResult and state.sessionResult != "ONGOING" else "Game has ended."

    def handle_single_player_guess(self, letter):
        if not self.polling_active: return
        sp_game_view = self.app_view.frames.get("SinglePlayerGame")
        if not sp_game_view: return
        try:
            is_correct = self.model.send_guess(letter.lower())
            self.sp_attempted_letters.add(letter.lower())
            self.app_view.after(0, lambda: sp_game_view.feedback_guess(letter, is_correct))
        except Exception as e:
            print(f"Error sending SP guess: {e}")
            self.app_view.after(0, lambda: sp_game_view.set_status(f"Error guessing: {e}", "red"))

    def handle_back_to_menu_from_sp_game(self):
        self.stop_polling()
        if not self.game_session_cleaned_up:
            try: 
                self.model.end_game_session()
                self.model.cleanup_player_session()
                self.game_session_cleaned_up = True
            except Exception as e:
                print(f"Error during back_to_menu cleanup from SP game: {e}")
        self.sp_attempted_letters.clear()
        self.sp_current_word = ""
        self.show_frame("MainMenu") 