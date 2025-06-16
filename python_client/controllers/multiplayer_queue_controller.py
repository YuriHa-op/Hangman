import time
from PyQt5.QtCore import QTimer
from .base_controller import BaseController

class MultiplayerQueueController(BaseController):
    def __init__(self, model, view):
        super().__init__(model, view)
        self.lobby_state_timer = QTimer()
        self.lobby_state_timer.timeout.connect(self.poll_lobby_state)
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.queue_end_time = 0
        self.total_queue_time = 30 # Default

    def on_show(self):
        self.view.clear_view()
        # Join or create a lobby on the server
        self.model.start_multiplayer_game()
        # Start polling for lobby state
        self.lobby_state_timer.start(1000) # Poll every 1 second
        self.poll_lobby_state() # Initial poll

    def on_hide(self):
        self.lobby_state_timer.stop()
        self.countdown_timer.stop()
        # Server should handle player removal from lobby on disconnect/logout
        # or if the lobby times out. No explicit leave_lobby call for now.

    def poll_lobby_state(self):
        lobby_state = self.model.get_multiplayer_lobby_state()
        if lobby_state:
            self.view.update_lobby_state(lobby_state)
            if lobby_state.get("state") == "STARTED":
                self.lobby_state_timer.stop()
                self.countdown_timer.stop()
                self.view.show_match_found_dialog()
                self.model.player_ready_for_first_round()
                self.view.main_window.show_view("MultiplayerGame")

            elif lobby_state.get('state') == 'NOMATCH':
                # Lobby was disbanded or player was removed
                self.lobby_state_timer.stop()
                self.countdown_timer.stop()
                self.view.show_no_match_dialog()

    def update_timer(self, creation_time_ms, queue_time_sec):
        self.total_queue_time = queue_time_sec
        self.queue_end_time = (creation_time_ms / 1000) + queue_time_sec
        if not self.countdown_timer.isActive():
            self.countdown_timer.start(1000) # Update countdown every second

    def update_countdown(self):
        now = time.time()
        remaining = int(self.queue_end_time - now)
        if remaining < 0:
            remaining = 0
        
        self.view.update_countdown(remaining, self.total_queue_time)

        if remaining <= 0 and self.lobby_state_timer.isActive():
            # Timer reached zero, polling should determine what happens next
            # (either game starts or lobby is disbanded).
            # The poll_lobby_state method handles this logic.
            pass

    def leave_lobby_and_go_back(self):
        self.on_hide()
        # NOTE: Server side doesn't have a clean "leave lobby" method.
        # The player will remain in the lobby until it starts or times out.
        # If they rejoin, the server should correctly place them back.
        self.view.main_window.show_view("MainMenu") 