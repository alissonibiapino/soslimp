import customtkinter as ctk
from PIL import Image

# Outras views

# Cores
from theme import colors

# from theme import colors

class Coluna1(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=colors.BRANCO)
        
        # Configuração das linhas da colunas e das linhas
        self.grid_columnconfigure(0, weight=1)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Linha 1
        linha1 = ctk.CTkFrame(
            self,
            fg_color=colors.BRANCO,
            corner_radius=10,
            border_width=2,
            border_color=colors.AZUL_SECUNDARIO)
        
        linha1.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        linha1.grid_columnconfigure(0, weight=1)
        linha1.grid_rowconfigure(0, weight=1)

        logo = ctk.CTkImage(
            light_image=Image.open("assets/img/SOSLimp.png"),
            dark_image=Image.open("assets/img/SOSLimp.png"),
            size=(180, 50)
        )
        logo_label = ctk.CTkLabel(linha1, text="", image=logo)
        logo_label.grid(row=0, column=0, pady=15, sticky="n")

        # Linha 2
        linha2 = ctk.CTkFrame(
            self,
            fg_color=colors.BRANCO,
            corner_radius=10,
            border_width=2,
            border_color=colors.AZUL_SECUNDARIO)
        
        linha2.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        linha2.grid_columnconfigure(0, weight=1)
        linha2.grid_rowconfigure(0, weight=1)

        # Linha 3
        linha3 = ctk.CTkFrame(
            self,
            fg_color=colors.BRANCO,
            corner_radius=10,
            border_width=2,
            border_color=colors.AZUL_SECUNDARIO)
        
        linha3.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        linha3.grid_columnconfigure(0, weight=1)
        linha3.grid_rowconfigure(0, weight=1)

        # Linha 4
        linha3 = ctk.CTkFrame(
            self,
            fg_color=colors.BRANCO,
            corner_radius=10,
            border_width=2,
            border_color=colors.AZUL_SECUNDARIO)
        
        linha3.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        linha3.grid_columnconfigure(0, weight=1)
        linha3.grid_rowconfigure(0, weight=1)
