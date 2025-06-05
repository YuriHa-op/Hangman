import tkinter as tk
from PIL import Image, ImageTk
from .base_view import BaseView

class MultiplayerGameView(BaseView):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.word_var = tk.StringVar()
        self.timer_var = tk.StringVar()
        self.round_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.keyboard_buttons = {}

        tk.Label(self, text="Multiplayer Game", font=("Arial", 20)).pack(pady=5)
        tk.Label(self, textvariable=self.word_var, font=("Consolas", 28)).pack(pady=5)
        tk.Label(self, textvariable=self.timer_var, font=("Arial", 16)).pack(pady=2)
        tk.Label(self, textvariable=self.round_var, font=("Arial", 12)).pack(pady=2)
        
        self.scores_panel = tk.Frame(self)
        self.scores_panel.pack(pady=5)

        self.status_display_label = tk.Label(self, textvariable=self.status_var, font=("Arial", 14), fg="green")
        self.status_display_label.pack(pady=2)

        kb_frame = tk.Frame(self)
        kb_frame.pack(pady=10)
        for i, row in enumerate(["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]):
            row_frame = tk.Frame(kb_frame)
            row_frame.pack()
            for letter in row:
                btn = tk.Button(row_frame, text=letter, width=3, height=1, font=("Arial", 10),
                                command=lambda l=letter: self.controller.handle_multiplayer_guess(l))
                btn.pack(side=tk.LEFT, padx=1, pady=1)
                self.keyboard_buttons[letter] = btn

        tk.Button(self, text="Back to Menu", command=self.back_to_menu).pack(pady=10)

        try:
            # Ensure eye.png is in a known location, e.g., an 'assets' folder or same directory
            # For simplicity, assuming it's in the same directory as app.py or a relative path from there.
            # A more robust solution would use absolute paths or a resource management system.
            self.eye_img = Image.open("eye.png").resize((16, 16)) # Consider path carefully
            self.eye_tk = ImageTk.PhotoImage(self.eye_img)
        except FileNotFoundError:
            print("Error: eye.png not found. Ensure it is in the correct path.")
            self.eye_tk = None # Fallback if image not found
        except Exception as e:
            print(f"Error loading eye.png: {e}")
            self.eye_tk = None
        
        # Attributes for dialogs to ensure they are managed correctly
        self.afk_popup = None
        self.last_chance_popup = None
        self.cleanup_popup = None
        self.afk_timer_id = None

    def on_show(self):
        self.set_status("")
        self.controller.start_multiplayer_game_poll()
        self.close_afk_dialog() 
        self.close_last_chance_dialog()
        self.close_game_cleaned_up_dialog()

    def update_display(self, word, timer, round_text, status, players, scores, pov_username, guesses_map, actual_words_map, can_truly_guess, is_user_done_guessing_for_spectate, interaction_over_for_pov):
        self.word_var.set(word)
        self.timer_var.set(timer)
        self.round_var.set(round_text)
        self.status_var.set(status)
        self.update_scores_panel(players, scores, pov_username, is_user_done_guessing_for_spectate)
        self.update_keyboard(pov_username, guesses_map, actual_words_map, can_truly_guess, interaction_over_for_pov)

    def update_scores_panel(self, players, scores, pov_username, is_user_done_guessing_for_self):
        for widget in self.scores_panel.winfo_children():
            widget.destroy()

        for player in players:
            player_frame = tk.Frame(self.scores_panel)
            player_frame.pack(side=tk.LEFT, padx=3)
            
            score_text = f"{player}:{scores.get(player, 0)}"
            is_current_user = (player == self.master.get_username()) # master is HangmanApp

            if is_current_user and pov_username == player: # It's me, and I am viewing myself
                score_label_text = f"> {score_text} <"
            elif pov_username == player: # I am spectating this player
                score_label_text = f"Spectating: {score_text}"
            else: # Other player, not currently spectated by me
                score_label_text = score_text
            
            tk.Label(player_frame, text=score_label_text, font=("Arial", 10)).pack(side=tk.LEFT)

            if self.eye_tk and not is_current_user and is_user_done_guessing_for_self:
                spectate_btn = tk.Button(player_frame, image=self.eye_tk, 
                                         command=lambda p=player: self.controller.set_spectate_player(p),
                                         borderwidth=0, width=18, height=18)
                spectate_btn.pack(side=tk.LEFT, padx=2)
            elif is_current_user and pov_username != player and is_user_done_guessing_for_self:
                return_btn = tk.Button(player_frame, text="My View", 
                                       command=lambda: self.controller.set_spectate_player(None),
                                       font=("Arial", 8), width=7, height=1)
                return_btn.pack(side=tk.LEFT, padx=2)

    def update_keyboard(self, pov_username, guesses_map, actual_words_map, can_truly_guess, interaction_over_for_pov):
        pov_guesses = set(guesses_map.get(pov_username, []))
        pov_actual_word = actual_words_map.get(pov_username, "").upper()
        current_user_is_pov = (pov_username == self.master.get_username()) # master is HangmanApp

        for letter_button_char, btn_widget in self.keyboard_buttons.items():
            letter_lower = letter_button_char.lower()
            bg_color = 'SystemButtonFace' # Default
            btn_state = tk.DISABLED # Default to disabled

            if interaction_over_for_pov:
                if letter_lower in pov_guesses:
                    if pov_actual_word and letter_lower in pov_actual_word.lower(): bg_color = '#4CAF50'  # Green
                    elif pov_actual_word: bg_color = '#f44336'  # Red
            elif letter_lower in pov_guesses:
                if pov_actual_word and letter_lower in pov_actual_word.lower(): bg_color = '#4CAF50'  # Green
                elif pov_actual_word: bg_color = '#f44336'  # Red
            else: # Letter not yet guessed by POV, round active for POV
                if can_truly_guess and current_user_is_pov:
                    btn_state = tk.NORMAL
            
            btn_widget.config(state=btn_state, bg=bg_color)
    
    def set_status(self, message, color="green"):
        self.status_var.set(message)
        if hasattr(self, 'status_display_label'):
            self.status_display_label.config(fg=color)

    def back_to_menu(self):
        self.controller.handle_back_to_menu_from_mp_game()

    def _center_popup(self, popup_window, width, height):
        master_x = self.master.winfo_x()
        master_y = self.master.winfo_y()
        master_width = self.master.winfo_width()
        master_height = self.master.winfo_height()
        pos_x = master_x + (master_width // 2) - (width // 2)
        pos_y = master_y + (master_height // 2) - (height // 2)
        popup_window.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
        popup_window.resizable(False, False)
        popup_window.attributes("-topmost", True)
        popup_window.grab_set()

    def show_afk_dialog(self, on_yes_callback, on_timeout_callback, countdown_seconds=10):
        if self.afk_popup and self.afk_popup.winfo_exists(): return
        if self.last_chance_popup and self.last_chance_popup.winfo_exists(): self.close_last_chance_dialog()

        self.afk_popup = tk.Toplevel(self.master)
        self.afk_popup.title("Still There?")
        self._center_popup(self.afk_popup, 300, 150)

        tk.Label(self.afk_popup, text="Are you still in the game?", font=("Arial", 14)).pack(pady=10)
        self.afk_countdown_label = tk.Label(self.afk_popup, text=f"Closing in: {countdown_seconds}s", font=("Arial", 12))
        self.afk_countdown_label.pack(pady=5)

        self.afk_yes_button = tk.Button(self.afk_popup, text="Yes, I'm here!", command=lambda: [
            self.afk_yes_button.config(state=tk.DISABLED, text="Processing..."),
            on_yes_callback()
        ])
        self.afk_yes_button.pack(pady=10)

        self.afk_popup.protocol("WM_DELETE_WINDOW", lambda: [on_timeout_callback(), self.close_afk_dialog(was_closed_by_user=True)])
        self._afk_dialog_countdown_timer(countdown_seconds, on_timeout_callback)

    def _afk_dialog_countdown_timer(self, seconds_left, on_timeout_callback):
        if not (self.afk_popup and self.afk_popup.winfo_exists()): return
        if seconds_left > 0:
            if self.afk_countdown_label and self.afk_countdown_label.winfo_exists():
                self.afk_countdown_label.config(text=f"Closing in: {seconds_left}s")
            if self.afk_timer_id: self.master.after_cancel(self.afk_timer_id)
            self.afk_timer_id = self.master.after(1000, lambda: self._afk_dialog_countdown_timer(seconds_left - 1, on_timeout_callback))
        else:
            if self.afk_countdown_label and self.afk_countdown_label.winfo_exists():
                self.afk_countdown_label.config(text="Timer expired. Still here?")
            if self.afk_yes_button and self.afk_yes_button.winfo_exists():
                self.afk_yes_button.config(text="Try Next Round?", state=tk.NORMAL)
            if on_timeout_callback: on_timeout_callback()

    def close_afk_dialog(self, was_closed_by_user=False): # Removed unused was_answered, was_timed_out
        if self.afk_timer_id: self.master.after_cancel(self.afk_timer_id); self.afk_timer_id = None
        if self.afk_popup and self.afk_popup.winfo_exists():
            self.afk_popup.grab_release()
            self.afk_popup.destroy()
        self.afk_popup = None 
        self.afk_countdown_label = None # Clear refs
        self.afk_yes_button = None    # Clear refs

    def is_afk_dialog_showing(self):
        return self.afk_popup and self.afk_popup.winfo_exists()

    def show_game_cleaned_up_dialog(self, on_ok_callback):
        if self.cleanup_popup and self.cleanup_popup.winfo_exists(): return
        if self.afk_popup and self.afk_popup.winfo_exists(): self.close_afk_dialog()
        if self.last_chance_popup and self.last_chance_popup.winfo_exists(): self.close_last_chance_dialog()

        self.cleanup_popup = tk.Toplevel(self.master)
        self.cleanup_popup.title("Game Over")
        self._center_popup(self.cleanup_popup, 350, 150)

        tk.Label(self.cleanup_popup, text="The game session was closed\ndue to inactivity or server cleanup.", font=("Arial", 13)).pack(pady=20)
        ok_button = tk.Button(self.cleanup_popup, text="OK", command=lambda: [self.close_game_cleaned_up_dialog(), on_ok_callback()])
        ok_button.pack(pady=10)
        self.cleanup_popup.protocol("WM_DELETE_WINDOW", lambda: [self.close_game_cleaned_up_dialog(), on_ok_callback()])

    def close_game_cleaned_up_dialog(self):
        if self.cleanup_popup and self.cleanup_popup.winfo_exists():
            self.cleanup_popup.grab_release()
            self.cleanup_popup.destroy()
        self.cleanup_popup = None

    def show_last_chance_dialog(self, on_last_chance_callback):
        if self.last_chance_popup and self.last_chance_popup.winfo_exists(): return
        if self.afk_popup and self.afk_popup.winfo_exists(): self.close_afk_dialog()

        self.last_chance_popup = tk.Toplevel(self.master)
        self.last_chance_popup.title("Game Stalled")
        self._center_popup(self.last_chance_popup, 380, 180)

        msg_label = tk.Label(self.last_chance_popup, 
                             text="Server may be cleaning up the game due to inactivity.", 
                             font=("Arial", 12), wraplength=340)
        msg_label.pack(pady=(20, 10))
        last_chance_button = tk.Button(self.last_chance_popup, text="Try Next Round (Last Chance)", 
                                       font=("Arial", 12, "bold"), bg="#e67e22", fg="white",
                                       command=lambda: [self.close_last_chance_dialog(), on_last_chance_callback()])
        last_chance_button.pack(pady=10)
        self.last_chance_popup.protocol("WM_DELETE_WINDOW", self.close_last_chance_dialog)

    def close_last_chance_dialog(self):
        if self.last_chance_popup and self.last_chance_popup.winfo_exists():
            self.last_chance_popup.grab_release()
            self.last_chance_popup.destroy()
        self.last_chance_popup = None 