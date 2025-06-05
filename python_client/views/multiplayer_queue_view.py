import tkinter as tk
# from tkinter import ttk # Not strictly needed by current MultiplayerQueueView, but good for consistency if dialogs evolve
from .base_view import BaseView

class MultiplayerQueueView(BaseView):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.queue_label = tk.Label(self, text="Queueing for Match...", font=("Arial", 20))
        self.queue_label.pack(pady=10)
        self.timer_label = tk.Label(self, text="Time left: --", font=("Arial", 16))
        self.timer_label.pack(pady=5)
        self.player_count_label = tk.Label(self, text="-/- players", font=("Arial", 16))
        self.player_count_label.pack(pady=5)
        self.cancel_button = tk.Button(self, text="Cancel", command=self.cancel_queue, font=("Arial", 14), bg="#d32f2f", fg="#fff")
        self.cancel_button.pack(pady=10)
        self.popup = None # To manage popups

    def on_show(self):
        self.update_queue_display("Time left: --", "-/- players") # Reset display
        self.controller.start_multiplayer_queue_poll()

    def update_queue_display(self, timer_text, player_count_text):
        self.timer_label.config(text=timer_text)
        self.player_count_label.config(text=player_count_text)

    def cancel_queue(self):
        self.controller.cancel_multiplayer_queue()

    def show_match_found_dialog(self, players, countdown_callback):
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
        self.popup = tk.Toplevel(self)
        self.popup.title("Match Found!")
        # Center the popup on the master window
        master_x = self.master.winfo_x()
        master_y = self.master.winfo_y()
        master_width = self.master.winfo_width()
        master_height = self.master.winfo_height()
        popup_width = 350  # Adjust as needed
        popup_height = 200 + (len(players) // 3) * 40 # Adjust height based on players
        pos_x = master_x + (master_width // 2) - (popup_width // 2)
        pos_y = master_y + (master_height // 2) - (popup_height // 2)
        self.popup.geometry(f"{popup_width}x{popup_height}+{pos_x}+{pos_y}")
        self.popup.resizable(False, False)
        self.popup.attributes("-topmost", True)

        tk.Label(self.popup, text="Match Found!", font=("Arial", 22), fg="#4CAF50").pack(pady=10)
        grid_frame = tk.Frame(self.popup)
        grid_frame.pack(pady=10)
        for idx, player in enumerate(players):
            row, col = divmod(idx, 3)
            lbl = tk.Label(grid_frame, text=player, font=("Arial", 16), bg="#222", fg="#fff", width=14, pady=5)
            lbl.grid(row=row, column=col, padx=5, pady=5)
        self.countdown_label_popup = tk.Label(self.popup, text="Game starts in 5", font=("Arial", 24), fg="#FFD600")
        self.countdown_label_popup.pack(pady=10)
        self.popup.grab_set() # Make it modal
        self.popup.update_idletasks() # Ensure window is drawn and centered before countdown
        self._start_countdown_in_popup(5, countdown_callback)

    def _start_countdown_in_popup(self, seconds, callback):
        if not (self.popup and self.popup.winfo_exists()): return
        if seconds > 0:
            self.countdown_label_popup.config(text=f"Game starts in {seconds}")
            self.popup.update()
            self.after(1000, lambda: self._start_countdown_in_popup(seconds - 1, callback))
        else:
            if self.popup and self.popup.winfo_exists(): 
                self.popup.grab_release()
                self.popup.destroy()
            self.popup = None
            callback() # Notify controller countdown finished

    def show_no_match_found_dialog(self):
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
        self.popup = tk.Toplevel(self)
        self.popup.title("No Match Found")
        # Center the popup
        master_x = self.master.winfo_x()
        master_y = self.master.winfo_y()
        master_width = self.master.winfo_width()
        master_height = self.master.winfo_height()
        popup_width = 300
        popup_height = 150
        pos_x = master_x + (master_width // 2) - (popup_width // 2)
        pos_y = master_y + (master_height // 2) - (popup_height // 2)
        self.popup.geometry(f"{popup_width}x{popup_height}+{pos_x}+{pos_y}")
        self.popup.resizable(False, False)
        self.popup.attributes("-topmost", True)

        tk.Label(self.popup, text="No Match Found", font=("Arial", 18), fg="#d32f2f").pack(pady=10)
        tk.Label(self.popup, text="No other players joined in time.\nPlease try again.", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.popup, text="OK", command=lambda: [
            self.popup.grab_release() if self.popup and self.popup.winfo_exists() else None,
            self.popup.destroy() if self.popup and self.popup.winfo_exists() else None, 
            setattr(self, 'popup', None), 
            self.controller.handle_no_match_found_dialog_ok()
        ]).pack(pady=10)
        self.popup.protocol("WM_DELETE_WINDOW", lambda: [
            self.popup.grab_release() if self.popup and self.popup.winfo_exists() else None,
            self.popup.destroy() if self.popup and self.popup.winfo_exists() else None, 
            setattr(self, 'popup', None), 
            self.controller.handle_no_match_found_dialog_ok()
        ])
        self.popup.grab_set() # Make it modal

    def close_no_match_found_dialog(self):
        if hasattr(self, 'popup') and self.popup and self.popup.winfo_exists():
            self.popup.grab_release()
            self.popup.destroy()
        self.popup = None 