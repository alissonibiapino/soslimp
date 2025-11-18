import customtkinter as ctk
import matplotlib.pyplot as plt
import time
from decimal import Decimal

from PIL import Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from views import coluna3.
# from app import show_home

from database.queries import get_colaboradores, get_caixa_atual, get_categorias, get_produtos_por_categoria, insert_registra_pedido

caixa_atual = get_caixa_atual()
categorias = get_categorias()


from theme import colors, fonts

# colaboradores_dict = {nome_pessoa: cod_pessoa for cod_pessoa, nome_pessoa in colaboradores}
# nomes_colaboradores = list(colaboradores_dict.keys())

class Coluna1(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#212121")
        self.controller = controller

        # Tipos de transação
        transacoes = {
            1: 'DÉBITO',
            2: 'CRÉDITO',
            3: 'PIX',
            4: 'DINHEIRO'
        }
        
        self.grid_columnconfigure(0, weight=1)

        categoria_selecionada = ctk.StringVar(value="Categoria do produto")
        transacao_selecionada = ctk.StringVar(value="Seleciona método de pagamento")

        produto_selecionado = ctk.StringVar(value="Selecione um produto")
        produto_selecionado_descricao = ctk.StringVar(value="Descrição")
        produto_selecionado_quantidade = ctk.StringVar(value="0")
        
        # colaborador_selecionado = ctk.StringVar(value="Selecione")

        # self.grid_rowconfigure(0, weight=1)
        # self.grid_rowconfigure(1, weight=1)
        # self.grid_rowconfigure(2, weight=1)
        # self.grid_rowconfigure(3, weight=1)

        self.produtos = {}

        def atualizar_produtos(categoria_nome):
            id_categoria = categorias[categoria_nome]
            self.produtos = get_produtos_por_categoria(id_categoria)
            select_produto.configure(values=list(self.produtos.keys()))
            select_produto.configure(state="normal")

        def atualizar_preco(produto_nome):
            produto_info = self.produtos.get(produto_nome)
            # print(produto_info["descricao"])
            # print(produto_info["preco"])
            # print(produto_info["marca"])
            if produto_info:
                produto_selecionado_descricao.set(produto_info["descricao"])
                produto_valor_var.configure(text=f"{produto_info['preco']}")
                # produto_valor_total.configure(text=f"R$ {produto_info['preco'] * int(produto_selecionado_quantidade.get())}")

            entrada_quantidade.configure(state="normal")
            select_transacao.configure(state="normal")
            atualizar_valor(1)

        def atualizar_valor(quantidade):
            if int(entrada_quantidade.get()) == "":
                return
            else:
                produto_valor_total.configure(text=f"R$ {float(produto_valor_var.cget("text")) * int(entrada_quantidade.get())}")

        def valida_quantidade(quantidade):
            if quantidade.isdigit() and len(quantidade) <= 2:
                return True
            if quantidade == "":
                return True
            return False
        
        def registrar_venda():
            cod_produto_selecionado = self.produtos.get(produto_selecionado.get())
            preco_produto_selecionado = self.produtos.get(produto_selecionado.get())
            tipo_pagamento_produto_selecionado = 0

            if transacao_selecionada.get() == "DÉBITO": tipo_pagamento_produto_selecionado = 1
            if transacao_selecionada.get() == "CRÉDITO": tipo_pagamento_produto_selecionado = 2
            if transacao_selecionada.get() == "PIX": tipo_pagamento_produto_selecionado = 3
            if transacao_selecionada.get() == "DINHEIRO": tipo_pagamento_produto_selecionado = 4
            # print("Código da loja: ")
            # print("Código do colaborador: ")
            # print("Forma de pagamento: ", tipo_pagamento_produto_selecionado)
            # print("Valor total: ", )
            # print("Hora do registro: ", time.time())
            # print("==========================================")
            # print("Código do produto: ", cod_produto_selecionado['cod_produto'])
            # print("Quantidade: ", int(entrada_quantidade.get()))
            # print("Preço unitário: ", preco_produto_selecionado['preco'])
            # print("Código da venda: ")

            insert_registra_pedido(1, 1, tipo_pagamento_produto_selecionado, round(Decimal(produto_valor_var.cget("text")) * int(entrada_quantidade.get()), 2), cod_produto_selecionado['cod_produto'], int(entrada_quantidade.get()), preco_produto_selecionado['preco'])
            self.controller.show_home()
            

        vcmd = (self.register(valida_quantidade), "%P")

        # Linha 1
        linha1 = ctk.CTkFrame(
            self,
            corner_radius=10,
            border_width=2,
            border_color=colors.AZUL_SECUNDARIO
        )
        
        linha1.grid(row=0, column=0, sticky="ew")
        linha1.grid_columnconfigure(0, weight=1)

        logo = ctk.CTkImage(
            light_image=Image.open("assets/img/SOSLimp.png"),
            dark_image=Image.open("assets/img/SOSLimp.png"),
            size=(180, 50)
        )
        logo_label = ctk.CTkLabel(linha1, text="", image=logo)
        logo_label.grid(row=0, column=0, pady=15, padx=5, sticky="nsew")

        # buttonTest = ctk.CTkButton(linha1, text="Ir para outra aba", command=self.controller.show_transaction)
        # buttonTest.grid(row=0, column=0, pady=15, sticky="n")

        # Linha 2
        linha2 = ctk.CTkFrame(
            self,
            corner_radius=10,
            border_width=2,
            border_color=colors.AZUL_SECUNDARIO)
        
        linha2.grid(row=1, column=0, sticky="nsew")
        linha2.grid_columnconfigure(0, weight=1)
        linha2.grid_rowconfigure(0, weight=1)

        label_linha2_valor = ctk.CTkLabel (
            linha2,
            text="Registrar nova compra:",
            font=fonts.FONTE_TITULO
        )
        label_linha2_valor.grid(row=0, column=0, pady=(15, 10), padx=20, sticky='nw')

                                                                                                # ESSE command ENVIA AUTOMATICAMENTE O VALOR SELECIONADO
        select_categoria = ctk.CTkOptionMenu(linha2, values=list(categorias.keys()), variable=categoria_selecionada, command=atualizar_produtos)
        select_categoria.grid(row=1, column=0, padx=20, sticky='nsew')

        select_produto = ctk.CTkOptionMenu(linha2, values=["Produto"], state="disabled", variable=produto_selecionado, command=atualizar_preco)
        select_produto.grid(row=2, column=0, padx=20, pady=10, sticky='nsew')

        entrada_quantidade = ctk.CTkEntry (
                linha2,
                placeholder_text="Quantidade de itens",
                state="disabled",
                validate="key",
                textvariable=produto_selecionado_quantidade,
                validatecommand=vcmd
            )
        entrada_quantidade.grid(row=3, column=0, padx=20, pady=10, sticky='nsew')
        entrada_quantidade.bind("<KeyRelease>", atualizar_valor)

        select_transacao = ctk.CTkOptionMenu(linha2, variable=transacao_selecionada, values=list(transacoes.values()), state="disabled")
        select_transacao.grid(row=4, column=0, padx=20, sticky='nsew')

        label_resumo = ctk.CTkLabel (
            linha2,
            text="Resumo da compra",
            font=fonts.FONTE_TITULO
        )
        label_resumo.grid(row=6, column=0, padx=20, sticky='nw')

        produto_nome = ctk.CTkLabel (label_resumo, text=f"{produto_selecionado.get()}", textvariable=(produto_selecionado), font=("Segoe UI Bold", 16))
        produto_nome.grid(row=7, column=0, padx=10, sticky="nw")

        produto_descricao = ctk.CTkLabel (label_resumo, text=f"{produto_selecionado_descricao.get()}", textvariable=(produto_selecionado_descricao))
        produto_descricao.grid(row=8, column=0, padx=10, pady=(0, 15), sticky="nw")

        resumo_frame = ctk.CTkFrame(linha2, fg_color="#212121")
        resumo_frame.grid(row=9, column=0, pady=5, padx=30, sticky="w")
        resumo_frame.grid_columnconfigure(0, weight=1)

        resumo_frame_esq = ctk.CTkFrame (resumo_frame, fg_color="#039340")
        resumo_frame_esq.grid(row=0, column=0, sticky="n")

        produto_metodo = ctk.CTkLabel (resumo_frame_esq, text="Método de pagamento")
        produto_metodo.grid(row=1, column=0, sticky="nw")

        produto_valor = ctk.CTkLabel (resumo_frame_esq, text="Valor unitário")
        produto_valor.grid(row=2, column=0, sticky="nw")

        produto_quantidade = ctk.CTkLabel (resumo_frame_esq, text="Quantidade")
        produto_quantidade.grid(row=3, column=0, sticky="nw")

        valor_compra = ctk.CTkLabel (resumo_frame_esq, text="Valor total da compra")
        valor_compra.grid(row=4, column=0, sticky="nw")

        resumo_frame_dir = ctk.CTkFrame (resumo_frame, fg_color="red")
        resumo_frame_dir.grid(row=0, column=1, padx=10, sticky="n")

        produto_metodo_var = ctk.CTkLabel (resumo_frame_dir, text=f"{transacao_selecionada.get()}", textvariable=(transacao_selecionada))
        produto_metodo_var.grid(row=0, column=0, sticky="nw")

        produto_valor_var = ctk.CTkLabel (resumo_frame_dir, text="")
        produto_valor_var.grid(row=1, column=0, sticky="nw")

        produto_quantidade = ctk.CTkLabel (resumo_frame_dir, text=f"{produto_selecionado_quantidade.get()}", textvariable=(produto_selecionado_quantidade))
        produto_quantidade.grid(row=2, column=0, sticky="nw")

        produto_valor_total = ctk.CTkLabel (resumo_frame_dir, text=f"")
        produto_valor_total.grid(row=3, column=0, sticky="nw")
        
        botao_registrar_compra = ctk.CTkButton(linha2, text="REGISTRAR COMPRA", height=35, command=registrar_venda)
        botao_registrar_compra.grid(row=10, column=0, padx=20, pady=10, sticky='nsew')

        # Linha 3
        linha3 = ctk.CTkFrame(
            self,
            corner_radius=10,
            border_width=2,
            border_color=colors.AZUL_SECUNDARIO)
        
        linha3.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        linha3.grid_columnconfigure(0, weight=1)

        label_linha3_valor_caixa = ctk.CTkLabel (
            linha3,
            text=f"TROCO DISPONÍVEL EM CAIXA: R$ {float(caixa_atual[0][0]):.2f}".replace(".", ",")
        )
        label_linha3_valor_caixa.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Linha 4
        # linha4 = ctk.CTkFrame(
        #     self,
        #     corner_radius=10,
        #     border_width=2,
        #     border_color=colors.AZUL_SECUNDARIO)
        
        # linha4.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        # # linha4.grid_columnconfigure(0, weight=1)
        # # linha4.grid_rowconfigure(0, weight=1)

        # fig, ax = plt.subplots(figsize=(1, 3))

        # horarios = ['08h', '09h', '10h', '11h', '12h', '13h', '14h', '15h', '16h', '17h', '18h']
        # counts = [12, 21, 55, 40, 65, 12, 30, 78, 51, 31, 13]
        # bar_labels = ['08h', '09h', '10h', '11h', '12h', '13h', '14h', '15h', '16h', '17h', '18h']
        # bar_colors = [colors.AZUL_PRIMARIO, colors.AZUL_SECUNDARIO]

        # ax.bar(horarios, counts, label=bar_labels, color=bar_colors)

        # canvas = FigureCanvasTkAgg(fig, master=linha4)
        # canvas_widget = canvas.get_tk_widget()
        # canvas_widget.pack(side="top", fill="both", expand=False, padx=10, pady=10)
