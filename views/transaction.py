import customtkinter as ctk

# Cores
from theme import colors

class Transaction(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=colors.BRANCO)

        label = ctk.CTkLabel(self, text='Essa é a tela de transaction', width=40, height=28, fg_color='transparent')
        label.place(x=10, y=10)

        buttonTest = ctk.CTkButton(self, text="Ir para outra aba", command=master.show_home)
        buttonTest.grid(row=0, column=0, pady=15, sticky="n")
    