import tkinter as tk
from .base_view import BaseView

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
        username = self.controller.get_username() # Get username via its specific controller
        self.welcome_label.config(text=f"Welcome, {username}!")

    def logout(self):
        self.controller.handle_logout() 