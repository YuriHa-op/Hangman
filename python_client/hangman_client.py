import sys
import os
import time
import traceback
from omniORB import CORBA
import GameModule
import GameModule__POA
import CosNaming
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import json

# Default ORB settings (change if your server uses different host/port)
ORB_HOST = os.environ.get('ORB_HOST', 'localhost')
ORB_PORT = os.environ.get('ORB_PORT', '900')

# --- Helper function to show a pop-up if no match is found ---
def show_no_match_popup():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo(
        title="No Match Found",
        message="No opponent was found. Please try again later."
    )
    root.destroy()


def get_game_service():
    # Initialize the ORB
    orb = CORBA.ORB_init([
        '-ORBInitRef', f'NameService=corbaloc:iiop:{ORB_HOST}:{ORB_PORT}/NameService'
    ], CORBA.ORB_ID)

    # Obtain reference to the naming service
    obj = orb.resolve_initial_references('NameService')
    naming_context = obj._narrow(CosNaming.NamingContext)
    if naming_context is None:
        print('Failed to narrow the naming context')
        sys.exit(1)

    # Resolve the GameService object
    name = [CosNaming.NameComponent('GameService', '')]
    try:
        obj_ref = naming_context.resolve(name)
        game_service = obj_ref._narrow(GameModule.GameService)
        if game_service is None:
            print('GameService reference is not valid')
            sys.exit(1)
        return game_service
    except Exception as e:
        print('Could not resolve GameService:', e)
        sys.exit(1)


def main_menu(game_service, username):
    while True:
        print(f"\nWelcome, {username}!")
        print("1. Start Game")
        print("2. View Leaderboard")
        print("3. Logout")
        choice = input("Select an option: ").strip()
        if choice == '1':
            start_game(game_service, username)
        elif choice == '2':
            print(game_service.viewLeaderboard())
        elif choice == '3':
            game_service.logout(username)
            print("Logged out.")
            break
        else:
            print("Invalid choice.")

def start_game(game_service, username):
    print("\nRequesting a match...")
    masked_word = game_service.startGame(username)
    if masked_word == 'WAITING_FOR_MATCH':
        print("Waiting for an opponent...")
        # Poll for match
        waiting_time = game_service.getWaitingTime()
        start = time.time()
        while time.time() - start < waiting_time:
            time.sleep(1)
            masked_word = game_service.getMaskedWord(username)
            if masked_word != 'WAITING_FOR_MATCH' and masked_word:
                break
        if masked_word == 'WAITING_FOR_MATCH' or not masked_word:
            print("No match found. Try again later.")
            show_no_match_popup()  # Show pop-up dialog
            game_service.endGameSession(username)
            return
    if masked_word != 'WAITING_FOR_MATCH':
        print("Match found! The game will start in 5 seconds...")
        for i in range(5, 0, -1):
            print(f"Starting in {i}...", end='\r')
            time.sleep(1)
        print(" " * 30, end='\r')  # Clear the line
    print("Game started! Let's play Hangman.")
    play_game_session(game_service, username)

def play_game_session(game_service, username):
    # Main game session loop (best of 3)
    while True:
        round_result = play_round(game_service, username)
        # After each round, show round winner and session result
        state = game_service.getGameState(username)
        if state.roundWinner:
            if state.roundWinner == username:
                print(f"You won round {state.currentRound + 1}!")
            else:
                print(f"{state.roundWinner} won round {state.currentRound + 1}.")
        else:
            print("No one won this round.")
        if state.sessionResult and state.sessionResult != 'ONGOING':
            if state.sessionResult == 'WIN':
                print("\nCongratulations! You won the game session!")
            elif state.sessionResult == 'LOSE':
                print("\nYou lost the game session.")
            else:
                print(f"\nGame session result: {state.sessionResult}")
            game_service.endGameSession(username)
            game_service.cleanupPlayerSession(username)
            break
        # Start next round if game is not over
        print("\nStarting next round...")
        started = game_service.startNewRound(username)
        if not started:
            print("Could not start new round. Returning to main menu.")
            break
    print("Returning to main menu.")

