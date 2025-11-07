import customtkinter as ctk
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Cores
from theme import colors

class Coluna2(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.grid_columnconfigure(0, weight=1)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

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

        label_dashboard = ctk.CTkLabel(linha1, text='Acessar dashboard')
        label_dashboard.place(x=10, y=10)


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

        label_infos_loja = ctk.CTkLabel(linha2, text='Informação futura')
        label_infos_loja.place(x=10, y=10)

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

        fig, ax = plt.subplots(figsize=(4, 2), subplot_kw=dict(aspect="equal"))
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        data = [15, 3, 4, 5, 1]
        formas_de_pagamento = ['Débito', 'Crédito', 'Pix', 'Dinheiro', 'Boleto']

        def func(pct, allvals):
            absolute = int(np.round(pct/100.*np.sum(allvals)))
            return f"{absolute:d}"

        wedges, texts, autotexts = ax.pie(data, autopct=lambda pct: func(pct, data), textprops=dict(color="w"))

        ax.legend(wedges, formas_de_pagamento, title="Formas de pagamento", loc="center", bbox_to_anchor=(1, 0, 0.5, 1))

        plt.setp(autotexts, size=10, weight="bold")

        canvas = FigureCanvasTkAgg(fig, master=linha3)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side="top", fill="both", expand=False, padx=10, pady=10)