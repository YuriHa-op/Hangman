import tkinter as tk
from tkinter import ttk
from .base_view import BaseView

class LeaderboardView(BaseView):
    def __init__(self, master, controller):
        super().__init__(master, controller)
        tk.Label(self, text="Leaderboard", font=("Arial", 20)).pack(pady=10)
        self.tree = ttk.Treeview(self, columns=("Username", "Wins"), show="headings")
        # Configure column headings
        self.tree.heading("Username", text="Username")
        self.tree.column("Username", anchor="w", width=200) # Anchor west, specify width
        self.tree.heading("Wins", text="Wins")
        self.tree.column("Wins", anchor="center", width=100) # Anchor center, specify width
        
        self.tree.pack(expand=True, fill="both", padx=20, pady=10)
        tk.Button(self, text="Back to Menu", command=lambda: self.controller.show_frame("MainMenu")).pack(pady=10)

    def on_show(self):
        self.controller.load_leaderboard()

    def display_leaderboard(self, entries):
        self.tree.delete(*self.tree.get_children()) # Clear existing items
        if entries: # Check if entries is not None and not empty
            for entry in entries:
                # Ensure entry has username and wins attributes, otherwise provide defaults
                username = getattr(entry, 'username', 'N/A')
                wins = getattr(entry, 'wins', 'N/A')
                self.tree.insert("", "end", values=(username, wins))
        # else: # Optionally, display a message if leaderboard is empty
            # self.tree.insert("", "end", values=("No leaderboard data available.", "")) 