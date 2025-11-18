import customtkinter as ctk
from PIL import Image

# Outras views
from views.home import Home
from views.produtos import Transaction
from views.login import Login

from theme import fonts

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração visual
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("theme/soslimp-theme.json")
        self.title("SOSLimp")
        self.geometry("1280x720")
        fonts.iniciar_fontes()

        self.current_frame = None
        self.show_login()
    
    def show_login(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = Login(self)
        self.current_frame.pack(fill="both", expand=True)

    def show_home(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = Home(self)
        self.current_frame.pack(fill="both", expand=True)

    def show_transaction(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = Transaction(self)
        self.current_frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()
