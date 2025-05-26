import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import time
import json # Added for show_match_found_dialog and show_details in MatchHistory

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
        tk.Button(self.popup, text="OK", command=lambda: [self.popup.destroy(), self.controller.handle_no_match_found_dialog_ok()]).pack(pady=10)
        self.popup = None

class MatchHistoryView(BaseView):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        tk.Label(self, text="Match History", font=("Arial", 20)).pack(pady=10)
        self.tree = ttk.Treeview(self, columns=("Game ID", "Players", "Winner", "Rounds"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(expand=True, fill="both")
        tk.Button(self, text="Back to Menu", command=lambda: self.controller.show_frame("MainMenu")).pack(pady=10)
        self.tree.bind("<Double-1>", self.on_item_double_click)

    def on_show(self):
        self.controller.load_match_history()

    def display_match_history(self, games_data):
        self.tree.delete(*self.tree.get_children()) # Clear existing items
        games = json.loads(games_data)
        for game in games:
            self.tree.insert("", "end", values=(
                game.get("gameId", "N/A"),
                ", ".join(game.get("players", [])),
                game.get("overallWinner", "N/A"),
                game.get("totalRounds", "N/A")
            ))

    def on_item_double_click(self, event):
        item = self.tree.selection()
        if not item: return
        game_id = self.tree.item(item[0], "values")[0]
        if game_id and game_id != "N/A":
            self.controller.show_match_details(game_id)

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

class SinglePlayerGameView(BaseView):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        self.word_var = tk.StringVar()
        self.timer_var = tk.StringVar()
        self.incorrect_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.keyboard_buttons = {}
        self.popup = None

        tk.Label(self, text="Single Player Game", font=("Arial", 20)).pack(pady=10)
        tk.Label(self, textvariable=self.word_var, font=("Consolas", 32)).pack(pady=10)
        tk.Label(self, textvariable=self.timer_var, font=("Arial", 18)).pack(pady=5)
        tk.Label(self, textvariable=self.incorrect_var, font=("Arial", 14)).pack(pady=5)
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

    def update_display(self, masked_word, timer_text, incorrect_text, status_text, attempted_letters, current_word, round_over, game_over):
        self.word_var.set(masked_word)
        self.timer_var.set(timer_text)
        self.incorrect_var.set(incorrect_text)
        self.status_var.set(status_text)
        # Pass all necessary info to update_keyboard
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

    def show_match_found_countdown(self, countdown_callback):
        if self.popup and self.popup.winfo_exists(): self.popup.destroy()
        self.popup = tk.Toplevel(self)
        self.popup.title("Match Found")
        label = tk.Label(self.popup, text="Match found! The game will start in 5 seconds...", font=("Arial", 16))
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