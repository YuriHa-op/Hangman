import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import time
import json # Added for show_match_found_dialog and show_details in MatchHistory
from datetime import datetime # Added for timestamp formatting
import os

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
        
        popup = tk.Toplevel(self)
        popup.title("Match Details")
        
        # Nicely format and display the details
        text_widget = tk.Text(popup, wrap="word", height=20, width=60, font=("Courier New", 10))
        text_widget.pack(padx=10, pady=10)
        
        # --- Format the content ---
        content = f"Game ID: {details.get('gameId', 'N/A')}\n"
        
        winner = details.get('overallWinner')
        if winner:
            content += f"Winner: {winner}\n"
            
        content += "Players: " + ", ".join(details.get('players', [])) + "\n\n"
        
        content += "--- Rounds ---\n"
        for i, round_detail in enumerate(details.get('rounds', [])):
            content += f"Round {i+1}:\n"
            content += f"  Word: {round_detail.get('word', 'N/A')}\n"
            round_winner = round_detail.get('winner')
            content += f"  Winner: {round_winner if round_winner else 'None'}\n"
            content += "  Player Details:\n"
            for player_round in round_detail.get('playerRounds', []):
                content += f"    - {player_round.get('username')}:\n"
                content += f"        Guessed Correctly: {'Yes' if player_round.get('guessedCorrectly') else 'No'}\n"
                content += f"        Guesses: {player_round.get('guesses', '')}\n"
                content += f"        Time Taken: {player_round.get('timeTakenMs', 'N/A')}ms\n"
            content += "\n"
        
        text_widget.insert("1.0", content)
        text_widget.config(state="disabled") # Make it read-only
        
        close_button = tk.Button(popup, text="Close", command=popup.destroy)
        close_button.pack(pady=5)
        
        popup.transient(self.master)
        popup.grab_set()

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
        
        self.scores_frame = tk.Frame(self)
        self.scores_frame.pack(pady=5)

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

        self.right_panel = tk.Frame(self)
        self.right_panel.pack(side=tk.RIGHT, fill="both", expand=True, padx=10, pady=10)

    def on_show(self):
        self.controller.start_multiplayer_game_poll()
        self.set_status("Connecting to game...", "blue")
        # Reset any specific UI states needed
        self.update_scores_panel([], {}, None, False, False) # Clear score panel
        self.update_keyboard(None, {}, {}, False, False) # Reset keyboard

    def update_display(self, word, timer, round_text, status, players, scores, pov_username, guesses_map, actual_words_map, can_truly_guess, is_user_done_guessing_for_spectate, interaction_over_for_pov, should_update_keyboard, should_update_scores):
        # Update main labels via StringVars
        self.word_var.set(word)
        self.timer_var.set(timer)
        self.round_var.set(round_text)
        self.status_var.set(status)
        
        if should_update_scores:
            self.update_scores_panel(players, scores, pov_username, can_truly_guess, is_user_done_guessing_for_spectate)
        
        if should_update_keyboard:
            self.update_keyboard(pov_username, guesses_map, actual_words_map, can_truly_guess, interaction_over_for_pov)

    def update_scores_panel(self, players, scores, pov_username, can_guess_for_self, is_user_done_guessing_for_self):
        # Clear existing score widgets
        for widget in self.scores_frame.winfo_children():
            widget.destroy()
        
        my_username = self.master.get_username()

        # Sort players to have the current user first, then others alphabetically
        sorted_players = sorted(players, key=lambda p: (p != my_username, p.lower()))

        for player in sorted_players:
            score = scores.get(player, 0)
            
            # Create a frame for each player's info
            player_frame = tk.Frame(self.scores_frame, bg="#333", bd=1, relief="solid")
            player_frame.pack(fill="x", expand=True, pady=3, padx=3)
            
            # Determine background color and status text
            is_pov = (player == pov_username)
            is_self = (player == my_username)

            status_text = ""
            if scores.get(f"{player}_finished", False):
                status_text = "✓ Finished"
                bg_color = "#004D40" # Dark Green
            elif is_pov:
                status_text = "▶ Spectating"
                bg_color = "#4A148C" # Purple
            else:
                bg_color = "#424242" # Dark Grey
            
            # Highlight for the user's own frame
            if is_self:
                bg_color = "#01579B" # Blue
                if is_pov and status_text == "▶ Spectating":
                    status_text = "Your Turn" # More intuitive for self
                elif status_text == "✓ Finished":
                    status_text = "✓ You Finished"

            player_frame.config(bg=bg_color)
            
            # Player label (includes spectating status)
            player_name_label = tk.Label(player_frame, text=f"{player}", font=("Arial", 14), anchor="w", bg=bg_color, fg="white")
            player_name_label.pack(side="left", padx=5, fill='x', expand=True)

            # Score label
            score_label = tk.Label(player_frame, text=f"Score: {score}", font=("Arial", 14), anchor="e", bg=bg_color, fg="white")
            score_label.pack(side="right", padx=5)

            # Status label (Finished/Spectating)
            if status_text:
                status_indicator = tk.Label(player_frame, text=status_text, font=("Arial", 10, "italic"), anchor="e", bg=bg_color, fg="#BDBDBD")
                status_indicator.pack(side="right", padx=5)

            # Make the frame clickable to spectate (if not self and not finished)
            if not is_self:
                player_frame.bind("<Button-1>", lambda e, p=player: self.controller.set_spectate_player(p))
                player_name_label.bind("<Button-1>", lambda e, p=player: self.controller.set_spectate_player(p))
                score_label.bind("<Button-1>", lambda e, p=player: self.controller.set_spectate_player(p))

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
        if hasattr(self, 'cleanup_popup') and self.cleanup_popup and self.cleanup_popup.winfo_exists():
            return

        if hasattr(self, 'afk_popup') and self.afk_popup and self.afk_popup.winfo_exists():
            self.close_afk_dialog()

        self.cleanup_popup = tk.Toplevel(self.master)
        self.cleanup_popup.title("Game Over")

        tk.Label(self.cleanup_popup, text="The game ended due to inactivity.").pack(pady=15)
        tk.Button(self.cleanup_popup, text="OK", command=lambda: [self.close_game_cleaned_up_dialog(), on_ok_callback()]).pack(pady=10)

        self.cleanup_popup.protocol("WM_DELETE_WINDOW", lambda: [self.close_game_cleaned_up_dialog(), on_ok_callback()])

    def close_game_cleaned_up_dialog(self):
        if hasattr(self, 'cleanup_popup') and self.cleanup_popup and self.cleanup_popup.winfo_exists():
            self.cleanup_popup.destroy()
        self.cleanup_popup = None # Clear the attribute

    # New method to show the "Last Chance" dialog
    def show_last_chance_dialog(self, on_last_chance_callback):
        if hasattr(self, 'last_chance_popup') and self.last_chance_popup and self.last_chance_popup.winfo_exists():
            return # Already showing

        if hasattr(self, 'afk_popup') and self.afk_popup and self.afk_popup.winfo_exists():
            self.close_afk_dialog()

        self.last_chance_popup = tk.Toplevel(self.master)
        self.last_chance_popup.title("Game Stalled")

        tk.Label(self.last_chance_popup, text="The round seems stalled. Start next round?", wraplength=300).pack(pady=15)
        tk.Button(self.last_chance_popup, text="Start Next Round", command=lambda: [self.close_last_chance_dialog(), on_last_chance_callback()]).pack(pady=10)

        self.last_chance_popup.protocol("WM_DELETE_WINDOW", self.close_last_chance_dialog)

    def close_last_chance_dialog(self):
        if hasattr(self, 'last_chance_popup') and self.last_chance_popup and self.last_chance_popup.winfo_exists():
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
        tk.Label(self, text="Leaderboard", font=("Arial", 24, "bold")).pack(pady=10)
        
        # Use a Treeview for a structured leaderboard display
        self.tree = ttk.Treeview(self, columns=("Rank", "Player", "Wins"), show="headings")
        self.tree.heading("Rank", text="Rank")
        self.tree.column("Rank", width=50, anchor="center")
        self.tree.heading("Player", text="Player")
        self.tree.column("Player", width=200, anchor="w")
        self.tree.heading("Wins", text="Wins")
        self.tree.column("Wins", width=100, anchor="center")
        
        self.tree.pack(expand=True, fill="both", padx=20, pady=10)
        
        tk.Button(self, text="Back to Menu", command=lambda: self.controller.show_frame("MainMenu")).pack(pady=10)

    def on_show(self):
        self.controller.load_leaderboard()

    def display_leaderboard(self, entries):
        # Clear previous entries
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # `entries` is now expected to be a list of LeaderboardEntryDTO-like objects
        if not entries:
            self.tree.insert("", "end", values=("", "No leaderboard data available.", ""))
            return
            
        for i, entry in enumerate(entries):
            rank = i + 1
            username = entry.username
            wins = entry.wins
            self.tree.insert("", "end", values=(rank, username, wins))

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