def play_round(game_service, username):
    # Play a single round
    while True:
        state = game_service.getGameState(username)
        masked_word = state.maskedWord
        incorrect = state.incorrectGuesses
        remaining = state.remainingTime
        print(f"\nWord: {masked_word}")
        print(f"Incorrect guesses: {incorrect}/5 | Time left: {remaining}s")
        guess = input("Enter a letter (or 'quit' to exit): ").strip().lower()
        if guess == 'quit':
            game_service.endGameSession(username)
            print("Game exited.")
            sys.exit(0)
        if len(guess) != 1 or not guess.isalpha():
            print("Please enter a single letter.")
            continue
        correct = game_service.sendGuess(username, guess[0])
        if correct:
            print("Correct!")
        else:
            print("Incorrect.")
        # Refresh state after guess
        state = game_service.getGameState(username)
        if state.roundOver:
            # Call finishRound with remaining time and guessed status
            guessed_word = '_' not in state.maskedWord
            game_service.finishRound(username, state.remainingTime, guessed_word)
            print("\nRound over!")
            return

def login_or_create(game_service):
    while True:
        print("\n1. Login\n2. Create Account\n3. Exit")
        choice = input("Select an option: ").strip()
        if choice == '1':
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            try:
                if game_service.login(username, password):
                    print("Login successful!")
                    return username
                else:
                    print("Login failed. Check your credentials.")
            except GameModule.AlreadyLoggedInException as e:
                print("Error:", e.message)
        elif choice == '2':
            username = input("Choose a username: ").strip()
            password = input("Choose a password: ").strip()
            if game_service.createPlayer(username, password):
                print("Account created! You can now log in.")
            else:
                print("Account creation failed. Username may already exist.")
        elif choice == '3':
            sys.exit(0)
        else:
            print("Invalid choice.")

def main():
    print("Python CORBA Hangman Client")
    try:
        game_service = get_game_service()
        username = login_or_create(game_service)
        app = HangmanApp(game_service, username)
        app.mainloop()
    except Exception as e:
        print("An error occurred:")
        traceback.print_exc()

