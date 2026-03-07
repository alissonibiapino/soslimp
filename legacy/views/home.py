import customtkinter as ctk
# from PIL import Image

# Outras views
from views.coluna1 import Coluna1
from views.coluna2 import Coluna2
from views.coluna3 import Coluna3

class Home(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        # Configuração do layout
        self.grid_columnconfigure(0)
        self.grid_columnconfigure(0, weight=1, minsize=500)

        self.grid_columnconfigure(1)
        self.grid_columnconfigure(1, weight=1, minsize=350)

        self.grid_columnconfigure(2)
        self.grid_columnconfigure(2, weight=1, minsize=350)

        self.grid_rowconfigure(0, weight=1)

        # Jogando as views no App
        col2 = Coluna2(self, master)
        col2.grid(row=0, column=1, padx=10, sticky="nsew")

        col3 = Coluna3(self)
        col3.grid(row=0, column=2, padx=10, sticky="nsew")

        col1 = Coluna1(self, master, col2, col3)
        col1.grid(row=0, column=0, padx=10, sticky="nsew")
