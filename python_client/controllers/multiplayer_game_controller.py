import time
from PyQt5.QtCore import QTimer, QObject, QRunnable, QThreadPool, pyqtSignal
from .base_controller import BaseController

class WorkerSignals(QObject):
    guess_result = pyqtSignal(str, bool)

class GuessWorker(QRunnable):
    def __init__(self, model, letter):
        super().__init__()
        self.model = model
        self.letter = letter
        self.signals = WorkerSignals()

    def run(self):
        is_correct = self.model.send_multiplayer_guess(self.letter)
        self.signals.guess_result.emit(self.letter, is_correct)

class NextRoundWorker(QRunnable):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def run(self):
        self.model.start_multiplayer_next_round()

class MultiplayerGameController(BaseController):
    def __init__(self, model, view):
        super().__init__(model, view)
        self.game_state_timer = QTimer()
        self.game_state_timer.timeout.connect(self.poll_game_state)
        self.game_over = False
        self.is_between_rounds = False
        self.last_event_count = 0

        self.afk_pre_check_timer = QTimer()
        self.afk_pre_check_timer.setSingleShot(True)
        self.afk_pre_check_timer.timeout.connect(self._trigger_afk_dialog_if_conditions_met)
        
        self.round_at_afk_check_start = -1
        
        self.thread_pool = QThreadPool()

    def on_show(self):
        self.view.reset_view()
        self.game_over = False
        self.is_between_rounds = False
        self.round_at_afk_check_start = -1
        self.last_event_count = 0
        self.afk_pre_check_timer.stop()
        self.thread_pool.clear()
        
        self.game_state_timer.start(500)
        self.poll_game_state()

    def on_hide(self):
        self.game_state_timer.stop()
        self.afk_pre_check_timer.stop()
        self.view.close_all_dialogs()
        
        self.thread_pool.waitForDone(-1)
        self.thread_pool.clear()

    def poll_game_state(self):
        lobby_state = self.model.get_multiplayer_lobby_state()
        
        if not lobby_state or lobby_state.get('state') == 'NOMATCH':
            self.game_state_timer.stop()
            self.view.show_game_cleaned_up_dialog(on_ok_callback=self.forfeit_and_leave)
            return
            
        # If the lobby has started but the gameState object isn't there yet,
        # just wait for the next poll. Don't try to render a blank state.
        game_data = lobby_state.get("gameState", {})
        if lobby_state.get('state') == 'STARTED' and not game_data:
            print("[DEBUG] Lobby is STARTED but gameState is not yet available. Waiting for next poll.")
            return

        current_username = self.model.get_username()
        self.view.update_view_from_state(lobby_state, current_username)

        # Process Game Events for notifications
        game_events = game_data.get("gameEvents", [])
        if len(game_events) > self.last_event_count:
            new_events = game_events[self.last_event_count:]
            for event in new_events:
                # To avoid showing own leave message after returning to menu
                if current_username not in event:
                    self.view.display_game_event(event)
            self.last_event_count = len(game_events)
            
        game_winner = game_data.get("gameWinner", "")

        if game_winner and not self.game_over:
            self.game_over = True
            self.game_state_timer.stop()
            
            my_username = self.model.get_username()
            session_result = "WIN" if game_winner == my_username else "LOSE"
            game_id = self.model.get_mp_game_id()
            if game_id:
                self.model.set_last_game_id(game_id)

            # Restore the game over dialog before showing results
            self.view.show_game_over_dialog(session_result, on_ok_callback=self._navigate_to_results)
            return

        is_round_in_progress = game_data.get("roundInProgress", True)
        if not is_round_in_progress and not self.game_over and not self.is_between_rounds:
            self.is_between_rounds = True
            
            current_round = game_data.get("currentRound", -1)
            round_winner = game_data.get("roundWinner", "")

            if round_winner:
                QTimer.singleShot(3000, self.request_next_round)
                return

            finish_times = game_data.get("allPlayerFinishTimes", {})

            # If the round is over with no winner, check if ANYONE finished.
            # If the finish_times map is empty, it means no one successfully
            # completed the word or exhausted their guesses before a potential
            # global timeout. This is the definition of a stall.
            if not finish_times:
                # Stall condition / AFK check
                conditions_for_afk = (
                    not self.afk_pre_check_timer.isActive() and
                    not self.view.is_afk_dialog_showing()
                )
                if conditions_for_afk:
                    self.round_at_afk_check_start = current_round
                    self.afk_pre_check_timer.start(4000)
            else:
                # At least one person finished properly. The round is over.
                # Proceed to the next round.
                QTimer.singleShot(3000, self.request_next_round)

        if is_round_in_progress:
            self.is_between_rounds = False
            self.view.close_all_dialogs()

    def _trigger_afk_dialog_if_conditions_met(self):
        lobby_state = self.model.get_multiplayer_lobby_state()
        if not lobby_state: return
        
        game_data = lobby_state.get("gameState", {})
        is_round_in_progress = game_data.get("roundInProgress", True)
        current_round = game_data.get("currentRound", -1)

        if not is_round_in_progress and current_round == self.round_at_afk_check_start:
            self.view.show_afk_dialog()

    def _handle_afk_yes(self):
        self.view.close_afk_dialog()
        self.request_next_round()

    def _handle_afk_timeout(self):
        lobby_state = self.model.get_multiplayer_lobby_state()
        if not lobby_state:
            return

        game_data = lobby_state.get("gameState", {})
        is_round_in_progress = game_data.get("roundInProgress", True)
        game_winner = game_data.get("gameWinner", "")

        if not is_round_in_progress and not game_winner:
            QTimer.singleShot(0, self.view.show_last_chance_dialog)
        
    def _handle_last_chance_yes(self):
        self.view.close_last_chance_dialog()
        self.request_next_round()

    def _navigate_to_results(self):
        # Explicitly close and delete the dialog before hiding the view
        if hasattr(self.view, '_game_over_dialog') and self.view._game_over_dialog:
            self.view._game_over_dialog.hide()
            self.view._game_over_dialog.deleteLater()
            self.view._game_over_dialog = None
        self.on_hide()
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, lambda: self.view.main_window.show_view("MultiplayerGameResults"))

    def make_guess(self, letter):
        if not self.game_over and not self.is_between_rounds:
            self.view.virtual_keyboard.set_button_pending(letter)
            worker = GuessWorker(self.model, letter)
            worker.signals.guess_result.connect(self._handle_guess_result)
            self.thread_pool.start(worker)

    def _handle_guess_result(self, letter, is_correct):
        self.view.virtual_keyboard.update_button_color(letter, is_correct)

    def request_next_round(self):
        if not self.game_over:
            worker = NextRoundWorker(self.model)
            self.thread_pool.start(worker)

    def leave_game_and_go_back(self):
        self.model.leave_multiplayer_game()
        self.on_hide()
        self.view.main_window.show_view("MainMenu")

    def forfeit_and_leave(self):
        self.on_hide()
        self.view.main_window.show_view("MainMenu") 