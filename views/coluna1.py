import customtkinter as ctk
import matplotlib.pyplot as plt

from PIL import Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from database.queries import get_colaboradores, get_caixa_atual, get_categorias, get_produtos_por_categoria

caixa_atual = get_caixa_atual()
categorias = get_categorias()


from theme import colors, fonts

# colaboradores_dict = {nome_pessoa: cod_pessoa for cod_pessoa, nome_pessoa in colaboradores}
# nomes_colaboradores = list(colaboradores_dict.keys())

class Coluna1(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Tipos de transação
        transacoes = {
            0: 'TRANSAÇÃO',
            1: 'DÉBITO',
            2: 'CRÉDITO',
            3: 'PIX',
            4: 'TED',
            5: 'DOC',
            6: 'DINHEIRO'
        }
        # transacoes = ['Dinheiro', 'Crédito', 'Débito', 'Pix']
        
        # Configuração das linhas da colunas e das linhas
        self.grid_columnconfigure(0, weight=1)

        categoria_selecionada = ctk.StringVar(value="Categoria do produto")
        colaborador_selecionado = ctk.StringVar(value="Selecione")

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)


        def atualizar_produtos(categoria_nome):
            id_categoria = categorias[categoria_nome]
            print(f"Categoria selecionada: {categoria_nome} (ID: {id_categoria})")
            atualizar_produtos_por_categoria(id_categoria)


        def atualizar_produtos_por_categoria(id_categoria):
            produtos = get_produtos_por_categoria(id_categoria)
            select_produto.configure(values=list(produtos.keys()))
            select_produto.configure(state="normal")

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
            text="Registrar nova compra:",
            font=fonts.FONTE_TITULO
        )
        label_linha2_valor.grid(row=0, column=0, pady=20, padx=20, sticky='nw')

                                                                                                # ESSE command ENVIA AUTOMATICAMENTE O VALOR SELECIONADO
        select_categoria = ctk.CTkOptionMenu(linha2, values=list(categorias.keys()), variable=categoria_selecionada, command=atualizar_produtos)
        select_categoria.grid(row=1, column=0, padx=20, sticky='nsew')

        select_produto = ctk.CTkOptionMenu(linha2, values=["Produto"], state="disabled")
        select_produto.grid(row=2, column=0, padx=20, pady=10, sticky='nsew')

        entrada_quantidade = ctk.CTkEntry (
                linha2,
                placeholder_text="Quantidade de itens"
            )
        entrada_quantidade.grid(row=3, column=0, padx=20, pady=10, sticky='nsew')

        select_transacao = ctk.CTkOptionMenu(linha2, values=list(transacoes.values()))
        select_transacao.grid(row=4, column=0, padx=20, sticky='nsew')

        entrada_valor_cliente = ctk.CTkEntry (
                linha2,
                placeholder_text="Dinheiro do cliente"
            )
        entrada_valor_cliente.grid(row=5, column=0, padx=20, pady=10, sticky='nsew')

        label_linha2_resumo = ctk.CTkLabel (
            linha2,
            text="Resumo da compra",
            font=fonts.FONTE_TITULO
        )
        label_linha2_resumo.grid(row=6, column=0, pady=5, padx=20, sticky='nw')
        
        label_linha2_resumo = ctk.CTkLabel (
            linha2,
            text=f"Sabão em pó\nMétodo de pagamento: R$\nValor unitário: R$\nQuantidade:\nValor total da compra:\nTroco R$",
            font=fonts.FONTE_TEXTO,
            justify="left"
        )
        label_linha2_resumo.grid(row=7, column=0, padx=25, sticky='w')

        botao_registrar_compra = ctk.CTkButton(linha2, text="REGISTRAR COMPRA", height=35)
        botao_registrar_compra.grid(row=8, column=0, padx=20, pady=10, sticky='nsew')

        # linha2_conteudo = ctk.CTkFrame(linha2, fg_color="transparent")
        # linha2_conteudo.grid(row=1, column=0, pady=5, padx=5, sticky="nsew")
        # linha2_conteudo.grid_columnconfigure(0, weight=1)
        
        # form_valor = ctk.CTkEntry (
        #     linha2_conteudo,
        #     placeholder_text="R$ 00,00"
        # )
        # form_valor.grid(row=0, column=0, padx=5, sticky='nsew')

        # select_tipo_transacao = ctk.CTkOptionMenu (
        #     linha2_conteudo,
        #     values=list(transacoes.values())
        # )
        # select_tipo_transacao.grid(row=0, column=1, padx=5, sticky='nsew')

        # # select_colaborador = ctk.CTkOptionMenu (
        # #     linha2_conteudo,
        # #     values=nomes_colaboradores,
        # #     variable=colaborador_selecionado
        # # )
        # # select_colaborador.grid(row=0, column=2, padx=5, sticky='nsew')



        # linha2_rodape = ctk.CTkFrame(linha2)
        # linha2_rodape.grid(row=2, column=0, pady=5, padx=5, sticky="nsew")
        # linha2_rodape.grid_columnconfigure(0, weight=1)

        # # select_produto = ctk.CTkOptionMenu (
        # #     linha2_rodape,
        # #     values=transacoes
        # # )
        # # select_produto.grid(row=0, column=0, padx=5, sticky='ew')

        # registrar_venda = ctk.CTkButton(linha2_rodape, text="REGISTRAR COMPRA")
        # registrar_venda.grid(row=2, column=0, pady=5, padx=5, sticky="nsew")

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
