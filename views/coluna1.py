import customtkinter as ctk
import matplotlib.pyplot as plt

from PIL import Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from database.queries import get_colaboradores

colaboradores = get_colaboradores()

colaboradores_dict = {nome_pessoa: cod_pessoa for cod_pessoa, nome_pessoa in colaboradores}
nomes_colaboradores = list(colaboradores_dict.keys())

# Cores
from theme import colors

# from theme import colors

class Coluna1(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Tipos de transação
        transacoes = ['Dinheiro', 'Crédito', 'Débito', 'Pix']

        # Fazer lógica para puxar os colaboradores do banco depois!!!
        colaboradores = ['Alisson', 'Daniel', 'José']
        
        # Configuração das linhas da colunas e das linhas
        self.grid_columnconfigure(0, weight=1)

        colaborador_selecionado = ctk.StringVar(value="Selecione")

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Linha 1
        linha1 = ctk.CTkFrame(
            self,
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

        buttonTest = ctk.CTkButton(linha1, text="Ir para outra aba", command=self.controller.show_transaction)
        buttonTest.grid(row=0, column=0, pady=15, sticky="n")

        # Linha 2
        linha2 = ctk.CTkFrame(
            self,
            corner_radius=10,
            border_width=2,
            border_color=colors.AZUL_SECUNDARIO)
        
        linha2.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        linha2.grid_columnconfigure(0, weight=1)
        linha2.grid_rowconfigure(0, weight=1)

        label_linha2_valor = ctk.CTkLabel (
            linha2,
            text="Nova entrada de valor:"
        )
        label_linha2_valor.grid(row=0, column=0, pady=10, padx=10)
        
        form_valor = ctk.CTkEntry (
            linha2,
            placeholder_text="R$ 00,00"
        )
        form_valor.grid(row=1, column=0, pady=10, padx=10, sticky='nsew')

        select_tipo_transacao = ctk.CTkOptionMenu (
            linha2,
            values=transacoes
        )
        select_tipo_transacao.grid(row=1, column=1, pady=10, padx=10, sticky='nsew')

        select_colaborador = ctk.CTkOptionMenu (
            linha2,
            values=nomes_colaboradores,
            variable=colaborador_selecionado
        )
        select_colaborador.grid(row=1, column=2, pady=10, padx=10, sticky='nsew')

        # Linha 3
        linha3 = ctk.CTkFrame(
            self,
            corner_radius=10,
            border_width=2,
            border_color=colors.AZUL_SECUNDARIO)
        
        linha3.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        linha3.grid_columnconfigure(0, weight=1)
        linha3.grid_rowconfigure(0, weight=1)

        label_linha3_valor_caixa = ctk.CTkLabel (
            linha3,
            text="TROCO DISPONÍVEL EM CAIXA: "
        )
        label_linha3_valor_caixa.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        # Linha 4
        linha4 = ctk.CTkFrame(
            self,
            corner_radius=10,
            border_width=2,
            border_color=colors.AZUL_SECUNDARIO)
        
        linha4.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        linha4.grid_columnconfigure(0, weight=1)
        linha4.grid_rowconfigure(0, weight=1)

        fig, ax = plt.subplots(figsize=(1, 3))

        horarios = ['08h', '09h', '10h', '11h', '12h', '13h', '14h', '15h', '16h', '17h', '18h']
        counts = [12, 21, 55, 40, 65, 12, 30, 78, 51, 31, 13]
        bar_labels = ['08h', '09h', '10h', '11h', '12h', '13h', '14h', '15h', '16h', '17h', '18h']
        bar_colors = [colors.AZUL_PRIMARIO, colors.AZUL_SECUNDARIO]

        ax.bar(horarios, counts, label=bar_labels, color=bar_colors)

        canvas = FigureCanvasTkAgg(fig, master=linha4)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side="top", fill="both", expand=False, padx=10, pady=10)
