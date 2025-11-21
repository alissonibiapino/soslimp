import customtkinter as ctk
from PIL import Image

# Cores
from theme import colors, fonts
from database.queries import get_categorias, get_produtos_por_categoria

class Produtos(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0)
        self.grid_columnconfigure(0, weight=1)

        self.grid_columnconfigure(1)
        self.grid_columnconfigure(1, weight=0)

        self.grid_columnconfigure(2)
        self.grid_columnconfigure(2, weight=1)

        self.grid_rowconfigure(0, weight=1)

        self.categorias = get_categorias()
        self.produtos = {}
        self.carregar_coluna1()
        self.carregar_coluna2()

    def atualizar(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.carregar_coluna1()

    def carregar_coluna1(self):
        def atualizar_produtos(categoria_nome):
            id_categoria = self.categorias[categoria_nome]
            self.produtos = get_produtos_por_categoria(id_categoria)
            self.carregar_coluna2()

        col1 = ctk.CTkFrame(
            self,
            corner_radius=10,
            border_width=2,
            border_color=colors.AZUL_SECUNDARIO)
        col1.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        col1.grid_columnconfigure(0, weight=1, minsize=200)

        col1_cabecalho = ctk.CTkFrame(col1)
        col1_cabecalho.grid(row=0, column=0, sticky="w", padx=15, pady=5)
        col1_cabecalho.grid_columnconfigure(0, weight=1)

        voltar = ctk.CTkImage(
            light_image=Image.open("assets/img/voltar.png"),
            dark_image=Image.open("assets/img/voltar.png"),
            size=(30, 20)
        )
        voltar_label = ctk.CTkLabel(col1_cabecalho, text="", image=voltar)
        voltar_label.grid(row=0, column=0, pady=20, padx=5, sticky="w")
        voltar_label.bind("<Button-1>", lambda e: self.master.show_home())
        # voltar_label("<Button-1>", self.master.show_home())

        label_produtos = ctk.CTkLabel(col1_cabecalho, text="Produtos por categoria:", font=fonts.FONTE_TITULO)
        label_produtos.grid(row=0, column=1, pady=20, padx=15, sticky="w")

        # label_produtos_equilibrador = ctk.CTkLabel(col1_cabecalho, text="")
        # label_produtos_equilibrador.grid(row=0, column=2, pady=20, padx=15, sticky="e")

        for index, categoria in enumerate(self.categorias):
            btn_categoria = ctk.CTkButton(col1, text=categoria, height=50, command=lambda t=categoria: atualizar_produtos(t))
            btn_categoria.grid(row=index + 1, column=0, sticky="nsew", pady=5, padx=15)

    def carregar_coluna2(self):
        col2 = ctk.CTkFrame(
            self,
            corner_radius=10,
            border_width=2,
            border_color=colors.AZUL_SECUNDARIO)
        col2.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        col2.grid_columnconfigure(0, weight=1)

        for index, (nome_produto, dados_produto) in enumerate(self.produtos.items()):
            frame_produto = ctk.CTkFrame(col2)
            frame_produto.grid(row=index, column=0, sticky="nsew", pady=15, padx=20)
            frame_produto.grid_columnconfigure(0, weight=1)
            frame_produto.grid_rowconfigure(0, weight=1)

            label_produto = ctk.CTkLabel(frame_produto, text=nome_produto, font=("", 15))
            label_produto.grid(row=0, column=0, sticky="nw")

            label_produto_desc = ctk.CTkLabel(frame_produto, text=dados_produto['descricao'], font=fonts.FONTE_TEXTO)
            label_produto_desc.grid(row=1, column=0, sticky="nw")

            label_produto_marca = ctk.CTkLabel(frame_produto, text=dados_produto['marca'], fg_color=colors.AZUL_SECUNDARIO, text_color="#fafafa", padx=10, pady=5, corner_radius=2)
            label_produto_marca.grid(row=0, column=1, sticky="e")

            label_produto_preco = ctk.CTkLabel(frame_produto, text=f"R$ {dados_produto['preco']}", fg_color="#8C8C8C", text_color="#fafafa", padx=10, pady=5, corner_radius=2)
            label_produto_preco.grid(row=0, column=2, sticky="e", padx=10)

    