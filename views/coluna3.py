import customtkinter as ctk

from theme import colors

from database.queries import get_ultimas_vendas

ultimas_vendas = get_ultimas_vendas()
print(ultimas_vendas)

class Coluna3(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=0)
        self.grid_rowconfigure(0, weight=1)

        linha1 = ctk.CTkFrame(
            self,
            fg_color=colors.BRANCO,
            corner_radius=10,
            border_width=2,
            border_color=colors.AZUL_SECUNDARIO)
        
        linha1.grid(row=0, column=0, sticky="nsew", padx=10, pady=5)

        ultimas_entradas_label = ctk.CTkLabel(linha1, text="ÚLTIMAS ENTRADAS", font=("Arial", 20))
        ultimas_entradas_label.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)

        linha_historico = ctk.CTkFrame(linha1, fg_color=colors.BRANCO)
        linha_historico.grid(row=1, column=0, padx=3, pady=0)

        for linha, (id_venda, dados) in enumerate(ultimas_vendas.items()):
            linha_venda = ctk.CTkFrame(linha_historico)
            linha_venda.grid(row=linha, column=0, padx=10, pady=5, sticky="w")

            coluna_valor_venda = ctk.CTkLabel(linha_venda, text=f"R$ {dados['preco_unitario']}", width=50, anchor='w')
            coluna_valor_venda.grid(row=0, column=0, padx=0, pady=0)

            coluna_tipo_pagamento = ctk.CTkFrame(linha_venda)
            coluna_tipo_pagamento.grid(row=0, column=1, padx=10, pady=0)

            coluna_tipo_pagamento_icone = ctk.CTkLabel(coluna_tipo_pagamento, text="[  ]", width=10, anchor='w')
            coluna_tipo_pagamento_icone.grid(row=0, column=1, padx=0, pady=0)

            coluna_tipo_pagamento = ctk.CTkLabel(coluna_tipo_pagamento, text=f"{dados['forma_pagamento']}", width=70, anchor='w')
            coluna_tipo_pagamento.grid(row=0, column=2, padx=8, pady=0)

            coluna_editar = ctk.CTkLabel(coluna_tipo_pagamento, text="[ E ]", width=10, anchor='w')
            coluna_editar.grid(row=0, column=2, padx=0, pady=0)

            coluna_excluir = ctk.CTkLabel(coluna_tipo_pagamento, text="[ X ]", width=10, anchor='w')
            coluna_excluir.grid(row=0, column=3, padx=0, pady=0)

            coluna_horario_venda = ctk.CTkFrame(linha_venda)
            coluna_horario_venda.grid(row=0, column=4, padx=10, pady=0)

            coluna_horario_venda_icon = ctk.CTkLabel(coluna_horario_venda, text="[ H ]")
            coluna_horario_venda_icon.grid(row=0, column=0, padx=0, pady=0)
            
            hora = dados['data'].strftime("%H:%M")
            coluna_horario_venda_texto = ctk.CTkLabel(coluna_horario_venda, text=f"{hora}")
            coluna_horario_venda_texto.grid(row=0, column=1, padx=0, pady=0)
