import customtkinter as ctk

from database.queries import get_produtos

produtos = get_produtos()
# produtos_dict = {nome_produto:   in produtos}

class Coluna3(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
