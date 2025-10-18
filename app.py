import customtkinter as ctk
from PIL import Image

# Outras views
from views.coluna1 import Coluna1
from views.coluna2 import Coluna2
from views.coluna3 import Coluna3

# Cores
from theme import colors

class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=colors.BRANCO)

        # Configuração inicial do App
        ctk.set_appearance_mode("light")
        self.title("SOSLimp")
        self.geometry("1280x720")
        # self.minsize("1280x720")

        # Configuração do layout
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=1)

        self.grid_rowconfigure(0, weight=1)

        # Jogando as views no App
        col1 = Coluna1(self)
        col1.grid(row=0, column=0, padx=40, pady=10, sticky="nsew")

        col2 = Coluna2(self)
        col2.grid(row=0, column=1, padx=40, pady=10, sticky="nsew")

        col2 = Coluna2(self)
        col2.grid(row=0, column=2, padx=40, pady=10, sticky="nsew")
        
        # Iniciar o app
        self.mainloop()

App()