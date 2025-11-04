import customtkinter as ctk

# Cores
from theme import colors

class Transaction(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=colors.BRANCO)
        self.controller = controller

        label = ctk.CTkLabel(self, text='Essa é a tela de transaction', width=40, height=28, fg_color='transparent')
        label.place(x=10, y=10)