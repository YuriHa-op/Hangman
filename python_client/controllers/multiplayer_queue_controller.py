import threading
import time
from .base_controller import BaseController

class MultiplayerQueueController(BaseController):
    def __init__(self, app_view, model):
        super().__init__(app_view, model)
        self.mp_queue_polling_thread = None

    def on_show(self):
        """Called when the MultiplayerQueueView is shown. Starts polling."""
        # print("MultiplayerQueueController: on_show called")
        self.start_multiplayer_queue_poll()

    def on_hide(self):
        """Called when the MultiplayerQueueView is hidden. Stops polling."""
        # print("MultiplayerQueueController: on_hide called")
        super().on_hide() # This will call self.stop_polling()
        # Ensure dialogs are closed if view is hidden abruptly
        queue_view = self.app_view.frames.get("MultiplayerQueue")
        if queue_view and hasattr(queue_view, 'close_no_match_found_dialog'):
            queue_view.close_no_match_found_dialog()
        # Consider closing match_found_dialog too if it can persist

    def stop_polling(self):
        """Stops the multiplayer queue polling thread."""
        super().stop_polling() # Sets self.polling_active to False
        if self.mp_queue_polling_thread and self.mp_queue_polling_thread.is_alive():
            try:
                self.mp_queue_polling_thread.join(timeout=0.5) # Wait briefly for thread to finish
            except Exception as e:
                print(f"Error joining mp_queue_polling_thread: {e}")
        self.mp_queue_polling_thread = None
        # print("MultiplayerQueueController: Polling stopped and thread cleaned up.")

    def start_multiplayer_queue_poll(self):
        if self.polling_active:
            # print("MultiplayerQueueController: Polling already active.")
            return
        # print("MultiplayerQueueController: Starting multiplayer queue poll.")
        self.polling_active = True
        try:
            self.model.start_multiplayer_game() # Join/start lobby in model
            self.mp_queue_polling_thread = threading.Thread(target=self._poll_mp_lobby_state, daemon=True)
            self.mp_queue_polling_thread.start()
        except Exception as e:
            print(f"Error starting multiplayer game/queue poll: {e}")
            self.polling_active = False
            # Optionally update view with error
            queue_view = self.app_view.frames.get("MultiplayerQueue")
            if queue_view:
                self.app_view.after(0, lambda: queue_view.update_queue_display("Error starting queue", ""))
            self.show_frame("MainMenu")

    def _poll_mp_lobby_state(self):
        queue_view = self.app_view.frames.get("MultiplayerQueue")
        if not queue_view:
            print("MultiplayerQueueController: QueueView not found. Stopping poll.")
            self.polling_active = False
            return

        # print("MultiplayerQueueController: Polling loop started.")
        while self.polling_active: # Rely on self.polling_active, set by on_hide/stop_polling
            try:
                lobby_state_data = self.model.get_multiplayer_lobby_state()
                
                players = self.model.get_lobby_players()
                max_players = self.model.get_lobby_max_players()
                creation_time_ms = self.model.get_lobby_creation_time()
                queue_time_s = self.model.get_lobby_queue_time_seconds()
                lobby_status = self.model.get_lobby_status_state()

                now_ms = int(time.time() * 1000)
                seconds_left = max(0, queue_time_s - int((now_ms - creation_time_ms) / 1000))
                
                self.app_view.after(0, lambda: queue_view.update_queue_display(
                    f"Time left: {seconds_left}",
                    f"{len(players)}/{max_players} players"
                ))

                if lobby_status == "STARTED" and seconds_left == 0:
                    self.polling_active = False 
                    self.app_view.after(0, lambda: queue_view.show_match_found_dialog(players, self._mp_queue_countdown_finished))
                    break 
                elif lobby_status == "NOMATCH" or (lobby_status == "WAITING" and seconds_left == 0):
                    self.polling_active = False
                    self.app_view.after(0, queue_view.show_no_match_found_dialog)
                    break

            except Exception as e:
                print(f"Error polling multiplayer lobby state: {e}")
                self.polling_active = False 
                self.app_view.after(0, self.show_frame, "MainMenu")
                break
            time.sleep(0.25) 
        
        # print(f"MultiplayerQueueController: Polling loop ended. Polling_active: {self.polling_active}")
        # if not self.polling_active: # This condition might be true if loop exited due to polling_active becoming false
            # The model.cleanup_player_session() should be called if polling stops *and* we are not transitioning to game
            # This is handled by cancel_multiplayer_queue and handle_no_match_found_dialog_ok explicitly.
            # If polling stopped because match was found, cleanup is not desired here.
            # If polling stopped due to error or hiding view before match, then cleanup handled by those paths.
            # Consider if cleanup is needed if poll stops due to internal error but not NOMATCH/timeout.
            # The original code had: if not self.polling_active: self.model.cleanup_player_session()
            # This could lead to premature cleanup if match was found. Let's be more specific.
            pass # Cleanup is handled by explicit actions like cancel or NOMATCH dialog OK.

    def _mp_queue_countdown_finished(self):
        # print("MultiplayerQueueController: Match found countdown finished.")
        if self.model.get_username():
            try:
                self.model.player_ready_for_first_round()
            except Exception as e:
                print(f"Error signaling player ready for first round: {e}")
        self.show_frame("MultiplayerGame") 

    def handle_no_match_found_dialog_ok(self):
        """Called when user clicks OK on the 'No Match Found' dialog."""
        # print("MultiplayerQueueController: No match found dialog OK'd.")
        try:
            self.model.cleanup_player_session()
        except Exception as e:
            print(f"Error cleaning up player session: {e}")
        self.show_frame("MainMenu")

    def cancel_multiplayer_queue(self):
        """Called when the user cancels the queue."""
        # print("MultiplayerQueueController: Cancelling multiplayer queue.")
        self.stop_polling() # This will set polling_active to False and join thread
        try:
            self.model.cleanup_player_session()
        except Exception as e:
            print(f"Error cleaning up player session on cancel: {e}")
        
        queue_view = self.app_view.frames.get("MultiplayerQueue")
        if queue_view and hasattr(queue_view, 'close_no_match_found_dialog'):
            queue_view.close_no_match_found_dialog()
        
        self.show_frame("MainMenu") 