import tkinter as tk
from .base_view import BaseView

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
        self.controller.handle_exit_app() 