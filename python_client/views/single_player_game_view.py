import tkinter as tk
from .base_view import BaseView

class SinglePlayerGameView(BaseView):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.word_var = tk.StringVar()
        self.timer_var = tk.StringVar()
        self.incorrect_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.score_var = tk.StringVar() # For Score: 0/3
        self.round_var = tk.StringVar() # For Round: 1/3
        self.keyboard_buttons = {}
        
        # Dialog management attributes
        self.popup = None # For match found countdown
        self.game_over_popup = None # For game over dialog

        tk.Label(self, text="1v1 Hangman Challenge", font=("Arial", 20)).pack(pady=10)
        
        top_info_frame = tk.Frame(self)
        top_info_frame.pack(pady=5)
        tk.Label(top_info_frame, textvariable=self.word_var, font=("Consolas", 32)).pack(side=tk.LEFT, padx=20)
        self.timer_label_widget = tk.Label(top_info_frame, textvariable=self.timer_var, font=("Arial", 18))
        self.timer_label_widget.pack(side=tk.LEFT, padx=20)

        stats_frame = tk.Frame(self)
        stats_frame.pack(pady=5)
        tk.Label(stats_frame, textvariable=self.round_var, font=("Arial", 16)).pack(side=tk.LEFT, padx=10)
        tk.Label(stats_frame, textvariable=self.score_var, font=("Arial", 16)).pack(side=tk.LEFT, padx=10)
        tk.Label(stats_frame, textvariable=self.incorrect_var, font=("Arial", 14)).pack(side=tk.LEFT, padx=10)
        
        self.status_display_label = tk.Label(self, textvariable=self.status_var, font=("Arial", 16), fg="blue")
        self.status_display_label.pack(pady=5)

        kb_frame = tk.Frame(self)
        kb_frame.pack(pady=10)
        for i, row in enumerate(["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]):
            row_frame = tk.Frame(kb_frame)
            row_frame.pack()
            for letter in row:
                btn = tk.Button(row_frame, text=letter, width=4, height=2,
                                command=lambda l=letter: self.controller.handle_single_player_guess(l))
                btn.pack(side=tk.LEFT, padx=2, pady=2)
                self.keyboard_buttons[letter] = btn

        tk.Button(self, text="Back to Menu", command=self.back_to_menu).pack(pady=10)

    def on_show(self):
        self.controller.start_single_player_game()
        # Ensure dialogs are closed if they were somehow left open from a previous session
        self._close_match_found_dialog()
        self._close_sp_game_over_dialog()

    def update_display(self, masked_word, timer_text, incorrect_text, status_text, player_wins, current_round_num, attempted_letters, current_word, round_over, game_over, timer_color="black"):
        self.word_var.set(masked_word)
        self.timer_var.set(timer_text)
        self.incorrect_var.set(incorrect_text)
        self.status_var.set(status_text)
        self.score_var.set(f"Score: {player_wins}/3") 
        self.round_var.set(f"Round: {current_round_num + 1}")
        if hasattr(self, 'timer_label_widget'):
            self.timer_label_widget.config(fg=timer_color)
        self.update_keyboard(attempted_letters, current_word, round_over or game_over)

    def update_keyboard(self, attempted_letters, current_word_upper, disable_all):
        for letter_button_char, btn_widget in self.keyboard_buttons.items():
            letter_lower = letter_button_char.lower()

            if letter_lower in attempted_letters:
                # This letter has been guessed.
                # feedback_guess has set its initial color and disabled it.
                # We only forcefully update its color if it's the end of the round/game (disable_all = True)
                # and the actual word is known, to ensure consistency.
                # Its state must remain DISABLED.
                if disable_all and current_word_upper:
                    final_bg_color = '#4CAF50' if letter_lower in current_word_upper.lower() else '#f44336'
                    btn_widget.config(bg=final_bg_color, state=tk.DISABLED)
                else:
                    # Mid-round, or end of round but word not yet available for this update.
                    # Color is already set by feedback_guess. Ensure it remains disabled.
                    if btn_widget['state'] != tk.DISABLED: # Safeguard, should already be disabled.
                        btn_widget.config(state=tk.DISABLED)
            else:
                # Letter not yet attempted.
                if disable_all:
                    btn_widget.config(state=tk.DISABLED, bg='SystemButtonFace')
                else:
                    btn_widget.config(state=tk.NORMAL, bg='SystemButtonFace')

    def feedback_guess(self, letter, is_correct):
        btn = self.keyboard_buttons[letter.upper()]
        btn.config(bg='#4CAF50' if is_correct else '#f44336')
        btn.config(state=tk.DISABLED)

    def set_status(self, message, color="blue"):
        self.status_var.set(message)
        if hasattr(self, 'status_display_label'):
            self.status_display_label.config(fg=color)

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

    def show_match_found_countdown(self, countdown_callback, opponent_name="Opponent"):
        self._close_match_found_dialog() # Close if already open
        self.popup = tk.Toplevel(self.master)
        self.popup.title("Match Found")
        popup_width = 400
        popup_height = 180
        self._center_popup(self.popup, popup_width, popup_height)

        tk.Label(self.popup, text=f"Match found! Your opponent: {opponent_name}", font=("Arial", 15)).pack(padx=20, pady=(10,5))
        tk.Label(self.popup, text="The game will start in...", font=("Arial", 14)).pack(pady=(0,5))
        self.countdown_label_popup = tk.Label(self.popup, text="5", font=("Arial", 32, "bold"))
        self.countdown_label_popup.pack(pady=5)
        # self.popup.update() # update_idletasks might be better before countdown
        self.popup.update_idletasks()
        self._start_countdown_in_popup(5, countdown_callback)

    def _start_countdown_in_popup(self, seconds, callback):
        if not (self.popup and self.popup.winfo_exists()): return
        if seconds > 0:
            self.countdown_label_popup.config(text=str(seconds))
            # self.popup.update() # Avoid too frequent updates if not needed
            self.after(1000, lambda: self._start_countdown_in_popup(seconds - 1, callback))
        else:
            self._close_match_found_dialog()
            callback() # Notify controller
            
    def _close_match_found_dialog(self):
        if self.popup and self.popup.winfo_exists():
            self.popup.grab_release()
            self.popup.destroy()
        self.popup = None

    def show_sp_game_over_dialog(self, result_text, on_ok_callback):
        self._close_sp_game_over_dialog() # Close if already open
        self.game_over_popup = tk.Toplevel(self.master)
        self.game_over_popup.title("Game Over")
        popup_width = 300
        popup_height = 150
        self._center_popup(self.game_over_popup, popup_width, popup_height)

        tk.Label(self.game_over_popup, text=result_text, font=("Arial", 18)).pack(pady=20)
        ok_button = tk.Button(self.game_over_popup, text="OK", command=lambda: [
            self._close_sp_game_over_dialog(),
            on_ok_callback()
        ], width=10)
        ok_button.pack(pady=10)
        self.game_over_popup.protocol("WM_DELETE_WINDOW", lambda: [
            self._close_sp_game_over_dialog(),
            on_ok_callback()
        ])

    def _close_sp_game_over_dialog(self):
        if self.game_over_popup and self.game_over_popup.winfo_exists():
            self.game_over_popup.grab_release()
            self.game_over_popup.destroy()
        self.game_over_popup = None

    def back_to_menu(self):
        self.controller.handle_back_to_menu_from_sp_game() 