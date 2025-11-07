import customtkinter as ctk

from theme import colors

from database.queries import get_ultimas_vendas

ultimas_vendas = get_ultimas_vendas()
print(ultimas_vendas)

class Coluna3(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=colors.BRANCO)

        self.grid_columnconfigure(0, weight=1)

        self.grid_rowconfigure(0, weight=1)

        linha1 = ctk.CTkFrame(
            self,
            fg_color=colors.BRANCO,
            corner_radius=10,
            border_width=2,
            border_color=colors.AZUL_SECUNDARIO)
        
        linha1.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)
        linha1.grid_columnconfigure(0, weight=1)
        linha1.grid_rowconfigure(0, weight=1)

        for linha, (id_venda, dados) in enumerate(ultimas_vendas.items()):
            label = ctk.CTkLabel(linha1, text=f"{dados['forma_pagamento']} — R${dados['preco_unitario']}")
            label.grid(row=linha, column=0, padx=10, pady=5)

