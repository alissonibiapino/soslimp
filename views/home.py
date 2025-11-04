import customtkinter as ctk
# from PIL import Image

# Outras views
from views.coluna1 import Coluna1
from views.coluna2 import Coluna2
from views.coluna3 import Coluna3

# Cores
from theme import colors

class Home(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=colors.BRANCO)
        self.controller = controller
        
        # Configuração do layout
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=1)

        self.grid_rowconfigure(0, weight=1)

        # Jogando as views no App
        col1 = Coluna1(self, controller)
        col1.grid(row=0, column=0, padx=25, pady=10, sticky="nsew")

        col2 = Coluna2(self)
        col2.grid(row=0, column=1, padx=25, pady=10, sticky="nsew")

        col3 = Coluna3(self)
        col3.grid(row=0, column=2, padx=25, pady=10, sticky="nsew")
        