# --- Tkinter GUI Classes ---
class HangmanApp(tk.Tk):
    def __init__(self, game_service, username):
        super().__init__()
        self.title("Hangman - Python Client")
        self.geometry("800x600")
        self.game_service = game_service
        self.username = username
        self.frames = {}
        for F in (MainMenu, MultiplayerLobby, MatchHistory, MultiplayerGame, SinglePlayerGame, Leaderboard):
            frame = F(self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        self.show_frame(MainMenu)
    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()

class MainMenu(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text=f"Welcome, {master.username}!", font=("Arial", 24)).pack(pady=20)
        tk.Button(self, text="Single Player", command=lambda: master.show_frame(SinglePlayerGame)).pack(pady=10)
        tk.Button(self, text="Multiplayer", command=lambda: master.show_frame(MultiplayerLobby)).pack(pady=10)
        tk.Button(self, text="Match History", command=lambda: master.show_frame(MatchHistory)).pack(pady=10)
        tk.Button(self, text="Leaderboard", command=lambda: master.show_frame(Leaderboard)).pack(pady=10)
        tk.Button(self, text="Logout", command=self.logout).pack(pady=10)
    def logout(self):
        self.master.game_service.logout(self.master.username)
        self.master.destroy()

class MultiplayerLobby(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.label = tk.Label(self, text="Multiplayer Lobby", font=("Arial", 20))
        self.label.pack(pady=10)
        self.players_list = tk.Listbox(self)
        self.players_list.pack(pady=10)
        self.status_label = tk.Label(self, text="Waiting for players...")
        self.status_label.pack(pady=10)
        tk.Button(self, text="Back to Menu", command=self.back_to_menu).pack(pady=10)
        self.polling = False
    def on_show(self):
        self.polling = True
        threading.Thread(target=self.poll_lobby, daemon=True).start()
    def poll_lobby(self):
        self.master.game_service.startMultiplayerGame(self.master.username)
        while self.polling:
            state_json = self.master.game_service.getMultiplayerLobbyState(self.master.username)
            state = json.loads(state_json)
            self.players_list.delete(0, tk.END)
            for player in state.get("players", []):
                self.players_list.insert(tk.END, player)
            if state.get("state") == "STARTED":
                self.status_label.config(text="Game started!")
                self.polling = False
                self.master.show_frame(MultiplayerGame)
                return
            else:
                self.status_label.config(text="Waiting for players...")
            time.sleep(1)
    def back_to_menu(self):
        self.polling = False
        self.master.show_frame(MainMenu)
    def destroy(self):
        self.polling = False
        super().destroy()

class MatchHistory(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text="Match History", font=("Arial", 20)).pack(pady=10)
        self.tree = ttk.Treeview(self, columns=("Game ID", "Players", "Winner", "Rounds"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(expand=True, fill="both")
        tk.Button(self, text="Back to Menu", command=lambda: master.show_frame(MainMenu)).pack(pady=10)
        self.tree.bind("<Double-1>", self.show_details)
    def on_show(self):
        self.tree.delete(*self.tree.get_children())
        history_json = self.master.game_service.getMatchHistory(self.master.username)
        games = json.loads(history_json)
        for game in games:
            self.tree.insert("", "end", values=(
                game["gameId"],
                ", ".join(game["players"]),
                game["overallWinner"],
                game["totalRounds"]
            ))
    def show_details(self, event):
        item = self.tree.selection()[0]
        game_id = self.tree.item(item, "values")[0]
        details_json = self.master.game_service.getMatchDetails(game_id)
        details = json.loads(details_json)
        msg = f"Game ID: {details['gameId']}\nWinner: {details['overallWinner']}\nPlayers: {', '.join(details['players'])}\nRounds:\n"
        for rnd in details["rounds"]:
            msg += f"  Round {rnd['roundNumber']}: Word='{rnd['word']}', Winner={rnd['winner']}\n"
        messagebox.showinfo("Match Details", msg)

class MultiplayerGame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.word_var = tk.StringVar()
        self.timer_var = tk.StringVar()
        self.round_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.scores_var = tk.StringVar()
        self.keyboard_buttons = {}

        tk.Label(self, text="Multiplayer Game", font=("Arial", 20)).pack(pady=10)
        tk.Label(self, textvariable=self.word_var, font=("Consolas", 32)).pack(pady=10)
        tk.Label(self, textvariable=self.timer_var, font=("Arial", 18)).pack(pady=5)
        tk.Label(self, textvariable=self.round_var, font=("Arial", 14)).pack(pady=5)
        tk.Label(self, textvariable=self.scores_var, font=("Arial", 14)).pack(pady=5)
        tk.Label(self, textvariable=self.status_var, font=("Arial", 16), fg="green").pack(pady=5)

        kb_frame = tk.Frame(self)
        kb_frame.pack(pady=10)
        for i, row in enumerate(["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]):
            row_frame = tk.Frame(kb_frame)
            row_frame.pack()
            for letter in row:
                btn = tk.Button(row_frame, text=letter, width=4, height=2,
                                command=lambda l=letter: self.make_guess(l))
                btn.pack(side=tk.LEFT, padx=2, pady=2)
                self.keyboard_buttons[letter] = btn

        tk.Button(self, text="Back to Menu", command=self.back_to_menu).pack(pady=10)
        self.polling = False

    def enable_keyboard(self):
        for btn in self.keyboard_buttons.values():
            btn.config(state=tk.NORMAL, bg='SystemButtonFace')

    def on_show(self):
        self.polling = True
        self.enable_keyboard()
        self.status_var.set("")
        threading.Thread(target=self.poll_game, daemon=True).start()

    def poll_game(self):
        cleaned_up = False
        while self.polling:
            state_json = self.master.game_service.getMultiplayerLobbyState(self.master.username)
            state = json.loads(state_json)
            game = state.get("gameState", {})
            self.word_var.set(game.get("maskedWord", ""))
            self.timer_var.set(f"Time left: {game.get('remainingTime', 0)}s")
            self.round_var.set(f"Round: {game.get('currentRound', 0) + 1}")
            scores = game.get("scores", {})
            scores_str = " | ".join(f"{p}: {scores.get(p, 0)}" for p in state.get("players", []))
            self.scores_var.set(f"Scores: {scores_str}")
            guesses = set(game.get("guesses", []))
            for letter, btn in self.keyboard_buttons.items():
                if letter.lower() in guesses:
                    btn.config(state=tk.DISABLED)
            if not game.get("roundInProgress", True):
                winner = game.get("roundWinner", "")
                if winner:
                    if winner == self.master.username:
                        self.status_var.set("You won this round!")
                    else:
                        self.status_var.set(f"{winner} won this round.")
                else:
                    self.status_var.set("No one won this round.")
                for btn in self.keyboard_buttons.values():
                    btn.config(state=tk.DISABLED)
                # Start next round if game is not over
                if not game.get("gameWinner") and game.get("sessionResult", "ONGOING") == "ONGOING":
                    time.sleep(2)
                    self.master.game_service.startMultiplayerNextRound(self.master.username)
                    self.enable_keyboard()
            if game.get("gameWinner"):
                if not cleaned_up:
                    try:
                        self.master.game_service.endGameSession(self.master.username)
                        self.master.game_service.cleanupPlayerSession(self.master.username)
                    except Exception:
                        pass
                    cleaned_up = True
                if game["gameWinner"] == self.master.username:
                    self.status_var.set("🎉 You won the game! 🎉")
                else:
                    self.status_var.set(f"{game['gameWinner']} won the game.")
                self.polling = False
            time.sleep(1)

    def make_guess(self, letter):
        correct = self.master.game_service.sendMultiplayerGuess(self.master.username, letter.lower())
        btn = self.keyboard_buttons[letter.upper()]
        if correct:
            btn.config(bg='#4CAF50')  # Green
        else:
            btn.config(bg='#f44336')  # Red
        btn.config(state=tk.DISABLED)

    def back_to_menu(self):
        self.polling = False
        self.master.show_frame(MainMenu)

class SinglePlayerGame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.word_var = tk.StringVar()
        self.timer_var = tk.StringVar()
        self.incorrect_var = tk.StringVar()
        self.status_var = tk.StringVar()
        self.keyboard_buttons = {}

        tk.Label(self, text="Single Player Game", font=("Arial", 20)).pack(pady=10)
        tk.Label(self, textvariable=self.word_var, font=("Consolas", 32)).pack(pady=10)
        tk.Label(self, textvariable=self.timer_var, font=("Arial", 18)).pack(pady=5)
        tk.Label(self, textvariable=self.incorrect_var, font=("Arial", 14)).pack(pady=5)
        tk.Label(self, textvariable=self.status_var, font=("Arial", 16), fg="blue").pack(pady=5)

        kb_frame = tk.Frame(self)
        kb_frame.pack(pady=10)
        for i, row in enumerate(["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]):
            row_frame = tk.Frame(kb_frame)
            row_frame.pack()
            for letter in row:
                btn = tk.Button(row_frame, text=letter, width=4, height=2,
                                command=lambda l=letter: self.make_guess(l))
                btn.pack(side=tk.LEFT, padx=2, pady=2)
                self.keyboard_buttons[letter] = btn

        tk.Button(self, text="Back to Menu", command=self.back_to_menu).pack(pady=10)
        self.polling = False

    def enable_keyboard(self):
        for btn in self.keyboard_buttons.values():
            btn.config(state=tk.NORMAL, bg='SystemButtonFace')

    def on_show(self):
        self.polling = True
        self.enable_keyboard()
        self.status_var.set("")
        threading.Thread(target=self.start_game, daemon=True).start()

    def start_game(self):
        self.master.game_service.startGame(self.master.username)
        # Wait for match (if needed)
        masked_word = self.master.game_service.getMaskedWord(self.master.username)
        if masked_word == 'WAITING_FOR_MATCH':
            waiting_time = self.master.game_service.getWaitingTime()
            start = time.time()
            while time.time() - start < waiting_time:
                time.sleep(1)
                masked_word = self.master.game_service.getMaskedWord(self.master.username)
                if masked_word != 'WAITING_FOR_MATCH' and masked_word:
                    break
            if masked_word == 'WAITING_FOR_MATCH' or not masked_word:
                self.status_var.set("No match found. Try again later.")
                self.polling = False
                return
        # Show match found dialog with countdown only after match is found
        self.show_match_found_countdown()
        self.enable_keyboard()
        while self.polling:
            state = self.master.game_service.getGameState(self.master.username)
            self.word_var.set(state.maskedWord)
            self.timer_var.set(f"Time left: {state.remainingTime}s")
            self.incorrect_var.set(f"Incorrect guesses: {state.incorrectGuesses}/5")
            guessed = set(state.maskedWord.replace(" ", "").replace("_", "").lower())
            for letter, btn in self.keyboard_buttons.items():
                if letter.lower() in guessed:
                    btn.config(state=tk.DISABLED)
            if state.roundOver:
                guessed_word = "_" not in state.maskedWord
                self.master.game_service.finishRound(self.master.username, state.remainingTime, guessed_word)
                if state.roundWinner:
                    if state.roundWinner == self.master.username:
                        self.status_var.set("You won this round!")
                    else:
                        self.status_var.set(f"{state.roundWinner} won this round.")
                else:
                    self.status_var.set("No one won this round.")
                for btn in self.keyboard_buttons.values():
                    btn.config(state=tk.DISABLED)
                # Start next round if game is not over
                if not state.gameOver and state.sessionResult == "ONGOING":
                    time.sleep(2)
                    self.master.game_service.startNewRound(self.master.username)
                    self.enable_keyboard()
            if state.sessionResult and state.sessionResult != "ONGOING":
                if state.sessionResult == "WIN":
                    self.status_var.set("🎉 You won the game! 🎉")
                elif state.sessionResult == "LOSE":
                    self.status_var.set("You lost the game.")
                else:
                    self.status_var.set(f"Game session result: {state.sessionResult}")
                self.polling = False
            time.sleep(1)

    def show_match_found_countdown(self):
        popup = tk.Toplevel(self)
        popup.title("Match Found")
        label = tk.Label(popup, text="Match found! The game will start in 5 seconds...", font=("Arial", 16))
        label.pack(padx=20, pady=20)
        countdown_label = tk.Label(popup, text="5", font=("Arial", 32))
        countdown_label.pack(pady=10)
        self.update()
        for i in range(5, 0, -1):
            countdown_label.config(text=str(i))
            popup.update()
            time.sleep(1)
        popup.destroy()

    def make_guess(self, letter):
        correct = self.master.game_service.sendGuess(self.master.username, letter.lower())
        btn = self.keyboard_buttons[letter.upper()]
        if correct:
            btn.config(bg='#4CAF50')  # Green
        else:
            btn.config(bg='#f44336')  # Red
        btn.config(state=tk.DISABLED)

    def back_to_menu(self):
        self.polling = False
        self.master.game_service.endGameSession(self.master.username)
        self.master.game_service.cleanupPlayerSession(self.master.username)
        self.master.show_frame(MainMenu)

class Leaderboard(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        tk.Label(self, text="Leaderboard", font=("Arial", 20)).pack(pady=10)
        self.tree = ttk.Treeview(self, columns=("Username", "Wins"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack(expand=True, fill="both")
        tk.Button(self, text="Back to Menu", command=lambda: master.show_frame(MainMenu)).pack(pady=10)

    def on_show(self):
        self.tree.delete(*self.tree.get_children())
        # Try to use getLeaderboardEntries if available, else fallback to viewLeaderboard
        try:
            entries = self.master.game_service.getLeaderboardEntries()
            for entry in entries:
                self.tree.insert("", "end", values=(entry.username, entry.wins))
        except Exception:
            # Fallback: parse text leaderboard
            text = self.master.game_service.viewLeaderboard()
            for line in text.splitlines():
                if ':' in line:
                    user, wins = line.split(':', 1)
                    self.tree.insert("", "end", values=(user.strip(), wins.strip().replace(' wins', '')))

if __name__ == '__main__':
    main() 