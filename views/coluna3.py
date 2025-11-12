import customtkinter as ctk
from PIL import Image

from theme import colors

from database.queries import get_ultimas_vendas

ultimas_vendas = get_ultimas_vendas()
print(ultimas_vendas)

def editar_entrada():
    print('Clicou em editar')

def excluir_entrada():
    print('Clicou em excluir')

class Coluna3(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=0)
        self.grid_rowconfigure(0, weight=1)

        linha1 = ctk.CTkFrame(
            self,
            corner_radius=10,
            border_width=2,
            border_color=colors.AZUL_SECUNDARIO)
        
        linha1.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

        # linha1.grid_rowconfigure(1, weight=1)  # linha do scroll ocupa o espaço vertical
        # linha1.grid_columnconfigure(0, weight=1)

        ultimas_entradas_label = ctk.CTkLabel(linha1, text="ÚLTIMAS ENTRADAS", font=("Arial", 20))
        ultimas_entradas_label.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

        # linha_historico = ctk.CTkScrollableFrame(linha1, scrollbar_button_color=colors.AZUL_SECUNDARIO, scrollbar_button_hover_color=colors.AZUL_PRIMARIO)
        # linha_historico.grid(row=1, column=0, padx=6, pady=0, sticky="nsew")

        linha_historico = ctk.CTkFrame(linha1)
        linha_historico.grid(row=1, column=0, padx=6, pady=0)

        for linha, (id_venda, dados) in enumerate(ultimas_vendas.items()):
            linha_venda = ctk.CTkFrame(linha_historico)
            linha_venda.grid(row=linha, column=0, padx=10, pady=5, sticky="w")

            coluna_valor_venda = ctk.CTkLabel(linha_venda, text=f"R$ {dados['preco_unitario']}", width=60, anchor='w')
            coluna_valor_venda.grid(row=0, column=0, padx=0, pady=0)

            coluna_tipo_pagamento = ctk.CTkFrame(linha_venda)
            coluna_tipo_pagamento.grid(row=0, column=1, padx=10, pady=0)

            if dados['forma_pagamento'] == 'Pix':
                forma_de_pagamento_icon = ctk.CTkImage(
                    light_image = Image.open("assets/img/pix.png"),
                    dark_image = Image.open("assets/img/pix.png"),
                    size=(12, 12)
                )
                forma_de_pagamento_label = ctk.CTkLabel(coluna_tipo_pagamento, text="", image=forma_de_pagamento_icon)
                forma_de_pagamento_label.grid(row=0, column=0, pady=0, sticky="n")
                coluna_tipo_pagamento = ctk.CTkLabel(coluna_tipo_pagamento, text=f"{dados['forma_pagamento']}", width=60, anchor='w')
                coluna_tipo_pagamento.grid(row=0, column=1, padx=6, pady=0)

            if dados['forma_pagamento'] == 'Crédito':
                forma_de_pagamento_icon = ctk.CTkImage(
                    light_image = Image.open("assets/img/cartao.png"),
                    dark_image = Image.open("assets/img/cartao.png"),
                    size=(12, 12)
                )
                forma_de_pagamento_label = ctk.CTkLabel(coluna_tipo_pagamento, text="", image=forma_de_pagamento_icon)
                forma_de_pagamento_label.grid(row=0, column=0, pady=0, sticky="n")
                coluna_tipo_pagamento = ctk.CTkLabel(coluna_tipo_pagamento, text=f"{dados['forma_pagamento']}", width=60, anchor='w')
                coluna_tipo_pagamento.grid(row=0, column=1, padx=6, pady=0)

            if dados['forma_pagamento'] == 'Débito':
                forma_de_pagamento_icon = ctk.CTkImage(
                    light_image = Image.open("assets/img/cartao.png"),
                    dark_image = Image.open("assets/img/cartao.png"),
                    size=(12, 12)
                )
                forma_de_pagamento_label = ctk.CTkLabel(coluna_tipo_pagamento, text="", image=forma_de_pagamento_icon)
                forma_de_pagamento_label.grid(row=0, column=0, pady=0, sticky="n")
                coluna_tipo_pagamento = ctk.CTkLabel(coluna_tipo_pagamento, text=f"{dados['forma_pagamento']}", width=60, anchor='w')
                coluna_tipo_pagamento.grid(row=0, column=1, padx=6, pady=0)

            if dados['forma_pagamento'] == 'Dinheiro':
                forma_de_pagamento_icon = ctk.CTkImage(
                    light_image = Image.open("assets/img/dinheiro.png"),
                    dark_image = Image.open("assets/img/dinheiro.png"),
                    size=(8, 12)
                )
                forma_de_pagamento_label = ctk.CTkLabel(coluna_tipo_pagamento, text="", image=forma_de_pagamento_icon)
                forma_de_pagamento_label.grid(row=0, column=0, pady=0, sticky="n")
                coluna_tipo_pagamento = ctk.CTkLabel(coluna_tipo_pagamento, text=f"{dados['forma_pagamento']}", anchor='w')
                coluna_tipo_pagamento.grid(row=0, column=1, padx=6, pady=0)

            editar_icon = ctk.CTkImage(
                light_image = Image.open("assets/img/editar.png"),
                dark_image = Image.open("assets/img/editar.png"),
                size=(12, 12)
            )

            editar_label_btn = ctk.CTkButton (
                master=coluna_tipo_pagamento,
                text="",
                image=editar_icon,
                fg_color="#FFFFFF",
                width=12,
                hover_color="#FAFAFA",
                hover=True,
                command=editar_entrada
            )
            editar_label_btn.grid(row=0, column=2, pady=0, sticky="n")

            excluir_icon = ctk.CTkImage(
                light_image = Image.open("assets/img/excluir.png"),
                dark_image = Image.open("assets/img/excluir.png"),
                size=(12, 12)
            )

            excluir_label_btn = ctk.CTkButton (
                master=coluna_tipo_pagamento,
                text="",
                image=excluir_icon,
                fg_color="#FFFFFF",
                width=12,
                hover_color="#FAFAFA",
                hover=True,
                command=excluir_entrada
            )
            excluir_label_btn.grid(row=0, column=3, pady=0, sticky="n")


            # excluir_label = ctk.CTkLabel(coluna_tipo_pagamento, text="", image=excluir_icon)
            # excluir_label.grid(row=0, column=3, pady=0, padx=5, sticky="n")

            coluna_horario_venda = ctk.CTkFrame(linha_venda)
            coluna_horario_venda.grid(row=0, column=4, padx=10, pady=0)

            horario_icon = ctk.CTkImage(
                light_image = Image.open("assets/img/horario.png"),
                dark_image = Image.open("assets/img/horario.png"),
                size=(12, 12)
            )
            horario_label = ctk.CTkLabel(coluna_horario_venda, text="", image=horario_icon)
            horario_label.grid(row=0, column=0, pady=0, padx=5, sticky="n")

            hora = dados['data'].strftime("%H:%M")
            coluna_horario_venda_texto = ctk.CTkLabel(coluna_horario_venda, text=f"{hora}")
            coluna_horario_venda_texto.grid(row=0, column=1, padx=0, pady=0, sticky="n")