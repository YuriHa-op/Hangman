import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import time
import json # Added for show_match_found_dialog and show_details in MatchHistory
from datetime import datetime # Added for timestamp formatting

class BaseView(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.master = master # This is the HangmanApp (root Tk window)
        self.controller = controller

    def on_show(self):
        # Called when the frame is raised
        pass

class HangmanApp(tk.Tk): # This will be the main application window
    def __init__(self, controller):
        super().__init__()
        self.title("Hangman - Python Client")
        self.geometry("800x600")
        self.controller = controller
        self.frames = {}

        # The controller will tell HangmanApp which frames to initialize and show

    def add_frame(self, FrameClass, frame_name):
        frame = FrameClass(self, self.controller) # Pass controller to each frame
        self.frames[frame_name] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        return frame

    def show_frame(self, frame_name):
        frame = self.frames[frame_name]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show() # Call on_show if it exists

    def get_username(self):
        # Delegate to controller, which gets it from model
        return self.controller.get_username()

    def run(self):
        self.mainloop()

class LoginView(BaseView):
    def __init__(self, master, controller):
        super().__init__(master, controller)

        tk.Label(self, text="Login or Create Account", font=("Arial", 20)).pack(pady=20)

        tk.Label(self, text="Username:").pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()

        tk.Label(self, text="Password:").pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()

        tk.Button(self, text="Login", command=self.login).pack(pady=10)
        tk.Button(self, text="Create Account", command=self.create_account).pack(pady=5)
        tk.Button(self, text="Exit", command=self.exit_app).pack(pady=5)

        self.status_label = tk.Label(self, text="", fg="red")
        self.status_label.pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.controller.handle_login(username, password)

    def create_account(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.controller.handle_create_account(username, password)

    def set_status(self, message, color="red"):
        self.status_label.config(text=message, fg=color)

    def clear_entries(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def exit_app(self):
        self.controller.handle_exit()

class MainMenuView(BaseView):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        # Username will be set by on_show
        self.welcome_label = tk.Label(self, text="", font=("Arial", 24))
        self.welcome_label.pack(pady=20)

        tk.Button(self, text="Single Player", command=lambda: self.controller.show_frame("SinglePlayerGame")).pack(pady=10)
        tk.Button(self, text="Multiplayer", command=lambda: self.controller.show_frame("MultiplayerQueue")).pack(pady=10)
        tk.Button(self, text="Match History", command=lambda: self.controller.show_frame("MatchHistory")).pack(pady=10)
        tk.Button(self, text="Leaderboard", command=lambda: self.controller.show_frame("Leaderboard")).pack(pady=10)
        tk.Button(self, text="Logout", command=self.logout).pack(pady=10)

    def on_show(self):
        username = self.master.get_username() # Get username via HangmanApp -> Controller -> Model
        self.welcome_label.config(text=f"Welcome, {username}!")

    def logout(self):
        self.controller.handle_logout()

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
        tk.Label(self.popup, text="Match Found!", font=("Arial", 22), fg="#4CAF50").pack(pady=10)
        grid_frame = tk.Frame(self.popup)
        grid_frame.pack(pady=10)
        for idx, player in enumerate(players):
            row, col = divmod(idx, 3)
            lbl = tk.Label(grid_frame, text=player, font=("Arial", 16), bg="#222", fg="#fff", width=14, pady=5)
            lbl.grid(row=row, column=col, padx=5, pady=5)
        self.countdown_label_popup = tk.Label(self.popup, text="Game starts in 5", font=("Arial", 24), fg="#FFD600")
        self.countdown_label_popup.pack(pady=10)
        self.popup.update()
        self._start_countdown_in_popup(5, countdown_callback)

    def _start_countdown_in_popup(self, seconds, callback):
        if not (self.popup and self.popup.winfo_exists()): return
        if seconds > 0:
            self.countdown_label_popup.config(text=f"Game starts in {seconds}")
            self.popup.update()
            self.after(1000, lambda: self._start_countdown_in_popup(seconds - 1, callback))
        else:
            if self.popup and self.popup.winfo_exists(): self.popup.destroy()
            self.popup = None
            callback() # Notify controller countdown finished

    def show_no_match_found_dialog(self):
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
        self.popup = tk.Toplevel(self)
        self.popup.title("No Match Found")
        tk.Label(self.popup, text="No Match Found", font=("Arial", 18), fg="#d32f2f").pack(pady=10)
        tk.Label(self.popup, text="No other players joined in time.\nPlease try again.", font=("Arial", 14)).pack(pady=10)
        # The controller will handle going back to menu after this dialog is closed by the user.
        tk.Button(self.popup, text="OK", command=lambda: [
            self.popup.destroy(), 
            setattr(self, 'popup', None), # Ensure popup attribute is cleared
            self.controller.handle_no_match_found_dialog_ok()
        ]).pack(pady=10)

    def close_no_match_found_dialog(self):
        if hasattr(self, 'popup') and self.popup and self.popup.winfo_exists():
            self.popup.destroy()
        self.popup = None

class MatchHistoryView(BaseView):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        tk.Label(self, text="Match History", font=("Arial", 20)).pack(pady=10)

        # Frame for mode selection
        mode_frame = tk.Frame(self)
        mode_frame.pack(pady=5)
        tk.Label(mode_frame, text="Select History Type:").pack(side=tk.LEFT, padx=5)
        self.history_type_var = tk.StringVar()
        self.history_type_combo = ttk.Combobox(mode_frame, textvariable=self.history_type_var,
                                               values=["Multiplayer Matches", "1v1 Matches"],
                                               state="readonly")
        self.history_type_combo.pack(side=tk.LEFT)
        self.history_type_combo.bind("<<ComboboxSelected>>", self.on_history_type_change)
        self.history_type_combo.set("Multiplayer Matches") # Default selection

        self.tree = ttk.Treeview(self, columns=("Date/Time", "Players", "Winner", "Rounds"), show="headings")
        self.tree.heading("Date/Time", text="Date/Time")
        self.tree.column("Date/Time", width=150, anchor="w")
        self.tree.heading("Players", text="Players")
        self.tree.column("Players", width=200, anchor="w")
        self.tree.heading("Winner", text="Winner")
        self.tree.column("Winner", width=100, anchor="center")
        self.tree.heading("Rounds", text="Rounds")
        self.tree.column("Rounds", width=80, anchor="center")
        self.tree.pack(expand=True, fill="both")
        tk.Button(self, text="Back to Menu", command=lambda: self.controller.show_frame("MainMenu")).pack(pady=10)
        self.tree.bind("<Double-1>", self.on_item_double_click)

    def on_show(self):
        # Load history based on current combobox selection (or default if first time)
        self.load_selected_history()

    def on_history_type_change(self, event=None):
        self.load_selected_history()

    def load_selected_history(self):
        selected_type = self.history_type_var.get()
        mode = 'singleplayer' if selected_type == "1v1 Matches" else 'multiplayer'
        self.controller.load_match_history(mode)

    def display_match_history(self, games_data, mode): # Mode passed to confirm what was loaded
        self.tree.delete(*self.tree.get_children()) # Clear existing items
        games = json.loads(games_data)
        for game in games:
            game_id = game.get("gameId", "N/A")
            timestamp_ms = game.get("gameEndTime", 0) # Expecting milliseconds
            dt_object = "N/A"
            if timestamp_ms > 0:
                try:
                    # Convert milliseconds to seconds for datetime.fromtimestamp
                    dt_object = datetime.fromtimestamp(timestamp_ms / 1000).strftime("%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    print(f"Error formatting timestamp {timestamp_ms}: {e}")
                    dt_object = "Invalid Date"
            
            # gameId is used as iid (internal item id)
            self.tree.insert("", "end", iid=game_id, values=(
                dt_object,
                ", ".join(game.get("players", [])),
                game.get("overallWinner", "N/A"),
                game.get("totalRounds", "N/A")
            ))

    def on_item_double_click(self, event):
        selected_item_iid = self.tree.selection()
        if not selected_item_iid: return
        game_id = selected_item_iid[0] # game_id is the iid
        if game_id and game_id != "N/A": # Ensure game_id is valid
            selected_type = self.history_type_var.get()
            mode = 'singleplayer' if selected_type == "1v1 Matches" else 'multiplayer'
            self.controller.show_match_details(game_id, mode)

    def show_details_popup(self, details_data):
        details = json.loads(details_data)
        msg = f"Game ID: {details.get('gameId', 'N/A')}\nWinner: {details.get('overallWinner', 'N/A')}\nPlayers: {', '.join(details.get('players', []))}\nRounds:\n"
        for rnd in details.get("rounds", []):
            msg += f"  Round {rnd.get('roundNumber', '?')}: Word='{rnd.get('word', 'N/A')}', Winner={rnd.get('winner', 'N/A')}\n"
        messagebox.showinfo("Match Details", msg, parent=self) # Ensure popup is child of this frame

class MultiplayerGameView(BaseView):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.word_var = tk.StringVar()
        self.timer_var = tk.StringVar()
        self.round_var = tk.StringVar()
        self.status_var = tk.StringVar()
        # self.scores_var = tk.StringVar() # Scores will be in a dedicated frame
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
            # Ensure eye.png is in the same directory or provide a full path
            self.eye_img = Image.open("eye.png").resize((16, 16))
            self.eye_tk = ImageTk.PhotoImage(self.eye_img)
        except Exception as e:
            print(f"Error loading eye.png: {e}")
            self.eye_tk = None

    def on_show(self):
        self.set_status("")
        self.controller.start_multiplayer_game_poll()
        self.close_afk_dialog() # Ensure any lingering dialog is closed on show

    def update_display(self, word, timer, round_text, status, players, scores, pov_username, guesses_map, actual_words_map, can_truly_guess, is_user_done_guessing_for_spectate, interaction_over_for_pov):
        self.word_var.set(word)
        self.timer_var.set(timer)
        self.round_var.set(round_text)
        self.status_var.set(status)
        self.update_scores_panel(players, scores, pov_username, True, is_user_done_guessing_for_spectate) # can_guess_for_self is simplified here
        self.update_keyboard(pov_username, guesses_map, actual_words_map, can_truly_guess, interaction_over_for_pov)

    def update_scores_panel(self, players, scores, pov_username, can_guess_for_self, is_user_done_guessing_for_self):
        for widget in self.scores_panel.winfo_children():
            widget.destroy()
        
        # Determine if the current user can spectate (i.e., their own game part is over)
        # This logic might be better handled in the controller and passed as a boolean.
        # For now, we use is_user_done_guessing_for_self

        for player in players:
            player_frame = tk.Frame(self.scores_panel)
            player_frame.pack(side=tk.LEFT, padx=3)
            
            score_text = f"{player}:{scores.get(player, 0)}"
            if player == pov_username and player == self.master.get_username(): # Your own view, not spectating
                score_text = f"> {score_text} <" # Indicate current POV if it's you
            elif player == pov_username: # Spectating this player
                 score_text = f"Spectating: {score_text}"

            tk.Label(player_frame, text=score_text, font=("Arial", 10)).pack(side=tk.LEFT)

            # Add spectate button if it's not the user themselves and user is done/can spectate
            if self.eye_tk and player != self.master.get_username() and is_user_done_guessing_for_self:
                spectate_btn = tk.Button(player_frame, image=self.eye_tk, 
                                         command=lambda p=player: self.controller.set_spectate_player(p),
                                         borderwidth=0, width=18, height=18)
                spectate_btn.pack(side=tk.LEFT, padx=2)
            elif player == self.master.get_username() and pov_username != self.master.get_username() and is_user_done_guessing_for_self:
                 # If user is spectating someone else, show button to return to self view
                return_btn = tk.Button(player_frame, text="My View", 
                                       command=lambda: self.controller.set_spectate_player(None),
                                       font=("Arial", 8), width=7)
                return_btn.pack(side=tk.LEFT, padx=2)

    def update_keyboard(self, pov_username, guesses_map, actual_words_map, can_truly_guess, interaction_over_for_pov):
        # pov_username: The player whose perspective we're viewing.
        # guesses_map: {player_name: [list of guessed letters]}
        # actual_words_map: {player_name: "ACTUALWORD"}
        # can_truly_guess: Boolean, True if the *user* (not necessarily POV) can make a guess for their own word.
        # interaction_over_for_pov: Boolean, True if game/round is over for POV, or POV finished their word/guesses.

        pov_guesses = set(guesses_map.get(pov_username, []))
        pov_actual_word = actual_words_map.get(pov_username, "").upper()

        for letter_button_char, btn_widget in self.keyboard_buttons.items():
            letter_lower = letter_button_char.lower()

            if interaction_over_for_pov: # Game/round over for POV, or POV is done
                btn_widget.config(state=tk.DISABLED)
                if letter_lower in pov_guesses:
                    if pov_actual_word and letter_lower in pov_actual_word.lower():
                        btn_widget.config(bg='#4CAF50')  # Green
                    elif pov_actual_word: # Word known, but letter not in it
                        btn_widget.config(bg='#f44336')  # Red
                    # If pov_actual_word is not known, color from immediate feedback (if any) or default disabled
                # else: # Not guessed, remains default disabled color
                #    btn_widget.config(bg='SystemButtonFace')
            elif letter_lower in pov_guesses: # Round active for POV, but this letter already guessed by POV
                btn_widget.config(state=tk.DISABLED)
                if pov_actual_word and letter_lower in pov_actual_word.lower():
                    btn_widget.config(bg='#4CAF50')  # Green
                elif pov_actual_word: # Word known, but letter not in it
                    btn_widget.config(bg='#f44336')  # Red
                # If pov_actual_word not known, rely on controller to not have sent this if it was an active guess, 
                # or if it was, the immediate feedback from make_guess needs to be handled or was already done.
            else: # Letter not yet guessed by POV, round active for POV
                # Enable only if it's the user's turn to guess (can_truly_guess refers to user, not pov)
                current_user_is_pov = (pov_username == self.master.get_username())
                if can_truly_guess and current_user_is_pov:
                    btn_widget.config(state=tk.NORMAL, bg='SystemButtonFace')
                else:
                    # Disabled if it's not the user's turn or they are spectating someone else who hasn't guessed this
                    btn_widget.config(state=tk.DISABLED, bg='SystemButtonFace') 
    
    def set_status(self, message, color="green"):
        self.status_var.set(message)
        if hasattr(self, 'status_display_label'):
            self.status_display_label.config(fg=color)

    def back_to_menu(self):
        self.controller.handle_back_to_menu_from_mp_game()

    def show_afk_dialog(self, on_yes_callback, on_timeout_callback, countdown_seconds=10):
        if hasattr(self, 'afk_popup') and self.afk_popup and self.afk_popup.winfo_exists():
            return # Already showing

        # Ensure "Last Chance" dialog is closed if we are re-showing the primary AFK dialog
        if hasattr(self, 'last_chance_popup') and self.last_chance_popup and self.last_chance_popup.winfo_exists():
            self.close_last_chance_dialog()

        self.afk_popup = tk.Toplevel(self.master)
        self.afk_popup.title("Still There?")
        self.afk_popup.attributes("-topmost", True)
        
        # Calculate position relative to the main window center
        master_x = self.master.winfo_x()
        master_y = self.master.winfo_y()
        master_width = self.master.winfo_width()
        master_height = self.master.winfo_height()
        popup_width = 300
        popup_height = 150
        pos_x = master_x + (master_width // 2) - (popup_width // 2)
        pos_y = master_y + (master_height // 2) - (popup_height // 2)
        self.afk_popup.geometry(f"{popup_width}x{popup_height}+{pos_x}+{pos_y}")
        self.afk_popup.resizable(False, False)

        tk.Label(self.afk_popup, text="Are you still in the game?", font=("Arial", 14)).pack(pady=10)
        self.afk_countdown_label = tk.Label(self.afk_popup, text=f"Closing in: {countdown_seconds}s", font=("Arial", 12))
        self.afk_countdown_label.pack(pady=5)

        self.afk_yes_button = tk.Button(self.afk_popup, text="Yes, I'm here!", command=lambda: [
            self.afk_yes_button.config(state=tk.DISABLED, text="Processing..."), # Immediate feedback
            on_yes_callback() # Call controller action
            # self.close_afk_dialog(was_answered=True) # REMOVE THIS - Controller will close based on state
        ])
        self.afk_yes_button.pack(pady=10)

        self.afk_popup.protocol("WM_DELETE_WINDOW", lambda: [on_timeout_callback(), self.close_afk_dialog(was_closed_by_user=True)])
        self.afk_popup.grab_set() # Make it modal

        self._afk_dialog_countdown_timer(countdown_seconds, on_timeout_callback)

    def _afk_dialog_countdown_timer(self, seconds_left, on_timeout_callback):
        if not (hasattr(self, 'afk_popup') and self.afk_popup and self.afk_popup.winfo_exists()):
            return

        if seconds_left > 0:
            if hasattr(self, 'afk_countdown_label') and self.afk_countdown_label and self.afk_countdown_label.winfo_exists():
                self.afk_countdown_label.config(text=f"Closing in: {seconds_left}s")
            
            if hasattr(self, 'afk_timer_id') and self.afk_timer_id is not None:
                 self.master.after_cancel(self.afk_timer_id)
            self.afk_timer_id = self.master.after(1000, lambda: self._afk_dialog_countdown_timer(seconds_left - 1, on_timeout_callback))
        else:
            # Timeout - Dialog stays open, content changes, button becomes "Try Next Round?"
            if hasattr(self, 'afk_countdown_label') and self.afk_countdown_label and self.afk_countdown_label.winfo_exists():
                self.afk_countdown_label.config(text="Timer expired. Still here?")
            if hasattr(self, 'afk_yes_button') and self.afk_yes_button and self.afk_yes_button.winfo_exists():
                self.afk_yes_button.config(text="Try Next Round?", state=tk.NORMAL) # Keep button active
            
            # Call timeout callback (for controller cooldown etc.), but dialog remains open
            if on_timeout_callback: # Ensure callback exists
                on_timeout_callback()
            # Do NOT call self.close_afk_dialog() here anymore.
            # It will be closed externally by the controller based on game state changes.

    def close_afk_dialog(self, was_answered=False, was_timed_out=False, was_closed_by_user=False):
        if hasattr(self, 'afk_timer_id') and self.afk_timer_id:
            self.master.after_cancel(self.afk_timer_id)
            self.afk_timer_id = None
        if hasattr(self, 'afk_popup') and self.afk_popup and self.afk_popup.winfo_exists():
            self.afk_popup.grab_release()
            self.afk_popup.destroy()
        
        # Nullify attributes to allow them to be recreated cleanly
        self.afk_popup = None 
        self.afk_countdown_label = None
        self.afk_yes_button = None
        # The controller will manage its state flags based on the callbacks.

        # Attribute for the new "Last Chance" dialog
        self.last_chance_popup = None

    def is_afk_dialog_showing(self):
        return hasattr(self, 'afk_popup') and self.afk_popup and self.afk_popup.winfo_exists()

    def show_game_cleaned_up_dialog(self, on_ok_callback):
        # Close any other popups this view might have
        if hasattr(self, 'afk_popup') and self.afk_popup and self.afk_popup.winfo_exists():
            self.close_afk_dialog()
        if hasattr(self, 'last_chance_popup') and self.last_chance_popup and self.last_chance_popup.winfo_exists():
            self.close_last_chance_dialog() # Ensure this is closed too

        if hasattr(self, 'cleanup_popup') and self.cleanup_popup and self.cleanup_popup.winfo_exists():
            return # Already showing

        self.cleanup_popup = tk.Toplevel(self.master)
        self.cleanup_popup.title("Game Over")
        self.cleanup_popup.attributes("-topmost", True)

        master_x = self.master.winfo_x()
        master_y = self.master.winfo_y()
        master_width = self.master.winfo_width()
        master_height = self.master.winfo_height()
        popup_width = 350 # Slightly wider for message
        popup_height = 150
        pos_x = master_x + (master_width // 2) - (popup_width // 2)
        pos_y = master_y + (master_height // 2) - (popup_height // 2)
        self.cleanup_popup.geometry(f"{popup_width}x{popup_height}+{pos_x}+{pos_y}")
        self.cleanup_popup.resizable(False, False)

        tk.Label(self.cleanup_popup, text="The game session was closed\ndue to inactivity.", font=("Arial", 14)).pack(pady=20)
        
        ok_button = tk.Button(self.cleanup_popup, text="OK", command=lambda: [
            self.cleanup_popup.destroy(),
            setattr(self, 'cleanup_popup', None), # Clean up attribute
            on_ok_callback()
        ])
        ok_button.pack(pady=10)
        self.cleanup_popup.protocol("WM_DELETE_WINDOW", lambda: [
            self.cleanup_popup.destroy(),
            setattr(self, 'cleanup_popup', None),
            on_ok_callback()
        ])
        self.cleanup_popup.grab_set()

    def close_game_cleaned_up_dialog(self):
        if hasattr(self, 'cleanup_popup') and self.cleanup_popup and self.cleanup_popup.winfo_exists():
            if self.cleanup_popup.grab_status(): # Check if grab is set before releasing
                self.cleanup_popup.grab_release()
            self.cleanup_popup.destroy()
        self.cleanup_popup = None # Clear the attribute

    # New method to show the "Last Chance" dialog
    def show_last_chance_dialog(self, on_last_chance_callback):
        if hasattr(self, 'last_chance_popup') and self.last_chance_popup and self.last_chance_popup.winfo_exists():
            return # Already showing

        # Ensure other popups (like AFK) are closed first
        if hasattr(self, 'afk_popup') and self.afk_popup and self.afk_popup.winfo_exists():
            self.close_afk_dialog()

        self.last_chance_popup = tk.Toplevel(self.master)
        self.last_chance_popup.title("Game Stalled")
        self.last_chance_popup.attributes("-topmost", True)

        master_x = self.master.winfo_x()
        master_y = self.master.winfo_y()
        master_width = self.master.winfo_width()
        master_height = self.master.winfo_height()
        popup_width = 380 # Wider for longer text
        popup_height = 180 # Taller for two lines of text + button
        pos_x = master_x + (master_width // 2) - (popup_width // 2)
        pos_y = master_y + (master_height // 2) - (popup_height // 2)
        self.last_chance_popup.geometry(f"{popup_width}x{popup_height}+{pos_x}+{pos_y}")
        self.last_chance_popup.resizable(False, False)

        msg_label = tk.Label(self.last_chance_popup, 
                             text="Server may be cleaning up the game due to inactivity.", 
                             font=("Arial", 12), wraplength=popup_width-40)
        msg_label.pack(pady=(20, 10))

        last_chance_button = tk.Button(self.last_chance_popup, text="Try Next Round (Last Chance)", 
                                       font=("Arial", 12, "bold"), bg="#e67e22", fg="white",
                                       command=lambda: [
                                           self.close_last_chance_dialog(), # Close immediately
                                           on_last_chance_callback() # Then call controller action
                                       ])
        last_chance_button.pack(pady=10)

        self.last_chance_popup.protocol("WM_DELETE_WINDOW", self.close_last_chance_dialog) # Also close on X
        self.last_chance_popup.grab_set()

    def close_last_chance_dialog(self):
        if hasattr(self, 'last_chance_popup') and self.last_chance_popup and self.last_chance_popup.winfo_exists():
            if self.last_chance_popup.grab_status(): # Check if grab is currently set
                self.last_chance_popup.grab_release() # Ensure grab is released
            self.last_chance_popup.destroy()
        self.last_chance_popup = None

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
        self.popup = None
        self.game_over_popup = None # To manage game over dialog

        tk.Label(self, text="1v1 Hangman Challenge", font=("Arial", 20)).pack(pady=10) # Title updated
        
        # Frame for top info (Word and Timer)
        top_info_frame = tk.Frame(self)
        top_info_frame.pack(pady=5)
        tk.Label(top_info_frame, textvariable=self.word_var, font=("Consolas", 32)).pack(side=tk.LEFT, padx=20)
        # Store the timer label widget to change its color
        self.timer_label_widget = tk.Label(top_info_frame, textvariable=self.timer_var, font=("Arial", 18))
        self.timer_label_widget.pack(side=tk.LEFT, padx=20)

        # Frame for game stats (Round, Score, Incorrect)
        stats_frame = tk.Frame(self)
        stats_frame.pack(pady=5)
        tk.Label(stats_frame, textvariable=self.round_var, font=("Arial", 16)).pack(side=tk.LEFT, padx=10)
        tk.Label(stats_frame, textvariable=self.score_var, font=("Arial", 16)).pack(side=tk.LEFT, padx=10) # Score Label
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

    def update_display(self, masked_word, timer_text, incorrect_text, status_text, player_wins, current_round_num, attempted_letters, current_word, round_over, game_over, timer_color="black"):
        self.word_var.set(masked_word)
        self.timer_var.set(timer_text)
        self.incorrect_var.set(incorrect_text)
        self.status_var.set(status_text)
        self.score_var.set(f"Score: {player_wins}/3") 
        self.round_var.set(f"Round: {current_round_num + 1}")
        # Apply color to timer label
        if hasattr(self, 'timer_label_widget'): # Check if timer_label_widget exists (it should if initialized correctly)
            self.timer_label_widget.config(fg=timer_color)
        else: # Fallback if timer_label_widget not found (should not happen)
            pass 

        self.update_keyboard(attempted_letters, current_word, round_over or game_over)

    def update_keyboard(self, attempted_letters, current_word_upper, disable_all):
        # `attempted_letters` is a set of all letters guessed by the user this round (e.g., {'a', 'x', 'e'})
        # `current_word_upper` is the actual word in uppercase (e.g., "PYTHON") or "" if not yet known.
        # `disable_all` is true if round/game is over

        for letter_button_char, btn_widget in self.keyboard_buttons.items():
            letter_lower = letter_button_char.lower()

            if disable_all:
                btn_widget.config(state=tk.DISABLED)
                # If game/round is over, finalize colors based on known current_word_upper
                if letter_lower in attempted_letters:
                    if current_word_upper and letter_lower in current_word_upper.lower():
                        btn_widget.config(bg='#4CAF50')  # Green
                    elif current_word_upper: # Word is known, but letter not in it
                        btn_widget.config(bg='#f44336')  # Red
                    # If current_word_upper is still not known at game over, button keeps its last color from feedback_guess
                # else: # If not attempted, it remains default or could be greyed out
                #     btn_widget.config(bg='SystemButtonFace') 
            elif letter_lower in attempted_letters:
                btn_widget.config(state=tk.DISABLED)
                if current_word_upper: # Only set authoritative color if actual word is known
                    if letter_lower in current_word_upper.lower():
                        btn_widget.config(bg='#4CAF50')  # Green
                    else:
                        btn_widget.config(bg='#f44336')  # Red
                # If current_word_upper is not known, button was already colored by feedback_guess, so don't change it here.
            else:
                btn_widget.config(state=tk.NORMAL, bg='SystemButtonFace')

    def feedback_guess(self, letter, is_correct):
        btn = self.keyboard_buttons[letter.upper()]
        if is_correct:
            btn.config(bg='#4CAF50')  # Green
        else:
            btn.config(bg='#f44336')  # Red
        btn.config(state=tk.DISABLED) # Always disable after guess

    def set_status(self, message, color="blue"):
        self.status_var.set(message)
        if hasattr(self, 'status_display_label'):
            self.status_display_label.config(fg=color)

    def show_match_found_countdown(self, countdown_callback, opponent_name="Opponent"):
        if self.popup and self.popup.winfo_exists(): self.popup.destroy()
        self.popup = tk.Toplevel(self)
        self.popup.title("Match Found")
        label = tk.Label(self.popup, text=f"Match found! Your opponent: {opponent_name}\nThe game will start in 5 seconds...", font=("Arial", 16))
        label.pack(padx=20, pady=20)
        self.countdown_label_popup = tk.Label(self.popup, text="5", font=("Arial", 32))
        self.countdown_label_popup.pack(pady=10)
        self.popup.update()
        self._start_countdown_in_popup(5, countdown_callback)

    def _start_countdown_in_popup(self, seconds, callback):
        if not (self.popup and self.popup.winfo_exists()): return

        if seconds > 0:
            self.countdown_label_popup.config(text=str(seconds))
            self.popup.update()
            self.after(1000, lambda: self._start_countdown_in_popup(seconds - 1, callback))
        else:
            if self.popup and self.popup.winfo_exists(): self.popup.destroy()
            self.popup = None
            callback() # Notify controller

    def show_sp_game_over_dialog(self, result_text, on_ok_callback):
        if self.game_over_popup and self.game_over_popup.winfo_exists():
            self.game_over_popup.destroy()

        self.game_over_popup = tk.Toplevel(self.master)
        self.game_over_popup.title("Game Over")
        
        # Simple dialog, can be styled more later if needed
        # Calculate position relative to the main window center
        master_x = self.master.winfo_x()
        master_y = self.master.winfo_y()
        master_width = self.master.winfo_width()
        master_height = self.master.winfo_height()
        popup_width = 300
        popup_height = 150
        pos_x = master_x + (master_width // 2) - (popup_width // 2)
        pos_y = master_y + (master_height // 2) - (popup_height // 2)
        self.game_over_popup.geometry(f"{popup_width}x{popup_height}+{pos_x}+{pos_y}")
        self.game_over_popup.resizable(False, False)
        self.game_over_popup.attributes("-topmost", True) # Make it appear on top

        tk.Label(self.game_over_popup, text=result_text, font=("Arial", 18), pady=20).pack()
        ok_button = tk.Button(self.game_over_popup, text="OK", command=lambda: [
            self.game_over_popup.destroy(),
            setattr(self, 'game_over_popup', None),
            on_ok_callback()
        ], width=10)
        ok_button.pack(pady=10)

        self.game_over_popup.protocol("WM_DELETE_WINDOW", lambda: [
            self.game_over_popup.destroy(),
            setattr(self, 'game_over_popup', None),
            on_ok_callback()
        ])
        self.game_over_popup.grab_set() # Make it modal

    def back_to_menu(self):
        self.controller.handle_back_to_menu_from_sp_game()

class LeaderboardView(BaseView):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        tk.Label(self, text="Leaderboard", font=("Arial", 20)).pack(pady=10)
        self.tree = ttk.Treeview(self, columns=("Username", "Wins"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(expand=True, fill="both")
        tk.Button(self, text="Back to Menu", command=lambda: self.controller.show_frame("MainMenu")).pack(pady=10)

    def on_show(self):
        self.controller.load_leaderboard()

    def display_leaderboard(self, entries):
        self.tree.delete(*self.tree.get_children()) # Clear existing items
        for entry in entries:
            self.tree.insert("", "end", values=(entry.username, entry.wins))

# Helper for popups (from original code, could be refactored into a utility or BaseView method)
def show_no_match_popup_tk(): # This is the Tkinter specific version
    # This function is a bit problematic in MVC as it creates its own Tk root.
    # It should ideally be handled by a view showing a dialog on the main app window.
    # For now, we might call this from a controller if really needed, but better to integrate.
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo(
        title="No Match Found",
        message="No opponent was found. Please try again later."
    )
    root.destroy()