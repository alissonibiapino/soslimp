import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import Counter

from sessao import SessaoDeLogin
from theme import fonts

from database.queries import get_ultimas_vendas

# Cores
from theme import colors

class Coluna2(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.valor_total = 0
        self.carregar_coluna2()

    def atualizar(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.carregar_coluna2()

    def carregar_coluna2(self):
        self.grid_columnconfigure(0, weight=1)

        self.valor_total = 0

        # Calcular vendas de hoje etcc.
        def calcular_dados_de_vendas():
            ultimas_vendas = get_ultimas_vendas(SessaoDeLogin.loja_cod)
            for venda in ultimas_vendas.values():
                self.valor_total += venda['preco_unitario']
            print(self.valor_total)

        calcular_dados_de_vendas()

        # Linha 1
        linha1 = ctk.CTkFrame(
            self,
            corner_radius=10,
            border_width=2,
            border_color=colors.AZUL_SECUNDARIO,
            height=80
        )        
        linha1.grid(row=0, column=0, sticky="new", padx=5, pady=5)

        ir_produtos = ctk.CTkButton(self, text="Ir para produtos", font=("", 20), command=self.controller.show_produtos)
        ir_produtos.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
                        
        # Linha 2
        linha2 = ctk.CTkFrame(
            self,
            corner_radius=10,
            border_width=2,
            border_color=colors.AZUL_SECUNDARIO)
        
        linha2.grid(row=1, column=0, sticky="new", padx=5, pady=5)

        label_bem_vindo = ctk.CTkLabel(linha2, text=f'Bem vindo, {SessaoDeLogin.nome}', font=fonts.FONTE_TITULO)
        label_bem_vindo.grid(row=0, column=0, sticky="nw", pady=(10, 2), padx=15)

        label_loja = ctk.CTkLabel(linha2, text=f'Você está na loja {SessaoDeLogin.loja_nome}', font=fonts.FONTE_TEXTO)
        label_loja.grid(row=1, column=0, sticky="nw", pady=(0, 5), padx=15)

        label_loja_infos = ctk.CTkLabel(linha2, text=f'Informações de contato:', font=fonts.FONTE_TITULO)
        label_loja_infos.grid(row=2, column=0, sticky="nw", pady=(0, 0), padx=15)

        label_loja_end = ctk.CTkLabel(linha2, text=f'Endereço: {SessaoDeLogin.loja_end}', font=fonts.FONTE_TEXTO)
        label_loja_end.grid(row=3, column=0, sticky="nw", pady=(0, 0), padx=15)

        label_loja_tel = ctk.CTkLabel(linha2, text=f'Telefone: {SessaoDeLogin.loja_num}', font=fonts.FONTE_TEXTO)
        label_loja_tel.grid(row=4, column=0, sticky="nw", pady=(0, 0), padx=15)

        label_loja_email = ctk.CTkLabel(linha2, text=f'E-mail: {SessaoDeLogin.loja_email}', font=fonts.FONTE_TEXTO)
        label_loja_email.grid(row=5, column=0, sticky="nw", pady=(0, 0), padx=15)

        label_loja_infos_faturamento = ctk.CTkLabel(linha2, text=f'Faturamento diário:', font=fonts.FONTE_TITULO)
        label_loja_infos_faturamento.grid(row=6, column=0, sticky="nw", pady=(20, 2), padx=15)

        label_loja_faturamento_diario = ctk.CTkLabel(linha2, text=f'R$ {self.valor_total}', font=(fonts.FONTE_TEXTO, 30))
        label_loja_faturamento_diario.grid(row=7, column=0, sticky="nw", pady=(0, 8), padx=15)

        # Linha 3
        linha3 = ctk.CTkFrame(
            self,
            corner_radius=10,
            border_width=2,
            border_color=colors.AZUL_SECUNDARIO)
        
        linha3.grid(row=2, column=0, sticky="new", padx=5, pady=5)
        linha3.grid_rowconfigure(0, weight=1)
        linha3.grid_columnconfigure(0, weight=1)


        ultimas_vendas = get_ultimas_vendas(SessaoDeLogin.loja_cod)

        horas = [dados["data"].hour for dados in ultimas_vendas.values()]
        contagem = Counter(horas)

        horas_ordenadas = sorted(contagem.keys())
        quantidade = [contagem[h] for h in horas_ordenadas]

        fig, ax = plt.subplots(figsize=(5, 3), dpi=100)
        ax.bar(horas_ordenadas, quantidade)
        ax.set_title("Vendas por horário")
        # ax.set_xlabel("Hora do dia")
        ax.set_ylabel("Quantidade")
        ax.set_xticks(horas_ordenadas)

        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=linha3)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True, padx=10, pady=10)

        canvas.draw()
