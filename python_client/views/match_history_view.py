import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
from .base_view import BaseView

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
        try:
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
                
                self.tree.insert("", "end", iid=game_id, values=(
                    dt_object,
                    ", ".join(game.get("players", [])),
                    game.get("overallWinner", "N/A"),
                    game.get("totalRounds", "N/A")
                ))
        except json.JSONDecodeError:
            print(f"Error decoding match history JSON: {games_data}")
            # Optionally inform the user via a status label if the view has one
        except Exception as e:
            print(f"Error displaying match history: {e}")

    def on_item_double_click(self, event):
        selected_item_iid = self.tree.selection()
        if not selected_item_iid: return
        game_id = selected_item_iid[0] # game_id is the iid
        if game_id and game_id != "N/A": # Ensure game_id is valid
            selected_type = self.history_type_var.get()
            mode = 'singleplayer' if selected_type == "1v1 Matches" else 'multiplayer'
            self.controller.show_match_details(game_id, mode)

    def show_details_popup(self, details_data):
        try:
            details = json.loads(details_data)
            if "error" in details:
                msg = f"Error: {details['error']}"
            else:
                msg = f"Game ID: {details.get('gameId', 'N/A')}\nWinner: {details.get('overallWinner', 'N/A')}\nPlayers: {', '.join(details.get('players', []))}\nRounds:\n"
                for rnd in details.get("rounds", []):
                    msg += f"  Round {rnd.get('roundNumber', '?')}: Word='{rnd.get('word', 'N/A')}', Winner={rnd.get('winner', 'N/A')}\n"
        except json.JSONDecodeError:
            msg = "Error: Could not parse match details."
        except Exception as e:
            msg = f"An unexpected error occurred: {e}"
        messagebox.showinfo("Match Details", msg, parent=self) # Ensure popup is child of this frame 