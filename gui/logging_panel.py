import tkinter as tk
from tkinter import ttk


class LoggingPanel:

    def __init__(self, main):

        self.main = main

        self.tab = ttk.Frame(main.notebook)
        main.notebook.add(self.tab, text="Logging")

        self.log_box = tk.Text(self.tab)
        self.log_box.pack(fill="both", expand=True)

    def log(self, message):

        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)