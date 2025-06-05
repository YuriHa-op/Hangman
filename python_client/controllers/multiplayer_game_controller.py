import threading
import time
from .base_controller import BaseController

class MultiplayerGameController(BaseController):
    def __init__(self, app_view, model):
        super().__init__(app_view, model)
        self.mp_game_polling_thread = None
        self.spectating_player = None
        self.last_keyboard_state_mp = None
        
        # AFK related attributes
        self.afk_dialog_active = False
        self.afk_dialog_cooldown_until = 0
        self.AFK_DIALOG_COOLDOWN_SECONDS = 20 # Cooldown period for AFK dialog
        self.afk_pre_check_delay_active = False
        self.afk_pre_check_timer_id = None
        self.round_at_afk_check_start = -1

        # Multiplayer next round scheduling
        self.mp_next_round_timer_id = None
        self.mp_next_round_scheduled_for_round = -1

        # Helper for game state tracking within a poll cycle
        self._mp_game_was_ongoing = False 

    def on_show(self):
        # print("MultiplayerGameController: on_show called")
        self.start_multiplayer_game_poll()

    def on_hide(self):
        # print("MultiplayerGameController: on_hide called")
        super().on_hide() # Calls self.stop_polling()
        # Ensure dialogs are closed if view is hidden abruptly
        mp_game_view = self.app_view.frames.get("MultiplayerGame")
        if mp_game_view:
            if hasattr(mp_game_view, 'close_afk_dialog'): mp_game_view.close_afk_dialog()
            if hasattr(mp_game_view, 'close_last_chance_dialog'): mp_game_view.close_last_chance_dialog()
            if hasattr(mp_game_view, 'close_game_cleaned_up_dialog'): mp_game_view.close_game_cleaned_up_dialog()

    def stop_polling(self):
        super().stop_polling() # Sets self.polling_active to False
        if self.mp_game_polling_thread and self.mp_game_polling_thread.is_alive():
            try:
                self.mp_game_polling_thread.join(timeout=0.5)
            except Exception as e:
                print(f"Error joining mp_game_polling_thread: {e}")
        self.mp_game_polling_thread = None

        # Cancel any pending timers
        if self.afk_pre_check_timer_id: self.app_view.after_cancel(self.afk_pre_check_timer_id); self.afk_pre_check_timer_id = None
        if self.mp_next_round_timer_id: self.app_view.after_cancel(self.mp_next_round_timer_id); self.mp_next_round_timer_id = None
        
        self.afk_pre_check_delay_active = False
        # print("MultiplayerGameController: Polling stopped, thread and timers cleaned up.")

    def start_multiplayer_game_poll(self):
        if self.polling_active:
            return
        # print("MultiplayerGameController: Starting multiplayer game poll.")
        self.polling_active = True
        self.spectating_player = None 
        self.last_keyboard_state_mp = None 
        self._mp_game_was_ongoing = False # Reset for new game session view
        
        # Reset AFK state for a new game session view
        self.afk_dialog_active = False
        self.afk_pre_check_delay_active = False
        if self.afk_pre_check_timer_id: self.app_view.after_cancel(self.afk_pre_check_timer_id); self.afk_pre_check_timer_id = None
        self.round_at_afk_check_start = -1
        self.afk_dialog_cooldown_until = 0 # Reset cooldown

        # Reset next round timer state
        if self.mp_next_round_timer_id: self.app_view.after_cancel(self.mp_next_round_timer_id); self.mp_next_round_timer_id = None
        self.mp_next_round_scheduled_for_round = -1

        mp_game_view = self.app_view.frames.get("MultiplayerGame")
        if mp_game_view:
             mp_game_view.set_status("") # Clear status on new game start

        self.mp_game_polling_thread = threading.Thread(target=self._poll_mp_game_state, daemon=True)
        self.mp_game_polling_thread.start()

    def _poll_mp_game_state(self):
        mp_game_view = self.app_view.frames.get("MultiplayerGame")
        if not mp_game_view:
            print("MultiplayerGameController: MultiplayerGameView not found. Stopping poll.")
            self.polling_active = False
            return

        my_username = self.model.get_username()
        cleaned_up_session = False # Tracks if cleanupPlayerSession was called in this poll lifecycle

        while self.polling_active:
            try:
                previous_mp_game_was_ongoing = self._mp_game_was_ongoing
                _ = self.model.get_multiplayer_lobby_state() 

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
                player_finish_times_map = self.model.get_mp_player_finish_times()
                players = self.model.get_lobby_players()

                self._mp_game_was_ongoing = (lobby_status_current == "STARTED" or session_result_server == "ONGOING")

                if previous_mp_game_was_ongoing and lobby_status_current == "NOMATCH":
                    self.polling_active = False
                    if self.afk_pre_check_timer_id: self.app_view.after_cancel(self.afk_pre_check_timer_id); self.afk_pre_check_timer_id = None
                    self.app_view.after(0, mp_game_view.close_afk_dialog)
                    self.app_view.after(50, mp_game_view.close_last_chance_dialog)
                    self.app_view.after(200, lambda: mp_game_view.show_game_cleaned_up_dialog(on_ok_callback=lambda: self.show_frame("MainMenu")))
                    if not cleaned_up_session: 
                        try: 
                            self.model.cleanup_player_session()
                        except Exception: 
                            pass
                        cleaned_up_session = True
                    break 

                if not players and previous_mp_game_was_ongoing: 
                    self.polling_active = False
                    if self.afk_pre_check_timer_id: self.app_view.after_cancel(self.afk_pre_check_timer_id); self.afk_pre_check_timer_id = None
                    self.app_view.after(0, mp_game_view.close_afk_dialog)
                    self.app_view.after(50, mp_game_view.close_last_chance_dialog) 
                    self.app_view.after(200, lambda: mp_game_view.show_game_cleaned_up_dialog(on_ok_callback=lambda: self.show_frame("MainMenu")))
                    if not cleaned_up_session: 
                        try: 
                            self.model.cleanup_player_session()
                        except Exception: 
                            pass
                        cleaned_up_session = True
                    break 

                word_display = masked_words.get(self.spectating_player if self.spectating_player else my_username, "_ _ _")
                timer_display = f"Time left: {remaining_time}s"
                round_display = f"Round: {current_round_server + 1}"
                status_display = ""

                my_masked_word = masked_words.get(my_username, "")
                my_incorrect_guesses = incorrect_guesses_map.get(my_username, 0)
                my_player_is_done_this_round = (my_incorrect_guesses >= 5) or \
                                               (my_masked_word and "_" not in my_masked_word)

                if self.afk_pre_check_timer_id:
                    is_game_over_for_cancel = game_winner_server or (session_result_server not in ["ONGOING", None, ""])
                    is_new_round_started_for_cancel = round_in_progress_server and \
                                                    current_round_server != self.round_at_afk_check_start
                    if is_game_over_for_cancel or is_new_round_started_for_cancel:
                        self.app_view.after_cancel(self.afk_pre_check_timer_id)
                        self.afk_pre_check_timer_id = None
                        self.afk_pre_check_delay_active = False

                if self.spectating_player and self.spectating_player not in players: self.spectating_player = None 
                pov_username = self.spectating_player if self.spectating_player else my_username
                if self.spectating_player:
                    spectated_masked = masked_words.get(self.spectating_player, "")
                    spectated_incorrect = incorrect_guesses_map.get(self.spectating_player, 0)
                    if (spectated_incorrect >= 5) or (spectated_masked and "_" not in spectated_masked) or not round_in_progress_server:
                        self.spectating_player = None; pov_username = my_username 
                
                pov_is_done_guessing = (incorrect_guesses_map.get(pov_username, 0) >= 5) or (masked_words.get(pov_username, "") and "_" not in masked_words.get(pov_username, ""))
                can_truly_guess = (pov_username == my_username) and not self.spectating_player and round_in_progress_server and not game_winner_server and not my_player_is_done_this_round
                interaction_over_for_pov = bool(game_winner_server) or (not round_in_progress_server and pov_username == my_username) or (pov_username == my_username and my_player_is_done_this_round) or (self.spectating_player and pov_is_done_guessing)
                is_user_done_guessing_for_spectate_button = my_player_is_done_this_round or not round_in_progress_server

                if game_winner_server or (session_result_server not in ["ONGOING", None, ""]):
                    status_display = f"{game_winner_server} won the game." if game_winner_server else f"Game Over: {session_result_server}"
                    if game_winner_server == my_username: status_display = "🎉 You won the game! 🎉"
                    self.polling_active = False 
                    if self.afk_pre_check_timer_id: self.app_view.after_cancel(self.afk_pre_check_timer_id); self.afk_pre_check_timer_id = None
                    self.app_view.after(0, mp_game_view.close_afk_dialog); self.app_view.after(0, mp_game_view.close_last_chance_dialog)
                    if not cleaned_up_session: 
                        try: 
                            self.model.end_game_session()
                            self.model.cleanup_player_session()
                        except Exception: 
                            pass
                        cleaned_up_session = True
                
                elif round_in_progress_server: 
                    status_display = "Guess the word!"
                    if my_player_is_done_this_round: status_display = "Waiting for other players..."
                    if self.spectating_player: status_display = f"Spectating {self.spectating_player}"

                    if self.afk_dialog_active: self.app_view.after(0, mp_game_view.close_afk_dialog); self.afk_dialog_active = False
                    self.app_view.after(0, mp_game_view.close_last_chance_dialog)
                    if self.afk_pre_check_delay_active:
                        if self.afk_pre_check_timer_id: self.app_view.after_cancel(self.afk_pre_check_timer_id); self.afk_pre_check_timer_id = None
                        self.afk_pre_check_delay_active = False
                else: 
                    if round_winner_server:
                        status_display = f"{round_winner_server} won this round."
                        if round_winner_server == my_username: status_display = "You won this round!"
                        if self.afk_dialog_active: self.app_view.after(0, mp_game_view.close_afk_dialog); self.afk_dialog_active = False
                        self.app_view.after(0, mp_game_view.close_last_chance_dialog)
                        if self.afk_pre_check_delay_active: 
                            if self.afk_pre_check_timer_id: self.app_view.after_cancel(self.afk_pre_check_timer_id); self.afk_pre_check_timer_id = None
                            self.afk_pre_check_delay_active = False
                        if session_result_server == "ONGOING": 
                            self._schedule_next_round_attempt_mp(current_round_server)
                    else: 
                        status_display = "No one won this round."
                        if session_result_server == "ONGOING":
                            if player_finish_times_map: 
                                self._schedule_next_round_attempt_mp(current_round_server)
                        conditions_for_afk_initiation = (
                            not game_winner_server and session_result_server == "ONGOING" and
                            not self.afk_dialog_active and not self.afk_pre_check_delay_active and 
                            time.time() > self.afk_dialog_cooldown_until
                        )
                        if conditions_for_afk_initiation:
                            self.round_at_afk_check_start = current_round_server 
                            self.afk_pre_check_delay_active = True
                            if self.afk_pre_check_timer_id: self.app_view.after_cancel(self.afk_pre_check_timer_id)
                            self.afk_pre_check_timer_id = self.app_view.after(4000, self._trigger_first_afk_dialog_if_conditions_met)

                self.app_view.after(0, lambda pov_u=pov_username, p_guesses=dict(player_guesses_map), act_words=dict(all_current_words), c_truly_g=can_truly_guess, interact_o=interaction_over_for_pov, wd=word_display, td=timer_display, rd=round_display, sd=status_display, pl=list(players), sc=dict(scores), iudgfsb=is_user_done_guessing_for_spectate_button: 
                    mp_game_view.update_display(wd, td, rd, sd, pl, sc, pov_u, p_guesses, act_words, c_truly_g, iudgfsb, interact_o)
                )
                current_keyboard_state_tuple = (pov_username, frozenset(player_guesses_map.get(pov_username, [])), all_current_words.get(pov_username, ""), can_truly_guess, interaction_over_for_pov, current_round_server)
                if current_keyboard_state_tuple != self.last_keyboard_state_mp:
                     self.app_view.after(0, lambda pov_u=pov_username, p_guesses=dict(player_guesses_map), act_words=dict(all_current_words), c_truly_g=can_truly_guess, interact_o=interaction_over_for_pov: 
                        mp_game_view.update_keyboard(pov_u, p_guesses, act_words, c_truly_g, interact_o))
                     self.last_keyboard_state_mp = current_keyboard_state_tuple
                
                if not self.polling_active: break
            except Exception as e:
                print(f"Error in _poll_mp_game_state: {e}")
                import traceback; traceback.print_exc()
                self.polling_active = False
                if mp_game_view: 
                    self.app_view.after(0, lambda: mp_game_view.set_status("Error in game. Returning to menu.", "red"))
                    self.app_view.after(2000, lambda: self.show_frame("MainMenu")) 
                break 
            time.sleep(0.25)

        # Polling loop cleanup (already partially in stop_polling, but good for explicit exit from loop too)
        if self.afk_pre_check_timer_id: self.app_view.after_cancel(self.afk_pre_check_timer_id); self.afk_pre_check_timer_id = None
        self.afk_pre_check_delay_active = False
        if mp_game_view: 
            self.app_view.after(0, mp_game_view.close_afk_dialog)
            self.app_view.after(0, mp_game_view.close_last_chance_dialog)
            self.app_view.after(0, mp_game_view.close_game_cleaned_up_dialog)
        # self.mp_game_polling_thread = None # Done by stop_polling

    def handle_multiplayer_guess(self, letter):
        if self.spectating_player: return 
        if not self.polling_active: return 
        mp_game_view = self.app_view.frames.get("MultiplayerGame")
        try:
            self.model.send_multiplayer_guess(letter.lower())
        except Exception as e:
            if mp_game_view:
                self.app_view.after(0, lambda: mp_game_view.set_status(f"Error sending guess: {e}", "red"))

    def set_spectate_player(self, player_username):
        self.spectating_player = player_username
        self.last_keyboard_state_mp = None # Force keyboard refresh

    def handle_back_to_menu_from_mp_game(self):
        self.stop_polling() # This should handle thread and timer cleanup
        try:
            self.model.end_game_session()
            self.model.cleanup_player_session()
        except Exception as e:
            print(f"Error during back_to_menu cleanup from MP game: {e}")
        self.show_frame("MainMenu")

    def _handle_afk_yes(self):
        self.afk_dialog_active = False 
        mp_game_view = self.app_view.frames.get("MultiplayerGame")
        # View should close its own dialog immediately. Controller confirms state.
        if mp_game_view and hasattr(mp_game_view, 'is_afk_dialog_showing') and mp_game_view.is_afk_dialog_showing():
             self.app_view.after(0, mp_game_view.close_afk_dialog)
        self.afk_dialog_cooldown_until = time.time() + self.AFK_DIALOG_COOLDOWN_SECONDS
        try:
            self.model.start_multiplayer_next_round()
        except Exception as e:
            print(f"Error starting next round after AFK dialog: {e}")

    def _handle_afk_timeout(self):
        self.afk_dialog_active = False 
        mp_game_view = self.app_view.frames.get("MultiplayerGame")
        if mp_game_view and hasattr(mp_game_view, 'is_afk_dialog_showing') and mp_game_view.is_afk_dialog_showing():
            self.app_view.after(0, mp_game_view.close_afk_dialog)
        self.afk_dialog_cooldown_until = time.time() + self.AFK_DIALOG_COOLDOWN_SECONDS
        if mp_game_view and self.polling_active: # Only show last chance if still in game context
            self.app_view.after(0, lambda: mp_game_view.show_last_chance_dialog(
                on_last_chance_callback=self._handle_last_chance_yes
            ))

    def _trigger_first_afk_dialog_if_conditions_met(self):
        self.afk_pre_check_timer_id = None 
        self.afk_pre_check_delay_active = False
        mp_game_view = self.app_view.frames.get("MultiplayerGame")
        if not (self.polling_active and mp_game_view): return # Game ended or view changed

        current_server_round = self.model.get_mp_current_round()
        is_round_still_in_progress = self.model.is_mp_round_in_progress()
        current_game_winner = self.model.get_mp_game_winner()
        current_session_result = self.model.get_mp_session_result()

        if not current_game_winner and current_session_result == "ONGOING" and \
           self.round_at_afk_check_start == current_server_round and \
           not is_round_still_in_progress and \
           not self.afk_dialog_active and \
           time.time() > self.afk_dialog_cooldown_until:
            self.afk_dialog_active = True 
            self.app_view.after(0, lambda: mp_game_view.show_afk_dialog(
                on_yes_callback=self._handle_afk_yes,
                on_timeout_callback=self._handle_afk_timeout
            ))

    def _handle_last_chance_yes(self):
        try:
            self.model.start_multiplayer_next_round()
        except Exception as e:
            mp_game_view = self.app_view.frames.get("MultiplayerGame")
            if mp_game_view:
                 self.app_view.after(0, lambda err_e=e: mp_game_view.set_status(f"Error starting next round: {str(err_e)}", "red")) 

    def _schedule_next_round_attempt_mp(self, round_just_ended):
        if self.mp_next_round_scheduled_for_round == round_just_ended and self.mp_next_round_timer_id is not None:
            return
        if self.mp_next_round_timer_id: self.app_view.after_cancel(self.mp_next_round_timer_id)
        self.mp_next_round_scheduled_for_round = round_just_ended
        self.mp_next_round_timer_id = self.app_view.after(3000, self._execute_start_multiplayer_next_round)

    def _execute_start_multiplayer_next_round(self):
        self.mp_next_round_timer_id = None 
        if not self.polling_active or self.app_view.current_frame_name != "MultiplayerGame":
            return
        try:
            _ = self.model.get_multiplayer_lobby_state() 
            is_now_round_in_progress = self.model.is_mp_round_in_progress()
            game_is_over = self.model.get_mp_game_winner() or (self.model.get_mp_session_result() not in ["ONGOING", None, ""])
            if game_is_over: return
            if not is_now_round_in_progress:
                self.model.start_multiplayer_next_round()
        except Exception as e:
            print(f"Error in _execute_start_multiplayer_next_round: {e}") 