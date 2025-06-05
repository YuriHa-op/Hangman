import tkinter as tk

class BaseView(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.master = master # This is the HangmanApp (root Tk window) or another container
        self.controller = controller

    def on_show(self):
        # Called when the frame is raised
        pass 