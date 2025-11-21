import customtkinter as ctk

# Cores
from theme import colors

class Transaction(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0)
        self.grid_columnconfigure(0, weight=1)

        self.grid_columnconfigure(1)
        self.grid_columnconfigure(1, weight=1)

        self.grid_rowconfigure(0, weight=1)

        col1 = ctk.CTkFrame(self, fg_color="red")
        col1.grid(row=0, column=0, padx=0, sticky="nsew")

        col2 = ctk.CTkFrame(self, fg_color="green")
        col2.grid(row=0, column=0, padx=0, sticky="nsew")
    